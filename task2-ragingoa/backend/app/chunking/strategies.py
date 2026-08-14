from app.chunking.base import ChunkingStrategy
from app.models.document import DocumentChunk


class PassageChunking(ChunkingStrategy):
    """
    Baseline strategy.

    Treat the entire source passage as one retrieval unit.
    """

    name = "passage"

    def chunk(self, document: DocumentChunk) -> list[DocumentChunk]:
        return [document]


class SentenceChunking(ChunkingStrategy):
    """
    Split a passage into sentence-level retrieval units.
    """

    name = "sentence"

    def chunk(self, document: DocumentChunk) -> list[DocumentChunk]:
        sentences = self._split_sentences(document.text)

        chunks: list[DocumentChunk] = []

        for index, sentence in enumerate(sentences):
            sentence = sentence.strip()

            if not sentence:
                continue

            chunks.append(
                DocumentChunk(
                    id=f"{document.id}_s{index}",
                    text=sentence,
                    language=document.language,
                    query_id=document.query_id,
                    passage_id=document.passage_id,
                    query_type=document.query_type,
                    is_selected=document.is_selected,
                    source=document.source,
                    metadata={
                        **document.metadata,
                        "chunk_strategy": self.name,
                        "chunk_index": index,
                    },
                )
            )

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        import re

        return re.split(
            r"(?<=[.!?।॥])\s+",
            text.strip(),
        )


class FixedSizeChunking(ChunkingStrategy):
    """
    Split a document into fixed-size word chunks
    with configurable overlap.
    """

    name = "fixed"

    def __init__(self, chunk_size: int = 100, overlap: int = 20):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if overlap < 0:
            raise ValueError("overlap cannot be negative")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, document: DocumentChunk) -> list[DocumentChunk]:
        words = document.text.split()

        if not words:
            return []

        chunks: list[DocumentChunk] = []

        step = self.chunk_size - self.overlap

        for index, start in enumerate(range(0, len(words), step)):
            chunk_words = words[start:start + self.chunk_size]

            if not chunk_words:
                break

            chunks.append(
                DocumentChunk(
                    id=f"{document.id}_f{index}",
                    text=" ".join(chunk_words),
                    language=document.language,
                    query_id=document.query_id,
                    passage_id=document.passage_id,
                    query_type=document.query_type,
                    is_selected=document.is_selected,
                    source=document.source,
                    metadata={
                        **document.metadata,
                        "chunk_strategy": self.name,
                        "chunk_index": index,
                        "chunk_size": self.chunk_size,
                        "overlap": self.overlap,
                        "start_word": start,
                    },
                )
            )

            if start + self.chunk_size >= len(words):
                break

        return chunks