"""
@author: Arno
@created: 2023-05-25
@modified: 2023-06-02

Data Classes for data from database

"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.data.dbschematypes import SiteType, TransactionType
from src.data.money import Money
from src.data.types import Timestamp


@dataclass
class Site:
    """Dataclass for site"""

    id: int
    name: str
    sitetype: SiteType
    api: str = ""
    secret: str = ""
    hasprice: bool = False
    enabled: bool = True


@dataclass
class Profile:
    """Dataclass for profile"""

    name: str
    id: int = 0
    password: str = ""
    enabled: bool = True


@dataclass
class Wallet:
    """Dataclass for wallet"""

    site: Site
    profile: Profile
    id: int = 0
    address: str = ""
    enabled: bool = True


@dataclass
class SiteWallets:
    """Dataclass for site and coupled wallets"""

    site: Site
    wallets: list[Wallet]


@dataclass
class Asset:
    """Dataclass for an asset"""

    id: int
    name: str
    symbol: str
    precision: int
    chain: str


@dataclass
class Transaction:
    """Dataclass for transactions"""

    id: int
    profile: Profile
    timestamp: Timestamp
    transactiontype: TransactionType
    site: Site
    from_wallet: Wallet
    to_wallet: Wallet
    quote_asset: Asset
    base_asset: Asset
    fee_asset: Asset
    quantity: Money
    fee: Money
    txid: str
    note: str = ""


@dataclass
class Price:
    """Dataclass for price history"""

    timestamp: Timestamp
    price: Money
    quote_asset: Asset
    base_asset: Asset
    site: Site
