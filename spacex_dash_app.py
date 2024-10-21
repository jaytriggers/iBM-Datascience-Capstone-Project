# Import required libraries
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

Data = spacex_df[['Launch Site','class']]
data = Data.groupby('Launch Site').sum().reset_index()
print(spacex_df[['Launch Site','class','Payload Mass (kg)','Booster Version Category']])

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
             style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    html.Div(['Select a Launch Site here',
               dcc.Dropdown(options=[
                   {'label': 'All Sites', 'value': 'All'},
                   {'label': 'CCAFS LC-40 Site', 'value': 'CCAFS LC-40'},
                   {'label': 'VAFB SLC-4E Site', 'value': 'VAFB SLC-4E'},
                   {'label': 'KSC LC-39A Site', 'value': 'KSC LC-39A'},
                   {'label': 'CCAFS SLC-40 Site', 'value': 'CCAFS SLC-40'}],
                   id='site-dropdown', value='All', searchable=True),
               ]),  # Add comma here
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.Div([html.P("Payload range (Kg):"),
             dcc.RangeSlider(
                id='payload-slider',
                min =0, max =10000 , step =2500,
                marks = {0:'0',2500:'2500',5000:'5000',7500:'7500',10000:'10000'},
                value = [min_payload,max_payload])]),
    
    # TASK 3: Add a slider to select payload range
    # Add your range slider here

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Defining the callback decorator
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
# Defining the callback function
def select_Launch_Site(selected_site):
    if selected_site == 'All':
        data = spacex_df[['Launch Site', 'class']]
        data = data.groupby('Launch Site').sum().reset_index()
        # Defining pie chart 
        fig = go.Figure(go.Pie(labels=data['Launch Site'], values=data['class'], hole=.3))
        fig.update_layout(title='Total Success Launches by Site')
        return fig
    else:
        data = spacex_df[spacex_df['Launch Site'] == selected_site]
        data = data.groupby('class').size().reset_index(name = 'count')

        # Plot pie chart for selected site showing success/failure
        fig = go.Figure(go.Pie(labels=['Failure', 'Success'], values=data['count'], hole=.3))
        fig.update_layout(title=f'Success vs Failure for {selected_site}')
        return fig

#Defining the callback decorator for the scatter plot 
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),  # Dropdown for Launch Site
     Input(component_id='payload-slider', component_property='value')]  # RangeSlider for Payload
)
def payloadMass_selection(selected_site, selected_payload_range):
    # Unpack the range selected by the RangeSlider
    min_payload, max_payload = selected_payload_range  # Get the lower and upper bounds

    # Filter the dataframe based on the selected site
    data = spacex_df[['Launch Site', 'class', 'Payload Mass (kg)', 'Booster Version Category']]

    if selected_site == 'All':
        # Filter the data to show only rows where the payload mass is within the selected range
        data = data[(data['Payload Mass (kg)'] >= min_payload) & (data['Payload Mass (kg)'] <= max_payload)]
    else:
        # Filter by both the selected site and the payload mass range
        data = data[(data['Launch Site'] == selected_site) & 
                    (data['Payload Mass (kg)'] >= min_payload) & 
                    (data['Payload Mass (kg)'] <= max_payload)]

    # Create the scatter plot with the filtered data
    fig = go.Figure(
        go.Scatter(
            x=data['Payload Mass (kg)'], 
            y=data['class'], 
            mode='markers',
            marker=dict(color=data['Booster Version Category'].astype('category').cat.codes)
        )
    )

    # Update layout with title
    fig.update_layout(title=f'Correlation between Payload and Success for {selected_site}')
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
