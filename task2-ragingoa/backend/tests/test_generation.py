import pytest

from app.generation.context import Context
from app.generation.generator import (
    AnswerGenerator,
    FakeAnswerGenerator,
)
from app.models.document import DocumentChunk


def make_document(text: str) -> DocumentChunk:
    return DocumentChunk(
        id="1",
        text=text,
        language="hi",
        query_id="123",
        passage_id="0",
        query_type="DESCRIPTION",
        is_selected=True,
        source="test",
        metadata={},
    )


def test_fake_generator():
    document = make_document(
        "भारत की राजधानी नई दिल्ली है।"
    )

    context = Context(
        text="[Source 1]\nभारत की राजधानी नई दिल्ली है।",
        documents=[document],
    )

    generator = FakeAnswerGenerator()

    answer = generator.generate(
        query="भारत की राजधानी क्या है?",
        context=context,
        language="hi",
    )

    assert answer == "भारत की राजधानी नई दिल्ली है।"


def test_fake_generator_without_context():
    context = Context(
        text="",
        documents=[],
    )

    generator = FakeAnswerGenerator()

    answer = generator.generate(
        query="भारत की राजधानी क्या है?",
        context=context,
        language="hi",
    )

    assert answer == "I could not find relevant information."


def test_empty_query():
    context = Context(
        text="",
        documents=[],
    )

    generator = FakeAnswerGenerator()

    with pytest.raises(ValueError):
        generator.generate(
            query="",
            context=context,
            language="hi",
        )


def test_generator_is_abstract():
    with pytest.raises(TypeError):
        AnswerGenerator()