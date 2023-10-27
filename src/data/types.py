"""
@author: Arno
@created: 2023-05-09
@modified: 2023-10-27

Several types

"""
from dataclasses import dataclass, field
from enum import Enum
from typing import NewType

Timestamp = NewType("Timestamp", int)
TimestampMS = NewType("TimestampMS", int)


@dataclass(order=True)
class TransactionInfo:
    """Dataclass for info of transactions"""

    address: str
    nr_txs: int = 0
    final_balance: int = 0
    total_received: int = 0


class OrderedEnum(Enum):
    def __init__(self, value, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__order = len(self.__class__)

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.__order >= other.__order
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.__order > other.__order
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.__order <= other.__order
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.__order < other.__order
        return NotImplemented
