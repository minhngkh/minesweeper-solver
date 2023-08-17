from enum import Enum

UNOPENED = -2
FLAGGED = -1

UNOPENED_CHAR = "_"
FLAGGED_CHAR = "X"


class Answer(Enum):
    TRUE = 1
    FALSE = 2
    UNKNOWN = 3
