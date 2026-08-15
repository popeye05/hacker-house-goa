from app.models.document import DocumentChunk
from app.retrieval.retriever import Retriever


class FakeEmbeddingModel:

    def encode(self, texts: list[str]) -> list[list[float]]:
        vectors = []

        for text in texts:
            text = text.lower()

            if (
                "delhi" in text
                or "भारत की राजधानी" in text
                or "capital of india" in text
            ):
                vectors.append([1.0, 0.0, 0.0])

            elif (
                "mumbai" in text
                or "महाराष्ट्र" in text
            ):
                vectors.append([0.0, 1.0, 0.0])

            else:
                vectors.append([0.0, 0.0, 1.0])

        return vectors


def make_document(
    id: str,
    text: str,
) -> DocumentChunk:
    return DocumentChunk(
        id=id,
        text=text,
        language="hi",
        query_id="123",
        passage_id=id,
        query_type="DESCRIPTION",
        is_selected=True,
        source="test",
        metadata={},
    )


def test_retriever():
    model = FakeEmbeddingModel()

    retriever = Retriever(
        embedding_model=model,
        dimension=3,
    )

    documents = [
        make_document(
            "1",
            "भारत की राजधानी नई दिल्ली है।",
        ),
        make_document(
            "2",
            "मुंबई महाराष्ट्र की राजधानी है।",
        ),
        make_document(
            "3",
            "भारत एक विशाल देश है।",
        ),
    ]

    retriever.add_documents(documents)

    assert len(retriever) == 3

    results = retriever.retrieve(
        "What is the capital of India?",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].document.id == "1"


def test_empty_query():
    retriever = Retriever(
        embedding_model=FakeEmbeddingModel(),
        dimension=3,
    )

    assert retriever.retrieve("") == []
    assert retriever.retrieve("   ") == []