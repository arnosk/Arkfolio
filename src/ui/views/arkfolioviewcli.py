"""
@author: Arno
@created: 2023-05-16
@modified: 2023-10-23

Command editor UI for ArkFolio

"""
import logging
import sys
from sre_compile import isstring

from pandas import DataFrame

from src.ui.controllers.arkfoliocontroller import ArkfolioController
from src.ui.views.viewclihelper import Command, get_input_command

log = logging.getLogger(__name__)


class ArkfolioViewCli:
    """UI CLI class for ArkFolio"""

    def __init__(self) -> None:
        pass

    def run(self, control: ArkfolioController) -> None:
        """CLI UI Starting point:"""
        self.control = control
        self.menu_main()

    def menu_main(self) -> None:
        """CLI UI main program:"""
        while True:
            cmd = get_input_command("Main> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    sys.exit("Exiting")
                case Command(command="help" | "h"):
                    self.show_help()
                case Command(
                    command="transactions" | "transaction" | "txns" | "txn" | "t"
                ):
                    self.menu_txns()
                case Command(command="wallets" | "wallet" | "w"):
                    self.menu_wallet()
                case Command(command="portfolio" | "p"):
                    self.menu_portfolio()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def menu_txns(self) -> None:
        """CLI UI transactions"""
        while True:
            cmd = get_input_command("Transaction> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case Command(command="show" | "s"):
                    self.txns_show()
                case Command(command="filter" | "f"):
                    self.show_help()
                case Command(command="export" | "e"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def menu_wallet(self) -> None:
        """CLI UI wallets"""
        while True:
            cmd = get_input_command("Wallet> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case Command(command="show" | "s"):
                    self.wallets_show()
                case Command(command="add" | "a", arguments=[id_name, *rest]):
                    self.wallets_add_check(cmd, id_name)
                case Command(command="add" | "a"):
                    self.wallets_show_sitemodels()
                case Command(command="remove" | "rem" | "r" | "del" | "d"):
                    self.show_help()
                case Command(command="update" | "u"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def menu_portfolio(self) -> None:
        """CLI UI portfolio"""
        while True:
            cmd = get_input_command("Portfolio> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case Command(command="show" | "s"):
                    self.portfolio_show()
                case Command(command="graph" | "g"):
                    self.show_help()
                case Command(command="filter" | "f"):
                    self.show_help()
                case Command(command="export" | "e"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def show_help(self) -> None:
        print("---------------------------------")
        print("    Help for Arkfolio CLI UI")
        print("---------------------------------")
        print("Quit/Exit         - Quits program or back to previous menu")
        print("Help              - This help message")
        print("Transactions      - Open txns menu")
        print("    Show              - Show txns")
        print("    Filter            - Filter txns on site, address, start, end data")
        print("    Export            - Export txns, according to selected filter")
        print("Wallet            - Open wallet menu")
        print("    Show              - Show wallet")
        print("    Add               - Show available wallet types")
        print("    Add type          - Add a wallet of type. Type is id or sitename")
        print("    Remove            - Removing a wallet")
        print("    Update            - Update a wallet, rename, disable/enable")
        print("Portfolio         - Open portfolio menu")
        print("    Show              - Show portfolio")
        print("    Filter            - Filter portfolio")
        print("    Graph             - Graph portfolio")
        print("    Export portfolio  - Export portfolio at date time")
        print("---------------------------------")
        print("Donations are welcome!")
        print("    ETH, POLYGON, BNB, PULSE:")
        print("        0xcF99cB3Be2F279D96B8ebF877aF22e05E58Db001")
        print("---------------------------------")

    def txns_show(self) -> None:
        print("---------------------------------")
        print("    Transactions")
        print("---------------------------------")
        df: DataFrame = self.control.get_txns()
        print(df)

    def wallets_show(self) -> None:
        print("---------------------------------")
        print("    Wallets")
        print("---------------------------------")
        df: DataFrame = self.control.get_wallets()
        print(df)

    def wallets_show_sitemodels(self) -> None:
        print("---------------------------------")
        print("    Available wallet types")
        print("---------------------------------")
        df: DataFrame = self.control.get_wallet_sitemodels()
        print(df)

    def wallets_add_check(self, cmd: Command, id_or_name: str) -> None:
        print("---------------------------------")
        print("    Add wallet check")
        print("---------------------------------", end="")
        id = 0
        if id_or_name.isdigit():
            id = int(id_or_name)
        else:
            id = self.control.get_sitemodel_id(id_or_name)

        if id > 0:
            if self.control.check_wallet_sitemodel_id_exists(id):
                self.wallets_add(id)
            else:
                print(f"\nUnknown id {cmd.arguments[0]!r}, try again.")
        else:
            print(f"\nUnknown argument {cmd.arguments[0]!r}, try again.")

    def wallets_add(self, id: int) -> None:
        print("\r    Add wallet                   ")
        print("---------------------------------")
        print(f"id: {id}")
        while True:
            cmd_addr = get_input_command("Wallet address: ", to_lowercase=False)
            match cmd_addr:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    cmd_name = get_input_command(
                        "Wallet name: ", default_answer="", to_lowercase=False
                    )
                    wallet_ok = self.control.add_wallet(
                        sitemodel=self.control.sitemodels[id],
                        address=cmd_addr.command,
                        name=cmd_name.command,
                    )
                    if wallet_ok:
                        print("New wallet is added")
                    else:
                        print("Error adding new wallet")
                    break

    def portfolio_show(self) -> None:
        print("---------------------------------")
        print("    Portfolio")
        print("---------------------------------")
