import pandas as pd
import numpy as np
from .base import Strategy

class MovingAverageCross(Strategy):
    """Stratégie simple basée sur le croisement de deux moyennes mobiles."""

    def __init__(self, short_window=20, long_window=50):
        super().__init__(short_window=short_window, long_window=long_window)
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Génère des signaux basés sur le croisement des moyennes mobiles."""
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0

        # Calcul des moyennes mobiles
        signals['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1, center=False).mean()

        # Création des signaux
        # Lorsque la moyenne mobile courte passe au-dessus de la longue -> Achat (1)
        signals['signal'][self.short_window:] = \
            np.where(signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:], 1.0, 0.0)

        # Génération des ordres : différence de signaux pour ne prendre que les changements
        signals['positions'] = signals['signal'].diff()

        # On ne garde que les signaux d'achat (1) et de vente (-1)
        signals = signals[signals['positions'] != 0]
        signals['signal'] = signals['positions']
        
        return signals[['signal']]
