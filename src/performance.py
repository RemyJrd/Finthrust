import pandas as pd
import numpy as np

def calculate_performance_metrics(portfolio: pd.DataFrame):
    """Calcule les métriques de performance clés."""
    if portfolio.empty:
        return pd.DataFrame()

    total_return = (portfolio['total'][-1] / portfolio['total'][0]) - 1
    
    # Max Drawdown
    rolling_max = portfolio['total'].cummax()
    daily_drawdown = portfolio['total'] / rolling_max - 1.0
    max_drawdown = daily_drawdown.min()

    # Sharpe Ratio (annualisé, en supposant des données quotidiennes)
    sharpe_ratio = (portfolio['returns'].mean() / portfolio['returns'].std()) * np.sqrt(252) if portfolio['returns'].std() != 0 else 0

    metrics = {
        'Rendement Total': f"{total_return:.2%}",
        'Max Drawdown': f"{max_drawdown:.2%}",
        'Ratio de Sharpe': f"{sharpe_ratio:.2f}",
    }

    return pd.DataFrame.from_dict(metrics, orient='index', columns=['Valeur'])
