# RAG in Goa — SarvamAI powered STT RAG

## Team: ** NerdRats**
**Event:** Hacker House Goa 2026 — Task #2

<img width="1907" height="843" alt="image" src="https://github.com/user-attachments/assets/844cc8c1-624f-4a98-8bd6-a2037ec8f692" />


## link: https://rag-in-goa-nerdrats.vercel.app/
A voice-first RAG system that transcribes spoken questions, retrieves semantically relevant passages from a 500,000-document Hindi corpus, and generates grounded, source-backed answers — with a live web frontend and a fully deployed backend API.

---

## Overview

The system accepts a spoken question, transcribes it to text, retrieves the most relevant passages from a vector database, and generates a natural-language answer using only the retrieved context. The pipeline is cross-lingual: questions and retrieved passages do not need to share a language, since retrieval is performed in a shared multilingual embedding space.

**Pipeline:** Voice input → Speech-to-Text → Vector retrieval → Context construction → Grounded answer generation → Response

---

## Architecture

### Backend
- **Framework:** FastAPI (Python)
- **Speech-to-Text:** Sarvam AI (`saaras:v4` model), supporting multiple Indian languages
- **Vector database:** Qdrant Cloud (hosted, on-disk collection)
- **Embedding model:** `intfloat/multilingual-e5-small` (384-dimensional multilingual embeddings)
- **Answer generation:** Sarvam AI (`sarvam-105b`), grounded strictly to retrieved context
- **Deployment:** Render (Web Service, free tier)

### Frontend
- **Framework:** React + TypeScript (Vite)
- **Deployment:** Vercel
- Records audio in-browser, sends it to the backend, and displays the transcript, generated answer, and response latency.

### Data
- **Source dataset:** [`ai4bharat/MSMARCO-XI`](https://huggingface.co/datasets/ai4bharat/MSMARCO-XI) — a multilingual, machine-translated adaptation of MS MARCO, covering 14 Indian languages plus English.
- **Indexed subset:** ~500,000 Hindi-language passages, drawn directly from the Hindi-specific parquet file (`train/hintrain.parquet`) rather than the full ~55.6 GB, 14-language dataset.

---

## Key Design Decisions

### Dataset scope
The full multilingual dataset (55+ GB, ~11.5 million rows) was far larger than could reasonably be indexed within the hackathon's time and compute constraints. Two scoping decisions kept the project tractable without compromising the core demonstration:

- **Single-language focus (Hindi):** The challenge brief did not mandate multilingual support, so narrowing to Hindi reduced embedding and storage load substantially while producing a more focused, defensible product narrative.
- **Passage cap (500,000):** Sized against Qdrant Cloud's free-tier storage ceiling (4 GB disk, 1 GB RAM), with on-disk vector storage enabled to keep the collection within budget while leaving headroom for indexing overhead.

### Retrieval architecture
An earlier local FAISS-based retrieval path (embedding model + FAISS index run inside the backend process) was replaced with Qdrant Cloud's server-side inference (`cloud_inference=True`). This means:
- The backend never loads an embedding model, FAISS, or PyTorch at runtime.
- Both indexed passages and incoming queries are embedded identically by Qdrant's hosted infrastructure, keeping query-time and index-time vectors consistent.
- The production backend's dependency footprint is minimal — comfortably inside Render's free-tier memory limit.

---

## Indexing Pipeline (Google Colab)

The one-time indexing job — turning raw Hindi passages into a searchable Qdrant collection — was run in Google Colab to take advantage of free GPU compute, separate from the always-on backend.

**Process:**
1. Downloaded the Hindi-only parquet file directly from Hugging Face Hub (`train/hintrain.parquet`, ~3.7 GB), avoiding the need to stream or download the full multilingual dataset.
2. Read the parquet file in batched row groups via `pyarrow.parquet.ParquetFile.iter_batches()` rather than loading it entirely into memory with `pandas`, to keep RAM usage flat regardless of file size.
3. Flattened each query row's nested passage list (`Translated_passages`) into individual retrievable units.
4. Generated embeddings locally on Colab's GPU using `sentence-transformers` with the `intfloat/multilingual-e5-small` model — substantially faster than relying on Qdrant's server-side inference for a one-time bulk job of this size.
5. Uploaded embeddings and payloads to Qdrant Cloud in batches of 256, using integer point IDs (Qdrant requires point IDs to be an unsigned integer or UUID; the original composite passage identifier was retained inside the payload for traceability).
6. Created the Qdrant collection with `on_disk=True` for both vectors and payload, keeping the deployment within free-tier storage limits.

**Result:** 500,224 Hindi passages indexed in approximately 90 minutes (~92 passages/second on a Colab GPU runtime).

### Issues encountered and resolved during indexing
- **Wrong dataset identifier/config:** The dataset's per-language `load_dataset` config shortcuts (e.g., `"hi"`) were not available; the correct approach was loading the specific per-language parquet file directly via `data_files`.
- **Streaming hangs:** Streaming reads of the parquet file via `datasets` intermittently stalled, likely due to unauthenticated Hugging Face Hub rate limits combined with range-request behavior. Resolved by downloading the file directly instead of streaming.
- **Memory crashes:** `pandas.read_parquet()` on the full file caused Colab kernel crashes (nested list columns expanding into memory-heavy Python objects). Resolved by switching to batched `pyarrow` reads.
- **Invalid point IDs:** Qdrant rejected composite string IDs (e.g., `"query123_2"`); resolved by using a plain incrementing integer ID and preserving the original identifier as a payload field.

---

## Retrieval and Generation

- **Retrieval:** `QdrantRetriever` queries Qdrant Cloud using `cloud_inference`, embedding the raw query text with the same model used at index time, and returns the top-k most similar passages by cosine similarity.
- **Context construction:** Retrieved passages are assembled into a bounded, labeled context block (`[Source N]`), capped at a configurable character limit to avoid exceeding the generation model's context window.
- **Answer generation:** The Sarvam-hosted LLM is prompted to answer strictly from the supplied context, explicitly instructed not to invent facts and to state when the context is insufficient — favoring a grounded refusal over hallucination when retrieved passages do not directly answer a narrowly-phrased question.

---

## Deployment

### Backend — Render
- **Root directory:** points to the backend subfolder within the monorepo.
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment variables:** `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION`, `QDRANT_EMBEDDING_MODEL`, `SARVAM_API_KEY`

**Requirements optimization:** The original `requirements.txt` — accumulated from local development, including the one-time Colab indexing dependencies — included PyTorch, Transformers, Sentence-Transformers, FAISS, and related packages. None of these are used by the running backend, since retrieval is fully delegated to Qdrant's server-side inference. Their presence caused the initial deployment to exceed Render's free-tier 512 MB memory limit during Python's import phase, before the application could even bind a port.

Resolving this required tracing the backend's actual runtime import graph and removing incidental dependencies on the unused local-FAISS retrieval path:
- Separated the `SearchResult` data class from the FAISS-index module it was co-located with, so importing it no longer required importing `faiss`.
- Converted an unused type hint (`retriever: Retriever`) in the RAG pipeline's constructor to a `TYPE_CHECKING`-only import, preventing the legacy `Retriever`/`EmbeddingModel` module chain — which pulled in `sentence-transformers` and PyTorch — from loading at runtime.
- Reduced `requirements.txt` to only the packages actually imported by the live request path: `fastapi`, `uvicorn`, `pydantic`, `python-multipart`, `python-dotenv`, `qdrant-client`, `sarvamai`.

This brought the deployed image comfortably within the free-tier memory limit.

### Frontend — Vercel
- **Root directory:** points to the frontend subfolder within the monorepo.
- **Framework:** auto-detected Vite build.
- **Environment variable:** `VITE_API_URL`, set to the deployed Render backend URL. The frontend's API base URL was refactored from a hardcoded `localhost` reference to read from this environment variable, allowing the same codebase to run against a local backend during development and the deployed backend in production without code changes.

### Cross-Origin Configuration
The backend's CORS middleware allowlist was updated to include the deployed Vercel origin alongside the local development origin, required for the browser to permit requests from the production frontend to the production backend.

---

## Issues Encountered During Deployment

- **Out-of-memory crash on first deploy:** Caused by the unoptimized `requirements.txt`, as described above; resolved by trimming dependencies to the runtime-required set.
- **Apparent deployment hang:** A subsequent deploy appeared to freeze with no log output and no port binding. Diagnosed by process of elimination — verifying the trimmed requirements had deployed correctly, confirming `main.py` and the start command were correctly configured, and ultimately resolved by clearing Render's build cache and redeploying, consistent with a stale cached build layer.
- **403 Forbidden from Sarvam API in production:** The deployed backend's speech-to-text calls failed authentication despite an apparently correct API key. Root cause was the environment variable value being wrapped in quotation marks in Render's dashboard; environment variable values are treated as literal strings, so the quotes were sent as part of the key itself. Resolved by storing the raw key value with no surrounding quotes.
- **CORS error masking a server error:** A browser-reported CORS failure was initially mistaken for a CORS configuration issue. The underlying cause was a 500 Internal Server Error on the backend (the Sarvam authentication failure above); FastAPI does not reliably attach CORS headers to unhandled exception responses, which the browser surfaces as a CORS block rather than the underlying server error. Resolved by reading the backend's server-side logs directly rather than relying on the browser's error message.

---

## Known Limitations

- **Coverage gaps:** As an indexed subset (500k of several million available Hindi passages), narrowly-phrased factual questions may not always retrieve a passage containing the specific answer, even when topically related passages exist. The system is designed to decline rather than hallucinate in this case, which is treated as correct grounded behavior rather than a defect.
- **Single-language corpus:** Only Hindi passages are indexed. Queries in other languages are still transcribed and embedded correctly (embeddings are multilingual), but no non-Hindi source material exists to retrieve.
- **Legacy code paths:** An earlier local-FAISS retrieval implementation remains in the codebase as dead code, superseded by the Qdrant-based retriever, and is excluded from the deployed dependency graph.

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend framework | React + TypeScript (Vite) |
| Frontend hosting | Vercel |
| Backend framework | FastAPI (Python) |
| Backend hosting | Render |
| Vector database | Qdrant Cloud |
| Embedding model | `intfloat/multilingual-e5-small` |
| Speech-to-text | Sarvam AI (`saaras:v4`) |
| Answer generation | Sarvam AI (`sarvam-105b`) |
| Source dataset | `ai4bharat/MSMARCO-XI` (Hugging Face) |
| Indexing environment | Google Colab (GPU runtime) |

---

## Acknowledgements

Built for Hacker House Goa 2026 by Team NerdRats, using the AI4Bharat MSMARCO-XI dataset and Sarvam AI's speech and language models.
