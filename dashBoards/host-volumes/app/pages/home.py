import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table, callback


import pandas as pd

import numpy as np
import statistics 
import requests
import os
from geopy.distance import geodesic
from PIL import Image
import sys

import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go

import requests
from geopy.distance import geodesic
import json
from pandas import json_normalize
from geopy.geocoders import Nominatim
import pyproj
from sqlalchemy import create_engine, MetaData, inspect, text
import configparser
from configparser import ConfigParser
import psycopg2
import datetime
from datetime import date, timedelta


# To create meta tag for each page, define the title, image, and description.
dash.register_page(__name__,
                   path='/',  # '/' is home page and it represents the url
                   name='Home',  # name of page, commonly used as name of link
                   title='Index',  # title that appears on browser's tab
                   #image='pg1.png',  # image in the assets folder
                   description='ParKli Overview'
)


# page 1 data
#df = px.data.gapminder()

##########################################################################################################################################
# Funktion zum Lesen der Datenbankverbindung aus einer Ini-Datei
def database_connection():
     # Pfad des aktuellen Skripts
    #current_script_path = os.path.dirname(__file__)

    # Pfad zum Basisverzeichnis des Projekts
    #base_directory_path = os.path.dirname(current_script_path)

    # Pfad zur config.ini im lib-Ordner
    #config_file_path = os.path.join(base_directory_path, 'lib', 'config.ini')

    # Konfigurationsdatei lesen
    #config = configparser.ConfigParser()
    #config.read(config_file_path)

    # Datenbankverbindung herstellen
    dbname = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOSTNAME']
    port = os.environ['POSTGRES_PORT']
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    engine = create_engine(connection_string)
    return engine

#####################################################################################################################################################
# Funktion zum Abrufen der Daten aus der Datenbank
def fetch_data_from_db(engine):
    query = text('SELECT * FROM "greenSpaceHackCleanData"')
    return pd.read_sql(query, engine)


########################################################################################################################################################


def download_inaturalist_data(min_lat, max_lat, min_lon, max_lon):
     
    # Definieren Sie den geografischen Bereich
    swlat = min_lat  # Südliche Breite
    swlng = min_lon  # Westliche Länge
    nelat = max_lat  # Nördliche Breite
    nelng = max_lon  # Östliche Länge


    # Setzen Sie die Anfangsseite auf 1
    page = 1

    # Initialisieren Sie eine leere Liste zum Speichern der Beobachtungsdaten
    all_observations = []

    while True:
        
        if page > 4:
            break
        
        # Setzen Sie die API-Endpunkt-URL mit den entsprechenden Parametern
        url = f'https://api.inaturalist.org/v1/observations?swlat={swlat}&swlng={swlng}&nelat={nelat}&nelng={nelng}&page={page}&per_page=200'

        # Machen Sie eine GET-Anfrage an die iNaturalist API
        response = requests.get(url)

        # Extrahieren Sie die Beobachtungsdaten aus der API-Antwort (JSON-Format)
        data = response.json()

        # Überprüfen Sie, ob Beobachtungsdaten vorhanden sind
        if 'results' in data:
            # Fügen Sie die Beobachtungsdaten zur Liste hinzu
            all_observations.extend(data['results'])
            
            # Überprüfen Sie, ob die Anzahl der Beobachtungen kleiner als die maximale Seite ist
            if len(data['results']) < data['per_page']:
                break  # Beenden Sie die Schleife, wenn alle Beobachtungen abgerufen wurden

            # Inkrementieren Sie die Seite für die nächste Anfrage
            page += 1
        else:
            break  # Beenden Sie die Schleife, wenn keine Beobachtungen vorhanden sind
    # Ausgabe der Gesamtanzahl der heruntergeladenen Beobachtungen
    observation_count = len(all_observations)
    print(f'Anzahl der heruntergeladenen Beobachtungen: {observation_count}')
    
    df = pd.json_normalize(all_observations)
    df[['latitude', 'longitude']] = df['location'].str.split(',', expand=True)

    # Datentypen der neuen Spalten korrigieren
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    df.head()
    print(len(df))
    return df 



#######################################################################################################################################################################
 # Navigiert eine Ebene nach oben und dann in den Ordner 'assets'   

# Define a function to load and filter data
def load_eyeonwater_data(lat_center, lon_center, radius):

    relative_path = os.path.join('..', 'assets', 'CSVPictureDate')
    # Vollständiger Pfad zur Datei, ausgehend vom aktuellen Skriptverzeichnis
    save_folder_CSV = os.path.join(os.path.dirname(__file__), relative_path)

    # Überprüfen, ob bereits eine CSV-Datei existiert
    csv_path = os.path.join(save_folder_CSV, 'data_api.csv')
    if os.path.exists(csv_path):
    # Lade das DataFrame aus der CSV-Datei
        df = pd.read_csv(csv_path)
        df['date_photo'] = pd.to_datetime(df['date_photo']) 
        df_eyeonwater_len = (len(df))
       
        df['distance'] = df.apply(lambda row: geodesic((row['lat'], row['lng']), (lat_center, lon_center)).km, axis=1)
        df = df[df['distance'] <= radius]
        return df, df_eyeonwater_len
    else:
        df =0
        df_eyeonwater_len=0
        return df, df_eyeonwater_len
################################################################################################################################

# Load the EyeOnWater data (replace with the actual file path)
df_eyeonwater, df_eyeonwater_len = load_eyeonwater_data(48.7721, 9.1733, 1)


#########################################################################################################################################################################
try:
    #Laden der Daten von greenspacehack.com
   
    engine = database_connection()
    dfGreenSpaceHack = fetch_data_from_db(engine)

    dfGreenSpaceHack_FeuerSee = dfGreenSpaceHack.copy()
    
    dfGreenSpaceHack_FeuerSee['distance'] = dfGreenSpaceHack_FeuerSee.apply(lambda row: geodesic((row['location.1'], row['location.0']), (48.7721, 9.1733)).km, axis=1)
    
    dfGreenSpaceHack_FeuerSee = dfGreenSpaceHack_FeuerSee[dfGreenSpaceHack_FeuerSee['distance'] <= 0.7]
    print(len(dfGreenSpaceHack_FeuerSee))
    # Berechnung des durchschnittlichen NEST-Scores für den Feuersee
    average_nest_score_feuersee = dfGreenSpaceHack_FeuerSee['Overall NEST score'].mean()

except Exception as e:
    print(f"Daten konnten nicht heruntergeladen werden: {e}")
    engine = database_connection()
    dfGreenSpaceHack = fetch_data_from_db(engine)
    if dfGreenSpaceHack is not None:
        print("Daten erfolgreich aus der Datenbank abgerufen.")
    else:
        print("Keine Daten in der Datenbank vorhanden.")


#############################################################################################################################################

# Dictionary mit Fragen und Antworten
questions_dict = {
    "shade": {
        "question": "Measure of shade elements",
        "answers": {
            0.0: "Keine (habe aber welche erwartet) / None (but expected some)",
            1.0: "Schlecht / Poor",
            2.0: "Ausreichend / Adequate / Keine (habe keine erwartet) / None (didn't expect any)",
            3.0: "Gut / Good"
        }
    },
    "drinking_fountains": {
        "question": "Measure of drinking fountains",
        "answers": {
            0.0: "Keine (habe aber welche erwartet) / None (but expected some)",
            1.0: "Schlecht / Poor",
            2.0: "Ausreichend / Adequate / Keine (habe keine erwartet) / None (didn't expect any)",
            3.0: "Gut / Good"
        }
    },
    "biodiversity": {
        "question": "Measure of biodiversity (wildlife/wild flowers)",
        "answers": {
            0.0: "Keine / None",
            1.0: "Schlecht / Poor",
            2.0: "Ausreichend / Adequate",
            3.0: "Gut / Good"
        }
    },
    "green_space_care": {
        "question": "Measure of green space care (flower beds/planters)",
        "answers": {
            0.0: "Keine / None",
            1.0: "Schlecht / Poor",
            2.0: "Ausreichend / Adequate",
            3.0: "Gut / Good"
        }
    }
}
##############################################################################################################################################

url = f"https://api.inaturalist.org/v1/observations?project_id=parkli"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    #data["total_results"]
else:
    print("Fehler bei der Anfrage:", response.status_code)

# Define the coordinates for Feuersee
feuersee_center_lat = 48.7721
feuersee_center_lon = 9.1733
radius = 0.01

# Calculate the bounding box for the specified radius around Feuersee
min_lat = feuersee_center_lat - radius
max_lat = feuersee_center_lat + radius
min_lon = feuersee_center_lon - radius
max_lon = feuersee_center_lon + radius

# Download iNaturalist data for the Feuersee area
df_inaturalist_feuersee = download_inaturalist_data(min_lat, max_lat, min_lon, max_lon)

# Replace 'true' and 'false' with actual boolean values and create numeric columns
df_inaturalist_feuersee['taxon.threatened'] = df_inaturalist_feuersee['taxon.threatened'].replace({'true': True, 'false': False})
df_inaturalist_feuersee['taxon.introduced'] = df_inaturalist_feuersee['taxon.introduced'].replace({'true': True, 'false': False})
df_inaturalist_feuersee['threatened_numeric'] = df_inaturalist_feuersee['taxon.threatened'].fillna(0).astype(int)
df_inaturalist_feuersee['introduced_numeric'] = df_inaturalist_feuersee['taxon.introduced'].fillna(0).astype(int)

    
##############################################################################################################################################

card_iNaturalist = dbc.Card(
  
      #dbc.CardHeader("Anzahl Beobachtungen iNaturalist ParKli"),
      dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-search"), " Beobachtungen iNaturalist ParKli"], className="text-nowrap"),
            html.H5(data["total_results"]),
          
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
  
)

##############################################################################################################################
card_GreenSpaceHack = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-question-square"), " Anzahl Fragebögen Greenspace Hack"], className="text-nowrap"),
            html.H5(len(dfGreenSpaceHack)),
        ], className="border-start border-danger border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)

##############################################################################################################################
card_EyeOnWater = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-water"), " Anzahl Beobachtungen EyeOnWater"], className="text-nowrap"),
            html.H5(df_eyeonwater_len),
    
        ], className="border-start border-secondary border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)
##############################################################################################################################
# Create the layout for the EyeOnWater section
eyeonwater_layout = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-water"), " EyeOnWater Observations around Feuersee, Stuttgart"], className="text-center"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[
                    {'label': 'FU Value (User)', 'value': 'fu_value'},
                    {'label': 'FU Value (App)', 'value': 'fu_processed'},
                ],
                value='fu_value',
                clearable=False,
            ),
            dcc.Graph(id='density-map'),
        ], className="border-start border-secondary border-5"
    ),
    className="m-4 shadow bg-white rounded"
)
##############################################################################################################################
# Create the additional dropdown and graphs for pH and Secchi disk measurements
card_ph_secchi = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-bar-chart"), " pH and Secchi Disk Measurements"], className="text-center"),
            dcc.Dropdown(
                id='ph-secchi-dropdown',
                options=[
                    {'label': 'pH Values', 'value': 'p_ph'},
                    {'label': 'Secchi Disk Depth', 'value': 'sd_depth'},
                ],
                value='p_ph',
                clearable=False,
            ),
            dcc.Graph(id='ph-secchi-graph'),
        ], className="border-start border-secondary border-5"
    ),
    className="m-4 shadow bbg-white rounded"
)
##############################################################################################################################
# Create the card for observation count and distribution
card_observations_distribution = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-bar-chart-line"), " Observations and Distribution"], className="text-center"),
            dcc.Dropdown(
                id='observations-distribution-dropdown',
                options=[
                    {'label': 'Number of Observations', 'value': 'observations'},
                    {'label': 'Distribution (Boxplot)', 'value': 'distribution'},
                ],
                value='observations',
                clearable=False,
            ),
            dcc.Graph(id='observations-distribution-graph'),
        ], className="border-start border-secondary border-5"
    ),
    className="m-4 shadow bg-white rounded"
)

##############################################################################################################################
card_GreenSpaceHack_Number_of_questionnaires_Feuersee = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-question-square"), " Anzahl Fragebögen Feuersee"], className="text-wrap"),
            html.H5(len(dfGreenSpaceHack_FeuerSee)),
        ], className="border-start border-danger border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)
############################################################################################################################
# Erstellung einer Card zur Anzeige des durchschnittlichen NEST-Scores
card_average_nest_score_feuersee = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-bar-chart"), " Average NEST Score Feuersee"], className="text-wrap"),
            html.H5(f"{average_nest_score_feuersee:.2f}"),
        ], className="border-start border-danger border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)

##############################################################################################################################
card_GreenSpaceHack_NEST_Score_Map = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-map"), " NEST Score Map"], className="text-center"),
            dcc.Graph(
                id='nest-score-map',
                figure=px.scatter_mapbox(
                    dfGreenSpaceHack_FeuerSee, lat='location.1', lon='location.0',
                    color='Overall NEST score', size='Overall NEST score',
                    color_continuous_scale=px.colors.cyclical.IceFire,
                    size_max=20, zoom=13, mapbox_style="open-street-map",
                    title='NEST Score around Feuersee, Stuttgart'
                )
            ),
        ], className="border-start border-danger border-5"
    ),
    className="m-4 shadow bg-white rounded h-100 class"
)
##############################################################################################################################
card_greenspacehack_questions = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-question-circle"), " GreenSpaceHack Questions"], className="text-center"),
            dcc.Dropdown(
                id='greenspacehack-questions-dropdown',
                options=[
                    {'label': 'Shade Elements', 'value': 'shade'},
                    {'label': 'Drinking Fountains', 'value': 'drinking_fountains'},
                    {'label': 'Biodiversity', 'value': 'biodiversity'},
                    {'label': 'Green Space Care', 'value': 'green_space_care'}
                ],
                value='shade',
                clearable=False,
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='greenspacehack-questions-graph'), width=8),
                    dbc.Col(html.Div(id='question-legend'), width=4)
                ]
            )
        ], className="border-start border-danger border-5"
    ),
    className="m-4 shadow bg-white rounded h-100 class"
)


##############################################################################################################################
# Create the layout for the iNaturalist section
inaturalist_layout = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-search"), " iNaturalist Observations around Feuersee, Stuttgart"], className="text-center"),
            dcc.Dropdown(
                id='dropdown_map_invasive_threatened_species_home',
                options=[
                    {'label': 'Übersicht Arten', 'value': 'all_species'},
                    {'label': 'Invasive Arten', 'value': 'invasive_species'},
                    {'label': 'Bedrohte Arten', 'value': 'threatened_species'}
                ],
                value='all_species',
                clearable=False,
            ),
            html.Br(),
            dcc.Graph(id='map_invasive_threatened_species_home'),
        ], className="border-start border-success border-5"
    ),
    className="m-4 shadow bg-white rounded h-100 class"
)
##############################################################################################################################
# Create the card for the pie chart
pie_chart_layout = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-pie-chart"), " Verteilung Spezieskategorien"], className="text-center"),
            dcc.Graph(id='pie_species_categories_home')
        ], className="border-start border-success border-5"
    ),
    className="m-4 shadow bg-white rounded h-100 class"
)
#################################################################################################################################
# Card für die Anzahl der Beobachtungen
card_inaturalist_observations = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-eye"), " Anzahl Beobachtungen iNaturalist"], className="text-wrap"),
            html.H5(len(df_inaturalist_feuersee)),
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)

##################################################################################################################################
# Card für die Anzahl der unterschiedlichen Arten
species_counts = df_inaturalist_feuersee['taxon.preferred_common_name'].nunique()
card_inaturalist_species = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-list-task"), " Unterschiedliche Arten iNaturalist"], className="text-wrap"),
            html.H5(species_counts),
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)
#####################################################################################################################################
# Card für die Anzahl der invasiven Arten
invasive_species_counts = df_inaturalist_feuersee[df_inaturalist_feuersee['introduced_numeric'] == 1]['taxon.preferred_common_name'].nunique()
card_inaturalist_invasive_species = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-exclamation-triangle"), " Invasive Arten iNaturalist"], className="text-wrap"),
            html.H5(invasive_species_counts),
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)
#######################################################################################################################################
# Card für die Anzahl der bedrohten Arten
threatened_species_counts = df_inaturalist_feuersee[df_inaturalist_feuersee['threatened_numeric'] == 1]['taxon.preferred_common_name'].nunique()
card_inaturalist_threatened_species = dbc.Card(
    dbc.CardBody(
        [
            html.H4([html.I(className="bi bi-shield-exclamation"), " Bedrohte Arten iNaturalist"], className="text-wrap"),
            html.H5(threatened_species_counts),
        ], className="border-start border-success border-5"
    ),
    className="text-center m-4 shadow bg-light rounded",
)
#########################################################################################################################################


# Layout
layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(card_iNaturalist), 
                dbc.Col(card_GreenSpaceHack), 
                dbc.Col(card_EyeOnWater),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(eyeonwater_layout, width=4),
                dbc.Col(card_ph_secchi, width=4),
                dbc.Col(card_observations_distribution, width=4),
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                card_GreenSpaceHack_Number_of_questionnaires_Feuersee,
                            ],
                        ),
                        dbc.Row(
                            [
                                card_average_nest_score_feuersee,
                            ],
                        ),
                    ], width={"size": 2}
                ),                     
                dbc.Col(card_GreenSpaceHack_NEST_Score_Map, width=5),
                dbc.Col(card_greenspacehack_questions, width=5),
                
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                card_inaturalist_observations,
                            ],
                        ),
                        dbc.Row(
                            [
                                card_inaturalist_species
                            ],
                        ),
                        dbc.Row(
                            [
                                card_inaturalist_invasive_species,
                            ],
                        ),
                        dbc.Row(
                            [
                                card_inaturalist_threatened_species,
                            ],
                        ),
                    ], width={"size": 2}
                ),                     
                dbc.Col(inaturalist_layout, width=5),
                dbc.Col(pie_chart_layout, width=5),
                
            ],
        ),
        html.Br(),
    ]
)
##########################################################################################################################
# Callback to update the density map based on the selected metric
@callback(
    Output('density-map', 'figure'),
    Input('metric-dropdown', 'value')
)
def update_density_map(selected_metric):
    fig = px.density_mapbox(
        df_eyeonwater, lat='lat', lon='lng', z=selected_metric,
        radius=10, center=dict(lat=48.7721, lon=9.1733), zoom=13,
        mapbox_style="open-street-map"
    )
    return fig
#################################################################################################################################
# Callback to update the pH values or Secchi disk depth based on the selected metric
@callback(
    Output('ph-secchi-graph', 'figure'),
    Input('ph-secchi-dropdown', 'value')
)
def update_ph_secchi_graph(selected_metric):
     
    if selected_metric == 'p_ph':
        df_filtered = df_eyeonwater[df_eyeonwater['p_ph'].notna()]
        df_filtered =  df_filtered.loc[(df_filtered['p_ph'] > 0)]
        fig = px.scatter(df_filtered, x='date_photo', y='p_ph', title='pH Values Over Time')

    elif selected_metric == 'sd_depth':
        df_filtered = df_eyeonwater[((df_eyeonwater['sd_depth'].notna()) & ((df_eyeonwater['sd_depth'] > 0) & (df_eyeonwater['sd_depth'] < 1)))]
        fig = px.scatter(df_filtered, x='date_photo', y='sd_depth', title='Secchi Disk Depth Over Time')
    else:
        dash.no_update
    
    return fig
###############################################################################################################################
# Callback to update the number of observations or the distribution based on the selected metric
@callback(
    Output('observations-distribution-graph', 'figure'),
    Input('observations-distribution-dropdown', 'value')
)
def update_observations_distribution_graph(selected_metric):
    if selected_metric == 'observations':
        df_observation_filtered_df = df_eyeonwater.groupby('month_year')['image'].count().reset_index()
        df_observation_filtered_df.sort_values(by='month_year')
        fig = px.bar(df_observation_filtered_df, x='month_year', y='image', labels={'month_year':'Zeit', 'image': 'Beobachtungen'})
    elif selected_metric == 'distribution':
        fig = px.box(df_eyeonwater, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot')
    return fig
#################################################################################################################################
# Callback to update the GreenSpaceHack questions graph
@callback(
    [Output('greenspacehack-questions-graph', 'figure'),
     Output('question-legend', 'children')],
    Input('greenspacehack-questions-dropdown', 'value')
)
def update_greenspacehack_questions_graph(selected_question):
    if selected_question == 'shade':
        df_filtered = dfGreenSpaceHack_FeuerSee[['AM6', 'AM7']].melt(var_name='Measure', value_name='Score')
        fig = px.box(df_filtered, x='Measure', y='Score', title='Shade Elements Scores')
        legend = questions_dict['shade']['answers']
    elif selected_question == 'drinking_fountains':
        df_filtered = dfGreenSpaceHack_FeuerSee[['AM10']].melt(var_name='Measure', value_name='Score')
        fig = px.box(df_filtered, x='Measure', y='Score', title='Drinking Fountains Scores')
        legend = questions_dict['drinking_fountains']['answers']
    elif selected_question == 'biodiversity':
        df_filtered = dfGreenSpaceHack_FeuerSee[['NA7']].melt(var_name='Measure', value_name='Score')
        fig = px.box(df_filtered, x='Measure', y='Score', title='Biodiversity Scores')
        legend = questions_dict['biodiversity']['answers']
    elif selected_question == 'green_space_care':
        df_filtered = dfGreenSpaceHack_FeuerSee[['NA8']].melt(var_name='Measure', value_name='Score')
        fig = px.box(df_filtered, x='Measure', y='Score', title='Green Space Care Scores')
        legend = questions_dict['green_space_care']['answers']
    else:
        fig = go.Figure()
        legend = {}

    fig.update_layout(transition_duration=500)

    legend_html = html.Ul([
        html.Li(f"{value}: {description}") for value, description in legend.items()
    ])

    return fig, legend_html
########################################################################################################################################
# Callback to update the iNaturalist map
@callback(
    Output('map_invasive_threatened_species_home', 'figure'),
    Input('dropdown_map_invasive_threatened_species_home', 'value')
)
def update_map_overview_invasive_threatened_species(value):
    if value == 'threatened_species':
        filtered_df = df_inaturalist_feuersee[df_inaturalist_feuersee['threatened_numeric'] == 1]
    elif value == 'invasive_species':
        filtered_df = df_inaturalist_feuersee[df_inaturalist_feuersee['introduced_numeric'] == 1]
    else:
        filtered_df = df_inaturalist_feuersee.copy()

    fig = px.scatter_mapbox(
        filtered_df, 
        lat="latitude", 
        lon="longitude",
        hover_name="taxon.preferred_common_name",
        hover_data=["taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
        color="taxon.preferred_common_name",
        color_continuous_scale=px.colors.cyclical.IceFire, 
        zoom=13, 
        mapbox_style="open-street-map",
        title='iNaturalist Observations around Feuersee, Stuttgart'
    )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
   
    return fig

# Callback to update the pie chart
@callback(
    Output('pie_species_categories_home', 'figure'),
    Input('dropdown_map_invasive_threatened_species_home', 'value')
)
def update_pie_chart(value):
    if value == 'threatened_species':
        filtered_df = df_inaturalist_feuersee[df_inaturalist_feuersee['threatened_numeric'] == 1]
    elif value == 'invasive_species':
        filtered_df = df_inaturalist_feuersee[df_inaturalist_feuersee['introduced_numeric'] == 1]
    else:
        filtered_df = df_inaturalist_feuersee.copy()

    # Pie Chart for Species Categories
    iconic_taxon_counts = filtered_df['taxon.iconic_taxon_name'].value_counts()
    fig_pie = px.pie(
        iconic_taxon_counts, 
        names=iconic_taxon_counts.index, 
        values=iconic_taxon_counts.values, 
        title='Verteilung Spezieskategorien',
        labels={'names': 'Kategorie', 'values': 'Anzahl der Beobachtungen'}
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig_pie
