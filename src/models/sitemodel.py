"""
@author: Arno
@created: 2023-05-26
@modified: 2023-07-11

Abstract class for all sites

Writing a new sitemodel must start with defining the id and the sitetype, 
name is set to the classname
The settings can be changed by user in Database, but must be initialized
"""
import logging
from abc import ABC, abstractmethod

from src.data.dbschemadata import Price, Site, TransactionRaw
from src.data.types import Timestamp
from src.db.db import Db
from src.db.dbsitemodel import get_sitemodel, insert_sitemodel, update_sitemodel
from src.srv.serverhelper2 import insert_transaction_raw

log = logging.getLogger(__name__)


class SiteModel(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.site: Site

    def model_dbinit(self, db: Db) -> None:
        """Initialization of site model in database
        First time: write sitemodel to database
        All other times: read sitemodel from database
        """
        log.debug(f"Site model initialize {self.site.name} with database")
        insert_sitemodel(self.site, db)
        site = get_sitemodel(self.site.id, db)
        self.site.api = site[3]
        self.site.secret = site[4]
        self.site.hasprice = site[5]
        self.site.enabled = site[6]
        log.debug(f"Init of sitemodel ready {self.site}")

    def asset_dbinit(self, db: Db) -> None:
        """Initialization the assets used by this site model in database"""
        log.debug(f"No Asset initialize for {self.site.name} with database")

    def search_transactions(self, addresses: dict[int, list[str]], db: Db) -> None:
        log.debug(f"Start searching transactions for {self.site.name}")
        for profileid, addresslist in addresses.items():
            txns = self.get_transactions(addresslist, Timestamp(1682081512))
            log.debug(f"New found transactions: {len(txns)}")
            for txn in txns:
                insert_transaction_raw(txn, profileid, self.site, db)
        return

    def get_transactions(
        self, addresses: list[str], last_time: Timestamp = Timestamp(0)
    ) -> list[TransactionRaw]:
        raise NotImplementedError(
            f"Site model {self.__class__.__name__} doesn't have transactions"
        )

    def get_price(self) -> list[Price]:
        if not self.site.hasprice:
            raise NotImplementedError(
                f"Site model {self.__class__.__name__} doesn't have price history"
            )
        return []

    def set_api_secret(self, db: Db, api: str, secret: str) -> None:
        self.site.api = api
        self.site.secret = secret
        update_sitemodel(self.site, db)

    def convert_asset_to_own(self, assetname: str) -> str:
        """Converting assetname on site to the assetname used in this program"""
        return assetname
