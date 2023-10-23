"""
@author: Arno
@created: 2023-09-15
@modified: 2023-10-23

View CLI UI helper
"""
import logging
import shlex
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class Command:
    """Class that represents a command for CLI view"""

    command: str
    arguments: list[str]

    def __post_init__(self):
        self.command = self.command.lower()
        self.arguments = [x.lower() for x in self.arguments]


def get_input_command(message: str = "> ", default_answer: str = "help") -> Command:
    """User input"""
    print()
    input_str = input(message)
    if input_str == "":
        input_str = default_answer
    command, *arguments = shlex.split(input_str)
    return Command(command, arguments)
