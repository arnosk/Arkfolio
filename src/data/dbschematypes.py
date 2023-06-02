"""
@author: Arno
@created: 2023-05-26
@modified: 2023-05-27

Enum Classes for data in database

"""
from enum import Enum, auto


class SiteType(Enum):
    """Class for type of website / exchange names"""

    MANUAL = 0
    BLOCKCHAIN = 1
    EXCHANGE = 2
    BROKER = 3
    INFO = 4


class TransactionType(Enum):
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
    OUT_EXPENSE = 400
    OUT_LOSS = 401
