# Project Tardis
- `13/04/2026 - 22/05/2026`
- Epitech Promo 2030
- G2 - Data Analysis
## 👤 Contributors :
- Eva Belanger : eva.belanger@epitech.eu 
- Loup Souche : loup.souche@epitech.eu
- Lukas Pouezevara : lukas.pouezevara@epitech.eu
## 🗒️ Norm : 
- Commit norm : < action > (file - function) : comment
- Example : `<add> (README.md) : add the file readme.md in the repo`
## 📑 Description
The Tardis project involves creating a predictive model for train delays, after cleaning a CSV file. Our goal is to Analyze historical train delay data, uncover hidden patterns, and develop a predictive model that can forecast delays before they happen.

Key features implemented:
- Data Cleaning & Preprocessing – Handle missing values, inconsistencies, and prepare the dataset for analysis.
- Exploratory Data Analysis (EDA) – Generate insightful visualizations to understand trends and correlations.
- Predictive Modeling – Implement a basic machine learning model to predict train delays.
- Dashboard Development – Create an interactive web app using Streamlit to display insights and allow user interaction.

## How to use (on ubuntu)
1. Make sure that jupyter-lab, pip and venv are installed on your laptop.
2. Launch the cleaning with `tardis_eda.ipynb` file on jupyter-lab.
3. Launch the model with `tadis_model.ipynb` file on jupyter-lab.
4. Export the model to file named `model.joblib`
5. Launch the dashboard in a venv, with this command : `streamlit run tardis_dashboard.py`.

## Files on repository
- `requirements.txt` : All project dependencies
- `tardis_eda.ipynb` : Data cleaning, exploration, and feature engineering
- `cleaned_dataset.csv` : Processed dataset output from EDA notebook
- `tardis_model.ipynb` : Model training, evaluation, and selection
- `model.pkl` or `model.joblib` : Trained model file
- `tardis_dashboard.py` : Interactive Streamlit dashboard
