from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'
FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=creds)

results = service.files().list(
    q=f"'{FOLDER_ID}' in parents",
    fields="files(id, name, mimeType)"
).execute()

files = results.get('files', [])
print(f"Found {len(files)} files:")
for f in files:
    print(f"  {f['name']} ({f['mimeType']})")