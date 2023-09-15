"""
@author: Arno
@created: 2023-05-19
@modified: 2023-09-15

Database Handler Class

"""
import logging

from src.data.dbschematypes import (
    ChildAddressType,
    SiteType,
    TransactionType,
    WalletAddressType,
)
from src.db.db import Db
from src.db.schema import DB_SCRIPT_CREATE_TABLES
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def db_init(db: Db) -> None:
    db_connect(db)
    _getversion(db)
    _postconnect(db)


def db_connect(db: Db) -> None:
    db.open()


def _getversion(db: Db) -> int:
    """Get latest Db version and status"""
    if not check_table(db, "version"):
        log.debug("No version table found")
        return 0

    query = "SELECT id, status FROM version ORDER BY id DESC LIMIT 1"
    res = db.query(query)
    (id, status) = res[0]
    if status == 0:
        raise DbError(f"Database migration not correctly upgraded. Version: {id}")
    log.debug(f"Version: {id}")
    return id


def _postconnect(db: Db) -> None:
    log.debug("Start script to create tables")
    db.executescript(DB_SCRIPT_CREATE_TABLES)
    _insert_site_types(db)
    _insert_transaction_types(db)
    _insert_walletaddress_types(db)
    _insert_walletchildaddress_types(db)
    db.execute(DB_UPDATE_VERSION, (1,))
    db.commit()


def _insert_site_types(db: Db) -> None:
    """Insert rows according to enum data type"""
    log.debug("Start inserting enumeration of SiteType to database")
    DB_INSERT_TYPE = "INSERT OR IGNORE INTO sitetype VALUES (?, ?);"
    for type in SiteType:
        db.execute(DB_INSERT_TYPE, (type.value, type.name))
    db.commit()


def _insert_transaction_types(db: Db) -> None:
    """Insert rows according to enum data type"""
    log.debug("Start inserting enumeration of TransactionType to database")
    DB_INSERT_TYPE = "INSERT OR IGNORE INTO transactiontype VALUES (?, ?, ?);"
    for type in TransactionType:
        type_name = type.name.split("_", 1)
        if len(type_name) <= 1:
            raise DbError(
                f"Unable to initiate transaction type {type.value}:{type.name}"
            )
        db.execute(DB_INSERT_TYPE, (type.value, type_name[0], type_name[1]))
    db.commit()


def _insert_walletaddress_types(db: Db) -> None:
    """Insert rows according to enum data type"""
    log.debug("Start inserting enumeration of WalletAddressType to database")
    DB_INSERT_TYPE = "INSERT OR IGNORE INTO walletaddresstype VALUES (?, ?);"
    for type in WalletAddressType:
        db.execute(DB_INSERT_TYPE, (type.value, type.name))
    db.commit()


def _insert_walletchildaddress_types(db: Db) -> None:
    """Insert rows according to enum data type"""
    log.debug("Start inserting enumeration of ChildAddressType to database")
    DB_INSERT_TYPE = "INSERT OR IGNORE INTO childaddresstype VALUES (?, ?);"
    for type in ChildAddressType:
        db.execute(DB_INSERT_TYPE, (type.value, type.name))
    db.commit()


def check_table(db: Db, table_name: str) -> bool:
    """Check if table exists in database"""
    if not db.has_connection():
        raise DbError("Database not connected")

    if table_name is None:
        return False

    query_chk_table = 'SELECT name FROM sqlite_master WHERE type="table" AND name=?'
    if db.query(query_chk_table, (table_name,)):
        # table exists
        return True
    return False


# strftime('%s','now') instead of unixepoch() used for unix epoch timestamp
DB_UPDATE_VERSION = f"""
UPDATE version SET migration_timestamp_end = strftime('%s', 'now'), status = 1 WHERE id = ? AND status = 0;
"""
