from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.pipeline.rag import RAGPipeline
from app.api.dependencies import get_rag_pipeline


router = APIRouter(
    prefix="/api/v1",
    tags=["RAG"],
)
class LatencyResponseModel(BaseModel):
    embedding_ms: float
    retrieval_ms: float
    context_ms: float
    generation_ms: float
    total_ms: float

class RAGRequest(BaseModel):
    query: str
    language: str
    top_k: int = 5


class RAGResponseModel(BaseModel):
    answer: str
    context: str
    latency: LatencyResponseModel


@router.post(
    "/rag/answer",
    response_model=RAGResponseModel,
)
def answer(
    request: RAGRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline),
):
    response = rag.answer(
        query=request.query,
        language=request.language,
        top_k=request.top_k,
    )

    return RAGResponseModel(
        answer=response.answer,
        context=response.context,
        latency=LatencyResponseModel(
            embedding_ms=response.latency.embedding_ms,
            retrieval_ms=response.latency.retrieval_ms,
            context_ms=response.latency.context_ms,
            generation_ms=response.latency.generation_ms,
            total_ms=response.latency.total_ms,
    ),
)