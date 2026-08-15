import pytest

from app.models.document import DocumentChunk
from app.retrieval.index import FAISSIndex


def make_document(id: str, text: str) -> DocumentChunk:
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


def test_add_and_search():
    documents = [
        make_document("1", "India is a country."),
        make_document("2", "New Delhi is the capital of India."),
        make_document("3", "Mumbai is in Maharashtra."),
    ]

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]

    index = FAISSIndex(dimension=3)

    index.add(documents, embeddings)

    assert len(index) == 3

    results = index.search(
        [0.0, 1.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].document.id == "2"
    assert results[0].score == pytest.approx(1.0)


def test_dimension_mismatch():
    index = FAISSIndex(dimension=3)

    document = make_document("1", "Test")

    with pytest.raises(ValueError):
        index.add(
            [document],
            [[1.0, 0.0]],
        )


def test_empty_index():
    index = FAISSIndex(dimension=3)

    results = index.search(
        [1.0, 0.0, 0.0],
        top_k=5,
    )

    assert results == []


def test_invalid_configuration():
    with pytest.raises(ValueError):
        FAISSIndex(dimension=0)

    index = FAISSIndex(dimension=3)

    with pytest.raises(ValueError):
        index.search(
            [1.0, 0.0, 0.0],
            top_k=0,
        )