import os


class Logger:
    _instance = None
    _verbose = False

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize()
            if cls._instance._verbose:
                cls._instance._print_env()
        return cls._instance

    def _initialize(self):
        # Check the VERBOSE environment variable
        self._verbose = os.getenv("LOCAL_RAG_VERBOSE", "false").lower() == "true"

    def obfuscate_value(self, value):
        if len(value) > 13:
            return value[:5] + "***" + value[-5:]
        return value

    def _print_env(self):
        print("Environment variables loaded:")
        for key, value in os.environ.items():
            # Skip if the key doesn't start with LOCAL_RAG_
            if not key.startswith("LOCAL_RAG_"):
                continue
            obfuscated = self.obfuscate_value(value)
            print(f"\t{key}: {obfuscated}")

    def print(self, message):
        if self._verbose:
            print(message)
