"""
@author: Arno
@created: 2023-09-15
@modified: 2023-10-20

TkInter GUI for ArkFolio

"""
import logging
from tkinter import BOTH, Button, Frame, Tk

from pandas import DataFrame
from pandastable import Table, TableModel

from src.ui.controllers.arkfoliocontroller import ArkfolioController

log = logging.getLogger(__name__)


class ArkfolioViewTk(Tk):
    """GUI TkInter class for ArkFolio"""

    def __init__(self) -> None:
        self.df: DataFrame

        super().__init__()
        self.title("Arkfolio")
        self.button_exit = Button(text="Quit")
        self.button_exit.bind("<Button-1>", self.handle_button_exit)
        self.button_exit.pack()
        self.button_txns = Button(text="Txns")
        self.button_txns.bind("<Button-1>", self.handle_button_txns)
        self.button_txns.pack()
        self.bind("<F1>", self.show_help)

        self.f = Frame(self.master)
        self.f.pack(fill=BOTH, expand=1)
        self.df = TableModel.getSampleData()
        self.table = Table(
            self.f, dataframe=self.df, showtoolbar=True, showstatusbar=True
        )
        self.table.show()

    def run(self, control: ArkfolioController) -> None:
        """Start the event loop."""
        self.control: ArkfolioController = control
        self.mainloop()

    def show_help(self, event) -> None:
        """Show help commands"""
        print("Help for Arkfolio TkInter GUI")

    def handle_button_exit(self, event):
        self.destroy()

    def handle_button_txns(self, event):
        dftxns: DataFrame = self.control.get_txns()
        self.df = dftxns
        self.table = Table(
            self.f, dataframe=self.df, showtoolbar=True, showstatusbar=True
        )
        self.table.show()
