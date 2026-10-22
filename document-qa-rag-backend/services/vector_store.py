import chromadb
from chromadb.api.types import Where
from torch import chunk

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="document_chunks",
    metadata={"hnsw:space": "cosine"}
    )

def store_chunks(
    document_id: str,
    chunks: list[dict],
    embeddings,
) -> int:
    """Persist chunks and their precomputed embeddings."""
    
    valid_chunks = [
        chunk for chunk in chunks if chunk["text"].strip()
    ]
    
    if not valid_chunks:
        return 0

    collection.add(
        ids=[
            f"{document_id}_{chunk["chunk_id"]}" for chunk in valid_chunks
        ],
        documents=[
            chunk["text"] for chunk in valid_chunks
        ],
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "document_id": document_id,
                "chunk_id": chunk["chunk_id"],
                "page_number": chunk["page_number"],
                "word_count": chunk["word_count"]
            }
            for chunk in valid_chunks
        ]
    )

    return len(valid_chunks)

def search_stored_chunks(
    question_embedding,
    top_k: int = 3,
    document_id: str | None = None
) -> list[dict]:
    """Search stored vectors and return matching chunks."""
    
    total_chunks = collection.count()
    
    if total_chunks == 0 or top_k <= 0:
        return []

    filters: Where | None = (
        {"document_id": document_id}
        if document_id is not None else None
    )

    candidate_count = min(top_k * 3, total_chunks)
    
    result = collection.query(
        query_embeddings=[question_embedding.tolist()],
        n_results=candidate_count,
        where=filters,
        include=["documents", "metadatas", "distances"]
    )
    
    print(result)

    matches = []
    selected_word_sets = []

    ids = result["ids"][0] if result["ids"] else []
    document_rows = result["documents"] or []
    metadata_rows = result["metadatas"] or []
    distance_rows = result["distances"] or []

    if not ids or not document_rows or not metadata_rows or not distance_rows:
        return matches

    for chunk_id, chunk_text, metadata, distance in zip(
        ids,
        document_rows[0] or [],
        metadata_rows[0] or [],
        distance_rows[0] or [],
    ):
        if chunk_text is None or metadata is None:
            continue

        words = set(chunk_text.lower().split())

        # Skip chunks that are almost duplicates of an
        # already selected chunk.
        is_duplicate = False

        for selected_words in selected_word_sets:
            if not words or not selected_words:
                continue

            overlap = len(words & selected_words)
            similarity = overlap / len(words | selected_words)

            if similarity >= 0.80:
                is_duplicate = True
                break

        if is_duplicate:
            continue

        matches.append({
            "id": chunk_id,
            "document_id": metadata["document_id"],
            "chunk_id": metadata["chunk_id"],
            "page_number": metadata["page_number"],
            "word_count": metadata["word_count"],
            "text": chunk_text,
            "similarity_score": round(1 - distance, 4),
        })

        selected_word_sets.append(words)

        if len(matches) >= top_k:
            break

    return matches


def list_stored_documents() -> list[dict]:
    """List indexed documents and summarize their stored chunks."""
    result = collection.get(include=["metadatas"])
     
    documents = {}
    
    if not result["metadatas"]:
        return []
     
    for metadata in result["metadatas"]:
        document_id = metadata["document_id"]
         
        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "chunk_count": 0,
                "pages": set(),
            }
            
        documents[document_id]["chunk_count"] += 1
        documents[document_id]["pages"].add(metadata["page_number"])

    return [
        {
            "document_id": document["document_id"],
            "chunk_count": document["chunk_count"],
            "page_count": len(document["pages"]),
        }
        for document in documents.values()
    ]
    
def delete_stored_document(document_id: str) -> bool:
    """Delete all chunks belonging to one document."""
    existing = collection.get(
        where={"document_id": document_id},
        include=["metadatas"],
    )

    if not existing["ids"]:
        return False

    collection.delete(where={"document_id": document_id})
    return True