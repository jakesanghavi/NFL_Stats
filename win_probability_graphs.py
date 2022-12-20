import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import os
from matplotlib.offsetbox import OffsetImage

# Dictionary of colors for the graph that map to team colors
COLORS = {'ARI': '#97233F', 'ATL': '#A71930', 'BAL': '#241773', 'BUF': '#00338D', 'CAR': '#0085CA', 'CHI': '#00143F',
          'CIN': '#FB4F14', 'CLE': '#FB4F14', 'DAL': '#B0B7BC', 'DEN': '#002244', 'DET': '#046EB4', 'GB': '#24423C',
          'HOU': '#C9243F', 'IND': '#003D79', 'JAX': '#136677', 'KC': '#CA2430', 'LA': '#002147', 'LAC': '#2072BA',
          'LV': '#C4C9CC', 'MIA': '#0091A0', 'MIN': '#4F2E84', 'NE': '#0A2342', 'NO': '#A08A58', 'NYG': '#192E6C',
          'NYJ': '#203731', 'PHI': '#014A53', 'PIT': '#FFC20E', 'SEA': '#7AC142', 'SF': '#C9243F', 'TB': '#D40909',
          'TEN': '#4095D1', 'WAS': '#FFC20F'}


def adjust_seconds_remaining(row):
    """
    This function is to help vectorize an operation later on the code to adjust the time remaining in each row.

    Parameters
    ----------
    row : pd.DataFrame row
    """
    if row['game_half'] == 'Overtime':
        return row['game_seconds_remaining'] - (600 - extra_time)
    return row['game_seconds_remaining'] + extra_time


# Specify the season you want to look at
year = '2022'

# Input your play-by-play data here
data = pd.read_csv(os.getcwd() + '/Data/nfl_' + year + '_pbp_reg.csv', low_memory=False)

# Disable annoying warnings
pd.options.mode.chained_assignment = None

# Input your desired game id here
game_id = '2022_15_IND_MIN'

# Filter the data to only include data from your game.
game_data = data.loc[data.game_id == game_id]

# Set some variables that will be useful
home_team = game_data.home_team.iloc[1]
away_team = game_data.away_team.iloc[1]
game_week = game_data.week.iloc[1]
game_year = game_id[:4]

# Grab the scores to be displayed in the final plot
home_score = game_data.home_score.iloc[1]
away_score = game_data.away_score.iloc[1]

# Slim down the data
home_team_wp_off = game_data.loc[game_data.posteam == home_team][['wp', 'game_seconds_remaining', 'game_half']]
home_team_wp_def = game_data.loc[game_data.defteam == home_team][['def_wp', 'game_seconds_remaining', 'game_half']]
home_team_wp_def.columns = ['wp', 'game_seconds_remaining', 'game_half']
home_team_wp = pd.concat([home_team_wp_off, home_team_wp_def])
home_team_wp = home_team_wp.sort_values('game_seconds_remaining', ascending=False)

away_team_wp_off = game_data.loc[game_data.posteam == away_team][['wp', 'game_seconds_remaining', 'game_half']]
away_team_wp_def = game_data.loc[game_data.defteam == away_team][['def_wp', 'game_seconds_remaining', 'game_half']]
away_team_wp_def.columns = ['wp', 'game_seconds_remaining', 'game_half']
away_team_wp = pd.concat([away_team_wp_off, away_team_wp_def])
away_team_wp = away_team_wp.sort_values('game_seconds_remaining', ascending=False)

# This helps unify the WP into one value
home_team_wp = home_team_wp.loc[home_team_wp['wp'] > 0.5]
away_team_wp = away_team_wp.loc[away_team_wp['wp'] > 0.5]
home_team_wp['wp'] = 1 - home_team_wp['wp']

# Deal with overtime games
max_game_seconds = 3600.0
len_var = len(game_data) - 1
extra_time = 0
if 'Overtime' in game_data['game_half'].values:
    extra_time = 600 - game_data['game_seconds_remaining'].iloc[len_var]
    max_game_seconds += extra_time

# Create a unified, smaller DF
home_df = home_team_wp[['wp', 'game_seconds_remaining', 'game_half']]
away_df = away_team_wp[['wp', 'game_seconds_remaining', 'game_half']]
wp_df = pd.concat([home_df, away_df])

# Deal with overtime in this unified DF
wp_df['game_seconds_remaining'] = wp_df.apply(adjust_seconds_remaining, axis=1)

# Sort the DF by time
wp_df = wp_df.sort_values('game_seconds_remaining')

# Initalize the figure and axis
fig, ax = plt.subplots(figsize=(15, 15))

# Set bounds for your axes
plt.xlim([0.0, max_game_seconds])
plt.ylim([0.0, 1.0])

# Initialize your extra time amount and the middle of each period
ot_split_extra = (max_game_seconds - 3600.0) / 2
x = np.array([3150, 2250, 1350, 450])

# Set the tick labels, depending on if the game went to OT
my_x = np.array(['Q1', 'Q2', 'Q3', 'Q4'])
if max_game_seconds > 3600.0:
    my_x = np.array(['Q1', 'Q2', 'Q3', 'Q4', 'OT'])
    x = np.array([max_game_seconds - 450, max_game_seconds - 1350, max_game_seconds - 2250, max_game_seconds - 3150,
                  ot_split_extra])
plt.xticks(x, my_x)

# Create vertical lines for the quarter breaks
plt.axvline(max_game_seconds - 900, 0, 1, color='black')
plt.axvline(max_game_seconds - 1800, 0, 1, color='black')
plt.axvline(max_game_seconds - 2700, 0, 1, color='black')
plt.axvline(max_game_seconds - 3600, 0, 1, color='black')
plt.axvline(0, 0, 1, color='black')

# Plot the win probability signs and invert the x-axis
plt.plot(wp_df['game_seconds_remaining'], wp_df['wp'], color=COLORS[home_team], linewidth=3.0)
plt.gca().invert_xaxis()

# Set the y-tick labels
y = np.array([0.0, 0.25, 0.50, 0.75, 1.00])
my_y = np.array(['100%', '75%', '50%', '75%', '100%'])
plt.yticks(y, my_y)
plt.axhline(0.5, 0, 3600, label='50%', color='black')

# Fill in the WP line to make things look nice
plt.fill_between(wp_df['game_seconds_remaining'], wp_df['wp'], 0.50, where=(wp_df['wp'] < 0.5), color=COLORS[home_team],
                 alpha=0.3, interpolate=True)
plt.fill_between(wp_df['game_seconds_remaining'], wp_df['wp'], 0.50, where=(wp_df['wp'] > 0.5), color=COLORS[away_team],
                 alpha=0.3, interpolate=True)

# Set the title of the plot and label the y-axis
ax.set_title(
    str(game_year) + ' Season, Week ' + str(game_week) + ' - ' + str(away_team) + '(' + str(away_score) + ') @ ' + str(
        home_team) + '(' + str(home_score) + ')', fontsize=20, pad=15)
ax.set_ylabel('Win Probability', fontsize=16, labelpad=15)

# Create variables for your logos
home_pic = (os.getcwd() + '/Logo_Pack/' + home_team + '.png')
away_pic = (os.getcwd() + '/Logo_Pack/' + away_team + '.png')
home_pic = plt.imread(home_pic)
away_pic = plt.imread(away_pic)

# Create OffSetImages for your logos
home_pic = OffsetImage(home_pic, zoom=1.30)
away_pic = OffsetImage(away_pic, zoom=1.30)

# Position the logos
home_pic.set_offset((850, 800))
away_pic.set_offset((850, 4500))

# Add the logos to the axis
ax.add_artist(home_pic)
ax.add_artist(away_pic)

# Save the image, properly formatted, to your desired path.
plt.savefig(game_id + '_wp.png', dpi=400)

# You can show the plot if you'd like, but it will not look correct.
# plt.show()
