# File: project.py
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Unit:
    id: Optional[int] = field(default=None)
    name: str = ""
    is_done: bool = False

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
    extra: str = ""
    main_contractor: Optional[str] = None  # New Optional Attribute
    units: List[str] = field(default_factory=list)  # List of Unit Names
