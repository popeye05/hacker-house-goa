import pytest

from app.chunking.strategies import (
    FixedSizeChunking,
    PassageChunking,
    SentenceChunking,
)
from app.models.document import DocumentChunk


def make_document(text: str) -> DocumentChunk:
    return DocumentChunk(
        id="hi_123_0",
        text=text,
        language="hi",
        query_id="123",
        passage_id="0",
        query_type="DESCRIPTION",
        is_selected=True,
        source="translated",
        metadata={},
    )


def test_passage_chunking():
    document = make_document(
        "भारत एक विशाल देश है।"
    )

    chunks = PassageChunking().chunk(document)

    assert len(chunks) == 1
    assert chunks[0].text == document.text


def test_sentence_chunking():
    document = make_document(
        "भारत एक विशाल देश है। "
        "भारत की राजधानी नई दिल्ली है।"
    )

    chunks = SentenceChunking().chunk(document)

    assert len(chunks) == 2
    assert chunks[0].text == "भारत एक विशाल देश है।"
    assert chunks[1].text == "भारत की राजधानी नई दिल्ली है।"


def test_sentence_chunking_english():
    document = make_document(
        "India is a large country. "
        "New Delhi is its capital."
    )

    chunks = SentenceChunking().chunk(document)

    assert len(chunks) == 2


def test_fixed_size_chunking():
    document = make_document(
        "one two three four five six seven eight nine ten"
    )

    strategy = FixedSizeChunking(
        chunk_size=5,
        overlap=2,
    )

    chunks = strategy.chunk(document)

    assert len(chunks) == 3

    assert chunks[0].text == "one two three four five"
    assert chunks[1].text == "four five six seven eight"
    assert chunks[2].text == "seven eight nine ten"


def test_fixed_size_invalid_configuration():
    with pytest.raises(ValueError):
        FixedSizeChunking(chunk_size=0)

    with pytest.raises(ValueError):
        FixedSizeChunking(chunk_size=10, overlap=10)

    with pytest.raises(ValueError):
        FixedSizeChunking(chunk_size=10, overlap=11)