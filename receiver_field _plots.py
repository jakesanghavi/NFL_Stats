import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from adjustText import adjust_text
import os
from matplotlib.offsetbox import OffsetImage
import sys

COLORS = {'ARI':'#97233F','ATL':'#A71930','BAL':'#241773','BUF':'#00338D','CAR':'#0085CA','CHI':'#00143F',
          'CIN':'#FB4F14','CLE':'#FB4F14','DAL':'#B0B7BC','DEN':'#002244','DET':'#046EB4','GB':'#24423C',
          'HOU':'#C9243F','IND':'#003D79','JAX':'#136677','KC':'#CA2430','LA':'#002147','LAC':'#2072BA',
          'LV':'#C4C9CC','MIA':'#0091A0','MIN':'#4F2E84','NE':'#0A2342','NO':'#A08A58','NYG':'#192E6C',
          'NYJ':'#203731','PHI':'#014A53','PIT':'#FFC20E','SEA':'#7AC142','SF':'#C9243F','TB':'#D40909',
          'TEN':'#4095D1','WAS':'#FFC20F'}

TEAMS = {'ARI':'CARDINALS','ATL':'FALCONS','BAL':'RAVENS','BUF':'BILLS','CAR':'PANTHERS','CHI':'BEARS',
          'CIN':'BENGALS','CLE':'BROWNS','DAL':'COWBOYS','DEN':'BRONCOS','DET':'LIONS','GB':'PACKERS',
          'HOU':'TEXANS','IND':'COLTS','JAX':'JAGUARS','KC':'CHIEFS','LA':'RAMS','LAC':'CHARGERS',
          'LV':'RAIDERS','MIA':'DOLPHINS','MIN':'VIKINGS','NE':'PATRIOTS','NO':'SAINTS','NYG':'GIANTS',
          'NYJ':'JETS','PHI':'EAGLES','PIT':'STEELERS','SEA':'SEAHAWKS','SF':'49ERS','TB':'BUCCANEERS',
          'TEN':'TITANS','WAS':'WASHINGTON'}

# Choose your desired season
year = str(2020)

data = pd.read_csv('reg_season_play_by_play_' + year + '.csv', low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

player_name = input("Receiver name: ")
title_name = player_name
first_name_char = player_name[0] + '.'
last_name = player_name.split(' ', 1)[-1]
player_name = first_name_char + last_name

data = data.loc[data.receiver == player_name]
data = data.loc[data.play_type == 'pass']
data = data.loc[data.incomplete_pass == 0]
data = data.loc[~data.desc.str.contains('incomplete')]
data = data.loc[~data.desc.str.contains('No Play')]
data = data.loc[data.play_type != 'no_play']
data.reset_index(inplace=True)
data = data[data['yards_after_catch'].notnull()]
data['yardline_1'] = 100 - data['yardline_100'] + 10
# data = data.sort_values('yardline_1', ascending=False)
data['air_yards_to'] = data['yardline_1'] + data['air_yards']
data['yardline_2'] = data['yardline_1'] + data['air_yards'] + data['yards_after_catch']
# data['yardline_2'] = data['yardline_1'] + data['yards_gained']
data = data.sort_values(['yardline_1', 'yardline_2'], ascending=[True, True])
data.reset_index(inplace=True)
data['catch_number'] = data.index.values + 1
data['catch_number'] = data['catch_number'] * (50/len(data))
data['catch_number'] = data['catch_number'] + 1.65

fig, ax = plt.subplots(figsize=(15,15))

# Set field dimensions
plt.xlim(0, 120)  # Field length including endzones
plt.ylim(0, 53.3)  # field width

# Set field color green
ax.set_facecolor('#79af75')
ax.set_alpha(0.5)

# Print lines
for i in range(0, 120, 10):
    plt.axvline(i, color='white', linewidth=3, alpha=0.4, zorder=1)
    if i == 10 or i == 110:  # Make endzone lines
        plt.axvline(i, color='white', linewidth=5, alpha=0.4, zorder=1)

# Paint numbers
yds_from_sideline = 12
for i in range(10, 50, 10):
    plt.text(i+10, 53.3-yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)
    plt.text(110-i, 53.3-yds_from_sideline,  str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)

    plt.text(i+10, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')
    plt.text(110-i, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')

# Paint 50 yard line numbers
plt.text(60, 53.3-yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)
plt.text(60, yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')

LeftColor = COLORS[data['posteam'].iloc[0]]
RightColor = COLORS[data['posteam'].iloc[0]]
plt.text(5, 26.5, TEAMS[data['posteam'].iloc[0]], color=LeftColor, fontsize=30, verticalalignment='center', horizontalalignment='center', rotation=90)
plt.text(115, 26.5, TEAMS[data['posteam'].iloc[0]], color=RightColor, fontsize=30, verticalalignment='center', horizontalalignment='center', rotation=270)

team_logo = (os.getcwd() + "\Logo_Pack"'\\' + data['posteam'].iloc[0] + '.png')
team_logo = plt.imread(team_logo)
team_logo = OffsetImage(team_logo, zoom=0.50)
team_logo.set_offset((750, 375))
ax.add_artist(team_logo)

ax.scatter(data['air_yards_to'], data['catch_number'], color='b')
ax.scatter(data['yardline_1'], data['catch_number'], color='y')
ax.scatter(data['yardline_2'], data['catch_number'], color='r')


for x in range(0, len(data)):
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['yardline_1'].iloc[x], xmax=data['air_yards_to'].iloc[x], color='b')
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['air_yards_to'].iloc[x], xmax=data['yardline_2'].iloc[x], color='r')
    if data.pass_touchdown.iloc[x] == 1:
        ax.scatter(data['yardline_2'].iloc[x], data['catch_number'].iloc[x], color='g')

plt.xticks([])
plt.yticks([])

# plt.suptitle(title_name + ' 2019 Receptions Chart',fontsize=20)
ax.set_title(title_name + ' ' + year + ' Receptions Chart',fontsize=20,pad=25)
# ax.set_title('Stats: Receptions=' + str(int(len(data))) + ', Yards=' + str(int(data['air_yards'].sum()) + int(data['yards_after_catch'].sum())) + ', AY=' + str(int(data['air_yards'].sum())) + ', YAC=' + str(int(data['yards_after_catch'].sum())) + ', TD=' + str(int(data['pass_touchdown'].sum())), fontsize=10)
# ax.text(60,54,'Stats: Receptions=' + str(int(len(data))) + ', Yards=' + str(int(data['air_yards'].sum()) + int(data['yards_after_catch'].sum())) + ', AY=' + str(int(data['air_yards'].sum())) + ', YAC=' + str(int(data['yards_after_catch'].sum())) + ', TD=' + str(int(data['pass_touchdown'].sum())), fontsize=10, horizontalalignment='center')

# plt.savefig('receiver_graph_test.png',dpi=400)

plt.show()

