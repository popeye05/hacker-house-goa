from app.ingestion.normalizer import normalize_record


def test_normalize_record():
    record = {
        "query_id": "123",
        "query_type": "DESCRIPTION",
        "source_lang": "en",
        "target_lang": "hi",
        "passages": {
            "Translated_passages": [
                "यह पहला passage है।",
                "यह दूसरा passage है।",
            ],
            "is_selected": [1, 0],
        },
    }

    chunks = normalize_record(record, language="hi")

    assert len(chunks) == 2

    assert chunks[0].id == "hi_123_0"
    assert chunks[0].language == "hi"
    assert chunks[0].is_selected is True

    assert chunks[1].id == "hi_123_1"
    assert chunks[1].is_selected is False