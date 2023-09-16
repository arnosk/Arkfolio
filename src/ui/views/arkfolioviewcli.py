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
        print("Transactions      - Show txns")
        print("Filter txns       - Filter txns on site, address, start date, end data")
        print("Add wallet        - Adding a wallet")
        print("Remove wallet     - Removing a wallet")
        print("Update wallet     - Update a wallet, rename, disable/enable")
        print("Portfolio         - Show portfolio")
        print("Graph             - Show graph portfolio")
        print("Export txns       - Export txns, according to selected filter")
        print("Export Portfolio  - Export portfolio at date time")

    def run(self) -> None:
        """CLI UI main program:"""
        print(f"Arkfolio main")
        print(f"-------------")
        while True:
            cmd = get_input_command()
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    sys.exit("Exiting")
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")
