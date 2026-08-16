
import argparse
from pathlib import Path

from app.data.loader import MSMARCOXILoader
from app.data.msmarco import MSMARCOXIAdapter
from app.embeddings.model import EmbeddingModel
from app.retrieval.index import FAISSIndex



# Number of text passages embedded at once.
EMBED_BATCH_SIZE = 32


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a FAISS index from MSMARCO-XI.",
    )
    parser.add_argument("--language", default="hi", choices=("hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ne", "or", "as", "ur", "sa"))
    parser.add_argument("--split", default="validation", choices=("train", "validation"))
    parser.add_argument(
        "--max-records",
        type=int,
        default=100,
        help="Number of dataset records to index; use 0 for the entire split (default: 100).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/index"),
        help="Directory for index.faiss and documents.json (default: data/index).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.max_records < 0:
        raise ValueError("--max-records must be 0 or greater")

    print("Starting MSMARCO-XI index build...")
    print(f"Dataset: {args.language}/{args.split}")
    print(
        "Records: entire split"
        if args.max_records == 0
        else f"Records: first {args.max_records}"
    )


    # 1. Models
 

    embedding_model = EmbeddingModel()

    adapter = MSMARCOXIAdapter()

    # BGE-M3 produces 1024-dimensional embeddings.
    index = FAISSIndex(dimension=1024)

    #dataset

    loader = MSMARCOXILoader(
        split=args.split,
        language=args.language,
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

    
  

        if args.max_records and total_records >= args.max_records:
            break

    #

    if documents_batch:

        _process_batch(
            index=index,
            embedding_model=embedding_model,
            documents=documents_batch,
        )

        total_documents += len(documents_batch)


    args.output.mkdir(
        parents=True,
        exist_ok=True,
    )

    index.save(args.output)

    print()
    print("======================================")
    print("Index build complete")
    print("======================================")
    print(f"Records processed: {total_records}")
    print(f"Documents indexed: {total_documents}")
    print(f"Index location: {args.output}")
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

