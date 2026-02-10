from enum import Enum, auto

class VectorObjectType(str, Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PROFILE = auto()

    STORY = auto()

    POST = auto()
    POST_CONTENT = auto()

    HIGHLIGHT = auto()
    HIGHLIGHT_CONTENT = auto()
