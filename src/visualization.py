import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_results(data, trades):
    """Crée un graphique Plotly avec les résultats du backtest."""
    fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.1)

    # 1. Graphique en chandelier
    fig.add_trace(go.Candlestick(x=data.index,
                               open=data['Open'],
                               high=data['High'],
                               low=data['Low'],
                               close=data['Close'],
                               name='OHLC'), row=1, col=1)

    # 2. Visualisation des ordres
    buy_trades = trades[trades['signal'] > 0]
    sell_trades = trades[trades['signal'] < 0]

    fig.add_trace(go.Scatter(x=buy_trades.index, y=buy_trades['price'],
                             mode='markers', name='Achat',
                             marker=dict(color='green', size=10, symbol='triangle-up')),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=sell_trades.index, y=sell_trades['price'],
                             mode='markers', name='Vente',
                             marker=dict(color='red', size=10, symbol='triangle-down')),
                  row=1, col=1)

    fig.update_layout(
        title='Résultats du Backtest',
        yaxis_title='Prix',
        xaxis_title='Date',
        height=600,
        template='plotly_dark',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(rangeslider_visible=False)

    return fig
