"""
@author: Arno
@created: 2023-05-29
@modified: 2023-05-29

Dynamically search for SiteModel

"""
import logging

from src.data.dbschemadata import Site
from src.data.dbschematypes import SiteType
from src.db.db import Db
from src.models.sitemodel import SiteModel

log = logging.getLogger(__name__)


class Bitcoin(SiteModel):
    def model_init(self, db: Db) -> None:
        self.site = Site(
            id=1,
            name=self.__class__.__name__,
            sitetype=SiteType.BLOCKCHAIN,
            api="",
            secret="",
            hasprice=False,
            enabled=True,
        )
        self._model_init(db)
