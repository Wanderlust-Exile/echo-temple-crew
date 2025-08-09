import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Any, Optional


class GoogleSheetsInterface:
    def __init__(self, credentials_file: str, sheet_name: str):
        """
        Initialize the Google Sheets interface.

        :param credentials_file: Path to Google API JSON credentials.
        :param sheet_name: Name of the Google Sheet to interact with.
        """
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = self._authorize()
        self.sheet = self.client.open(self.sheet_name).sheet1

    def _authorize(self):
        """Authorize with Google Sheets API."""
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        return gspread.authorize(creds)

    def upload_data(self, data: List[List[Any]], clear_first: bool = True):
        """
        Uploads data to the sheet. Optionally clears the sheet first.

        :param data: List of rows to upload.
        :param clear_first: Whether to clear the sheet before uploading.
        """
        if clear_first:
            self.sheet.clear()
        self.sheet.update("A1", data)

    def append_data(self, data: List[List[Any]]):
        """
        Append rows to the sheet.

        :param data: List of rows to append.
        """
        for row in data:
            self.sheet.append_row(row, value_input_option="USER_ENTERED")

    def read_data(self, range_str: Optional[str] = None) -> List[List[Any]]:
        """
        Read data from the sheet.

        :param range_str: Optional range string (e.g., 'A1:C10').
        :return: List of rows with data.
        """
        if range_str:
            return self.sheet.get(range_str)
        return self.sheet.get_all_values()

    def update_cell(self, row: int, col: int, value: Any):
        """
        Update a specific cell.

        :param row: Row number (1-indexed).
        :param col: Column number (1-indexed).
        :param value: Value to set.
        """
        self.sheet.update_cell(row, col, value)

    def find_and_replace(self, find_str: str, replace_str: str):
        """
        Find and replace all instances of a string in the sheet.

        :param find_str: String to find.
        :param replace_str: String to replace it with.
        """
        cell_list = self.sheet.findall(find_str)
        for cell in cell_list:
            self.sheet.update_cell(cell.row, cell.col, replace_str)
