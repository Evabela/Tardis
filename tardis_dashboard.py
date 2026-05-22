import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt

df = pd.read_csv("cleaned_dataset.csv", sep=";")

existing_departure_stations = df["Departure station"].unique()
existing_arrival_stations = df["Arrival station"].unique()

#Configuration of page
st.title("🚉 Analyses des données de la SNCF")
st.set_page_config("Tardis | Prévoir les retards SNCF", page_icon=":bullettrain_side:", layout="wide",
                   menu_items={'About': "Bienvenue sur notre tableau de bord interactif qui vous permet de prévoir les retards futurs sur un trajet en train."})

#Load of prediction's model
@st.cache_resource
def load_model():
    return joblib.load("model.joblib")

model = load_model()


# Custom CSS for a better look
st.markdown(
    """
    <style>
    /* Adjusting metrics for theme compatibility */
    [data-testid="stMetric"] {
        background-color: rgba(9, 38, 74, 0.3);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(151, 166, 195, 0.2);
    }
    .prediction-box {
        background-color: rgba(2, 136, 209, 0.1);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #0288d1;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

result, stats, graphs, model_stats = st.tabs(["🔮 Résultat prédiction", "📊 Statistiques", "📈 Graphiques", "🖥️ Modèle de prédiction"])

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

def convert_minutes(mins):
    convert = {"hours": 0, "minutes": 0, "seconds": 0}
    convert["hours"] = int(mins // 60)
    convert["minutes"] = int(mins % 60)
    convert["seconds"] = int((mins % 1) * 60)
    return convert

st.session_state.save_values = None

def print_city(df, name):
    """
    Print statistics on the selected city
    """
    start = df[df["Departure station"] == name]
    end = df[df["Arrival station"] == name]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre de trains passant par cette station", f"{df["Number of real trains"].mean():.0f}")
        pct_cancel = 100 * start["Number of cancelled trains"] / start["Number of scheduled trains"]
        st.metric("Pourcentage de trains annulés", f"{pct_cancel.mean():.2f} %")
    with col2:
        pct_late = 100 * end["Number of trains delayed at departure"] / end["Number of real trains"]
        st.metric("Pourcentage de trains en retard au départ", f"{pct_late.mean():.2f} %")
        pct_late = 100 * end["Number of trains delayed at arrival"] / end["Number of real trains"]
        st.metric("Pourcentage de trains en retard à l'arrivée", f"{pct_late.mean():.2f} %")
    with col3:
        av_late = convert_minutes(start["Average delay of late trains at departure"].mean())
        st.metric("Moyenne des retards au départ", f"{str(av_late["hours"]) + "h" if av_late["hours"] != 0 else ""}{av_late["minutes"]} min")
        av_late = convert_minutes(start["Average delay of late trains at arrival"].mean())
        st.metric("Moyenne des retards à l'arrivée", f"{str(av_late["hours"]) + "h" if av_late["hours"] != 0 else ""}{av_late["minutes"]} min")
    
    #Graphic for city in function of year selected
    st.subheader("Évolution au fil des années")
    year = st.radio("Sélectionnez une année", sorted(df["Year"].unique()), horizontal=True)
    start_year = start[start["Year"] == year].groupby("Month")["Average delay of late trains at departure"].mean()
    end_year = end[end["Year"] == year].groupby("Month")["Average delay of late trains at arrival"].mean()
    chart_data = pd.DataFrame({"Retard au départ": start_year, "Retard à l'arrivée": end_year}).interpolate().fillna(0)
    st.line_chart(chart_data, x_label="Mois de janvier à décembre", y_label="Nombre moyen de trains en retard")    

# Statistics from dataset
with stats:
    st.markdown("## Temps de trajet en fonction du service")
    st.markdown("Avec :\n- Nationaux : les trains reliant deux gares françaises\n- Internationaux : les trains reliant une gare française et une gare internationnale.")

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
        st.markdown(f"#### Retards moyen au départ: {str(late["hours"]) + "h" if late["hours"] != 0 else ""}{late["minutes"]} min")
        delay = convert_minutes(df["Average delay of all trains at departure"].mean())
        st.markdown(f"#### Temps moyen au départ: {str(delay["hours"]) + "h" if delay["hours"] != 0 else ""}{delay["minutes"]} min")
    with col2:
        late = convert_minutes(df["Average delay of late trains at arrival"].mean())
        st.markdown(f"#### Retards moyen à l'arrivée: {str(late["hours"]) + "h" if late["hours"] != 0 else ""}{late["minutes"]} min")
        delay = convert_minutes(df["Average delay of all trains at arrival"].mean())
        st.markdown(f"#### Temps moyen à l'arrivée: {str(delay["hours"]) + "h" if delay["hours"] != 0 else ""}{delay["minutes"]} min")
    st.divider()

    st.markdown("## Statistiques par stations")
    list_cities = df["Departure station"].unique()
    station = st.selectbox("Sélectionner une station pour voir ses informations", list_cities, placeholder="Sélectionnez une station")
    if station:
        print_city(df, station)

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

# Correlation between trains late at departure and their departure station
temp = df.groupby("Departure station").aggregate("sum").reset_index()
temp['Correlation late / nb of trains'] = 100 * temp['Number of cancelled trains'] / temp['Number of real trains']
temp = temp.sort_values("Correlation late / nb of trains", ascending=False).head(10)

with graphs:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Pourcentage de trains en retard au départ par rapport à la station")
        st.bar_chart(temp, x="Departure station", y="Correlation late / nb of trains", height=400, x_label="Station de départ", y_label="Pourcentage", color="#3C62BD")
    with col2:
        st.subheader("Répartition des causes de retards")
        fig1, ax1 = plt.subplots(figsize=(5, 5))
        colors = plt.cm.Paired.colors
        ax1.pie(causes_means, labels=causes_means.index, autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 10})
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig1, use_container_width=False)
    st.divider()

with model_stats:
    st.text("Example")

with st.sidebar:
    st.title("Prévisions des retards SNCF")
    st.selectbox("Station de départ", existing_departure_stations, key="departure_station", index=None, placeholder="Sélectionnez une station de départ")
    st.selectbox("Station d'arrivée", existing_arrival_stations, key="arrival_station", index=None, placeholder="Sélectionnez une station d'arrivée")
    st.date_input("Date de départ", key="departure_date", min_value="today", format="DD/MM/YYYY")
    st.selectbox("Type de Train", ["National", "International"], key="train_type", index=None, placeholder="Sélectionnez un type de train")

    if st.button("Afficher les prévisions de retards", type="primary") :
        if st.session_state.departure_station is None or st.session_state.arrival_station is None or st.session_state.departure_date is None or st.session_state.train_type is None:
            st.warning("⚠️ Valeur.s manquante.s")
            st.stop()
        if st.session_state.departure_station == st.session_state.arrival_station:
            st.error("❌ Les stations de départ et d'arrivée ne peuvent pas être les mêmes.")
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
            st.session_state.save_values = {
                "late": max(0, model.predict(donnees_entree)[0]),
                "start": departure,
                "end": arrival,
                "season": values["season"],
                "date": journey_date
            }
        except Exception as e:
            st.error("Erreur lors de la prédiction.")
            st.warning(f"Détail technique : {e}")
    
    st.divider()
    st.info("Tableau de bord interactif qui permet de prévoir les futurs retards sur un trajet en train.")

with result:
    if (st.session_state.save_values):
        tab = st.session_state.save_values
        st.markdown(
            f"""
        <div class="prediction-box">
            <h3>Résultat détaillé</h3>
            <p><b>{tab["start"]}</b> -> <b>{tab["end"]}</b> - <b>{tab["date"].strftime("%d/%m/%Y")}</b> :</p>
            <h3 style="color: #3182ce;">⏱️ Retard estimé : {tab["late"]:.0f} minutes</h3>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.info("👈 Remplissez les informations de votre prochain départ pour lancer une prédiction")
