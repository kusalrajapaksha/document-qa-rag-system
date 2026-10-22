from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200

def test_document_endpoint():
    response = client.get("/documents")
    assert response.status_code == 200
    
def test_ask_rejects_empty_question():
    response = client.post(
        "/document/ask",
        data={"question": "   "},
    )

    assert response.status_code == 400