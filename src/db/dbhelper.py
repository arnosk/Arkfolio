"""
@author: Arno
@created: 2022-11-03
@modified: 2023-05-20

Database Helper function to create tables

"""
from enum import Enum, auto

from src.data.coindata import CoinData
from src.data.dbdata import DbTableName
from src.db.db import Db


def insert_website(db: Db, website: str) -> int:
    """Insert definition of the website or exchange"""
    query = f"INSERT INTO {DbTableName.WEBSITE.value} (name, url) VALUES(?,?)"
    args = (website, "https://")
    res = db.execute(query, args)
    db.commit()
    return res


def get_website_id(db: Db, website: str) -> int:
    """Retrieves the website id"""
    query = f"SELECT id FROM {DbTableName.WEBSITE.value} WHERE name = ?"
    args = (website,)
    res = db.query(query, args)
    if len(res) > 0:
        return res[0][0]
    else:
        return 0


def insert_coin(db: Db, coin: CoinData, website_id: int) -> int:
    """Insert a new coin to the coins table

    return value = rowcount or total changes
    """
    query = f"INSERT INTO {DbTableName.COIN.value} (website_id, siteid, name, symbol, chain, base) VALUES(?,?,?,?,?,?)"
    args = (
        website_id,
        coin.siteid,
        coin.name,  # also quote
        coin.symbol,  # also quote symbol
        coin.chain,
        coin.base,
    )
    res = db.execute(query, args)
    db.commit()
    return res


def delete_coin(db: Db, siteid: str, website_id: int) -> int:
    """Delete an existing coin

    return value = rowcount or total changes
    """
    query = f"DELETE FROM {DbTableName.COIN.value} WHERE siteid=? AND website_id=?"
    args = (siteid, website_id)
    res = db.execute(query, args)
    db.commit()
    return res


def get_coin(db: Db, siteid: str, website_id: int) -> list:
    """Retrieves the coin from id"""
    query = f"SELECT * FROM {DbTableName.COIN.value} WHERE siteid=? AND website_id=?"
    args = (siteid, website_id)
    res = db.query(query, args)
    return res


def get_coins(db: Db, search: str, website_id: int) -> list:
    """Retrieves coins from search string"""
    query = f"""SELECT siteid, name, symbol, chain, base FROM {DbTableName.COIN.value} WHERE
                website_id = {website_id} AND
                (siteid like ? or
                name like ? or
                symbol like ? or
                base like ?
                )
            """
    n = query.count("?")
    args = (f"%{search}%",) * n
    res = db.query(query, args)
    return res


def check_coin_table(db: Db) -> bool:
    """Check existance of coin table"""
    return db.check_table(DbTableName.COIN.value)
