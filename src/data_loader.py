import pandas as pd
import streamlit as st

@st.cache_data
def load_data(uploaded_file):
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
