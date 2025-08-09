import os
import faiss
import pandas as pd
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
google_sheets_interface = os.getenv("google_sheets_interface")
INDEX_PATH = "logs/lead_embeddings.index"
EMBEDDING_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=OPENAI_API_KEY)

def _load_google_sheet(sheet_name="Leads"):
    """Load leads from Google Sheet into DataFrame."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_service_account.json", scope)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(google_sheets_interface).worksheet(sheet_name)
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def _create_embeddings(df):
    """Create embeddings for each row's combined text."""
    texts = df.apply(lambda row: " | ".join(map(str, row.values)), axis=1).tolist()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    vectors = np.array([r.embedding for r in response.data]).astype("float32")
    return vectors

def _save_index(vectors, df):
    """Save FAISS index to disk."""
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, INDEX_PATH)
    df.to_csv("logs/lead_data.csv", index=False)  # Keep ID mapping

def build_semantic_index():
    """Build or rebuild the semantic index from the Google Sheet."""
    df = _load_google_sheet()
    vectors = _create_embeddings(df)
    _save_index(vectors, df)
    print(f"Semantic index built with {len(df)} leads.")

def semantic_query(query, k=5):
    """Search the semantic index with natural language query."""
    if not os.path.exists(INDEX_PATH):
        build_semantic_index()

    index = faiss.read_index(INDEX_PATH)
    df = pd.read_csv("logs/lead_data.csv")

    # Embed query
    query_vec = np.array(
        client.embeddings.create(model=EMBEDDING_MODEL, input=[query]).data[0].embedding
    ).astype("float32").reshape(1, -1)

    D, I = index.search(query_vec, k)
    results = df.iloc[I[0]]
    return results.to_dict(orient="records")
