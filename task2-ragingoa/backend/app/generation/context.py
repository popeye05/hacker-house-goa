from dataclasses import dataclass

from app.models.document import DocumentChunk
from app.retrieval.retriever import SearchResult


@dataclass(frozen=True)
class Context:
    """
    Retrieved context prepared for answer generation.
    """

    text: str
    documents: list[DocumentChunk]


class ContextBuilder:
    """
    Converts retrieval results into a clean context block
    that can be passed to an LLM.
    """

    def __init__(self, max_characters: int = 8000):
        if max_characters <= 0:
            raise ValueError("max_characters must be greater than 0")

        self.max_characters = max_characters

    def build(
        self,
        results: list[SearchResult],
    ) -> Context:
        """
        Build a bounded context from retrieved documents.
        """

        selected_documents: list[DocumentChunk] = []
        sections: list[str] = []

        current_length = 0

        for index, result in enumerate(results, start=1):
            document = result.document

            section = (
                f"[Source {index}]\n"
                f"{document.text.strip()}"
            )

            # Account for the separator/newlines.
            additional_length = len(section) + 2

            if current_length + additional_length > self.max_characters:
                break

            sections.append(section)
            selected_documents.append(document)

            current_length += additional_length

        return Context(
            text="\n\n".join(sections),
            documents=selected_documents,
        )