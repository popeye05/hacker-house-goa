from dataclasses import dataclass

from app.generation.context import ContextBuilder
from app.generation.generator import AnswerGenerator
from app.retrieval.retriever import Retriever


@dataclass(frozen=True)
class RAGResponse:
    """
    Final response returned by the RAG pipeline.
    """

    answer: str
    context: str


class RAGPipeline:
    """
    Orchestrates retrieval, context construction,
    and answer generation.
    """

    def __init__(
        self,
        retriever: Retriever,
        context_builder: ContextBuilder,
        generator: AnswerGenerator,
    ):
        self.retriever = retriever
        self.context_builder = context_builder
        self.generator = generator

    def answer(
        self,
        query: str,
        language: str,
        top_k: int = 5,
    ) -> RAGResponse:

        if not query.strip():
            raise ValueError("query cannot be empty")

        results = self.retriever.retrieve(
            query,
            top_k=top_k,
        )

        context = self.context_builder.build(results)

        answer = self.generator.generate(
            query=query,
            context=context,
            language=language,
        )

        return RAGResponse(
            answer=answer,
            context=context.text,
        )