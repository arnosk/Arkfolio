"""
@author: Arno
@created: 2022-11-02
@modified: 2023-05-20

Database Class

"""
import logging
import sqlite3
from typing import Any

import config

log = logging.getLogger(__name__)


class Db:
    """Class for database actions

    constructor:
        config(Dict): Database connection params
    usage:
        # SQlite:
        config = {'dbname':':memory:'}
        db=DbSqllite3(config,'sqlite')

        # Next do sql stuff
        db.open()
        ...
        db.close()
    """

    def __init__(self, config: dict):
        self.config = config
        self.conn: sqlite3.Connection = None  # type: ignore

    def __enter__(self):
        try:
            self.open()
        except:
            pass
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        if self.has_connection():
            self.commit()
            self.conn.close()
            self.conn = None  # type: ignore
            log.debug(f"DB Closed")

    def open(self):
        """Function to create and open or only open a connection to the database"""
        if not self.has_connection():
            dbname = self.config["dbname"]
            self.conn = sqlite3.connect(dbname, timeout=10)
            log.debug(f"DB Connected: {dbname}")
        else:
            log.debug(f"DB already connected {self.conn}")

    def execute(self, sql: str, params=None) -> int:
        """Execute a query

        Executes a query and returns number of rows or number of changes
        For SQLite cursor.rowcount doesn't exists

        sql = query to execute,
        params = dictionary for parameters in query
        return value = rowcount or total changes
        """
        log.debug(f"DB execute: {sql}, {params}")
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        result = self.conn.total_changes
        cursor.close()
        return result

    def query(self, sql: str, params=None) -> list[Any]:
        """Execute a query and returns the result

        sql = query to execute,
        params = dictionary for parameters in query
        return value = fetched data from query
        """
        log.debug(f"DB query: {sql}, {params}")
        cursor = self.conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def executescript(self, script: str) -> int:
        """Execute a script (must have COMMIT;)"""
        max_chars = config.MAX_CHAR_LOG_SCRIPT_LENGHT
        log.debug(
            f"DB script start: {script[:max_chars]}"
            f"{'...' if len(script)>max_chars else ''}"
        )
        cursor = self.conn.cursor()
        cursor.executescript(script)
        result = self.conn.total_changes
        log.debug(f"DB script end, Total changes: {result}")
        return result

    def commit(self):
        self.conn.commit()

    def rollback(self):
        log.debug(f"DB Rollback start")
        self.conn.rollback()
        log.debug(f"DB Rollback ready")

    def has_connection(self):
        return self.conn != None
