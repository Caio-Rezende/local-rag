# Import dotenv to load environment variables from a .env file
from dotenv import load_dotenv

from db import DBSingleton
from llm import LLMSingleton
from logger import Logger


try:
    # Load environment variables from the .env file
    load_dotenv()

    logger = Logger()

    db = DBSingleton()
    db.create_embeddings("inputs/CardiologianaEmergencia.pdf")
    retriever = db.get_retriever()

    llm = LLMSingleton()

    line = "=" * 50

    while True:
        print(f"\n{line}\n")
        # Prompt the user for input
        query = input("Enter your query (or leave blank to exit): ")

        # Check if the 'Esc' key is pressed
        if query == "":
            print("Exiting...")
            break

        # Call the query method with the user input
        result = llm.query(retriever, query)

        # Print the result
        logger.print(result)

except Exception as e:
    print(f"An error occurred: {e}")
