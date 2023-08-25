"""
@author: Arno
@created: 2023-07-01
@modified: 2023-08-25

Database Handler Class

"""
import logging

from src.data.dbschemadata import Asset
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_asset(db: Db, asset: Asset) -> None:
    symbol_exists = check_symbol_exists(db, asset)
    if symbol_exists:
        raise DbError(
            f"Not allowed to create new asset with same symbol and different name: {asset}"
        )
    asset_exists = check_asset_exists(db, asset)
    if asset_exists:
        # TODO: raise error?
        log.debug(f"Skipping insert. Asset already exists in db {asset}")
        return
    query = "INSERT INTO asset (name, symbol, decimal_places, chain) VALUES (?,?,?,?);"
    queryargs = (asset.name, asset.symbol, asset.decimal_places, asset.chain)
    db.execute(query, queryargs)
    db.commit()


def check_symbol_exists(db: Db, asset: Asset) -> bool:
    """Checks if asset symbol exists with different name in db"""
    query = "SELECT id FROM asset WHERE name<>? AND symbol=? AND chain=?;"
    queryargs = (asset.name, asset.symbol, asset.chain)
    result = db.query(query, queryargs)
    if len(result) == 0:
        return False
    return True


def check_asset_exists(db: Db, asset: Asset) -> bool:
    """Checks if asset exists in db"""
    result = get_asset_ids(db, asset.symbol, asset.chain)
    if len(result) == 0:
        return False
    return True


def get_asset_id(db: Db, name: str, chain: str = "") -> int:
    result = get_asset_ids(db, name, chain)
    if len(result) == 0:
        raise DbError(f"No asset found {name} on chain {chain}")
    if len(result) > 1:
        raise DbError(f"More than 1 asset found {name} on chain {chain}: {result}")
    return result[0][0]


def get_asset_ids(db: Db, name: str, chain: str = ""):
    query = "SELECT id FROM asset WHERE (name=? OR symbol=?) AND chain=?;"
    queryargs = (name, name, chain)
    result = db.query(query, queryargs)
    return result


def get_asset(db: Db, id: int) -> Asset:
    query = "SELECT id, name, symbol, decimal_places, chain FROM asset WHERE id=?;"
    queryargs = (id,)
    result = db.query(query, queryargs)
    log.debug(f"Record of asset id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of asset id: {id} in database")
    return Asset(
        id=result[0][0],
        name=result[0][1],
        symbol=result[0][2],
        decimal_places=result[0][3],
        chain=result[0][4],
    )
