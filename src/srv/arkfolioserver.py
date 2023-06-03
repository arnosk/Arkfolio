"""
@author: Arno
@created: 2023-05-18
@modified: 2023-06-02

Server for ArkFolio

"""
import logging
import site
from typing import Protocol

import config
from src.data.dbschemadata import Profile, Site, SiteWallets, Wallet
from src.db.db import Db
from src.db.dbinit import db_init
from src.db.dbwallet import get_all_wallets
from src.models import sitemodel
from src.models.sitemodel import SiteModel
from src.models.sitemodelfinder import find_all_sitemodels

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

    def run(self):
        log.debug("Starting Arkfolio server")

        # sites_w_tx: list[Site] = get_all_sites_with_transaction()

        sites_wallets: dict[int, list[Wallet]] = self.get_wallets_for_txsite(
            self.sitemodels, self.db
        )
        log.debug(f"Found sitemodels: {self.sitemodels}")
        log.debug(f"Found wallets: {sites_wallets}")

        # sites_wallets: list[SiteWallets] = couple_site_to_wallets(sites_w_tx, wallets)

        # loop through site_wallets to get txs
        # how to get from Site object to the SiteModel ???
        # For blockchain wallet: do this per wallet address or per chain api
        # with use of asyncio, ccxt

        # sites_w_price: list[site] = get_all_sites_with_prices()
        # assets_f_prices: list[asset] = get_all_assets_prices()
        # retrieve new prices or historical prices if needed

    def get_wallets_for_txsite(
        self, sitemodels: dict[int, SiteModel], db: Db
    ) -> dict[int, list[Wallet]]:
        walletsraw: list = get_all_wallets(self.db)
        wallets = {}
        for rawdata in walletsraw:
            siteid = rawdata[1]
            profileid = rawdata[2]
            prof = Profile(id=profileid)
            enabled: bool = rawdata[4]
            if enabled:
                sitemodel: SiteModel = sitemodels[siteid]
                wallet = Wallet(
                    site=sitemodel.site,
                    profile=prof,
                    id=rawdata[0],
                    address=rawdata[3],
                    enabled=rawdata[4],
                )
                wallets.setdefault(siteid, []).append(wallet)
        return wallets


# sites filled by an programmer of this program

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
