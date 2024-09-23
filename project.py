# project.py
from dataclasses import dataclass
from datetime import date

@dataclass
class Project:
    id: int = None
    name: str = ""
    number: str = ""
    start_date: date = date.today()
    end_date: date = None
    status: str = "Active"
    is_residential_complex: bool = False
    number_of_units: int = 0
    residential_details: str = ""
