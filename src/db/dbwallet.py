"""
@author: Arno
@created: 2023-05-30
@modified: 2023-08-19

Database Handler Class

"""
import logging

from netaddr import P
from numpy import add

from src.data.dbschemadata import Wallet
from src.data.dbschematypes import WalletAddressType
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_wallet(db: Db, wallet: Wallet) -> None:
    wallet_exists = check_wallet_exists(db, wallet)
    if wallet_exists:
        raise DbError(
            f"Not allowed to create new wallet with same address and site {wallet}"
        )
    insert_wallet_raw(
        db=db,
        siteid=None if wallet.site == None else wallet.site.id,
        profileid=wallet.profile.id,
        name=wallet.name,
        address=wallet.address,
        addresstype=wallet.addresstype.value,
        owned=wallet.owned,
        enabled=wallet.enabled,
        haschild=wallet.haschild,
    )


def insert_wallet_raw(
    db: Db,
    siteid: int | None,
    profileid: int,
    name: str,
    address: str,
    addresstype: int = 1,
    owned: bool = True,
    enabled: bool = True,
    haschild: bool = False,
) -> None:
    query = """INSERT OR IGNORE INTO wallet 
                (site_id, profile_id, name, address, addresstype, owned, enabled, haschild) 
            VALUES (?,?,?,?,?,?,?,?);"""
    queryargs = (
        siteid,
        profileid,
        name,
        address,
        addresstype,
        owned,
        enabled,
        haschild,
    )
    db.execute(query, queryargs)
    db.commit()


def check_wallet_exists(db: Db, wallet: Wallet) -> bool:
    """Checks if combination of site_id and address is unique"""
    result = get_wallet_ids(db, wallet)
    if len(result) == 0:
        return False
    return True


def get_wallet_id(db: Db, wallet: Wallet) -> int:
    result = get_wallet_ids(db, wallet)
    if len(result) == 0:
        return -1
    return result[0][0]


def get_wallet_ids(db: Db, wallet: Wallet):
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


def get_wallet_id_raw(db: Db, address: str, siteid: int, profileid: int):
    """Get wallet id from db, for specific address and site and profile"""
    query = "SELECT id FROM wallet WHERE profile_id=? AND site_id=? AND address=?;"
    queryargs = (profileid, siteid, address)
    result = db.query(query, queryargs)
    return result


def get_one_wallet_id(db: Db, address: str, siteid: int, profileid: int) -> int:
    """Get only one wallet id from db, for specific address and site and profile"""
    result = get_wallet_id_raw(db, address, siteid, profileid)
    if len(result) > 1:
        raise DbError(
            f"Multiple wallets found with same address: {address} for site {siteid}"
        )
    if len(result) < 1:
        return 0
    return result[0][0]


def get_wallet_id_unknowns(db: Db, siteid: int, profileid: int) -> int:
    query = "SELECT id FROM wallet WHERE owned=false AND addrestype=? AND site_id=? AND profile_id=?;"
    queryargs = (WalletAddressType.UNKNOWN.value, siteid, profileid)
    result = db.query(query, queryargs)
    if len(result) == 0:
        return 0
    if len(result) == 1:
        return result[0][0]
    raise DbError(
        f"Multiple records found for the UNKNOWN wallet in database "
        f"for site {siteid} and profile {profileid}: {result}"
    )


def get_wallet(db: Db, id: int) -> tuple:
    query = """SELECT id, site_id, profile_id, name, address, addresstype, owned, enabled, haschild 
            FROM wallet WHERE id=?;"""
    result = db.query(query, (id,))
    log.debug(f"Record of wallet id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result[0]


def get_all_wallets(db: Db) -> list:
    query = """SELECT id, site_id, profile_id, name, address, addresstype, owned, enabled, haschild 
            FROM wallet"""
    result = db.query(query)
    log.debug(f"Record of wallets in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result


def get_all_active_wallets(db: Db) -> list:
    query = """SELECT id, site_id, profile_id, name, address, addresstype, owned, enabled, haschild 
            FROM wallet WHERE enabled=true AND owned=true"""
    result = db.query(query)
    log.debug(f"Record of wallets in database: {result}")
    if len(result) == 0:
        log.info(f"No records found of a wallet in database")
    return result


def update_wallet(db: Db, wallet: Wallet) -> None:
    query = "UPDATE wallet SET name=?, address=?, enabled=? WHERE id=?;"
    queryargs = (wallet.name, wallet.address, wallet.enabled, wallet.id)
    db.execute(query, queryargs)
    db.commit()
