import pdfplumber
from tabulate import tabulate

def get_pdf_to_text(pdf_path: str) -> str:
    """
    PDF 파일에서 일반 텍스트를 추출합니다.
    :param pdf_path: PDF 파일 경로
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip() if text else "PDF에서 텍스트를 추출할 수 없습니다."
    except Exception as e:
        return f"PDF 처리 중 오류 발생: {e}"

def get_pdf_to_markdown(pdf_path: str) -> str:
    """
    PDF 파일에서 마크다운 포맷으로 텍스트를 추출합니다.
    :param pdf_path: PDF 파일 경로
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            md = ""
            for i, page in enumerate(pdf.pages):
                md += f"# Page {i+1}\n\n"
                # 표 추출
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        md += tabulate(table, tablefmt="github") + "\n\n"
                # 일반 텍스트 추출
                page_text = page.extract_text()
                if page_text:
                    lines = page_text.splitlines()
                    for line in lines:
                        if line.strip().endswith(":"):
                            md += f"## {line.strip()}\n"
                        else:
                            md += f"{line}\n"
                    md += "\n"
        return md.strip() if md else "PDF에서 마크다운을 추출할 수 없습니다."
    except Exception as e:
        return f"PDF 처리 중 오류 발생: {e}" 