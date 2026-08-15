from app.models.document import DocumentChunk
from app.embeddings.model import EmbeddingModel
from app.retrieval.retriever import Retriever
from app.generation.generator import FakeAnswerGenerator
from app.generation.context import ContextBuilder
from app.pipeline.rag import RAGPipeline


def make_rag():
    documents = [
        DocumentChunk(
            id="1",
            text="भारत की राजधानी नई दिल्ली है।",
            language="hi",
            query_id="123",
            passage_id="0",
            query_type="DESCRIPTION",
            is_selected=True,
            source="test",
            metadata={},
        ),
        DocumentChunk(
            id="2",
            text="मुंबई महाराष्ट्र की राजधानी है।",
            language="hi",
            query_id="123",
            passage_id="1",
            query_type="DESCRIPTION",
            is_selected=False,
            source="test",
            metadata={},
        ),
    ]

    model = EmbeddingModel()

    retriever = Retriever(
        embedding_model=model,
        dimension=1024,
    )

    retriever.add_documents(documents)

    context_builder = ContextBuilder(
        max_characters=8000
    )

    generator = FakeAnswerGenerator()

    return RAGPipeline(
        retriever=retriever,
        context_builder=context_builder,
        generator=generator,
    )


def test_rag_pipeline():
    rag = make_rag()

    response = rag.answer(
        query="What is the capital of India?",
        language="hi",
        top_k=2,
    )

    assert response.answer == "भारत की राजधानी नई दिल्ली है।"


def test_rag_pipeline_empty_query():
    rag = make_rag()

    try:
        rag.answer(
            query="",
            language="hi",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty query")