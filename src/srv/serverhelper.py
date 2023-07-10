"""
@author: Arno
@created: 2023-06-03
@modified: 2023-07-10

Helper functions for Server

"""
import logging

from src.data.dbschemadata import Profile, Wallet
from src.db.db import Db
from src.db.dbwallet import get_all_active_wallets
from src.models.sitemodel import SiteModel

log = logging.getLogger(__name__)


def get_wallets_per_site(
    sitemodels: dict[int, SiteModel], db: Db
) -> dict[int, list[Wallet]]:
    """Get all wallets from database

    And return a dict with key = Site.id and values = list of wallets
    """
    walletsraw: list = get_all_active_wallets(db)
    wallets = {}
    for rawdata in walletsraw:
        siteid = rawdata[1]
        profileid = rawdata[2]
        profile = Profile(id=profileid)
        sitemodel: SiteModel = sitemodels[siteid]
        if sitemodel.site.enabled:
            wallet = Wallet(
                site=sitemodel.site,
                profile=profile,
                id=rawdata[0],
                name=rawdata[3],
                address=rawdata[4],
                haschild=rawdata[7],
            )
            wallets.setdefault(siteid, []).append(wallet)
    return wallets
