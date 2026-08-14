from app.models.document import DocumentChunk


def test_document_chunk_creation():
    chunk = DocumentChunk(
        id="hi_123_0",
        text="भारत में सबसे अधिक वर्षा कहाँ होती है?",
        language="hi",
        query_id="123",
        passage_id="0",
        query_type="DESCRIPTION",
        is_selected=True,
        source="translated",
        metadata={"target_lang": "hi"},
    )

    assert chunk.id == "hi_123_0"
    assert chunk.language == "hi"
    assert chunk.is_selected is True
    assert chunk.metadata["target_lang"] == "hi"