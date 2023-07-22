"""
@author: Arno
@created: 2023-07-12
@modified: 2023-07-22

Database Handler Class

"""
import logging

from src.data.dbschemadata import ScrapingTxn, Site
from src.data.types import Timestamp
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_scrapingtxn(scrape: ScrapingTxn, db: Db) -> None:
    scrape_exists = check_scrapingtxn_exists(scrape, db)
    if scrape_exists:
        raise DbError(
            f"""Not allowed to create new scraping txn for 
            same wallet {scrape.wallet}"""
        )
    query = """INSERT OR IGNORE INTO scrapingtxn 
            (wallet_id, scrape_timestamp_start, scrape_timestamp_end) 
            VALUES (?,?,?);"""
    queryargs = (
        scrape.wallet.id,
        scrape.scrape_timestamp_start,
        scrape.scrape_timestamp_end,
    )
    db.execute(query, queryargs)
    db.commit()


def insert_ignore_scrapingtxn(scrape: ScrapingTxn, db: Db) -> None:
    scrape_exists = check_scrapingtxn_exists(scrape, db)
    if scrape_exists:
        return
    query = """INSERT OR IGNORE INTO scrapingtxn 
            (wallet_id, scrape_timestamp_start, scrape_timestamp_end) 
            VALUES (?,?,?);"""
    queryargs = (
        scrape.wallet.id,
        scrape.scrape_timestamp_start,
        scrape.scrape_timestamp_end,
    )
    db.execute(query, queryargs)
    db.commit()


def check_scrapingtxn_exists(scrape: ScrapingTxn, db: Db) -> bool:
    """Checks if asset on site exists in db"""
    result = get_scrapingtxn_ids(scrape, db)
    if len(result) == 0:
        return False
    if len(result) > 1:
        raise DbError(
            f"""More than 1 scraping txn found for wallet {scrape.wallet} 
            : {result}"""
        )
    return True


def get_scrapingtxn_ids(scrape: ScrapingTxn, db: Db):
    query = """SELECT id, wallet_id, scrape_timestamp_start, scrape_timestamp_end 
            FROM scrapingtxn WHERE wallet_id=?;"""
    queryargs = (scrape.wallet.id,)
    result = db.query(query, queryargs)
    return result


def get_scrapingtxn_timestamp_end(scrape: ScrapingTxn, db: Db) -> Timestamp:
    result = get_scrapingtxn_ids(scrape, db)
    if len(result) == 0:
        return Timestamp(0)
    if len(result) > 1:
        raise DbError(
            f"""More than 1 scraping txn found for wallet {scrape.wallet} 
            : {result}"""
        )
    return Timestamp(result[0][3])


def update_scrapingtxn(scrape: ScrapingTxn, db: Db) -> None:
    update_scrapingtxn_raw(scrape.scrape_timestamp_end, scrape.wallet.id, db)


def update_scrapingtxn_raw(timestamp_end: int, walletid: int, db: Db) -> None:
    query = "UPDATE scrapingtxn SET scrape_timestamp_end=? WHERE wallet_id=?;"
    queryargs = (timestamp_end, walletid)
    db.execute(query, queryargs)
    db.commit()
