"""RAG query service."""
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from langchain_ollama import ChatOllama
import ollama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from ..database import PDFMetadata, ChatSession, ChatMessage
from ..config import settings


class RAGService:
    """Service for RAG operations."""

    def __init__(self):
        """Initialize RAG service."""
        self.persist_directory = settings.VECTOR_DB_DIR

    def query_multi_pdf(
        self,
        question: str,
        model: str,
        pdf_ids: Optional[List[str]],
        db: Session
    ) -> Tuple[str, List[Dict], List[str]]:
        """Query across multiple PDFs with source attribution.

        Args:
            question: User question
            model: LLM model to use
            pdf_ids: List of PDF IDs to query (None = all PDFs)
            db: Database session

        Returns:
            Tuple of (answer, sources, reasoning_steps)
        """
        reasoning_steps = []

        # Get PDF metadata
        query = db.query(PDFMetadata)
        if pdf_ids:
            query = query.filter(PDFMetadata.pdf_id.in_(pdf_ids))
        pdfs = query.all()

        if not pdfs:
            return "No PDFs found to query.", [], []

        reasoning_steps.append(f"📚 Searching across {len(pdfs)} PDF(s): {', '.join([p.name for p in pdfs])}")

        # Initialize LLM
        llm = ChatOllama(model=model)
        reasoning_steps.append(f"🤖 Using model: {model}")

        # Query prompt for multi-query retriever
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate 2
            different versions of the given user question to retrieve relevant documents from
            a vector database. By generating multiple perspectives on the user question, your
            goal is to help the user overcome some of the limitations of the distance-based
            similarity search. Provide these alternative questions separated by newlines.
            Original question: {question}"""
        )

        reasoning_steps.append("🔍 Generating alternative search queries...")

        # Retrieve from all collections
        all_docs = []
        embeddings = OllamaEmbeddings(model="nomic-embed-text")

        for pdf in pdfs:
            vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=embeddings,
                collection_name=pdf.collection_name
            )

            retriever = MultiQueryRetriever.from_llm(
                vector_db.as_retriever(search_kwargs={"k": 3}),
                llm,
                prompt=QUERY_PROMPT
            )

            try:
                reasoning_steps.append(f"📄 Retrieving from: {pdf.name}")
                # Use invoke instead of deprecated get_relevant_documents
                docs = retriever.invoke(question)
                # Ensure metadata is present
                for doc in docs:
                    if "pdf_name" not in doc.metadata:
                        doc.metadata["pdf_name"] = pdf.name
                    if "pdf_id" not in doc.metadata:
                        doc.metadata["pdf_id"] = pdf.pdf_id
                all_docs.extend(docs)
                reasoning_steps.append(f"✅ Found {len(docs)} relevant chunks in {pdf.name}")
            except Exception as e:
                reasoning_steps.append(f"⚠️ Error retrieving from {pdf.name}: {str(e)}")
                print(f"Error retrieving from {pdf.name}: {e}")

        reasoning_steps.append(f"📊 Total chunks retrieved: {len(all_docs)}")

        # Format context with source labels
        context_parts = []
        for doc in all_docs[:10]:
            source = doc.metadata.get("pdf_name", "Unknown")
            context_parts.append(f"[Source: {source}]\n{doc.page_content}\n")

        formatted_context = "\n---\n".join(context_parts)
        reasoning_steps.append(f"🔗 Using top {min(len(all_docs), 10)} chunks for context")

        # RAG prompt template with chain-of-thought
        template = """Answer the question based ONLY on the following context from multiple PDF documents.
        Each section is marked with its source document.

        Use chain-of-thought reasoning:
        1. First, identify which parts of the context are relevant to the question
        2. Analyze the information from each source document
        3. Synthesize the information to form a comprehensive answer
        4. Ensure you cite the source document name for each piece of information
        5. If information comes from multiple sources, mention all relevant sources
        6. If sources contradict, note the discrepancy and cite both sources

        Context:
        {context}

        Question: {question}

        Think step-by-step and provide your answer with source citations:"""

        prompt = ChatPromptTemplate.from_template(template)
        chain = (
            {"context": lambda x: formatted_context, "question": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )

        reasoning_steps.append("💭 Generating answer with source citations...")

        # Check if model supports thinking (e.g., qwen3, deepseek-r1)
        thinking_models = ['qwen3', 'deepseek-r1', 'qwen', 'deepseek']
        supports_thinking = any(tm in model.lower() for tm in thinking_models)

        if supports_thinking:
            reasoning_steps.append("🧠 Using thinking-enabled model with chain-of-thought reasoning...")
            try:
                # Enhanced system message for chain-of-thought reasoning
                cot_system_message = f"""You are an expert AI assistant that uses chain-of-thought reasoning.

Answer the question based ONLY on the provided context from PDF documents.

CHAIN-OF-THOUGHT PROCESS:
1. **Read and understand** the question carefully
2. **Scan the context** to identify all relevant information
3. **Break down** the information by source document
4. **Analyze** how each piece relates to the question
5. **Synthesize** a comprehensive answer
6. **Cite sources** explicitly for every claim

Context from PDF documents:
{formatted_context}

Think through each step carefully, showing your reasoning process."""

                # Use Ollama client directly for thinking-capable models
                ollama_response = ollama.chat(
                    model=model,
                    messages=[
                        {"role": "system", "content": cot_system_message},
                        {"role": "user", "content": f"Question: {question}\n\nThink step-by-step and provide a detailed answer with source citations."}
                    ],
                    think=True,
                    stream=False
                )

                # Add thinking process to reasoning steps
                if hasattr(ollama_response.message, 'thinking') and ollama_response.message.thinking:
                    thinking_text = ollama_response.message.thinking
                    # Show more of the thinking process (500 chars instead of 200)
                    reasoning_steps.append(f"💡 Model's chain-of-thought:\n{thinking_text[:500]}{'...' if len(thinking_text) > 500 else ''}")

                response = ollama_response.message.content
            except Exception as e:
                print(f"Error using thinking mode, falling back to standard: {e}")
                response = chain.invoke(question)
        else:
            response = chain.invoke(question)

        # Extract source information
        sources = [
            {
                "pdf_name": doc.metadata.get("pdf_name"),
                "pdf_id": doc.metadata.get("pdf_id"),
                "chunk_index": doc.metadata.get("chunk_index", 0)
            }
            for doc in all_docs[:10]
        ]

        reasoning_steps.append("✨ Answer generated successfully!")

        return response, sources, reasoning_steps

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict]],
        db: Session
    ) -> ChatMessage:
        """Save chat message to database.

        Args:
            session_id: Chat session identifier
            role: Message role (user or assistant)
            content: Message content
            sources: Source documents (for assistant messages)
            db: Database session

        Returns:
            Saved chat message
        """
        # Ensure session exists
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(
                session_id=session_id,
                created_at=datetime.now(),
                last_active=datetime.now()
            )
            db.add(session)
        else:
            session.last_active = datetime.now()

        # Save message
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=sources,
            timestamp=datetime.now()
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    def get_session_messages(self, session_id: str, db: Session) -> List[ChatMessage]:
        """Get all messages for a session.

        Args:
            session_id: Chat session identifier
            db: Database session

        Returns:
            List of chat messages
        """
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp).all()
