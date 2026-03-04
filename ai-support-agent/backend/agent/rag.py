"""
RAG (Retrieval Augmented Generation) module for ShopNest AI Support Agent
Uses FAISS vector store with sentence-transformers for semantic search
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import Config

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
FAQ_FILE_PATH = BASE_DIR / "data" / "faq.txt"
FAISS_INDEX_PATH = BASE_DIR / "faiss_index"

# Global vector store instance
vector_store = None


def load_faq_documents():
    """
    Load and read the FAQ text file

    Returns:
        str: Content of the FAQ file
    """
    print(f"📄 Loading FAQ file from: {FAQ_FILE_PATH}")

    if not FAQ_FILE_PATH.exists():
        raise FileNotFoundError(f"FAQ file not found at {FAQ_FILE_PATH}")

    with open(FAQ_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"✅ Loaded {len(content)} characters from FAQ file")
    return content


def chunk_documents(text: str):
    """
    Split text into chunks using RecursiveCharacterTextSplitter

    Args:
        text: Text content to split

    Returns:
        list[str]: List of text chunks
    """
    chunk_size = Config.RAG_CHUNK_SIZE
    chunk_overlap = Config.RAG_CHUNK_OVERLAP

    print(f"✂️  Chunking text with size={chunk_size}, overlap={chunk_overlap}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_text(text)
    print(f"✅ Created {len(chunks)} text chunks")

    return chunks


def create_embeddings_model():
    """
    Initialize the sentence-transformers embedding model

    Returns:
        HuggingFaceEmbeddings: Embedding model instance
    """
    print(f"🤖 Loading sentence-transformers model: {Config.RAG_EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=Config.RAG_EMBEDDING_MODEL,
        model_kwargs={'device': Config.RAG_EMBEDDING_DEVICE},
        encode_kwargs={'normalize_embeddings': True}
    )

    print("✅ Embeddings model loaded successfully")
    return embeddings


def build_faiss_index(chunks: list[str], embeddings):
    """
    Build a new FAISS index from text chunks

    Args:
        chunks: List of text chunks
        embeddings: Embeddings model instance

    Returns:
        FAISS: Vector store instance
    """
    print("🔨 Building new FAISS index from chunks...")

    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    print("✅ FAISS index built successfully")
    return vector_store


def save_faiss_index(vector_store, path: Path):
    """
    Persist FAISS index to disk

    Args:
        vector_store: FAISS vector store instance
        path: Directory path to save the index
    """
    print(f"💾 Saving FAISS index to: {path}")

    # Create directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(path))
    print("✅ FAISS index saved successfully")


def load_faiss_index(path: Path, embeddings):
    """
    Load existing FAISS index from disk

    Args:
        path: Directory path where index is stored
        embeddings: Embeddings model instance

    Returns:
        FAISS: Loaded vector store instance
    """
    print(f"📂 Loading existing FAISS index from: {path}")

    vector_store = FAISS.load_local(
        folder_path=str(path),
        embeddings=embeddings
    )

    print("✅ FAISS index loaded successfully")
    return vector_store


def initialize_rag_system():
    """
    Initialize the RAG system by either loading existing index or building new one

    Returns:
        FAISS: Vector store instance
    """
    global vector_store

    print("\n" + "="*60)
    print("🚀 Initializing RAG System for ShopNest Support Agent")
    print("="*60 + "\n")

    # Create embeddings model
    embeddings = create_embeddings_model()

    # Check if FAISS index already exists
    if FAISS_INDEX_PATH.exists() and (FAISS_INDEX_PATH / "index.faiss").exists():
        print("🔍 Existing FAISS index found!")
        vector_store = load_faiss_index(FAISS_INDEX_PATH, embeddings)
    else:
        print("🆕 No existing index found. Building new FAISS index...")

        # Load FAQ content
        faq_content = load_faq_documents()

        # Chunk the content
        chunks = chunk_documents(faq_content)

        # Build FAISS index
        vector_store = build_faiss_index(chunks, embeddings)

        # Save for future use
        save_faiss_index(vector_store, FAISS_INDEX_PATH)

    print("\n" + "="*60)
    print("✅ RAG System Initialization Complete!")
    print("="*60 + "\n")

    return vector_store


def retrieve_relevant_chunks(query: str, k: int = None) -> list[str]:
    """
    Retrieve the top-k most relevant text chunks for a given query

    Args:
        query: User query string
        k: Number of top results to return (uses Config.RAG_RETRIEVAL_K if not provided)

    Returns:
        list[str]: List of relevant text chunks
    """
    global vector_store

    if vector_store is None:
        raise RuntimeError("RAG system not initialized. Call initialize_rag_system() first.")

    if k is None:
        k = Config.RAG_RETRIEVAL_K

    print(f"🔍 Searching for top {k} relevant chunks for query: '{query[:50]}...'")

    # Perform similarity search
    results = vector_store.similarity_search(query, k=k)

    # Extract text content from results
    chunks = [doc.page_content for doc in results]

    print(f"✅ Retrieved {len(chunks)} relevant chunks")

    return chunks


# Initialize RAG system on module import
vector_store = initialize_rag_system()
