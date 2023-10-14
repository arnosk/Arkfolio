"""
@author: Arno
@created: 2023-09-15
@modified: 2023-10-14

TkInter GUI for ArkFolio

"""
import logging
from tkinter import Button, Tk

from src.ui.controllers.arkfoliocontroller import ArkfolioController

log = logging.getLogger(__name__)


class ArkfolioViewTk(Tk):
    """GUI TkInter class for ArkFolio"""

    def __init__(self) -> None:
        super().__init__()
        self.title("Arkfolio")
        self.button = Button(text="Quit")
        self.button.bind("<Button-1>", self.handle_button_press)
        self.button.pack()
        self.bind("<F1>", self.show_help)

    def run(self, control: ArkfolioController) -> None:
        """Start the event loop."""
        self.mainloop()

    def show_help(self, event) -> None:
        """Show help commands"""
        print("Help for Arkfolio TkInter GUI")

    def handle_button_press(self, event):
        self.destroy()
