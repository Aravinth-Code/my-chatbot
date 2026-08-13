from enum import Enum

class DocumentSourceType(str, Enum):
    FILE = "FILE"
    URL = "URL"
