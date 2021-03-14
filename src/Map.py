import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
from vega_datasets import data
import pandas as pd

from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# alt.data_transformers.disable_max_rows()
# df = pd.read_csv('../data/processed/cleaned_data.csv')
# df = df.query('country == "US" ') 

# Setup app and layout/frontend

server = Flask(__name__)
app = dash.Dash(__name__,server=server,  external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
app.server.config['SQLALCHEMY_DATABASE_URI'] = "postgres+psycopg2://postgres:one-percent@130.211.113.135:5432/postgres"

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
        Id = self.Id
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

print(df.columns)

app.layout = html.Div([
    html.Iframe(
        id='map',
        style={'border-width': '0', 'width': '100%', 'height': '400px'}),
    html.Label(['province Selection']),
    dcc.Dropdown(
        id='province-widget',
        value='Select your province',  # REQUIRED to show the plot on the first page load
        options=[{'label': province, 'value': province} for province in df['state'].unique()]),
    html.Br(),
    html.Label(['Price Range']),
    dcc.RangeSlider(
        id='price',
        min=df['price'].min(),
        max=df['price'].max(),
        value=[df['price'].min(), df['price'].max()]),
    html.Br(),
    html.Label(['Point Range']),
    dcc.RangeSlider(
        id='points',
        min=df['points'].min(),
        max=df['points'].max(),
        value=[df['points'].min(), df['points'].max()])])

# Set up callbacks/backend
@app.callback(
    Output('map', 'srcDoc'),
    Input('province-widget', 'value'),
    Input('price', 'value'),
    Input('points', 'value'))
def plot_altair(selected_province, price_value, points_value):
    
    if selected_province == 'Select your province':
        df_filtered = df
    else:
        df_filtered = df[df['Province'] == selected_province]

    state_map = alt.topo_feature(data.us_10m.url, 'states')
    df_filtered = df_filtered[(df_filtered['NumberofEmployees'] >= min(price_value)) & (df_filtered['NumberofEmployees'] <= max(price_value))]
    df_filtered = df_filtered[(df_filtered['FeePaid'] >= min(points_value)) & (df_filtered['FeePaid'] <= max(points_value))]
    states_grouped = df_filtered.groupby(['state', 'state_id'], as_index=False)
    wine_states = states_grouped.agg({'FeePaid': ['mean'],
                                      'NumberofEmployees': ['mean'],
                                      'value': ['mean'],
                                      'description': ['count']})

    wine_states.columns = wine_states.columns.droplevel(level=1)
    wine_states = wine_states.rename(columns={"state": "State",
                                              "state_id": "State ID",
                                              "description": "Num Reviews",
                                              "points": 'Ave Rating',
                                              "price": 'Ave Price',
                                              "value": 'Ave Value'})
    map_click = alt.selection_multi(fields=['state'])
    states = alt.topo_feature(data.us_10m.url, "states")

    colormap = alt.Scale(domain=[0, 100, 1000, 2000, 4000, 8000, 16000, 32000],
                         range=['#C7DBEA', '#CCCCFF', '#B8AED2', '#3A41C61',
                                '#9980D4', '#722CB7', '#663399', '#512888'])

    foreground = alt.Chart(states).mark_geoshape().encode(
        color=alt.Color('Num Reviews:Q',
                        scale=colormap),

        tooltip=[alt.Tooltip('State:O'),
                 alt.Tooltip('Ave Rating:Q', format='.2f'),
                 alt.Tooltip('Ave Price:Q', format='$.2f'),
                 alt.Tooltip('Ave Value:Q', format='.2f'),
                 alt.Tooltip('Num Reviews:Q')]
    ).mark_geoshape(
        stroke='black',
        strokeWidth=0.5
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(wine_states,
                             'State ID',
                             ['State', 'State ID', 'Ave Rating', 'Ave Price', 'Ave Value', 'Num Reviews'])
    ).project(
        type='albersUsa'
    )

    background = alt.Chart(states).mark_geoshape(
        fill='gray',
        stroke='dimgray'
    ).project(
        'albersUsa'
    )
    chart = (background + foreground).configure_view(
                height=400,
                width=570,
                strokeWidth=4,
                fill=None,
                stroke=None).encode(opacity=alt.condition(map_click, alt.value(1), alt.value(0.2))).add_selection(map_click)
    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)