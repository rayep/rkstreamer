"""
Dependency Injection Modules
"""

from .models import ISongModel, ISongQueue
from .controllers import ISongController
from .views import ISongView
from .network import INetworkProvider, INetworkProviderResponse
from .patterns import Command
from .player import MusicPlayer, MusicPlayerControls

__all__ = [
    'ISongModel',
    'ISongQueue',
    'INetworkProvider',
    'INetworkProviderResponse',
    'ISongController',
    'ISongView',
    'Command',
    'MusicPlayer',
    'MusicPlayerControls']
