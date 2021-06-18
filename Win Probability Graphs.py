import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from adjustText import adjust_text
import seaborn as sns
import os
from matplotlib.offsetbox import OffsetImage

COLORS = {'ARI':'#97233F','ATL':'#A71930','BAL':'#241773','BUF':'#00338D','CAR':'#0085CA','CHI':'#00143F',
          'CIN':'#FB4F14','CLE':'#FB4F14','DAL':'#B0B7BC','DEN':'#002244','DET':'#046EB4','GB':'#24423C',
          'HOU':'#C9243F','IND':'#003D79','JAX':'#136677','KC':'#CA2430','LA':'#002147','LAC':'#2072BA',
          'LV':'#C4C9CC','MIA':'#0091A0','MIN':'#4F2E84','NE':'#0A2342','NO':'#A08A58','NYG':'#192E6C',
          'NYJ':'#203731','PHI':'#014A53','PIT':'#FFC20E','SEA':'#7AC142','SF':'#C9243F','TB':'#D40909',
          'TEN':'#4095D1','WAS':'#FFC20F'}

data = pd.read_csv('reg_season_play_by_play_2020.csv', low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

game_id = '2020_04_BAL_WAS'

game_data = data.loc[data.game_id==game_id]

home_team = game_data.home_team.iloc[1]
away_team = game_data.away_team.iloc[1]
game_week = game_data.week.iloc[1]
game_year = game_id[:4]

home_score = game_data.home_score.iloc[1]
away_score = game_data.away_score.iloc[1]

home_team_wp_off = game_data.loc[game_data.posteam==home_team][['wp', 'game_seconds_remaining', 'game_half']]
home_team_wp_def = game_data.loc[game_data.defteam==home_team][['def_wp', 'game_seconds_remaining', 'game_half']]
home_team_wp_def.columns = ['wp', 'game_seconds_remaining', 'game_half']
home_team_wp = pd.concat([home_team_wp_off, home_team_wp_def])
home_team_wp = home_team_wp.sort_values('game_seconds_remaining',ascending=False)

away_team_wp_off = game_data.loc[game_data.posteam==away_team][['wp', 'game_seconds_remaining', 'game_half']]
away_team_wp_def = game_data.loc[game_data.defteam==away_team][['def_wp', 'game_seconds_remaining', 'game_half']]
away_team_wp_def.columns = ['wp', 'game_seconds_remaining', 'game_half']
away_team_wp = pd.concat([away_team_wp_off, away_team_wp_def])
away_team_wp = away_team_wp.sort_values('game_seconds_remaining',ascending=False)

home_team_wp = home_team_wp.loc[home_team_wp['wp'] > 0.5]
away_team_wp = away_team_wp.loc[away_team_wp['wp'] > 0.5]
home_team_wp['wp'] = 1 - home_team_wp['wp']

max_game_seconds = 3600.0
len_var = len(game_data) - 1
extra_time = 0
# if game_data['game_half'].iloc[len_var] == 'overtime':
if 'Overtime' in game_data['game_half'].values:
    extra_time = 600 - game_data['game_seconds_remaining'].iloc[len_var]
    max_game_seconds += extra_time

htwp = home_team_wp['wp']
htgsr = home_team_wp['game_seconds_remaining']
htgh = home_team_wp['game_half']
home_df = pd.DataFrame(columns = ['wp', 'game_seconds_remaining', 'game_half'])
home_df['wp'] = htwp
home_df['game_seconds_remaining'] = htgsr
home_df['game_half'] = htgh
atwp = away_team_wp['wp']
atgsr = away_team_wp['game_seconds_remaining']
atgh = away_team_wp['game_half']
away_df = pd.DataFrame(columns = ['wp', 'game_seconds_remaining', 'game_half'])
away_df['wp'] = atwp
away_df['game_seconds_remaining'] = atgsr
away_df['game_half'] = atgh
wp_df = pd.concat([home_df, away_df])
for x in range(0, len(wp_df)):
    if(wp_df['game_half'].iloc[x] == 'Overtime'):
        wp_df['game_seconds_remaining'].iloc[x] -= (600 - extra_time)
        continue
    wp_df['game_seconds_remaining'].iloc[x] += extra_time
# wp_df.loc[wp_df.game_half != 'Overtime', 'game_seconds_remaining'] = "Matt"
wp_df = wp_df.sort_values('game_seconds_remaining')
# print(max_game_seconds)

fig, ax = plt.subplots(figsize=(15,15))

wtwp = wp_df['wp']
wtgsr = wp_df['game_seconds_remaining']
plt.xlim([0.0,max_game_seconds])
plt.ylim([0.0,1.0])
# plt.plot(htgsr, htwp, color=COLORS[home_team])
# plt.plot(atgsr, atwp, color=COLORS[away_team])
# plt.plot(wtgsr, wtwp, color=COLORS[away_team])
# plt.gca().invert_xaxis()

x_axis_labels = [item.get_text() for item in ax.get_xticklabels()]
y_axis_labels = [item.get_text() for item in ax.get_yticklabels()]

if max_game_seconds == 3600.0:
    x = np.array([3150, 2250, 1350, 450])
    my_x = np.array(['Q1', 'Q2', 'Q3', 'Q4'])
    plt.xticks(x, my_x)
    plt.axvline(2700, 0, 1, label='end Q1', color='black')
    plt.axvline(1800, 0, 1, label='end Q2', color='black')
    plt.axvline(900, 0, 1, label='end Q3', color='black')
    plt.axvline(0, 0, 1, label='end Q4', color='black')
    plt.plot(wtgsr, wtwp, color=COLORS[home_team], linewidth=3.0)
    plt.gca().invert_xaxis()
else:
    ot_split_extra = (max_game_seconds - 3600.0)/2
    ot_split = ot_split_extra + 3600.0
    x = np.array([max_game_seconds - 450, max_game_seconds - 1350, max_game_seconds - 2250, max_game_seconds - 3150, ot_split_extra])
    my_x = np.array(['Q1', 'Q2', 'Q3', 'Q4', 'OT'])
    plt.xticks(x, my_x)
    plt.axvline(max_game_seconds - 900, 0, 1, label='end Q1', color='black')
    plt.axvline(max_game_seconds - 1800, 0, 1, label='end Q2', color='black')
    plt.axvline(max_game_seconds - 2700, 0, 1, label='end Q3', color='black')
    plt.axvline(max_game_seconds - 3600, 0, 1, label='end Q4', color='black')
    plt.axvline(0, 0, 1, label='end OT', color='black')
    plt.plot(wtgsr, wtwp, color=COLORS[home_team], linewidth=3.0)
    plt.gca().invert_xaxis()
y = np.array([0.0, 0.25, 0.50, 0.75, 1.00])
my_y = np.array(['100%', '75%', '50%', '75%', '100%'])
plt.yticks(y, my_y)
plt.axhline(0.5, 0, 3600, label='50%', color='black')
plt.fill_between(wp_df['game_seconds_remaining'], wp_df['wp'], 0.50,where=(wp_df['wp']<0.5), color=COLORS[home_team], alpha=0.3, interpolate=True)
plt.fill_between(wp_df['game_seconds_remaining'], wp_df['wp'], 0.50,where=(wp_df['wp']>0.5), color=COLORS[away_team], alpha=0.3, interpolate=True)
ax.set_title(str(game_year) + ' Season, Week ' + str(game_week) + ' - ' + str(away_team) + '(' + str(away_score) + ') @ ' + str(home_team) + '(' + str(home_score) + ')',fontsize=20,pad=15)
ax.set_ylabel('Win Probability', fontsize=16,labelpad=15)

home_pic = (os.getcwd() + "\Team_Logos"'\\' + home_team + '.png')
away_pic = (os.getcwd() + "\Team_Logos"'\\' + away_team + '.png')
home_pic = plt.imread(home_pic)
away_pic = plt.imread(away_pic)

home_pic = OffsetImage(home_pic, zoom=1.30)
away_pic = OffsetImage(away_pic, zoom=1.30)
# home_pic.set_offset((5500, 600))
# away_pic.set_offset((5500, 5000))
home_pic.set_offset((850, 800))
away_pic.set_offset((850, 4500))

ax.add_artist(home_pic)
ax.add_artist(away_pic)

# plt.savefig(game_id + '.png',dpi=400)
plt.savefig(game_id + '_with_line.png',dpi=400)
plt.show()
