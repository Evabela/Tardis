import streamlit as st
import pandas as pd

df = pd.read_csv("cleaned_dataset.csv", sep=";")

existing_departure_stations = df["Departure station"].unique()
existing_arrival_stations = df["Arrival station"].unique()

st.title("Analyses des données de la SNCF")

# Chart of the evolution of the number of real trains over the years
data = df.groupby("Year")["Number of real trains"].sum().reset_index()
data["Year"] = data["Year"].astype(str)

tab1 = st.tabs(["Évolution du nombre de trains réels au fil des années"])[0]
tab1.line_chart(data.set_index("Year")["Number of real trains"], height=400)

#Pie chart of the cause of delays

#Chercher des graphique à afficher dans la partie principale du dashboard


with st.sidebar:
    st.title("Prévisions des retards SNCF")
    st.selectbox("Station de départ", existing_departure_stations, key="departure_station", index=None, placeholder="Sélectionnez une station de départ")
    st.selectbox("Station d'arrivée", existing_arrival_stations, key="arrival_station", index=None, placeholder="Sélectionnez une station d'arrivée")
    st.date_input("Date de départ", key="departure_date")
    st.selectbox("Type de Train", ["National", "International"], key="train_type", index=None, placeholder="Sélectionnez un type de train")

    if st.button("Afficher les prévisions de retards", type="primary") and st.session_state.departure_station is not None and st.session_state.arrival_station is not None and st.session_state.departure_date is not None and st.session_state.train_type is not None:
        st.write("Utiliser le modèle ici")