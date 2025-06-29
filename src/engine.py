import pandas as pd

def run_backtest(data: pd.DataFrame, strategy, **strategy_params):
    """
    Exécute le backtest d'une stratégie.
    Pour l'instant, une simulation très simple sans latence, slippage, etc.
    """
    # 1. Générer les signaux à partir de la stratégie
    strat_instance = strategy(**strategy_params)
    signals = strat_instance.generate_signals(data)

    # 2. Simuler le portefeuille
    initial_capital = 100000.0
    positions = pd.DataFrame(index=signals.index).fillna(0.0)
    portfolio = pd.DataFrame(index=data.index).fillna(0.0)

    # Joindre les signaux aux données de marché
    portfolio = data.join(signals, how='left').fillna(0)
    
    # Logique de trading simple : 1 unité par trade
    positions['position'] = portfolio['signal'].cumsum()
    
    portfolio['holdings'] = positions['position'] * portfolio['Close']
    portfolio['cash'] = initial_capital - (portfolio['signal'] * portfolio['Close']).cumsum()
    portfolio['total'] = portfolio['cash'] + portfolio['holdings']
    portfolio['returns'] = portfolio['total'].pct_change()

    # Isoler les trades exécutés pour la visualisation
    trades = signals[signals['signal'] != 0].copy()
    trades['price'] = data.loc[trades.index]['Close']
    trades['type'] = trades['signal'].apply(lambda x: 'BUY' if x > 0 else 'SELL')

    return portfolio, trades
