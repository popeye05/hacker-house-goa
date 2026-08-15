from app.embeddings.model import EmbeddingModel
from app.models.document import DocumentChunk
from app.retrieval.retriever import Retriever


def make_document(
    id: str,
    text: str,
    language: str,
) -> DocumentChunk:
    return DocumentChunk(
        id=id,
        text=text,
        language=language,
        query_id="123",
        passage_id=id,
        query_type="DESCRIPTION",
        is_selected=True,
        source="test",
        metadata={},
    )


def test_real_multilingual_retrieval():
    model = EmbeddingModel()

    # BGE-M3 produces 1024-dimensional embeddings.
    retriever = Retriever(
        embedding_model=model,
        dimension=1024,
    )

    documents = [
        make_document(
            "india-capital",
            "भारत की राजधानी नई दिल्ली है।",
            "hi",
        ),
        make_document(
            "mumbai",
            "मुंबई महाराष्ट्र की राजधानी है।",
            "hi",
        ),
        make_document(
            "goa",
            "गोवा भारत के पश्चिमी तट पर स्थित है।",
            "hi",
        ),
        make_document(
            "delhi-english",
            "New Delhi is the capital of India.",
            "en",
        ),
    ]

    retriever.add_documents(documents)

    results = retriever.retrieve(
        "भारत की राजधानी क्या है?",
        top_k=2,
    )

    assert len(results) == 2

    result_ids = [result.document.id for result in results]

    assert "india-capital" in result_ids