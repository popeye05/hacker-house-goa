from dataclasses import dataclass

from app.models.document import DocumentChunk


@dataclass
class SearchResult:
    document: DocumentChunk
    score: float