"""
@author: Arno
@created: 2023-05-29
@modified: 2023-06-02

Database Handler Class

"""
import logging

from src.data.dbschemadata import Site
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_sitemodel(site: Site, db: Db) -> None:
    query = """INSERT OR IGNORE INTO site 
            (id, name, sitetype_id, api, secret, hasprice, enabled) 
            VALUES (?,?,?,?,?,?,?);"""
    queryargs = (
        site.id,
        site.name,
        site.sitetype.value,
        site.api,
        site.secret,
        site.hasprice,
        site.enabled,
    )
    db.execute(query, queryargs)
    db.commit()


def get_sitemodel(id: int, db: Db) -> tuple:
    query = """SELECT id, name, sitetype_id, api, secret, hasprice, enabled 
            FROM site WHERE id = ?;"""
    result = db.query(query, (id,))
    log.debug(f"Record of sitemodel id {id} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of sitemodel id: {id} in database")
    return result[0]


def update_sitemodel(site: Site, db: Db) -> None:
    query = "UPDATE site SET api=?, secret=?, hasprice=?, enabled=? WHERE id=?;"
    queryargs = (site.api, site.secret, site.hasprice, site.enabled, site.id)
    db.execute(query, queryargs)
    db.commit()
