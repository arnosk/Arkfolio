"""
@author: Arno
@created: 2023-05-18
@modified: 2023-08-16

Controller for ArkFolio

"""
import logging
from typing import Protocol

import configprivate as conf
from src.data.dbschemadata import Profile, Wallet
from src.data.dbschematypes import WalletAddressType
from src.db.db import Db
from src.db.dbprofile import check_profile_exists, get_profile, insert_profile
from src.db.dbwallet import check_wallet_exists, get_wallet_id2_one, insert_wallet
from src.errors.dberrors import DbError
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
        self.create_wallet(sitemodels[1], conf.BTC_ADDRESS[1])  # a whale
        self.create_wallet(sitemodels[1], conf.BTC_ADDRESS[2])  # xpub
        self.create_wallet(sitemodels[1], conf.BTC_ADDRESS[3])  # electrum mpk

    def set_profile(self, name: str) -> None:
        """Set to profile to name
        If doesn't exist yet, create new profile with this name
        """
        if not check_profile_exists(self.db, name):
            insert_profile(self.db, name)
        self.profile = get_profile(self.db, name)

    def create_wallet(self, sitemodel: SiteModel, address: str) -> None:
        addresstype: WalletAddressType = sitemodel.check_address(address)
        if addresstype == WalletAddressType.INVALID:
            log.info(f"{sitemodel.site.name} address is not valid: {address}")
            return

        wallet = Wallet(
            site=sitemodel.site,
            profile=self.profile,
            address=address,
            addresstype=addresstype,
        )
        if addresstype != WalletAddressType.NORMAL:
            wallet.haschild = True
        wallet_exists = check_wallet_exists(self.db, wallet)
        if wallet_exists:
            log.info(
                f"Wallet already exists with same site/chain and address: "
                f"{'No site' if wallet.site == None else wallet.site.name}, {wallet.address}"
            )
            #### temp
            if addresstype == WalletAddressType.NORMAL:
                return
            parentid = get_wallet_id2_one(
                self.db, address, sitemodel.site.id, self.profile.id
            )
            wallet.id = parentid
            childaddresses = sitemodel.get_new_child_addresses(
                db=self.db,
                wallet=wallet,
            )
            #### end temp
            return

        insert_wallet(self.db, wallet)

        if addresstype == WalletAddressType.NORMAL:
            return

        # calcultate child addresses for public address
        parentid = get_wallet_id2_one(
            self.db, address, sitemodel.site.id, self.profile.id
        )
        if parentid == 0:
            raise DbError(
                f"No wallet found with address: {address} for site {sitemodel.site.name}"
            )
        wallet.id = parentid
        childaddresses = sitemodel.get_new_child_addresses(self.db, wallet)
