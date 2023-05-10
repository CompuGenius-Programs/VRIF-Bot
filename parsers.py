from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Page:
    """Class for a wiki page."""
    title: str = ""
    url: str = ""
    override: str = ""


@dataclass_json
@dataclass
class VRIF:
    """Class for a wiki category."""
    title: str = ""
    url: str = ""
    pages: List[Page] = field(default_factory=list)


@dataclass_json
@dataclass
class External:
    """Class for a wiki category."""
    title: str = ""
    url: str = ""
