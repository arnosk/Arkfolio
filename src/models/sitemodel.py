"""
@author: Arno
@created: 2023-05-26
@modified: 2023-08-19

Abstract class for all sites

Writing a new sitemodel must start with defining the id and the sitetype, 
name is set to the classname
The settings can be changed by user in Database, but must be initialized
"""
import logging
import profile
from abc import ABC, abstractmethod

from src.data.dbschemadata import Price, Site, TransactionRaw, Wallet, WalletChild
from src.data.dbschematypes import WalletAddressType
from src.data.types import Timestamp, TransactionInfo
from src.db.db import Db
from src.db.dbscrapingtxn import (
    get_scrapingtxn_timestamp_end,
    insert_ignore_scrapingtxn_raw,
    update_scrapingtxn_raw,
)
from src.db.dbsitemodel import get_sitemodel, insert_sitemodel, update_sitemodel
from src.db.dbwallet import get_wallet_id_unknowns
from src.db.dbwalletchild import (
    get_walletchild_addresses,
    insert_walletchild,
    update_child_of_wallet_unkowns,
)
from src.errors.modelerrors import WalletIdError
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
        insert_sitemodel(db, self.site)
        site = get_sitemodel(db, self.site.id)
        self.site.api = site[3]
        self.site.secret = site[4]
        self.site.hasprice = site[5]
        self.site.enabled = site[6]
        log.debug(f"Init of sitemodel ready {self.site}")

    def set_api_secret(self, db: Db, api: str, secret: str) -> None:
        self.site.api = api
        self.site.secret = secret
        update_sitemodel(db, self.site)

    def search_transactions(self, db: Db, wallet: Wallet) -> None:
        log.debug(f"Check for new transactions {self.site.name}-{wallet.address}")
        if (
            wallet.addresstype == WalletAddressType.INVALID
            or wallet.addresstype == WalletAddressType.UNKNOWN
        ):
            logging.exception(
                f"Not searching transactions for {wallet.addresstype} wallet: {self.site.name}-{wallet.address}"
            )
            return
        if wallet.haschild:
            self.check_for_new_childwallets(db, wallet)
        self._search_transactions(db, wallet)

    def _search_transactions(self, db: Db, wallet: Wallet) -> None:
        log.debug(f"Start searching transactions for {self.site.name}-{wallet.address}")
        if wallet.haschild:
            addresses = get_walletchild_addresses(db, wallet.id)
        else:
            addresses = [wallet.address]

        insert_ignore_scrapingtxn_raw(db, wallet.id)
        last_time = get_scrapingtxn_timestamp_end(db, wallet)
        txns = self.get_transactions(addresses, last_time)
        txns.sort()
        log.debug(f"New found transactions: {len(txns)}")
        for txn in txns:
            result_ok = process_and_insert_rawtransaction(
                db, txn, wallet.profile.id, self.site
            )
            if result_ok:
                update_scrapingtxn_raw(db, txn.timestamp + 1, wallet.id)
        return

    def check_for_new_childwallets(self, db: Db, wallet: Wallet):
        log.debug(f"Check for new child wallets {self.site.name}-{wallet.address}")
        if wallet.id == 0:
            raise WalletIdError(f"No id in structure for wallet: {wallet}")
        childwallets = self.get_new_child_addresses(db, wallet)
        for child in childwallets:
            # TODO: get unknown wallet, check if this wallet has an child with same address,
            # TODO: if so change the properties of that child to new master
            wallet_uknowns_parent_id = get_wallet_id_unknowns(
                db, self.site.id, wallet.profile.id
            )
            if wallet_uknowns_parent_id > 0:
                update_child_of_wallet_unkowns(db, wallet_uknowns_parent_id, child)
            else:
                insert_walletchild(db, child)
        for child in childwallets:
            log.debug(
                f"New child address: {child.address} - {child.type} - {child.parent.addresstype} - {child.parent.address:.10}"
            )

    ### From here to be Implemented in new sitemodel

    def asset_dbinit(self, db: Db) -> None:
        """Initialization the assets used by this site model in database"""
        log.debug(f"No Asset initialize for {self.site.name} with database")

    def check_address(self, address: str) -> WalletAddressType:
        """Check the validity of an address
        0 = incorrect, 1 = normal address, 2 = unkown wallet,
        3 = xpub bip32, 4 = ypub bip49, 5 = zpub bip84, 6 = electrum mpk"""
        log.debug(f"No check for {self.site.name} address")
        return WalletAddressType.INVALID

    def get_transactions(
        self, addresses: list[str], last_time: Timestamp = Timestamp(0)
    ) -> list[TransactionRaw]:
        raise NotImplementedError(
            f"Site model {self.__class__.__name__} doesn't have transactions"
        )

    def get_transaction_info(self, addresses: list[str]) -> list[TransactionInfo]:
        raise NotImplementedError(
            f"Site model {self.__class__.__name__} doesn't have transactions"
        )

    def get_new_child_addresses(self, db: Db, wallet: Wallet) -> list[WalletChild]:
        return []

    def get_price(self) -> list[Price]:
        if not self.site.hasprice:
            raise NotImplementedError(
                f"Site model {self.__class__.__name__} doesn't have price history"
            )
        return []

    def convert_asset_to_own(self, assetname: str) -> str:
        """Converting assetname on info site to the assetname used in this program
        Every site uses its own handle for an asset"""
        return assetname
