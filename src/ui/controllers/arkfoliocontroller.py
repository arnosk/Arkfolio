"""
@author: Arno
@created: 2023-05-18
@modified: 2023-07-10

Controller for ArkFolio

"""
import logging
from typing import Protocol

from src.data.dbschemadata import Profile, Wallet
from src.db.db import Db
from src.db.dbprofile import check_profile_exists, get_profile, insert_profile
from src.db.dbwallet import check_wallet_exists, insert_wallet
from src.models.sitemodel import SiteModel
from src.srv.arkfolioserver import ArkfolioServer

log = logging.getLogger(__name__)


class ArkfolioView(Protocol):
    def show_help(self) -> None:
        ...


class ArkfolioController:
    """Controller for Arkfolio program"""

    def __init__(self, view: ArkfolioView, db: Db, server: ArkfolioServer) -> None:
        self.view = view
        self.db = db
        self.srv = server
        self.profile: Profile

    def run(self):
        log.debug("Starting Arkfolio controller")

        # TODO: Use profiles, for now only 1 profile
        self.set_profile(name="Profile 1")

        # TODO: User must be able to choose form sites to create new wallets
        # sitemodels: list[SiteModel] = self.srv.get_sitemodels()
        sitemodels: dict[int, SiteModel] = self.srv.sitemodels

        # Temp for testing first site, create wallet in db
        self.create_wallet(sitemodels[1], "1PeizMg76Cf96nUQrYg8xuoZWLQozU5zGW")

    def set_profile(self, name: str) -> None:
        """Set to profile to name
        If doesn't exist yet, create new profile with this name
        """
        if not check_profile_exists(name, self.db):
            insert_profile(name, self.db)
        self.profile = get_profile(name, self.db)

    def create_wallet(self, sitemodel: SiteModel, address: str) -> None:
        address_ok = sitemodel.check_address(address)
        if address_ok == 0:
            log.info(f"{sitemodel.site.name} address is not valid: {address}")
            return

        wallet = Wallet(site=sitemodel.site, profile=self.profile, address=address)
        wallet_exists = check_wallet_exists(wallet, self.db)
        if wallet_exists:
            log.info(
                f"Wallet already exists with same site/chain and address: "
                f"{'No site' if wallet.site == None else wallet.site.name}, {wallet.address}"
            )
            return

        insert_wallet(wallet, self.db)
