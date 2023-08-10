"""
@author: Arno
@created: 2023-07-01
@modified: 2023-08-10

Database Handler Class

"""
import logging

from src.data.dbschemadata import Transaction
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_transaction(db: Db, txn: Transaction) -> None:
    asset_exists = check_transaction_exists(db, txn.txid)
    if asset_exists:
        raise DbError(f"Not allowed to create new transaction with same hash {txn}")
    query = """INSERT OR IGNORE INTO transactions 
                    (profile_id, site_id, transactiontype_id, timestamp, txid, 
                     from_wallet_id, from_walletchild_id, 
                     to_wallet_id, to_walletchild_id,
                     quote_asset_id, base_asset_id, fee_asset_id,
                     quantity, fee, note) 
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);"""
    queryargs = (
        txn.profile.id,
        txn.site.id,
        txn.transactiontype.value,
        int(txn.timestamp),
        txn.txid,
        txn.from_wallet.id,
        None if txn.from_walletchild == None else txn.from_walletchild.id,
        txn.to_wallet.id,
        None if txn.to_walletchild == None else txn.to_walletchild.id,
        txn.quote_asset.id,
        txn.base_asset.id,
        txn.fee_asset.id,
        txn.quantity.amount_cents,
        txn.fee.amount_cents,
        txn.note,
    )
    db.execute(query, queryargs)
    db.commit()


def insert_transaction_raw(
    db: Db,
    profileid: int,
    siteid: int,
    transactiontype: int,
    timestamp: int,
    transactionid: str,
    from_walletid: int,
    from_walletchildid: int | None,
    to_walletid: int,
    to_walletchildid: int | None,
    quote_assetid: int,
    base_assetid: int | None,
    fee_assetid: int | None,
    quantity_cents: int,
    fee_cents: int,
    note: str,
) -> int:
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
        transactiontype,
        timestamp,
        transactionid,
        from_walletid,
        from_walletchildid,
        to_walletid,
        to_walletchildid,
        quote_assetid,
        base_assetid,
        fee_assetid,
        quantity_cents,
        fee_cents,
        note,
    )
    result = db.execute(query, queryargs)
    db.commit()
    return result


def check_transaction_exists(db: Db, txid: str) -> bool:
    """Checks if asset on site exists in db"""
    result = get_assetonsite_ids(db, txid)
    if len(result) == 0:
        return False
    return True


def get_assetonsite_ids(db: Db, txid: str):
    query = "SELECT id FROM transactions WHERE txid=?;"
    queryargs = (txid,)
    result = db.query(query, queryargs)
    return result
