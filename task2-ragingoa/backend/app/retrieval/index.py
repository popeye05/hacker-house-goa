from dataclasses import dataclass, asdict
import json
from pathlib import Path

import faiss
import numpy as np

from app.models.document import DocumentChunk


@dataclass
class SearchResult:
    document: DocumentChunk
    score: float


class FAISSIndex:
    """
    FAISS-backed vector index for DocumentChunk objects.

    We use inner-product similarity with normalized embeddings.
    For normalized vectors, inner product is equivalent to cosine similarity.
    """

    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError("dimension must be greater than 0")

        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.documents: list[DocumentChunk] = []

    def add(
        self,
        documents: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        """
        Add documents and their embeddings to the FAISS index.
        """

        if len(documents) != len(embeddings):
            raise ValueError(
                "Number of documents must match number of embeddings"
            )

        if not documents:
            return

        vectors = np.asarray(embeddings, dtype=np.float32)

        if vectors.ndim != 2:
            raise ValueError("Embeddings must be a 2D array")

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension {self.dimension}, "
                f"got {vectors.shape[1]}"
            )

        self.index.add(vectors)
        self.documents.extend(documents)

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """
        Return the most similar documents.
        """

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        if not self.documents:
            return []

        vector = np.asarray(
            [embedding],
            dtype=np.float32,
        )

        if vector.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embedding dimension {self.dimension}, "
                f"got {vector.shape[1]}"
            )

        k = min(top_k, len(self.documents))

        scores, indices = self.index.search(vector, k)

        results: list[SearchResult] = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            results.append(
                SearchResult(
                    document=self.documents[index],
                    score=float(score),
                )
            )

        return results

    def save(self, directory: str | Path) -> None:
        """
        Save the FAISS index and its associated documents to disk.

        Creates:
            directory/index.faiss
            directory/documents.json
        """

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        index_path = directory / "index.faiss"
        documents_path = directory / "documents.json"

        faiss.write_index(self.index, str(index_path))

        documents_data = [
            asdict(document)
            for document in self.documents
        ]

        with documents_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                documents_data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    @classmethod
    def load(
        cls,
        directory: str | Path,
    ) -> "FAISSIndex":
        """
        Load a previously saved FAISS index and its documents.
        """

        directory = Path(directory)

        index_path = directory / "index.faiss"
        documents_path = directory / "documents.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not documents_path.exists():
            raise FileNotFoundError(
                f"Documents file not found: {documents_path}"
            )

        index = faiss.read_index(str(index_path))

        with documents_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            documents_data = json.load(file)

        instance = cls(dimension=index.d)
        instance.index = index

        instance.documents = [
            DocumentChunk(**document)
            for document in documents_data
        ]

        return instance

    def __len__(self) -> int:
        return len(self.documents)