"""
@author: Arno
@created: 2023-05-16
@modified: 2023-10-14

Command editor UI for ArkFolio

"""
import logging
import sys

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
                    self.show_txns()
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
                    self.show_wallets()
                case Command(command="add" | "a"):
                    self.show_help()
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
                    self.show_portfolio()
                case Command(command="graph" | "g"):
                    self.show_help()
                case Command(command="filter" | "f"):
                    self.show_help()
                case Command(command="export" | "e"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def show_help(self) -> None:
        """Show the available cli commands"""
        print("---------------------------------")
        print("    Help for Arkfolio CLI UI")
        print("---------------------------------")
        print("Quit/Exit         - Quits program or back to previous menu")
        print("Help              - This help message")
        print("Transactions      - Open txns menu")
        print("    Show txns         - Show txns")
        print("    Filter txns       - Filter txns on site, address, start, end data")
        print("    Export txns       - Export txns, according to selected filter")
        print("Wallet            - Open wallet menu")
        print("    Show wallets      - Show wallet")
        print("    Add wallet        - Adding a wallet")
        print("    Remove wallet     - Removing a wallet")
        print("    Update wallet     - Update a wallet, rename, disable/enable")
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

    def show_txns(self) -> None:
        """Show transactions"""
        print("---------------------------------")
        print("    Transactions")
        print("---------------------------------")

    def show_wallets(self) -> None:
        """Show wallets"""
        print("---------------------------------")
        print("    Wallets")
        print("---------------------------------")

    def show_portfolio(self) -> None:
        """Show portfolio"""
        print("---------------------------------")
        print("    Portfolio")
        print("---------------------------------")
