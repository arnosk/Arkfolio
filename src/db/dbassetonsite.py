"""
@author: Arno
@created: 2023-07-03
@modified: 2023-08-10

Database Handler Class

"""
import logging

from src.data.dbschemadata import Asset, AssetOnSite, Site
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_assetonsite(db: Db, assetonsite: AssetOnSite) -> None:
    asset_exists = check_assetonsite_exists(db, assetonsite)
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


def check_assetonsite_exists(db: Db, assetonsite: AssetOnSite) -> bool:
    """Checks if asset on site exists in db"""
    result = get_assetonsite_ids(db, assetonsite)
    if len(result) == 0:
        return False
    return True


def get_assetonsite_ids(db: Db, assetonsite: AssetOnSite):
    query = (
        "SELECT id FROM assetonsite WHERE asset_id=? AND site_id=? AND id_on_site=?;"
    )
    queryargs = (assetonsite.asset.id, assetonsite.site.id, assetonsite.id_on_site)
    result = db.query(query, queryargs)
    return result
