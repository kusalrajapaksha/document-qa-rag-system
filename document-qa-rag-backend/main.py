from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from uuid import uuid4
from services.pdf_service import extract_pdf_text
from services.chunking import chunk_pages
from services.embedding_service import search_chunks, get_embedding_model
from services.vector_store import store_chunks, search_stored_chunks, list_stored_documents, delete_stored_document
from services.llm_service import generate_answer

app = FastAPI(title="Personal Document Q&A")
MIN_SIMILARITY_SCORE = 0.35

@app.get("/")
def home():
    return {"message": "Document Q&A API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "document-qa"
        }
    
    
@app.get("/hello")
def hello(name: str = "Student"):
    return {
        "message": f"Hello, {name}!"
    }


@app.post("/document/preview")
async def preview_document(
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    file_bytes = await file.read()
    
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file.")
    
    try:
        result = extract_pdf_text(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

    return {
        "filename": file.filename,
        "page_count": result["page_count"],
        "pages": result["pages"]
    }
    
@app.post("/document/chunk-preview")
async def chunk_preview_document(
    file: UploadFile = File(...),
    chunk_size: int = 500,
    overlap: int = 50
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    file_bytes = await file.read()
    
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file.")

    try:
        result = extract_pdf_text(file_bytes)
        
        chunks = chunk_pages(result["pages"], chunk_size=chunk_size, overlap=overlap)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

    return {
        "filename": file.filename,
        "page_count": result["page_count"],
        "chunk_count": len(chunks),
        "chunks": chunks
    }
    
    
@app.post("/document/search-preview")
async def search_document(
    file: UploadFile = File(...),
    question: str = Form(...),
    chunk_size: int = 500,
    overlap: int = 50,
    top_k: int = 3
):
    
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    file_bytes = await file.read()
    
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file.")

    try:
        result = extract_pdf_text(file_bytes)
        chunks = chunk_pages(result["pages"], chunk_size=chunk_size, overlap=overlap)
        search_results = search_chunks(chunks, question, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

    return {
        "filename": file.filename,
        "question": question,
        "result_count": len(search_results),
        "results": search_results,
    }
    
@app.post("/document/index")
async def index_document(
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    file_bytes = await file.read()
    
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty PDF file.")

    try:
        document = extract_pdf_text(file_bytes)
        chunks = chunk_pages(document["pages"], chunk_size=500, overlap=50)
        # Here you would typically store the chunks in your vector store
        # For example: store_chunks(document_id=file.filename, chunks=chunks, embeddings=compute_embeddings(chunks))
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No valid chunks extracted from PDF file.")
        
        model = get_embedding_model()
        
        valid_chunks = [
            chunk for chunk in chunks if chunk["text"].strip()
        ]
        
        embeddings = model.encode(
            [chunk["text"] for chunk in valid_chunks],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        
        document_id = str(uuid4())
        
        count = store_chunks(document_id=document_id, chunks=valid_chunks, embeddings=embeddings)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF file: {str(e)}")

    return {
        "document_id": document_id,
        "filename": file.filename,
        "page_count": document["page_count"],
        "chunk_count": count,
        "status": "indexed"
    }
    
@app.post("/document/search")
async def search_indexed_document(
    question: str = Form(...),
    document_id: str | None = Form(default=None),
    top_k: int = Form(default=3),
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    if top_k < 1 or top_k > 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10.")
    
    model = get_embedding_model()
    
    question_embedding = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    
    results = search_stored_chunks(
        question_embedding=question_embedding,
        top_k=top_k,
        document_id=document_id
    )

    return {
        "question": question,
        "result_count": len(results),
        "results": results,
    }
    
    
    
    # cf33d159-9b47-4d67-b966-da0ec85dbb76
    
@app.post("/document/ask")
async def ask_document(
    question: str = Form(...),
    document_id: str | None = Form(default=None),
    top_k: int = Form(default=3),
):
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    if top_k < 1 or top_k > 10:
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 10.")

    model = get_embedding_model()

    question_embedding = model.encode(
        question,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    chunks = search_stored_chunks(
        question_embedding=question_embedding,
        top_k=top_k,
        document_id=document_id
    )
    
    chunks = [
        chunk
        for chunk in chunks 
        if chunk["similarity_score"] >= MIN_SIMILARITY_SCORE
]
    
    if not chunks:
        return {
            "question": question,
            "answer": (
                "I could not find relevant information "
                "in the indexed documents."
            ),
            "sources": [],
        }
        
    try:
        answer = generate_answer(
            question=question,
            chunks=chunks
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    sources = [
        {
            "document_id": chunk["document_id"],
            "page_number": chunk["page_number"],
            "chunk_id": chunk["chunk_id"],
            "similarity_score": chunk["similarity_score"],
            "text": chunk["text"],
        }
        for chunk in chunks
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }

@app.get("/documents")
async def list_documents():
    documents = list_stored_documents()

    return {
        "document_count": len(documents),
        "documents": documents,
    }

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    deleted = delete_stored_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "document_id": document_id,
        "status": "deleted",
    }
