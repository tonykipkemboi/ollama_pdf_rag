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

    def __repr__(self) -> str:
        # Create a preview of the text (first 50 characters)
        text_preview = self.text if len(self.text) <= 50 else self.text[:50] + "..."
        return (
            f"Chunk(\n"
            f"  id={self.id!r},\n"
            f"  pdf_name={self.pdf_name!r},\n"
            f"  pdf_page={self.pdf_page},\n"
            f"  section_name={self.section_name!r},\n"
            f"  subsection_name={self.subsection_name!r},\n"
            f"  chunk_type={self.chunk_type!r},\n"
            f"  text={text_preview!r}\n"
            f")"
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
    )
    print(chunk)
