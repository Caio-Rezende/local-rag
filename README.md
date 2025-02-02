# LOCAL RAG

This project aims to help load a file into a local database (FAISS), which is a vector database, to enable querying with LangChain on GROQ APIs. It is designed to efficiently index and reuse embedded files for fast and reliable searches. The project now supports **chat history awareness**, allowing queries to consider the context of previous interactions.

## Table of Contents

- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Creating a GROQ API Key](#creating-a-groq-api-key)
- [Usage](#usage)
- [Indexing Files](#indexing-files)
- [Chat History Awareness](#chat-history-awareness)
- [License](#license)

---

## Getting Started

To get started with this project, follow the steps below:

1. Clone the repository:
   ```bash
   git clone https://github.com/Caio-Rezende/local-rag
   cd local-rag
   ```

2. Set up a Python virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

This project uses environment variables to configure various settings. A sample `.env` file is provided in the repository as `env.sample`. You need to create a `.env` file in the root directory of the project and populate it with the required values.

### Example `.env` file:

```env
LOCAL_RAG_VERBOSE=true
LOCAL_RAG_GROQ_API_KEY=your_api_key_here
LOCAL_RAG_GROQ_LLM_MODEL=llama3-8b-8192
LOCAL_RAG_CONTEXT_PROMPT="Dada a história do chat e a última pergunta do usuário, que pode referenciar o\n        contexto na história do chat, reformule a pergunta de forma que possa ser entendida\n        sem a necessidade da história do chat. NÃO responda à pergunta, apenas reformule-a\n        se necessário e, caso contrário, retorne-a como está.\n        O estilo de escrita é formal e claro, dirigido a pacientes e visitantes do hospital.\n        Você deve ficar atento ao histórico do chat para determinar se uma consulta ja foi marcada, ou seja, se alguém marcou consulta antes da pessoa, você deve retornar que está indisponível."
LOCAL_RAG_SYSTEM_PROMPT="Atue com a personalidade de um assistente profissional especializado em tarefas de resposta a perguntas relacionadas a serviços hospitalares.\n\nUse os seguintes pedaços de contexto para responder à pergunta do usuário.\nSe você não souber a resposta, diga apenas que não tem informações suficientes para responder.\n\nContexto: {context}"
```

### Steps to Set Up:

1. Copy the `env.sample` file to `.env`:
   ```bash
   cp env.sample .env
   ```
2. Open the `.env` file and replace the placeholder values with your actual configuration.

---

## Creating a GROQ API Key

To use the GROQ API, you need to generate an API key. Follow these steps:

1. Log in to your GROQ account at [GROQ Dashboard](https://dashboard.groq.com).
2. Navigate to the **API Keys** section in your account settings.
3. Click on **Create New API Key**.
4. Provide a name for your API key (e.g., "ProjectName Key").
5. Set the appropriate permissions for the key based on your project requirements.
6. Click **Generate Key** and copy the generated key.
7. Paste the key into the `LOCAL_RAG_GROQ_API_KEY` field in your `.env` file.

---

## Usage

Once the environment variables are set up and the GROQ API key is configured, you can start using the project.

### Example Usage:

1. Start the script iteration:
   ```bash
   python main.py
   ```
2. The application will prompt you to enter a query. This query will be used to search the indexed files stored in the local FAISS database.
3. If no query is entered, the script will exit.

---

## Indexing Files

To index a file for querying, you need to modify the `main.py` file. Locate the following line in the script:

```python
db.create_embeddings("inputs/CardiologianaEmergencia.pdf")
```

Replace `"inputs/CardiologianaEmergencia.pdf"` with the path to the file you want to index. Once indexed, the file's embeddings are stored locally, allowing for fast and efficient reuse in subsequent queries.

### Key Features:
- **File Reuse**: Once a file is embedded, it is stored locally and does not need to be re-indexed unless changes are made.
- **Customizable**: You can index multiple files by modifying the script to include additional file paths.

---

## Chat History Awareness

This project now supports **chat history awareness**, enabling the system to consider the context of previous interactions when processing queries. This feature is particularly useful for maintaining continuity in conversations and providing more accurate responses.

### How It Works:

1. **Contextualization Prompt**: The `LOCAL_RAG_CONTEXT_PROMPT` environment variable defines how the system reformulates user queries based on chat history. For example:
   ```env
   LOCAL_RAG_CONTEXT_PROMPT="Dada a história do chat e a última pergunta do usuário, que pode referenciar o\n        contexto na história do chat, reformule a pergunta de forma que possa ser entendida\n        sem a necessidade da história do chat. NÃO responda à pergunta, apenas reformule-a\n        se necessário e, caso contrário, retorne-a como está."
   ```
   This ensures that the system reformulates queries to be self-contained and understandable without requiring prior context.

2. **System Prompt**: The `LOCAL_RAG_SYSTEM_PROMPT` environment variable defines the assistant's behavior and response style. For example:
   ```env
   LOCAL_RAG_SYSTEM_PROMPT="Atue com a personalidade de um assistente profissional especializado em tarefas de resposta a perguntas relacionadas a serviços hospitalares.\n\nUse os seguintes pedaços de contexto para responder à pergunta do usuário.\nSe você não souber a resposta, diga apenas que não tem informações suficientes para responder.\n\nContexto: {context}"
   ```

3. **Chat History Integration**: The system uses the chat history to determine the context of the current query and provide more relevant responses.

---

## License

This project is licensed under the [MIT License](LICENSE).