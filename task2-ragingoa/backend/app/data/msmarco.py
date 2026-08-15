
from typing import Any

from app.models.document import DocumentChunk


class MSMARCOXIAdapter:

    def record_to_documents(
        self,
        example: dict[str, Any],
    ) -> list[DocumentChunk]:

        query_id = str(example.get("query_id", ""))
        query_type = str(example.get("query_type", ""))

        source_lang = str(example.get("source_lang", ""))
        target_lang = str(example.get("target_lang", ""))

        query = str(example.get("query", ""))
        english_query = str(example.get("Eng_Query", ""))

        answer = str(example.get("Answer", ""))
        english_answer = str(example.get("Eng_Answer", ""))

        passages = example.get("passages", {})

        if not isinstance(passages, dict):
            return []

        translated_passages = passages.get(
            "Translated_passages",
            [],
        )

        selected_flags = passages.get(
            "is_selected",
            [],
        )

        if not isinstance(translated_passages, list):
            return []

        if not isinstance(selected_flags, list):
            selected_flags = []

        documents: list[DocumentChunk] = []

        for passage_index, passage in enumerate(
            translated_passages
        ):
            text = str(passage).strip()

            if not text:
                continue

            is_selected = False

            if passage_index < len(selected_flags):
                is_selected = bool(
                    selected_flags[passage_index]
                )

            document_id = f"{query_id}_{passage_index}"

            documents.append(
                DocumentChunk(
                    id=document_id,
                    text=text,
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
                    },
                )
            )

        return documents

