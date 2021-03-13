import dash
import dash_html_components as html
import dash_core_components as dcc
import altair as alt
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from vega_datasets import data
import plotly as py
import plotly.express as px
import plotly.graph_objects as go

alt.data_transformers.disable_max_rows()

########## Additional Data Filtering ###########################################
df = pd.read_csv('data/processed/business_data.csv', sep=';') #data/processed/cleaned_data.csv


#display_df = display_df.rename(columns={'title': 'Title', 'variety':'Variety', 'state':'State', 'points':'Points', 'price':'Price'})
###############################################################################


def create_card(header='Header', content='Card Content'): 
    
    if header:
        card = dbc.Card([dbc.CardHeader(header),
            dbc.CardBody(html.Label([content]))])
    elif not header:
        card = dbc.Card([dbc.CardBody(html.Label([content]))])
    return card 


def within_thresh(value, businesstype, column, data, sd_away=1):
    '''returns the lower and upper thresholds and whether the input
       falls within this threshold
    '''
    mean_df = data.groupby('BusinessType').mean()
    sd_df = data.groupby('BusinessType').std()
    
    mean = mean_df.loc[businesstype, column]
    sd = sd_df.loc[businesstype, column]
    
    upper_thresh = mean + sd_away*sd 
    lower_thresh = mean - sd_away*sd
    
    if value > upper_thresh or value < lower_thresh: 
        return lower_thresh, upper_thresh, False
    else: 
        return lower_thresh, upper_thresh, True


app = dash.Dash(__name__ , external_stylesheets=[dbc.themes.BOOTSTRAP])
# Set the app title
app.title = "Fraudulent Buisness Detection"
server=app.server

colors = {
    'background': "#00000",
    'text': '#522889'
}

collapse = html.Div(
    [
        dbc.Button(
            "Learn more",
            id="collapse-button",
            className="mb-3",
            outline=False,
            style={'margin-top': '10px',
                'width': '150px',
                'background-color': 'white',
                'color': '#522889'}
        ),
    ]
)

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1('Fraudulent Buisness Detection', style={'text-align': 'center', 'color': 'white', 'font-size': '40px', 'font-family': 'Georgia'}),
            dbc.Collapse(html.P(
                """
                The dashboard will help you with your wine shopping today. Whether you desire crisp Californian Chardonnay or bold Cabernet Sauvignon from Texas, simply select a state and the wine type. The results will help you to choose the best wine for you.
                """,
                style={'color': 'white', 'width': '70%'}
            ), id='collapse'),
        ], md=10),
        dbc.Col([collapse])
    ], style={'backgroundColor': '#0F5DB6', 'border-radius': 3, 'padding': 15, 'margin-top': 22, 'margin-bottom': 22, 'margin-right': 11}),

    # dcc.Tabs([
        dcc.Tab([
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Label([
                        'Company Name'], style={
                'color': '#0F5DB6', "font-weight": "bold"
            }),
                    dcc.Textarea(
                        id='business-name',
                        style={'width': '100%', 'height': 30},
                        placeholder='Select a State',
                        value = 'Time Education Inc'

                    ),
                    html.Br(),
                    html.Label(['Street Address'], style={'color': '#0F5DB6', "font-weight": "bold"}
                    ),
                    html.Br(),
                    dcc.Textarea(id='address', value='Time Education Inc'),
                    html.Br(),
                    html.Label(['Search Url'], style={'color': '#0F5DB6', "font-weight": "bold"}),
                    dcc.Textarea(style={'width': '100%', 'height': 30}),
                    dbc.Button('Web Search', id = 'scrape-btn', n_clicks=0, className='reset-btn-1'),
                    ], style={'border': '1px solid', 'border-radius': 3, 'padding': 15, 'margin-top': 22, 'margin-bottom': 15, 'margin-right': 0, 'height' : 350}, md=4,
                ),
                dbc.Col([], md=1),
                dbc.Col([
                    html.Br(),
                    html.Br(),
                    dbc.Row([create_card(None, 'This is where the score will go')]),
                    html.Br(),
                    dbc.Row([create_card(None,'This will be the number of outlier pts')]),
                ], md = 2),
                dbc.Col([
                    dcc.Graph(id='pie-chart',
                             figure = {'layout': go.Layout(margin={'b': 0})})
                ],)


                # dbc.Col([
                #         html.Br(),
                #         html.Br(),
                #         dbc.Row([create_card('card1', 'card 1 content')]),
                #         dbc.Row([create_card('Card2','Card 2 Content')]),
                #     ], md=2),
                # dbc.Col([
                #      html.Br(),
                #      html.Br(),
                #      dbc.Row([create_card('card3', 'card3 content')]),
                #      dbc.Row([create_card('Card4','Card 4 Content')]),
                #     ], md=4)
                ]),
            dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader('Key Insights:', 
                            style={'fontWeight': 'bold', 'color':'white','font-size': '22px', 'backgroundColor':'#0F5DB6', 'height': '50px'}),
                            dbc.CardBody(id='highest_value_name', style={'color': '#2EC9F0', 'fontSize': 18,  'height': '70px'}),
                            dbc.CardBody(id='insight-1', style={'color': '#522889', 'fontSize': 18,  'height': '380px'}),
                        ]),
                    ], md = 4),
                    dbc.Col([], md = 2),
                    dbc.Col([
                    dbc.Row([
                            dcc.Graph(id='histogram'),         
                        ]),
                        dcc.Dropdown(
                                id='feature_type',
                                value='select a feature',
                                options = [{'label': col, 'value': col} for col in df.columns],
                                placeholder='Select a Feature', 
                                multi=False
                            ),
                    html.Br(), 
                    ],md = 6),
                ]),
            ], label='MDS Winery'),
    ])


@app.callback(Output('insight-1', 'children'),
             Input('business-name', 'value'))
def url_presence(business):
    website = 'www.google.com'
    # business_df = df.query('BusinessName == @business')
    # website = business_df.iloc[-1, 'website']
    if website:
        insight = f"Website: {website}"
    if website:
        insight = 'No website available'
    return insight

@app.callback(Output('insight-2', 'children'),
             Input('business-name', 'value'))
def time_online(business):
    
    website = 'www.google.com'
    # business_df = df.query('BusinessName == @business')
    # website = business_df.iloc[-1, 'website']
    if website:
        insight = f"Website: {website}"
    if website:
        insight = 'No website available'
    return insight



def calculate_scores(business):
    scores = ['green', 'green', 'green', 'red']
    return scores

@app.callback(Output('pie-chart', 'figure'),
             [Input('feature_type', 'value'),
            Input('business-name', 'value')])
def plot_donut(score, business):

    score_list = calculate_scores(business)
    df_dict = {'feat': ['physical', 'online', 'government', 'other'],
           'size': [25, 25 ,25,25],
           'score' : score_list}

    pie_df = pd.DataFrame(df_dict)

    fig = go.Figure(data=[go.Pie(labels=pie_df['feat'],
                             values=[25,25,25,25])])
    fig.update_traces(hoverinfo='label+percent', textinfo='label', textfont_size=20,
                    marker=dict(colors=pie_df['score'], line=dict(color='#000000', width=1)))
    fig.update_layout(showlegend=False)

    return fig

@app.callback(Output('address', 'value'),
             [Input('business-name', 'value')])
def update_address(business):
    
    business_df = df.query('BusinessName == @business')
    house = business_df.iloc[-1, 13]
    street = business_df.iloc[-1, 14]
    
    
    return str(int(house))+' ' +street

@app.callback(Output("histogram", "figure"),
             [Input('feature_type', 'value'),
             Input('business-name', 'value')])
def plot_hist(xaxis, business):
    business_df = df.query('BusinessName == @business')
    estimate = business_df.iloc[-1, -4] # use -4 for employees, -3 for FeesPaid
    type_value = business_df.iloc[0, 9]

    xaxis = 'NumberofEmployees'
    type_value = 'Office'
    lower_thresh, upper_thresh, _ = within_thresh(estimate, type_value, xaxis, df, 1)
    hist_data = df.query('BusinessType == @type_value').loc[:, xaxis]
    xrange = None
    fig = px.histogram(hist_data, x = xaxis,height=400)
    fig.update_xaxes(range=xrange)
    fig.update_layout(shapes=[
        dict(
        type= 'line',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= lower_thresh, x1= lower_thresh
        ),
        dict(
        type= 'line',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= upper_thresh, x1=upper_thresh
        ),
        dict(
        type= 'line',
        line_color='red',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= estimate, x1=estimate
        )
    ])
    return fig
            #fig.update_xaxes(tickangle=n_clicks*45)
            

        # dcc.Tab([
        #     dbc.Row([
        #         dbc.Col([
        #             html.Br(),
        #             html.Label([
        #                 'State Selection'], style={
        #         'color': '#522889', "font-weight": "bold"
        #     }),
        #             dcc.Dropdown(
        #                 id='table_state',
        #                 value='select your state',  
        #                 options=[{'label': state, 'value': state} for state in df['state'].sort_values().unique()],
        #                 multi=True,
        #                 placeholder='Select a State'
        #             ),
        #             html.Br(),
        #             html.Label(['Wine Type'], style={
        #         'color': '#522889', "font-weight": "bold"
        #     }
        #             ),
        #             dcc.Dropdown(
        #                 id='table_variety',
        #                 value='select a variety', 
        #                 placeholder='Select a Variety', 
        #                 multi=True
        #             ),
        #             html.Br(),
        #             html.Label(['Price Range'], style={
        #         'color': '#522889', "font-weight": "bold"
        #     }
        #             ),
        #             dcc.RangeSlider(
        #                 id='table_price',
        #                 min=df['price'].min(),
        #                 max=df['price'].max(),
        #                 value=[df['price'].min(), df['price'].max()],
        #                 marks = {4: '$4', 25: '$25', 50: '$50', 75: '$75', 100: '$100','color': '#7a4eb5'}
        #             ),
        #             html.Label(['Points Range'], style={
        #         'color': '#522889', "font-weight": "bold"
        #     }
        #             ),
                    
        #             dcc.RangeSlider(
        #                 id='table_points',
        #                 min=df['points'].min(),
        #                 max=df['points'].max(),
        #                 value=[df['points'].min(), df['points'].max()],
        #                 marks = {80: '80', 85: '85', 90: '90', 95: '95', 100: '100'}, className='slider'
        #                 ),
        #             html.Br(),
        #             dbc.Button('Reset', id = 'reset-btn-2', n_clicks=0, className='reset-btn-2'),
        #         ],style={'border': '1px solid', 'border-radius': 3, 'padding': 15, 'margin-top': 22, 'margin-bottom': 22, 'margin-right': 0}, md=4),
        #         dbc.Col([
        #             html.Br(),
        #             html.Br(),
        #             dash_table.DataTable(
        #                 id='table',
        #                 columns=[{"name": col, "id": col} for col in display_df.columns[:]], 
        #                 data=display_df.to_dict('records'),
        #                 page_size=10,
        #                 sort_action='native',
        #                 filter_action='native',
        #                 style_header = {'textAlign': 'left'},
        #                 style_data = {'textAlign': 'left'},
        #                 style_cell_conditional=[
        #                     {'if': {'column_id': 'Title'},
        #                     'width': '50%'},
        #                     {'if': {'column_id': 'Price'},
        #                     'width': '9%'},
        #                     {'if': {'column_id': 'Points'},
        #                     'width': '10%'}],
        #                 style_cell={
        #                     'overflow': 'hidden',
        #                     'textOverflow': 'ellipsis',
        #                     'maxWidth': 0
        #                 },
        #             ),
        #         ], md=8)
        #     ]),
        #     dbc.Row([
        #         dbc.Col([
        #             html.Br(),
        #             html.Iframe(
        #                 id = 'table_plots',
        #                 style={'border-width': '0', 'width': '100%', 'height': '600px'})]),
        #         dbc.Col([
        #         dcc.Dropdown(
        #                 id='axis',
        #                 value='price',  
        #                 options=[{'label': "price", 'value': "price"}, 
        #                 {'label': "points", 'value': "points"}]
        #         ),
        #         html.Iframe(
        #                 id = 'heat_plot',
        #                 style={'border-width': '0', 'width': '100%', 'height': '100%'})])
        #         ])     
        # ],label='Data')]),

    












if __name__ == '__main__':
    app.run_server(debug=True)