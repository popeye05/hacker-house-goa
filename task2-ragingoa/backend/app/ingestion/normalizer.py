from typing import Any

from app.models.document import DocumentChunk


def normalize_record(
    record: dict[str, Any],
    language: str,
) -> list[DocumentChunk]:
    """
    Convert one MSMARCO-XI dataset record into normalized
    retrievable document chunks.

    Chunking is deliberately NOT performed here.

    The normalizer only converts the source dataset into
    our internal representation.
    """

    query_id = str(record["query_id"])
    query_type = str(record.get("query_type", ""))

    passages = record["passages"]

    documents: list[DocumentChunk] = []

    translated_passages = passages.get("Translated_passages", [])
    selected = passages.get("is_selected", [])

    for passage_id, text in enumerate(translated_passages):
        documents.append(
            DocumentChunk(
                id=f"{language}_{query_id}_{passage_id}",
                text=str(text),
                language=language,
                query_id=query_id,
                passage_id=str(passage_id),
                query_type=query_type,
                is_selected=bool(selected[passage_id])
                if passage_id < len(selected)
                else False,
                source="translated",
                metadata={
                    "source_lang": record.get("source_lang"),
                    "target_lang": record.get("target_lang"),
                },
            )
        )

    return documents