from functools import cache
from typing import final, Final


@final
class UndefinedType:
    __slots__ = ()

    @cache
    def __new__(cls):
        return super().__new__(cls)

    def __repr__(self):
        return "Undefined"

    def __bool__(self):
        return False


Undefined: Final[UndefinedType] = UndefinedType()
