"""
@author: Arno
@created: 2023-06-01
@modified: 2023-08-10

Database Handler Class

"""
import logging

from src.data.dbschemadata import Profile
from src.db.db import Db
from src.errors.dberrors import DbError

log = logging.getLogger(__name__)


def insert_profile(db: Db, name: str, password: str = "") -> None:
    query = "INSERT OR IGNORE INTO profile (name, password, enabled) VALUES (?,?,?);"
    queryargs = (name, password, True)
    db.execute(query, queryargs)
    db.commit()


def check_profile_exists(db: Db, name: str) -> bool:
    result = get_profile_ids(db, name)
    if len(result) == 0:
        return False
    return True


def get_profile_ids(db: Db, name: str):
    query = "SELECT id FROM profile WHERE name=?;"
    queryargs = (name,)
    result = db.query(query, queryargs)
    return result


def get_profile(db: Db, name: str) -> Profile:
    query = "SELECT id, name, password, enabled FROM profile WHERE name=?;"
    result = db.query(query, (name,))
    log.debug(f"Record of wallet name {name} in database: {result}")
    if len(result) == 0:
        raise DbError(f"No record found of profile: {name} in database")
    return Profile(
        id=result[0][0], name=result[0][1], password=result[0][2], enabled=result[0][3]
    )


def update_profile(db: Db, profile: Profile) -> None:
    query = "UPDATE profile SET name=?, password=?, enabled=? WHERE id=?;"
    queryargs = (profile.name, profile.password, profile.enabled, profile.id)
    db.execute(query, queryargs)
    db.commit()
