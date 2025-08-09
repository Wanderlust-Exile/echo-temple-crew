import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


# Load your Google service credentials (adjust the path)
SERVICE_ACCOUNT_FILE = "secrets/credentials.json"
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive.readonly"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

docs_service = build("docs", "v1", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)

# Optional: location to store note metadata logs
METADATA_LOG_PATH = "logs/notes_metadata.json"


def list_recent_docs(limit=5):
    """Fetch most recent Google Docs to allow for memory injection"""
    results = drive_service.files().list(
        pageSize=limit,
        fields="files(id, name, createdTime, modifiedTime)",
        q="mimeType='application/vnd.google-apps.document'",
        orderBy="modifiedTime desc",
    ).execute()
    return results.get("files", [])


def get_document_content(doc_id):
    """Retrieve plain text content of a Google Doc by ID"""
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get("body", {}).get("content", [])
    text = ""
    for elem in content:
        if "paragraph" in elem:
            for p in elem["paragraph"].get("elements", []):
                text += p.get("textRun", {}).get("content", "")
    return text.strip()


def upload_training_notes_to_gdoc(note_content, campaign_name=None):
    # Auto-generate a document name
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H%M")
    campaign_slug = campaign_name.replace(" ", "_") if campaign_name else "general"
    doc_title = f"Training Notes - {campaign_slug} - {date_str}_{time_str}"

    # Fetch memory (previous docs)
    previous_docs = list_recent_docs()
    memory_context = ""
    for doc in previous_docs:
        doc_id = doc["id"]
        doc_text = get_document_content(doc_id)
        memory_context += f"\n--- Memory from {doc['name']} ---\n{doc_text}\n"

    # Combine memory context and new note
    full_content = f"{memory_context}\n\n--- New Notes ({date_str}) ---\n{note_content.strip()}"

    # Create the document
    doc_metadata = {"title": doc_title}
    doc = docs_service.documents().create(body=doc_metadata).exe

