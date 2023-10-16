"""
@author: Arno
@created: 2023-10-16
@modified: 2023-10-16

Helper functions for Controller

"""
import logging

from src.data.dbschemadata import Profile, Transaction, Wallet
from src.data.dbschematypes import WalletAddressType
from src.db.db import Db
from src.db.dbtransaction import get_db_transactions
from src.func.helperfunc import convert_timestamp

log = logging.getLogger(__name__)


def get_transactions(db: Db, profile: Profile) -> list[Transaction]:
    txns: list[Transaction] = []
    result = get_db_transactions(db, profile.id)
    if len(result) > 0:
        for res in result:
            print(f"{convert_timestamp(res[1])}:{res}")
    return txns
