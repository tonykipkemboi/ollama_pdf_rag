from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ChunkType(str, Enum):
    TEXT = "text"
    TABLE = "table"
    BULLETPOINTS = "bulletpoints"
    IMAGE_CAPTION = "image_caption"


class Chunk(BaseModel):
    id: str
    pdf_name: str
    pdf_page: int
    section_name: Optional[str] = None
    subsection_name: Optional[str] = None
    chunk_type: ChunkType
    text: str
    keywords: Optional[list] = None

    def __repr__(self) -> str:
        return (
            f"CHUNK {self.id}:\n"
            f"Document={self.pdf_name!r},\n"
            f"Page={self.pdf_page},\n"
            f"Section={self.section_name!r},\n"
            f"Subsection={self.subsection_name!r},\n"
            f"Type={self.chunk_type},\n"
            f"Text={self.text!r}\n"
        )

    def __str__(self) -> str:
        return self.__repr__()


if __name__ == "__main__":
    chunk = Chunk(
        id="1",
        pdf_name="sample.pdf",
        pdf_page=1,
        section_name="Introduction",
        chunk_type=ChunkType.TEXT,
        text="This is a sample text chunk.",
        keywords=["sample", "text", "chunk"],
    )
    print(chunk)
