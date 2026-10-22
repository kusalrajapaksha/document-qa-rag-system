import json
import pytest
from urllib.error import URLError

from services.llm_service import generate_answer

class FakeResponse:
    """Simulate an HTTP response from Ollama."""
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return False
    
    def read(self):
        return json.dumps({
            "message": {
                "content": "The document explains RAG. [Page 2]"
            }
        }).encode("utf-8")
    
def test_generate_answer_returns_model_response(monkeypatch):
    captured = {}
     
    def fake_urlopen(request, timeout):
        captured["payload"] = json.loads(
            request.data.decode("utf-8")
        )
        captured["timeout"] = timeout
        return FakeResponse()
    
    monkeypatch.setattr("services.llm_service.urlopen", fake_urlopen)
    
    question = "What does the document explain?"
    
    chunks = [
        {
            "page_number": 2,
            "text": "RAG combines retrieval with language generation.",
        }
    ]
    
    answer = generate_answer(question, chunks)
    
    assert answer == "The document explains RAG. [Page 2]"
    
    payload = captured["payload"]
    
    assert payload["model"] == "qwen2.5:3b"
    assert payload["stream"] is False
    assert payload["messages"][1]["content"].find(question) >= 0
    assert (
        "RAG combines retrieval with language generation."
        in payload["messages"][1]["content"]
    )
    
def test_generate_answer_handles_ollama_connection_error(
    monkeypatch,
):
    def fake_urlopen(request, timeout):
        raise URLError("Connection refused")

    monkeypatch.setattr(
        "services.llm_service.urlopen",
        fake_urlopen,
    )

    chunks = [
        {
            "page_number": 1,
            "text": "Example document text.",
        }
    ]

    with pytest.raises(
        RuntimeError,
        match="Could not connect to Ollama",
    ):
        generate_answer("What is this about?", chunks)
