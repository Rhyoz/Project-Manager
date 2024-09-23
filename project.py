# project.py
from dataclasses import dataclass
from datetime import date

@dataclass
class Project:
    id: int = None
    name: str = ""
    number: str = ""
    start_date: str = date.today().strftime("%Y-%m-%d")  # Stored as string in YYYY-MM-DD
    end_date: str = None
    status: str = "Active"
    is_residential_complex: bool = False
    number_of_units: int = 0
    residential_details: str = ""
    worker: str = ""  # New field added
