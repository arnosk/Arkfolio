"""
@author: Arno
@created: 2023-07-01
@modified: 2023-10-27

Database Handler Class

"""
import logging

from src.data.dbschemadata import Transaction
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_transaction(db: Db, txn: Transaction) -> None:
    if txn.to_walletchild == None:
        txn_exists = check_transaction_exists(
            db=db,
            txid=txn.txid,
            towalletid=txn.to_wallet.id,
        )
    else:
        txn_exists = check_transaction_exists(
            db=db,
            txid=txn.txid,
            towalletid=txn.to_wallet.id,
            towalletchildid=txn.to_walletchild.id,
        )
    if txn_exists:
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


def check_transaction_exists(
    db: Db, txid: str, towalletid: int, towalletchildid: int = -1
) -> bool:
    """Checks if transaction exists in db
    Ttransaction can have same txid, but other output address (normal or child)"""
    if towalletchildid > 0:
        query = "SELECT id FROM transactions WHERE txid=? AND to_walletchild_id=?;"
        queryargs = (txid, towalletchildid)
    else:
        # no to_walletchild
        query = "SELECT id FROM transactions WHERE txid=? AND to_wallet_id=? AND to_walletchild_id=NULL;"
        queryargs = (txid, towalletid, towalletchildid)
    result = db.query(query, queryargs)
    if len(result) == 0:
        return False
    return True


def get_transaction_ids(db: Db, txid: str):
    query = "SELECT id FROM transactions WHERE txid=?;"
    queryargs = (txid,)
    result = db.query(query, queryargs)
    return result


def get_db_transactions(db: Db, profileid: int) -> list:
    query = """SELECT transactions.id, timestamp, txid, note, quantity, fee,
                site.id, site.name, sitetype.id, sitetype.name,
                transactiontype.id, transactiontype.type, transactiontype.subtype, 
                from_wallet_id, walletfrom.address, walletfrom.enabled, walletfrom.owned, walletfrom.haschild, walletfrom.name, 
                walletfrom.addresstype, wallettypefrom.name,
                to_wallet_id, walletto.address, walletto.enabled, walletto.owned, walletto.haschild, walletto.name, 
                walletto.addresstype, wallettypeto.name,
                from_walletchild_id, walletchildfrom.address, walletchildfrom.used, 
                walletchildfrom.type, childaddresstypefrom.name,
                to_walletchild_id, walletchildto.address, walletchildto.used, 
                walletchildto.type, childaddresstypeto.name,
                quote_asset_id, assetquote.name, assetquote.symbol, assetquote.decimal_places, assetquote.chain,
                base_asset_id, assetbase.name, assetbase.symbol, assetbase.decimal_places, assetbase.chain,
                fee_asset_id, assetfee.name, assetfee.symbol, assetfee.decimal_places, assetfee.chain
            FROM transactions 
            INNER JOIN site ON site.id = transactions.site_id
            INNER JOIN sitetype ON sitetype.id = site.sitetype_id
            INNER JOIN transactiontype ON transactiontype.id = transactions.transactiontype_id
            INNER JOIN wallet AS walletfrom ON walletfrom.id = transactions.from_wallet_id
            INNER JOIN walletaddresstype AS wallettypefrom ON wallettypefrom.id = walletfrom.addresstype
            INNER JOIN wallet AS walletto ON walletto.id = transactions.to_wallet_id
            INNER JOIN walletaddresstype AS wallettypeto ON wallettypeto.id = walletto.addresstype
            LEFT JOIN walletchild AS walletchildfrom ON walletchildfrom.id = transactions.from_walletchild_id
            LEFT JOIN childaddresstype AS childaddresstypefrom ON childaddresstypefrom.id = walletchildfrom.type
            LEFT JOIN walletchild AS walletchildto ON walletchildto.id = transactions.to_walletchild_id
            LEFT JOIN childaddresstype AS childaddresstypeto ON childaddresstypeto.id = walletchildto.type
            LEFT JOIN asset AS assetquote ON assetquote.id = transactions.quote_asset_id
            LEFT JOIN asset AS assetbase ON assetbase.id = transactions.base_asset_id
            LEFT JOIN asset AS assetfee ON assetfee.id = transactions.fee_asset_id
            WHERE transactions.profile_id=?;"""
    queryargs = (profileid,)
    result = db.query(query, queryargs)
    return result


def update_transaction_child_to_wallet(
    db: Db, walletchild_id: int, walletchild_parentid: int, newwallet_id: int
) -> None:
    """Update a transaction:
    The Child wallet address is changed to a normal wallet address"""
    queryargs = (newwallet_id, walletchild_id, walletchild_parentid)
    query = "UPDATE transactions SET from_walletchild_id=NULL, from_wallet_id=? WHERE from_walletchild_id=? AND from_wallet_id=?;"
    db.execute(query, queryargs)
    query = "UPDATE transactions SET to_walletchild_id=NULL, to_wallet_id=? WHERE to_walletchild_id=? AND to_wallet_id=?;"
    db.execute(query, queryargs)
    db.commit()
