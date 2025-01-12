

"""
This app creates an .....
"""



import dash
from dash import Dash, dcc, html, Input, Output, callback, State
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

#PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

app = dash.Dash(
    __name__, 
    use_pages=True, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
server = app.server


navbar = dbc.Navbar(
    
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Img(src="./assets/ParKli_400px.png", height="30")
                                #dbc.NavbarBrand("ParKli", className="ms-2")
                            ],
                            width={"size":"auto"}
                        )
                    ],
                align="center",
                className="g-0"
                ),
                href="/",
                style={"textDecoration": "none"},
                
            ),
            
            # dbc.Row(
            #     [
            #         dbc.Col(
            #             [
            #                 html.Img(src="./assets/ParKli_400px.png", height="30")
            #                 #dbc.NavbarBrand("ParKli", className="ms-2")
            #             ],
            #             width={"size":"auto"}
            #         )
            #     ],
            #     align="center",
            #     className="g-0"
            # ),
            
           
            
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Collapse(
                                [
                                 
                                    dbc.Nav(
                                        [   
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    [
                                                        html.Div(page["name"], className="ms-1"),
                                                    ],
                                                    href=page["path"],
                                                    active="exact",
                                                )
                                            )
                                            
                                            for page in dash.page_registry.values()
                        
                                            if page["module"] != "pages.not_found_404"
                                        
                                        ],                                    
                                    ),
                                   
                                ],
                                id="navbar-collapse",
                                is_open=False,
                                navbar=True,
                                
                                
                            )
                        
                        ],
                        width={"size":"auto"},
                        #style={'margin':{"r":0,"t":0,"l":0,"b":0}}
                    )
                    
                ],
                align="center",

              
            ),
        
         
            dbc.Col(dbc.NavbarToggler(id="navbar-toggler", n_clicks=0)),
            
        ],
        
        fluid=True

    ),
    color="#eaeeef",
    light = True
    #dark=False
    
)



app.layout = dbc.Container([
    
    
        
       navbar,
       
       html.Br(),
       html.Br(),
      
       
       dash.page_container,
       
        dcc.Store(id='memory-output',  storage_type='session', data={}),
        dcc.Store(id='selectedData-State',  storage_type='session', data={}),
        dcc.Store(id='stored-data', storage_type='session', data={}),     
        dcc.Store(id='cleanedEyeOnWater-Data', storage_type='session', data={}), 
        dcc.Store(id='unCleanedEyeOnWater-Data', storage_type='session', data={}), 
        dcc.Store(id='greenSpaceHack-Data', storage_type='session', data={}),
       
], fluid=True)


@dash.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":

    app.run_server(debug=False)

