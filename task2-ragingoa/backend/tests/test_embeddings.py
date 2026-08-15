from app.embeddings.model import EmbeddingModel


def test_embedding_model():
    model = EmbeddingModel()

    embeddings = model.encode(
        [
            "What is the capital of India?",
            "भारत की राजधानी क्या है?",
        ]
    )

    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
    assert len(embeddings[0]) == len(embeddings[1])