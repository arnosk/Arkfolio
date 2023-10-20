"""
@author: Arno
@created: 2023-05-16
@modified: 2023-10-20

Startup program for ArkFolio UI

"""
import logging

import config
from src.db.db import Db
from src.logging import config_logging
from src.ui.controllers.arkfoliocontroller import ArkfolioController
from src.ui.views.arkfolioviewcli import ArkfolioViewCli
from src.ui.views.arkfolioviewtk import ArkfolioViewTk

log = logging.getLogger(__name__)


def __main__():
    """ArkFolio UI"""
    config_logging()
    db = Db(config.DB_CONFIG)
    try:
        # view_cli = ArkfolioViewCli()
        # app = ArkfolioController(db, view_cli)
        view_tk = ArkfolioViewTk()
        app = ArkfolioController(db, view_tk)
        app.run()
    except Exception as e:
        log.exception(e)
    finally:
        db.close()


if __name__ == "__main__":
    __main__()
