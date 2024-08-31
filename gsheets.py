import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Dict, Set

load_dotenv()

basedir = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Asic:
    id: str
    manufacturer: str
    model: str
    ths: int
    consumption: int
    rub_price: float
    usdt_price: float
    algorithm: List[str]
    coin: List[str]

class GoogleSheetsAPI:
    def __init__(self):
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            f'{basedir}/technologydynamicsasiccalc-76e05fa1a200.json')
        self.client = gspread.authorize(self.creds)

    def open_sheet(self, sheet_id: str = os.getenv("GOOGLE_SHEET_ID")):
        return self.client.open_by_key(sheet_id)

    def read_data(self, range_name, sheet_id: str = os.getenv("GOOGLE_SHEET_ID")):
        sheet = self.open_sheet(sheet_id)
        worksheet = sheet.sheet1
        return worksheet.get(range_name)
    
    def serialize(self, sheet_id: str = os.getenv("GOOGLE_SHEET_ID")):
        data = self.read_data(sheet_id=sheet_id, range_name='A1:I1000')
        data = [Asic(*row) for row in data[1:] if len(row) == 9]  # Убедитесь, что строка имеет 9 элементов
        return data

g = GoogleSheetsAPI()
asic_data = g.serialize()
