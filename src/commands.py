from session_store import SessionManager


class CommandHandler:
    """Handles special commands like \h, exit, and reset."""

    _session_store = SessionManager()

    def handle_command(self, command: str) -> int:
        """
        Handle special commands.
        Returns 1 if the loop should continue, -1 to exit or 0 to ignore current command.
        """
        if command == "exit" or command == "":
            print("Exiting...")
            return -1
        elif command == "reset":
            print("Resetting chat history...")
            self._session_store.reset()
            return 0
        elif command == "\\h":
            print("Options:")
            print("  exit  - Exit the application")
            print("  reset - Reset the chat history")
            print("  \\h    - Show this help menu")
            return 0

        return 1