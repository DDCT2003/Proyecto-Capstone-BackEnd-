from pathlib import Path
from PyPDF2 import PdfReader

def extract_text_from_pdf(path: str) -> str:
    try:
        with open(path, "rb") as f:
            reader = PdfReader(f)
            return "\n".join((p.extract_text() or "") for p in reader.pages)
    except:
        return ""

def extract_text_from_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except:
        return ""

def extract_text(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    return ""

def compute_match(required_skills, candidate_skills):
    if not required_skills or not candidate_skills:
        return 0.0

    req = {s.lower() for s in required_skills}
    cand = {s.lower() for s in candidate_skills}

    intersection = req.intersection(cand)

    score = (len(intersection) / len(req)) * 100
    return round(score, 1)
