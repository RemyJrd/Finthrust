# Finthrust - Terminal de Backtesting de Stratégies

Ce projet est une application web pour visualiser et backtester des stratégies de trading sur des actifs financiers.

## 🎯 Objectif

Visualiser le comportement de stratégies de trading avancées sur des actifs volatils, en intégrant des indicateurs personnalisés et un modèle de remplissage réaliste des ordres (slippage, spread, latence, etc.).

## 🚀 Installation et Lancement

1.  **Clonez le projet :**
    ```bash
    git clone <votre-repo>
    cd Finthrust
    ```

2.  **Créez un environnement virtuel et installez les dépendances :**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Lancez l'application Streamlit :**
    ```bash
    streamlit run app.py
    ```

L'application devrait s'ouvrir dans votre navigateur à l'adresse `http://localhost:8501`.

## 📂 Structure du Projet

-   `app.py`: Interface utilisateur (Streamlit).
-   `requirements.txt`: Dépendances Python.
-   `src/`: Logique du backend.
    -   `data_loader.py`: Chargement des données.
    -   `engine.py`: Moteur de backtesting.
    -   `performance.py`: Calcul des métriques.
    -   `visualization.py`: Création des graphiques.
    -   `strategies/`: Contient les stratégies de trading.
-   `data/`: Données d'exemple.
