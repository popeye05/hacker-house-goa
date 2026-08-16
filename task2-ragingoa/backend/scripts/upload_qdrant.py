import json
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

INDEX_DOCUMENTS = Path("data/index/documents.json")
BATCH_SIZE = 64
VECTOR_SIZE = 384  # intfloat/multilingual-e5-small


def main() -> None:
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection = os.getenv("QDRANT_COLLECTION", "msmarco_xi")
    embedding_model = os.getenv(
        "QDRANT_EMBEDDING_MODEL",
        "intfloat/multilingual-e5-small",
    )

    if not url or not api_key:
        raise RuntimeError("QDRANT_URL and QDRANT_API_KEY must be set.")

    with INDEX_DOCUMENTS.open(encoding="utf-8") as file:
        documents = json.load(file)

    client = QdrantClient(
        url=url,
        api_key=api_key,
        cloud_inference=True,
        timeout=120,
    )

    if not client.collection_exists(collection):
        client.create_collection(
            collection_name=collection,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

    for start in range(0, len(documents), BATCH_SIZE):
        batch = documents[start : start + BATCH_SIZE]

        client.upload_points(
            collection_name=collection,
            points=[
                models.PointStruct(
                    id=start + offset,
                    vector=models.Document(
                        text=document["text"],
                        model=embedding_model,
                    ),
                    payload=document,
                )
                for offset, document in enumerate(batch)
            ],
            wait=True,
        )

        print(f"Uploaded {min(start + BATCH_SIZE, len(documents))}/{len(documents)}")

    print(f"Done: {len(documents)} passages uploaded to '{collection}'.")


if __name__ == "__main__":
    main()