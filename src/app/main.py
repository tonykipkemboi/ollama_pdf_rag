"""
Streamlit application for PDF-based Retrieval-Augmented Generation (RAG) using Ollama + LangChain.

This application allows users to upload a PDF, process it,
and then ask questions about the content using a selected language model.
"""

import logging
import os
import re
import shutil
import tempfile
import warnings

import ollama
import pdfplumber
import streamlit as st

# Suppress torch warning
warnings.filterwarnings("ignore", category=UserWarning, message=".*torch.classes.*")

from typing import Any, Dict, List, Optional, Tuple

from components import chat, pdf_viewer, sidebar
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Set protobuf environment variable to avoid error messages
# This might cause some issues with latency but it's a tradeoff
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Define persistent directory for ChromaDB
PERSIST_DIRECTORY = os.path.join("data", "vectors")

CHUNK_SIZE = 7000
CHUNK_OVERLAP = 150

# Streamlit page configuration
st.set_page_config(
    page_title="MicroStep ChatBot using RAG",
    page_icon="🎈",
    layout="wide",
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

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(data)
    logger.info("Document split into chunks")

    # Updated embeddings configuration with persistent storage
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name=f"pdf_{hash(file_upload.name)}",  # Unique collection name per file
    )
    logger.info("Vector DB created with persistent storage")

    shutil.rmtree(temp_dir)
    logger.info(f"Temporary directory {temp_dir} removed")
    return vector_db


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
        vector_db.as_retriever(), llm, prompt=QUERY_PROMPT
    )

    # 🔹 **Manually Retrieve Context for Debugging**
    retrieved_docs = retriever.invoke(question)  # Retrieve documents
    retrieved_context = "\n\n".join(
        [doc.page_content for doc in retrieved_docs]
    )  # Extract text

    # logger.info(f"Retrieved Context:\n{retrieved_context}")  # Log the retrieved context

    # RAG prompt template
    template = """Answer the question based ONLY on the following context:
    {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # 🔹 **Manually Format the Prompt Before Sending to LLM**
    formatted_prompt = prompt.format(context=retrieved_context, question=question)
    logger.info(f"Final Input Prompt Sent to LLM:\n{formatted_prompt}")

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
    st.subheader("🧠 MicroStep ChatBot using RAG", divider="gray", anchor=False)

    # Get available models
    models_info = ollama.list()
    available_models = extract_model_names(models_info)

    # Create layout
    col1, col2 = st.columns([1.5, 2])

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "vector_db" not in st.session_state:
        st.session_state["vector_db"] = None
    if "use_sample" not in st.session_state:
        st.session_state["use_sample"] = False

    # Model selection
    if available_models:
        selected_model = col2.selectbox(
            "Pick a model available locally on your system ↓",
            available_models,
            key="model_select",
        )

    st.sidebar.header("Upload & Zoom")

    # Add checkbox for sample PDF
    use_sample = st.sidebar.toggle("Use sample PDF (CV.pdf)", key="sample_checkbox")

    # Clear vector DB if switching between sample and upload
    if use_sample != st.session_state.get("use_sample"):
        if st.session_state["vector_db"] is not None:
            st.session_state["vector_db"].delete_collection()
            st.session_state["vector_db"] = None
            st.session_state["pdf_pages"] = None
        st.session_state["use_sample"] = use_sample

    if use_sample:
        # Use the sample PDF
        sample_path = "data/pdfs/sample/cv.pdf"
        if os.path.exists(sample_path):
            if st.session_state["vector_db"] is None:
                with st.spinner("Processing sample PDF..."):
                    loader = UnstructuredPDFLoader(file_path=sample_path)
                    data = loader.load()
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
                    )
                    chunks = text_splitter.split_documents(data)
                    st.session_state["vector_db"] = Chroma.from_documents(
                        documents=chunks,
                        embedding=OllamaEmbeddings(model="nomic-embed-text"),
                        persist_directory=PERSIST_DIRECTORY,
                        collection_name="sample_pdf",
                    )
                    # Open and display the sample PDF
                    with pdfplumber.open(sample_path) as pdf:
                        st.session_state["pdf_pages"] = [
                            page.to_image().original for page in pdf.pages
                        ]
        else:
            st.error("Sample PDF file not found in the current directory.")
    else:
        # Regular file upload with unique key
        file_upload = st.sidebar.file_uploader(
            "Upload a PDF file ↓",
            type="pdf",
            accept_multiple_files=False,
            key="pdf_uploader",
        )

        if file_upload:
            if st.session_state["vector_db"] is None:
                with st.spinner("Processing uploaded PDF..."):
                    st.session_state["vector_db"] = create_vector_db(file_upload)
                    # Store the uploaded file in session state
                    st.session_state["file_upload"] = file_upload
                    # Extract and store PDF pages
                    with pdfplumber.open(file_upload) as pdf:
                        st.session_state["pdf_pages"] = [
                            page.to_image().original for page in pdf.pages
                        ]

    # Display PDF if pages are available
    if "pdf_pages" in st.session_state and st.session_state["pdf_pages"]:
        # PDF display controls
        zoom_level = st.sidebar.slider(
            "Zoom Level",
            min_value=100,
            max_value=1000,
            value=700,
            step=50,
            key="zoom_slider",
        )

        # Display PDF pages
        with col1:
            with st.container(height=700, border=True):
                for page_image in st.session_state["pdf_pages"]:
                    st.image(page_image, width=zoom_level)

    # Delete collection button
    delete_collection = col1.button(
        "⚠️ Delete collection", type="secondary", key="delete_button"
    )

    if delete_collection:
        delete_vector_db(st.session_state["vector_db"])
        col1.info("Collection deleted successfully.")

    # Chat interface
    with col2:
        message_container = st.container(height=560, border=True)

        # Display chat history
        for i, message in enumerate(st.session_state["messages"]):
            avatar = "🤖" if message["role"] == "assistant" else "😎"
            with message_container.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

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
                        if st.session_state["vector_db"] is not None:
                            response = process_question(
                                prompt, st.session_state["vector_db"], selected_model
                            )
                            # response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
                            st.markdown(response)
                        else:
                            st.warning("Please upload a PDF file first.")

                # Add assistant response to chat history
                if st.session_state["vector_db"] is not None:
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": response}
                    )

            except Exception as e:
                st.error(e, icon="⛔️")
                logger.error(f"Error processing prompt: {e}")
        else:
            if st.session_state["vector_db"] is None:
                st.warning("Upload a PDF file or use the sample PDF to begin chat...")


if __name__ == "__main__":
    main()
