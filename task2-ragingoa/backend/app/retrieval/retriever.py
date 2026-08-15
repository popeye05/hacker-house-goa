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
        dimension: int,
    ):
        self.embedding_model = embedding_model
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

    def __len__(self) -> int:
        return len(self.index)