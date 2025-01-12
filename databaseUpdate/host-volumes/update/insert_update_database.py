import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, update
from sqlalchemy import text, inspect
from sqlalchemy.types import Integer, Text, String, DateTime, Float 
from sqlalchemy.sql import select
#from db import get_db_connection
import requests
from datetime import datetime, timedelta

#from fuzzywuzzy import fuzz
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

import time

import json

from sqlalchemy.dialects.postgresql import insert as pg_insert
from requests.exceptions import SSLError, RequestException
import configparser
import os





##########################################################################################################################################
def database_connection():

        
    # Datenbankkonfiguration extrahieren-
    dbname = os.environ['POSTGRES_DB']
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOSTNAME']
    port = os.environ['POSTGRES_PORT']
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    # Verbindungszeichenfolge erstellen
    return connection_string

###############################################################################################################################################

def safe_request(url, params, max_retries=3, delay=5):
    """Sendet eine Anfrage und versucht es erneut bei SSLError."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # LÃ¶st eine Exception fÃ¼r HTTP-Fehlercodes aus
            return response
        except requests.exceptions.SSLError as e:
            print(f"SSL-Fehler bei Versuch {attempt + 1} von {max_retries}: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)  # Wartezeit vor dem nÃ¤chsten Versuch
            else:
                raise  # Letzter Versuch: Fehler weitergeben
        except requests.exceptions.RequestException as e:
            print(f"Anfragefehler: {e}")
            raise  # Andere Arten von Fehlern direkt weitergeben, da sie nicht durch Wiederholung behoben werden kÃ¶nnen

#################################################################################################################################################

# Funktion, um Daten fÃ¼r einen bestimmten Tag herunterzuladen und in die Datenbank zu schreiben
def fetch_and_store_data_for_date(date, place_id=12870, table_name='inaturalist_observations'):
    

    
    url = 'https://api.inaturalist.org/v1/observations'
    params = {
        'quality_grade': 'any',
        'identifications': 'any',
        'place_id': place_id,
        'd1': date.strftime('%Y-%m-%d'),
        'd2': date.strftime('%Y-%m-%d'),
        'per_page': 200
    }

    all_observations = []
    page = 1
    max_retries = 5  # Maximale Anzahl von Versuchen
    retry_delay = 10  # VerzÃ¶gerung zwischen den Versuchen in Sekunden

    while True:
        
        response = safe_request(url, params=params, max_retries=5, delay=10)
        data = response.json()

        if 'results' in data and len(data['results']) > 0:
            all_observations.extend(data['results'])
            if len(data['results']) < params['per_page']:
                    break  # Letzte Seite erreicht
            page += 1
            params['page'] = page
        else:
                break  # Keine Daten gefunden oder Fehler

        

    observation_count = len(all_observations)
    print(f'Anzahl der heruntergeladenen Beobachtungen: {observation_count}')

    connection_string=database_connection()
        
    # Datenbank-Engine erstellen
    engine = create_engine(connection_string)
    
    
    if observation_count > 0:
        df_new = pd.json_normalize(all_observations)
        df_new[['latitude', 'longitude']] = df_new['location'].str.split(',', expand=True)

        df_new['latitude'] = df_new['latitude'].astype(float)
        df_new['longitude'] = df_new['longitude'].astype(float)

        for column in df_new.columns:
            if df_new[column].apply(lambda x: isinstance(x, (list, dict))).any():
                df_new[column] = df_new[column].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)

      
        
        # Inspektor-Objekt erstellen
        inspector = inspect(engine)

        if inspector.has_table(table_name):

            # Spaltennamen aus der Datenbanktabelle abrufen
            columns_in_db = [col['name'] for col in inspector.get_columns(table_name)]
    
            # Spalten im DataFrame, die nicht in der Datenbanktabelle vorhanden sind
            columns_not_in_db = [col for col in df_new.columns if col not in columns_in_db]
            
            # Spalten in der Datenbank, die nicht im DataFrame vorhanden sind
            missing_columns_in_df = [col for col in columns_in_db if col not in df_new.columns]

            # Spalten im DataFrame, die nicht in der Datenbanktabelle vorhanden sind, entfernen
            #df_new = df_new[[col for col in df_new.columns if col in columns_in_db]]

            # Metadatenobjekt erstellen
            metadata = MetaData()
            
            # Tabelle aus Metadaten laden
            table = Table(table_name, metadata, autoload_with=engine)

            

            # FÃ¼r jede fehlende Spalte in der Datenbanktabelle
            for col in columns_not_in_db:
                # Spalte zur Tabelle hinzufÃ¼gen
                with engine.connect() as conn:
                    with conn.begin():
                        # Erstellen Sie ein text-Objekt fÃ¼r Ihre SQL-Anweisung
                        sql = text(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" VARCHAR;')
                        # FÃ¼hren Sie die SQL-Anweisung aus
                        conn.execute(sql)
                        print(f"Spalte '{col}' wurde zur Tabelle '{table_name}' hinzugefÃ¼gt.")


            # Fehlende Spalten im DataFrame mit Standardwerten hinzufÃ¼ge
            for col in missing_columns_in_df:
                df_new[col] = None  # oder einen anderen Standardwert
            
            
            # Ausgabe der Unterschiede
            print("Spalten im DataFrame, die nicht in der Datenbanktabelle vorhanden sind:", columns_not_in_db)
            print("Spalten in der Datenbanktabelle, die nicht im DataFrame vorhanden sind:", missing_columns_in_df)

            #return df_new
            # Bestehende IDs aus der Datenbank abrufen
            with engine.connect() as connection:
                existing_ids_query = text(f'SELECT id FROM "{table_name}";')
                existing_ids_result = connection.execute(existing_ids_query)
                existing_ids = {row[0] for row in existing_ids_result}

            
             
            # ÃœberprÃ¼fen, ob IDs bereits vorhanden sind, und Filtern des DataFrame
            df_new_filtered = df_new[~df_new['id'].isin(existing_ids)]
            df_ID_update = df_new[df_new['id'].isin(existing_ids)]

            # Fehlende Daten in die Datenbank einfÃ¼gen, wenn df_new_filtered nicht leer ist
            if not df_new_filtered.empty:
                df_new_filtered.to_sql(table_name, engine, if_exists='append', index=False)
                print(f"Anzahl neu hinzugefÃ¼gter DatensÃ¤tze: {len(df_new_filtered)}")
            else:
                print("Keine neuen DatensÃ¤tze zum HinzufÃ¼gen.")
            
            if not df_ID_update.empty:
                # FÃ¼r jeden Datensatz in df_ID_update
                for index, row in df_ID_update.iterrows():
                    # Konvertiere die Zeile in ein Dictionary, ignoriere NaN-Werte
                    data_to_update = {key: value for key, value in row.to_dict().items() if pd.notna(value)}
                    
                    # Entferne den SchlÃ¼ssel 'id' aus dem Update-Dict, da 'id' nicht aktualisiert werden soll
                    if 'id' in data_to_update:
                        del data_to_update['id']
                
                    # Erstelle ein Update-Statement
                    stmt = (
                        update(table).
                        where(table.c.id == row['id']). 
                        values(**data_to_update)
                    )
                
                    # FÃ¼hre das Update-Statement aus
                    with engine.connect() as conn:
                        conn.execute(stmt)
                
                print(f"Anzahl der aktualisierten DatensÃ¤tze: {len(df_ID_update)}")
            else:
                print("Keine neuen DatensÃ¤tze zum Updaten.")
        else:    

            df_new.to_sql(table_name, engine, if_exists='append', index=False)
            print(f'Daten fÃ¼r {date.strftime("%Y-%m-%d")} gespeichert.')

            return None


#############################################################################################################################################
#
def get_latest_date_in_db(table_name):
    
    connection_string=database_connection()
    # Datenbank-Engine erstellen
    engine = create_engine(connection_string)
    
    query = text(f"SELECT max(observed_on) FROM {table_name}")
    with engine.connect() as conn:
        result = conn.execute(query)
        latest_date = result.scalar()

    if latest_date is not None and isinstance(latest_date, str):
        # Konvertiert den String zurÃ¼ck in ein datetime-Objekt, falls notwendig
        latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
    
    return latest_date

#########################################################################################################################################

def main():
    table_name = 'inaturalist_observations'

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(f"+       Start Container: {start_time}")
    print(f"+++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    # Ermitteln des aktuellsten Datums in der DB
    latest_date_in_db = get_latest_date_in_db(table_name)
    if not latest_date_in_db:
        # Fallback, wenn die Tabelle leer ist: Beginnen Sie 30 Tage vor dem aktuellen Datum
        latest_date_in_db = datetime.now() - timedelta(days=30)
    else:
        # Wenn Daten vorhanden sind, beginnen Sie 30 Tage vor dem letzten Datum in der Datenbank
        latest_date_in_db = latest_date_in_db - timedelta(days=30)

    # Daten vom ermittelten Startdatum bis gestern hinzufÃ¼gen/aktualisieren
    start_date = latest_date_in_db.date()
    end_date = datetime.now().date() - timedelta(days=1)  # Um das heutige Datum auszuschlieÃŸen

    for single_date in pd.date_range(start=start_date, end=end_date):
        print(f"Herunterladen und Speichern von Daten fÃ¼r: {single_date.strftime('%Y-%m-%d')}")
        df_new = fetch_and_store_data_for_date(single_date, place_id=12870, table_name=table_name)
        time.sleep(10)
     

if __name__ == "__main__":
    main()
