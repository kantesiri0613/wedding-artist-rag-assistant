"""Knowledge-base loading and chunking."""

from pathlib import Path
import re


def chunk_text(text: str, lines_per_chunk: int = 8) -> list[str]:
    """Split numbered knowledge-base sections into small retrieval documents."""
    sections = [part.strip() for part in re.split(r"\n(?=\d+\.|={5,})", text) if part.strip()]
    chunks: list[str] = []
    for section in sections:
        lines = [line.strip() for line in section.splitlines() if line.strip()]
        for start in range(0, len(lines), lines_per_chunk):
            chunk = "\n".join(lines[start:start + lines_per_chunk])
            if len(chunk) > 30:
                chunks.append(chunk)
    return chunks


def load_chunks(data_file: Path) -> list[str]:
    """Read and chunk a UTF-8 knowledge-base file."""
    return chunk_text(data_file.read_text(encoding="utf-8"))
