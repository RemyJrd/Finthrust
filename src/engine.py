import pandas as pd

def run_backtest(data, strategy_instance, initial_capital=100000):
    """
    Exécute le backtest d'une stratégie sur un ensemble de données.
    """
    # La stratégie est déjà une instance, pas besoin de la créer.

    # Générer les signaux
    signals = strategy_instance.generate_signals(data)

    # 2. Simuler le portefeuille
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    portfolio = pd.DataFrame(index=data.index).fillna(0.0)

    # Joindre les signaux aux données de marché de manière robuste
    # On utilise pd.merge sur la colonne 'Date' après avoir réinitialisé l'index
    # pour éviter les erreurs liées à des index incompatibles.
    left = data.reset_index()
    right = signals.reset_index()
    portfolio = pd.merge(left, right, on='Date', how='left')
    portfolio = portfolio.set_index('Date').fillna(0)
    
    # Logique de trading simple : 1 unité par trade
    positions['position'] = portfolio['signal'].cumsum()
    
    portfolio['holdings'] = positions['position'] * portfolio['Close']
    portfolio['cash'] = initial_capital - (portfolio['signal'] * portfolio['Close']).cumsum()
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()

    # Isoler les trades exécutés pour la visualisation
    trades = pd.DataFrame(columns=['Type', 'Price'])
    diff_positions = positions['position'].diff()
    
    for i in range(len(diff_positions)):
        if diff_positions.iloc[i] > 0: # Achat
            trades.loc[diff_positions.index[i]] = ['Buy', data['Close'].iloc[i]]
        elif diff_positions.iloc[i] < 0: # Vente
            trades.loc[diff_positions.index[i]] = ['Sell', data['Close'].iloc[i]]

    return portfolio, trades
