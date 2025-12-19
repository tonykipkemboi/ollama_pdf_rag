"""
Streamlit application for PDF-based Retrieval-Augmented Generation (RAG) using Ollama + LangChain.

This application allows users to upload a PDF, process it,
and then ask questions about the content using a selected language model.
"""

import streamlit as st
import logging
import os
import tempfile
import shutil
import pdfplumber
import ollama
import warnings
from datetime import datetime
from pathlib import Path

# Suppress torch warning
warnings.filterwarnings('ignore', category=UserWarning, message='.*torch.classes.*')

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from typing import List, Tuple, Dict, Any, Optional

# Set protobuf environment variable to avoid error messages
# This might cause some issues with latency but it's a tradeoff
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Define persistent directory for ChromaDB
PERSIST_DIRECTORY = os.path.join("data", "vectors")

# Streamlit page configuration
st.set_page_config(
    page_title="Ollama PDF RAG Streamlit UI",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def extract_model_names(models_info: Any) -> Tuple[str, ...]:
    """
    Extract model names from the provided models information.

    Args:
        models_info: Response from ollama.list()

    Returns:
        Tuple[str, ...]: A tuple of model names.
    """
    logger.info("Extracting model names from models_info")
    try:
        # The new response format returns a list of Model objects
        if hasattr(models_info, "models"):
            # Extract model names from the Model objects
            model_names = tuple(model.model for model in models_info.models)
        else:
            # Fallback for any other format
            model_names = tuple()
            
        logger.info(f"Extracted model names: {model_names}")
        return model_names
    except Exception as e:
        logger.error(f"Error extracting model names: {e}")
        return tuple()


def create_vector_db(file_upload) -> Chroma:
    """
    Create a vector database from an uploaded PDF file.

    Args:
        file_upload (st.UploadedFile): Streamlit file upload object containing the PDF.

    Returns:
        Chroma: A vector store containing the processed document chunks.
    """
    logger.info(f"Creating vector DB from file upload: {file_upload.name}")
    temp_dir = tempfile.mkdtemp()

    path = os.path.join(temp_dir, file_upload.name)
    with open(path, "wb") as f:
        f.write(file_upload.getvalue())
        logger.info(f"File saved to temporary path: {path}")
        loader = UnstructuredPDFLoader(path)
        data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    logger.info("Document split into chunks")

    # Updated embeddings configuration with persistent storage
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=f"pdf_{hash(file_upload.name)}"  # Unique collection name per file
    )
    logger.info("Vector DB created with persistent storage")

    shutil.rmtree(temp_dir)
    logger.info(f"Temporary directory {temp_dir} removed")
    return vector_db


def generate_pdf_id(file_upload) -> str:
    """Generate unique ID for PDF."""
    timestamp = datetime.now().isoformat()
    return f"pdf_{abs(hash(file_upload.name + timestamp))}"


def process_and_store_pdf(file_upload, pdf_id: str, is_sample: bool = False):
    """Process single PDF and store in session state."""
    logger.info(f"Processing PDF: {file_upload.name} with ID: {pdf_id}")

    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, file_upload.name)

    # Save file
    with open(path, "wb") as f:
        f.write(file_upload.getvalue())
        logger.info(f"File saved to temporary path: {path}")

    # Load and chunk
    loader = UnstructuredPDFLoader(path)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
    chunks = text_splitter.split_documents(data)
    logger.info(f"Document split into {len(chunks)} chunks")

    # Add metadata to EACH chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata.update({
            "pdf_id": pdf_id,
            "pdf_name": file_upload.name,
            "chunk_index": i,
            "source_file": file_upload.name
        })

    # Create vector DB with unique collection
    collection_name = f"pdf_{abs(hash(file_upload.name + pdf_id))}"
    logger.info(f"Creating vector DB with collection name: {collection_name}")

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=collection_name
    )
    logger.info("Vector DB created with persistent storage")

    # Extract PDF pages
    with pdfplumber.open(file_upload) as pdf:
        pdf_pages = [page.to_image().original for page in pdf.pages]
    logger.info(f"Extracted {len(pdf_pages)} pages from PDF")

    # Store in session state
    st.session_state["pdfs"][pdf_id] = {
        "name": file_upload.name,
        "vector_db": vector_db,
        "pages": pdf_pages,
        "file_upload": file_upload,
        "collection_name": collection_name,
        "upload_timestamp": datetime.now(),
        "doc_count": len(chunks),
        "is_sample": is_sample
    }
    st.session_state["active_pdfs"].append(pdf_id)
    logger.info(f"PDF stored in session state with {len(chunks)} chunks")

    # Cleanup
    shutil.rmtree(temp_dir)
    logger.info(f"Temporary directory {temp_dir} removed")


def delete_pdf(pdf_id: str):
    """Delete single PDF and its collection."""
    if pdf_id in st.session_state["pdfs"]:
        pdf_data = st.session_state["pdfs"][pdf_id]
        logger.info(f"Deleting PDF: {pdf_data['name']} (ID: {pdf_id})")

        # Delete vector collection
        try:
            pdf_data["vector_db"].delete_collection()
            logger.info(f"Deleted collection: {pdf_data['collection_name']}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

        # Remove from state
        del st.session_state["pdfs"][pdf_id]
        st.session_state["active_pdfs"].remove(pdf_id)

        st.success(f"Deleted {pdf_data['name']}")


def delete_all_pdfs():
    """Delete all PDFs."""
    logger.info("Deleting all PDFs")
    for pdf_id in list(st.session_state["pdfs"].keys()):
        delete_pdf(pdf_id)
    st.session_state["pdfs"] = {}
    st.session_state["active_pdfs"] = []


def process_question_multi_pdf(
    question: str,
    pdfs_dict: Dict[str, Dict],
    selected_model: str
) -> Tuple[str, List[Dict]]:
    """Query across multiple PDFs with source attribution."""
    logger.info(f"Processing question across {len(pdfs_dict)} PDFs: {question}")

    llm = ChatOllama(model=selected_model)

    # Query prompt
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate 2
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}"""
    )

    # Retrieve from ALL PDF collections
    all_retrieved_docs = []
    for pdf_id, pdf_data in pdfs_dict.items():
        vector_db = pdf_data["vector_db"]

        retriever = MultiQueryRetriever.from_llm(
            vector_db.as_retriever(search_kwargs={"k": 3}),
            llm,
            prompt=QUERY_PROMPT
        )

        try:
            docs = retriever.get_relevant_documents(question)
            logger.info(f"Retrieved {len(docs)} documents from {pdf_data['name']}")
            # Ensure metadata
            for doc in docs:
                if "pdf_name" not in doc.metadata:
                    doc.metadata["pdf_name"] = pdf_data["name"]
                if "pdf_id" not in doc.metadata:
                    doc.metadata["pdf_id"] = pdf_id
            all_retrieved_docs.extend(docs)
        except Exception as e:
            logger.warning(f"Error retrieving from {pdf_data['name']}: {e}")

    logger.info(f"Total documents retrieved: {len(all_retrieved_docs)}")

    # Format context with source labels
    context_parts = []
    for doc in all_retrieved_docs[:10]:  # Top 10 chunks
        source = doc.metadata.get("pdf_name", "Unknown")
        context_parts.append(f"[Source: {source}]\n{doc.page_content}\n")

    formatted_context = "\n---\n".join(context_parts)

    # RAG prompt with source awareness
    template = """Answer the question based ONLY on the following context from multiple PDF documents.
    Each section is marked with its source document.

    When answering:
    1. Cite the source document name for each piece of information
    2. If information comes from multiple sources, mention all relevant sources
    3. If sources contradict, note the discrepancy and cite both

    Context:
    {context}

    Question: {question}

    Answer (include source citations):"""

    prompt = ChatPromptTemplate.from_template(template)
    chain = (
        {"context": lambda x: formatted_context, "question": lambda x: x}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(question)
    logger.info("Generated response with source attribution")

    # Extract source details
    source_details = [
        {
            "pdf_name": doc.metadata.get("pdf_name"),
            "pdf_id": doc.metadata.get("pdf_id"),
            "chunk_index": doc.metadata.get("chunk_index", 0)
        }
        for doc in all_retrieved_docs[:10]
    ]

    return response, source_details


def process_question(question: str, vector_db: Chroma, selected_model: str) -> str:
    """
    Process a user question using the vector database and selected language model.

    Args:
        question (str): The user's question.
        vector_db (Chroma): The vector database containing document embeddings.
        selected_model (str): The name of the selected language model.

    Returns:
        str: The generated response to the user's question.
    """
    logger.info(f"Processing question: {question} using model: {selected_model}")
    
    # Initialize LLM
    llm = ChatOllama(model=selected_model)
    
    # Query prompt template
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate 2
        different versions of the given user question to retrieve relevant documents from
        a vector database. By generating multiple perspectives on the user question, your
        goal is to help the user overcome some of the limitations of the distance-based
        similarity search. Provide these alternative questions separated by newlines.
        Original question: {question}""",
    )

    # Set up retriever
    retriever = MultiQueryRetriever.from_llm(
        vector_db.as_retriever(), 
        llm,
        prompt=QUERY_PROMPT
    )

    # RAG prompt template
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Create chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(question)
    logger.info("Question processed and response generated")
    return response


@st.cache_data
def extract_all_pages_as_images(file_upload) -> List[Any]:
    """
    Extract all pages from a PDF file as images.

    Args:
        file_upload (st.UploadedFile): Streamlit file upload object containing the PDF.

    Returns:
        List[Any]: A list of image objects representing each page of the PDF.
    """
    logger.info(f"Extracting all pages as images from file: {file_upload.name}")
    pdf_pages = []
    with pdfplumber.open(file_upload) as pdf:
        pdf_pages = [page.to_image().original for page in pdf.pages]
    logger.info("PDF pages extracted as images")
    return pdf_pages


def delete_vector_db(vector_db: Optional[Chroma]) -> None:
    """
    Delete the vector database and clear related session state.

    Args:
        vector_db (Optional[Chroma]): The vector database to be deleted.
    """
    logger.info("Deleting vector DB")
    if vector_db is not None:
        try:
            # Delete the collection
            vector_db.delete_collection()
            
            # Clear session state
            st.session_state.pop("pdf_pages", None)
            st.session_state.pop("file_upload", None)
            st.session_state.pop("vector_db", None)
            
            st.success("Collection and temporary files deleted successfully.")
            logger.info("Vector DB and related session state cleared")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting collection: {str(e)}")
            logger.error(f"Error deleting collection: {e}")
    else:
        st.error("No vector database found to delete.")
        logger.warning("Attempted to delete vector DB, but none was found")


def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    st.subheader("🧠 Ollama PDF RAG playground", divider="gray", anchor=False)

    # Get available models
    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    # Create layout
    col1, col2 = st.columns([1.5, 2])

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "pdfs" not in st.session_state:
        st.session_state["pdfs"] = {}
    if "active_pdfs" not in st.session_state:
        st.session_state["active_pdfs"] = []
    if "vector_db" not in st.session_state:
        st.session_state["vector_db"] = None
    if "use_sample" not in st.session_state:
        st.session_state["use_sample"] = False

    # Model selection
    if available_models:
        selected_model = col2.selectbox(
            "Pick a model available locally on your system ↓",
            available_models,
            key="model_select"
        )

    # PDF Management UI in Sidebar
    with st.sidebar:
        st.divider()
        st.subheader("📚 Loaded PDFs")

        if st.session_state.get("pdfs"):
            total_pdfs = len(st.session_state["pdfs"])
            total_chunks = sum(pdf["doc_count"] for pdf in st.session_state["pdfs"].values())

            st.metric("Total PDFs", total_pdfs)
            st.metric("Total Chunks", total_chunks)
            st.divider()

            # List PDFs
            for pdf_id in st.session_state["active_pdfs"]:
                pdf_data = st.session_state["pdfs"][pdf_id]

                with st.expander(f"📄 {pdf_data['name']}", expanded=False):
                    st.caption(f"Chunks: {pdf_data['doc_count']}")
                    st.caption(f"Pages: {len(pdf_data['pages'])}")

                    if st.button("🗑️ Delete", key=f"delete_{pdf_id}"):
                        delete_pdf(pdf_id)
                        st.rerun()

            st.divider()
            if st.button("🗑️ Delete All PDFs"):
                delete_all_pdfs()
                st.rerun()
        else:
            st.info("No PDFs loaded yet.")

    # Add checkbox for sample PDF
    use_sample = col1.toggle(
        "Use sample PDF (Scammer Agent Paper)", 
        key="sample_checkbox"
    )
    
    # Clear vector DB if switching between sample and upload
    if use_sample != st.session_state.get("use_sample"):
        if st.session_state["vector_db"] is not None:
            st.session_state["vector_db"].delete_collection()
            st.session_state["vector_db"] = None
            st.session_state["pdf_pages"] = None
        st.session_state["use_sample"] = use_sample

    if use_sample:
        # Use the sample PDF
        sample_pdf_path = Path("data/pdfs/sample/scammer-agent.pdf")
        if sample_pdf_path.exists():
            # Check if already loaded
            sample_id = "sample_pdf"
            if sample_id not in st.session_state.get("pdfs", {}):
                with st.spinner("Loading sample PDF..."):
                    # Create a file-like object
                    with open(sample_pdf_path, "rb") as f:
                        file_bytes = f.read()

                    # Create UploadedFile-like object
                    class SampleFile:
                        def __init__(self, path, content):
                            self.name = path.name
                            self._content = content

                        def getvalue(self):
                            return self._content

                    sample_file = SampleFile(sample_pdf_path, file_bytes)
                    process_and_store_pdf(sample_file, sample_id, is_sample=True)
        else:
            st.error("Sample PDF file not found in the current directory.")
    else:
        # Regular file upload with multi-file support
        file_uploads = col1.file_uploader(
            "Upload PDF files ↓",
            type="pdf",
            accept_multiple_files=True,
            key="pdf_uploader"
        )

        if file_uploads:
            for file_upload in file_uploads:
                pdf_id = generate_pdf_id(file_upload)

                # Skip if already processed
                if pdf_id not in st.session_state.get("pdfs", {}):
                    with st.spinner(f"Processing {file_upload.name}..."):
                        process_and_store_pdf(file_upload, pdf_id)

    # Stacked PDF Viewer
    if st.session_state.get("pdfs") and st.session_state.get("active_pdfs"):
        zoom_level = col1.slider(
            "Zoom Level",
            min_value=100,
            max_value=1000,
            value=700,
            step=50,
            key="zoom_slider"
        )

        with col1:
            with st.container(height=410, border=True):
                for pdf_id in st.session_state["active_pdfs"]:
                    if pdf_id not in st.session_state["pdfs"]:
                        continue

                    pdf_data = st.session_state["pdfs"][pdf_id]

                    # PDF header with metadata
                    st.markdown(f"### 📄 {pdf_data['name']}")
                    st.caption(
                        f"Uploaded: {pdf_data['upload_timestamp'].strftime('%Y-%m-%d %H:%M')} | "
                        f"Chunks: {pdf_data['doc_count']} | "
                        f"Pages: {len(pdf_data['pages'])}"
                    )

                    # Quick remove button
                    if st.button("🗑️ Remove", key=f"remove_{pdf_id}"):
                        delete_pdf(pdf_id)
                        st.rerun()

                    st.divider()

                    # Display all pages
                    for page_idx, page_image in enumerate(pdf_data['pages']):
                        st.caption(f"Page {page_idx + 1}")
                        st.image(page_image, width=zoom_level)

                    # Spacing between PDFs
                    st.markdown("---")
    else:
        col1.info("Upload PDF files to view them here.")

    # Delete collection button
    delete_collection = col1.button(
        "⚠️ Delete collection", 
        type="secondary",
        key="delete_button"
    )

    if delete_collection:
        delete_vector_db(st.session_state["vector_db"])

    # Chat interface
    with col2:
        message_container = st.container(height=500, border=True)

        # Display chat history
        for message in st.session_state["messages"]:
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with message_container.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

                # Show sources if available
                if message["role"] == "assistant" and "sources" in message:
                    st.divider()
                    st.caption("📚 Sources:")

                    sources_by_pdf = {}
                    for src in message["sources"]:
                        pdf_name = src.get("pdf_name", "Unknown")
                        if pdf_name not in sources_by_pdf:
                            sources_by_pdf[pdf_name] = 0
                        sources_by_pdf[pdf_name] += 1

                    for pdf_name, count in sources_by_pdf.items():
                        st.markdown(f"- **{pdf_name}** ({count} chunks)")

        # Chat input and processing
        if prompt := st.chat_input("Enter a prompt here...", key="chat_input"):
            try:
                # Add user message to chat
                st.session_state["messages"].append({"role": "user", "content": prompt})
                with message_container.chat_message("user", avatar="😎"):
                    st.markdown(prompt)

                # Process and display assistant response
                with message_container.chat_message("assistant", avatar="🤖"):
                    with st.spinner(":green[processing...]"):
                        if st.session_state.get("pdfs"):
                            response, sources = process_question_multi_pdf(
                                prompt,
                                st.session_state["pdfs"],
                                selected_model
                            )
                            st.markdown(response)

                            # Display sources
                            if sources:
                                st.divider()
                                st.caption("📚 Sources:")

                                # Group by PDF
                                sources_by_pdf = {}
                                for src in sources:
                                    pdf_name = src.get("pdf_name", "Unknown")
                                    if pdf_name not in sources_by_pdf:
                                        sources_by_pdf[pdf_name] = 0
                                    sources_by_pdf[pdf_name] += 1

                                for pdf_name, count in sources_by_pdf.items():
                                    st.markdown(f"- **{pdf_name}** ({count} chunks)")
                        else:
                            st.warning("Please upload PDF files first.")
                            response = None
                            sources = None

                # Add assistant response to chat history with sources
                if response:
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })

            except Exception as e:
                st.error(e, icon="⛔️")
                logger.error(f"Error processing prompt: {e}")
        else:
            if not st.session_state.get("pdfs"):
                st.warning("Upload PDF files or use the sample PDF to begin chat...")


if __name__ == "__main__":
    main()