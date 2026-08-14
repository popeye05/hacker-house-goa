from abc import ABC, abstractmethod

from app.models.document import DocumentChunk


class ChunkingStrategy(ABC):
    """
    Interface implemented by every chunking strategy.
    """

    name: str

    @abstractmethod
    def chunk(self, document: DocumentChunk) -> list[DocumentChunk]:
        """
        Split a document into retrievable chunks.
        """
        raise NotImplementedError