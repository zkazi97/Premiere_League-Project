"""
Zain Kazi
Premiere league Transfer Analysis
"""
#%% Import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

pio.renderers.default='browser'

#%% Read in data
df_transfer = pd.read_excel('C:/Users/zaink/Documents/Python Scripts/PremiereLeagueData.xlsx')

# Clean transfer data
df_transfer = df_transfer[df_transfer['year'] > 2009]
df_transfer['permanent'] = (df_transfer['fee'].str[0] == "£") | (df_transfer['fee'] == 'Free transfer')
df_permanent = df_transfer[df_transfer['permanent'] == True]

# Money spent and brought in by season
df_season = df_permanent.groupby(['season','transfer_movement'], as_index=False)['fee_cleaned'].sum()
df_year = df_transfer.groupby(['year','transfer_movement'], as_index=False)['fee_cleaned'].sum()
df_in = df_season[df_season['transfer_movement'] == 'in'].rename(columns = {"fee_cleaned":'Amount Spent'})
df_in['spent_negative'] = -df_in['Amount Spent']
df_out = df_season[df_season['transfer_movement'] == 'out'].rename(columns = {'fee_cleaned':'Amount Brought In'})
df_net = pd.merge(df_in,df_out, on = 'season').drop(columns = ['transfer_movement_x','transfer_movement_y'])
df_net['spent_negative'] = -df_net['Amount Spent']
df_net['Net Spending'] = df_net['Amount Brought In'] - df_net['Amount Spent']
df_net['spending_ratio'] = df_net['Amount Spent']/df_net['Amount Brought In']

# Money spent by team by season
df_team = df_permanent.groupby(['club_name','season','transfer_movement'], as_index=False)['fee_cleaned'].sum()
df_team = df_team.pivot(index='club_name', columns=['transfer_movement','season']).stack(level='season')
df_team = df_team.reset_index(level = ['club_name','season'])
df_team.columns = df_team.columns.droplevel()
df_team.columns = ['Club Name', 'Season','Amount Spent','Amount Brought In']
df_team = df_team.fillna(0)
df_team['Net Spending'] = df_team['Amount Brought In'] - df_team['Amount Spent']


# Spending of Top 6
Top6 = ['Arsenal FC','Chelsea FC','Liverpool FC','Manchester City','Manchester United','Tottenham Hotspur']

# Money spent and brought in by season
df_season_top = df_permanent[df_permanent['club_name'].isin(Top6)] .groupby(['season','transfer_movement'], as_index=False)['fee_cleaned'].sum()
df_top_in = df_season_top[df_season['transfer_movement'] == 'in'].rename(columns = {"fee_cleaned":'fee_in'})
df_top_out = df_season_top[df_season['transfer_movement'] == 'out'].rename(columns = {'fee_cleaned':'fee_out'})
df_top6 = pd.merge(df_top_in,df_top_out, on = 'season').drop(columns = ['transfer_movement_x','transfer_movement_y'])
df_top6['spent_negative'] = -df_top6['fee_in']
df_top6['net_spent'] = df_top6['fee_out'] - df_top6['fee_in']
df_top6['spending_ratio'] = df_top6['fee_in']/df_top6['fee_out']
df_net['Top6_Spent'] = df_top6['net_spent'] / df_net['Net Spending']

#%% Player Rating Data

# Read in player ratings
df_ratings = pd.read_csv('C:/Users/zaink/Documents/Python Scripts/WhoScoredFinal1.csv')
df_ratings_head = df_ratings.head(100)

# Filter by EPL after 2010 
seasons = []
for i in range(2010,2020):
    season = str(i) +'/'+ str(i+1)
    seasons.append(season)   
df_ratings = df_ratings[(df_ratings['seasonName'].isin(seasons)) & (df_ratings['tournamentShortName'] == 'EPL')]
df_ratings['player_name'] = df_ratings['name']
df_ratings['club_name'] = df_ratings['teamName']

# Group by player ratings for each team
df_ratings_avg = df_ratings.groupby(['player_name','club_name'], as_index=False)['rating'].mean()

# Find inconsistencies in team naming convention prior to merging
ratingTeams = np.sort(df_ratings_avg['club_name'].unique())
transferTeams = np.sort(df_permanent['club_name'].unique())
transferTeams = np.delete(transferTeams,np.where(transferTeams == 'Leeds United'))
teamNames = pd.DataFrame({'rating':ratingTeams,'transfer':transferTeams})

# Define function to change team names in ratings data to match team names in player data
def replaceTeamName(original, replacement):
    df_ratings_avg['club_name'] = np.where(df_ratings_avg['club_name'] == original,replacement, df_ratings_avg['club_name'])

# Change teams to create consistency in ratings and transfer data
replaceTeamName('Arsenal','Arsenal FC')
replaceTeamName('Birmingham','Birmingham City')
replaceTeamName('Blackburn','Blackburn Rovers')
replaceTeamName('Blackpool','Blackpool FC')
replaceTeamName('Bolton','Bolton Wanderers')
replaceTeamName('Bournemouth','AFC Bournemouth')
replaceTeamName('Brighton','Brighton & Hove Albion')
replaceTeamName('Burnley','Burnley FC')
replaceTeamName('Cardiff','Cardiff City')
replaceTeamName('Chelsea','Chelsea FC')
replaceTeamName('Everton','Everton FC')
replaceTeamName('Fulham','Fulham FC')
replaceTeamName('Huddersfield','Huddersfield Town')
replaceTeamName('Hull','Hull City')
replaceTeamName('Leicester','Leicester City')
replaceTeamName('Liverpool','Liverpool FC')
replaceTeamName('Middlesbrough','Middlesbrough FC')
replaceTeamName('Norwich','Norwich City')
replaceTeamName('Southampton','Southhampton FC')
replaceTeamName('Stoke','Stoke City')
replaceTeamName('Sunderland','Sunderland AFC')
replaceTeamName('Swansea','Swansea City')
replaceTeamName('Reading','Reading FC')
replaceTeamName('Tottenham','Tottenham Hotspur')
replaceTeamName('Watford','Watford FC')
replaceTeamName('West Ham','West Ham United')
replaceTeamName('Wigan','Wigan Athletic')

# Merge ratings and transfer data
df_merge = pd.merge(df_ratings_avg, df_permanent, on = ['player_name','club_name'], how = 'inner')
df_merge_in = df_merge[df_merge['transfer_movement'] == 'in']
df_merge_in['Top 6'] = df_merge_in['club_name'].isin(Top6)
df_merge_in['standard_fee'] = df_merge_in['fee_cleaned']
df_merge_in['Rating to Fee'] = df_merge_in['rating']/df_merge_in['fee_cleaned']

# Create team options for dropdown
teamNames = list(df_merge.club_name.unique())
teamOptions = [{"label": "All", "value": "All"}]
for team in sorted(teamNames):
    t = {"label": team, "value": team}
    teamOptions.append(t)


# # Spending distribution
# plt.style.use('ggplot')
# sns.color_palette("mako")
# sns.distplot(df_permanent['fee_cleaned'], kde = True)
# plt.xlabel('Transfer Fees')

# # Graph seasonal spending
# plt.figure(figsize=(12,10))
# sns.barplot(x = 'Amount Spent', y = 'season', data = df_net, color = 'red', orient = 'h', ci = None)
# sns.barplot(x = 'Amount Brought In', y = 'season', data = df_net, color = 'green', orient = 'h', ci = None)
# plt.ylabel('Season')
# plt.xlabel('Amount Spent (Millions)')
# plt.title('Transfer Activity in 2010s')

# # Graph seasonal spending
# plt.figure(figsize=(12,10))
# sns.barplot(x = 'Net Spending', y = 'season', data = df_net, palette='PuBuGn', orient = 'h', ci = None)
# plt.ylabel('Season')
# plt.xlabel('Net Spending (Millions)')
# plt.title('Transfer Activity in 2010s')

# # Graph seasonal spending
# plt.figure(figsize=(12,10))
# sns.barplot(x = 'spending_ratio', y = 'season', data = df_net, palette='PuBuGn', orient = 'h', ci = None)
# plt.ylabel('Season')
# plt.xlabel('Spending Ratio')
# plt.title('Ratio of British Pounds Spent vs. Brought in 2010s')

# # Graph spending trends 
# plt.figure(figsize=(12,6))
# sns.lineplot(x = 'season', y = 'Amount Spent', data = df_in, color = 'red', ci = None)
# sns.lineplot(x = 'season', y = 'Amount Brought In', data = df_out, color = 'blue', ci = None)
# sns.lineplot(x = 'season', y = 'Net Spending', data = df_net, color = 'green', ci = None)
# plt.axhline(0, 0, linestyle = '--', color = 'black')
# plt.ylabel('Amount Spent (Millions)')
# plt.xlabel('Season')
# plt.xticks(rotation=45)
# plt.title('Transfer Trends in 2000s')
# plt.legend(title='Transfer Activity', loc='upper left', labels=['Spent', 'Brought in', 'Net Spent'])
# plt.figure()

# # Scatter of Spending vs Ratings
# plt.figure(figsize=(18,6))
# sns.scatterplot(x = 'fee_cleaned', y = 'rating', data = df_merge_in)
# plt.xlabel('Transfer Fee')
# plt.ylabel('Average Rating')
# plt.title('Transfer Fees vs. Player Ratings')
# plt.figure()

# # Scatter of Spending vs Ratings
# plt.figure(figsize=(18,6))
# sns.scatterplot(x = 'fee_cleaned', y = 'rating', data = df_merge_in, hue = 'Top 6')
# plt.xlabel('Transfer Fee')
# plt.ylabel('Average Rating')
# plt.title('Transfer Fees vs. Player Ratings')
# plt.figure()

# # Scatter of Spending vs Ratings
# plt.figure(figsize=(18,6))
# sns.scatterplot(x = 'fee_cleaned', y = 'rating', data = df_merge_in[df_merge_in['club_name'].isin(Top6)], hue = 'club_name')
# plt.xlabel('Transfer Fee')
# plt.ylabel('Average Rating')
# plt.title('Transfer Fees vs. Player Ratings')
# plt.figure()

# Top 6 vs. Others
df_net['Top6_Spent'] = df_top6['net_spent'] / df_net['Net Spending']
plt.figure(figsize=(12,10))
sns.barplot(x = 'Top6_Spent', y = 'season', data = df_net, palette='icefire', orient = 'h', ci = None)
plt.ylabel('Season')
plt.xlabel('Percent Spent by Top 6')
plt.title('Top 6 Spending Percentage by Season')

# Import packages
import dash 
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Start data
app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# App layout (Dash Components)
app.layout = html.Div([

    html.H1("Premiere League Spending", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_year",
                 options=teamOptions,
                 multi=False,
                 value="All",
                 style={'width': "40%"}
                 ),

    html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_bee_map', figure={})

])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_bee_map', component_property='figure')],
    [Input(component_id='slct_year', component_property='value')]
)
def update_graph(option_slctd):
    print(option_slctd)
    print(type(option_slctd))
    container = "The team chosen by the user was: {}".format(option_slctd)
    fig = px.line(df_net, x='season', y=['Amount Brought In','Amount Spent','Net Spending'])
    if option_slctd != "All":
        global df_team
        df_team_slctd = df_team[df_team['Club Name'] == option_slctd]
        fig = px.line(df_team_slctd, x = 'Season',  y=['Amount Brought In','Amount Spent','Net Spending'])
    
    return container, fig



# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)



