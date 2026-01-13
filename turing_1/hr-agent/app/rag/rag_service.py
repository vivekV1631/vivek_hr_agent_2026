"""
Lightweight RAG service using Chroma + sentence-transformers.
Provides functions to ingest local text files and retrieve relevant context
for a query.
"""
from pathlib import Path
from typing import List
import os

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
except Exception as e:
    # Inform developer which packages are required if import fails
    raise ImportError("Missing RAG dependencies. Install 'chromadb' and 'sentence-transformers'.")

DB_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "hr_docs")
EMBED_MODEL_NAME = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")

# Load a compact sentence-transformer for embeddings
_model = SentenceTransformer(EMBED_MODEL_NAME)
# Create a Chroma client that persists to disk (duckdb+parquet)
_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=DB_DIR))

# Ensure a collection exists; create if missing
try:
    _collection = _client.get_collection(COLLECTION_NAME)
except Exception:
    _collection = _client.create_collection(name=COLLECTION_NAME)


def _embed_texts(texts: List[str]):
    # Convert list of texts into embedding vectors
    # Returns a list of float vectors suitable for Chroma
    emb = _model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return emb.tolist()


def ingest_documents_from_folder(folder: str):
    """Read .txt files from folder and add to Chroma collection.

    This reads all .txt files in the folder, computes embeddings and stores
    documents and metadata into the Chroma collection. Returns ingestion status.
    """
    p = Path(folder)
    if not p.exists() or not p.is_dir():
        # Folder must exist and contain .txt documents
        return {"status": "no_folder"}

    docs = []
    ids = []
    metadatas = []

    # Read files deterministically (sorted) for reproducibility
    for f in sorted(p.glob("*.txt")):
        text = f.read_text(encoding="utf-8").strip()
        if not text:
            continue
        ids.append(str(f.name))
        docs.append(text)
        metadatas.append({"source": str(f.name)})

    if not docs:
        # Nothing to ingest
        return {"status": "no_docs"}

    # Compute embeddings for documents
    embeddings = _embed_texts(docs)

    # Delete any existing records with the same ids (idempotent ingest)
    try:
        _collection.delete(ids=ids)
    except Exception:
        # Ignore delete errors for first-time ingestion
        pass

    # Add documents, metadata and pre-computed embeddings to collection
    _collection.add(documents=docs, metadatas=metadatas, ids=ids, embeddings=embeddings)
    _client.persist()
    return {"status": "ingested", "count": len(docs)}


def get_relevant_context(query: str, top_k: int = 3) -> List[str]:
    """Return top_k most relevant document texts for given query.

    This performs a vector similarity query in Chroma and returns the
    matched document texts which can be prepended to an LLM prompt.
    """
    if not query:
        return []

    # Embed the query and run a nearest-neighbor search
    q_emb = _embed_texts([query])
    try:
        results = _collection.query(query_embeddings=q_emb, n_results=top_k, include=["documents", "metadatas"])
    except Exception:
        # On errors, return empty context rather than failing overall request
        return []

    docs = []
    # results["documents"] is a list per query; flatten into a list of texts
    for doc_list in results.get("documents", []):
        for d in doc_list:
            docs.append(d)
    return docs
