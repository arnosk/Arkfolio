"""
@author: Arno
@created: 2023-07-03
@modified: 2023-07-04

Database Handler Class

"""
import logging

from src.data.dbschemadata import Asset, AssetOnSite, Site
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_assetonsite(assetonsite: AssetOnSite, db: Db) -> None:
    asset_exists = check_assetonsite_exists(assetonsite, db)
    if asset_exists:
        raise DbError(
            f"Not allowed to create new asset on site with same name or symbol {assetonsite}"
        )
    query = "INSERT OR IGNORE INTO assetonsite (asset_id, site_id, id_on_site, base) VALUES (?,?,?,?);"
    queryargs = (
        assetonsite.asset.id,
        assetonsite.site.id,
        assetonsite.id_on_site,
        assetonsite.base,
    )
    db.execute(query, queryargs)
    db.commit()


def check_assetonsite_exists(assetonsite: AssetOnSite, db: Db) -> bool:
    """Checks if asset on site exists in db"""
    result = get_assetonsite_ids(assetonsite, db)
    if len(result) == 0:
        return False
    return True


def get_assetonsite_ids(assetonsite: AssetOnSite, db: Db):
    query = (
        "SELECT id FROM assetonsite WHERE asset_id=? AND site_id=? AND id_on_site=?;"
    )
    queryargs = (assetonsite.asset.id, assetonsite.site.id, assetonsite.id_on_site)
    result = db.query(query, queryargs)
    return result
