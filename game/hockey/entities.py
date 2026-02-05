"""
Entités du module Hockey.

Réexporte les classes depuis le module principal pour éviter la duplication.
"""

from game.models.entities import HockeyPlayer, Puck

__all__ = ["HockeyPlayer", "Puck"]
