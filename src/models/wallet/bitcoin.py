"""
@author: Arno
@created: 2023-05-29
@modified: 2023-05-29

Dynamically search for SiteModel

"""
import logging

from src.data.dbschemadata import Site, Transaction
from src.data.dbschematypes import SiteType
from src.db.db import Db
from src.func.helperfunc import convert_timestamp
from src.models.sitemodel import SiteModel
from src.req.requesthelper import request_get_dict

log = logging.getLogger(__name__)


class Bitcoin(SiteModel):
    def __init__(self):
        super().__init__()
        self.site = Site(
            id=1,
            name=self.__class__.__name__,
            sitetype=SiteType.BLOCKCHAIN,
            api="",
            secret="",
            hasprice=False,
            enabled=True,
        )

    def get_transactions(self, addresses: list[str]) -> list[Transaction]:
        log.debug(f"Start getting transactions for {self.site.name}")
        x = _get_transactins_blockchaininfo(addresses)
        log.debug(f"Result: {x}")
        return []


def _get_transactins_blockchaininfo(
    accounts: list[str],
) -> dict[str, tuple[bool, float]]:
    """May raise RemoteError or KeyError"""
    transactions = {}
    # params = "|".join(accounts)
    for acc in accounts:
        resp = request_get_dict(
            url=f"https://blockchain.info/rawaddr/{acc}",
            handle_429=True,
            # If we get a 429 then their docs suggest 10 seconds
            # https://blockchain.info/
            backoff_in_seconds=15,
        )

        n_tx = resp["n_tx"]
        balance = resp["final_balance"]
        print(f"Address {acc} has {n_tx} txs, balance = {balance}")
        i = 0
        for tx in resp["txs"]:
            i = i + 1
            # print(f"TX {i}: {tx}")
            tx_in = False
            tx_out = False
            tx_fee = 0
            tx_value = 0
            address_in = ""
            address_out = ""
            tx_time = tx["time"]
            for input in tx["inputs"]:
                # print(f"input: {input}")
                address_in = input["prev_out"]["addr"]
                if address_in == acc:
                    tx_in = True
                    tx_fee = tx["fee"]
                    tx_value = input["value"]

            for output in tx["out"]:
                # print(f"output {output}")
                addr = output.get("addr", "unknown")
                if addr == acc:
                    tx_out = True
                    address_out = addr
                    tx_value = output["value"]

            timestr = convert_timestamp(tx_time)
            print(
                f"tx {i}: {timestr} in {tx_in}, out {tx_out}, fee {tx_fee}, value {tx_value}, "
                f"From {tx_in} {address_in} to {tx_out} {address_out} "
            )

    return transactions
