from pathlib import Path
from time import perf_counter
from app.embeddings.model import EmbeddingModel
from app.models.document import DocumentChunk
from app.retrieval.index import FAISSIndex, SearchResult


class Retriever:
    """
    Combines the embedding model and FAISS vector index
    into a simple semantic retrieval interface.
    """

    def __init__(
        self,
        embedding_model: EmbeddingModel,
        dimension: int | None = None,
        index_path: str | Path | None = None,
    ):
        self.embedding_model = embedding_model

        if index_path is not None:
            self.index = FAISSIndex.load(index_path)
        else:
            if dimension is None:
                raise ValueError(
                    "dimension is required when index_path is not provided"
                )

            self.index = FAISSIndex(dimension)

    def add_documents(
        self,
        documents: list[DocumentChunk],
    ) -> None:
        """
        Embed and add documents to the vector index.
        """

        if not documents:
            return

        texts = [document.text for document in documents]

        embeddings = self.embedding_model.encode(texts)

        self.index.add(
            documents,
            embeddings,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Retrieve the most semantically relevant documents.
        """

        if not query.strip():
            return []

        query_embedding = self.embedding_model.encode([query])[0]

        return self.index.search(
            query_embedding,
            top_k=top_k,
        )

    def retrieve_with_latency(
        self,
        query: str,
        top_k: int = 5,
) -> tuple[list[SearchResult], float, float]:

        if not query.strip():
            return [], 0.0, 0.0

        # Query embedding
        embedding_start = perf_counter()

        query_embedding = self.embedding_model.encode([query])[0]

        embedding_end = perf_counter()

        embedding_ms = (embedding_end - embedding_start) * 1000

        # FAISS search
        search_start = perf_counter()

        results = self.index.search(
            query_embedding,
            top_k=top_k,
        )

        search_end = perf_counter()

        faiss_ms = (search_end - search_start) * 1000

        return results, embedding_ms, faiss_ms

    def __len__(self) -> int:
        return len(self.index)