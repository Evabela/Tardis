import streamlit as st

st.title("Tardis Dashboard")
st.write("This is a dashboard for the Tardis project. It will be used to display the results of the model and the data analysis.")

st.text_input("Station de départ", key="departure_station")
st.text_input("Station d'arrivée", key="arrival_station")
st.date_input("Date de départ", key="departure_date")
st.text_input("Type de train (national/international)", key="train_type")