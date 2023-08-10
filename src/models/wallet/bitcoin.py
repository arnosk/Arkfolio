"""
@author: Arno
@created: 2023-05-29
@modified: 2023-08-10

Sitemodel for bitcoin blockchain

"""
import logging
import time

from pycoin.symbols.btc import network  # type: ignore

import config
from src.data.dbschemadata import Asset, Site, TransactionRaw
from src.data.dbschematypes import SiteType, TransactionType, WalletAddressType
from src.data.types import Timestamp
from src.db.db import Db
from src.db.dbasset import insert_asset
from src.errors.modelerrors import WalletAddressTypeError
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
        asset: Asset = Asset(name="Bitcoin", symbol="BTC", decimal_places=8)
        insert_asset(db, asset)

    def check_address(self, address: str) -> WalletAddressType:
        """Check the validity of an address
        0 = incorrect, 1 = normal address,
        2 = xpub bip32, 3 = ypub bip49, 4 = zpub bip84, 5 = electrum mpk"""
        if network.parse.address(address):
            log.debug(f"Validating result: address - {address}")
            return WalletAddressType.NORMAL
        if network.parse.bip32_pub(address):
            log.debug(f"Validating result: xpub - {address}")
            return WalletAddressType.XPUB
        if network.parse.bip49_pub(address):
            log.debug(f"Validating result: ypub - {address}")
            return WalletAddressType.YPUB
        if network.parse.bip84_pub(address):
            log.debug(f"Validating result: zpub - {address}")
            return WalletAddressType.ZPUB
        if network.parse.electrum_pub("E:" + address):
            log.debug(f"Validating result: electrum mpk - {address}")
            return WalletAddressType.ELECTRUM
        log.debug(f"Validating result: invalid address - {address}")
        return WalletAddressType.INVALID

    def get_child_address(self, pub: str, type: WalletAddressType) -> str:
        if type == WalletAddressType.NORMAL or type == WalletAddressType.INVALID:
            raise WalletAddressTypeError(
                f"Wallet address type must be a master public key type: {pub} - {type}"
            )

        # TODO: distinguish child address by childaddresstype: receiving vs change for bitcoin
        # TODO: add column in chlld address table
        # TODO: get nr of existing child addresses in db for receiving and change address
        # TODO: per child address type, calculate next child address
        # TODO: check if the nr of transactions, if greater than 0, add to child address table
        # TODO: repeat until nr of tx is 0 for every child address type, also add this to db
        # TODO: in server, when checking txs, also calculate next child address and check on txs

        if type == WalletAddressType.ELECTRUM:
            wallet = network.parse.electrum_pub("E:" + pub)
            if wallet == None:
                raise WalletAddressTypeError(
                    f"Public key is not an electrum mpk: {pub} - {type}"
                )
            for key in wallet.subkeys("0-4/0-1"):
                log.debug(f"loop:  {key.address()}")
            # receiving addresses
            log.debug(f"{wallet.subkey('0/0').address()}")
            log.debug(f"{wallet.subkey('1/0').address()}")
            log.debug(f"{wallet.subkey('2/0').address()}")
            log.debug(f"{wallet.subkey('3/0').address()}")
            # change addresses
            log.debug(f"{wallet.subkey('0/1').address()}")
            log.debug(f"{wallet.subkey('1/1').address()}")
            log.debug(f"{wallet.subkey('2/1').address()}")
            log.debug(f"{wallet.subkey('3/1').address()}")
            return wallet.subkey("0/0").address()
        # else:
        wallet = None
        if type == WalletAddressType.XPUB:
            wallet = network.parse.bip32_pub(pub)
        if type == WalletAddressType.YPUB:
            wallet = network.parse.bip49_pub(pub)
        if type == WalletAddressType.ZPUB:
            wallet = network.parse.bip84_pub(pub)

        if wallet == None:
            raise WalletAddressTypeError(
                f"Public key or addresstype is not a correct: {pub} - {type}"
            )
        for key in wallet.subkeys("0-1/0-4"):
            log.debug(f"loop:  {key.address()}")
        # receiving addresses
        log.debug(f"{wallet.subkey(0).subkey(0).address()}")
        log.debug(f"{wallet.subkey(0).subkey(1).address()}")
        log.debug(f"{wallet.subkey(0).subkey(2).address()}")
        log.debug(f"{wallet.subkey(0).subkey(3).address()}")
        # change addresses
        log.debug(f"{wallet.subkey(1).subkey(0).address()}")
        log.debug(f"{wallet.subkey(1).subkey(1).address()}")
        log.debug(f"{wallet.subkey(1).subkey(2).address()}")
        log.debug(f"{wallet.subkey(1).subkey(3).address()}")
        return wallet.subkey(0).subkey(0).address()

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
