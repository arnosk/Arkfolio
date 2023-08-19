"""
@author: Arno
@created: 2023-07-04
@modified: 2023-08-19

Database Handler Class

"""
import logging

from src.data.dbschemadata import WalletChild
from src.data.dbschematypes import ChildAddressType
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_walletchild(db: Db, walletchild: WalletChild) -> None:
    wallet_exists = check_walletchild_exists(db, walletchild.address)
    if wallet_exists:
        raise DbError(
            f"Not allowed to create new child wallet with same address {walletchild}"
        )
    insert_walletchild_raw(
        db=db,
        parentid=walletchild.parent.id,
        address=walletchild.address,
        type=walletchild.type.value,
        used=walletchild.used,
    )


def insert_walletchild_raw(
    db: Db, parentid: int, address: str, type: int = 0, used: bool = True
):
    query = """INSERT OR IGNORE INTO walletchild 
                (parent_id, address, type, used) 
            VALUES (?,?,?,?);"""
    queryargs = (
        parentid,
        address,
        type,
        used,
    )
    db.execute(query, queryargs)
    db.commit()


def check_walletchild_exists(db: Db, address: str) -> bool:
    """Checks if address is unique"""
    result = get_walletchild_ids(db, address)
    if len(result) == 0:
        return False
    return True


def get_walletchild_id(db: Db, address: str, parentid: int):
    query = "SELECT id FROM walletchild WHERE parent_id=? AND address=?;"
    queryargs = (parentid, address)
    result = db.query(query, queryargs)
    return result


def get_walletchild_ids(db: Db, address: str):
    query = (
        "SELECT id, parent_id, address, type, used FROM walletchild WHERE address=?;"
    )
    queryargs = (address,)
    result = db.query(query, queryargs)
    return result


def get_walletchild(db: Db, id: int):
    query = "SELECT id, parent_id, address, type, used FROM walletchild WHERE id=?;"
    result = db.query(query, (id,))
    log.debug(f"Record of walletchild id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result


def get_walletchilds(db: Db, parentid: int) -> list:
    query = (
        "SELECT id, parent_id, address, type, used FROM walletchild WHERE parent_id=?;"
    )
    result = db.query(query, (parentid,))
    log.debug(f"Record of wallet child in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet child in database")
    return result


def get_walletchild_addresses(db: Db, parentid: int) -> list[str]:
    result = get_walletchilds(db, parentid)
    addresses: list[str] = []
    for res in result:
        addresses.append(res[2])
    return addresses


def get_walletchildtypes(db: Db, parentid: int, type: ChildAddressType) -> list:
    query = "SELECT id, parent_id, address, type, used FROM walletchild WHERE parent_id=? AND type=?;"
    result = db.query(query, (parentid, type.value))
    log.debug(f"Record of wallet child in database: {result}")
    if len(result) == 0:
        log.debug(f"No records found of a wallet child in database")
    return result


def get_nr_walletchildtypes(db: Db, parentid: int, type: ChildAddressType) -> int:
    result = get_walletchildtypes(db, parentid, type)
    return len(result)


def update_child_of_wallet_unkowns(
    db: Db, unknwonparentid: int, walletchild: WalletChild
):
    query = """UPDATE walletchild 
                SET parent_id=?, type=?, used=?
                WHERE parent_id=? and address=?;"""
    queryargs = (
        walletchild.parent.id,
        walletchild.type.value,
        True,
        unknwonparentid,
        walletchild.address,
    )
    db.execute(query, queryargs)
    db.commit()
