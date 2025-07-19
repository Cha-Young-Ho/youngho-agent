import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from settings import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SCOPES

def download_file_from_gdrive(file_id, dest_path):
    """Google Drive에서 파일 다운로드"""
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=GOOGLE_SCOPES)
    service = build('drive', 'v3', credentials=creds)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.close()
    return dest_path

def process_drive_file(file_id: str, mode: str = "text") -> str:
    """
    Google Drive에서 파일을 받아 확장자별로 처리합니다.
    :param file_id: 구글 드라이브 파일 ID
    :param mode: 'text' 또는 'markdown'
    """
    from pdf_processor import get_pdf_to_text, get_pdf_to_markdown
    
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=GOOGLE_SCOPES)
    service = build('drive', 'v3', credentials=creds)
    file = service.files().get(fileId=file_id, fields='name, mimeType').execute()
    filename = file['name']
    ext = filename.split('.')[-1].lower()
    temp_path = f"/tmp/{filename}"

    # 파일 다운로드
    download_file_from_gdrive(file_id, temp_path)

    try:
        # 확장자별 처리
        if ext == "pdf":
            if mode == "markdown":
                return get_pdf_to_markdown(temp_path)
            else:
                return get_pdf_to_text(temp_path)
        elif ext == "txt":
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content if mode == "text" else f"```\n{content}\n```"
        elif ext in ["doc", "docx", "docs"]:
            doc = service.files().export(fileId=file_id, mimeType="text/plain").execute()
            content = doc.decode("utf-8")
            return content if mode == "text" else f"```\n{content}\n```"
        else:
            return f"지원하지 않는 파일 형식입니다: {ext}"
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path) 