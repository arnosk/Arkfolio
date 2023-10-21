"""
@author: Arno
@created: 2023-10-16
@modified: 2023-10-21

Helper functions for Controller

"""
import logging

from src.data.dbschemadata import Asset, Profile, Site, Transaction, Wallet, WalletChild
from src.data.dbschematypes import (
    ChildAddressType,
    SiteType,
    TransactionType,
    WalletAddressType,
)
from src.data.money import Money
from src.db.db import Db
from src.db.dbtransaction import get_db_transactions
from src.db.dbwallet import get_db_wallets

log = logging.getLogger(__name__)


def get_transactions(db: Db, profile: Profile) -> list[Transaction]:
    txns: list[Transaction] = []
    result = get_db_transactions(db, profile.id)
    if len(result) > 0:
        for res in result:
            site = Site(id=res[6], name=res[7], sitetype=SiteType(value=res[8]))
            walletfrom = Wallet(
                profile=profile,
                site=site,
                id=res[13],
                address=res[14],
                enabled=res[15],
                owned=res[16],
                haschild=res[17],
                name=res[18],
                addresstype=WalletAddressType(value=res[19]),
            )
            walletto = Wallet(
                profile=profile,
                site=site,
                id=res[21],
                address=res[22],
                enabled=res[23],
                owned=res[24],
                haschild=res[25],
                name=res[26],
                addresstype=WalletAddressType(value=res[27]),
            )
            walletchildfrom = None
            if walletfrom.haschild:
                walletchildfrom = WalletChild(
                    parent=walletfrom,
                    id=res[29],
                    address=res[30],
                    used=res[31],
                    type=ChildAddressType(value=res[32]),
                )
            walletchildto = None
            if walletto.haschild:
                walletchildto = WalletChild(
                    parent=walletto,
                    id=res[34],
                    address=res[35],
                    used=res[36],
                    type=ChildAddressType(value=res[37]),
                )
            assetquote = Asset(
                id=res[39],
                name=res[40],
                symbol=res[41],
                decimal_places=res[42],
                chain=res[43],
            )
            assetbase = Asset(
                id=res[44],
                name=res[45],
                symbol=res[46],
                decimal_places=res[47],
                chain=res[48],
            )
            assetfee = Asset(
                id=res[49],
                name=res[50],
                symbol=res[51],
                decimal_places=res[52],
                chain=res[53],
            )
            quantity = Money(
                amount_cents=res[4],
                decimal_places=assetquote.decimal_places,
                precision=2,
                currency_symbol=assetquote.symbol,
            )
            fee = Money(
                amount_cents=res[5],
                decimal_places=assetfee.decimal_places,
                precision=2,
                currency_symbol=assetfee.symbol,
            )
            txn = Transaction(
                profile=profile,
                id=res[0],
                timestamp=res[1],
                txid=res[2],
                note=res[3],
                quantity=quantity,
                fee=fee,
                site=site,
                transactiontype=TransactionType(value=res[10]),
                from_wallet=walletfrom,
                to_wallet=walletto,
                from_walletchild=walletchildfrom,
                to_walletchild=walletchildto,
                quote_asset=assetquote,
                base_asset=assetbase,
                fee_asset=assetfee,
            )
            txns.append(txn)
    return txns


def get_wallets(db: Db, profile: Profile) -> list[Wallet]:
    wallets: list[Wallet] = []
    result = get_db_wallets(db, profile.id)
    if len(result) > 0:
        for res in result:
            site = Site(id=res[1], name="?", sitetype=SiteType.BLOCKCHAIN)
            wallet = Wallet(
                profile=profile,
                site=site,
                id=res[0],
                address=res[4],
                enabled=res[6],
                owned=res[7],
                haschild=res[8],
                name=res[3],
                addresstype=WalletAddressType(value=res[5]),
            )
            wallets.append(wallet)
    return wallets
