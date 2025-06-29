import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import date

@st.cache_data
def load_data_from_csv(uploaded_file):
    """Charge les données depuis un fichier CSV uploadé."""
    if uploaded_file is None:
        return None
    try:
        df = pd.read_csv(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        # S'assurer que les colonnes OHLC sont présentes
        required_cols = {'Open', 'High', 'Low', 'Close'}
        if not required_cols.issubset(df.columns):
            st.error(f"Le fichier CSV doit contenir les colonnes : {', '.join(required_cols)}")
            return None
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

@st.cache_data
def download_data_from_yfinance(ticker, start_date, end_date):
    """Télécharge et prépare les données depuis Yahoo Finance."""
    try:
        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            return None

        # Aplatir les colonnes si elles sont en multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Supprimer les lignes avec des données manquantes
        df.dropna(inplace=True)
        
        # Revérifier si le dataframe est vide après suppression
        if df.empty:
            return None

        return df
    except Exception as e:
        # Log l'erreur côté serveur pour le débogage
        print(f"Erreur YFinance pour {ticker}: {e}")
        return None
