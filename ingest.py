from src.config import DATA_DIR
from src.document_loader import load_documents
from src.text_splitter import make_chunks
from src.vector_store import build_vector_store


def main():
    print("Loading documents...")
    documents = load_documents(DATA_DIR)
    print(f"Loaded {len(documents)} document(s).")

    print("Splitting documents into chunks...")
    chunks = make_chunks(documents)
    print(f"Created {len(chunks)} chunk(s).")

    print("Creating embeddings and saving to ChromaDB...")
    count = build_vector_store(chunks)
    print(f"Done. Indexed {count} chunk(s).")
    print("You can now run: streamlit run app.py")


if __name__ == "__main__":
    main()
