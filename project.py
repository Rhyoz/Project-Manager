# project.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Project:
    id: Optional[int] = field(default=None)
    name: str = ""
    number: str = ""
    start_date: str = ""
    end_date: Optional[str] = None
    status: str = ""
    is_residential_complex: bool = False
    number_of_units: int = 0
    worker: str = ""
    residential_details: str = ""
    extra: str = ""
    main_contractor: Optional[str] = None  # New Optional Attribute
