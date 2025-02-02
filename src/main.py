# Import dotenv to load environment variables from a .env file
from dotenv import load_dotenv

from db import DBSingleton
from llm import LLMSingleton
from logger import Logger
from commands import CommandHandler


try:
    # Load environment variables from the .env file
    load_dotenv()

    logger = Logger()

    db = DBSingleton()
    db.create_embeddings("inputs/CardiologianaEmergencia.pdf")
    retriever = db.get_retriever()

    llm = LLMSingleton()
    llm.add_retriever(retriever)

    line = "=" * 50

    handler = CommandHandler()

    while True:
        print(f"\n{line}\n")
        # Prompt the user for input
        query = input("Enter your query (or \h for options): ")

        action = handler.handle_command(query)

        if action == -1:
            break
        elif action == 0:
            continue

        # Call the query method with the user input
        result = llm.query(query)

        # Print the result
        logger.print(result)

except Exception as e:
    print(f"An error occurred: {e}")
