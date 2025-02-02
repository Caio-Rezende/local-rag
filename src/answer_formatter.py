class AnswerFormatter:
    """Handles the formatting of answers and references."""

    @staticmethod
    def format_answer_with_references(_, source_documents: list) -> str:
        """Formats the answer with references from source documents."""

        answer = ""
        if len(source_documents) > 0:
            answer += "\n\n" + "#" * 20 + " References"

            # Dictionary to group pages by document
            references = {}

            for doc in source_documents:
                document_name = doc.metadata.get("source", "Unknown")
                page_number = doc.metadata.get("page", "Unknown")

                # Add the page to the document's list of pages, avoiding duplicates
                if document_name not in references:
                    references[document_name] = set()
                references[document_name].add(page_number)

            # Sort and format the references
            for i, (document_name, pages) in enumerate(sorted(references.items())):
                sorted_pages = sorted(pages)  # Sort pages numerically
                answer += f"\n\t{i+1} - {document_name} - Pages: {', '.join(map(str, sorted_pages))}"

        return answer
