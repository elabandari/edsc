import dash
import dash_html_components as html
import dash_core_components as dcc
import altair as alt
import pandas as pd
import dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import plotly as py
import plotly.express as px
import plotly.graph_objects as go
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from scipy import stats

import plotly.io as pio

# pio.templates.default = "simple_white"


alt.data_transformers.disable_max_rows()

########## Additional Data Filtering ###########################################
# df = pd.read_csv('data/processed/business_data.csv', sep=';') #data/processed/cleaned_data.csv

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
    if column == 'Total Fees Paid':
        a = data.groupby('businessname').sum().reset_index()
        b = data.loc[:,['businessname','BusinessType']]
        data = pd.merge(a, b, how="left", on="businessname").drop_duplicates()
        column = 'FeePaid'

    mean_df = data.groupby('BusinessType').mean()
    sd_df = data.groupby('BusinessType').std()
    
    mean = mean_df.loc[businesstype, column]
    sd = float(sd_df.loc[businesstype, column])
    
    upper_thresh = mean + sd_away*sd 
    lower_thresh = mean - sd_away*sd

    if lower_thresh < 0:
        lower_thresh = 0 

    if float(value) > upper_thresh or float(value) < lower_thresh: 
        return lower_thresh, upper_thresh, False
    else: 
        return lower_thresh, upper_thresh, True

server = Flask(__name__)
app = dash.Dash(__name__ , external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
app.title = "Fraudulent Business Detection"

app.server.config['SQLALCHEMY_DATABASE_URI'] = "postgres+psycopg2://postgres:one-percent@130.211.113.135:5432/postgres"
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app.server)

df = pd.read_sql_table('license_data', con=db.engine)
address_quantile_df = pd.read_sql_table('address_quantiles', con=db.engine)
address_count_df = pd.read_sql_table('address_counts', con=db.engine)
address_frequencies_df = pd.read_sql_table('address_frequencies', con=db.engine)
registered_url_df = pd.read_sql_table('registered_urls', con=db.engine)
possible_url_df = pd.read_sql_table('possible_urls', con=db.engine)
url_info_df = pd.read_sql_table('url_info', con=db.engine)

jb_emp_post = pd.read_sql_table('jobbank_employer_posting', con=db.engine)
jb_emp_post = jb_emp_post.rename(columns={'business_name': 'BusinessName'})

# business_info = pd.read_sql_table('business_info', con=db.engine)
# business_info = business_info.rename(columns={'business_name': 'BusinessName'})

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
            html.H1('Fraudulent Business Detection', style={'text-align': 'center', 'color': 'white', 'font-size': '40px', 'font-family': 'Georgia'}),
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
                    dcc.Dropdown(
                        id='business-name',
                        options=[{'label': name, 'value': name} for name in list(df['businessname'].dropna().unique())],
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
                    ], style={'border': '1px solid', 'border-radius': 3, 'margin-top': 22, 'margin-bottom': 15, 'margin-right': 0, 'height' : 350}, md=4,
                ),
                # dbc.Col([], md=1),
                # dbc.Col([
                #     html.Br(),
                #     html.Br(),
                #     dbc.Row([dbc.Card([
                #         dbc.CardHeader('Features Beyond 1-SD away from mean'),
                #         dbc.CardBody(id='score', style={'color': '#0F5DB6', 'fontSize': 18,  'height': '70px'}),
                #     ]
                #     )]),
                #     html.Br(),
                # ], md = 2),
                dbc.Col([
                    dcc.Graph(id='pie-chart',
                             figure = {'layout': go.Layout(margin={'b': 0})})
                ],)

                ]),
            dbc.Row([
                    dbc.Col([
                        html.Br(),
                        dbc.CardColumns([
                            dbc.Card([
                                dbc.CardHeader(html.H4('Website URL')),
                                dbc.CardBody(id='insight-1'),
                            ], color = 'primary', outline=True),
                            dbc.Card([
                                dbc.CardHeader(html.H4('Website Validity')),
                                dbc.CardBody(id='insight-2')

                            ], color = 'primary', outline=True),
                            dbc.Card([
                                dbc.CardHeader('Features Beyond 1-SD away from mean'),
                                dbc.CardBody(id='score'),
                            ], color = 'primary', outline=True),
                            dbc.Card([
                                dbc.CardHeader(html.H4('Addresses Listed')),
                                dbc.CardBody(id='insight-4'),
                            ], color = 'primary', outline=True),
                            dbc.Card([
                                dbc.CardHeader(html.H4('Common Addresses')),
                                dbc.CardBody(id='insight-5'),
                            ], color = 'primary', outline=True)
                            # dbc.CardHeader('Key Insights:', 
                            # style={'fontWeight': 'bold', 'color':'white','font-size': '22px', 'backgroundColor':'#0F5DB6', 'height': '50px'}),
                        ]),
                    ], md = 6, style={'border': '1px solid', 'border-radius': 3, 'margin-top': 22, 'margin-bottom': 15, 'margin-right': 0}),
                    dbc.Col([
                    dbc.Row([
                            dcc.Graph(id='histogram'),         
                        ]),
                        dcc.Dropdown(
                                id='feature_type',
                                value='Number of Employees',
                                options = [{'label': col, 'value': col} for col in ['Fee Paid', 'Number of Employees', 'Total Fees Paid', 'Missing Values']],
                                placeholder='Select a Feature', 
                                multi=False
                            ),
                        dcc.Dropdown(
                                id='std',
                                options = [{'label': col, 'value': col} for col in [1,2,3]],
                                placeholder='Select a standard dev', 
                                value='',
                                multi=False
                            ),
                    html.Br(), 
                    ],md = 6),
                ]),
            ]),
    ])


@app.callback(Output('insight-1', 'children'),
             Input('business-name', 'value'))
def url_presence(business):
    try:
        website = registered_url_df[registered_url_df['businessname'] == business].url.iat[0]
        return f"{website}"
    except IndexError:
        try:
            possible_website = possible_url_df[possible_url_df['businessname'] == business].iloc[0]
            return f"{possible_website['url']} *estimate: {possible_website['prob']}% confident"
        except:
            return f"No website found"

@app.callback(Output('insight-2', 'children'),
             Input('business-name', 'value'))
def time_online(business):
    try :
        filtered_url_df = registered_url_df[registered_url_df['businessname'] == business]
        url = filtered_url_df['url'].iat[0]
        print(url)
        url_time_df =url_info_df[url_info_df['url'] == url]
        url_time_df = url_time_df.set_index('url')
        reg_time = pd.to_datetime(url_time_df.loc[url, 'register_date'])
        reg_time = reg_time.strftime('%B') + ' ' + reg_time.strftime('%Y')
        exp_time = pd.to_datetime(url_time_df.loc[url, 'expire_date'])
        if datetime.now() < exp_time:
            conj = 'has'
            exp_time = 'present'
        else: 
            conj = 'was'
            exp_time = pd.to_datetime(url_time_df.loc['url', 'expire_date'])
            exp_time = exp_time.strftime('%B') + ' ' + exp_time.stftime('%Y')
        if time_online:
            insight = f"The website {conj} been online from {reg_time} to {exp_time}"
        elif time_online:
                insight = 'No website available'
        return insight
    except (KeyError, IndexError):
        return 'No website information available'

# @app.callback(Output('insight-3', 'children'),
#              Input('business-name', 'value'))
# def website_online(business):
    
#     number_addresses = ''
#     # business_df = df.query('BusinessName == @business')
#     # domain_length = business_df.iloc[-1, 'time_online']
#     if time_online:
#         insight = f"The website has been online: {time_online}"
#     if time_online:
#         insight = 'No website available'
#     return insight

@app.callback(Output('insight-4', 'children'),
            Input('business-name', 'value'))
def address_quantile(business):
    count = address_count_df[address_count_df.BusinessName == business].full_adress.iat[0]
    biztype = df[df.businessname == business].BusinessType.iloc[0]
    quantile = address_quantile_df[address_quantile_df.BusinessType == biztype]['quantile'].iat[0]

    if count >= quantile:
        return f"This business has {count} addresses. This is in the top 1% in the {biztype} category"
    else:
        return f"This business has {count} addresses."

@app.callback(Output('insight-5', 'children'),
            Input('business-name', 'value'))
def address_frequency(business):
    address = df[df.businessname == business].iloc[0]
    address_text  = ' '.join(filter(None, address[['House', 'Street', 'City', 'Province','Country','PostalCode']]))

    try: 
        address_f = address_frequencies_df[address_frequencies_df.full_adress == address_text]['BusinessName'].iat[0]

        if stats.percentileofscore(address_frequencies_df.BusinessName.values, address_f) >= 99:
            return f'This address has {address_f} businesses listed at it. That is in the top 1%'
        else:
            return f'This address has {address_f} businesses listed at it'
    except IndexError:
        return f'No addresses for this business'

def calculate_scores(business):
    business = 'Time Education Inc'
    toy3 = {'BusinessName':"Time Education Inc", 'num_posting' : '0'}
    toy1 = {'BusinessName':"Time Education Inc", 'url' : 'www.google.ca'}
    toy2 = {'url' : 'www.google.ca', 'register_date' : '1999-01-02', 'expire_date': '2022-09-29'}
    url_df = pd.DataFrame(toy1, index=[1])
    url_info = pd.DataFrame(toy2, index=[1])
    jb_emp_post = pd.DataFrame(toy3, index=[1])
    filtered_url_df = url_df.query('BusinessName == @business')
    # has registered website
    # longevity of website
    # has more than 1 employee
    # number of missing inputs 

    ###############################
    # length of time online 

    if url_df.loc[1,'url'] == url_df.loc[1,'url']:  # checks if nan 
        url_color = 'green'
    else: 
        url_color = 'red'
    
    url = url_df.loc[1, 'url']
    url_time_df =url_info.query('url == @url')
    url_time_df = url_time_df.set_index('url')
    reg_time = pd.to_datetime(url_time_df.loc[url, 'register_date'])
    exp_time = pd.to_datetime(url_time_df.loc[url, 'expire_date'])
    time_diff = exp_time - reg_time

    if time_diff < timedelta(7) or url_color == 'red':
        longevity_color = 'red'
    elif time_diff < timedelta(365):
        longevity_color = 'yellow'
    else:
        longevity_color='green'

    ##############################
    # Job Posting

    # jb_emp_post = pd.merge(df, jb_emp_post, how='left', on='businessname')
    # num_posting = jb_emp_post.query('BusinessName == @business').iloc[0,-1]
    # print(num_posting)

    # if int(num_posting) > 0:
    #     job_post_color = 'green'
    # else:
    #     job_post_color = 'red'

    #############################

    scores = [url_color, longevity_color, 'job_post_color', 'red']
    return scores

@app.callback(Output('pie-chart', 'figure'),
             [Input('feature_type', 'value'),
            Input('business-name', 'value')])
def plot_donut(score, business):

    score_list = calculate_scores(business)
    df_dict = {'feat': ['website', 'reviews', 'job posting', 'other'],
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
    
    address = df[df.businessname == business].iloc[0]
    address_text  = ' '.join(filter(None, address[['House', 'Street', 'City', 'Province','Country','PostalCode']]))
    
    return  address_text

@app.callback(Output("histogram", "figure"),
             [Input('feature_type', 'value'),
             Input('business-name', 'value'),
             Input('std', 'value')])
def plot_hist(xaxis, business,sd):
 
    xrange = None
    ci_color = 'black'
    business_df = df.query('businessname == @business')
    type_value = business_df.iloc[0, 9]
    #business_join = pd.merge(business_info, df, how='left', on='BusinessName')

    if sd == '':
        sd = 1

    if xaxis == 'Fee Paid':
        clean_name = 'Fees Paid'
        xaxis = 'FeePaid by'
        index = -4
        estimate = business_df.iloc[-1, index] # use -4 for employees, -3 for FeesPaid
        hist_data = df.query('BusinessType == @type_value').loc[:, xaxis]
        lower_thresh, upper_thresh, _ = within_thresh(estimate, type_value, xaxis, df, sd)
        xrange=[0, upper_thresh*1.25]

    elif xaxis == 'Number of Employees':
        clean_name = 'Number of Employees at'
        xaxis = 'NumberofEmployees'
        index = -5
        estimate = business_df.iloc[-1, index]
        hist_data = df.query('BusinessType == @type_value').loc[:, xaxis]
        lower_thresh, upper_thresh, _ = within_thresh(estimate, type_value, xaxis, df, sd)
        xrange=[0, upper_thresh*1.25]
        
    elif xaxis == 'Total Fees Paid':
        clean_name = 'Total Fees Paid by'
        estimate = df.groupby('businessname').sum().loc[business, "FeePaid"]
        hist_data = df.groupby('businessname').sum().loc[:, 'FeePaid']
        lower_thresh, upper_thresh, _ = within_thresh(estimate, type_value, xaxis, df, sd)
        xaxis = 'FeePaid'
        xrange=[0, upper_thresh*1.25]
    
   # elif xaxis == 'turnover':
        # business_info.query('BusinessName == @business')
        # estimate = business_df.iloc[-1, 2]
        # hist_data = df.query('BusinessType == @type_value')
       #estimate = business_join.groupby('BusinessName')

    elif xaxis == 'Missing Values':
        clean_name = 'Missing Values in'
        business_df['Average Number of Missing Values'] = business_df.isnull().sum(axis=1)
        estimate = business_df.loc[:,'Average Number of Missing Values'].sum()/business_df.loc[:,'Average Number of Missing Values'].mean()
        missing_df = pd.DataFrame.copy(df)
        missing_df['Average Number of Missing Values'] = df.isnull().sum(axis=1)
        total_missing = missing_df.groupby('businessname').sum().loc[:,'Average Number of Missing Values']
        count_reports = missing_df.groupby('businessname').count().loc[:,'Average Number of Missing Values']
        hist_data = total_missing/count_reports
        xaxis = 'Average Number of Missing Values'
        lower_thresh = estimate
        upper_thresh = estimate
        ci_color = 'red'


    fig = px.histogram(hist_data, x = xaxis,height=400)
    fig.update_xaxes(range=xrange)
    fig.update_layout(shapes=[
        dict(
        type= 'line',
        line_color = ci_color,
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= lower_thresh, x1= lower_thresh
        ),
        dict(
        type= 'line',
        line_color = ci_color,
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= upper_thresh, x1=upper_thresh
        ),
        dict(
        type= 'line',
        line_color='red',
        yref= 'paper', y0= 0, y1= 1,
        xref= 'x', x0= estimate, x1=estimate
        ),
    ], title=f"Distribution of {clean_name} {type_value} companies"
    )
    return fig

@app.callback(Output("score", "children"),
             [Input('feature_type', 'value'),
             Input('business-name', 'value'),
             Input('std', 'value')])
def count_sigs(xaxis, business,sd):
    business_df = df.query('businessname == @business')
    type_value = business_df.iloc[0, 9]
    featlist = ['FeePaid', 'NumberofEmployees', 'Total Fees Paid']

    sd = 1

    for feat in featlist:

        if feat == 'FeePaid':
            index = -4
            estimate = business_df.iloc[-1, index] # use -5 for employees, -4 for FeesPaid
            hist_data = df.query('BusinessType == @type_value').loc[:, feat]
            _, __, containsFee = within_thresh(estimate, type_value, feat, df, sd)

        elif feat == 'NumberofEmployees':
            index = -5
            estimate = business_df.iloc[-1, index]
            hist_data = df.query('BusinessType == @type_value').loc[:, feat]
            _, __, containsEmp= within_thresh(estimate, type_value, feat, df, sd)
            
        elif feat == 'Total Fees Paid':
            estimate = df.groupby('businessname').sum().loc[business, "FeePaid"]
            hist_data = df.groupby('businessname').sum().loc[:, 'FeePaid']
            _, __, containstotfee = within_thresh(estimate, type_value, feat, df, sd)

    sum_score = containsFee + containsEmp + containstotfee
    output = len(featlist) - sum_score
    return output




# last year that they gave info to public 
# number of employees
# operating revenue 
# glassdoor presence






if __name__ == '__main__':
    app.run_server(debug=True)