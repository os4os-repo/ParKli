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
import time
import psycopg2
from configparser import ConfigParser


dash.register_page(__name__,
                   path='/biodiversity',  # represents the url text
                   name='Biodiversity',  # name of page, commonly used as name of link
                   title='ParKli Biodiversity'  # epresents the title of browser's tab
)




########################################################################################################################################################

def download_data_from_postgresql_(min_lat, max_lat, min_lon, max_lon):
    """
    Lädt Beobachtungsdaten aus der PostgreSQL-Datenbank basierend auf einem geografischen Bereich herunter.

    :param min_lat: Minimale Breitengradgrenze des Bereichs.
    :param max_lat: Maximale Breitengradgrenze des Bereichs.
    :param min_lon: Minimale Längengradgrenze des Bereichs.
    :param max_lon: Maximale Längengradgrenze des Bereichs.
    :return: Ein pandas DataFrame mit den heruntergeladenen Daten.
    """

    # Pfad des aktuellen Skripts
    #current_script_path = os.path.dirname(__file__)

    # Pfad zum Basisverzeichnis des Projekts
    #base_directory_path = os.path.dirname(current_script_path)

    # Pfad zur config.ini im lib-Ordner
    #config_file_path = os.path.join(base_directory_path, 'lib', 'config.ini')

    # Konfigurationsdatei lesen
    #config = ConfigParser()
    #config.read(config_file_path)
    
    # Zugriff auf die Konfigurationswerte
    connection_details = {
        'dbname': os.environ['POSTGRES_DB'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'host': os.environ['POSTGRES_HOSTNAME'],
        'port': os.environ['POSTGRES_PORT']
    }
    
    # Verbindung zur Datenbank aufbauen
    try:
        conn = psycopg2.connect(**connection_details)
        cursor = conn.cursor()
        
        # SQL-Abfrage vorbereiten
        query = """
        SELECT * FROM inaturalist_observations
        WHERE CAST(latitude AS NUMERIC) BETWEEN %s AND %s
        AND CAST(longitude AS NUMERIC) BETWEEN %s AND %s;
        """
        
        # SQL-Abfrage ausführen
        cursor.execute(query, (min_lat, max_lat, min_lon, max_lon))
        
        # Ergebnisse abrufen
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=colnames)
        
        # Ressourcen freigeben
        cursor.close()
        conn.close()
        
        return df
    
    except Exception as e:
        print("Fehler beim Herunterladen der Daten:", e)
        return pd.DataFrame()  # Leeres DataFrame bei Fehler





def download_data_from_postgresql(min_lat, max_lat, min_lon, max_lon):
    """
    Lädt Beobachtungsdaten aus der PostgreSQL-Datenbank basierend auf einem geografischen Bereich herunter.

    :param min_lat: Minimale Breitengradgrenze des Bereichs.
    :param max_lat: Maximale Breitengradgrenze des Bereichs.
    :param min_lon: Minimale Längengradgrenze des Bereichs.
    :param max_lon: Maximale Längengradgrenze des Bereichs.
    :param connection_details: Ein Dictionary mit den Verbindungsdetails zur Datenbank.
    :return: Ein pandas DataFrame mit den heruntergeladenen Daten.
    """

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using 
    sys.stdout.write(f"[DEBUG] START download_data_from_postgresql - {start_time}\n")
    sys.stdout.flush()
    
     # Pfad des aktuellen Skripts
    #current_script_path = os.path.dirname(__file__)

        # Pfad zum Basisverzeichnis des Projekts
    #base_directory_path = os.path.dirname(current_script_path)

        # Pfad zur config.ini im lib-Ordner
    #config_file_path = os.path.join(base_directory_path, 'lib', 'config.ini')

    # Konfigurationsdatei lesen
    #config = ConfigParser()
    #config.read(config_file_path)
    
    # Zugriff auf die Konfigurationswerte
    dbname = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOSTNAME']
    port = os.environ['POSTGRES_PORT']
    
    connection_details = {
        'dbname': os.environ['POSTGRES_DB'],
        'user': os.environ['POSTGRES_USER'],
        'password': os.environ['POSTGRES_PASSWORD'],
        'host': os.environ['POSTGRES_HOSTNAME'],
        'port': os.environ['POSTGRES_PORT']
    }
    
    
    # Verbindung zur Datenbank aufbauen
    try:
        conn = psycopg2.connect(
            dbname=connection_details['dbname'],
            user=connection_details['user'],
            password=connection_details['password'],
            host=connection_details['host'],
            port=connection_details['port']
        )
        cursor = conn.cursor()
        
        # SQL-Abfrage vorbereiten
        query = f"""
        SELECT * FROM inaturalist_observations
        WHERE latitude BETWEEN %s AND %s
        AND longitude BETWEEN %s AND %s;
        """
        
        # SQL-Abfrage ausführen
        cursor.execute(query, (min_lat, max_lat, min_lon, max_lon))
        
        # Ergebnisse abrufen
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=colnames)
        
        # Ressourcen freigeben
        cursor.close()
        conn.close()

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
        sys.stdout.write(f"[DEBUG] END   download_data_from_postgresql - {end_time}\n")
        sys.stdout.flush()
        
        return df
    
    except Exception as e:
        print("Fehler beim Herunterladen der Daten:", e)
        return pd.DataFrame()  # Leeres DataFrame bei Fehler


##########################################################################################################################################

# Funktion zum Herunterladen von iNaturalist-Daten in einem bestimmten geografischen Bereich

def download_inaturalist_data(min_lat, max_lat, min_lon, max_lon):

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START download_inaturalist_data - {start_time}\n")
    sys.stdout.flush()
     
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
        
        if page > 5:
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

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] END   download_inaturalist_data - {end_time}\n")
    sys.stdout.flush()
    return df 
#########################################################################################################################################
#Lesen der Invasive Arten aus Excel Datei
def excel_invasive_species():

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START excel_invasive_species - {start_time}\n")
    sys.stdout.flush()
    
    #current_directory = os.getcwd()
    #path = os.path.join(current_directory, 'urlTest/src/assets/')
    # Navigiert eine Ebene nach oben und dann in den Ordner 'assets'
    relative_path = os.path.join('..', 'assets', '2023_02_14__IAS_Liste_BW_Kurzfassung_Internet_LUBW.xlsx')
    
    # Vollständiger Pfad zur Datei, ausgehend vom aktuellen Skriptverzeichnis
    file_path = os.path.join(os.path.dirname(__file__), relative_path)
    
    try:
        dfInvasiveArten = pd.read_excel(file_path, skiprows=1)
    except FileNotFoundError:
        print(f"Datei nicht gefunden: {file_path}")
    #dfInvasiveArten  = pd.read_excel(file_path, skiprows=1)

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] END   excel_invasive_species - {end_time}\n")
    sys.stdout.flush()

    return dfInvasiveArten

##########################################################################################################################################

card_Location = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-geo-alt me-2"), "Untersuchungsort"], className="text-nowrap text-center pe-2"),
            #dbc.FormText("Geben Sie den Namen der Stadt ein", className="text-nowrap", style={'width': '300px'}),
            #dbc.Input(id='city-input',persistence=True, placeholder="Geben Sie ein Namen einer Stadt ein...", type="text", style={'width': '300px'}),
            dbc.FormText("Geben Sie den Namen einer Stadt ein", className="w-auto col-md-6"),
            dbc.Input(id='city-input',persistence=False, placeholder="Stadt...", type="text", className="form-control col-md-6", style={'width': '200px'}),
            
            #dbc.FormText("Legen Sie den Suchradius in ° schrittweite 0.01 fest",className="text-nowrap", style={'width': '300px'}),
            #dbc.Input(id='latLon-input',placeholder='0.05', type="number", min=0, max=1, step=0.01, value='0.05', style={'width': '300px'}),
            dbc.FormText("Legen Sie den Suchradius in ° schrittweite 0.01 fest",className="w-auto col-md-6"),
            dbc.Input(id='latLon-input',placeholder='0.02', type="number", min=0, max=1, step=0.01, value='0.02', className="form-control col-md-6", style={'width': '200px'}),
            html.Br(),
            #html.Button('Daten herunterladen', id='download-button', n_clicks=0),
            dbc.Button("Daten herunterladen", id="download-button", n_clicks=0, outline=True, color="secondary", className="me-2 text-nowrap"),
            #dbc.Button("Load Session", id="loadSession-button", n_clicks=0, outline=True, color="secondary", className="me-2 text-nowrap"),
            html.Br(),
        ],
        className="border-start border-success border-5",
       
    ),
    className="m-2 shadow bg-white rounded ",
)

card_UpdateMap = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-map me-2"), "Auswahl Daten"], className="text-center"),
            html.Br(),
            #html.Div(id='map'),
            dcc.Graph(id='map', figure={}),
        ],
        className="border-start border-success border-5",
       
    ),
    className="m-2 shadow bg-white rounded",
)



    
################################################################################################################################################
def layout(data = dcc.Store(id='memory-output'), selectedDataState= dcc.Store(id='selectedData-State')):

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START layout - {start_time}\n")
    sys.stdout.flush()
    
    # print(data)
    # print(type(data))

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] END   layout - {end_time}\n")
    sys.stdout.flush()

    return html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        
                                        html.Br(), 
                                        html.Br(), 
                                        html.Br(), 
                                        html.Img(src="./assets/ParKli_Biodiv_300px.png", height="50", style={'display': 'inline-block'}),
                                        html.H1("ParKli Biodiversität",style={'textAlign': 'center', 'color': '#2F5F53','display': 'inline-block', 'margin-left': 'auto', 'margin-right': 'auto' }),
                                        
                                    ],
                                    className="position-absolute top-0 start-50"
                                    
                                )
                            ], width=12
                        )
                        
                    ]
                ),
                html.Br(), 
                html.Br(), 
                
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                card_Location,
                               
                            ], 
                            #width={"size": 2}
                            xs=5, sm=5, md=5, lg=4, xl=3, xxl=3
                        ),
                        dbc.Col(
                            [
                                card_UpdateMap,
                               
                            ], 
                            #width={"size": 10}
                            xs=7, sm=7, md=7, lg=9, xl=9, xxl=9
                        ),
                    ]
                ),
        
                html.Br(),
                html.Br(), 
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='box-select'),
                            ], width=12
                        )
                    ]
                ),  
        
            ]
        )

##################################################################################################################################################

# Callback-Funktion für das Herunterladen der iNaturalist-Daten und Aktualisierung der Scattermapbox
@callback(
    #Output('map', 'figure', allow_duplicate=True),
    Output('map', 'figure'),
    Output('memory-output', 'data'),
    Input('download-button', 'n_clicks'),
    State('city-input', 'value'),
    State('latLon-input', 'value'),
    State('memory-output', 'data'),
    prevent_initial_call=False
)
def update_map(n_clicks, city, latLonCorrection, data):
    
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START update_map - {start_time}\n")
    sys.stdout.flush()

    #print(data)
    #print(type(data))

    if n_clicks > 0 and city:
        # Längen- und Breitengrade der Stadt finden
        geolocator = Nominatim(user_agent='ParKli.de')
        location = geolocator.geocode(city, language='de')
        
        if location is None:
            return fig
        
        lat = location.latitude
        lon = location.longitude
        
        #print(type(latLonCorrection))
        
        latLonCorrection = float(latLonCorrection) 
        
        # Bereich für iNaturalist-Daten berechnen (z.B. 0.1 Grad um den ausgewählten Punkt)
        min_lat = lat - latLonCorrection
        max_lat = lat + latLonCorrection
        min_lon = lon - latLonCorrection
        max_lon = lon + latLonCorrection
        
        locationBW = geolocator.geocode(city, addressdetails=True)
        
        if locationBW and 'address' in locationBW.raw:
            address = locationBW.raw['address']
            # Überprüfen, ob das 'state'-Feld in der Adresse vorhanden ist und 'Baden-Württemberg' entspricht
            if 'state' in address and address['state'] == 'Baden-Württemberg':
                obersvation = download_data_from_postgresql(min_lat, max_lat, min_lon, max_lon)
            else:
                obersvation = download_inaturalist_data(min_lat, max_lat, min_lon, max_lon)
        
        
        # iNaturalist-Daten herunterladen
        #
        
        data=obersvation.to_dict('records')
        
        
        fig={}
        fig = px.scatter_mapbox(obersvation, 
            lat="latitude", 
            lon="longitude",
            hover_name="taxon.preferred_common_name",
            hover_data=["id","taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
            color_discrete_sequence=["black"],
            zoom=10, height=300
        )
        #fig.update_layout(mapbox_style="stamen-terrain")
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
         
        #return html.Div([ dcc.Graph(figure = fig)]), data     

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
        sys.stdout.write(f"[DEBUG] END   update_map - {end_time}\n")
        sys.stdout.flush()

        return fig, data
        #return fig
    elif data:
        print('Test')
        dash.no_update

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] END   update_map - {end_time}\n")
    sys.stdout.flush()

    return dash.no_update




#########################################################################################################################################
# Callback-Funktion für den Box Select
@callback(
    #Output('box-select', 'children', allow_duplicate=True),
    #Output('selectedData-State', 'selectedDataState', allow_duplicate=True),
    Output('box-select', 'children'),
    Output('selectedData-State', 'selectedDataState'),
    Input('map', 'selectedData'),
    State ('memory-output', 'data'),
    State ('selectedData-State', 'selectedDataState'),
    prevent_initial_call=True
)
def update_box_select(selectedData, data, selectedDataState):

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START update_box_select - {start_time}\n")
    sys.stdout.flush()

    if not selectedData:
        # Wenn keine Daten ausgewählt wurden, zeige einen leeren Plot
        return dash.no_update
    else:
        
        try:
            # Extrahiere die ausgewählten Daten
            #print(selectedData)
            #print(type(selectedData))
            
            
            
            points = selectedData['points']
            selected_df = pd.DataFrame(points)
            #print(selected_df.head())
            #selected_df.info()
            #print(selected_df['hovertext'])
            listHovertext= selected_df['customdata'].values.tolist()
            #print(type(listHovertext))
            #print(listHovertext)
            
            #extraction der id aus Liste
            new_list = [list[0] for list in listHovertext]
            
            #print(new_list)
            df = pd.DataFrame(data)
            #print(df)
            #df.info()
            
            #Filtern der ausgewählten ID aus Dataframe
            boolean_series = df.id.isin(new_list)
            filtered_df = df[boolean_series]
            #print(filtered_df)
            #print(len(filtered_df))
          
            #dfInvasiveSpecies = excel_invasive_species()
            
            #merged_dfInvasiveSpecies = pd.merge(filtered_df['taxon.name'], dfInvasiveSpecies['Wissenschaftlicher Name'], left_on='taxon.name', right_on='Wissenschaftlicher Name')
            #print(merged_dfInvasiveSpecies.head(30))
            
            # Gruppieren und Anzahl der Beobachtungen pro invasive Spezies berechnen
            #merged_dfInvasiveSpeciesCount = merged_dfInvasiveSpecies.groupby('taxon.name').size().reset_index(name='Count Invasive Species')
            
            # Ersetzen von NaN-Werten durch 0 und Umwandeln von True/False in 1/0

            # Ersetzen von String 'false' und 'true' durch echte Boolesche Werte
            filtered_df['taxon.threatened'] = filtered_df['taxon.threatened'].replace({'true': True, 'false': False})
            filtered_df['taxon.introduced'] = filtered_df['taxon.introduced'].replace({'true': True, 'false': False})

            filtered_df['threatened_numeric'] = filtered_df['taxon.threatened'].fillna(0).astype(int)
            filtered_df['introduced_numeric'] = filtered_df['taxon.introduced'].fillna(0).astype(int)
            
            selectedDataState=filtered_df.to_dict()
            
            # Zählen, wie oft Arten als bedroht markiert sind (taxon.threatened == True)
            threatened_count = filtered_df['threatened_numeric'].sum()
                       
            
            # Zählen, wie oft der Wert "research" in der Spalte 'quality_grade' vorkommt
            research_count = (filtered_df['quality_grade'] == 'research').sum()
            
            
            # Zählen, wie oft Arten als invasive markiert sind (taxon.introduced == True)
            invasive_count = filtered_df['introduced_numeric'].sum()
            
            # Zählen der einzigartigen bedrohten Arten
            unique_threatened_species_count = filtered_df[filtered_df['threatened_numeric'] == 1]['taxon.name'].nunique()

            # Zählen der einzigartigen invasiven Arten
            unique_invasive_species_count = filtered_df[filtered_df['introduced_numeric'] == 1]['taxon.name'].nunique()
            
            
            #Anzahl der Species Bar Plot
            species_counts = df.groupby('taxon.preferred_common_name').size().reset_index(name='observation_count')
            fig_invasive_threatened_species = px.bar(species_counts, y='observation_count', x='taxon.preferred_common_name', text='observation_count')
            fig_invasive_threatened_species.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_invasive_threatened_species.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        
            
            
            
            figSpecies = px.scatter_mapbox(
                filtered_df, 
                lat="latitude", 
                lon="longitude",
                hover_name="taxon.preferred_common_name",
                hover_data=["taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
                color="taxon.preferred_common_name",
                color_continuous_scale= px.colors.cyclical.IceFire, 
                zoom=10, height=400
            )
            #figSpecies.update_layout(mapbox_style="stamen-terrain")
            figSpecies.update_layout(mapbox_style="open-street-map")
            figSpecies.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
            
            # Zählen der Beobachtungen in jeder Spezieskategorie
            iconic_taxon_counts = filtered_df['taxon.iconic_taxon_name'].value_counts()

            # Erstellen des Pie Charts
            fig_taxonCounts_qualityGrade = px.pie(iconic_taxon_counts, 
                    names=iconic_taxon_counts.index, 
                    values=iconic_taxon_counts.values, 
                    title='Verteilung Spezieskategorien',
                    labels={'names': 'Kategorie', 'values': 'Anzahl der Beobachtungen'})
            # Anpassen der Textanzeige
            fig_taxonCounts_qualityGrade.update_traces(textposition='inside', textinfo='percent+label')
            
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
            sys.stdout.write(f"[DEBUG] END   update_box_select - {end_time}\n")
            sys.stdout.flush()
        
            return html.Div([
                
              
                html.Br(),
                html.Br(),
                
                dbc.Row(
                    [
                    
                        dbc.Col(
                            [
                                dbc.Row([
                                    
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [

                                                        html.P(children=["Beobachtungen Gesamt"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[len(df)], className="card-subtitle text-n h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                        html.P(children=["Ausgewählter Bereich"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[len(filtered_df)], className="card-subtitle  h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    
                                    ]),
                                html.Br(),
                                
                                dbc.Row([
                                    
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Unterschiedliche Arten"],className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[len(species_counts)],className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    dbc.Col(
                                        [
                                            dbc.Card(
                                                dbc.CardBody(
                                                    [
                                                        #html.P(children=["Beobachtungen von invasiven Arten im ausgewählten Bereich: ",len(merged_dfInvasiveSpecies)], className="card-subtitle text-nowrap h6 text-center"),
                                                        html.P(children=["Invasive Arten"], className="card-subtitle h5 text-center"),
                                                        html.Br(),
                                                        html.P(children=[invasive_count], className="card-subtitle h5 text-center"),
                                                    ],
                                                    className="border-start border-success border-5",
                                                ),
                                                className="m-2 shadow bg-white rounded h-100 class",
                                            )
                                        ],
                                        width={"size": 6},
                                    ),
                                    
                                    
                                ]),
                                html.Br(),
                                dbc.Row(
                                    [
                                    
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Unterschiedliche invasive Arten"], className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[unique_invasive_species_count], className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Bedrohte Arten"], className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[threatened_count], className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    ],
                                ),
                                html.Br(),
                                dbc.Row(
                                    [
                                    
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Unterschiedliche bedrohte Arten"], className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[unique_threatened_species_count], className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    dbc.Col(
                                            [
                                                dbc.Card(
                                                    dbc.CardBody(
                                                        [
                                                            html.P(children=["Beobachtungen Forschungsqualität"], className="card-subtitle h5 text-center"),
                                                            html.Br(),
                                                            html.P(children=[research_count], className="card-subtitle h5 text-center"),
                                                        ],
                                                        className="border-start border-success border-5",
                                                    ),
                                                    className="m-2 shadow bg-white rounded h-100 class",
                                                )
                                            ],
                                            width={"size": 6},
                                        ),
                                    ],
                                ),
                                
                                        
                            ], 
                            width={"size": 4},
                            className = "h-100 class",
                        
                    ),
                    
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Verteilung Beobachtung Qualitätsgrad/Spezieskategorien ", className="card-title text-center"),
                                        
                                        html.Br(),
                                        dcc.Dropdown(
                                            id="dropdown_taxonCounts_qualityGrade",
                                            options=['Qualitätsgrad', 'Spezieskategorien'],
                                            value='Spezieskategorien',
                                        ),
                                        html.Br(),
                                        dcc.Graph(id='taxonCounts_qualityGrade', figure = fig_taxonCounts_qualityGrade),
                                        #html.Br(),                                       
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                                ),
                                className="m-3 shadow bg-white rounded h-100 class",
                            ),                     
                        ], width={"size": 4}
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Geografische Übersicht Arten", className="card-title text-center"),
                                        html.Br(),
                                        dcc.Dropdown(
                                            id="dropdown_map_invasive_threatened_species",
                                            options=['Übersicht Arten', 'Invasive Arten', 'Bedrohte Arten'],
                                            value='Übersicht Arten',
                                        ), 
                                        html.Br(),                        
                                        dcc.Graph(id='map_invasive_threatened_species', figure = figSpecies),
                                        #html.Br()
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                                ),
                                className="m-3 shadow bg-white rounded h-100 class",
                            ),                     
                        ], 
                        width={"size":4}
                    ),
                ]),
                
                html.Br(),
                html.Br(),
                ######
                dbc.Row(
                    [
                    dbc.Col(
                        [
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Übersicht Beobachtungen", className="card-title text-center"),
                                        html.Br(),
                                        
                                        dcc.Dropdown(
                                            id="dropdown_invasive_threatened_species",
                                            options=['Übersicht Anzahl Arten', 'Invasive Arten', 'Bedrohte Arten'],
                                            value='Übersicht Anzahl Arten',
                                        ),
                                        dcc.Graph(id='invasive_threatened_species', figure = fig_invasive_threatened_species),
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                                ),
                                className="m-3 shadow bg-white rounded h-100 class",
                            ),                     
    
                            
                        ], 
                        width={"size": 12})
                    ]
                ),  
                
                #html.H5(filename),
                #html.H6(datetime.datetime.fromtimestamp(date)),
                

                #html.Hr(),
                html.Br(),
                html.Br(),
                dbc.Row([
                    dbc.Col([
                        
                         dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5("Tabelle Beobachtungen", className="card-title text-center"),
                                        html.Br(),
                                        dash_table.DataTable(
                                            species_counts.to_dict('records'),
                                            [{'name': i, 'id': i} for i in species_counts.columns],
                                            #page_size=10,
                                            filter_action="native",
                                            sort_action="native",
                                            sort_mode="single",
                                            column_selectable="single",
                                            fixed_rows={'headers': True},
                                            style_table={'margin': '10px', 'height': '350px'},
                                            style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 30, 'maxWidth': 50, 'width': 50}
                                        ),
                                        
                                    ],
                                     className="border-start border-success border-5",
                                    
                            ),
                            className="m-3 shadow bg-white rounded h-100 class",
                    ),  
                        
                       
                    ], width=12)
                ]),
                html.Br(),
                html.Br(),  
            ]), selectedDataState
        except Exception as e:
            print(e)
            
####################################################################################################################################

@callback(
    Output('taxonCounts_qualityGrade', 'figure'),
    Input('dropdown_taxonCounts_qualityGrade', 'value'),
    Input('selectedData-State', 'selectedDataState'),
    prevent_initial_call=True
    
)
def update_taxonCounts_qualityGrade(value, selectedDataState):
    
    df = pd.DataFrame(selectedDataState)
      
    if value == 'Qualitätsgrad':
        
        # Zählen der Qualitätsgrade
        quality_counts = df['quality_grade'].value_counts()

        # Visualisierung erstellen
        fig_taxonCounts_qualityGrade = px.pie(quality_counts, 
            names=quality_counts.index, 
            values=quality_counts.values, 
            title='Verteilung der Qualität der Beobachtungen',
            hover_data=[quality_counts.values])  # Fügt zusätzliche Daten zum Hover-Text hinzu
            # Anpassen der Textanzeige
        fig_taxonCounts_qualityGrade.update_traces(textposition='inside', textinfo='percent+label')
        return fig_taxonCounts_qualityGrade
    elif value == 'Spezieskategorien':
        
        # Zählen der Beobachtungen in jeder Spezieskategorie
        iconic_taxon_counts = df['taxon.iconic_taxon_name'].value_counts()

        # Erstellen des Pie Charts
        fig_taxonCounts_qualityGrade = px.pie(iconic_taxon_counts, 
                    names=iconic_taxon_counts.index, 
                    values=iconic_taxon_counts.values, 
                    title='Verteilung Spezieskategorien',
                    labels={'names': 'Kategorie', 'values': 'Anzahl der Beobachtungen'})
        # Anpassen der Textanzeige
        fig_taxonCounts_qualityGrade.update_traces(textposition='inside', textinfo='percent+label')
        
   
        return fig_taxonCounts_qualityGrade
    
    return dash.no_update

########################################################################################################################

@callback(
    Output('invasive_threatened_species', 'figure'),
    Input('dropdown_invasive_threatened_species', 'value'),
    Input('selectedData-State', 'selectedDataState'),
    prevent_initial_call=True
    
)
def update_invasive_threatened_species(value, selectedDataState):
    
    df = pd.DataFrame(selectedDataState)
    
    # Zählen, wie oft jede Art als bedroht, invasiv oder einheimisch markiert wurde
    grouped_df = df.groupby('taxon.name').agg({
        'threatened_numeric': 'sum',
        'introduced_numeric': 'sum',
    }).reset_index()
      
    if value == 'Bedrohte Arten':
        
        # Balkendiagramm für bedrohte Arten
        fig_invasive_threatened_species = px.bar(grouped_df, 
            x='taxon.name', 
            y='threatened_numeric', 
            title='Anzahl bedrohter Arten',
            labels={'taxon.threatened': 'Anzahl', 'taxon.name': 'Art'})
        
        return fig_invasive_threatened_species
    
    elif value == 'Invasive Arten':
        
        # Balkendiagramm für invasive Arten
        fig_invasive_threatened_species = px.bar(grouped_df, 
            x='taxon.name', 
            y='introduced_numeric', 
            title='Anzahl invasiver Arten',
            labels={'taxon.introduced': 'Anzahl', 'taxon.name': 'Art'})
        
       
        return fig_invasive_threatened_species
    
    elif value == 'Übersicht Anzahl Arten':
        
        species_counts = df.groupby('taxon.preferred_common_name').size().reset_index(name='observation_count')
        fig_invasive_threatened_species = px.bar(species_counts, y='observation_count', x='taxon.preferred_common_name', text='observation_count')
        fig_invasive_threatened_species.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_invasive_threatened_species.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        
   
        return fig_invasive_threatened_species
    
    return dash.no_update
############################################################################################################################################
@callback(
    Output('map_invasive_threatened_species', 'figure'),
    Input('dropdown_map_invasive_threatened_species', 'value'),
    Input('selectedData-State', 'selectedDataState'),
    prevent_initial_call=True
    
)
def update_map_overview_invasive_threatened_species(value, selectedDataState):

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] START update_map_overview_invasive_threatened_species - {start_time}\n")
    sys.stdout.flush()
 
    df = pd.DataFrame(selectedDataState)
    
    # Zählen, wie oft jede Art als bedroht, invasiv oder einheimisch markiert wurde
   
    if value != '':
        
        if value == 'Bedrohte Arten':
            #Filter threatened Species
            threatened_df = df[df['threatened_numeric'] == 1]
            df = threatened_df.copy()
            
        elif value == 'Invasive Arten':
        
            invasive_df = df[df['introduced_numeric'] == 1]
            df = invasive_df.copy()
       
        elif value == 'Übersicht Arten':
            
            print("")
        
        figSpecies = px.scatter_mapbox(
                df, 
                lat="latitude", 
                lon="longitude",
                hover_name="taxon.preferred_common_name",
                hover_data=["taxon.preferred_common_name", "time_observed_at", "place_guess", 'quality_grade'],
                color="taxon.preferred_common_name",
                color_continuous_scale= px.colors.cyclical.IceFire, 
                zoom=10, height=400
            )
            #figSpecies.update_layout(mapbox_style="stamen-terrain")
        figSpecies.update_layout(mapbox_style="open-street-map")
        figSpecies.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
        sys.stdout.write(f"[DEBUG] END   update_map_overview_invasive_threatened_species - {end_time}\n")
        sys.stdout.flush()
   
        return figSpecies

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Print message and time using
    sys.stdout.write(f"[DEBUG] END   update_map_overview_invasive_threatened_species - {end_time}\n")
    sys.stdout.flush()

    return dash.no_update
