from enum import Enum
from typing import TypeAlias
from collections import namedtuple


Field: TypeAlias = list[list[int]]
Clause: TypeAlias = list[int]

UNOPENED_VAL = -2
FLAGGED_VAL = -1

UNOPENED_CHAR = "_"
FLAGGED_CHAR = "X"


class Answer(Enum):
    TRUE = 1
    FALSE = 2
    UNKNOWN = 3
