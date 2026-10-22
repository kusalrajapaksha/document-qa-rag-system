import pytest

from services.chunking import chunk_pages

def test_chunk_pages_splits_text_into_chunks():
    pages = [
        {
            "page_number": 1,
            "text": "one two three four five six seven",
        }
    ]
    
    chunks = chunk_pages(
        pages,
        chunk_size=4,
        overlap=1,
    )
    
    assert len(chunks) == 2
    assert chunks[0]["text"] == "one two three four"
    assert chunks[1]["text"] == "four five six seven"
    
    
def test_chunk_pages_preserves_page_number():
    pages = [
        {"page_number": 3, "text": "alpha beta gamma"}
    ]

    chunks = chunk_pages(
        pages,
        chunk_size=5,
        overlap=1,
    )

    assert chunks[0]["page_number"] == 3
    
def test_chunk_pages_returns_empty_for_empty_text():
    pages = [{"page_number": 1, "text": ""}]

    chunks = chunk_pages(pages)

    assert chunks == []


def test_chunk_pages_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_pages([], chunk_size=0)


def test_chunk_pages_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_pages([], chunk_size=4, overlap=4)