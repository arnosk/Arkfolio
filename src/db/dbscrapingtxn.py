"""
@author: Arno
@created: 2023-07-12
@modified: 2023-07-12

Database Handler Class

"""
import logging

from src.data.dbschemadata import ScrapingTxn, Site
from src.data.types import Timestamp
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_scrapingtxn(scrape: ScrapingTxn, profileid: int, db: Db) -> None:
    scrape_exists = check_scrapingtxn_exists(scrape, profileid, db)
    if scrape_exists:
        raise DbError(
            f"""Not allowed to create new scraping txn for same site {scrape.site.name} 
            and profile: {profileid}"""
        )
    query = """INSERT OR IGNORE INTO scrapingtxn 
            (site_id, profile_id, scrape_timestamp_start, scrape_timestamp_end) 
            VALUES (?,?,?,?);"""
    queryargs = (
        scrape.site.id,
        profileid,
        scrape.scrape_timestamp_start,
        scrape.scrape_timestamp_end,
    )
    db.execute(query, queryargs)
    db.commit()


def insert_ignore_scrapingtxn(scrape: ScrapingTxn, profileid: int, db: Db) -> None:
    scrape_exists = check_scrapingtxn_exists(scrape, profileid, db)
    if scrape_exists:
        return
    query = """INSERT OR IGNORE INTO scrapingtxn 
            (site_id, profile_id, scrape_timestamp_start, scrape_timestamp_end) 
            VALUES (?,?,?,?);"""
    queryargs = (
        scrape.site.id,
        profileid,
        scrape.scrape_timestamp_start,
        scrape.scrape_timestamp_end,
    )
    db.execute(query, queryargs)
    db.commit()


def check_scrapingtxn_exists(scrape: ScrapingTxn, profileid: int, db: Db) -> bool:
    """Checks if asset on site exists in db"""
    result = get_scrapingtxn_ids(scrape, profileid, db)
    if len(result) == 0:
        return False
    if len(result) > 1:
        raise DbError(
            f"""More than 1 scraping txn found for site {scrape.site.name} 
            and profile {profileid}: {result}"""
        )
    return True


def get_scrapingtxn_ids(scrape: ScrapingTxn, profileid: int, db: Db):
    query = """SELECT id, site_id, profile_id, scrape_timestamp_start, scrape_timestamp_end 
            FROM scrapingtxn WHERE site_id=? AND profile_id=?;"""
    queryargs = (scrape.site.id, profileid)
    result = db.query(query, queryargs)
    return result


def get_scrapingtxn_timestamp_end(
    scrape: ScrapingTxn, profileid: int, db: Db
) -> Timestamp:
    result = get_scrapingtxn_ids(scrape, profileid, db)
    if len(result) == 0:
        return Timestamp(0)
    if len(result) > 1:
        raise DbError(
            f"""More than 1 scraping txn found for site {scrape.site.name} 
            and profile {profileid}: {result}"""
        )
    return Timestamp(result[0][4])


def update_scrapingtxn(scrape: ScrapingTxn, profileid: int, db: Db) -> None:
    query = "UPDATE scrapingtxn SET scrape_timestamp_end=? WHERE site_id=? AND profile_id=?;"
    queryargs = (scrape.scrape_timestamp_end, scrape.site.id, profileid)
    db.execute(query, queryargs)
    db.commit()


def update_scrapingtxn_raw(
    timestamp_end: int, profileid: int, siteid: int, db: Db
) -> None:
    query = "UPDATE scrapingtxn SET scrape_timestamp_end=? WHERE site_id=? AND profile_id=?;"
    queryargs = (timestamp_end, siteid, profileid)
    db.execute(query, queryargs)
    db.commit()
