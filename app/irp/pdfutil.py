"""Extract text from an uploaded IRP/BCP PDF (pure-Python, works offline)."""
from io import BytesIO

from pypdf import PdfReader


def extract_text(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n\n".join(parts).strip()
