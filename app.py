import streamlit as st
import pandas as pd
import os
import importlib
from datetime import date, timedelta

# Import local modules
from src.data_loader import download_data_from_yfinance
from src.engine import run_backtest
from src.performance import calculate_performance_metrics
from src.visualization import plot_results
from src.strategies.base import Strategy

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Finthrust Backtesting")

# --- Utility Functions ---
@st.cache_data
def find_strategies():
    """Trouve dynamiquement les classes de stratégie dans le dossier strategies."""
    strategy_files = [f for f in os.listdir('src/strategies') if f.endswith('.py') and f != '__init__.py' and f != 'base.py']
    strategies = {}
    for file in strategy_files:
        module_name = f"src.strategies.{file[:-3]}"
        module = importlib.import_module(module_name)
        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)
            if isinstance(attribute, type) and issubclass(attribute, Strategy) and attribute is not Strategy:
                readable_name = ' '.join(word.capitalize() for word in attribute.__name__.replace('_', ' ').split(' '))
                strategies[readable_name] = attribute
    return strategies

# --- Main UI ---
st.title("📈 Finthrust - Terminal de Backtesting")
st.markdown("Créez un portefeuille, sélectionnez une stratégie et analysez les résultats de vos backtests.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")

    # --- Portfolio Management ---
    st.subheader("1. Gestion du Portefeuille")
    if 'portfolio_assets' not in st.session_state:
        st.session_state.portfolio_assets = []

    with st.form(key='add_asset_form', clear_on_submit=True):
        ticker_input = st.text_input("Ticker (ex: AAPL, BTC-USD)")
        add_button = st.form_submit_button("Ajouter au portefeuille")
        if add_button and ticker_input:
            if not any(d['Ticker'] == ticker_input.upper() for d in st.session_state.portfolio_assets):
                st.session_state.portfolio_assets.append({'Ticker': ticker_input.upper()})
            else:
                st.warning(f"{ticker_input.upper()} est déjà présent.")

    if st.session_state.portfolio_assets:
        st.write("Actifs actuels :")
        for i, asset in enumerate(st.session_state.portfolio_assets):
            col1, col2 = st.columns([4, 1])
            col1.info(asset['Ticker'])
            if col2.button("🗑️", key=f"del_{i}"):
                st.session_state.portfolio_assets.pop(i)
                st.experimental_rerun()

    # --- Strategy Selection ---
    st.subheader("2. Sélection de la Stratégie")
    available_strategies = find_strategies()
    strategy_name = st.selectbox("Choisissez une stratégie", options=list(available_strategies.keys()))
    StrategyClass = available_strategies.get(strategy_name)

    params = {}
    if StrategyClass and hasattr(StrategyClass, 'params'):
        for p_name, p_value in StrategyClass.params.items():
            params[p_name] = st.number_input(f"{p_name.replace('_', ' ').title()}", value=p_value)

    # --- Backtest Controls ---
    st.subheader("3. Paramètres du Backtest")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date de début", pd.to_datetime('2023-01-01'))
    with col2:
        end_date = st.date_input("Date de fin", pd.to_datetime('today'))

    run_button = st.button("Lancer le Backtest", type="primary", use_container_width=True)

# --- Main Panel (Results) ---
if run_button:
    data = None
    if not st.session_state.portfolio_assets:
        st.error("❌ Erreur : Veuillez ajouter au moins un actif à votre portefeuille.")
    elif not StrategyClass:
        st.error("❌ Erreur : Veuillez sélectionner une stratégie valide.")
    elif start_date >= end_date:
        st.error("❌ Erreur : La date de début doit être antérieure à la date de fin.")
    else:
        # Le backtest est lancé sur le premier actif du portefeuille
        ticker_to_backtest = st.session_state.portfolio_assets[0]['Ticker']
        
        # Gérer l'affichage du statut ici, en dehors de la fonction cachée
        status_placeholder = st.sidebar.empty()
        status_placeholder.info(f"⏳ Téléchargement pour {ticker_to_backtest}...")
        
        data = download_data_from_yfinance(ticker_to_backtest, start_date, end_date)

        if data is not None and not data.empty:
            status_placeholder.success("✅ Données prêtes !")
            with st.spinner(f"Exécution du backtest pour {ticker_to_backtest}..."):
                selected_strategy = StrategyClass(**params)
                portfolio, trades = run_backtest(data, strategy_instance=selected_strategy)

                metrics = calculate_performance_metrics(portfolio, trades)
                fig = plot_results(data, trades, portfolio)

            st.subheader("📈 Métriques de Performance Clés")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rendement Total", f"{metrics.get('Rendement Total', 0):.2f}%")
            col2.metric("Valeur Finale", f"{metrics.get('Valeur Finale du Portefeuille', 0):,.2f}")
            col3.metric("Ratio de Sharpe", f"{metrics.get('Ratio de Sharpe', 0):.2f}")
            col4.metric("Total des Trades", f"{metrics.get('Nombre Total de Trades', 0)}")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Rendement Annuel", f"{metrics.get('Rendement Annuel', 0):.2f}%")
            col2.metric("Volatilité Annuelle", f"{metrics.get('Volatilité Annuelle', 0):.2f}%")
            col3.metric("Max Drawdown", f"{metrics.get('Max Drawdown', 0):.2f}%")
            
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Voir les données détaillées du portefeuille"):
                st.dataframe(portfolio, use_container_width=True)
        else:
            error_message = (
                f"❌ Données non trouvées pour {ticker_to_backtest}.\n\n"
                "**Causes possibles :**\n"
                "1. Le ticker est incorrect ou n'existe pas.\n"
                "2. Aucune donnée pour la période sélectionnée.\n"
                "3. Yahoo Finance a temporairement limité l'accès (trop de requêtes). Veuillez patienter quelques minutes."
            )
            status_placeholder.error(error_message)
else:
    st.info("Configurez votre portefeuille et votre stratégie, puis lancez le backtest.")
