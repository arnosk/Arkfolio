"""
@author: Arno
@created: 2023-05-18
@modified: 2023-08-26

Server for ArkFolio

"""
import logging

from requests import RequestException

from src.data.dbschemadata import Wallet
from src.db.db import Db
from src.db.dbinit import db_init
from src.errors.dberrors import DbError
from src.models.sitemodel import SiteModel
from src.models.sitemodelfinder import find_all_sitemodels
from src.srv.serverhelper import get_wallets_per_site

log = logging.getLogger(__name__)


class ArkfolioServer:
    """Arkfolio server"""

    def __init__(self, db: Db) -> None:
        self.db = db
        db_init(self.db)
        self.sitemodels: dict[int, SiteModel] = find_all_sitemodels()
        for sitemodel in self.sitemodels.values():
            log.debug(f"Sitemodel: {sitemodel}")
            sitemodel.model_dbinit(self.db)
            sitemodel.asset_dbinit(self.db)

    def run(self):
        log.info("Starting Arkfolio server")

        # Go through all wallets to get new transactions
        self.process_wallets()

    def process_wallets(self):
        sites_wallets: dict[int, list[Wallet]] = get_wallets_per_site(
            self.sitemodels, self.db
        )
        log.debug(f"Found sitemodels: {self.sitemodels}")
        log.debug(f"Found wallets: {sites_wallets}")

        for siteid, wallets in sites_wallets.items():
            for wallet in wallets:
                # TODO: This must be done every day...
                # TODO: Errors, like no connection, database fault must be shown to user
                try:
                    self.sitemodels[siteid].search_transactions(self.db, wallet)
                except (DbError, RequestException) as e:
                    log.exception(f"Error: {e}")

            log.debug(f"Wallets for {self.sitemodels[siteid].site.name} updated")

        # For blockchain wallet: do this per wallet address or per chain api
        # with use of asyncio, ccxt

        # sites_w_price: list[site] = get_all_sites_with_prices()
        # assets_f_prices: list[asset] = get_all_assets_prices()
        # retrieve new prices or historical prices if needed


# User has to add a wallet or exchange,
# this will add a wallet and a site for interfacing
# asset is added to list, for historical prices and for balances
# with new transactions with unknown assets, als oadds to list for pricing and balances

# from all blockchain/exchange module (inherits site.py) in folder x
# automatically load module on startup, without specifying it in code
# and add it to sites table, when new. If enabled user can select it.
# freqtrade has such mechanism


def add_site():
    """Adding a site"""


def add_wallet():
    """Adding a exchange wallet or blockchain wallet"""


def add_wallet_blockchain():
    """Adding blockchain wallet
    Adds blockchain to site list if not exists in site list
    Adds address to wallet list
    update internal memory with get_all_sites_w_tx, get_all_assets_prices
    """


def add_wallet_exchange():
    """Adding a exchange wallet
    Adds exchange to sit list if not exist in site list
    Adds exchange to wallet list if new
    update internal memory with get_all_sites_w_tx,
    update internal memory get_all_assets_prices dependinfg on found transactions, so not best places
    """
