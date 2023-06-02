"""
@author: Arno
@created: 2023-05-30
@modified: 2023-06-02

Database Handler Class

"""
import logging

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
        return
    query = "INSERT OR IGNORE INTO wallets (site_id, profile_id, address, enabled) VALUES (?,?,?,?);"
    queryargs = (wallet.site.id, wallet.profile.id, wallet.address, wallet.enabled)
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
    query = "SELECT id FROM wallets WHERE site_id=? AND address=?;"
    queryargs = (wallet.site.id, wallet.address)
    result = db.query(query, queryargs)
    return result


def get_wallet(id: int, db: Db) -> tuple:
    query = "SELECT * FROM wallets WHERE id = ?;"
    result = db.query(query, (id,))
    log.debug(f"Record of wallet id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of wallet id: {id} in database")
    return result[0]


def update_wallet(wallet: Wallet, db: Db) -> None:
    query = "UPDATE wallets SET address=?, enabled=? WHERE id=?;"
    queryargs = (wallet.address, wallet.enabled, wallet.id)
    db.execute(query, queryargs)
    db.commit()
