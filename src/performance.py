import pandas as pd
import numpy as np

def calculate_performance_metrics(portfolio, trades):
    """Calcule un ensemble détaillé de métriques de performance."""
    
    metrics = {}
    
    # Valeurs de base
    initial_value = portfolio['total'].iloc[0]
    final_value = portfolio['total'].iloc[-1]
    
    # Rendement
    total_return = (final_value / initial_value - 1)
    metrics['Rendement Total'] = total_return * 100
    metrics['Valeur Finale du Portefeuille'] = final_value
    
    # Période
    days = (portfolio.index[-1] - portfolio.index[0]).days
    if days > 0:
        # Utilisation de 365.25 pour une meilleure précision sur les années bissextiles
        annual_return = (1 + total_return) ** (365.25 / days) - 1
    else:
        annual_return = 0
    metrics['Rendement Annuel'] = annual_return * 100

    # Volatilité et Sharpe
    daily_returns = portfolio['total'].pct_change().dropna()
    if not daily_returns.empty and daily_returns.std() != 0:
        annual_volatility = daily_returns.std() * np.sqrt(252)
        # Le Sharpe Ratio utilise le rendement annualisé pour être cohérent
        sharpe_ratio = (annual_return) / annual_volatility if annual_volatility != 0 else 0
    else:
        annual_volatility = 0
        sharpe_ratio = 0
        
    metrics['Volatilité Annuelle'] = annual_volatility * 100
    metrics['Ratio de Sharpe'] = sharpe_ratio

    # Max Drawdown
    cumulative_returns = portfolio['total'] / initial_value
    peak = cumulative_returns.expanding(min_periods=1).max()
    drawdown = (cumulative_returns / peak - 1)
    metrics['Max Drawdown'] = drawdown.min() * 100
    
    # Trades
    metrics['Nombre Total de Trades'] = len(trades)
    
    return metrics
