"""
@author: Arno
@created: 2023-07-01
@modified: 2023-07-11

Database Handler Class

"""
import logging

from src.data.dbschemadata import Asset
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_asset(asset: Asset, db: Db) -> None:
    symbol_exists = check_symbol_exists(asset, db)
    if symbol_exists:
        raise DbError(
            f"Not allowed to create new asset with same symbol and different name: {asset}"
        )
    asset_exists = check_asset_exists(asset, db)
    if asset_exists:
        # TODO: raise error?
        log.error(f"Skipping insert, Asset already exists in db {asset}")
        return
    query = "INSERT INTO asset (name, symbol, decimal_places, chain) VALUES (?,?,?,?);"
    queryargs = (asset.name, asset.symbol, asset.decimal_places, asset.chain)
    db.execute(query, queryargs)
    db.commit()


def check_symbol_exists(asset: Asset, db: Db) -> bool:
    """Checks if asset symbol exists with different name in db"""
    query = "SELECT id FROM asset WHERE name<>? AND symbol=? AND chain=?;"
    queryargs = (asset.name, asset.symbol, asset.chain)
    result = db.query(query, queryargs)
    if len(result) == 0:
        return False
    return True


def check_asset_exists(asset: Asset, db: Db) -> bool:
    """Checks if asset exists in db"""
    result = get_asset_ids(asset.symbol, db, asset.chain)
    if len(result) == 0:
        return False
    return True


def get_asset_id(name: str, db: Db, chain: str = "") -> int:
    result = get_asset_ids(name, db, chain)
    if len(result) == 0:
        raise DbError(f"No asset found {name} on chain {chain}")
    if len(result) > 1:
        raise DbError(f"More than 1 asset found {name} on chain {chain}: {result}")
    return result[0][0]


def get_asset_ids(name: str, db: Db, chain: str = ""):
    query = "SELECT id FROM asset WHERE (name=? OR symbol=?) AND chain=?;"
    queryargs = (name, name, chain)
    result = db.query(query, queryargs)
    return result


def get_asset(id: int, db: Db) -> Asset:
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
