
from dotenv import load_dotenv

load_dotenv()
from app.embeddings.model import EmbeddingModel
from app.generation.context import ContextBuilder
from app.generation.generator import SarvamAnswerGenerator
from app.pipeline.rag import RAGPipeline
from app.retrieval.retriever import Retriever
from app.stt.sarvam import SarvamSTT


_stt: SarvamSTT | None = None
_rag_pipeline: RAGPipeline | None = None

def get_stt() -> SarvamSTT:
    global _stt

    if _stt is None:
        print("Initializing Sarvam STT...")
        _stt = SarvamSTT()
        print("Sarvam STT ready.")

    return _stt


def get_rag_pipeline() -> RAGPipeline:
    global _rag_pipeline

    if _rag_pipeline is None:
        print("Initializing RAG pipeline...")

        # 1. Load embedding model
        embedding_model = EmbeddingModel()

        # 2. Create retriever + FAISS index
        retriever = Retriever(
            embedding_model=embedding_model,
            index_path="data/index",
        )


      
        context_builder = ContextBuilder(
            max_characters=8000,
        )

        #Using the Sarvam Answe Generator
        generator = SarvamAnswerGenerator()

        # 7. Assemble complete RAG pipeline
        _rag_pipeline = RAGPipeline(
            retriever=retriever,
            context_builder=context_builder,
            generator=generator,
        )

        print("RAG pipeline ready.")

    return _rag_pipeline

