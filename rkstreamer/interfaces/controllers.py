"""
DI module for Controllers
"""

from typing import Union
from ._interface import ABC, abstractmethod


class ISongController(ABC):
    """Interface for Song controller"""

    @abstractmethod
    def handle_input(self, user_input: Union[str,int]) -> None:
        """Process user input"""
