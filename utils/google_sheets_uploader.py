import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.env_loader import load_environment

def upload_to_sheet(leads: list):
    env = load_environment()
    SHEET_ID = env["GOOGLE_SHEET_ID"]

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'google_sheets_interface.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(SHEET_ID)
    try:
        worksheet = sheet.worksheet("Leads")
    except:
        worksheet = sheet.add_worksheet(title="Leads", rows="1000", cols="10")

    headers = ["URL", "Emails", "Phones", "Category"]
    existing = worksheet.get_all_values()
    if not existing:
        worksheet.append_row(headers)

    for lead in leads:
        row = [
            lead.get("url", ""),
            ", ".join(lead.get("emails", [])),
            ", ".join(lead.get("phones", [])),
            lead.get("category", "")
        ]
        if row not in existing:
            worksheet.append_row(row)
