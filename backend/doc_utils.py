import io, PyPDF2, docx

def extract_text(file_bytes: bytes, mime: str) -> str:
    if mime == "application/pdf":
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in reader.pages)
    if mime == "application/vnd.openxmlformats-officedocument.wordprocessing.document":
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    # Añade más tipos si lo necesitas
    return file_bytes.decode(errors="ignore")
