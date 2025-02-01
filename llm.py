import os

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

from logger import Logger


class LLMSingleton:
    _instance = None  # Class-level attribute to hold the singleton instance
    _groq_llm = None  # Class-level attribute to hold the groq_llm instance
    _prompt_template = (
        None  # Class-level attribute to hold the prompt_template instance
    )
    _logger: Logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMSingleton, cls).__new__(cls)
            cls._instance._logger = Logger()
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
        instance._logger.print("Started GROQ")

        llm_prompt_template = os.getenv("LOCAL_RAG_LLM_PROMPT_TEMPLATE")

        instance._prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=llm_prompt_template.replace("\\n", "\n"),
        )
        obfuscated = instance._logger.obfuscate_value(llm_prompt_template)
        instance._logger.print(f"\tPrompt Template: {obfuscated}")

    def _chain(self, retriever):
        return RetrievalQA.from_chain_type(
            llm=self._groq_llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": self._prompt_template},
        )

    def query(self, retriever, query: str):
        result = self._chain(retriever)({"query": query})

        answer = result["result"]

        # Extract the source documents
        source_documents = result.get("source_documents", [])
        # Format the references

        if len(source_documents) > 0:
            answer += "\n\n" + "#" * 20 + " References"

            for doc in source_documents:
                answer += f"\n\tDocument: {doc.metadata.get('source', 'Unknown')} - Page: {doc.metadata.get('page', 'Unknown')}"

            answer += "\n" + "#" * 50

        return answer
