"""
@author: Arno
@created: 2023-05-18
@modified: 2023-10-20

Controller for ArkFolio

"""
import logging
from dataclasses import asdict
from typing import Protocol

import pandas as pd
from pandas import DataFrame

import configprivate as conf
from src.data.dbschemadata import Profile, Transaction, Wallet
from src.data.dbschematypes import WalletAddressType
from src.db.db import Db
from src.db.dbinit import db_connect
from src.db.dbprofile import check_profile_exists, get_profile, insert_profile
from src.db.dbwallet import check_wallet_exists, get_one_wallet_id, insert_wallet
from src.errors.dberrors import DbError
from src.func.helperfunc import convert_timestamp
from src.models.sitemodel import SiteModel
from src.models.sitemodelfinder import find_all_sitemodels
from src.ui.controllers.controllerhelper import get_transactions

log = logging.getLogger(__name__)


class ArkfolioView(Protocol):
    def run(self, control) -> None:
        ...


class ArkfolioController:
    """Controller for Arkfolio program"""

    def __init__(self, db: Db, view: ArkfolioView) -> None:
        self.view = view
        self.db = db
        self.profile: Profile
        db_connect(self.db)
        self.sitemodels: dict[int, SiteModel] = find_all_sitemodels()
        for sitemodel in self.sitemodels.values():
            log.debug(f"Sitemodel: {sitemodel}")
            sitemodel.model_dbread(self.db)

    def run(self):
        log.info("Starting Arkfolio controller")

        # TODO: Use profiles, for now only 1 profile
        self.set_profile(name="Profile 1")
        # self.tempCreateTestWallets()

        self.view.run(self)

    def set_profile(self, name: str) -> None:
        """Set to profile to name
        If doesn't exist yet, create new profile with this name
        """
        if not check_profile_exists(self.db, name):
            insert_profile(self.db, name)
        self.profile = get_profile(self.db, name)

    def get_txns(self) -> DataFrame:
        """Get transactions from database
        And convert to pandas dataframe"""
        txns: list[Transaction] = get_transactions(self.db, self.profile)
        txnsview: list = []
        for txn in txns:
            from_walletchildaddress = ""
            from_walletchildtype = ""
            to_walletchildaddress = ""
            to_walletchildtype = ""
            if txn.from_wallet.haschild and txn.from_walletchild != None:
                from_walletchildaddress = txn.from_walletchild.address
                from_walletchildtype = txn.from_walletchild.type.name
            if txn.to_wallet.haschild and txn.to_walletchild != None:
                to_walletchildaddress = txn.to_walletchild.address
                to_walletchildtype = txn.to_walletchild.type.name
            t = {
                "datetime": convert_timestamp(txn.timestamp),
                "txn_type": txn.transactiontype.name,
                "site": txn.site.name,
                "quantity": txn.quantity.amount,
                "quantity.currency": txn.quantity.currency_symbol,
                "fee": txn.fee.amount,
                "fee.currency": txn.fee.currency_symbol,
                "from_type": txn.from_wallet.addresstype.name,
                "from_wallet.name": txn.from_wallet.name,
                "from_wallet.address": txn.from_wallet.address,
                "from_child.address": from_walletchildaddress,
                "from_child.type": from_walletchildtype,
                "to_type": txn.to_wallet.addresstype.name,
                "to_wallet.name": txn.to_wallet.name,
                "to_wallet.address": txn.to_wallet.address,
                "to_child.address": to_walletchildaddress,
                "to_child.type": to_walletchildtype,
                "note": txn.note,
                "id": txn.id,
            }
            txnsview.append(t)

        df = pd.DataFrame(txnsview)
        return df

    def create_wallet(self, sitemodel: SiteModel, address: str) -> None:
        addresstype: WalletAddressType = sitemodel.check_address(address)
        if addresstype == WalletAddressType.INVALID:
            log.info(f"{sitemodel.site.name} addresstype is not valid: {address}")
            return

        wallet = Wallet(
            site=sitemodel.site,
            profile=self.profile,
            address=address,
            addresstype=addresstype,
        )
        if (
            addresstype == WalletAddressType.XPUB
            or addresstype != WalletAddressType.YPUB
            or addresstype != WalletAddressType.ZPUB
            or addresstype != WalletAddressType.ELECTRUM
        ):
            wallet.haschild = True
        wallet_exists = check_wallet_exists(self.db, wallet)
        if wallet_exists:
            log.info(
                f"Wallet already exists with same site/chain and address: "
                f"{'No site' if wallet.site == None else wallet.site.name}, {wallet.address}"
            )
            return

        insert_wallet(self.db, wallet)

        if not wallet.haschild:
            return

        # Create child addresses for master address
        parentid = get_one_wallet_id(
            self.db, address, sitemodel.site.id, self.profile.id
        )
        if parentid == 0:
            raise DbError(
                f"No wallet found for just created master address: {address} for site {sitemodel.site.name}"
            )
        wallet.id = parentid
        sitemodel.check_for_new_childwallets(self.db, wallet)

    def tempCreateTestWallets(self) -> None:
        # Temp for testing first site, create wallet in db
        self.create_wallet(self.sitemodels[1], conf.BTC_ADDRESS[1])  # a whale
        self.create_wallet(self.sitemodels[1], conf.BTC_ADDRESS[2])  # xpub
        self.create_wallet(self.sitemodels[1], conf.BTC_ADDRESS[3])  # electrum mpk
