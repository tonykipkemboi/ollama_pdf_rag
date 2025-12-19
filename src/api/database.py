"""Database models and session management."""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database configuration
DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/api.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=False  # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class PDFMetadata(Base):
    """PDF metadata table."""
    __tablename__ = "pdfs"

    pdf_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    collection_name = Column(String, unique=True, nullable=False)
    upload_timestamp = Column(DateTime, nullable=False)
    doc_count = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=False)
    is_sample = Column(Boolean, default=False)
    file_path = Column(String)


class ChatSession(Base):
    """Chat session table."""
    __tablename__ = "chat_sessions"

    session_id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    last_active = Column(DateTime, nullable=False)


class ChatMessage(Base):
    """Chat message table."""
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    sources = Column(JSON)
    timestamp = Column(DateTime, nullable=False)


# Create all tables
Base.metadata.create_all(bind=engine)
