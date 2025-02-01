import json
import torch
import os

from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger import Logger


class DBSingleton:
    """A singleton class to manage embeddings and vector database."""

    _instance = None
    _logger: Logger = None
    _embedded_files = set()  # To track embedded files
    _metadata_file = "faiss_db/embedded_files.json"  # File to store metadata
    _save_path = "faiss_db"
    _db = None  # Placeholder for the FAISS database

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBSingleton, cls).__new__(cls)
            cls._instance._logger = Logger()
            cls._instance._initialize()

        return cls._instance

    def _initialize(self):
        """Initialize the embedding function and database."""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self._embedding_function = SentenceTransformerEmbeddings(
            model_name="intfloat/multilingual-e5-large", model_kwargs={"device": device}
        )
        self._load_local()
        self._logger.print(f"Init DB {device}")

    def _load_local(self):
        """Load metadata of already embedded files."""
        self._logger.print("Loading DB")

        if os.path.exists(self._save_path):
            self._db = FAISS.load_local(
                self._save_path,
                self._embedding_function,
                allow_dangerous_deserialization=True,
            )
            self._logger.print(f"\tFAISS loaded from {self._save_path}.")
        else:
            self._logger.print(f"\tNo FAISS found at {self._save_path}.")

        if os.path.exists(self._metadata_file):
            with open(self._metadata_file, "r") as f:
                self._embedded_files = set(json.load(f))
            self._logger.print(f"\tLoaded metadata from {self._metadata_file}")

    def _save_local(self):
        """Save metadata of embedded files."""
        self._logger.print("Saving DB")

        if self._db is not None:
            self._db.save_local(self._save_path)
            self._logger.print(f"\tFAISS saved to {self._save_path}.")
        else:
            self._logger.print("\tNo FAISS to save.")

        if len(self._embedded_files) > 0:
            with open(self._metadata_file, "w") as f:
                json.dump(list(self._embedded_files), f)
            self._logger.print(f"\tmetadata saved to {self._metadata_file}")

    def _split_pdf(self, file_path, chunk_size=1000, chunk_overlap=200):
        """
        Processes a PDF file, splits it into pages, and then divides the text into smaller chunks.

        Args:
            file_path (str): The path to the PDF file.

        Returns:
            list: A list of text fragments (splits) from the PDF.
        """
        logger = Logger()

        # Create a loader instance to read and process the PDF
        loader = PyPDFLoader(file_path)
        logger.print(f"Loaded file: {file_path}")

        # Load the PDF and split it into pages for easier processing
        pages = loader.load_and_split()
        logger.print(f"\tTotal Pages: {len(pages)}")

        # Create a text splitter to divide text into chunks of 1000 characters with 200-character overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

        # Apply the text splitter to the PDF pages, resulting in a list of smaller text fragments
        splits = text_splitter.split_documents(pages)
        logger.print(f"\tTotal Splits: {len(splits)}")

        return splits

    def create_embeddings(self, file_path: str):
        """
        Create embeddings for the provided file path and store them in the FAISS database.

        Args:
            file_path (string): the file path to be loaded and embedded.

        Returns:
            None
        """
        if file_path in self._embedded_files:
            self._logger.print(f"File '{file_path}' has already been embedded.")
            return

        splits = self._split_pdf(file_path)

        if self._db is None:
            self._db = FAISS.from_documents(splits, self._embedding_function)
        else:
            self._db.add_documents(splits)

        self._embedded_files.add(file_path)
        self._save_local()
        self._logger.print("Embeddings created and stored in the FAISS database.")

    def get_retriever(self):
        """
        Get the FAISS database retriever.

        Returns:
            FAISS: The FAISS database retriever.
        """
        return self._db.as_retriever()
