from app.models.document import DocumentChunk
from app.retrieval.index import FAISSIndex


def make_document(document_id: str, text: str) -> DocumentChunk:
    return DocumentChunk(
        id=document_id,
        text=text,
        language="hi",
        query_id="123",
        passage_id=document_id,
        query_type="DESCRIPTION",
        is_selected=True,
        source="test",
        metadata={},
    )


def test_faiss_index_save_and_load(tmp_path):
    index = FAISSIndex(dimension=3)

    documents = [
        make_document("1", "भारत की राजधानी नई दिल्ली है।"),
        make_document("2", "मुंबई महाराष्ट्र की राजधानी है।"),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    index.add(documents, embeddings)

    index.save(tmp_path)

    loaded = FAISSIndex.load(tmp_path)

    assert len(loaded) == 2
    assert loaded.dimension == 3

    results = loaded.search(
        [1.0, 0.0, 0.0],
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].document.id == "1"
    assert results[0].document.text == "भारत की राजधानी नई दिल्ली है।"