"""
@author: Arno
@created: 2023-07-10
@modified: 2023-08-09

Helper functions for Server

"""
import logging

from src.data.dbschemadata import Site, TransactionRaw
from src.data.dbschematypes import TransactionType
from src.db.db import Db
from src.db.dbasset import get_asset_id
from src.db.dbtransaction import check_transaction_exists, insert_transaction_raw
from src.db.dbwallet import get_wallet_id2, get_wallet_id_notowned, insert_wallet_raw
from src.db.dbwalletchild import get_walletchild_id, insert_walletchild_raw
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def get_walletchild_ids_join(address: str, siteid: int, profileid: int, db: Db):
    """Get walletchild from db, for specific address and site and profile"""
    query = """SELECT walletchild.id, parent_id, walletchild.address, used FROM walletchild 
            INNER JOIN wallet ON walletchild.parent_id==wallet.id 
            WHERE walletchild.address=? AND wallet.site_id=? AND wallet.profile_id=?;"""
    queryargs = (address, siteid, profileid)
    result = db.query(query, queryargs)
    return result


def get_wallet_raw_own(
    address: str, site: Site, profileid: int, db: Db
) -> tuple[int, int]:
    """Get wallet id's from address
    Returns the wallet_id, walletchild_id"""

    res_wallet = get_wallet_id2(address, site.id, profileid, db)
    if len(res_wallet) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {site.name}"
        )
    if len(res_wallet) == 1:
        return (res_wallet[0][0], 0)
    res_wchild = get_walletchild_ids_join(address, site.id, profileid, db)
    if len(res_wchild) == 0:
        raise DbError(f"No wallets found with address: {address} for site {site.name}")
    if len(res_wchild) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {site.name}"
        )
    return (res_wchild[0][1], res_wchild[0][0])


def get_wallet_raw_notown(
    address: str, site: Site, profileid: int, db: Db
) -> tuple[int, int]:
    """Get wallet id's from address
    Returns the wallet_id, walletchild_id
    address is not owned and is added to/searched from the unknowns wallet"""
    res_wallet = get_wallet_id_notowned(site.id, profileid, db)
    if len(res_wallet) == 0:
        unknown_name = f"Unknowns {site.name}"
        insert_wallet_raw(
            siteid=site.id,
            profileid=profileid,
            name=unknown_name,
            address=unknown_name,
            addresstype=0,
            owned=False,
            enabled=False,
            haschild=True,
            db=db,
        )
        res_wallet = get_wallet_id_notowned(site.id, profileid, db)
    wallet_parent_id = res_wallet[0][0]
    res_wchild = get_walletchild_id(address, wallet_parent_id, db)
    if len(res_wchild) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {site.name}"
        )
    if len(res_wchild) == 0:
        insert_walletchild_raw(wallet_parent_id, address, True, db)
        res_wchild = get_walletchild_id(address, wallet_parent_id, db)

    return (wallet_parent_id, res_wchild[0][0])


def process_and_insert_rawtransaction(
    txn: TransactionRaw, profileid: int, site: Site, db: Db, chain: str = ""
) -> bool:
    """Processing the raw transaction before inserting into db

    wallet addresses are looked up in database for existance
    asset symbols/names are looked up in database for existance

    Returns true when transaction is added to database
    """
    log.debug(
        f"Trying to insert a raw txn for profileid {profileid} and site {site.name} and chain {chain}: {txn}"
    )
    txn_exists = check_transaction_exists(txn.txid, db)
    if txn_exists:
        # TODO: what if other profile has same transaction..., raise error?
        log.exception(f"Transaction already exist with same hash {txn.txid}")
        return False
        raise DbError(
            f"Not allowed to create new transaction with same hash {txn.txid}"
        )

    fromwalletid = 0
    fromwalletchildid = 0
    towalletid = 0
    towalletchildid = 0

    if txn.transactiontype == TransactionType.IN_UNDEFINED:
        # wallet to is this user
        fromwalletid, fromwalletchildid = get_wallet_raw_notown(
            txn.from_wallet, site, profileid, db
        )
        towalletid, towalletchildid = get_wallet_raw_own(
            txn.to_wallet, site, profileid, db
        )
    if txn.transactiontype == TransactionType.OUT_UNDEFINED:
        # wallet from is this user
        fromwalletid, fromwalletchildid = get_wallet_raw_own(
            txn.from_wallet, site, profileid, db
        )
        towalletid, towalletchildid = get_wallet_raw_notown(
            txn.to_wallet, site, profileid, db
        )

    quoteassetid = get_asset_id(txn.quote_asset, db, chain)
    baseassetid = (
        None if txn.base_asset == "" else get_asset_id(txn.base_asset, db, chain)
    )
    feeassetid = None if txn.fee_asset == "" else get_asset_id(txn.fee_asset, db, chain)

    result = insert_transaction_raw(
        profileid=profileid,
        siteid=site.id,
        transactiontype=txn.transactiontype.value,
        timestamp=txn.timestamp,
        transactionid=txn.txid,
        from_walletid=fromwalletid,
        from_walletchildid=None if fromwalletchildid == 0 else fromwalletchildid,
        to_walletid=towalletid,
        to_walletchildid=None if towalletchildid == 0 else towalletchildid,
        quote_assetid=quoteassetid,
        base_assetid=baseassetid,
        fee_assetid=feeassetid,
        quantity_cents=txn.quantity,
        fee_cents=txn.fee,
        note=txn.note,
        db=db,
    )
    return result > 0

    # query = """INSERT OR IGNORE INTO transactions
    #                 (profile_id, site_id, transactiontype_id, timestamp, txid,
    #                  from_wallet_id, from_walletchild_id,
    #                  to_wallet_id, to_walletchild_id,
    #                  quote_asset_id, base_asset_id, fee_asset_id,
    #                  quantity, fee, note)
    #             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
    # queryargs = (
    #     profileid,
    #     site.id,
    #     txn.transactiontype.value,
    #     txn.timestamp,
    #     txn.txid,
    #     fromwalletid,
    #     None if fromwalletchildid == 0 else fromwalletchildid,
    #     towalletid,
    #     None if towalletchildid == 0 else towalletchildid,
    #     quoteassetid,
    #     baseassetid,
    #     feeassetid,
    #     txn.quantity,
    #     txn.fee,
    #     txn.note,
    # )
    # result = db.execute(query, queryargs)
    # db.commit()
    # return result > 0
