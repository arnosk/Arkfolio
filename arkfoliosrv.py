"""
@author: Arno
@created: 2023-05-16
@modified: 2023-09-15

Startup program for ArkFolio Server

"""
import logging

import config
from src.db.db import Db
from src.logging import config_logging
from src.srv.arkfolioserver import ArkfolioServer

log = logging.getLogger(__name__)


def __main__():
    """ArkFolio Server"""
    config_logging()
    db = Db(config.DB_CONFIG)
    try:
        srv = ArkfolioServer(db)
        srv.run()
    except Exception as e:
        log.exception(e)
    finally:
        db.close()


if __name__ == "__main__":
    __main__()
