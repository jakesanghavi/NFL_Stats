import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import os
import urllib.request
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import seaborn as sns
import sys
import scipy.stats as st
import matplotlib.ticker as plticker


def change_width(ax, new_value) :
    for patch in ax.patches :
        current_width = patch.get_width()
        diff = current_width - new_value

        # we change the bar width
        patch.set_width(new_value)

        # we recenter the bar
        patch.set_x(patch.get_x() + diff * .5)


# Select your data file here
data = pd.read_csv('reg_pbp_and_sportradar_2020.csv', low_memory=False)
pfr_data = pd.read_csv('pfr_totals_2020.csv')
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

data = data[data['pass_route'].notnull()]

routes = data['pass_route']

data = data.loc[data.play_type_sportradar == 'pass']
data = data.loc[data.play_type == 'pass']

routes = routes.drop_duplicates()
routes_list=[]
for x in range(0,len(routes)):
    routes_list.append(routes.iloc[x])

# team_name = input("Choose a Team: ")
player_name = input("Choose a Receiver: ")
title_name = player_name
first_name_char = player_name[0] + '.'
last_name = player_name.split(' ', 1)[-1]
player_name = first_name_char + last_name
if title_name == 'D.K. Metcalf':
    player_name = 'DK.Metcalf'

# data=data.loc[data.posteam==team_name]
if title_name == 'Jarvis Landry':
    data = data.loc[data.pass_route != 'Underneath Screen']
data = data.loc[data.receiver==player_name]
data = data.loc[~data.desc.str.contains('No Play')]
data.reset_index(inplace=True)

for x in range(0, len(pfr_data)):
    pfr_data['Player'].iloc[x] = pfr_data['Player'].iloc[x].rsplit('\\', 1)[0]
# pfr_data['Player']= pfr_data['Player'].rsplit('\\', 1)[0]
pfr_data = pfr_data.loc[pfr_data.Player == title_name]
print(pfr_data)

# receiver_stats = data.loc[data['incomplete_pass'] == 0]
# receiver_stats = receiver_stats.loc[~data.desc.str.contains('incomplete')]
# receiver_stats = receiver_stats.loc[~data.desc.str.contains('No Play')]
# receiver_stats = receiver_stats[receiver_stats['yards_after_catch'].notnull()]
# receiver_stats.reset_index(inplace=True)

routes_data = pd.DataFrame(data, columns=['epa','pass_route', 'success'])
routes_data['count'] = 0
routes_data['total_epa'] = 1

# for x in range(0, len(routes_data))

for x in range(0,len(routes_data)):
    route_count = len(routes_data.loc[routes_data.pass_route == routes_data.pass_route.iloc[x]])
    routes_data['count'].iloc[x] = route_count
    routes_data['total_epa'].iloc[x] = route_count * routes_data['epa'].iloc[x]
    if(routes_data['pass_route'].iloc[x] == 'WR Screen'):
        routes_data['pass_route'].iloc[x] = 'WR Scrn'
    if(routes_data['pass_route'].iloc[x] == 'Underneath Screen'):
        routes_data['pass_route'].iloc[x] = 'Undr Scrn'

# for x in range(0,len(routes_data)):
#     route_count = len(routes_data.loc[routes_data.pass_route == routes_data.pass_route.iloc[x]])
#     routes_data['total_epa'].iloc[x] = route_count * routes_data['epa'].iloc[x]

routes_data = routes_data.sort_values('pass_route')

# fig,ax = plt.subplots(2,2, figsize=(15,8))
fig = plt.figure()

fig.suptitle('2020 Receiver Stats (When Targeted) by Route - ' + title_name
              + '\n'
             # 'Stats: Receptions=' + str(pfr_data['Rec'].iloc[0]) + ', Yards=' + str(pfr_data['Yds'].iloc[0]) + ', TD=' + str(pfr_data['TD'].iloc[0])
              + 'By Jake Sanghavi (data from nflfastR and SportRadar)'
            )

ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

sns.barplot(x='pass_route', y='count', data=routes_data, ax=ax1, ci=None)
sns.barplot(x='pass_route', y='epa', data=routes_data, ax=ax2, ci=None)
sns.barplot(x='pass_route', y='success', data=routes_data, ax=ax3, ci=None)
sns.barplot(x='pass_route', y='total_epa', data=routes_data, ax=ax4, ci=None)

ax1.title.set_text('Route Frequency')
ax1.set_xlabel('Route Type')
ax1.set_ylabel('# Plays')
ax1.tick_params(axis='x', which='major', labelsize=7)
# ax1.set_xticklabels([1, 'keypoint', 2], fontsize=3)
change_width(ax1, 1.)
ax2.title.set_text('EPA/play by Route Type')
ax2.set_xlabel('Route Type')
ax2.set_ylabel('EPA/play')
ax2.tick_params(axis='x', which='major', labelsize=7)
change_width(ax2, 1.)
ax3.title.set_text('Success Rate by Route Type')
ax3.set_xlabel('Route Type')
ax3.set_ylabel('Success Rate')
ax3.tick_params(axis='x', which='major', labelsize=7)
change_width(ax3, 1.)
ax4.title.set_text('Total EPA by Route Type')
ax4.set_xlabel('Route Type')
ax4.set_ylabel('Total EPA')
ax4.tick_params(axis='x', which='major', labelsize=7)
change_width(ax4, 1.)

plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.22)
# plt.savefig(title_name + '_2019_route_stats.png',dpi=800)

plt.show()


