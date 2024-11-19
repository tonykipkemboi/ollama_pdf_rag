"""
Streamlit application for PDF-based Retrieval-Augmented Generation (RAG) using Ollama + LangChain.

This application allows users to upload a PDF, process it,
and then ask questions about the content using a selected language model.
"""

import streamlit as st
import logging
import os
import ollama

from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.chat_models import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.documents import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from typing import List, Tuple, Dict, Any, Optional

# ub_a_bis_z_urls = [
#     'https://www.tu-braunschweig.de/ub/ausleihen-onlinezugriff',
#     'https://www.tu-braunschweig.de/ub/wir-ueber-uns/ub-von-a-z/allegro-c'
#     ]

ub_a_bis_z_urls = ['https://www.tu-braunschweig.de/ub/wir-ueber-uns/ub-von-a-z/allegro-c']


# Set protobuf environment variable to avoid error messages
# This might cause some issues with latency but it's a tradeoff
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

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


@st.cache_resource(show_spinner=True)
def extract_model_names(
    models_info: Dict[str, List[Dict[str, Any]]],
) -> Tuple[str, ...]:
    """
    Extract model names from the provided models information.

    Args:
        models_info (Dict[str, List[Dict[str, Any]]]): Dictionary containing information about available models.

    Returns:
        Tuple[str, ...]: A tuple of model names.
    """
    logger.info("Extracting model names from models_info")
    model_names = tuple(model["name"] for model in models_info["models"])
    logger.info(f"Extracted model names: {model_names}")
    return model_names


def create_docs_from_urls(urls) -> List[Document]:
    loader = WebBaseLoader(ub_a_bis_z_urls)
    docs = loader.load()
    return docs


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
    template = """Du bist eine künstliche Intelligenz, die in der Universitätsbibliothek (UB) der Technischen Universität Braunscheig (TUBS) arbeitet. Vor diesem Hintergrund, beantworten Sie die Frage NUR auf der Grundlage des folgenden Kontextes:
    {context}
    Question: {question}
    """
    
    # Create prompt
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


def delete_vector_db(vector_db: Optional[Chroma]) -> None:
    """
    Delete the vector database and clear related session state.

    Args:
        vector_db (Optional[Chroma]): The vector database to be deleted.
    """
    logger.info("Deleting vector DB")
    if vector_db is not None:
        vector_db.delete_collection()
        st.session_state.pop("pdf_pages", None)
        st.session_state.pop("file_upload", None)
        st.session_state.pop("vector_db", None)
        st.success("Collection and temporary files deleted successfully.")
        logger.info("Vector DB and related session state cleared")
        st.rerun()
    else:
        st.error("No vector database found to delete.")
        logger.warning("Attempted to delete vector DB, but none was found")

# Taken from:
# https://github.com/andrea-nuzzo/markdown-langchain-rag/blob/main/DocumentManager.py
def load_documents() -> List[Document]:
    loader = loader = DirectoryLoader("./documents", glob="./*.md", show_progress=True, loader_cls=UnstructuredMarkdownLoader)
    return loader.load()

def split_documents(docs) -> List[Document]:
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    all_sections = list()
    for doc in docs:
        sections = text_splitter.split_text(doc.page_content)
        all_sections.extend(sections)
    return all_sections

def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    st.subheader("🧠 Ollama UB RAG playground", divider="gray", anchor=False)

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
            key="model_select"
        )

    # Temp always regenerate
    #delete_vector_db(st.session_state["vector_db"]) 

    if st.session_state["vector_db"] is None:
        # docs = create_docs_from_urls(ub_a_bis_z_urls)
        docs = load_documents()
        if docs:
            for doc in docs:
                logger.info(doc.metadata)
                # logger.info(doc.page_content)
                
            if st.session_state["vector_db"] is None:
                # text_splitter = RecursiveCharacterTextSplitter(chunk_size=7500, chunk_overlap=100)
                # chunks = text_splitter.split_documents(sections)
                chunks = split_documents(docs)
                st.session_state["vector_db"] = Chroma.from_documents(
                    documents=chunks,
                    embedding=OllamaEmbeddings(model="nomic-embed-text"),
                    collection_name="myRAG"
                )
        else:
            st.error("No website data found.")

    
    # col1.markdown("Dies ist ein Test")


    # Delete collection button
    delete_collection = col1.button(
        "📚 Reload data", 
        type="secondary",
        key="delete_button"
    )

    if delete_collection:
        delete_vector_db(st.session_state["vector_db"])

    # Chat interface
    with col2:
        message_container = st.container(height=500, border=True)

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