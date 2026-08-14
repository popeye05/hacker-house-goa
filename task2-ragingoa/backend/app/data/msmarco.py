from collections.abc import Iterator
from typing import Any

from app.models.document import DocumentChunk


class MSMARCOXIReader:
    """
    Converts raw MSMARCO-XI records into normalized DocumentChunk objects.
    """

    @staticmethod
    def _extract_passage(passage: Any) -> tuple[str, bool]:
        """
        Extract passage text and selection information.

        Supports:
        - plain string passages
        - passages using `passage_text`
        - passages using `text`
        """

        if isinstance(passage, str):
            return passage, False

        if isinstance(passage, dict):
            # Real MSMARCO-XI uses passage_text.
            # Tests/other representations may use text.
            text = passage.get(
                "passage_text",
                passage.get("text", ""),
            )

            is_selected = bool(
                passage.get("is_selected", False)
            )

            return str(text), is_selected

        return str(passage), False

    def _normalize_example(
        self,
        example: dict[str, Any],
    ) -> list[DocumentChunk]:
        """
        Convert one raw MSMARCO-XI example into DocumentChunk objects.
        """

        query_id = str(example.get("query_id", ""))
        query_type = str(example.get("query_type", ""))

        source_lang = str(example.get("source_lang", ""))
        target_lang = str(example.get("target_lang", ""))

        query = str(example.get("query", ""))
        english_query = str(example.get("Eng_Query", ""))

        answer = str(example.get("Answer", ""))
        english_answer = str(example.get("Eng_Answer", ""))

        passages = example.get("passages", [])

        if passages is None:
            passages = []

        documents: list[DocumentChunk] = []

        for passage_index, passage in enumerate(passages):
            text, is_selected = self._extract_passage(passage)

            if not text.strip():
                continue

            # Stable ID independent of language.
            document_id = f"{query_id}_{passage_index}"

            documents.append(
                DocumentChunk(
                    id=document_id,
                    text=text.strip(),
                    language=target_lang,
                    query_id=query_id,
                    passage_id=str(passage_index),
                    query_type=query_type,
                    is_selected=is_selected,
                    source="translated",
                    metadata={
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "query": query,
                        "english_query": english_query,
                        "answer": answer,
                        "english_answer": english_answer,
                        "meta": example.get("meta", {}),
                    },
                )
            )

        return documents

    def iter_documents(
        self,
        records: Iterator[dict[str, Any]],
    ) -> Iterator[DocumentChunk]:
        """
        Lazily convert multiple MSMARCO-XI records.

        This keeps ingestion streaming instead of loading the
        entire dataset into memory.
        """

        for record in records:
            yield from self._normalize_example(record)


class MSMARCOXIAdapter:
    """
    Public adapter for MSMARCO-XI ingestion.
    """

    def __init__(self) -> None:
        self.reader = MSMARCOXIReader()

    def record_to_documents(
        self,
        record: dict[str, Any],
    ) -> list[DocumentChunk]:
        """Convert one record into normalized documents."""

        return self.reader._normalize_example(record)

    def iter_documents(
        self,
        records: Iterator[dict[str, Any]],
    ) -> Iterator[DocumentChunk]:
        """Lazily convert records into normalized documents."""

        return self.reader.iter_documents(records)