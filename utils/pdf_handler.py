import pdfplumber
import io


def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file bytes"""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return None


def get_pdf_metadata(file_bytes):
    """Extract basic metadata from PDF"""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return {
                'page_count': len(pdf.pages),
                'metadata': pdf.metadata
            }
    except:
        return {'page_count': 0, 'metadata': {}}