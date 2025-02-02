import os

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_groq import ChatGroq
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from logger import Logger
from answer_formatter import AnswerFormatter
from session_store import SessionManager


class LLMSingleton:
    _instance: "LLMSingleton" = None  # Class-level attribute to hold the singleton instance
    _groq_llm: ChatGroq = None  # Class-level attribute to hold the groq_llm instance
    _contextualize_q_system_prompt: str = ""  # System prompt for contextualization
    _qa_system_prompt: str = ""  # System prompt for Q&A
    _conversational_rag_chain: RunnableWithMessageHistory = None  # Chain for conversational RAG
    _session_store: SessionManager = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMSingleton, cls).__new__(cls)
            cls._instance._session_store = SessionManager()
            cls._initialize_groq_llm(cls._instance)

        return cls._instance

    @classmethod
    def _initialize_groq_llm(cls, instance):
        # Set the GROQ_API_KEY environment variable
        os.environ["GROQ_API_KEY"] = os.getenv("LOCAL_RAG_GROQ_API_KEY")

        # Instantiate the Groq language model and store it as a property
        instance._groq_llm = ChatGroq(
            model=os.getenv(
                "LOCAL_RAG_GROQ_LLM_MODEL"
            )  # Specify the model to use, e.g., "llama3-8b-8192"
        )
        logger = Logger()
        logger.print("Started GROQ")

        instance._contextualize_q_system_prompt = os.getenv("LOCAL_RAG_CONTEXT_PROMPT")
        instance._qa_system_prompt = os.getenv("LOCAL_RAG_SYSTEM_PROMPT")

    def add_retriever(self, retriever):
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self._groq_llm, retriever, contextualize_q_prompt
        )

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self._groq_llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )

        self._conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self._session_store.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

    def query(self, query: str) -> str:
        if self._conversational_rag_chain is None:
            raise RuntimeError(
                "Missing conversation rag chain. Use LLMSingleton().add_retriever first."
            )

        result = self._conversational_rag_chain.invoke(
            {"input": query},
            config={"configurable": {"session_id": "gml_nlp"}},
        )

        answer = result["answer"]

        # Extract the source documents
        source_documents = result.get("context", [])

        answer += AnswerFormatter.format_answer_with_references(answer, source_documents)

        self._session_store.save()

        return answer
