import dash
import dash_html_components as html
import dash_core_components as dcc
import altair as alt
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from scipy import stats

alt.data_transformers.disable_max_rows()

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

server = Flask(__name__)
app = dash.Dash(__name__ , external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "Fraudulent Business Detection"

app.server.config['SQLALCHEMY_DATABASE_URI'] = "postgres+psycopg2://postgres:one-percent@130.211.113.135:5432/postgres"
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app.server)

class Licence(db.Model):
    __tablename__ = "license_data"

    FolderYear = db.Column(db.Integer)
    LicenceRSN = db.Column(db.Integer)
    LicenceNUmber = db.Column(db.String(40))
    LicenceRevisionNumber = db.Column(db.Integer)
    BusinessName = db.Column(db.String(40))
    BusinessTradeName = db.Column(db.String(40))
    Status = db.Column(db.String(40))
    IssuedDate = db.Column(db.String(40))
    ExpiredDate = db.Column(db.String(40))
    BusinessType = db.Column(db.String(40))
    BusinessSubType = db.Column(db.String(40))
    Unit = db.Column(db.String(40))
    UnitType = db.Column(db.String(40))
    House = db.Column(db.String(40))
    Street = db.Column(db.String(40))
    City = db.Column(db.String(40))
    Province = db.Column(db.String(40))
    Country = db.Column(db.String(40))
    PostalCode = db.Column(db.String(40))
    LocalArea = db.Column(db.String(40))
    NumberOfEmployees = db.Column(db.Float)
    FeePaid = db.Column(db.Float)
    ExtractDate = db.Column(db.String(40))
    Geom = db.Column(db.String(40))
    Id = db.Column(db.Integer, nullable=False, primary_key=True)


    def __init__(self, FolderYear, LicenceRSN, LicenceNUmber,LicenceRevisionNumber,BusinessName,BusinessTradeName,Status,IssuedDate,ExpiredDate,BusinessType,BusinessSubType,Unit,UnitType,House,Street,City,Province,Country,PostalCode,LocalArea,NumberOfEmployees,FeePaid,ExtractDate,Geom,Id):
        FolderYear = self.FolderYear
        LicenceRSN = self.LicenceRSN
        LicenceNUmber = self.LicenceNUmber
        LicenceRevisionNumber = self.LicenceRevisionNumber
        BusinessName = self.BusinessName
        BusinessTradeName = self.BusinessTradeName
        Status = self.Status
        IssuedDate = self.IssuedDate
        ExpiredDate = self.ExpiredDate
        BusinessType = self.BusinessType
        BusinessSubType = self.BusinessSubType
        Unit = self.Unit
        UnitType = self.UnitType
        House = self.House
        Street = self.Street
        City = self.City
        Province = self.Province
        Country = self.Country
        PostalCode = self.PostalCode
        LocalArea = self.LocalArea
        NumberOfEmployees = self.NumberOfEmployees
        FeePaid = self.FeePaid
        ExtractDate = self.ExtractDate
        Geom = self.Geom
        Id = self.Id

df = pd.read_sql_table('license_data', con=db.engine)

class AddressQuantile(db.Model):
    __tablename__ = 'address_quantiles'

    BusinessType = db.Column(db.String(40), nullable=False, primary_key=True)
    Quantile = db.Column(db.Float)

    def __init__(self, BusinessType, Quantile):
        self.BusinessType = BusinessType
        self.Quantile = Quantile

address_quantile_df = pd.read_sql_table('address_quantiles', con=db.engine)

class AddressCounts(db.Model):
    __tablename__ = 'address_counts'

    BusinessType = db.Column(db.String(40), nullable=False, primary_key=True)
    Count = db.Column(db.Integer)

    def __init__(self, BusinessType, Count):
        self.BusinessType = BusinessType
        self.Count = Count

address_count_df = pd.read_sql_table('address_counts', con=db.engine)

class AddressFrequencies(db.Model):
    __tablename__ = 'address_frequencies'

    Address = db.Column(db.String(40), nullable=False, primary_key=True)
    Frequency = db.Column(db.Integer)

    def __init__(self, Address, Frequency):
        self.Address = Address
        self.Frequency = Frequency

address_frequencies_df = pd.read_sql_table('address_frequencies', con=db.engine)

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
                    html.Label(id='address'),  # Not capturing unit number
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
                            dbc.CardBody(id='insight-1', style={'color': '#2EC9F0', 'fontSize': 18,  'height': '70px'}),
                            html.Br(),
                            dbc.CardBody(id='insight-2', style={'color': '#522889', 'fontSize': 18,  'height': '380px'}),
                            html.Br(),
                            dbc.CardBody(id='insight-3', style={'color': '#522889', 'fontSize': 18,  'height': '380px'}),
                            html.Br(),
                            dbc.CardBody(id='insight-4', style={'color': '#522889', 'fontSize': 18,  'height': '380px'}),
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
    
    time_online = '356 days'
    # business_df = df.query('BusinessName == @business')
    # domain_length = business_df.iloc[-1, 'time_online']
    if time_online:
        insight = f"The website has been online: {time_online}"
    if time_online:
        insight = 'No website available'
    return insight

@app.callback(Output('insight-3', 'children'),
            Input('business-name', 'value'))
def address_quantile(business):
    count = address_count_df[address_count_df.BusinessName == business].full_adress.iat[0]
    biztype = df[df.businessname == business].BusinessType.iloc[0]
    quantile = address_quantile_df[address_quantile_df.BusinessType == biztype]['quantile'].iat[0]

    if count >= quantile:
        return f"This business has {count} addresses. This is in the top 1% in the {biztype} category"
    else:
        return f"This business has {count} addresses."

@app.callback(Output('insight-4', 'children'),
            Input('business-name', 'value'))
def address_frequency(business):
    address = df[df.businessname == business].iloc[0]
    address_text  = ' '.join(address[['House', 'Street', 'City', 'Province','Country','PostalCode']])
    address_f = address_frequencies_df[address_frequencies_df.full_adress == address_text]['BusinessName'].iat[0]

    if stats.percentileofscore(address_frequencies_df.BusinessName.values, address_f) >= 99:
        return f'This address has {address_f} businesses listed at it. That is in the top 1%'
    else:
        return f'This address has {address_f} businesses listed at it'

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

@app.callback(Output('address', 'children'),
             [Input('business-name', 'value')])
def update_address(business):
    
    business_df = df.query('businessname == @business')
    house = business_df.iloc[-1, 13]
    street = business_df.iloc[-1, 14]
    
    
    return str(float(house))+' ' +street

@app.callback(Output("histogram", "figure"),
             [Input('feature_type', 'value'),
             Input('business-name', 'value')])
def plot_hist(xaxis, business):
    print(business)
    if not business:
        business = "Golden Trim Enterprises Inc"
    business_df = df.query('businessname == @business')
    print(business_df.shape)
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