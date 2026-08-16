from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel

from app.pipeline.rag import RAGPipeline
from app.api.dependencies import get_rag_pipeline, get_stt
from app.stt.sarvam import SarvamSTT

import os
import tempfile
import time


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


class RetrievalResultModel(BaseModel):
    id: str
    score: float
    text: str
    language: str
    query_id: str
    is_selected: bool


class RetrievalDebugResponseModel(BaseModel):
    query: str
    results: list[RetrievalResultModel]


class VoiceRAGResponseModel(BaseModel):
    transcript: str
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


@router.post(
    "/rag/debug-retrieval",
    response_model=RetrievalDebugResponseModel,
)
def debug_retrieval(
    request: RAGRequest,
    rag: RAGPipeline = Depends(get_rag_pipeline),
):
    """Inspect the passages retrieved for a query without invoking the LLM."""
    results = rag.retrieve(request.query, top_k=request.top_k)

    return RetrievalDebugResponseModel(
        query=request.query,
        results=[
            RetrievalResultModel(
                id=result.document.id,
                score=result.score,
                text=result.document.text,
                language=result.document.language,
                query_id=result.document.query_id,
                is_selected=result.document.is_selected,
            )
            for result in results
        ],
    )


@router.post(
    "/rag/voice",
    response_model=VoiceRAGResponseModel,
)
async def voice_answer(
    audio: UploadFile = File(...),
    language: str = "en",
    top_k: int = 5,
    stt: SarvamSTT = Depends(get_stt),
    rag: RAGPipeline = Depends(get_rag_pipeline),
):
    suffix = os.path.splitext(audio.filename or "")[1]

    if not suffix:
        suffix = ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:

        temp_path = temp_file.name

        content = await audio.read()
        temp_file.write(content)

    try:
        # 1. Speech → Text
        stt_start = time.perf_counter()

        transcript = stt.transcribe(
            audio_path=temp_path,
            language=language,
        )

        stt_ms = (time.perf_counter() - stt_start) * 1000

        # 2. Text → RAG
        response = rag.answer(
            query=transcript,
            language=language,
            top_k=top_k,
        )

        # 3. Return combined result
        return VoiceRAGResponseModel(
            transcript=transcript,
            answer=response.answer,
            context=response.context,
            latency=LatencyResponseModel(
                embedding_ms=response.latency.embedding_ms,
                retrieval_ms=response.latency.retrieval_ms,
                context_ms=response.latency.context_ms,
                generation_ms=response.latency.generation_ms,
                total_ms=stt_ms + response.latency.total_ms,
            ),
        )

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
