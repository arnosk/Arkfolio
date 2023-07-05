"""
@author: Arno
@created: 2023-07-01
@modified: 2023-07-05

Database Handler Class

"""
import logging

from src.data.dbschemadata import Asset
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_asset(asset: Asset, db: Db) -> None:
    asset_exists = check_asset_exists(asset, db)
    if asset_exists:
        raise DbError(
            f"Not allowed to create new asset with same name or symbol {asset}"
        )
    query = (
        "INSERT OR IGNORE INTO asset (name, symbol, precision, chain) VALUES (?,?,?,?);"
    )
    queryargs = (asset.name, asset.symbol, asset.precision, asset.chain)
    db.execute(query, queryargs)
    db.commit()


def check_asset_exists(asset: Asset, db: Db) -> bool:
    """Checks if asset exists in db"""
    result = get_asset_ids(asset.name, db, asset.chain)
    if len(result) == 0:
        return False
    return True


def get_asset_id(name: str, db: Db, chain: str = ""):
    result = get_asset_ids(name, db, chain)
    if len(result) == 0:
        raise DbError(f"No asset found {name} on chain {chain}")
    if len(result) > 1:
        raise DbError(f"More than 1 asset found {name} on chain {chain}: {result}")
    return result[0]


def get_asset_ids(name: str, db: Db, chain: str = ""):
    query = "SELECT id FROM asset WHERE (name=? OR symbol=?) AND chain=?;"
    queryargs = (name, name, chain)
    result = db.query(query, queryargs)
    return result


def get_asset(id: int, db: Db) -> Asset:
    query = "SELECT id, name, symbol, precision, chain FROM asset WHERE id=?;"
    queryargs = (id,)
    result = db.query(query, queryargs)
    log.debug(f"Record of asset id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of asset id: {id} in database")
    return Asset(
        id=result[0][0],
        name=result[0][1],
        symbol=result[0][2],
        precision=result[0][3],
        chain=result[0][4],
    )
