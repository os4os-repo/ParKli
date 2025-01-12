import base64
import datetime
from datetime import date

import io

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table, callback, callback_context

import pandas as pd

import numpy as np
import statistics 
import requests
import os
from geopy.distance import geodesic
from PIL import Image
import sys
from lib.find_water_colour import find_water_colour

import csv

import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.express as px
import plotly.graph_objs as go
import sys
import json
from geopy.geocoders import Nominatim




dash.register_page(__name__,
                   path='/Water',  # represents the url text
                   name='Water',  # name of page, commonly used as name of link
                   title='ParKli Water'  # epresents the title of browser's tab
)
    

##################################################################################################################

def parse_contentCSV(contents, filename_csv):
    
    
    
    content_type, content_string = contents.split(',')
    


    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename_csv:
         
            df = pd.read_csv(io.StringIO(decoded.decode('unicode_escape')))
            
          
            print(len(df))
            
            
            df.to_csv("new_file.csv")
            df = pd.read_csv("new_file.csv", sep=',',skiprows=1)
            
            print(df.head())
           
            return df
        else:
            return dash.no_update
    
    except Exception as e:
        print(e)

##########################################################################################################################################

# Step 1: Convert city name to bounding box using geopy (Nominatim)
def get_bounding_box(city_name):
    #geolocator = Nominatim(user_agent="geoapiExercises")
    #location = geolocator.geocode(city_name)
    geolocator = Nominatim(user_agent="ParKli.de")
    location = geolocator.geocode(city_name, language='de')

    
    if location:
        # Define a bounding box around the city (e.g., +/- 0.1 degrees as buffer)
        min_lat = location.latitude - 0.1
        max_lat = location.latitude + 0.1
        min_lng = location.longitude - 0.1
        max_lng = location.longitude + 0.1
        
        # Return in 1.3.0 format (minLatitude, minLongitude, maxLatitude, maxLongitude)
        return f"{min_lat},{min_lng},{max_lat},{max_lng}"
    else:
        raise ValueError("City not found.")
    
##########################################################################################

# Step 2: Make request to EyeOnWater API with bbox
def fetch_observations(city_name, period):
    try:
        bbox = get_bounding_box(city_name)
    except ValueError as e:
        print(e)
        return

    url = "https://www.eyeonwater.org/api/observations"

    # Construct the API query parameters
    params = {
        "bbox": bbox,
        "bboxVersion": "1.3.0",  # OGC bbox version 1.3.0 (latitude first)
        "format": "application/json",  # Requesting JSON format
        "limit": 200,
        "sort": "desc",
        "period": period
    }

    headers = {
        'accept': 'application/json'
    }

    try:
        response = requests.get(url, params=params, headers=headers)

        # Step 3: Handle the API response
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                df = pd.DataFrame(data)
                return df
                
            else:
                print(f"No observations found for {city_name}.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
############################################################################################################

# Function to recursively flatten any nested dictionaries in the DataFrame
def flatten_json_columns(df):
    # While there are still columns that contain dictionaries, flatten them
    while any(isinstance(df[col].iloc[0], dict) for col in df.columns):
        # Identify columns that contain dictionaries
        dict_columns = [col for col in df.columns if isinstance(df[col].iloc[0], dict)]
        
        for col in dict_columns:
            # Expand the dictionary column into multiple columns
            expanded_df = pd.json_normalize(df[col])
            
            # Rename new columns to reflect their origin
            expanded_df.columns = [f"{sub_col}" for sub_col in expanded_df.columns]
            
            # Drop the original dictionary column and concatenate the new columns
            df = pd.concat([df.drop(columns=[col]), expanded_df], axis=1)
    
    return df




#########################################################################################################################################
def delete_all_files_in_folder(folder_path):
    """
    Löscht alle Dateien in einem gegebenen Verzeichnis.
    """
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}. Reason: {e}")


############################################################################################################################################
# Funktion zum Herunterladen des Bildes
def download_image(url, save_folder):
    # Check if the image already exists in the folder
    filename = os.path.join(save_folder, os.path.basename(url))
    if os.path.exists(filename):
        return filename

    # If not, download and save the image
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        return None


#########################################################################################################################################
def cleanData(df):
    
  
    try:
        
         
            
            #Abstand zwischen beobachteten und berechneter Wert, wenn dieser zu groß löschen aus dem Dataframe
            dfStreuung = df.loc[(abs(df['fu_value'] - df['fu_processed']) < 2.0)]
            print(len(dfStreuung))

            df = dfStreuung.copy()
            df = df.dropna(subset=['p_cloud_cover'])        
            print(len(dfStreuung))
            
            # Navigiert eine Ebene nach oben und dann in den Ordner 'assets'
            relative_path = os.path.join('..', 'assets', 'Bilder')
    
            # Vollständiger Pfad zur Datei, ausgehend vom aktuellen Skriptverzeichnis
            path = os.path.join(os.path.dirname(__file__), relative_path)
            
             # Navigiert eine Ebene nach oben und dann in den Ordner 'assets'
            relative_path = os.path.join('..', 'assets', 'CSVPictureDate')
    
            # Vollständiger Pfad zur Datei, ausgehend vom aktuellen Skriptverzeichnis
            save_folder_CSV = os.path.join(os.path.dirname(__file__), relative_path)
                      
           
            
            #save_folder_CSV = './CSVPictureDate'
            # Create the save folder if it doesn't exist
            if not os.path.exists(save_folder_CSV):
                os.makedirs(save_folder_CSV)
            # Create the save folder if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                
            # Überprüfen, ob bereits eine CSV-Datei existiert
            csv_path = os.path.join(save_folder_CSV, 'data_api.csv')
            if os.path.exists(csv_path):
                # Lade das DataFrame aus der CSV-Datei
                df_existing = pd.read_csv(csv_path)
                dfnew_entries = df[~df['image'].isin(df_existing['image'])]
                #df_updated = pd.concat([df_existing, new_entries], ignore_index=True)
                #df_updated.to_csv('data.csv', index=False)  
            else:
                dfnew_entries = df.copy()
            
            
            if not dfnew_entries.empty:
                dfnew_entries['image_path'] = dfnew_entries['image'].apply(lambda url: download_image(url, path))

                dfnew_entries["total_pixels"] = 0
                dfnew_entries["color_pixels"] = 0

                # # # Schleife über alle Dateien im Ordner
                for filename in os.listdir(path):
                    
                    if filename.endswith(".png"):
                    # Bild öffnen
                        img = Image.open(os.path.join(path, filename))
                        # Gesamtanzahl der Pixel
                        total_pixels = img.width * img.height

                        # Anzahl der Farbpixel
                        color_pixels = len(set(img.getdata()))
                        
                            
                        row = dfnew_entries.loc[dfnew_entries['image'].str.contains(filename)]
                        
                        # Überprüfe, ob eine Zeile gefunden wurde
                        if not row.empty:
                        #Pixelzahl und Anzahl der Farbpixel in DataFrame speichern
                            dfnew_entries.loc[row.index, "total_pixels"] = total_pixels
                            dfnew_entries.loc[row.index, "color_pixels"] = color_pixels
                            
                dfnew_entries = dfnew_entries.dropna(subset=['p_cloud_cover'])
                df_copy = dfnew_entries.copy()
                #Delete Duplicates 
                df_copy.drop_duplicates(['day', 'total_pixels', 'color_pixels'], keep='first', inplace=True)
                dfnew_entries =df_copy.copy()
                #Drop tuples weithout picture
                dfnew_entries = dfnew_entries.drop(dfnew_entries[(dfnew_entries['total_pixels'] == 0) & (dfnew_entries['color_pixels'] == 0)].index)
                print(len(df))
                
                # overcastSunny = 'sunny'
                p_cloud_cover = 0.0

                dfnew_entries["Flag"] = "Placeholder"
                dfnew_entries["fu_processed_wacodi_processed"] = 0

                # # # # Schleife über alle Dateien im Ordner
                for filename in os.listdir(path):
                    
                    if filename.endswith(".png"):
                        
                        row = dfnew_entries.loc[df['image'].str.contains(filename)]
                        
                        if not row.empty:
                # #              #print(row)
                            p_cloud_cover = row['p_cloud_cover'].values[0]

                            if p_cloud_cover <= 50.0:
                                overcastSunny = 'overcast'
                            else:
                                overcastSunny = 'sunny'

                            findWaterColour = find_water_colour(os.path.join(path, filename), overcastSunny)

                            successFindWaterColour = findWaterColour['success']
                            fuProcessedWacodiProcessed = findWaterColour['FUvalue']
                            
                            dfnew_entries.loc[row.index, "Flag"] = successFindWaterColour
                            dfnew_entries.loc[row.index, "fu_processed_wacodi_processed"] = fuProcessedWacodiProcessed
                            
            
            
            
            if os.path.exists(csv_path):
                # Lade das DataFrame aus der CSV-Datei
                #df_existing = pd.read_csv(csv_path)
                #dfnew_entries = df[~df['image'].isin(df_existing['image'])]
                df_updated = pd.concat([df_existing, dfnew_entries], ignore_index=True)
                df_updated.to_csv(csv_path, index=False)
                df = df_updated.copy()
            else:
                #dfnew_entries = df.copy()
                dfnew_entries.to_csv(csv_path)
                df = dfnew_entries.copy()
                #dfAll = pd.read_csv(csv_path, sep=',')
                #print(len(dfAll))
                #new_entries['image_path'] = new_entries['image'].apply(lambda url: download_image(url, save_folder))

            delete_all_files_in_folder(path)
            
            dfTrue = df.loc[(df['Flag'] == True)]
            
            print(len(dfTrue))
            
            #dfTrue=dfTrue.drop(columns=['active', 'last_update','update_count','input_date','apk_user_n_code','geom', 'image.1', 'nickname.1'])
            #dfTrue.to_csv("new_file.csv")
            #dfTrue = pd.read_csv("new_file.csv", sep=',')
            #df=df.rename(columns={'Unnamed': 'id'}, inplace=True)
            print(dfTrue.head())
           
            return dfTrue
    except Exception as e:
        print(e)






########################################################################################################
card_Upload = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-filetype-csv me-2"), "Upload EyeOnWater Data"], className="text-center pe-2"),
            
            html.Br(),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                        'width': '100%',
                        'height': '40px',
                        'lineHeight': '40px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '1px'
                },
                            # Allow multiple files to be uploaded
                multiple=True
            ),
            
            html.Br(),
        ],
        className="border-start border-secondary border-5",
       
    ),
    className="m-2 shadow bg-white rounded ",
)



card_Location = dbc.Card(
    dbc.CardBody(
        [
            html.H2([html.I(className="bi bi-geo-alt me-2"), "Untersuchungsort"], className="text-nowrap text-center pe-2"),
            dbc.FormText("Geben Sie den Namen einer Stadt ein", className="w-auto col-md-6"),
            dbc.Input(id='city-input_EyeOnWater', persistence=False, placeholder="Stadt...", type="text", className="form-control col-md-6", style={'width': '200px'}),

            dbc.FormText("Legen Sie den Suchradius in ° schrittweite 0.01 fest", className="w-auto col-md-6"),
            dbc.Input(id='latLon-input', placeholder='0.02', type="number", min=0, max=1, step=0.01, value='0.02', className="form-control col-md-6", style={'width': '200px'}),

            # New form text and input for the period in months
            dbc.FormText("Untersuchungszeitraum in Monaten", className="w-auto col-md-6"),
            dbc.Input(id='period-input', placeholder='Zeitraum in Monaten', type="number", min=1, value=36, className="form-control col-md-6", style={'width': '200px'}),

            html.Br(),
            dbc.Button("Daten herunterladen", id="download-button_EyeOnWater", n_clicks=0, outline=True, color="secondary", className="me-2 text-nowrap"),
            html.Br(),
        ],
        className="border-start border-secondary border-5",
    ),
    className="m-2 shadow bg-white rounded",
)



card_UpdateMapScatterMapbox = dbc.Card(
    dbc.CardBody(
        [
            html.H1([html.I(className="bi bi-map me-2"), "Auswahl Daten"], className="text-nowrap text-center"),
            html.Br(),
            #html.Div(id='map'),
            dcc.Graph(id='scatter-mapbox', figure={}),
        ],
        className="border-start border-secondary border-5",
       
    ),
    className="m-2 shadow bg-white rounded",
)


 
    
    
    
    
#######################################################################################################

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
                                html.Img(src="./assets/ParKli_Wasser_300px.png", height="50", style={'display': 'inline-block'}),
                                html.H1("ParKli Gewässer",style={'textAlign': 'center', 'color': '#2F5F53','display': 'inline-block', 'margin-left': 'auto', 'margin-right': 'auto' }),
                                        
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
                        #card_Upload, 
                        #html.Br(),
       
                        card_Location, 
                                
                    ], 
                    width={"size": 3, "offset":0}
                    #xs=2, sm=2, md=3, lg=3, xl=3, xxl=3
                ),
                dbc.Col(
                    [
                        card_UpdateMapScatterMapbox,
                                
                    ], width={"size": 9, "offset":0}
                ),
                
                    
            ],
        ),

                   
        html.Br(),
       

 
        

        # Erstelle einen Box Select, um Punkte auszuwählen
        
        html.Div(id='select-box'),
        
        #dcc.Graph(id='box-select', figure={}),
    
       
    
        #html.Div(id='scatter-map'),
    
        #html.Div(id='box-plot'),
        
    ]
)
############################################################################################################################

    
# @callback(
#     Output('scatter-mapbox', 'figure'),
#     Output('stored-data', 'dataEyeonWater'),
#     Input('upload-data', 'contents'),
#     State('upload-data', 'filename'),
#     State('stored-data','dataEyeonWater'),
#     prevent_initial_call=True
    
# )
# def update_output(list_of_contents, list_of_names, dataEyeonWater):
#     if list_of_contents is not None:
        
#         print(list_of_contents)
#         print(list_of_names)
        
#         parsed_data = []
        
#         for content, name in zip(list_of_contents, list_of_names):
#             parsed_content = parse_contentCSV(content, name)  # Annahme: parse_contents-Funktion extrahiert den Inhalt und gibt einen DataFrame zurück
#             parsed_data.append(parsed_content)
    
#         df = pd.concat(parsed_data)  # Zusammenführen der einzelnen DataFrames zu einem DataFrame
        
#         dataEyeonWater = df.to_dict('records')
#         print(type(dataEyeonWater))

#         #df = (parse_contentCSV(c,n)( for c, n in zip(list_of_contents, list_of_names))
       
#         fig = px.scatter_mapbox(df, 
#             lat="lat", 
#             lon="lng",
#             hover_name="n_code",
#             hover_data=["n_code", "date_photo", "device_model", 'nickname','fu_processed','fu_value'],
#             color_discrete_sequence=["black"],
#             zoom=10, height=300
#         )
#         #fig.update_layout(mapbox_style="stamen-terrain")
#         fig.update_layout(mapbox_style="open-street-map")
#         fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
#         return fig, dataEyeonWater
    
#     return dash.no_update


# ######################################################################################################################################


# # Callback to update map and store data
@callback(
    Output('scatter-mapbox', 'figure'),
    Output('stored-data', 'dataEyeonWater'),
    State('city-input_EyeOnWater', 'value'),
    Input('download-button_EyeOnWater', 'n_clicks'),
    State('period-input', 'value'),
    prevent_initial_call=True
)
def update_map(city_name, n_clicks, period):
    if city_name:
        # Fetch the data from EyeOnWater API
        df = fetch_observations(city_name, period)
        
        if df is not None and len(df) > 0:
            # Flatten the nested JSON structure in the data
            df = flatten_json_columns(df)
            
            # Store the data for further usage
            dataEyeonWater = df.to_dict('records')

            # Update the map figure
            fig = px.scatter_mapbox(df, 
                lat="lat", 
                lon="lng",
                hover_name="image",  # Use image URL as unique key
                hover_data=["date_photo", "device_model", 'nickname', 'fu_processed', 'fu_value'],
                color_discrete_sequence=["blue"],
                zoom=10, height=300
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            
            return fig, dataEyeonWater
    
    return dash.no_update, dash.no_update





# @callback(
#     Output('scatter-mapbox', 'figure'),
#     Output('stored-data', 'dataEyeonWater'),
#     [Input('download-button_EyeOnWater', 'n_clicks'),
#      Input('upload-data', 'contents')],
#     [State('city-input_EyeOnWater', 'value'),
#      State('upload-data', 'filename'),
#      State('stored-data', 'dataEyeonWater')],
#     prevent_initial_call=True
# )
# def update_map_or_upload(n_clicks, list_of_contents, city_name, list_of_names, dataEyeonWater):
#     # Identify which input triggered the callback
#     triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]

#     # If the trigger was the download button for the EyeOnWater API
#     if triggered_id == 'download-button_EyeOnWater' and city_name:
#         # Fetch data from EyeOnWater API
#         df = fetch_observations(city_name)
        
#         if df is not None and len(df) > 0:
#             # Flatten the nested JSON structure in the data
#             df = flatten_json_columns(df)
            
#             # Store the data for further usage
#             dataEyeonWater = df.to_dict('records')

#             # Update the map figure
#             fig = px.scatter_mapbox(df, 
#                 lat="lat", 
#                 lon="lng",
#                 hover_name="image",  # Use image URL as unique key
#                 hover_data=["date_photo", "device_model", 'nickname', 'fu_processed', 'fu_value'],
#                 color_discrete_sequence=["blue"],
#                 zoom=10, height=300
#             )
#             fig.update_layout(mapbox_style="open-street-map")
#             fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

#             return fig, dataEyeonWater

#     # If the trigger was an uploaded CSV file
#     elif triggered_id == 'upload-data' and list_of_contents is not None:
#         parsed_data = []
        
#         for content, name in zip(list_of_contents, list_of_names):
#             # Parse the uploaded CSV content
#             parsed_content = parse_contentCSV(content, name)
#             parsed_data.append(parsed_content)
        
#         df = pd.concat(parsed_data)  # Merge all parsed CSV data
#         dataEyeonWater = df.to_dict('records')

#         # Update the map figure
#         fig = px.scatter_mapbox(df, 
#             lat="lat", 
#             lon="lng",
#             hover_name="image",  # Use image URL as unique key
#             hover_data=["date_photo", "device_model", 'nickname', 'fu_processed', 'fu_value'],
#             color_discrete_sequence=["black"],
#             zoom=10, height=300
#         )
#         fig.update_layout(mapbox_style="open-street-map")
#         fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

#         return fig, dataEyeonWater

#     return dash.no_update, dash.no_update




    


#######################################################################################################################################
# Callback-Funktion für den Box Select
@callback(
    Output('select-box', 'children'),
    Output ('cleanedEyeOnWater-Data', 'cleanedDataEyeonWater'),
    #Output ('unCleanedEyeOnWater-Data', 'unCleanedDataEyeOnWater'),
    Input('scatter-mapbox', 'selectedData'),
    State('stored-data','dataEyeonWater'),
    State ('cleanedEyeOnWater-Data', 'cleanedDataEyeonWater')
    #State('unCleanedEyeOnWater-Data', 'unCleanedDataEyeOnWater')
)
def update_box_select(selectedData, dataEyeonWater, cleanedDataEyeonWater):
    if not selectedData:
        # Wenn keine Daten ausgewählt wurden, zeige einen leeren Plot
        return dash.no_update
    else:
        
        try:
            # Extrahiere die ausgewählten Daten
            print(selectedData)
            points = selectedData['points']
            selected_df = pd.DataFrame(points)
            print(selected_df.head())
            selected_df.info()
            #print(selected_df['hovertext'])
            listHovertext= selected_df['hovertext'].values.tolist()
            df = pd.DataFrame(dataEyeonWater)
            #df.info()
            
            
            
            # Parse the date column with the correct format
            df['date_photo'] = pd.to_datetime(df['date_photo'], format='%Y-%m-%d %H:%M:%S')

            # Create additional date columns
            df['month_year'] = df['date_photo'].dt.to_period("M")
            df['month'] = df['date_photo'].dt.month
            df['day'] = df['date_photo'].dt.to_period("D")
            df['month_year_period'] = df['month_year'].apply(lambda x: x.strftime('%Y-%m'))


            # df['date_photo'] = pd.to_datetime(df['date_photo'], format='%m/%d/%Y %I:%M:%S %p')
            # df['month_year'] = df['date_photo'].dt.to_period("M")
            # df['month'] = pd.DatetimeIndex(df['date_photo']).month
            # df['day'] = df['date_photo'].dt.to_period("D")
            # df['month_year_period'] = pd.PeriodIndex(df['month_year'], freq='M')
            # df['month_year_period'] = df['month_year_period'].apply(lambda x: x.strftime('%Y-%m'))
            
           
            
            #unclean Observations 
            #boolean_series = df.n_code.isin(listHovertext)
            boolean_series = df['image'].isin(listHovertext)
            filtered_df_unclean = df[boolean_series]
           
            
            print(filtered_df_unclean.head())
            
            
            
                      
            #Cleaning Process
            dfCleaned = cleanData(df) 
            
            #boolean_series = dfCleaned.n_code.isin(listHovertext)
            boolean_series_clean  = dfCleaned['image'].isin(listHovertext)
            filtered_df = dfCleaned[boolean_series_clean ]
            
            print(filtered_df.info())
            
            
            
            #df_observation_filtered_df = filtered_df.groupby('month_year')['n_code'].count().reset_index()
            df_observation_filtered_df = filtered_df.groupby('month_year')['image'].count().reset_index()
            df_observation_filtered_df.sort_values(by='month_year')
           
            #figObservationCount = px.bar(df_observation_filtered_df, x='month_year', y='n_code', labels={'month_year':'Zeit', 'n_code': 'Beobachtungen'})
            figObservationCount = px.bar(df_observation_filtered_df, x='month_year', y='image', labels={'month_year':'Zeit', 'image': 'Beobachtungen'})

            #print(data)
           
            cleanedDataEyeonWater = filtered_df.to_dict('records')
            #df.to_dict('records')
  
            #print(cleanedDataEyeonWater.head())
            print(type(cleanedDataEyeonWater))

            fig = px.box(filtered_df, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot')
            
            df_ph =  filtered_df.loc[(filtered_df['p_ph'] > 0)]
            
            df_SecchiDisk =filtered_df.loc[(((filtered_df['sd_depth']) > 0) & ((filtered_df['sd_depth'] < 1)))] 
            #df_SecchiDisk = round(df_SecchiDisk,2)
            
            #Avg per Month
            df_monthly = filtered_df.filter(['date_photo', 'fu_value', 'fu_processed'])
            df_monthly['date_photo'] = pd.to_datetime(df_monthly['date_photo'])
            df_monthly = df_monthly.set_index('date_photo')
            df_monthly = df_monthly.resample('ME').mean()
            df_monthly = df_monthly.interpolate()
            df_monthly = df_monthly.reset_index()
            df_avg = df_monthly.melt(id_vars=['date_photo'], var_name='variable', value_name='value')
            figAvgMonth = px.line(df_avg, x='date_photo', y='value', color='variable')
            
            #Durchschnitte berechnen und Runden
            fu_value_mean = filtered_df['fu_value'].mean()
            fu_value_mean = round(fu_value_mean,2)
            fu_processed_mean = filtered_df['fu_processed'].mean()
            fu_processed_mean=round(fu_processed_mean,2)
            ph_value_mean = df_ph['p_ph'].mean()
            ph_value_mean  = round(ph_value_mean ,2)
            sd_depth_value_mean = df_SecchiDisk['sd_depth'].mean()
            sd_depth_value_mean = round(sd_depth_value_mean,2)
            
            
            
            
            
            
            return html.Div(
                [
                    
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [

                                                                html.P(children=["Beobachtungen Gesamt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(df)], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Beobachtungen Gesamt bereinigt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(dfCleaned)], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
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

                                                                html.P(children=["Ausgewählter Bereich"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(filtered_df_unclean)], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Ausgewählter Bereich bereinigt"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[len(filtered_df)], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
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

                                                                html.P(children=["Forel-Ule-Skala Wert User"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[fu_value_mean], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Forel-Ule-Skala Wert App"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[fu_processed_mean], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
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

                                                                html.P(children=["pH-Werte"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[ph_value_mean], className="card-subtitle text-n h5 text-center"),
                                                            ],
                                                            className="border-start border-secondary border-5",
                                                        ),
                                                        className="m-2 shadow bg-white rounded h-100 class",
                                                    ),
                                                ],
                                                width={"size": 6},
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Card(
                                                        dbc.CardBody(
                                                            [
                                                                #html.P(children=["Anzahl der Beobachtungen im ausgewählten Bereich: ",len(filtered_df)], className="card-subtitle text-nowrap h6 text-center"),
                                                                html.P(children=["Secchi-Disk Wert"], className="card-subtitle h5 text-center"),
                                                                html.Br(),
                                                                html.P(children=[sd_depth_value_mean], className="card-subtitle  h5 text-center"),
                                                            ],
                                                                className="border-start border-secondary border-5",
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
                                                html.H5("Anzahl der Beobachtungen ausgewählter Bereich pro Monat", className="card-title text-center"),
                                                #html.H5("Box-Plot", className="card-title text-center"),
                                                html.Br(),
                                                # dcc.Dropdown(
                                                #     id="dropdownObservation",
                                                #     options=['Bereinigt', 'Unbereinigt'],
                                                #     value='Bereinigt',
                                                # ),
                                                html.Br(),
                                                dcc.Graph(id='observation', figure = figObservationCount),
                                                #html.Br(),
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                ],
                                width={"size": 8},
                                className = "h-100 class",
                            )
                        ]
                    ),
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Streuung der Werte", className="card-title text-center"),
                                                #html.H5("Box-Plot", className="card-title text-center"),
                                                html.Br(),
                                                dcc.Dropdown(
                                                    id="dropdownPlot",
                                                    options=['Box-Plot', 'Scatter-Plot'],
                                                    value='Box-Plot',
                                                ),
                                                html.Br(),
                                                dcc.Graph(id='distribution', figure = fig),
                                                #html.Br(),
                                            ],
                                            className="border-start border-secondary border-5",
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                    
                                ],
                                width={"size": 6},
                                className = "h-100 class",
                            ),
                            
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Sichtiefen-/pH-Wert-Messung", className="card-title text-center"),
                                                #html.H5("Box-Plot", className="card-title text-center"),
                                                html.Br(),
                                                dcc.Dropdown(
                                                    id="dropdownSd_pH",
                                                    options=['Sichtiefenmessung', 'pH-Wert-Messung'],
                                                    value='Sichtiefenmessung',
                                                ),
                                                html.Br(),
                                                dcc.Graph(id='sd_ph_fig', figure = fig),
                                                #html.Br(),
                                            ],
                                            className="border-start border-secondary border-5",
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                    
                                ],
                                width={"size": 6},
                                className = "h-100 class",
                            ),
                            
                            
                        ],
                    ),
                    
                    html.Br(),
                    html.Br(),
                    
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5("Durchschnitt pro Monat", className="card-title text-center"),
                                                dcc.Graph(figure = figAvgMonth),
                                                #html.Br(),
                                                
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                    
                                ],
                                width={"size": 6},
                            ),
                            
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [   
                                                 html.H5("Übersicht über die Werte", className="card-title text-center"),
                                               dash_table.DataTable(
                                                    filtered_df.to_dict('records'),
                                                    [{'name': i, 'id': i} for i in filtered_df.columns],
                                                    #page_size=10,
                                                    filter_action="native",
                                                    sort_action="native",
                                                    sort_mode="single",
                                                    column_selectable="single",
                                                    fixed_rows={'headers': True},
                                                    style_table={'margin': '10px', 'height': '400px'},
                                                    style_cell={'textAlign': 'left', 'padding': '1px', 'minWidth': 95, 'maxWidth': 95, 'width': 95}
                                                ),
                                                
                                            ],
                                            className="border-start border-secondary border-5",
                                            
                                        ),
                                        className="m-2 shadow bg-white rounded h-100 class",
                                    ),
                                ],
                                width={"size": 6},
                            ),
                            
                            
                        ],
                    ),
                    html.Br(),
                    html.Br(),
                ]
            ), cleanedDataEyeonWater #, unCleanedDataEyeOnWater
        
            #return fig
        except Exception as e:
            print(e)

################################################################################################################################        

@callback(
    Output('distribution', 'figure'),
    Input('dropdownPlot', 'value'),
    Input('cleanedEyeOnWater-Data','cleanedDataEyeonWater'),
    prevent_initial_call=True
    
)
def update_distribution(value, cleanedDataEyeonWater):
    
    df = pd.DataFrame(cleanedDataEyeonWater)
    if value == 'Box-Plot':
        fig = px.box(df, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot') 
        
        return fig
    elif value == 'Scatter-Plot':
        
        fig= px.scatter(df, x='month_year', y=['fu_processed', 'fu_value'], title='Scatter-Plot')
        
        return fig
    
    return dash.no_update
####################################################################################################################################

@callback(
    Output('sd_ph_fig', 'figure'),
    Input('dropdownSd_pH', 'value'),
    Input('cleanedEyeOnWater-Data','cleanedDataEyeonWater'),
    prevent_initial_call=True
    
)
def update_sdDepth_phValue(value, cleanedDataEyeonWater):
    
    df = pd.DataFrame(cleanedDataEyeonWater)
      
    if value == 'Sichtiefenmessung':
        if 'sd_depth' not in df.columns or df['sd_depth'].isnull().all():
            return dash.no_update

        df_SecchiDisk =df.loc[(((df['sd_depth']) > 0) & ((df['sd_depth'] < 1)))] 
        #fig = px.box(df_SecchiDisk, x='month_year', y=['fu_processed', 'fu_value'], points='all', title='Boxplot') 
        
        if df_SecchiDisk.empty:
            return dash.no_update

        fig= px.scatter(df_SecchiDisk, x='month_year', y='sd_depth', title='Sichtiefenmessung')
        
        return fig
    elif value == 'pH-Wert-Messung':

        if 'p_ph' not in df.columns or df['p_ph'].isnull().all():
            return dash.no_update
        
        df_ph =  df.loc[(df['p_ph'] > 0)]
        
        if df_ph.empty:
            return dash.no_update
        
        fig= px.scatter(df_ph, x='month_year', y='p_ph', title='pH-Wert-Messung')
        
        return fig
    
    return dash.no_update

