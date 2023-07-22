"""
@author: Arno
@created: 2023-07-04
@modified: 2023-07-22

Database Handler Class

"""
import logging

from src.data.dbschemadata import WalletChild
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_walletchild(walletchild: WalletChild, db: Db) -> None:
    wallet_exists = check_walletchild_exists(walletchild.address, db)
    if wallet_exists:
        raise DbError(
            f"Not allowed to create new child wallet with same address {walletchild}"
        )
    insert_walletchild_raw(
        parentid=walletchild.parent.id,
        address=walletchild.address,
        used=walletchild.used,
        db=db,
    )


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


def check_walletchild_exists(address: str, db: Db) -> bool:
    """Checks if address is unique"""
    result = get_walletchild_ids(address, db)
    if len(result) == 0:
        return False
    return True


def get_walletchild_id(address: str, parentid: int, db: Db):
    query = "SELECT id FROM walletchild WHERE parent_id=? AND address=?;"
    queryargs = (parentid, address)
    result = db.query(query, queryargs)
    return result


def get_walletchild_ids(address: str, db: Db):
    query = "SELECT id, parent_id, address, used FROM walletchild WHERE address=?;"
    queryargs = (address,)
    result = db.query(query, queryargs)
    return result


def get_walletchild(id: int, db: Db):
    query = "SELECT id, parent_id, address, used FROM walletchild WHERE id=?;"
    result = db.query(query, (id,))
    log.debug(f"Record of walletchild id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result


def get_walletchilds(parentid: int, db: Db) -> list:
    query = "SELECT id, parent_id, address, used FROM walletchild WHERE parent_id=?;"
    result = db.query(query, (parentid,))
    log.debug(f"Record of walletchild in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result


def get_walletchild_addresses(parentid: int, db: Db) -> list[str]:
    result = get_walletchilds(parentid, db)
    addresses: list[str] = []
    for res in result:
        addresses.append(res[2])
    return addresses
