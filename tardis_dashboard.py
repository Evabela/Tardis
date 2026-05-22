import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_dataset.csv", sep=";")

existing_departure_stations = df["Departure station"].unique()
existing_arrival_stations = df["Arrival station"].unique()

#Configuration of page
st.title("Analyses des données de la SNCF")
st.set_page_config("Analyses des données de la SNCF", page_icon=":bullettrain_side:", layout="wide",
                   menu_items={'About': "Welcome to our interactive dashboard which allows you to predict future delays on a train journey."})

#Load of prediction's model
@st.cache_resource
def load_model():
    return joblib.load("model.joblib")

model = load_model()

# Correlation between trains late at departure and their departure station
temp = df.groupby("Departure station").aggregate("sum").reset_index()
temp['Correlation late / nb of trains'] = 100 * temp['Number of cancelled trains'] / temp['Number of real trains']

tab1, tab2, tab3 = st.tabs(["Statistiques", "Graphiques", "Prédictions"])

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

def convert_minutes(mins):
    convert = {"hours": 0, "minutes": 0, "seconds": 0}
    convert["hours"] = int(mins // 60)
    convert["minutes"] = int(mins % 60)
    convert["seconds"] = int((mins % 1) * 60)
    return convert

with tab1:
    st.markdown("## Temps de trajet en fonction du service")
    st.markdown("Avec:\n- Nationaux : les trains reliant deux gares françaises\n- Internationaux : les trains reliant une gare française et une gare internationnale.")

    col1, col2 = st.columns(2)
    with col1:
        avg_nat = df[df["Service"] == "National"]["Average journey time"].mean()
        conv_nat = convert_minutes(avg_nat)
        st.markdown(f"#### Temps moyen de voyage au national: {str(conv_nat["hours"]) + "h" if conv_nat["hours"] != 0 else ""}{conv_nat["minutes"]} min")
    with col2:
        avg_inter = df[df["Service"] == "International"]["Average journey time"].mean()
        conv_inter = convert_minutes(avg_inter)
        st.markdown(f"#### Temps moyen de voyage à l'international: {str(conv_inter["hours"]) + "h" if conv_inter["hours"] != 0 else ""}{conv_inter["minutes"]} min")
    st.divider()

    st.markdown("## Trains prévus et retardés")
    st.markdown(f"#### Non-annulés: {100 * (1 - df["Number of cancelled trains"].sum() / df["Number of scheduled trains"].sum()):.2f} %")
    col1, col2 = st.columns(2)
    with col1:
        late = convert_minutes(df["Average delay of late trains at departure"].mean())
        st.markdown(f"#### Retard moyen au départ: {str(late["hours"]) + "h" if late["hours"] != 0 else ""}{late["minutes"]} min")
        delay = convert_minutes(df["Average delay of all trains at departure"].mean())
        st.markdown(f"#### Temps moyen au départ: {str(delay["hours"]) + "h" if delay["hours"] != 0 else ""}{delay["minutes"]} min")
    with col2:
        late = convert_minutes(df["Average delay of late trains at arrival"].mean())
        st.markdown(f"#### Retard moyen à l'arrivée: {str(late["hours"]) + "h" if late["hours"] != 0 else ""}{late["minutes"]} min")
        delay = convert_minutes(df["Average delay of all trains at arrival"].mean())
        st.markdown(f"#### Temps moyen à l'arrivée: {str(delay["hours"]) + "h" if delay["hours"] != 0 else ""}{delay["minutes"]} min")

with tab2:
    st.subheader("Pourcentage de trains en retard au départ par rapport à la station")
    st.bar_chart(temp, x="Departure station", y="Correlation late / nb of trains", height=400, x_label="Station de départ", y_label="Pourcentage")
    st.divider()
    st.subheader("Répartition des causes de retards")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        fig1, ax1 = plt.subplots(figsize=(8, 8))
        colors = plt.cm.Paired.colors
        ax1.pie(causes_means, labels=causes_means.index, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 10})
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1, use_container_width=False)

with tab3:
    st.text("Example")

def get_values_dataset(df: pd.DataFrame, start, stop, month):
    """
    We put the values needed by the model in a dict
    """
    values = {'season':"", 'nb trains': 0, 'journey time': 0.0, 'scheduled': 0, 'delayed': 0, 'prev month': 0.0}
    temp = df[(df["Departure station"] == start) & (df["Arrival station"] == stop)]

    #Get correct season
    if month in [12, 1, 2]:
        values["season"] = "Winter"
    elif month in [3, 4, 5]:
        values["season"] = "Spring"
    elif month in [6, 7, 8]:
        values["season"] = "Summer"
    else :
        values["season"] = "Autumn"
    values["nb trains"] = temp["Number of real trains"].mean()
    values["journey time"] = temp["Average journey time"].mean()
    values["scheduled"] = temp["Number of scheduled trains"].mean()
    values["delayed"] = temp["Number of trains delayed > 15min"].mean()
    values["prev month"] = temp["Delay previous month"].mean()
    return values

with st.sidebar:
    st.title("Prévisions des retards SNCF")
    st.selectbox("Station de départ", existing_departure_stations, key="departure_station", index=None, placeholder="Sélectionnez une station de départ")
    st.selectbox("Station d'arrivée", existing_arrival_stations, key="arrival_station", index=None, placeholder="Sélectionnez une station d'arrivée")
    st.date_input("Date de départ", key="departure_date", min_value="today", format="DD/MM/YYYY")
    st.selectbox("Type de Train", ["National", "International"], key="train_type", index=None, placeholder="Sélectionnez un type de train")

    if st.button("Afficher les prévisions de retards", type="primary") :
        if st.session_state.departure_station is None or st.session_state.arrival_station is None or st.session_state.departure_date is None or st.session_state.train_type is None:
            st.warning("Valeur.s manquante.s")
            st.stop()
        if st.session_state.departure_station == st.session_state.arrival_station:
            st.error("Les stations de départ et d'arrivée ne peuvent pas être les mêmes.")
            st.stop()
        try:
            journey_date = st.session_state.departure_date
            departure = st.session_state.departure_station
            arrival = st.session_state.arrival_station
            service = st.session_state.train_type
            values = get_values_dataset(df, departure, arrival, journey_date.month)
            donnees_entree = pd.DataFrame({
                'Year': [journey_date.year],
                'Month': [journey_date.month],
                'Service': [service],
                'Season': [values["season"]],
                'Departure station': [departure],
                'Arrival station': [arrival],
                'Number of real trains': [values["nb trains"]],
                'Average journey time': [values["journey time"]],
                'Number of scheduled trains': [values["scheduled"]],
                'Number of trains delayed > 15min': [values["delayed"]],
                'Delay previous month': [values["prev month"]]
            })
            retard_estime = max(0, model.predict(donnees_entree)[0])
            st.success(f"⏱️ Retard estimé : **{retard_estime:.0f} minutes**")
        except Exception as e:
            st.error("Erreur lors de la prédiction.")
            st.warning(f"Détail technique : {e}")