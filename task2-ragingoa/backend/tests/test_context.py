from app.generation.context import ContextBuilder
from app.models.document import DocumentChunk
from app.retrieval.index import SearchResult


def make_result(
    document_id: str,
    text: str,
    score: float,
) -> SearchResult:
    document = DocumentChunk(
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

    return SearchResult(
        document=document,
        score=score,
    )

def test_context_builder():
    results = [
        make_result(
            "1",
            "भारत की राजधानी नई दिल्ली है।",
            0.95,
        ),
        make_result(
            "2",
            "नई दिल्ली भारत का एक प्रमुख शहर है।",
            0.82,
        ),
    ]

    context = ContextBuilder().build(results)

    assert len(context.documents) == 2

    assert "भारत की राजधानी नई दिल्ली है।" in context.text
    assert "नई दिल्ली भारत का एक प्रमुख शहर है।" in context.text

    assert "[Source 1]" in context.text
    assert "[Source 2]" in context.text


def test_context_builder_respects_limit():
    results = [
        make_result(
            "1",
            "A" * 100,
            0.95,
        ),
        make_result(
            "2",
            "B" * 100,
            0.90,
        ),
    ]

    context = ContextBuilder(max_characters=120).build(results)

    assert len(context.documents) == 1
    assert "A" * 100 in context.text
    assert "B" * 100 not in context.text


def test_invalid_limit():
    try:
        ContextBuilder(max_characters=0)
        assert False
    except ValueError:
        pass