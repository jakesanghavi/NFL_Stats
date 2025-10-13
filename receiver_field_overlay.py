import pandas as pd
from matplotlib import pyplot as plt
from adjustText import adjust_text
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from svgpath2mpl import parse_path
from termcolor import colored
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
from pathlib import Path
import matplotlib.image as mpimg

COLORS = {'ARI': '#97233F', 'ATL': '#A71930', 'BAL': '#241773', 'BUF': '#00338D', 'CAR': '#0085CA', 'CHI': '#00143F',
          'CIN': '#FB4F14', 'CLE': '#FB4F14', 'DAL': '#B0B7BC', 'DEN': '#002244', 'DET': '#046EB4', 'GB': '#24423C',
          'HOU': '#C9243F', 'IND': '#003D79', 'JAX': '#136677', 'KC': '#CA2430', 'LA': '#002147', 'LAC': '#2072BA',
          'LV': '#C4C9CC', 'MIA': '#0091A0', 'MIN': '#4F2E84', 'NE': '#0A2342', 'NO': '#A08A58', 'NYG': '#192E6C',
          'NYJ': '#203731', 'PHI': '#014A53', 'PIT': '#FFC20E', 'SEA': '#7AC142', 'SF': '#C9243F', 'TB': '#D40909',
          'TEN': '#4095D1', 'WAS': '#FFC20F'}
COLORS2 = {'ARI': '#000000', 'ATL': '#000000', 'BAL': '#000000', 'BUF': '#c60c30', 'CAR': '#000000', 'CHI': '#c83803',
           'CIN': '#fb4f14', 'CLE': '#22150c', 'DAL': '#b0b7bc', 'DEN': '#fb4f14', 'DET': '#b0b7bc', 'GB': '#ffb612',
           'HOU': '#a71930', 'IND': '#a5acaf', 'JAX': '#006778', 'KC': '#ffb612', 'LA': '#b3995d', 'LAC': '#0073cf',
           'LV': '#000000', 'MIA': '#f58220', 'MIN': '#ffc62f', 'NE': '#c60c30', 'NO': '#000000', 'NYG': '#a71930',
           'NYJ': '#1c2d25', 'PHI': '#a5acaf', 'PIT': '#ffb612', 'SEA': '#69be28', 'SF': '#b3995d', 'TB': '#34302b',
           'TEN': '#4b92db', 'WAS': '#ffb612'}

TEAMS = {'ARI': 'CARDINALS', 'ATL': 'FALCONS', 'BAL': 'RAVENS', 'BUF': 'BILLS', 'CAR': 'PANTHERS', 'CHI': 'BEARS',
         'CIN': 'BENGALS', 'CLE': 'BROWNS', 'DAL': 'COWBOYS', 'DEN': 'BRONCOS', 'DET': 'LIONS', 'GB': 'PACKERS',
         'HOU': 'TEXANS', 'IND': 'COLTS', 'JAX': 'JAGUARS', 'KC': 'CHIEFS', 'LA': 'RAMS', 'LAC': 'CHARGERS',
         'LV': 'RAIDERS', 'MIA': 'DOLPHINS', 'MIN': 'VIKINGS', 'NE': 'PATRIOTS', 'NO': 'SAINTS', 'NYG': 'GIANTS',
         'NYJ': 'JETS', 'PHI': 'EAGLES', 'PIT': 'STEELERS', 'SEA': 'SEAHAWKS', 'SF': '49ERS', 'TB': 'BUCCANEERS',
         'TEN': 'TITANS', 'WAS': 'WASHINGTON'}

TAGS = {'ARI': '#RedSea', 'ATL': '#RiseUpATL', 'BAL': '#RavensFlock', 'BUF': '#BillsMafia', 'CAR': '#KeepPounding',
        'CHI': '#DaBears',
        'CIN': '#SEIZETHEDEY', 'CLE': '#Browns', 'DAL': '#DallasCowboys', 'DEN': '#BroncosCountry', 'DET': '#OnePride',
        'GB': '#GoPackGo',
        'HOU': '#WeAreTexans', 'IND': '#ForTheShoe', 'JAX': '#DUUUVAL', 'KC': '#ChiefsKingdom', 'LA': '#RamsHouse',
        'LAC': '#BoltUp',
        'LV': '#RaiderNation', 'MIA': '#FinsUp', 'MIN': '#Skol', 'NE': '#GoPats', 'NO': '#Saints',
        'NYG': '#TogetherBlue',
        'NYJ': '#JetsNation', 'PHI': '#FlyEaglesFly', 'PIT': '#HereWeGo', 'SEA': '#Seahawks', 'SF': '#FTTB',
        'TB': '#GoBucs',
        'TEN': '#Titans', 'WAS': '#WashingtonFootball'}

hfont = {'family': 'monospace'}


class HandlerEllipse(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        center = 0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent
        p = mpatches.Ellipse(xy=center, width=height + xdescent,
                             height=height + ydescent)
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]


year = 2025
season_type = "reg"

filename = Path.cwd() / "DataPack" / f"complete_{season_type}_pbp_{year}.csv"

data = pd.read_csv(filename, low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

player_name = input("Receiver name: ")
title_name = player_name
first_name_char = player_name[0] + '.'
last_name = player_name.split(' ', 1)[-1]
player_name = first_name_char + last_name

if title_name == "DJ Moore":
    data = data.loc[data.posteam == "CAR"]

data = data.loc[data.receiver == player_name]
data = data.loc[data.play_type == 'pass']
data = data.loc[data.incomplete_pass == 0]
data = data.loc[~data.desc.str.contains('incomplete')]
data = data.loc[~data.desc.str.contains('No Play')]
data = data.loc[data.play_type != 'no_play']
data.reset_index(inplace=True)
data = data[data['yards_after_catch'].notnull()]
data['yardline_1'] = 100 - data['yardline_100'] + 10
data['air_yards_to'] = data['yardline_1'] + data['air_yards']
data['yardline_2'] = data['yardline_1'] + data['air_yards'] + data['yards_after_catch']
data['sortable'] = data['yardline_2'] - data['yardline_1']
data = data.sort_values(['yardline_1', 'yardline_2'], ascending=[True, True])
data.reset_index(inplace=True)
data['catch_number'] = data.index.values + 1
data['catch_number'] = data['catch_number'] * (50 / len(data))
data['catch_number'] = data['catch_number'] + 1.65

fig, ax = plt.subplots(figsize=(15, 15))

# Set field dimensions
plt.xlim(0, 120)  # Field length including endzones
plt.ylim(0, 53.3)  # field width

# Set field color green
ax.set_facecolor('#79af75')
ax.set_alpha(0.5)

# Print lines
for i in range(0, 120, 5):
    if i != 5 and i != 115:
        plt.axvline(i, color='white', linewidth=3, alpha=0.4, zorder=0)
    if i == 10 or i == 110:  # Make endzone lines
        plt.axvline(i, color='white', linewidth=5, alpha=0.4, zorder=1)

# Paint numbers
yds_from_sideline = 12
for i in range(10, 50, 10):
    plt.text(i + 9.5, 53.3 - yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom',
             horizontalalignment='center', rotation=180)
    plt.text(109.5 - i, 53.3 - yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom',
             horizontalalignment='center', rotation=180)

    plt.text(i + 10, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom',
             horizontalalignment='center')
    plt.text(110 - i, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom',
             horizontalalignment='center')

for i in range(0, 50, 1):
    if i % 5 == 0:
        continue
    plt.text(109.6 - i, 53.3 - 1, "l", color='white', fontsize=15, verticalalignment='bottom',
             horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)
    plt.text(109.5 - i, 0, "l", color='white', fontsize=15, verticalalignment='bottom', horizontalalignment='center',
             rotation=180, alpha=0.4, zorder=1)
    plt.text(i + 9.7, 0, "l", color='white', fontsize=15, verticalalignment='bottom',
             horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)
    plt.text(i + 9.7, 53.3 - 1, "l", color='white', fontsize=15, verticalalignment='bottom',
             horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)

# Paint 50 yard line numbers
plt.text(60, 53.3 - yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom',
         horizontalalignment='center', rotation=180)
plt.text(60, yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom',
         horizontalalignment='center')

LeftColor = COLORS[data['posteam'].iloc[0]]
RightColor = COLORS[data['posteam'].iloc[0]]
plt.text(5, 26.5, TEAMS[data['posteam'].iloc[0]], color=LeftColor, fontsize=30, verticalalignment='center',
         horizontalalignment='center', rotation=90)
plt.text(115, 26.5, TEAMS[data['posteam'].iloc[0]], color=RightColor, fontsize=30, verticalalignment='center',
         horizontalalignment='center', rotation=270)

logo_dir = Path.cwd() / "Logo_Pack"
team_logo = logo_dir / f"{data['posteam'].iloc[0]}.png"
team_logo = mpimg.imread(team_logo)

desired_width = 50
zoom = desired_width / team_logo.shape[1]
logo_image = OffsetImage(team_logo, zoom=zoom)

x_rel, y_rel = 0.5, 0.5
ab = AnnotationBbox(logo_image, (x_rel, y_rel),
                    xycoords='axes fraction',
                    frameon=False,
                    zorder=1.5)

team_logo = OffsetImage(team_logo, zoom=zoom)
ax.add_artist(ab)

ax.scatter(data['air_yards_to'], data['catch_number'], color='y', zorder=2)
ax.scatter(data['yardline_1'], data['catch_number'], color='b', zorder=2)
ax.scatter(data['yardline_2'], data['catch_number'], color='r', zorder=2)

for x in range(0, len(data)):
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['yardline_1'].iloc[x], xmax=data['air_yards_to'].iloc[x],
              color='b')
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['air_yards_to'].iloc[x], xmax=data['yardline_2'].iloc[x],
              color='y')
    if data.pass_touchdown.iloc[x] == 1:
        ax.scatter(data['yardline_2'].iloc[x], data['catch_number'].iloc[x], color='g')

plt.xticks([])
plt.yticks([])

ax.set_title(f"{title_name} {year} Receptions Chart" + "\n" + "by Jake Sanghavi", fontsize=20, pad=15, **hfont)

# plt.savefig('receiver_graph_test.png', dpi=400)

plt.text(2.5, -1.8, TAGS[data['posteam'].iloc[0]], fontsize=12, **hfont)

c = [mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='b', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='y', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='r', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='g', edgecolor="none")]
labels = ['Line of Scrimmage', 'Point of Catch', 'Tackled', 'Touchdown']
leg = ax.legend(c, labels, title="Key:", loc='upper left', handler_map={mpatches.Circle: HandlerEllipse()},
                fancybox=True)
leg.get_title().set_position((-62, 0))

plt.show()
