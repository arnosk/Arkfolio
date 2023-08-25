"""
@author: Arno
@created: 2023-07-10
@modified: 2023-08-21

Helper functions for Server

"""
import logging

from src.data.dbschemadata import Site, TransactionRaw
from src.data.dbschematypes import TransactionType, WalletAddressType
from src.db.db import Db
from src.db.dbasset import get_asset_id
from src.db.dbtransaction import check_transaction_exists, insert_transaction_raw
from src.db.dbwallet import get_one_wallet_id, get_wallet_id_unknowns, insert_wallet_raw
from src.db.dbwalletchild import get_walletchild_id, insert_walletchild_raw
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def get_walletchild_ids_join(db: Db, address: str, siteid: int, profileid: int):
    """Get walletchild from db, for specific address and site and profile"""
    query = """SELECT walletchild.id, parent_id, walletchild.address, used FROM walletchild 
            INNER JOIN wallet ON walletchild.parent_id==wallet.id 
            WHERE walletchild.address=? AND wallet.site_id=? AND wallet.profile_id=?;"""
    queryargs = (address, siteid, profileid)
    result = db.query(query, queryargs)
    return result


def get_wallet_owned(
    db: Db, address: str, site: Site, profileid: int, allow_unknowns: bool
) -> tuple[int, int]:
    """Get wallet id's from address
    Returns the (wallet_id, walletchild_id)"""

    # TODO: Also search from wallets of other profiles??

    # search wallet addresses
    walletid = get_one_wallet_id(db, address, site.id, profileid)
    if walletid > 0:
        return (walletid, 0)

    # search child addresses
    res_wchild = get_walletchild_ids_join(db, address, site.id, profileid)
    if len(res_wchild) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {site.name}"
        )
    if len(res_wchild) == 1:
        return (res_wchild[0][1], res_wchild[0][0])

    # if len(res_wchild) == 0:
    if not allow_unknowns:
        raise DbError(f"No wallets found with address: {address} for site {site.name}")

    # else
    return get_wallet_unknowns(db, address, site, profileid)


def get_wallet_unknowns(
    db: Db, address: str, site: Site, profileid: int
) -> tuple[int, int]:
    """Get wallet id's from address
    Returns the (wallet_id, walletchild_id)
    address is not owned and is added to/searched from the unknowns wallet"""

    wallet_uknowns_parent_id = get_wallet_id_unknowns(db, site.id, profileid)
    if wallet_uknowns_parent_id == 0:
        unknown_name = f"Unknowns {site.name}"
        insert_wallet_raw(
            siteid=site.id,
            profileid=profileid,
            name=unknown_name,
            address=unknown_name,
            addresstype=WalletAddressType.UNKNOWN.value,
            owned=False,
            enabled=False,
            haschild=True,
            db=db,
        )
        wallet_uknowns_parent_id = get_wallet_id_unknowns(db, site.id, profileid)
    res_wchild = get_walletchild_id(db, address, wallet_uknowns_parent_id)
    if len(res_wchild) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {site.name}"
        )
    if len(res_wchild) == 0:
        insert_walletchild_raw(
            db=db, parentid=wallet_uknowns_parent_id, address=address, type=0, used=True
        )
        res_wchild = get_walletchild_id(db, address, wallet_uknowns_parent_id)

    return (wallet_uknowns_parent_id, res_wchild[0][0])


def process_and_insert_rawtransaction(
    db: Db, txn: TransactionRaw, profileid: int, site: Site, chain: str = ""
) -> bool:
    """Processing the raw transaction before inserting into db

    wallet addresses are looked up in database for existance
    asset symbols/names are looked up in database for existance

    Returns true when transaction is added to database
    """
    log.debug(
        f"Trying to insert a raw txn for profileid {profileid} and site {site.name} and chain {chain}: {txn}"
    )
    txn_exists = check_transaction_exists(db, txn.txid)
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
        # wallet to is this users address
        fromwalletid, fromwalletchildid = get_wallet_owned(
            db, txn.from_wallet, site, profileid, True
        )
        towalletid, towalletchildid = get_wallet_owned(
            db, txn.to_wallet, site, profileid, False
        )
    if txn.transactiontype == TransactionType.OUT_UNDEFINED:
        # wallet from is this users address
        fromwalletid, fromwalletchildid = get_wallet_owned(
            db, txn.from_wallet, site, profileid, False
        )
        towalletid, towalletchildid = get_wallet_owned(
            db, txn.to_wallet, site, profileid, True
        )

    quoteassetid = get_asset_id(db, txn.quote_asset, chain)
    baseassetid = (
        None if txn.base_asset == "" else get_asset_id(db, txn.base_asset, chain)
    )
    feeassetid = None if txn.fee_asset == "" else get_asset_id(db, txn.fee_asset, chain)

    result = insert_transaction_raw(
        db=db,
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
    )
    return result > 0
