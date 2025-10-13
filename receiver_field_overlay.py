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
import plotting_utils
from difflib import SequenceMatcher


COLORS = plotting_utils.get_team_colors()
COLORS2 = plotting_utils.get_team_alt_colors()
TEAMS = plotting_utils.get_team_names()
TAGS = plotting_utils.get_team_tags()

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

pfr_filename = Path.cwd() / "DataPack" / f"pfr_receiving_totals_{year}.csv"
pfr_data = pd.read_csv(pfr_filename)

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

player_name_input = input("Receiver name: ")

best_match = max(
    pfr_data.Player.dropna().unique(),
    key=lambda x: SequenceMatcher(None, player_name_input, x).ratio()
)

title_name = best_match
first_name_char = best_match[0] + '.'
last_name = best_match.split(' ', 1)[-1]
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

for x in range(0, len(pfr_data)):
    pfr_data['Player'].iloc[x] = pfr_data['Player'].iloc[x].rsplit('\\', 1)[0]

pfr_data = pfr_data.loc[pfr_data.Player == title_name]

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

ax.scatter(data['air_yards_to'], data['catch_number'], color='y', zorder=3)
ax.scatter(data['yardline_1'], data['catch_number'], color='b', zorder=3)
ax.scatter(data['yardline_2'], data['catch_number'], color='r', zorder=3)

for x in range(0, len(data)):
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['yardline_1'].iloc[x], xmax=data['air_yards_to'].iloc[x],
              color='b', zorder=2)
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['air_yards_to'].iloc[x], xmax=data['yardline_2'].iloc[x],
              color='y', zorder=2)
    if data.pass_touchdown.iloc[x] == 1:
        ax.scatter(data['yardline_2'].iloc[x], data['catch_number'].iloc[x], color='g', zorder=5)

plt.xticks([])
plt.yticks([])

ax.set_title(
    f"{title_name} {year} Receptions Chart\n",
    fontsize=20, pad=15, **hfont
)

# Reduce size of second line by 2 points
ax.title.set_fontsize(20)
ax.title.set_linespacing(1.2)
ax.text(0.5, 1.02,
        f"Stats - Receptions: {pfr_data['Rec'].iloc[0]}, Yards: {pfr_data['Yds'].iloc[0]}, TD: {pfr_data['TD'].iloc[0]}",
        transform=ax.transAxes, ha='center', va='bottom', fontsize=14, **hfont,
        style='italic')

# plt.savefig('receiver_graph_test.png', dpi=400)

plt.text(2.5, -1.8, TAGS[data['posteam'].iloc[0]], fontsize=12, **hfont)
plt.text(100, -1.8, "Credit: Jake Sanghavi", fontsize=10, **hfont)

c = [mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='b', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='y', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='r', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='g', edgecolor="none")]
labels = ['Line of Scrimmage', 'Point of Catch', 'Tackled', 'Touchdown']
leg = ax.legend(c, labels, title="Key:", loc='upper left', handler_map={mpatches.Circle: HandlerEllipse()},
                fancybox=True)
leg.get_title().set_position((-62, 0))

plt.show()
