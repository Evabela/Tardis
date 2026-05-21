import streamlit as st
import pandas as pd

df = pd.read_csv("cleaned_dataset.csv", sep=";")

existing_departure_stations = df["Departure station"].unique()
existing_arrival_stations = df["Arrival station"].unique()

st.title("Analyses des données de la SNCF")

# Chart of the evolution of the number of real trains over the years
data = df.groupby("Year")["Number of real trains"].sum().reset_index()
data["Year"] = data["Year"].astype(str)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Évolution du nombre de trains réels")
    st.line_chart(data.set_index("Year")["Number of real trains"], height=400)

# Pie chart of the cause of delays
causes_cols = [
    "Pct delay due to external causes",
    "Pct delay due to infrastructure",
    "Pct delay due to traffic management",
    "Pct delay due to rolling stock",
    "Pct delay due to station management and equipment reuse",
    "Pct delay due to passenger handling"
]
causes_means = df[causes_cols].mean()

# Rename the index
causes_means.index = [
    "Causes externes",
    "Infrastructure",
    "Gestion du trafic",
    "Matériel roulant",
    "Gestion en gare",
    "Prise en charge voyageurs"
]

with col2:
    st.subheader("Répartition des causes de retards")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Paired.colors
    ax.pie(causes_means, labels=causes_means.index, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 10})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)



with st.sidebar:
    st.title("Prévisions des retards SNCF")
    st.selectbox("Station de départ", existing_departure_stations, key="departure_station", index=None, placeholder="Sélectionnez une station de départ")
    st.selectbox("Station d'arrivée", existing_arrival_stations, key="arrival_station", index=None, placeholder="Sélectionnez une station d'arrivée")
    st.date_input("Date de départ", key="departure_date")
    st.selectbox("Type de Train", ["National", "International"], key="train_type", index=None, placeholder="Sélectionnez un type de train")

    if st.button("Afficher les prévisions de retards", type="primary") and st.session_state.departure_station is not None and st.session_state.arrival_station is not None and st.session_state.departure_date is not None and st.session_state.train_type is not None:
        st.write("Utiliser le modèle ici")