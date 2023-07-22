"""
@author: Arno
@created: 2023-05-26
@modified: 2023-07-22

Abstract class for all sites

Writing a new sitemodel must start with defining the id and the sitetype, 
name is set to the classname
The settings can be changed by user in Database, but must be initialized
"""
import logging
from abc import ABC, abstractmethod

from src.data.dbschemadata import Price, Site, TransactionRaw, Wallet
from src.data.types import Timestamp
from src.db.db import Db
from src.db.dbscrapingtxn import (
    get_scrapingtxn_timestamp_end,
    insert_ignore_scrapingtxn_raw,
    update_scrapingtxn_raw,
)
from src.db.dbsitemodel import get_sitemodel, insert_sitemodel, update_sitemodel
from src.db.dbwalletchild import get_walletchild_addresses
from src.srv.serverhelper2 import process_and_insert_rawtransaction

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

    def search_transactions(self, wallet: Wallet, db: Db) -> None:
        log.debug(
            f"Start searching transactions for {wallet.address} on {self.site.name}"
        )
        if wallet.haschild:
            addresses = get_walletchild_addresses(wallet.id, db)
        else:
            addresses = [wallet.address]

        insert_ignore_scrapingtxn_raw(wallet.id, db)
        last_time = get_scrapingtxn_timestamp_end(wallet, db)
        txns = self.get_transactions(addresses, last_time)
        txns.sort()
        log.debug(f"New found transactions: {len(txns)}")
        for txn in txns:
            result_ok = process_and_insert_rawtransaction(
                txn, wallet.profile.id, self.site, db
            )
            if result_ok:
                update_scrapingtxn_raw(txn.timestamp + 1, wallet.id, db)
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
