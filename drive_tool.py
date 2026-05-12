from googleapiclient.discovery import build
from google.oauth2 import service_account
from langchain_core.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'
FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

@tool
def search_drive_files(query: str) -> str:
    """Search for files in Google Drive using a Drive API query string.
    Examples:
    - name contains 'report'
    - mimeType = 'application/pdf'
    - fullText contains 'invoice'
    - name contains 'daily' and mimeType = 'application/pdf'
    """
    service = get_drive_service()
    full_query = f"'{FOLDER_ID}' in parents and ({query})"
    try:
        results = service.files().list(
            q=full_query,
            fields="files(id, name, mimeType, modifiedTime, size)",
            pageSize=20
        ).execute()
        files = results.get('files', [])
        if not files:
            return "No files found matching your query."
        output = f"Found {len(files)} file(s):\n"
        for f in files:
            modified = f.get('modifiedTime', 'N/A')[:10]
            output += f"- {f['name']} | Type: {f['mimeType'].split('/')[-1]} | Modified: {modified}\n"
        return output
    except Exception as e:
        return f"Search failed: {str(e)}"