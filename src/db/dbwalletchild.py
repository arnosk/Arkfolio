"""
@author: Arno
@created: 2023-07-04
@modified: 2023-07-04

Database Handler Class

"""
import logging

from src.data.dbschemadata import Wallet, WalletChild
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_walletchild(walletchild: WalletChild, db: Db) -> None:
    wallet_exists = check_walletchild_exists(walletchild, db)
    if wallet_exists:
        raise DbError(
            f"Not allowed to create new child wallet with same address {walletchild}"
        )
    query = """INSERT OR IGNORE INTO walletchild 
                (parent_id, address) 
            VALUES (?,?);"""
    queryargs = (
        walletchild.parent.id,
        walletchild.address,
    )
    db.execute(query, queryargs)
    db.commit()


def check_walletchild_exists(walletchild: WalletChild, db: Db) -> bool:
    """Checks if address is unique"""
    result = get_wallet_ids(walletchild.address, db)
    if len(result) == 0:
        return False
    return True


def get_wallet_ids(address: str, db: Db):
    # Get all id's regarding of profile!
    query = "SELECT id FROM walletchild WHERE address=?;"
    queryargs = (address,)
    result = db.query(query, queryargs)
    return result


def get_walletchild(id: int, db: Db):
    query = "SELECT * FROM walletchild WHERE id=?;"
    result = db.query(query, (id,))
    log.debug(f"Record of walletchild id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result


def get_walletchilds(parentid: int, db: Db) -> list:
    query = "SELECT * FROM walletchild WHERE parentid=?;"
    result = db.query(query, (parentid,))
    log.debug(f"Record of walletchild in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result
