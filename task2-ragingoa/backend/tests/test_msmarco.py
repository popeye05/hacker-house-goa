import json

from app.data.msmarco import MSMARCOXIAdapter


def test_msmarco_record_conversion():
    with open("tests/fixtures/msmarco_sample.json", encoding="utf-8") as file:
        record = json.load(file)

    adapter = MSMARCOXIAdapter()

    documents = adapter.record_to_documents(record)

    assert len(documents) == 2

    assert documents[0].id == "123_0"
    assert documents[0].text == "भारत की राजधानी नई दिल्ली है।"
    assert documents[0].language == "hi"
    assert documents[0].query_id == "123"
    assert documents[0].passage_id == "0"
    assert documents[0].is_selected is True

    assert documents[1].is_selected is False


def test_msmarco_streaming_conversion():
    with open("tests/fixtures/msmarco_sample.json", encoding="utf-8") as file:
        record = json.load(file)

    adapter = MSMARCOXIAdapter()

    documents = list(
        adapter.iter_documents(iter([record]))
    )
from app.data.msmarco import MSMARCOXIReader


def test_extract_string_passage():
    text, selected = MSMARCOXIReader._extract_passage(
        "India is a country."
    )

    assert text == "India is a country."
    assert selected is False


def test_extract_structured_passage():
    passage = {
        "text": "New Delhi is the capital of India.",
        "is_selected": True,
    }

    text, selected = MSMARCOXIReader._extract_passage(
        passage
    )

    assert text == "New Delhi is the capital of India."
    assert selected is True


def test_normalize_example():
    reader = MSMARCOXIReader()

    example = {
        "query_id": "123",
        "query_type": "DESCRIPTION",
        "source_lang": "en",
        "target_lang": "hi",
        "query": "भारत की राजधानी क्या है?",
        "Eng_Query": "What is the capital of India?",
        "Answer": "नई दिल्ली",
        "Eng_Answer": "New Delhi",
        "passages": [
            {
                "text": "नई दिल्ली भारत की राजधानी है।",
                "is_selected": True,
            },
            {
                "text": "मुंबई महाराष्ट्र की राजधानी है।",
                "is_selected": False,
            },
        ],
        "meta": {},
    }

    documents = reader._normalize_example(example)

    assert len(documents) == 2

    assert documents[0].text == "नई दिल्ली भारत की राजधानी है।"
    assert documents[0].is_selected is True

    assert documents[1].is_selected is False

    assert documents[0].query_id == "123"
    assert documents[0].language == "hi"
    assert len(documents) == 2