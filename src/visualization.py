import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_results(data, trades, portfolio):
    """Génère un graphique multi-panneaux avec les résultats du backtest."""
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2]
    )

    # 1. Graphique principal : Chandelier OHLC + Trades
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='OHLC'
    ), row=1, col=1)

    buy_trades = trades[trades['Type'] == 'Buy']
    sell_trades = trades[trades['Type'] == 'Sell']

    fig.add_trace(go.Scatter(
        x=buy_trades.index, y=buy_trades['Price'], mode='markers',
        marker=dict(color='cyan', size=10, symbol='triangle-up'),
        name='Achat'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=sell_trades.index, y=sell_trades['Price'], mode='markers',
        marker=dict(color='yellow', size=10, symbol='triangle-down'),
        name='Vente'
    ), row=1, col=1)

    # 2. Graphique du volume
    fig.add_trace(go.Bar(
        x=data.index,
        y=data.get('Volume', pd.Series(0, index=data.index)), # Gestion du cas où Volume n'existe pas
        name='Volume',
        marker_color='lightblue'
    ), row=2, col=1)

    # 3. Courbe de performance du portefeuille (Equity Curve)
    fig.add_trace(go.Scatter(
        x=portfolio.index,
        y=portfolio['total'],
        name='Valeur du Portefeuille',
        line=dict(color='lime', width=2)
    ), row=3, col=1)

    # Mise en forme du layout
    fig.update_layout(
        title_text='Analyse Complète du Backtest',
        height=800,
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Mise en forme des axes
    fig.update_yaxes(title_text="Prix", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    # Ajuster l'axe pour mieux voir les variations de la valeur du portefeuille
    fig.update_yaxes(title_text="Valeur Portefeuille", rangemode='normal', row=3, col=1)
    fig.update_xaxes(title_text="Date", row=3, col=1)
    
    return fig
