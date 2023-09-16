"""
@author: Arno
@created: 2023-05-16
@modified: 2023-05-20

Command editor UI for ArkFolio

"""
import logging
import sys

from src.ui.views.viewclihelper import Command, get_input_command

log = logging.getLogger(__name__)


class ArkfolioViewCli:
    """UI CLI class for ArkFolio"""

    def __init__(self) -> None:
        pass

    def show_help(self) -> None:
        """Show the available cli commands"""
        print("    Help for Arkfolio CLI UI")
        print("---------------------------------")
        print("Quit/Exit         - Quits program")
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
        print("    Filter            - Show portfolio")
        print("    Graph             - Show graph portfolio")
        print("    Export portfolio  - Export portfolio at date time")

    def run(self) -> None:
        """CLI UI main program:"""
        print(f"Arkfolio main")
        print(f"-------------")
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
        print(f"Arkfolio Transactions")
        print(f"---------------------")
        while True:
            cmd = get_input_command("Transaction> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def menu_wallet(self) -> None:
        """CLI UI wallets"""
        print(f"Arkfolio Wallets")
        print(f"---------------------")
        while True:
            cmd = get_input_command("Wallet> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")

    def menu_portfolio(self) -> None:
        """CLI UI portfolio"""
        print(f"Arkfolio Portfolio")
        print(f"---------------------")
        while True:
            cmd = get_input_command("Portfolio> ")
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    break
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")
