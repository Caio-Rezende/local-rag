import json
import os

from langchain.schema import messages_from_dict, messages_to_dict
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from logger import Logger


class SessionManager:
    """Manages session histories with persistence."""

    _instance = None  # Class-level attribute to hold the singleton instance
    _storage_file = "storage/session_store.json"
    _store: dict[str, BaseChatMessageHistory] = {}
    _logger: Logger = Logger()
    __initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self.__initialized:
            self._load_sessions()
            self.__initialized = True  # Mark as initialized

    def _load_sessions(self):
        """Load session histories from the storage file."""
        try:
            with open(self._storage_file, "r") as file:
                data = json.load(file)
                for session_id, messages in data.items():
                    history = ChatMessageHistory()
                    history.messages = messages_from_dict(messages)
                    self._store[session_id] = history
        except FileNotFoundError:
            # If the file doesn't exist, start with an empty store
            self._store = {}
        except json.JSONDecodeError:
            # Handle corrupted JSON file
            self._logger.print(
                "Warning: Could not decode session store file. Starting fresh."
            )
            self._store = {}

    def _save_sessions(self):
        """Save session histories to the storage file."""
        data = {
            session_id: messages_to_dict(
                history.messages
            )  # Assuming `messages` is serializable
            for session_id, history in self._store.items()
        }
        with open(self._storage_file, "w") as file:
            json.dump(data, file)

    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._store:
            self._store[session_id] = ChatMessageHistory()
        return self._store[session_id]

    def save(self):
        """Manually trigger saving session histories."""
        self._save_sessions()

    def reset(self):
        """Reset the session store and delete the storage file."""
        self._store = {}  # Clear the in-memory store
        if os.path.exists(self._storage_file):
            os.remove(self._storage_file)  # Delete the storage file
        self._logger.print("Session store has been reset.")
