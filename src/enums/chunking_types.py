from enum import Enum


class ChunkingType(Enum):
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic" 
    SENTENCE = "sentence"