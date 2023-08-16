"""
@author: Arno
@created: 2023-05-09
@modified: 2023-08-16

Several types

"""
from dataclasses import dataclass, field
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
