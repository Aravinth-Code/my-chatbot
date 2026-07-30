from enum import Enum

class ChunkStatus(str, Enum):
    CHUNKED = "CHUNKED"
    EMBEDDING = "EMBEDDING"
    EMBEDDED = "EMBEDDED"
    FAILED = "FAILED"