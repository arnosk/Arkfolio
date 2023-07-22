"""
@author: Arno
@created: 2023-05-30
@modified: 2023-07-08

Database Handler Class

"""
import logging

from netaddr import P
from numpy import add

from src.data.dbschemadata import Wallet
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_wallet(wallet: Wallet, db: Db) -> None:
    wallet_exists = check_wallet_exists(wallet, db)
    if wallet_exists:
        raise DbError(
            f"Not allowed to create new wallet with same address and site {wallet}"
        )
    insert_wallet_raw(
        siteid=None if wallet.site == None else wallet.site.id,
        profileid=wallet.profile.id,
        name=wallet.name,
        address=wallet.address,
        owned=wallet.owned,
        enabled=wallet.enabled,
        haschild=wallet.haschild,
        db=db,
    )


def insert_wallet_raw(
    siteid: int | None,
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
            VALUES (?,?,?,?,?,?,?);"""
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


def check_wallet_exists(wallet: Wallet, db: Db) -> bool:
    """Checks if combination of site_id and address is unique"""
    result = get_wallet_ids(wallet, db)
    if len(result) == 0:
        return False
    return True


def get_wallet_id(wallet: Wallet, db: Db) -> int:
    result = get_wallet_ids(wallet, db)
    if len(result) == 0:
        return -1
    return result[0][0]


def get_wallet_ids(wallet: Wallet, db: Db):
    # Get all id's regarding of profile!
    if wallet.site == None:
        query = "SELECT id FROM wallet WHERE site_id=NULL AND address=?;"
        queryargs = (wallet.address,)
    else:
        query = "SELECT id FROM wallet WHERE site_id=? AND address=?;"
        queryargs = (wallet.site.id, wallet.address)
    query = "SELECT id FROM wallet WHERE site_id=? AND address=?;"
    queryargs = (None if wallet.site == None else wallet.site.id, wallet.address)
    result = db.query(query, queryargs)
    return result


def get_wallet(id: int, db: Db) -> tuple:
    query = """SELECT id, site_id, profile_id, name, address, owned, enabled, haschild 
            FROM wallet WHERE id=?;"""
    result = db.query(query, (id,))
    log.debug(f"Record of wallet id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result[0]


def get_all_wallets(db: Db) -> list:
    query = """SELECT id, site_id, profile_id, name, address, owned, enabled, haschild 
            FROM wallet"""
    result = db.query(query)
    log.debug(f"Record of wallets in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result


def get_all_active_wallets(db: Db) -> list:
    query = """SELECT id, site_id, profile_id, name, address, owned, enabled, haschild 
            FROM wallet WHERE enabled=true AND owned=true"""
    result = db.query(query)
    log.debug(f"Record of wallets in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result


def get_wallet_id2(address: str, siteid: int, profileid: int, db: Db):
    """Get wallet from db, for specific address and site and profile"""
    query = "SELECT id FROM wallet WHERE profile_id=? AND site_id=? AND address=?;"
    queryargs = (profileid, siteid, address)
    result = db.query(query, queryargs)
    return result


def get_wallet_id_notowned(siteid: int, profileid: int, db: Db):
    query = "SELECT id FROM wallet WHERE owned=false AND site_id=? AND profile_id=?;"
    queryargs = (siteid, profileid)
    result = db.query(query, queryargs)
    return result


def update_wallet(wallet: Wallet, db: Db) -> None:
    query = "UPDATE wallet SET name=?, address=?, enabled=? WHERE id=?;"
    queryargs = (wallet.name, wallet.address, wallet.enabled, wallet.id)
    db.execute(query, queryargs)
    db.commit()
