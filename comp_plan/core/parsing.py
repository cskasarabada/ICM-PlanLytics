# comp_plan/core/parsing.py - Document text extraction
from pathlib import Path
import docx
from pypdf import PdfReader


def extract_text(path: Path) -> str:
    """Extract text from .docx, .pdf, or .txt files."""
    sfx = path.suffix.lower()
    if sfx == ".docx":
        d = docx.Document(str(path))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip())
    if sfx == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    return Path(path).read_text(errors="ignore")
