from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Wrapper around the multilingual embedding model.

    The model converts text into dense numerical vectors that can
    later be indexed in FAISS.
    """

    MODEL_NAME = "BAAI/bge-m3"

    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of texts into embedding vectors.
        """

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return embeddings.tolist()