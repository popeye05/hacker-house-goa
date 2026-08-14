from dataclasses import dataclass
from typing import Any #This is type hinting btw

# dataclass frozen makes the data vars immutable :)
@dataclass(frozen=True)
class DocumentChunk:
    """
    Normalized representation of a retrievable unit of context.

    This is the internal format used by the ingestion, chunking,
    indexing, retrieval, and evaluation layers.
    """

    id: str
    text: str

    language: str

    query_id: str
    passage_id: str

    query_type: str

    is_selected: bool

    source: str

    metadata: dict[str, Any]