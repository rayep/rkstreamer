"""
DI module for Views
"""

from ._interface import ABC, abstractmethod


class IView(ABC):
    """Interface for Song View"""

    @abstractmethod
    def display(self, entity):
        """Displays the entity"""

    @abstractmethod
    def display_selected(self, entity):
        """Displays the entity"""


class ISongView(IView):
    """Interface for Song View"""

    @abstractmethod
    def display_queue(self, queue):
        """Displays the queue"""
    
    @abstractmethod
    def display_rsongs_queue(self, queue):
        """Displays the related songs queue"""

    @abstractmethod
    def play_media(self, media) -> None:
        """Play the given media"""

    @abstractmethod
    def remove_media(self, media) -> None:
        """Play the given media"""

    @abstractmethod
    def add_media(self, media) -> None:
        """Play the given media"""

    @abstractmethod
    def player_input(self, user_input: str):
        """Input to music player"""

    @abstractmethod
    def set_controller_callback(self, callback_fn):
        """Updates the callback attribute to mlplayer's monitor state"""
