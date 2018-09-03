
import os

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import pandas as pd
import plotly.graph_objs as go

########################################
##
## prepping data
##
########################################

df = pd.read_csv('https://raw.githubusercontent.com/GWarrenn/dc-stop-frisk-dash/master/nbh_sf_df.csv')

##stop and frisk by month within neighborhood

nbh_counts = df.groupby(['neighborhood', 'year_month']).size().reset_index(name='counts')
nbh_counts['moving_avg'] = nbh_counts.groupby('neighborhood')['counts'].rolling(4).mean().reset_index(0,drop=True)

##stop and frisk by race within neighborhood

race_counts = df.groupby(['neighborhood', 'race_ethn']).size().reset_index(name='counts')

race_counts.loc[race_counts['race_ethn'] == 'White', 'order'] = 1
race_counts.loc[race_counts['race_ethn'] == 'Black', 'order'] = 2
race_counts.loc[race_counts['race_ethn'] == 'Hispanic/Latino', 'order'] = 3
race_counts.loc[race_counts['race_ethn'] == 'Asian', 'order'] = 4
race_counts.loc[race_counts['race_ethn'] == 'Unknown', 'order'] = 5

race_counts = race_counts[race_counts['order'].isin([1,2,3,4,5])]

race_counts = race_counts.sort_values(by=['neighborhood','order'])

##stop and frisk by time of day within neighborhood

df['datetime'] = pd.to_datetime(df['incident_date'])
df['hour'] = df.datetime.dt.hour

tod_counts = df.groupby(['neighborhood', 'hour']).size().reset_index(name='counts')
total_day_counts = df.groupby(['neighborhood']).size().reset_index(name='total_counts')

tod_counts = pd.merge(tod_counts,total_day_counts,on='neighborhood')
tod_counts['pct'] = tod_counts['counts'] / tod_counts['total_counts']

## building a neighborhood color palette to get consistant coloring

color_palette = {'Brightwood Park, Crestwood, Petworth' : '#592f7c',
					'Brookland, Brentwood, Langdon' : '#c1a506',
					'Capitol Hill, Lincoln Park' : '#ac5503',
					'Capitol View, Marshall Heights, Benning Heights' : '#8c2b0d',
					'Cathedral Heights, McLean Gardens, Glover Park' : '#68a59f',
					'Cleveland Park, Woodley Park, Massachusetts Avenue Heights, Woodland-Normanstone Terrace' : '#125ca5',
					'Colonial Village, Shepherd Park, North Portal Estates' : '#b9f43b',
					'Columbia Heights, Mt. Pleasant, Pleasant Plains, Park View' : '#6596e7',
					'Congress Heights, Bellevue, Washington Highlands' : '#d1aaad',
					'Deanwood, Burrville, Grant Park, Lincoln Heights, Fairmont Heights' : '#b38640',
					'Douglas, Shipley Terrace' : '#cda1e5',
					'Downtown, Chinatown, Penn Quarters, Mount Vernon Square, North Capitol Street' : '#dfbf1e',
					'Dupont Circle, Connecticut Avenue/K Street' : '#484d36',
					'Eastland Gardens, Kenilworth' : '#c89a5c',
					'Edgewood, Bloomingdale, Truxton Circle, Eckington' : '#f733a9',
					'Fairfax Village, Naylor Gardens, Hillcrest, Summit Park' : '#d7d645',
					'Friendship Heights, American University Park, Tenleytown' : '#c38239',
					'Georgetown, Burleith/Hillandale' : '#be73db',
					'Hawthorne, Barnaby Woods, Chevy Chase' 'Historic Anacostia' : '#32dcf4',
					'Howard University, Le Droit Park, Cardozo/Shaw' : '#129b58',
					'Ivy City, Arboretum, Trinidad, Carver Langston' : '#ec9582',
					'Kalorama Heights, Adams Morgan, Lanier Heights' : '#ffc6d0',
					'Lamont Riggs, Queens Chapel, Fort Totten, Pleasant Hill' : '#dbadd9',
					'Mayfair, Hillbrook, Mahaning Heights' : '#e13074',
					'Near Southeast, Navy Yard' : '#acfb9e',
					'North Cleveland Park, Forest Hills, Van Ness' : '#ca74f7',
					'North Michigan Park, Michigan Park, University Heights' : '#00f4e9',
					'River Terrace, Benning, Greenway, Dupont Park' : '#309ea2',
					'Shaw, Logan Circle' : '#0695bd',
					'Sheridan, Barry Farm, Buena Vista' : '#b206d2',
					'Southwest Employment Area, Southwest/Waterfront, Fort McNair, Buzzard Point' : '#dc65ae',
					'Spring Valley, Palisades, Wesley Heights, Foxhall Crescent, Foxhall Village, Georgetown Reservoir' : '#b908e2',
					'Takoma, Brightwood, Manor Park' : '#474d0f',
					'Twining, Fairlawn, Randle Highlands, Penn Branch, Fort Davis Park, Fort Dupont' : '#6ab814',
					'Union Station, Stanton Park, Kingman Park' : '#fed208',
					'West End, Foggy Bottom, GWU' : '#2130ca',
					'Woodland/Fort Stanton, Garfield Heights, Knox Hill' : '#8f9761',
					'Woodridge, Fort Lincoln, Gateway' : '#c95bd5'}

#################################################
##
## setting up dash plot elements
##
#################################################

app = dash.Dash(__name__,csrf_protect=False)

server = app.server

app.layout = html.Div(children=[
    html.Div([
    	html.Div(
            [
                html.H1(
                    'DC Stop and Frisk by Neighborhood',
                    className='eight columns',
                    style={'backgroundColor':'#F4F4F8',
                    		'font-family': 'Helvetica'}
                ),
            ],
            className='row'
        ),
        html.P(['Data Provided by DC Metropolitan Police Department ',
    		html.A('(Link to data)', 
    			href='https://mpdc.dc.gov/publication/stop-and-frisk-data-and-explanatory-notes',
    			style ={'font-family': 'Helvetica',
    					'font-size':'16px'})],    		
    		style ={'font-family': 'Helvetica',
    				'font-size':'16px'}),
    	html.P(['Visualization created by August Warren ',
    		html.A('https://gwarrenn.github.io/', 
    			href='https://gwarrenn.github.io/',
    			style ={'font-family': 'Helvetica',
    					'font-size':'16px'})],    		
    		style ={'font-family': 'Helvetica',
    				'font-size':'16px'}),			  
        dcc.Dropdown(
	    	id = 'nbh-filter',
	    	options=[
	        	{'label': i, 'value': i} for i in df.neighborhood.unique()
	    	],
	    	value=['Brightwood Park, Crestwood, Petworth',
	    			'Shaw, Logan Circle',
	    			'North Michigan Park, Michigan Park, University Heights'],
	    	multi=True
		),
	],style={'backgroundColor':'#F4F4F8'}),  
    dcc.Graph(id='ts-graph',
    	style={'width': '50%', 
    			'height': '70%',
    			'display': 'inline-block'},
    ),
    dcc.Graph(id='bar-race-graph',
    	style={'width': '50%', 
    			'height': '70%',
    			'display': 'inline-block'},
    ),
    dcc.Graph(id='bar-tod-graph'
    )
])

@app.callback(
	Output('ts-graph', 'figure'), 
	[Input('nbh-filter', 'value')])
def update_graph(selected_dropdown_value):
	traces = []
	for nbh in selected_dropdown_value:
	    filtered_df = nbh_counts[nbh_counts['neighborhood'] == nbh]
	    trace = {
	    	'x': filtered_df['year_month'], 
	    	'y': filtered_df['counts']}
	    traces.append(go.Scatter(trace,
	    	name=nbh,
	    	mode = 'markers',
	    	marker = dict(color = color_palette[nbh])))
	    trace = {
	    	'x': filtered_df['year_month'], 
	    	'y': filtered_df['moving_avg']}
	    traces.append(go.Scatter(trace,
	    	name=nbh,
	    	line = dict(width = 4),
	    	marker = dict(color = color_palette[nbh])))	    
	figure = dict(data=traces,
				layout=dict(
					paper_bgcolor = '#F4F4F8',
					plot_bgcolor = '#F4F4F8',
					showlegend=False,
					title='Total Stop and Frisk by Month within Neighborhood'
				),
    			style={'width': '50%', 
    				'height': '70%',
    				'display': 'inline-block'}
			)
	return figure

@app.callback(
	Output('bar-race-graph', 'figure'), 
	[Input('nbh-filter', 'value')])
def update_graph(selected_dropdown_value):
	traces = []
	for nbh in selected_dropdown_value:
	    filtered_df = race_counts[race_counts['neighborhood'] == nbh]
	    trace = {
	    	'x': filtered_df['race_ethn'], 
	    	'y': filtered_df['counts']}
	    traces.append(go.Bar(trace,
	    	name=nbh,
	    	marker = dict(color = color_palette[nbh])))   
	figure = dict(data=traces,
				layout=dict(
					paper_bgcolor = '#F4F4F8',
					plot_bgcolor = '#F4F4F8',
					showlegend=False,
					title='Total Stop and Frisk by Race/Ethnicity within Neighborhood'
				),
				style={'width': '50%', 
    				'height': '70%',
    				'display': 'inline-block'}
			)
	return figure


@app.callback(
	Output('bar-tod-graph', 'figure'), 
	[Input('nbh-filter', 'value')])
def update_graph(selected_dropdown_value):
	traces = []
	for nbh in selected_dropdown_value:
	    filtered_df = tod_counts[tod_counts['neighborhood'] == nbh]
	    trace = {
	    	'x': filtered_df['hour'], 
	    	'y': filtered_df['pct']}
	    traces.append(go.Bar(trace,
	    	name=nbh,
	    	marker = dict(color = color_palette[nbh])))   
	figure = dict(data=traces,
				layout=dict(
					paper_bgcolor = '#F4F4F8',
					plot_bgcolor = '#F4F4F8',
					showlegend=False,
					title='Total Stop and Frisk by Hour within Neighborhood',
					yaxis=dict(tickformat=".0%")
				),
				style={'width': '100%', 
    				'height': '100',
    				'display': 'inline-block'}
			)
	return figure

if __name__ == '__main__':
    app.run_server(debug=True)
