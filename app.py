import streamlit as st

from src.config import DATA_DIR
from src.document_loader import load_documents
from src.text_splitter import make_chunks
from src.vector_store import build_vector_store, get_collection, query_vector_store
from src.rag_chain import generate_answer, unique_sources


st.set_page_config(
    page_title="Internal Document RAG Assistant",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Internal Document RAG Assistant")
st.write(
    "Ask questions over internal documents and get grounded answers with source attribution."
)

with st.sidebar:
    st.header("Index status")
    try:
        collection = get_collection()
        count = collection.count()
        st.success(f"Indexed chunks: {count}")
    except Exception as exc:
        st.error(f"Vector database not ready: {exc}")
        count = 0

    st.header("Documents folder")
    st.code(str(DATA_DIR), language="text")

    col1, col2 = st.columns(2)
    if col1.button("Update index"):
        with st.spinner("Loading, chunking, embedding, and indexing new documents..."):
            documents = load_documents(DATA_DIR)
            chunks = make_chunks(documents)
            indexed_count = build_vector_store(chunks)
        st.success(f"Index updated. Total chunks: {indexed_count}.")
    if col2.button("Rebuild from scratch"):
        with st.spinner("Rebuilding entire index..."):
            documents = load_documents(DATA_DIR)
            chunks = make_chunks(documents)
            indexed_count = build_vector_store(chunks, force_rebuild=True)
        st.success(f"Rebuilt index with {indexed_count} chunks. Refresh if needed.")

st.subheader("Ask a question")
question = st.text_input(
    "Question",
    placeholder="Example: How many annual leave days are employees eligible for?",
)

top_k = st.slider("Number of retrieved chunks", min_value=2, max_value=8, value=5)

if st.button("Generate answer", type="primary"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Retrieving relevant document chunks..."):
            retrieved_chunks = query_vector_store(question, top_k=top_k)

        if not retrieved_chunks:
            st.error("No indexed content found. Click 'Update index' or run `python ingest.py` first.")
        else:
            with st.spinner("Generating grounded answer..."):
                answer = generate_answer(question, retrieved_chunks)

            st.subheader("Answer")
            st.write(answer)

            st.subheader("Source documents")
            for source in unique_sources(retrieved_chunks):
                st.markdown(f"- `{source}`")

            with st.expander("View retrieved chunks"):
                for i, chunk in enumerate(retrieved_chunks, start=1):
                    st.markdown(f"### Result {i}")
                    st.markdown(f"**Source:** `{chunk['source']}` | **Chunk:** {chunk['chunk_index']}")
                    st.markdown(f"**Distance:** `{chunk['distance']:.4f}`")
                    st.write(chunk["text"])
