"""
@author: Arno
@created: 2023-05-29
@modified: 2023-08-16

Sitemodel for bitcoin blockchain

"""
import logging
import time

from pycoin.networks.registry import network_for_netcode  # type: ignore

import config
from src.data.dbschemadata import Asset, Site, TransactionRaw, Wallet, WalletChild
from src.data.dbschematypes import (
    ChildAddressType,
    SiteType,
    TransactionType,
    WalletAddressType,
)
from src.data.types import Timestamp, TransactionInfo
from src.db.db import Db
from src.db.dbasset import insert_asset
from src.db.dbwalletchild import get_nr_walletchildtypes
from src.errors.dberrors import DbError
from src.errors.modelerrors import ChildAddressTypeError, WalletAddressTypeError
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
        network = network_for_netcode("BTC")
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

    def get_new_child_addresses(
        # self, db: Db, parentid: int, pub: str, wallettype: WalletAddressType
        self,
        db: Db,
        wallet: Wallet,
    ) -> list[WalletChild]:
        if (
            wallet.addresstype == WalletAddressType.NORMAL
            or wallet.addresstype == WalletAddressType.INVALID
        ):
            raise WalletAddressTypeError(
                f"Wallet address type must be a master public key type: {wallet}"
            )

        address_receiving = self._get_new_child_addresses(
            db=db,
            wallet=wallet,
            childtype=ChildAddressType.RECEIVING,
        )
        address_change = self._get_new_child_addresses(
            db=db,
            wallet=wallet,
            childtype=ChildAddressType.CHANGE,
        )
        return address_receiving + address_change

    def _get_new_child_addresses(
        self,
        db: Db,
        wallet: Wallet,
        childtype: ChildAddressType,
    ) -> list[WalletChild]:
        if childtype != ChildAddressType.RECEIVING:
            ca_code = 0
        elif childtype != ChildAddressType.CHANGE:
            ca_code = 1
        else:
            raise ChildAddressTypeError(
                f"Child address type must be RECEIVING or CHANGE: {wallet} - {childtype}"
            )

        # Get amount of existing child addresses in db for receiving or change address
        batch_start = get_nr_walletchildtypes(db, wallet.id, childtype)
        batch_size = config.CHILD_ADDRESS_BATCH_SIZE
        network = network_for_netcode(
            "BTC"
        )  # TODO: bring in general place, is also used above, make bitcoin kind of module
        childwallets: list[WalletChild] = []
        check_new_txs = True
        while check_new_txs:
            addresses: list[str] = []
            if wallet.addresstype == WalletAddressType.ELECTRUM:
                k = network.parse.electrum_pub("E:" + wallet.address)
                if k == None:
                    raise WalletAddressTypeError(
                        f"Public key is not an electrum mpk: {wallet}"
                    )
                for key in k.subkeys(
                    f"{batch_start}-{batch_start+batch_size}/{ca_code}"
                ):
                    addresses.append(key.address())
            else:
                k = None
                if wallet.addresstype == WalletAddressType.XPUB:
                    k = network.parse.bip32_pub(wallet.address)
                if wallet.addresstype == WalletAddressType.YPUB:
                    k = network.parse.bip49_pub(wallet.address)
                if wallet.addresstype == WalletAddressType.ZPUB:
                    k = network.parse.bip84_pub(wallet.address)

                if k == None:
                    raise WalletAddressTypeError(
                        f"Public key or addresstype is not a correct: {wallet}"
                    )
                for key in k.subkeys(
                    f"{ca_code}/{batch_start}-{batch_start+batch_size}"
                ):
                    addresses.append(key.address())

            txs_info = self.get_transaction_info(addresses)

            # Check if addresses have txs and repeat if they do
            check_new_txs = False
            for txinfo in txs_info:
                childwallet = WalletChild(
                    parent=wallet, used=True, address=txinfo.address, type=childtype
                )
                childwallets.append(childwallet)
                print(f"Found tx info for {wallet.address:.10}: {txinfo}")
                if txinfo.nr_txs != 0:
                    # Check new transactions, stay in while loop
                    check_new_txs = True
            batch_start = batch_start + batch_size
        return childwallets

    def get_transactions(
        self, addresses: list[str], last_time: Timestamp = Timestamp(0)
    ) -> list[TransactionRaw]:
        log.debug(f"Start getting transactions for {self.site.name}")
        result = _get_transactions_blockchaininfo(addresses, last_time)
        return result

    def get_transaction_info(self, addresses: list[str]) -> list[TransactionInfo]:
        log.debug(f"Start getting transaction info for {self.site.name}")
        result = _get_transaction_info_blockchaininfo(addresses)
        return result


def _get_transaction_info_blockchaininfo(addresses: list[str]) -> list[TransactionInfo]:
    """May raise RemoteError or KeyError
    Order is same
    """
    addresses_str = "|".join(addresses)
    nr_txs: list[TransactionInfo] = []
    backoff = config.BLOCKCHAININFO_BACKOFF
    resp = request_get_dict(
        url=f"https://blockchain.info/balance?active={addresses_str}",
        handle_429=True,
        backoff_in_seconds=backoff,
    )
    for address in addresses:
        tx = resp[address]
        txinfo = TransactionInfo(
            address=address,
            nr_txs=tx["n_tx"],
            final_balance=tx["final_balance"],
            total_received=tx["total_received"],
        )
        nr_txs.append(txinfo)
    log.info(f"Limiting requests to 1 query per {backoff} seconds")
    time.sleep(backoff)
    return nr_txs


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
