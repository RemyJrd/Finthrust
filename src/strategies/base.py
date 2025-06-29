from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """Classe de base abstraite pour les stratégies de trading."""

    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Génère des signaux de trading basés sur les données d'entrée.

        Args:
            data (pd.DataFrame): Données OHLCV.

        Returns:
            pd.DataFrame: Un DataFrame avec une colonne 'signal' (1 pour achat, -1 for vente, 0 pour neutre).
        """
        pass
