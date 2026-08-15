from dataclasses import dataclass
from time import perf_counter

from app.generation.context import ContextBuilder
from app.generation.generator import AnswerGenerator
from app.retrieval.retriever import Retriever


@dataclass(frozen=True)
class RAGLatency:
    embedding_ms: float
    faiss_ms: float
    retrieval_ms: float
    context_ms: float
    generation_ms: float
    total_ms: float

@dataclass(frozen=True)
class RAGResponse:
    """
    Final response returned by the RAG pipeline.
    """

    answer: str
    context: str
    latency: RAGLatency


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

        total_start = perf_counter()

       
        # -------------------------
        results, embedding_ms, faiss_ms = (
        self.retriever.retrieve_with_latency(
                query,
                top_k=top_k,
            )
        )

        retrieval_ms = embedding_ms + faiss_ms
       
        # Context construction

        context_start = perf_counter()

        context = self.context_builder.build(results)

        context_end = perf_counter()

        context_ms = (context_end - context_start) * 1000


        # Answer generation

        generation_start = perf_counter()

        answer = self.generator.generate(
            query=query,
            context=context,
            language=language,
        )

        generation_end = perf_counter()

        generation_ms = (generation_end - generation_start) * 1000

      #Total------------------------------------------------
        total_end = perf_counter()

        total_ms = (total_end - total_start) * 1000

        latency = RAGLatency(
            embedding_ms=embedding_ms,
            faiss_ms=faiss_ms,
            retrieval_ms=retrieval_ms,
            context_ms=context_ms,
            generation_ms=generation_ms,
            total_ms=total_ms,
        )

        return RAGResponse(
            answer=answer,
            context=context.text,
            latency=latency,
        )