import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

OLLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"

def generate_answer(
    question: str,
    chunks: list[dict]
) -> str:
    """Generate an answer grounded in retrieved document chunks."""
    
    context_parts = []
    
    for chunk in chunks:
        context_parts.append(
            f"[Page {chunk['page_number']}]\n{chunk['text']}"
        )
        
    context = "\n\n".join(context_parts)
    
    messages = [
        {"role": "system", 
         "content": (
            "You are a document question-answering assistant. "
            "Answer using only the supplied document context. "
            "If the context does not contain the answer, say "
            "'I could not find the answer in the provided document.' "
            "Do not invent facts. Cite supporting page numbers "
            "using the format [Page 1]."
            )
        },
        {"role": "user", 
         "content": (
            f"Document context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Give a clear, concise answer with page citations."
            )
        }
    ]
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2}
    }

    request = Request(
        OLLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["message"]["content"].strip()
        
    except HTTPError as exc:
        raise RuntimeError(
            f"Ollama returned HTTP {exc.code}."
        ) from exc

    except URLError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure it is running."
        ) from exc

    except (KeyError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Ollama returned an invalid response."
        ) from exc