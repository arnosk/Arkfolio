"""
@author: Arno
@created: 2023-05-29
@modified: 2023-05-29

Dynamically search for SiteModel

"""
import logging
import time
from re import T

import config
from src.data.dbschemadata import Site, Transaction, TransactionRaw, Wallet
from src.data.dbschematypes import SiteType, TransactionType
from src.data.types import Timestamp
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

    def get_transactions(self, addresses: dict[int, list[str]]) -> list[Transaction]:
        log.debug(f"Start getting transactions for {self.site.name}")
        for profileid, addresslist in addresses.items():
            x = _get_transactins_blockchaininfo(addresslist, Timestamp(1682081512))
            log.debug(f"Result: {x}")
        return []


def _get_transactins_blockchaininfo(
    accounts: list[str], last_time: Timestamp = Timestamp(0)
) -> list[TransactionRaw]:
    """May raise RemoteError or KeyError
    First tx from blockchain.info is newest
    """
    transactions: list[TransactionRaw] = []
    backoff = config.BLOCKCHAININFO_BACKOFF
    for acc in accounts:
        finished = False
        tx_i = 0
        tx_time = 1
        while not finished:
            offset = tx_i
            params = f"offset={offset}"

            resp = request_get_dict(
                url=f"https://blockchain.info/rawaddr/{acc}?{params}",
                handle_429=True,
                backoff_in_seconds=backoff,
            )

            n_tx = resp["n_tx"]
            balance = resp["final_balance"]
            print(f"Address {acc} has {n_tx} txs, balance = {balance}")
            for tx in resp["txs"]:
                tx_i = tx_i + 1
                # print(f"TX {tx_i}: {tx}")
                tx_type = TransactionType.UNDEF_UNDEFINED
                tx_fee = 0
                tx_value = 0
                address_from = ""
                address_to = ""
                tx_time = tx["time"]

                if tx_time <= int(last_time):
                    break

                for input in tx["inputs"]:
                    # print(f"input: {input}")
                    address_from = input["prev_out"]["addr"]
                    if address_from == acc:
                        tx_type = TransactionType.OUT_UNDEFINED
                        tx_fee = tx["fee"]
                        tx_value = input["value"]

                for output in tx["out"]:
                    # print(f"output {output}")
                    addr = output.get("addr", "unknown")
                    if addr == acc:
                        tx_type = TransactionType.IN_UNDEFINED
                        address_to = addr
                        tx_value = output["value"]

                txn = TransactionRaw(
                    transactiontype=tx_type,
                    timestamp=tx_time,
                    txid=tx["hash"],
                    quantity=tx_value,
                    fee=tx_fee,
                    from_wallet=address_from,
                    to_wallet=address_to,
                    quote_asset="BTC",
                    fee_asset="BTC",
                )
                transactions.append(txn)
                timestr = convert_timestamp(tx_time)
                print(f"{tx_i}: {txn}")

            finished = tx_i >= n_tx or tx_time <= int(last_time)
            log.info(f"Limiting requests to 1 query per {backoff} seconds")
            time.sleep(backoff)

    return transactions
