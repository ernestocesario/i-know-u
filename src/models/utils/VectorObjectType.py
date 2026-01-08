from enum import Enum, auto

class VectorObjectType(str, Enum):
    CONTENT = auto()
    POST = auto()
    HIGHLIGHT = auto()

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name
