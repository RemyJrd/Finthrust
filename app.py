import streamlit as st
import pandas as pd
import os
import importlib

from src.data_loader import load_data
from src.engine import run_backtest
from src.performance import calculate_performance_metrics
from src.visualization import plot_results
from src.strategies.base import Strategy

st.set_page_config(layout="wide", page_title="Finthrust Backtesting")

# --- Fonctions Utilitaires ---
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
                # Utiliser un nom lisible pour l'affichage
                readable_name = ' '.join(word.capitalize() for word in attribute.__name__.replace('_', ' ').split(' '))
                strategies[readable_name] = attribute
    return strategies

# --- Interface Utilisateur ---
st.title("📈 Finthrust - Terminal de Backtesting")
st.markdown("Visualisez et analysez vos stratégies de trading.")

# --- Barre Latérale (Contrôles) ---
with st.sidebar:
    st.header("⚙️ Paramètres")

    # 1. Upload de données
    uploaded_file = st.file_uploader("Chargez vos données (CSV)", type="csv")
    st.info("Le CSV doit contenir les colonnes: `Date`, `Open`, `High`, `Low`, `Close`.")

    # 2. Choix de la stratégie
    available_strategies = find_strategies()
    strategy_name = st.selectbox("Choisissez une stratégie", options=list(available_strategies.keys()))
    selected_strategy = available_strategies.get(strategy_name)

    # 3. Paramètres de la stratégie (dynamique)
    params = {}
    if selected_strategy:
        # Exemple simple, à rendre plus robuste
        if strategy_name == 'Moving Average Cross':
            params['short_window'] = st.slider("Fenêtre courte (jours)", 5, 50, 20)
            params['long_window'] = st.slider("Fenêtre longue (jours)", 20, 200, 50)
    
    # 4. Paramètres de simulation (futur)
    st.subheader("Modèle d'exécution")
    latency = st.number_input("Latence (ms)", value=0, disabled=True)
    slippage = st.number_input("Slippage (%)", value=0.0, disabled=True)

    # Bouton de lancement
    run_button = st.button("Lancer le Backtest", type="primary", use_container_width=True)

# --- Zone Principale (Résultats) ---
data = load_data(uploaded_file)

if run_button and data is not None and selected_strategy:
    with st.spinner('Calcul en cours...'):
        # Exécution du backtest
        portfolio, trades = run_backtest(data, selected_strategy, **params)

        # Calcul des performances
        performance_metrics = calculate_performance_metrics(portfolio)

        # Génération du graphique
        fig = plot_results(data, trades)

    st.subheader("📊 Résultats du Backtest")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tableau de Performance")
    st.dataframe(performance_metrics, use_container_width=True)

    with st.expander("Voir les données du portefeuille"):
        st.dataframe(portfolio, use_container_width=True)

elif run_button:
    st.warning("Veuillez charger un fichier de données pour commencer.")
else:
    st.info("Configurez votre backtest dans la barre latérale et cliquez sur 'Lancer'.")
