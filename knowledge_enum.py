import enum
from enum import auto

class DebugLevels(enum.StrEnum):
    OFF = auto()
    LOGGED = auto()
    DEBUG = auto()

    def __str__(self):
        return self.value

