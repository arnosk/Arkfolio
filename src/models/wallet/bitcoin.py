"""
@author: Arno
@created: 2023-05-29
@modified: 2023-07-10

Sitemodel for bitcoin blockchain

"""
import logging
import time

import coinaddrvalidator  # import ValidationResult, validate

import config
from src.data.dbschemadata import Asset, Site, TransactionRaw
from src.data.dbschematypes import SiteType, TransactionType
from src.data.types import Timestamp
from src.db.db import Db
from src.db.dbasset import insert_asset
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

    def asset_dbinit(self, db: Db) -> None:
        """Initialize asset bitcoin, BTC. No AssetOnSite necessary"""
        log.debug(f"Asset initialize for {self.site.name} with database")
        asset = Asset(name="Bitcoin", symbol="BTC", decimal_places=8)
        insert_asset(asset, db)

    def check_address(self, address: str) -> int:
        """Check the validity of an address
        0 = incorrect, 1 = ok, 2 = ok, but is master public key"""
        validation: coinaddrvalidator.ValidationResult = coinaddrvalidator.validate(
            "btc", address
        )
        result: bool = False
        if validation.name != "":
            result = validation.valid + validation.is_extended
        log.debug(f"Validating result: {result} ; {validation}")
        return result

    def get_transactions(
        self, addresses: list[str], last_time: Timestamp = Timestamp(0)
    ) -> list[TransactionRaw]:
        log.debug(f"Start getting transactions for {self.site.name}")
        result = _get_transactions_blockchaininfo(addresses, last_time)
        return result


def _get_transactions_blockchaininfo(
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
            txs = resp["txs"]
            log.debug(f"Address {acc} has {n_tx} all time txns, balance={balance}")
            log.debug(
                f"Reading {len(txs)} txns from offset={offset}, last time={last_time} ({convert_timestamp(last_time)})"
            )
            for tx in txs:
                tx_i = tx_i + 1
                tx_type = TransactionType.UNDEF_UNDEFINED
                tx_fee = 0
                tx_value = 0
                address_from = ""
                address_to = ""
                tx_time = tx["time"]

                if tx_time <= int(last_time):
                    log.debug(
                        f"Stop reading txns because tx time <= last time:"
                        f"{tx_time} ({convert_timestamp(tx_time)} <= "
                        f"{last_time} ({convert_timestamp(last_time)}"
                    )
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
                log.debug(f"{tx_i}: {tx_time} ({timestr}) - {txn.txid}")

            finished = tx_i >= n_tx or tx_time <= int(last_time)
            log.info(f"Limiting requests to 1 query per {backoff} seconds")
            time.sleep(backoff)

    return transactions
