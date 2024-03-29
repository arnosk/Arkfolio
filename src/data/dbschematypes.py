"""
@author: Arno
@created: 2023-05-26
@modified: 2023-10-18

Enum Classes for data in database

"""
from dataclasses import dataclass
from enum import Enum

from src.data.types import OrderedEnum


class SiteType(Enum):
    """Class for type of website / exchange names"""

    MANUAL = 0
    BLOCKCHAIN = 1
    EXCHANGE = 2
    BROKER = 3
    INFO = 4


# @dataclass(frozen=True) # Because of txn.sort in _search_transactions (sitemodel.py)
# But if frozen, the value cannot be used TransactionType(value=res) (controllerhelper.py)
class TransactionType(OrderedEnum):
    """Class for type of transactions"""

    TRADE_BUY = 100
    TRADE_SELL = 101
    TRADE_BUY_SETTLEMENT = 102
    TRADE_SELL_SETTLEMENT = 103
    MOVE_DEPOSIT = 200
    MOVE_WITHDRAWAL = 201
    IN_INCOME = 300
    IN_MINING = 301
    IN_STAKING = 302
    IN_DIVIDEND = 303
    IN_AIRDROP = 304
    IN_GIFT = 305
    IN_UNDEFINED = 399
    OUT_EXPENSE = 400
    OUT_LOSS = 401
    OUT_UNDEFINED = 499
    UNDEF_UNDEFINED = 999


class WalletAddressType(Enum):
    """Class for type of wallet address"""

    INVALID = 0
    NORMAL = 1
    UNKNOWN = 2
    XPUB = 3  # BIP32
    YPUB = 4  # BIP49
    ZPUB = 5  # BIP84
    ELECTRUM = 6  # MPK


class ChildAddressType(Enum):
    """Class for type of child address"""

    NORMAL = 0
    RECEIVING = 1
    CHANGE = 2
