"""
@author: Arno
@created: 2023-05-16
@modified: 2023-09-15

Startup program for ArkFolio

"""
import logging

import config
from src.db.db import Db
from src.logging import config_logging
from src.srv.arkfolioserver import ArkfolioServer
from src.ui.controllers.arkfoliocontroller import ArkfolioController
from src.ui.views.arkfolioviewcli import ArkfolioViewCli

log = logging.getLogger(__name__)


def __main__():
    """ArkFolio program"""
    config_logging()
    db = Db(config.DB_CONFIG)
    try:
        # TODO: Let server run always
        # so split up the server and ui into 2 different programs
        # Server gets asset prices and wallet txs every x min.
        srv = ArkfolioServer(db)
        view = ArkfolioViewCli()
        app = ArkfolioController(db, view)

        # TODO: Implement threading or seperate programs
        srv.run()
        app.run()
    except Exception as e:
        log.exception(e)
    finally:
        db.close()


if __name__ == "__main__":
    __main__()
