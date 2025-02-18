"""RAG pipeline implementation."""

import logging
from pathlib import Path
from typing import Any

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from llm import LLMManager

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Manages the RAG (Retrieval Augmented Generation) pipeline."""

    def __init__(self, vector_db: Any, llm_manager: LLMManager):
        self.vector_db = vector_db
        self.llm_manager = llm_manager
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()

    def _setup_retriever(self) -> MultiQueryRetriever:
        """Set up the multi-query retriever."""
        try:
            return MultiQueryRetriever.from_llm(
                retriever=self.vector_db.as_retriever(),
                llm=self.llm_manager.llm,
                prompt=self.llm_manager.get_query_prompt(),
            )
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}")
            raise

    def _setup_chain(self) -> Any:
        """Set up the RAG chain."""
        try:
            return (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.llm_manager.get_rag_prompt()
                | self.llm_manager.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error setting up chain: {e}")
            raise

    def get_response(self, question: str) -> str:
        """Get response for a question using the RAG pipeline."""
        try:
            logger.info(f"Getting response for question: {question}")
            return self.chain.invoke(question)
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise


if __name__ == "__main__":
    from document import DocumentProcessor
    from langchain_community.vectorstores import Chroma
    from langchain_ollama import OllamaEmbeddings

    processor = DocumentProcessor()
    pdf_path = Path("../../data/pdfs/sample/scammer-agent.pdf")
    documents = processor.load_pdf(pdf_path)
    chunks = processor.split_documents(documents)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model="nomic-embed-text"),
        collection_name="local-rag",
    )

    llm_manager = LLMManager()
    rag_pipeline = RAGPipeline(vector_db=vector_db, llm_manager=llm_manager)

    question = "What is this paper about in 1 sentence?"
    response = rag_pipeline.get_response(question)
    print(f"Response: {response}")
