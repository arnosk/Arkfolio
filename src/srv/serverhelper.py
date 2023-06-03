"""
@author: Arno
@created: 2023-06-03
@modified: 2023-06-03

Helper functions for Server

"""
import logging

from src.data.dbschemadata import Profile, Wallet
from src.db.db import Db
from src.db.dbwallet import get_all_wallets
from src.models.sitemodel import SiteModel


def get_wallets_per_site(
    sitemodels: dict[int, SiteModel], db: Db
) -> dict[int, list[Wallet]]:
    """Get all wallets from database

    And return a dict with key = Site.id and values = list of wallets
    """
    walletsraw: list = get_all_wallets(db)
    wallets = {}
    for rawdata in walletsraw:
        siteid = rawdata[1]
        profileid = rawdata[2]
        profile = Profile(id=profileid)
        enabled: bool = rawdata[4]
        if enabled:
            sitemodel: SiteModel = sitemodels[siteid]
            if sitemodel.site.enabled:
                wallet = Wallet(
                    site=sitemodel.site,
                    profile=profile,
                    id=rawdata[0],
                    address=rawdata[3],
                    enabled=rawdata[4],
                )
                wallets.setdefault(siteid, []).append(wallet)
    return wallets
