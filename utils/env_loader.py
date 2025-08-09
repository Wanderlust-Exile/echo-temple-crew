from dotenv import load_dotenv
import os

def load_environment():
    load_dotenv()
    return {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "CSE_ID": os.getenv("CSE_ID"),
        "GOOGLE_SHEET_ID": os.getenv("GOOGLE_SHEET_ID"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }
