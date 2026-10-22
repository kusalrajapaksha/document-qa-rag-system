# DocuMind — AI-Powered Document Assistant

DocuMind is a native iOS application that lets users upload PDF documents, ask natural-language questions, and inspect the passages used to generate answers.

It combines a **SwiftUI iOS client** with a **FastAPI backend** and a local retrieval-augmented generation (RAG) pipeline.

## Features

- Upload and index PDF documents
- Extract text and split it into overlapping chunks
- Generate semantic embeddings
- Store and retrieve chunks using ChromaDB
- Generate answers with a locally running Ollama language model
- Display source passages, page numbers, and similarity scores
- List and delete indexed documents
- Test core backend logic with pytest

## Architecture

1. **iOS:** SwiftUI, URLSession, async/await
2. **API:** Python and FastAPI
3. **PDF processing:** PyMuPDF
4. **Embeddings:** Sentence Transformers
5. **Vector database:** ChromaDB
6. **LLM inference:** Ollama with Qwen 2.5 3B
7. **Testing:** pytest and FastAPI TestClient

## How RAG works

1. Upload a PDF and extract its text.
2. Split the text into overlapping chunks.
3. Generate embeddings and store the chunks in ChromaDB.
4. Embed the user's question and retrieve relevant chunks.
5. Pass the retrieved context to the local language model.
6. Return the answer alongside source passages and page numbers.

## Local development

### Backend

Create and activate a Python virtual environment, then install the dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Install and start Ollama, then download the configured model:

```bash
ollama pull qwen2.5:3b
```

Start the API:

```bash
uvicorn main:app --reload --host 0.0.0.0
```

API documentation: `http://127.0.0.1:8000/docs`

Run the tests:

```bash
python -m pytest tests/ -v
```

### iOS

1. Open the Xcode project under `ios/`.
2. Configure the backend URL in `APIClient.swift`.
3. Start the backend and Ollama.
4. Run DocuMind in the iOS Simulator.

For a physical iPhone, configure the Mac's reachable local network address instead of `127.0.0.1`. Configure transport security appropriately for your development environment.

## Limitations

- Answer quality depends on retrieval quality and the selected language model.
- Similarity scores measure semantic similarity; they do not guarantee factual correctness.
- The current development setup is intended for local use, not public deployment.
- The local Ollama model must be running for answer generation.

## Future improvements

- Better retrieval evaluation and answer verification
- Improved document metadata and search
- Streaming responses
- Secure authentication and multi-user document isolation

## License

Choose a license appropriate for your intended use and distribution.
