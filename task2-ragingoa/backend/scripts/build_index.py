
from pathlib import Path

from app.data.loader import MSMARCOXILoader
from app.data.msmarco import MSMARCOXIAdapter
from app.embeddings.model import EmbeddingModel
from app.retrieval.index import FAISSIndex



LANGUAGE = "hi"
SPLIT = "validation"

MAX_RECORDS = 100

# Number of text passages embedded at once.
EMBED_BATCH_SIZE = 32

INDEX_DIR = Path("data/index")


def main() -> None:

    print("Starting MSMARCO-XI index build...")


    # 1. Models
 

    embedding_model = EmbeddingModel()

    adapter = MSMARCOXIAdapter()

    # BGE-M3 produces 1024-dimensional embeddings.
    index = FAISSIndex(dimension=1024)

    #dataset

    loader = MSMARCOXILoader(
        split=SPLIT,
        language=LANGUAGE,
        batch_size=2,
    )



    documents_batch = []

    total_records = 0
    total_documents = 0

    for record in loader.iter_records():

        documents = adapter.record_to_documents(record)

        if not documents:
            continue

        documents_batch.extend(documents)

        total_records += 1


        if len(documents_batch) >= EMBED_BATCH_SIZE:

            _process_batch(
                index=index,
                embedding_model=embedding_model,
                documents=documents_batch,
            )

            total_documents += len(documents_batch)

            print(
                f"Records: {total_records} | "
                f"Documents indexed: {total_documents}"
            )

           
            documents_batch.clear()

    
  

        if total_records >= MAX_RECORDS:
            break

    #

    if documents_batch:

        _process_batch(
            index=index,
            embedding_model=embedding_model,
            documents=documents_batch,
        )

        total_documents += len(documents_batch)


    INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    index.save(INDEX_DIR)

    print()
    print("======================================")
    print("Index build complete")
    print("======================================")
    print(f"Records processed: {total_records}")
    print(f"Documents indexed: {total_documents}")
    print(f"Index location: {INDEX_DIR}")
    print("======================================")


def _process_batch(
    index: FAISSIndex,
    embedding_model: EmbeddingModel,
    documents,
) -> None:

    texts = [
        document.text
        for document in documents
    ]

    embeddings = embedding_model.encode(texts)

    index.add(
        documents=documents,
        embeddings=embeddings,
    )


if __name__ == "__main__":
    main()

