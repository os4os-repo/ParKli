import base64
import datetime
from datetime import date

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

import csv

import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go
import sys
import json
from pandas import json_normalize

import configparser
from configparser import ConfigParser
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, update, text
from sqlalchemy.types import Integer, Text, String, Float
from sqlalchemy.dialects.postgresql import insert as pg_insert
import psycopg2
import psycopg2.extras as extras
import time

import warnings
warnings.filterwarnings('ignore')


dash.register_page(__name__,
                   path='/Stadt',  # represents the url text
                   name='Stadt',  # name of page, commonly used as name of link
                   title='ParKli Stadt'  # epresents the title of browser's tab
)

####################################################################################################################################

# Funktion zum Lesen der Datenbankverbindung aus einer Ini-Datei
def database_connection():
    sys.stdout.write('GreenSpaceHack - DB Connect\n')
    sys.stdout.flush()

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
    #db_params = config['database']

    dbname = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOSTNAME']
    port = os.environ['POSTGRES_PORT']
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

    engine = create_engine(connection_string)
    return engine



# Funktion zum Abrufen der Daten aus der Datenbank
def fetch_data_from_db(engine):
    query = text('SELECT * FROM "greenSpaceHack"')
    return pd.read_sql(query, engine)


def fetch_data(engine, table_name):
    with engine.connect() as connection:
        count_query = text(f'SELECT COUNT(*) FROM "{table_name}"')
        count_result = connection.execute(count_query).scalar()
        if count_result > 0:
            query = text(f'SELECT * FROM "{table_name}"')
            df = pd.read_sql(query, connection)
            return df
        else:
            return None




# Funktion zum Einfügen oder Aktualisieren der Daten in der Datenbank
def upsert_data_to_db(df, engine):
    metadata = MetaData()
    inspector = inspect(engine)

    if not inspector.has_table('greenSpaceHack'):
        df.to_sql('greenSpaceHack', engine, if_exists='replace', index=False)
        print(f"Tabelle 'greenSpaceHack' erstellt und Daten eingefügt.")
    else:
        with engine.connect() as connection:
            count_query = text('SELECT COUNT(*) FROM "greenSpaceHack"')
            count_result = connection.execute(count_query).scalar()
            if count_result == 0:
                df.to_sql('greenSpaceHack', engine, if_exists='append', index=False)
                print(f"Daten in die bestehende leere Tabelle 'greenSpaceHack' eingefügt.")
            else:
                primary_key_column = 'id'
                existing_ids_query = text(f'SELECT {primary_key_column} FROM "greenSpaceHack"')
                existing_ids_result = connection.execute(existing_ids_query)
                existing_ids = {row[0] for row in existing_ids_result}

                new_data = df[~df[primary_key_column].isin(existing_ids)]

                if not new_data.empty:
                    new_data.to_sql('greenSpaceHack', engine, if_exists='append', index=False)
                    print(f"Neue Daten für Tabelle 'greenSpaceHack' hinzugefügt.")


def upsert_data_to_db(df, engine, table_name):
    metadata = MetaData()
    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"Tabelle '{table_name}' erstellt und Daten eingefügt.")
    else:
        with engine.connect() as connection:
            count_query = text(f'SELECT COUNT(*) FROM "{table_name}"')
            count_result = connection.execute(count_query).scalar()
            if count_result == 0:
                df.to_sql(table_name, engine, if_exists='append', index=False)
                print(f"Daten in die bestehende leere Tabelle '{table_name}' eingefügt.")
            else:
                primary_key_column = 'id'
                existing_ids_query = text(f'SELECT {primary_key_column} FROM "{table_name}"')
                existing_ids_result = connection.execute(existing_ids_query)
                existing_ids = {row[0] for row in existing_ids_result}

                new_data = df[~df[primary_key_column].isin(existing_ids)]

                if not new_data.empty:
                    new_data.to_sql(table_name, engine, if_exists='append', index=False)
                    print(f"Neue Daten für Tabelle '{table_name}' hinzugefügt.")


####################################################################################################################################

 

try:
    #Herunterladen der Daten von greenspacehack.com
    api_url = "https://greenspacehack.org/data/full.geojson"
    response = requests.get(api_url)
    response.raise_for_status()
    #cast to json
    data = response.json()

    #Extratktion von Key Value in Dataframe
    df = pd.json_normalize(data, record_path =['features'])
    #Löschen des zweiten Key type 
    df = df.drop('type', axis=1)
    #löschen des Wortes properties vor den Spaltennamen
    df = df.rename(columns=lambda x: x.split('.')[1])
    #Spliten von Längen- und Breitengrad in einzelne Spalten 
    df[['location.0', 'location.1']] = df['coordinates'].apply(lambda x: pd.Series(x))

    engine = database_connection()
    upsert_data_to_db(df, engine, "greenSpaceHack")

except requests.RequestException as e:
    print(f"Daten konnten nicht heruntergeladen werden: {e}")
    engine = database_connection()
    df = fetch_data_from_db(engine)
    if df is not None:
        print("Daten erfolgreich aus der Datenbank abgerufen.")
    else:
        print("Keine Daten in der Datenbank vorhanden.")



df.head()

# Anzahl Fragebögen
sys.stdout.write('Test123')

print(len(df))

dfkurzerFragebogen = df[~(df['S3'].isna()) | ~(df['S4'].isna())| ~(df['S5'].isna()) | ~(df['S6'].isna()) | ~(df['S7'].isna()) | ~(df['S8'].isna()) | ~(df['S9'].isna())]
len(dfkurzerFragebogen)

dfLangerFrageBogen = df[(df['S3'].isna()) & (df['S4'].isna()) & (df['S5'].isna()) & (df['S6'].isna()) & (df['S7'].isna()) & (df['S8'].isna()) & (df['S9'].isna())]
print(len(dfLangerFrageBogen))

countLangeFrageBogen=len(dfLangerFrageBogen)
# Lösche alle Zeilen, die ein ";" in irgendeiner Spalte enthalten
dfLangerFrageBogen = dfLangerFrageBogen[~dfLangerFrageBogen.apply(lambda row: row.astype(str).str.contains(';').any(), axis=1)]

len(dfLangerFrageBogen)

#Löschen aller NaN in AC1, AC5 und AC10 sonst können nachfolgende Operationen die Identifikation von ; in Daten nicht erfolgen
dfLangerFrageBogen = dfLangerFrageBogen.dropna(subset=['AC1', 'AC5', 'AC10'])
print(len(dfLangerFrageBogen))

#dfLangerFrageBogen = dfLangerFrageBogen.replace({'AC5':{'Poor':0.0,'Schlecht':0.0,'Ausreichend':1.0,'Adequate':1.0,'Gut':2.0,'Good':2.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'Keine (habe keine erwartet)':1.0,'None_NOT_expected':1.0}, 'AC10':{'Poor':0.0,'Schlecht':0.0,'Ausreichend':1.0,'Adequate':1.0,'Gut':2.0,'Good':2.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'Keine (habe keine erwartet)':0.0,'None_NOT_expected':1.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AC1':{'1-3':1.0, '4-7':2.0, '>8 or open access':3.0},'AC5':{'Poor':0.0,'Schlecht':0.0,'Ausreichend':1.0,'Adequate':1.0,'Gut':2.0,'Good':2.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0, 'None expected':0.0,'Keine (habe keine erwartet)':1.0,'None_NOT_expected':1.0, 'None NOT expected':1.0}, 'AC10':{'Poor':0.0,'Schlecht':0.0,'Ausreichend':1.0,'Adequate':1.0,'Gut':2.0,'Good':2.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0, 'None expected':0.0, 'Keine (habe keine erwartet)':0.0,'None_NOT_expected':1.0,'None NOT expected':1.0,"None (didn't expect any)":1.0}})

#Zu einem spätern Zeitpunkt bei der Entwicklung der App werden die Werte 1 oder 2 oder 3 in das df geschrieben
#diese sind vom Type Object; daher cast aller Werte in float 

dfLangerFrageBogen['AC1'] = dfLangerFrageBogen['AC1'].astype(float)

#Filtern der Werte durch Verwendung der erwarteten Werte
dfLangerFrageBogen=dfLangerFrageBogen.loc[(dfLangerFrageBogen['AC1'] == 1.0) | (dfLangerFrageBogen['AC1']== 2.0) | (dfLangerFrageBogen['AC1']==3.0)]
dfLangerFrageBogen=dfLangerFrageBogen.loc[(dfLangerFrageBogen['AC5'] == 1.0) | (dfLangerFrageBogen['AC5']==2.0) | (dfLangerFrageBogen['AC5']==3.0) | (dfLangerFrageBogen['AC5']==0.0)]
dfLangerFrageBogen=dfLangerFrageBogen.loc[(dfLangerFrageBogen['AC10'] == 1.0) | (dfLangerFrageBogen['AC10']==2.0) | (dfLangerFrageBogen['AC10']==3.0) | (dfLangerFrageBogen['AC10']==0.0)]
len(dfLangerFrageBogen)

dfLangerFrageBogen= dfLangerFrageBogen.eval('AC_SCR_sum = AC1 + AC5 + AC10')
dfLangerFrageBogen[['AC1', 'AC5', 'AC10', 'AC_SCR_sum']].head()

#Zur Vergrößerung des Datensample werden "NaN" in "Yes" und "No" Antworten überführt.
#Wenn R1Q beantwortet wurde wird R1P auf "Yes" gesetzt, R1Q Folgefrage von R1P 
#Folgefrage R1Q kann einen "NaN" Wert annehmen wenn R1P mit "No" beantwortet wurde
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R1P'].isnull()) & (dfLangerFrageBogen['R1Q'].isnull()), 'R1P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R1P'].isnull()) & ~(dfLangerFrageBogen['R1Q'].isnull()), 'R1P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R1P'] == 'No') & (dfLangerFrageBogen['R1Q'].isnull()), 'R1Q'] = 0.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R1P':{'Yes':1.0,'No':0.0}, 'R1Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})
dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR1 = R1Q')
dfLangerFrageBogen[['R1P', 'R1Q', 'summeR1']].head()


dfLangerFrageBogen.loc[(dfLangerFrageBogen['R2P'].isnull()) & (dfLangerFrageBogen['R2Q'].isnull()), 'R2P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R2P'].isnull()) & ~(dfLangerFrageBogen['R2Q'].isnull()), 'R2P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R2P'] == 'No') & (dfLangerFrageBogen['R2Q'].isnull()), 'R2Q'] = 0.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R2P':{'Yes':1.0,'No':0.0}, 'R2Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})
dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR2 = R2Q')
dfLangerFrageBogen[['R2P', 'R2Q', 'summeR2']].head()

dfLangerFrageBogen.loc[(dfLangerFrageBogen['R3P'].isnull()) & (dfLangerFrageBogen['R3Q'].isnull()), 'R3P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R3P'].isnull()) & ~(dfLangerFrageBogen['R3Q'].isnull()), 'R3P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R3P'] == 'No') & (dfLangerFrageBogen['R3Q'].isnull()), 'R3Q'] = 0.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R3P':{'Yes':1.0,'No':0.0}, 'R3Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})
dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR3 = R3Q')


dfLangerFrageBogen.loc[(dfLangerFrageBogen['R4P'].isnull()) & (dfLangerFrageBogen['R4Q'].isnull()), 'R4P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R4P'].isnull()) & ~(dfLangerFrageBogen['R4Q'].isnull()), 'R4P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R4P'] == 'No') & (dfLangerFrageBogen['R4Q'].isnull()), 'R4Q'] = 0.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R4P':{'Yes':1.0,'No':0.0}, 'R4Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})
dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR4 = R4Q')

dfLangerFrageBogen.loc[(dfLangerFrageBogen['R5P'].isnull()) & (dfLangerFrageBogen['R5Q'].isnull()), 'R5P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R5P'].isnull()) & ~(dfLangerFrageBogen['R5Q'].isnull()), 'R5P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R5P'] == 'No') & (dfLangerFrageBogen['R5Q'].isnull()), 'R5Q'] = 0.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R5P':{'Yes':1.0,'No':0.0}, 'R5Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})

#Filtern der Werte durch Verwendung der erwarteten Werte
dfLangerFrageBogen =dfLangerFrageBogen[(((dfLangerFrageBogen['R5P'] == 0.0) | (dfLangerFrageBogen['R5P']== 1.0)) & ((dfLangerFrageBogen['R5Q']==0.0)| (dfLangerFrageBogen['R5Q']==2.0) | (dfLangerFrageBogen['R5Q']==4.0) | (dfLangerFrageBogen['R5Q']==6.0)))]

dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR5 = R5Q')

dfLangerFrageBogen.loc[(dfLangerFrageBogen['R6P'].isnull()) & (dfLangerFrageBogen['R6Q'].isnull()), 'R6P'] = 'No'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R6P'].isnull()) & ~(dfLangerFrageBogen['R6Q'].isnull()), 'R6P'] = 'Yes'
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R6P'] == 'No') & (dfLangerFrageBogen['R6Q'].isnull()), 'R6Q'] = 0.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['R6P'] == 'Yes') &  ~(dfLangerFrageBogen['R6Q'].isnull()), 'R6Q'] = 2.0
dfLangerFrageBogen = dfLangerFrageBogen.replace({'R6P':{'Yes':1.0,'No':0.0}, 'R6Q':{'Poor':2.0,'Schlecht':2.0,'Ausreichend':4.0,'Adequate':4.0,'Gut':6.0,'Good':6.0}})
#Ein Wert mit R6P Yes und anschließend NaN daher keine Logik

dfLangerFrageBogen['R6Q'] = dfLangerFrageBogen['R6Q'].astype(float)

#Filtern der Werte durch Verwendung der erwarteten Werte
dfLangerFrageBogen =dfLangerFrageBogen[(((dfLangerFrageBogen['R6P'] == 0.0) | (dfLangerFrageBogen['R6P']== 1.0)) & ((dfLangerFrageBogen['R6Q']==0.0)| (dfLangerFrageBogen['R6Q']==2.0) | (dfLangerFrageBogen['R6Q']==4.0) | (dfLangerFrageBogen['R6Q']==6.0)))]
print(len(dfLangerFrageBogen))

dfLangerFrageBogen= dfLangerFrageBogen.eval('summeR6 = R6Q')

dfLangerFrageBogen= dfLangerFrageBogen.eval('R_SCR_sum = summeR1 + summeR2 + summeR3+ summeR5 + summeR6')   
dfLangerFrageBogen[['R_SCR_sum', 'summeR1', 'summeR2', 'summeR3', 'summeR5', 'summeR6']].head()

dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM1':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM2':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM3':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM4':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM5':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM6':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
#AM7 nicht in NEST Score 
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM7':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM9':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})
dfLangerFrageBogen = dfLangerFrageBogen.replace({'AM10':{'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0,'Keine (habe aber welche erwartet)':0.0,'None_expected':0.0,'None expected':0.0,'Keine (habe keine erwartet)':2.0,'None_NOT_expected':2.0,'None NOT expected':2.0,'None (but expected some)':0.0,"None (didn't expect any)":2.0}})

dfLangerFrageBogen[['AM1','AM2','AM3', 'AM4', 'AM5', 'AM6', 'AM9', 'AM10']] = dfLangerFrageBogen[['AM1','AM2','AM3', 'AM4', 'AM5', 'AM6', 'AM9', 'AM10']].fillna(0)

dfLangerFrageBogen= dfLangerFrageBogen.eval('AM_SCR_sum = AM1 + AM2 + AM3 + AM4 + AM5 + AM6+ AM9 + AM10')
dfLangerFrageBogen [['AM1','AM2','AM3','AM4','AM5','AM6','AM9','AM10', 'AM_SCR_sum']].head()

dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'] == 'Yes') & (dfLangerFrageBogen['NA6b'] == 'Yes' ), 'summeNA6aNA6b'] = 3.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'] == 'Yes') & (dfLangerFrageBogen['NA6b'] == 'No' ), 'summeNA6aNA6b'] = 2.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'] == 'Yes') & (dfLangerFrageBogen['NA6b'].isnull()), 'summeNA6aNA6b'] = 2.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'] == 'No') & (dfLangerFrageBogen['NA6b'] == 'Yes' ), 'summeNA6aNA6b'] = 2.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'].isnull()) & (dfLangerFrageBogen['NA6b']== 'Yes' ), 'summeNA6aNA6b'] = 2.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'] == 'No') & (dfLangerFrageBogen['NA6b'] == 'No' ), 'summeNA6aNA6b'] = 0.0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NA6a'].isnull()) & (dfLangerFrageBogen['NA6b'].isnull()), 'summeNA6aNA6b'] = 0.0

dfLangerFrageBogen = dfLangerFrageBogen.replace({'NA7':{'None':0.0, 'Keine':0.0, 'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0}, 
                                                 'NA8':{'None':0.0, 'Keine':0.0, 'Poor':1.0,'Schlecht':1.0,'Ausreichend':2.0,'Adequate':2.0,'Gut':3.0,'Good':3.0}})


dfLangerFrageBogen= dfLangerFrageBogen.eval('NA_SCR_sum = summeNA6aNA6b + NA7+ NA8')
dfLangerFrageBogen[['summeNA6aNA6b','NA7', 'NA8', 'NA_SCR_sum']].head()


# Zuerst ersetzen wir leere Listen durch leere Strings, um sie später korrekt zu zählen
dfLangerFrageBogen['NN1b'] = df['NN1b'].apply(lambda x: '' if isinstance(x, list) and len(x) == 0 else x)

dfLangerFrageBogen['NN_SCR_sum'] = dfLangerFrageBogen['NN1b'].apply(lambda x: len(x) if isinstance(x, list) else len(str(x).split(',')))

dfLangerFrageBogen.loc[(dfLangerFrageBogen['NN1a'].isnull()) | (dfLangerFrageBogen['NN1a']== 'No' ), 'NN_SCR_sum'] = 0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NN1b'].isnull()),'NN_SCR_sum'] = 0
dfLangerFrageBogen.loc[(dfLangerFrageBogen['NN_SCR_sum'] > 3),'NN_SCR_sum'] = 3


# Mapping-Dictionary für die Prozentangaben
percentage_mapping_NA2b = {
    '0': 0,
    '<25%': 1,
    '26-50%': 2,
    '51-75%': 3
}

dfLangerFrageBogen['NA2b'] = dfLangerFrageBogen['NA2b'].apply(lambda x: percentage_mapping_NA2b[x] if x in percentage_mapping_NA2b else x)

# Mapping-Dictionary für die Prozentangaben
percentage_mapping_NA5 = {
    '0': 0,
    '1-10%': 0.75,
    '11-25%': 1.5,
    '25-50%': 2.25,
    '>50%': 3.0
}

dfLangerFrageBogen['NA5'] = dfLangerFrageBogen['NA5'].apply(lambda x: percentage_mapping_NA5[x] if x in percentage_mapping_NA5 else x)

dfLangerFrageBogen['NA2b'] = dfLangerFrageBogen['NA2b'].astype(float)

dfLangerFrageBogen['NA5'] = dfLangerFrageBogen['NA5'].astype(float)

dfLangerFrageBogen[['NA2b', 'NA4', 'NA5']] = dfLangerFrageBogen[['NA2b', 'NA4', 'NA5']].fillna(0.0) 

dfLangerFrageBogen.loc[dfLangerFrageBogen['NA2b'] == 3.0, 'SIG_NAT_FEATwat'] = 1.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA2b'] < 3.0, 'SIG_NAT_FEATwat'] = 0.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA4'] == 'Yes', 'SIG_NAT_FEATview'] = 1.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA4'] == 'No', 'SIG_NAT_FEATview'] = 0.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA4'] == 0.0, 'SIG_NAT_FEATview'] = 0.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA4'].isnull(), 'SIG_NAT_FEATview'] = 0.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA5'] >= 3.0, 'SIG_NAT_FEATtree'] = 1.0
dfLangerFrageBogen.loc[dfLangerFrageBogen['NA5'] < 3.0, 'SIG_NAT_FEATtree'] = 0.0

dfLangerFrageBogen= dfLangerFrageBogen.eval('NAsig_SCR_sum =  SIG_NAT_FEATtree + SIG_NAT_FEATview + SIG_NAT_FEATwat')


dfLangerFrageBogen[['NA2b', 'SIG_NAT_FEATwat', 'NA4', 'SIG_NAT_FEATview', 'NA5', 'SIG_NAT_FEATtree', 'NAsig_SCR_sum']].head()


dfLangerFrageBogen = dfLangerFrageBogen.replace({'IN1':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0, 'Widely spread':0.0}, 
                                                 'IN2':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0, 'Widely spread':0.0},
                                                 'IN3':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0},
                                                 'IN4':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0},
                                                 'IN5':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0},
                                                 'IN6':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0},
                                                 'IN7':{'None':2.0, 'Keine':2.0, 'In specific locations':2.0, 'Clustered':2.0, 'An bestimmten Orten':2.0,'Verbreitet':1.0,'Spread':1.0,'Weit verbreitet':0.0,'Widely Spread':0.0},
                                                 'IN8':{'None':0.0, 'Keine':0.0, 'Kaum bemerkbar':2.0,'Hardly noticeable':2.0,'Bemerkbar':1.0,'Noticeable':1.0,'Sehr bemerkbar':0.0,'Very noticeable':0.0},
                                                 'IN9':{'None':0.0, 'Keine':0.0, 'Kaum bemerkbar':2.0,'Hardly noticeable':2.0,'Bemerkbar':1.0,'Noticeable':1.0,'Sehr bemerkbar':0.0,'Very noticeable':0.0}})


# Liste der ausgewählten Spalten, für die die NaN-Werte in 0 umgewandelt werden sollen
selected_columns = ['IN1', 'IN2', 'IN3', 'IN4', 'IN5', 'IN6', 'IN7', 'IN8', 'IN9']

# Wandle NaN-Werte in 0 um für die ausgewählten Spalten
dfLangerFrageBogen[selected_columns] = dfLangerFrageBogen[selected_columns].fillna(0)


dfLangerFrageBogen= dfLangerFrageBogen.eval('IN_SCR_sum =  IN1 + IN2 + IN3 + IN4 + IN5 + IN6 + IN7 +IN8 + IN9')
dfLangerFrageBogen[['IN1', 'IN2', 'IN3', 'IN4', 'IN5', 'IN6', 'IN7', 'IN8', 'IN9', 'IN_SCR_sum']].head()

dfLangerFrageBogen = dfLangerFrageBogen.replace({'US1':{' Einigermaßen geeignet': 'Einigermaßen geeignet'}, 
                                                 'US2':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US3':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US4':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US6':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US7':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US8':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US9':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US10':{' Einigermaßen geeignet': 'Einigermaßen geeignet'},
                                                 'US11':{' Einigermaßen geeignet': 'Einigermaßen geeignet'}})



dfLangerFrageBogen = dfLangerFrageBogen.replace({'US1':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0}, 
                                                 'US2':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US3':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US4':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US6':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US7':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0, 'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US8':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0,'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US9':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0,'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US10':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0,'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0},
                                                 'US11':{'Nicht geeignet':0.0, 'Not suitable':0.0, 'Not':0.0, 'Einigermaßen geeignet':1.0,'Somewhat suitable':1.0,'Somewhat':1.0, 'Geeignet':2.0,'Suitable':2.0,'Sehr geeignet':3.0,'Very suitable':3.0, 'Very Suitable':3.0}})



# Lösche alle Zeilen, in denen in den ausgewählten Spalten 5 oder mehr NaN-Werte vorhanden sind
selected_columns = ['US1', 'US2', 'US3', 'US4', 'US6', 'US7', 'US8', 'US9', 'US10', 'US11']
dfLangerFrageBogen.dropna(subset=selected_columns, thresh=8, inplace=True)

dfLangerFrageBogen[selected_columns] = dfLangerFrageBogen[selected_columns].fillna(0)

dfLangerFrageBogen= dfLangerFrageBogen.eval('US_SCR_sum = US1 + US2 + US3 + US4 + US6 + US7 + US8 + US9 + US10 + US11')
dfLangerFrageBogen[['US1', 'US2', 'US3', 'US4', 'US6', 'US7', 'US8', 'US9', 'US10', 'US11', 'US_SCR_sum']].head()

#reenSpaceHack-Data = dfLangerFrageBogen.to_dict('records')

# 3. Calculate domain scores out of 100

dfLangerFrageBogen= dfLangerFrageBogen.eval('AC_WT = (AC_SCR_sum/9) *100')
dfLangerFrageBogen[['AC_SCR_sum','AC_WT']].head()


dfLangerFrageBogen= dfLangerFrageBogen.eval('R_WT = (R_SCR_sum/36) *100')
dfLangerFrageBogen[['R_SCR_sum','R_WT']].head()

dfLangerFrageBogen= dfLangerFrageBogen.eval('AM_WT = (AM_SCR_sum/24)*100')
dfLangerFrageBogen[['AM_SCR_sum','AM_WT']].head()

dfLangerFrageBogen= dfLangerFrageBogen.eval('NA_WT = (NA_SCR_sum/9)*100')
dfLangerFrageBogen[['NA_SCR_sum','NA_WT']].head()

dfLangerFrageBogen['NN_SCR_sum'] = dfLangerFrageBogen['NN_SCR_sum'].astype(float)
dfLangerFrageBogen= dfLangerFrageBogen.eval('NN_WT = (NN_SCR_sum/3)*100')
dfLangerFrageBogen[['NN_SCR_sum','NN_WT']].head()


dfLangerFrageBogen= dfLangerFrageBogen.eval('IN_WT = (IN_SCR_sum/18)*100')
dfLangerFrageBogen[['IN_SCR_sum','NA_WT']].head()


dfLangerFrageBogen= dfLangerFrageBogen.eval('NAsig_WT = (NAsig_SCR_sum/3)*100')
dfLangerFrageBogen[['NAsig_SCR_sum','NAsig_WT']].head()

dfLangerFrageBogen= dfLangerFrageBogen.eval('US_WT = (US_SCR_sum/30)*100')
dfLangerFrageBogen[['US_SCR_sum','US_WT']].head()

# Mapping-Dictionary für die Zahlenwerte zu den Strings
mapping_dict_gstypology = {
    'Urban park': 1,
    'Semi-natural/natural': 2,
    'Formal recreation': 3,
    'Civic space': 4,
    'Functional/amenity': 5,
    'Natural/green corridor': 6,
    'Woodlands/forest': 7,
    'Country park': 8,
    'Lake/reservoir/pond': 9,
    'Lake/ reservoir/ pond':9,
    'River/stream/canal (linear)': 10,
    'Marine/ coastal' : 11
}

# Wandle die Zahlenwerte in der Spalte "gstypology" in ihren entsprechenden String-Wert um
dfLangerFrageBogen['gstypology'] = dfLangerFrageBogen['gstypology'].replace(mapping_dict_gstypology)
#dfLangerFrageBogen[['gstypology']].head(60)

dfLangerFrageBogen['gstypology'] = dfLangerFrageBogen['gstypology'].astype(int)

dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 1, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.12)+(dfLangerFrageBogen.R_WT*0.22)+(dfLangerFrageBogen.AM_WT*0.13)+(dfLangerFrageBogen.NA_WT*0.12)+(dfLangerFrageBogen.NN_WT*0.20)+(dfLangerFrageBogen.IN_WT*0.11)+(dfLangerFrageBogen.NAsig_WT*0.09))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 2, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.16)+(dfLangerFrageBogen.R_WT*0.06)+(dfLangerFrageBogen.AM_WT*0.08)+(dfLangerFrageBogen.NA_WT*0.17)+(dfLangerFrageBogen.NN_WT*0.21)+(dfLangerFrageBogen.IN_WT*0.16)+(dfLangerFrageBogen.NAsig_WT*0.15))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 3, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.12)+(dfLangerFrageBogen.R_WT*0.33)+(dfLangerFrageBogen.AM_WT*0.19)+(dfLangerFrageBogen.NA_WT*0.14)+(dfLangerFrageBogen.NN_WT*0.02)+(dfLangerFrageBogen.IN_WT*0.13)+(dfLangerFrageBogen.NAsig_WT*0.06))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 4, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.13)+(dfLangerFrageBogen.R_WT*0.20)+(dfLangerFrageBogen.AM_WT*0.15)+(dfLangerFrageBogen.NA_WT*0.12)+(dfLangerFrageBogen.NN_WT*0.16)+(dfLangerFrageBogen.IN_WT*0.15)+(dfLangerFrageBogen.NAsig_WT*0.09))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 5, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.14)+(dfLangerFrageBogen.R_WT*0.12)+(dfLangerFrageBogen.AM_WT*0.12)+(dfLangerFrageBogen.NA_WT*0.15)+(dfLangerFrageBogen.NN_WT*0.24)+(dfLangerFrageBogen.IN_WT*0.17)+(dfLangerFrageBogen.NAsig_WT*0.06))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 6, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.19)+(dfLangerFrageBogen.R_WT*0.12)+(dfLangerFrageBogen.AM_WT*0.14)+(dfLangerFrageBogen.NA_WT*0.15)+(dfLangerFrageBogen.NN_WT*0.03)+(dfLangerFrageBogen.IN_WT*0.21)+(dfLangerFrageBogen.NAsig_WT*0.14))                                                  
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 7, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.15)+(dfLangerFrageBogen.R_WT*0.07)+(dfLangerFrageBogen.AM_WT*0.10)+(dfLangerFrageBogen.NA_WT*0.18)+(dfLangerFrageBogen.NN_WT*0.14)+(dfLangerFrageBogen.IN_WT*0.16)+(dfLangerFrageBogen.NAsig_WT*0.21))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 8, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.10)+(dfLangerFrageBogen.R_WT*0.13)+(dfLangerFrageBogen.AM_WT*0.13)+(dfLangerFrageBogen.NA_WT*0.14)+(dfLangerFrageBogen.NN_WT*0.20)+(dfLangerFrageBogen.IN_WT*0.11)+(dfLangerFrageBogen.NAsig_WT*0.18))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 9, 'Overall NEST score']  = ((dfLangerFrageBogen.AC_WT*0.15)+(dfLangerFrageBogen.R_WT*0.00)+(dfLangerFrageBogen.AM_WT*0.25)+(dfLangerFrageBogen.NA_WT*0.24)+(dfLangerFrageBogen.NN_WT*0.00)+(dfLangerFrageBogen.IN_WT*0.17)+(dfLangerFrageBogen.NAsig_WT*0.20))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 10, 'Overall NEST score'] = ((dfLangerFrageBogen.AC_WT*0.21)+(dfLangerFrageBogen.R_WT*0.03)+(dfLangerFrageBogen.AM_WT*0.11)+(dfLangerFrageBogen.NA_WT*0.17)+(dfLangerFrageBogen.NN_WT*0.18)+(dfLangerFrageBogen.IN_WT*0.14)+(dfLangerFrageBogen.NAsig_WT*0.16))
dfLangerFrageBogen.loc[dfLangerFrageBogen['gstypology'] == 11, 'Overall NEST score'] = ((dfLangerFrageBogen.AC_WT*0.13)+(dfLangerFrageBogen.R_WT*0.19)+(dfLangerFrageBogen.AM_WT*0.17)+(dfLangerFrageBogen.NA_WT*0.05)+(dfLangerFrageBogen.NN_WT*0.13)+(dfLangerFrageBogen.IN_WT*0.12)+(dfLangerFrageBogen.NAsig_WT*0.20))


dfLangerFrageBogen['Overall NEST score'] = dfLangerFrageBogen['Overall NEST score'].round(2)

mapping_dict_gstypology3 = {
    1: 'Urban park',
    2: 'Semi-natural/natural',
    3: 'Formal recreation',
    4: 'Civic space',
    5: 'Functional/amenity',
    6: 'Natural/green corridor',
    7: 'Woodlands/forest',
    8: 'Country park',
    9: 'Lake/reservoir/pond',
    10: 'River/stream/canal (linear)',
    11: "Marine/ coastal"
}

dfLangerFrageBogen['gstypology'] = dfLangerFrageBogen['gstypology'].replace(mapping_dict_gstypology3)


#Anzahl der Typologien 
#dfGstypology = dfLangerFrageBogen.groupby(dfLangerFrageBogen['gstypology']).count()
#dfGstypology[['id']]

print(dfLangerFrageBogen.head())
print(dfLangerFrageBogen.info())

#Durschnitt NestScore pro Typologie
dfGstypology = dfLangerFrageBogen.groupby(dfLangerFrageBogen['gstypology']).mean(numeric_only=True)
dfGstypology[['Overall NEST score']]

#Alle Werte mit NEST Score DropNaN
dfLangerFrageBogenNestScore = dfLangerFrageBogen.dropna(subset=['Overall NEST score'])
dfLangerFrageBogenNestScore[['Overall NEST score']]
#dfLangerFrageBogenNestScore.to_excel("Bereinigt_GreenSpaceHack.xlsx")


#Database 
engine = database_connection()

upsert_data_to_db(dfLangerFrageBogenNestScore, engine, "greenSpaceHackCleanData")

fig = px.scatter_mapbox(dfLangerFrageBogenNestScore, 
                        lat="location.1", 
                        lon="location.0",
                        hover_name="name",
                        hover_data=['id','Overall NEST score','name', 'gstypology'],
                        color="Overall NEST score",
                        size="Overall NEST score",
                        color_continuous_scale= px.colors.cyclical.IceFire, 
                        zoom=5, height=400
                       )
#fig.update_layout(mapbox_style="stamen-terrain")
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

dfGroupBy = dfLangerFrageBogenNestScore.groupby('gstypology').count()['id']
figAnzahlFrageBogenProTypology = px.bar(dfGroupBy, height=500)


# Erstellung der Heatmap
figHeatMap = px.density_mapbox(dfLangerFrageBogenNestScore, 
                        lat="location.1", 
                        lon="location.0",
                        z="Overall NEST score", 
                        radius=10,
                        zoom=5,
                        mapbox_style="carto-positron",
                        height=400)

#figHeatMap.update_layout(mapbox_style="open-street-map")
figHeatMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

####################################################################################################################################

card_SurveyFormsTotal = dbc.Card(
    dbc.CardBody(
        [
            html.P(children=["Anzahl Fragebögen Gesamt"], className="card-subtitle h5 text-center"),
            html.Br(),
            html.P(children=[len(df)], className="card-subtitle text-n h5 text-center"),
            
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)

card_ShortSurveyFormsTotal = dbc.Card(
    dbc.CardBody(
        [
            html.P(children=["Anzahl kurze Fragebögen Gesamt"], className="card-subtitle h5 text-center"),
            html.Br(),
            html.P(children=[len(dfkurzerFragebogen)], className="card-subtitle text-n h5 text-center"),
            
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)

card_longSurveyFormsTotal = dbc.Card(
    dbc.CardBody(
        [
            html.P(children=["Anzahl langer Fragebögen Gesamt"], className="card-subtitle h5 text-center"),
            html.Br(),
            html.P(children=[countLangeFrageBogen], className="card-subtitle text-n h5 text-center"),
            
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)

card_NestScore = dbc.Card(
    dbc.CardBody(
        [
            html.P(children=["Anzahl Fragebögen NEST Score"], className="card-subtitle h5 text-center"),
            html.Br(),
            html.P(children=[len(dfLangerFrageBogenNestScore)], className="card-subtitle text-n h5 text-center"),
            
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)


card_UpdateMapScatterMapbox = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-map me-2"), "NEST Score"], className="text-nowrap text-center"),
            html.Br(),
            #html.Div(id='map'),
            
            dcc.Graph(id='scatter-mapbox',figure = fig),
                    
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)

card_BarPlot = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(id='heading_distribution_surveys_NEST',className="bi bi-reception-4 me-2"), "Verteilung Typology"], className="text-nowrap text-center"),
            html.Br(),
            #html.Div(id='map'),
            
             dcc.Dropdown(
                id="dropdown_distribution_surveys_NEST",
                    options=['Fragebögen Typology', 'Streuung NEST pro Typology'],
                    value='Fragebögen Typology',
            ), 
            html.Br(),                        
                                       
            dcc.Graph(id='graph_distribution_surveys_NEST',figure = figAnzahlFrageBogenProTypology),
                    
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)


card_HeatMap = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-reception-4 me-2"), "Heatmap NEST Score"], className=" text-center"),
            html.Br(),
            #html.Div(id='map'),
            
            dcc.Graph(id='heatMap_mapbox',figure = figHeatMap),
                    
        ],
        className="border-start border-danger border-5",
       
    ),
    className="m-2 shadow bg-white rounded h-100 class",
)





####################################################################################################################
layout = html.Div(
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
                                html.Br(), 
                                html.Img(src="./assets/ParKli_Stadt_300px.png", height="50", style={'display': 'inline-block'}),
                                html.H1("ParKli Stadt",style={'textAlign': 'center', 'color': '#2F5F53','display': 'inline-block', 'margin-left': 'auto', 'margin-right': 'auto' }),
                                        
                            ],
                            className="position-absolute top-0 start-50"
                                    
                        )
                    ], width=12
                )
                        
            ]
        ),
        
        html.Br(), 
        html.Br(),
        html.Br(), 
        html.Br(),
                

        
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                
                               card_SurveyFormsTotal, 
                            ],
                        ),
                         dbc.Row(
                            [
                                card_longSurveyFormsTotal
                                
                            ],
                        ),
                        dbc.Row(
                            [
                                card_ShortSurveyFormsTotal,
                                
                            ],
                        ), 
                          dbc.Row(
                            [
                                card_NestScore,
                                
                            ],
                        ), 
                       
                                
                    ], width={"size": 3, "offset":0}
                ),
                dbc.Col(
                    [
                        card_UpdateMapScatterMapbox,
                                
                    ], width={"size": 9}
                ),
                
                    
            ],
        ),
        
        html.Br(), 
        html.Br(),
        
        
        dbc.Row(
            [
                dbc.Col(
                    [
                        card_BarPlot, 
                        
                    ],width={"size": 6}
                    
                ),
                dbc.Col(
                    [
                        card_HeatMap, 
                        
                    ],width={"size": 6}
                    
                ),
                
                
            ],
            
        ),
              
        html.Br(),
        
        html.Div(id='nest-score-select'),
    
       
    ]
)
#####################################################################################
@callback(
    Output('graph_distribution_surveys_NEST', 'figure'),
    Input('dropdown_distribution_surveys_NEST', 'value')
)
def update_graph(value):
    if value == 'Fragebögen Typology':
        
        figAnzahlFrageBogenProTypology = px.bar(dfGroupBy, height=500)
        return figAnzahlFrageBogenProTypology
       
    elif value == 'Streuung NEST pro Typology':
        #dff = df[df.continent==value]
        #fig = px.histogram(dff, x='country', y='lifeExp', histfunc='avg')
        fig_boxplot = px.box(dfLangerFrageBogenNestScore, x='gstypology', y='Overall NEST score', title='NEST Score nach Typologie - Boxplot')
        return fig_boxplot
 
    return dash.no_update
########################################################################################################################################
@callback(
    #Output('box-select', 'children', allow_duplicate=True),
    Output('nest-score-select', 'children'),
    Output('greenSpaceHack-Data', 'greenSpaceHackSelectedData'),
    Input('scatter-mapbox', 'selectedData'),
    prevent_initial_call=True
)
def update_box_select(selectedData):
    if not selectedData:
        # Wenn keine Daten ausgewählt wurden, zeige einen leeren Plot
        return dash.no_update
    else:
        
        
        try:
            
            print(selectedData)
            points = selectedData['points']
            selected_df = pd.DataFrame(points)
            
            greenSpaceHackSelectedData =selected_df.to_dict()
            print(selected_df.head())
            # selected_df.info()
            # print(selected_df['hovertext'])
            # listHovertext= selected_df['customdata'].values.tolist()
            # print(type(listHovertext))
            # print(listHovertext)
            
            # #extraction der id aus Liste
            # new_list = [list[0] for list in listHovertext]
            
            # print(new_list)
            # #df = pd.DataFrame(data)
            # #print(df.head())
            
            # boolean_series = dfLangerFrageBogenNestScore.id.isin(new_list)
            # filtered_df = df[boolean_series]
            # print(filtered_df)
            
            
            #df_points = pd.DataFrame(selectedData)
            
            # Erstellen Sie eine neue Spalte 'extracted_id', die das erste Element von 'customdata' enthält
            selected_df['extracted_id'] = selected_df['customdata'].apply(lambda x: x[0])

            # Nun verwenden Sie die 'extracted_id' Spalte, um die entsprechenden Datensätze aus other_df zu filtern
            filtered_data = dfLangerFrageBogenNestScore[dfLangerFrageBogenNestScore['id'].isin(selected_df['extracted_id'])]
            
            average_nest_score = selected_df['marker.size'].mean()

            print(average_nest_score)
            
            #fig_select_nest_score = px.box(selected_df, y='marker.size', title='Boxplot der NEST Scores')
            fig_select_nest_score = px.box(selected_df, y='marker.size', labels={'marker.size': 'NEST Score'}, title='Boxplot  NEST Scores')
            
            # Umstrukturierung der Daten für den Boxplot
            df_long = filtered_data.melt(value_vars=['AM6', 'AM7'], var_name='Verschattungstyp', value_name='Antwort')

            # Erstellen des Boxplots
            fig_shadow = go.Figure()

            # Hinzufügen der Boxplots für AM6 und AM7
            fig_shadow.add_trace(go.Box(y=df_long[df_long['Verschattungstyp'] == 'AM6']['Antwort'], name='AM6'))
            fig_shadow.add_trace(go.Box(y=df_long[df_long['Verschattungstyp'] == 'AM7']['Antwort'], name='AM7'))

            # Hinzufügen von Dummy-Datenpunkten für die Legende
            for value, label in zip([0.0, 1.0, 2.0, 3.0], ["Keine (habe aber welche erwartet)","Schlecht / Poor", "Ausreichend / Adequate /Keine (habe keine erwartet)", "Gut / Good"]):
                fig_shadow.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                        marker=dict(size=10, color='rgba(0,0,0,0)'),
                                        showlegend=True, name=f'{value}: {label}'))

            # Anpassen des Layouts
            fig_shadow.update_layout(title='Bewertungen für künstliche (AM6) und natürliche Verschattung (AM7)',
                            boxmode='group')
            
            
            
            return html.Div(
                [
                    html.Br(),
                    
                    
                    #html.H2([html.I(className="bi bi-reception-4 me-2"), "Test"], className=" text-center"),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("NEST-Score für ausgewählten Bereich", className="card-title text-center"),
                                                html.Br(),
                                                dcc.Dropdown(
                                                    id="dropdown_select_nest-score",
                                                    options=['NEST-Boxplot', 'NEST-Score Scatter'],
                                                    value='NEST-Boxplot',
                                                ),
                                                dcc.Graph(id='figure_select_nest_score', figure = fig_select_nest_score),
                                                # html.Br(),
                                            ],
                                            className="border-start border-danger border-5",
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),  
                                ], 
                                width=6
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Verschattung für ausgewählten Bereich", className="card-title text-center"),
                                                html.Br(),
                                                # # dcc.Dropdown(
                                                # #     id="dropdown_select_shadow",
                                                # #     options=['Boxplot-Verschattung', 'Scatter-Plot', ],
                                                # #     value='Boxplot-Verschattung',
                                                # # ),
                                                dcc.Graph(id='fig_select_shadow', figure = fig_shadow),
                                                # #html.Br(),
                                            ],
                                            className="border-start border-danger border-5",
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),  
                                ], 
                                width=6
                            ),
                        ]
                    ),

                    html.Br(),
                    html.Br(), 
                ]
            ), greenSpaceHackSelectedData
        except Exception as e:
            print(e)
            
########################################################################################################
@callback(
    Output('figure_select_nest_score', 'figure'),
    Input('dropdown_select_nest-score', 'value'),
    Input('greenSpaceHack-Data', 'greenSpaceHackSelectedData'),
    prevent_initial_call=True
    
)
def update_figure_select_nest_score(value, greenSpaceHackSelectedData):
    
    print(greenSpaceHackSelectedData)
    dfSelectNestScore = pd.DataFrame(greenSpaceHackSelectedData)
    
    print(dfSelectNestScore)
    # Zählen, wie oft jede Art als bedroht, invasiv oder einheimisch markiert wurde
   
    if value != '':
        
        if value == 'NEST-Boxplot':
            #Filter threatened Species
            fig_select_nest_score = px.box(dfSelectNestScore, y='marker.size', labels={'marker.size': 'NEST Score'}, title='Boxplot  NEST Scores')
           
        elif value == 'NEST-Score Scatter':
            fig_select_nest_score = px.scatter(dfSelectNestScore, y='marker.size', title='Scatterplot NEST Scores')
        
        return fig_select_nest_score
       
    
    return dash.no_update

########################################################################################################
# @callback(
#     Output('fig_select_shadow', 'figure'),
#     Input('dropdown_select_shadow', 'value'),
#     Input('greenSpaceHack-Data', 'greenSpaceHackSelectedData_01'),
#     prevent_initial_call=True
    
# )
# def update_figure_select_shadow(value, greenSpaceHackSelectedData_01):
    
#     df = pd.DataFrame(greenSpaceHackSelectedData_01)
    
#     # Zählen, wie oft jede Art als bedroht, invasiv oder einheimisch markiert wurde
   
#     if value != '':
        
#         if value == 'NEST-Boxplot':
#             #Filter threatened Species
#             fig_select_nest_score = px.box(df, y='marker.size', title='Boxplot  NEST Scores')
           
#         elif value == 'NEST-Score Scatter':
#             fig_select_nest_score = px.scatter(df, y='marker.size', title='Scatterplot NEST Scores')
        
#         return fig_select_nest_score
       
    
#     return dash.no_update
                 
