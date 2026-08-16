import os
import time

from qdrant_client import QdrantClient, models

from app.models.document import DocumentChunk
from app.retrieval.index import SearchResult


class QdrantRetriever:
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = os.getenv("QDRANT_COLLECTION", "msmarco_xi")
        self.embedding_model = os.getenv(
            "QDRANT_EMBEDDING_MODEL",
            "intfloat/multilingual-e5-small",
        )

        if not qdrant_url:
            raise RuntimeError(
                "Missing required environment variable: QDRANT_URL"
            )

        if not qdrant_api_key:
            raise RuntimeError(
                "Missing required environment variable: QDRANT_API_KEY"
            )

        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            cloud_inference=True,
        )

    def retrieve(self, query: str, top_k: int) -> list[SearchResult]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        response = self.client.query_points(
            collection_name=self.collection_name,
            query=models.Document(
                text=query.strip(),
                model=self.embedding_model,
            ),
            limit=top_k,
            with_payload=True,
        )

        results: list[SearchResult] = []

        for point in response.points:
            if point.payload is None:
                continue

            payload = point.payload
            ref_id = payload.get("ref_id", "")
            query_id, _, passage_idx = ref_id.rpartition("_")

            chunk = DocumentChunk(
                id=str(point.id),
                text=payload.get("text", ""),
                language=payload.get("language", "hi"),
                query_id=query_id or "unknown",
                passage_id=passage_idx or "0",
                query_type="unknown",
                is_selected=True,
                source=payload.get("source", "msmarco_xi"),
                metadata={"query": payload.get("query", "")},
            )

            results.append(
                SearchResult(
                    document=chunk,
                    score=point.score,
                )   
            )

        return results

    def retrieve_with_latency(
        self,
        query: str,
        top_k: int,
    ) -> tuple[list[SearchResult], float, float]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        start = time.perf_counter()

        results = self.retrieve(query, top_k)

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Qdrant Cloud performs both embedding and vector search.
        # There is no separate local embedding phase to measure.
        embedding_ms = 0.0
        faiss_ms = elapsed_ms

        return results, embedding_ms, faiss_ms