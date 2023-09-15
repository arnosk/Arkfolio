"""
@author: Arno
@created: 2023-05-16
@modified: 2023-05-20

Command editor UI for ArkFolio

"""
import logging
import shlex
import sys

from src.ui.views.viewclihelper import Command, get_input_command

log = logging.getLogger(__name__)


class ArkfolioViewCli:
    """UI class for ArkFolio in command editor"""

    def __init__(self) -> None:
        pass

    def show_help(self) -> None:
        """Show the available cli commands"""
        print("Help for Arkfolio CLI UI")

    def run(self) -> None:
        """CLI UI main program:"""
        print(f"Arkfolio CLI UI")
        while True:
            cmd = get_input_command()
            match cmd:
                case Command(command="quit" | "q" | "exit" | "e"):
                    sys.exit("Exiting")
                case Command(command="help" | "h"):
                    self.show_help()
                case _:
                    print(f"Unknown command {cmd.command!r}, try again.")
