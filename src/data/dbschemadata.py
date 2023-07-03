"""
@author: Arno
@created: 2023-05-25
@modified: 2023-07-03

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

    name: str = "temp"
    password: str = ""
    enabled: bool = True
    id: int = 0


@dataclass
class Wallet:
    """Dataclass for wallet"""

    site: Site
    profile: Profile
    address: str = ""
    enabled: bool = True
    id: int = 0


@dataclass
class Asset:
    """Dataclass for an asset"""

    name: str
    symbol: str
    precision: int = 0
    chain: str = ""
    id: int = 0


@dataclass
class AssetOnSite:
    """Dataclass for the identifier of an asset on a site"""

    asset: Asset
    site: Site
    id_on_site: str
    base: str = ""
    id: int = 0


@dataclass
class Transaction:
    """Dataclass for transactions"""

    id: int
    profile: Profile
    timestamp: Timestamp
    transactiontype: TransactionType
    site: Site
    txid: str
    from_wallet: Wallet
    to_wallet: Wallet
    quantity: Money
    fee: Money
    quote_asset: Asset
    base_asset: Asset
    fee_asset: Asset
    note: str = ""


@dataclass
class TransactionRaw:
    """Dataclass for writing raw transactions to db"""

    timestamp: int
    transactiontype: TransactionType
    txid: str
    from_wallet: str
    to_wallet: str
    quantity: int
    fee: int
    quote_asset: str = ""
    base_asset: str = ""
    fee_asset: str = ""
    note: str = ""


@dataclass
class Price:
    """Dataclass for price history"""

    timestamp: Timestamp
    price: Money
    quote_asset: Asset
    base_asset: Asset
    site: Site
