"""
@author: Arno
@created: 2023-06-03
@modified: 2023-07-08

Helper functions for Server

"""
import logging

from src.data.dbschemadata import Profile, TransactionRaw, Wallet
from src.data.dbschematypes import TransactionType
from src.db.db import Db
from src.db.dbasset import get_asset_id
from src.db.dbtransaction import check_transaction_exists
from src.db.dbwallet import get_all_active_wallets, insert_wallet
from src.db.dbwalletchild import get_walletchild_ids
from src.errors.dberrors import DbError
from src.models.sitemodel import SiteModel


def get_wallets_per_site(
    sitemodels: dict[int, SiteModel], db: Db
) -> dict[int, list[Wallet]]:
    """Get all wallets from database

    And return a dict with key = Site.id and values = list of wallets
    """
    walletsraw: list = get_all_active_wallets(db)
    wallets = {}
    for rawdata in walletsraw:
        siteid = rawdata[1]
        profileid = rawdata[2]
        profile = Profile(id=profileid)
        sitemodel: SiteModel = sitemodels[siteid]
        if sitemodel.site.enabled:
            wallet = Wallet(
                site=sitemodel.site,
                profile=profile,
                id=rawdata[0],
                name=rawdata[3],
                address=rawdata[4],
                haschild=rawdata[7],
            )
            wallets.setdefault(siteid, []).append(wallet)
    return wallets


def get_wallet_id2(address: str, siteid: int, profileid: int, db: Db):
    query = "SELECT id FROM wallet WHERE profile_id=? AND site_id=? AND address=?;"
    queryargs = (profileid, siteid, address)
    result = db.query(query, queryargs)
    return result


def get_wallet_id_notowned(siteid: int, profileid: int, db: Db):
    query = "SELECT id FROM wallet WHERE owned=false AND site_id=? AND profile_id=?;"
    queryargs = (siteid, profileid)
    result = db.query(query, queryargs)
    return result


def get_walletchild_id_notowned(address: str, parentid: int, db: Db):
    query = "SELECT id FROM walletchild WHERE parent_id=? AND address=?;"
    queryargs = (parentid, address)
    result = db.query(query, queryargs)
    return result


def get_walletchild_ids_join(address: str, siteid: int, profileid: int, db: Db):
    query = """SELECT id, parent_id, address, used FROM walletchild 
            INNER JOIN wallet ON walletchild.parent_id==wallet.id 
            WHERE walletchild.address=? AND wallet.siteid=? AND wallet.profile_id=?;"""
    queryargs = (address, siteid, profileid)
    result = db.query(query, queryargs)
    return result


def insert_walletchild_raw(parentid: int, address: str, used: bool, db: Db):
    query = """INSERT OR IGNORE INTO walletchild 
                (parent_id, address, used) 
            VALUES (?,?,?);"""
    queryargs = (
        parentid,
        address,
        used,
    )
    db.execute(query, queryargs)
    db.commit()


def insert_wallet_raw(
    siteid: int,
    profileid: int,
    name: str,
    address: str,
    owned: bool,
    enabled: bool,
    haschild: bool,
    db: Db,
) -> None:
    query = """INSERT OR IGNORE INTO wallet 
                (site_id, profile_id, name, address, owned, enabled, haschild) 
            VALUES (?,?,?,?,?,?);"""
    queryargs = (
        siteid,
        profileid,
        name,
        address,
        owned,
        enabled,
        haschild,
    )
    db.execute(query, queryargs)
    db.commit()


def get_wallet_raw(
    address: str, siteid: int, profileid: int, db: Db, owned: bool = True
) -> tuple[int, int]:
    if owned:
        res = get_wallet_id2(address, siteid, profileid, db)
        if len(res) > 1:
            raise DbError(
                f"Multiple wallets found with same address: {address} for site {siteid}"
            )
        if len(res) == 1:
            return (res[0][0], 0)
        res = get_walletchild_ids_join(address, siteid, profileid, db)
        if len(res) == 0:
            raise DbError(f"No wallets found with address: {address} for site {siteid}")
        if len(res) > 1:
            raise DbError(
                f"Multiple wallets found with same address: {address} for site {siteid}"
            )
        return (res[0][1], res[0][0])

    else:
        res = get_wallet_id_notowned(siteid, profileid, db)
        if len(res) == 0:
            insert_wallet_raw(
                siteid, profileid, "unknowns", "unknowns", False, False, True, db
            )
            res = get_wallet_id_notowned(siteid, profileid, db)
        wallet_parent_id = res[0][0]
        res = get_walletchild_id_notowned(address, wallet_parent_id, db)
        if len(res) > 1:
            raise DbError(
                f"Multiple wallets found with same address: {address} for site {siteid}"
            )
        if len(res) == 0:
            insert_walletchild_raw(wallet_parent_id, address, True, db)
            res = get_walletchild_id_notowned(address, wallet_parent_id, db)

        return (wallet_parent_id, res[0][0])


def insert_transaction_raw(
    txn: TransactionRaw, profileid: int, siteid: int, db: Db, chain: str = ""
) -> None:
    txn_exists = check_transaction_exists(txn.txid, db)
    if txn_exists:
        # TODO: what if other profile has same transaction...
        raise DbError(f"Not allowed to create new transaction with same hash {txn}")

    fromwalletid = 0
    fromwalletchildid = 0
    towalletid = 0
    towalletchildid = 0

    if txn.transactiontype == TransactionType.IN_UNDEFINED:
        # wallet from is this user
        fromwalletid, fromwalletchildid = get_wallet_raw(
            txn.from_wallet, siteid, profileid, db
        )
        towalletid, towalletchildid = get_wallet_raw(
            txn.to_wallet, siteid, profileid, db, False
        )
    if txn.transactiontype == TransactionType.OUT_UNDEFINED:
        # wallet to is this user
        fromwalletid, fromwalletchildid = get_wallet_raw(
            txn.from_wallet, siteid, profileid, db, False
        )
        towalletid, towalletchildid = get_wallet_raw(
            txn.to_wallet, siteid, profileid, db
        )

    quoteassetid = get_asset_id(txn.quote_asset, db, chain)
    baseassetid = (
        None if txn.base_asset == "" else get_asset_id(txn.base_asset, db, chain)
    )
    feeassetid = None if txn.fee_asset == "" else get_asset_id(txn.fee_asset, db, chain)

    query = """INSERT OR IGNORE INTO transactions 
                    (profile_id, site_id, transactiontype_id, timestamp, txid, 
                     from_wallet_id, from_walletchild_id, 
                     to_wallet_id, to_walletchild_id,
                     quote_asset_id, base_asset_id, fee_asset_id,
                     quantity, fee, note) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
    queryargs = (
        profileid,
        siteid,
        txn.transactiontype.value,
        txn.timestamp,
        txn.txid,
        fromwalletid,
        fromwalletchildid,
        towalletid,
        towalletchildid,
        quoteassetid,
        baseassetid,
        feeassetid,
        txn.quantity,
        txn.fee,
        txn.note,
    )
    db.execute(query, queryargs)
    db.commit()
