"""
@author: Arno
@created: 2023-09-15
@modified: 2023-09-15

TkInter GUI for ArkFolio

"""
import logging
from tkinter import Button, Tk

log = logging.getLogger(__name__)


class ArkfolioViewTk(Tk):
    """GUI TkInter class for ArkFolio"""

    def __init__(self) -> None:
        super().__init__()
        self.title("Arkfolio")
        self.button = Button(text="Show help")
        self.button.bind("<Button-1>", self.handle_button_press)
        self.button.pack()

    def run(self) -> None:
        """Start the event loop."""
        self.mainloop()

    def show_help(self) -> None:
        """Show help commands"""
        print("Test")

    def handle_button_press(self, event):
        self.destroy()
