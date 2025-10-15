import pandas as pd
from matplotlib import pyplot as plt
import os
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
from pathlib import Path
from datetime import date

common_width = 25
alpha = 0.1
r_epas = []
p_epas = []
plt.rcParams["font.family"] = "serif"
base = Path.cwd() / "DataPack" / "nflFastR"
year_dirs = [int(p.name) for p in base.iterdir() if p.is_dir() and p.name.isdigit()]

min_year = min(year_dirs)
max_year = max(year_dirs)
years = [y for y in range(1999, max_year+1)]

filename = Path.cwd() / "DataPack" / "nflFastR" / str(max_year) / f"reg_season_play_by_play_{max_year}.csv"
df = pd.read_csv(filename, low_memory=False)
max_week = np.max(df['week'])

del df


def getImage(path, gray):
    img = plt.imread(path)
    if gray:
        gray_background = np.full_like(img[:, :, :3], 0.5)

        # Create a composite image by blending the image and gray background while preserving alpha
        composite_image = (1 - alpha) * gray_background + alpha * img[:, :, :3]

        # Copy the alpha channel from the original image to the composite image
        img = np.dstack((composite_image, img[:, :, 3]))
    return OffsetImage(img, zoom=common_width / img.shape[1])


fig, ax = plt.subplots(figsize=(15, 15))
min_rush = 100
min_pass = 100
max_rush = -100
max_pass = -100
plot_type = input("Choose Historical Plot Type:\n1 for Offensive History\n2 for Defensive History\n3 for Net Off/Def History\n")

if plot_type not in ['1', '2', '3']:
    raise ValueError("Invalid plot type specified!")

team_var_map = {"1": "posteam", "2": "defteam", "3": "posteam"}
plot_title_map = {"1": "Offensive", "2": "Defensive", "3": "Net Off/Def"}
spacer_map = {
    "left_spacer": {
        "1": 0.036,
        "2": 0.01,
        "3": 0.045
    },
    "down_spacer": {
        "1": 0.015,
        "2": 0.03,
        "3": 0.018
    },
    "right_spacer": {
        "1": 0.013,
        "2": 0.03,
        "3": 0.013
    },
    "up_spacer": {
        "1": 0.03,
        "2": 0.015,
        "3": 0.03
    }
}

left_spacer = spacer_map['left_spacer'][plot_type]
down_spacer = spacer_map['down_spacer'][plot_type]
right_spacer = spacer_map['right_spacer'][plot_type]
up_spacer = spacer_map['up_spacer'][plot_type]

team_var = team_var_map[plot_type]
plot_title = plot_title_map[plot_type]

axis_append = "Net " if plot_type == "3" else ""

for year in years:
    filename = Path.cwd() / "DataPack" / "nflFastR" / str(year) / f"reg_season_play_by_play_{year}.csv"
    df = pd.read_csv(filename, low_memory=False)
    df = df.loc[df['week'] <= max_week]
    df = df[~df['desc'].str.upper().str.contains('TWO-POINT CONVERSION ATTEMPT')]
    df = df.loc[(df.qb_kneel == 0) & (df.qb_spike == 0)]

    total_off = df.loc[df['pass'] == 1].groupby(team_var, as_index=False)[['epa']].mean()

    # Do the same but for rushing plays
    total_off['rush_epa'] = df.loc[df.rush == 1].groupby(team_var, as_index=False)[['epa']].mean()['epa']
    total_off.columns = [team_var, 'pass_epa', 'rush_epa']

    if plot_type == "3":
        anti_df = df.loc[df['pass'] == 1].groupby('defteam', as_index=False)[['epa']].mean()
        anti_df['rush_epa'] = df.loc[df.rush == 1].groupby('defteam', as_index=False)[['epa']].mean()['epa']
        anti_df.columns = [team_var, 'pass_epa_def', 'rush_epa_def']
        total_off.columns = [team_var, 'pass_epa_off', 'rush_epa_off']

        total_off = total_off.merge(anti_df, on=team_var)
        total_off['pass_epa'] = total_off['pass_epa_off'] - total_off['pass_epa_def']
        total_off['rush_epa'] = total_off['rush_epa_off'] - total_off['rush_epa_def']
        total_off = total_off[[team_var, 'pass_epa', 'rush_epa']]

    del df

    x = total_off.rush_epa
    y = total_off.pass_epa

    r_epas += list(x)
    p_epas += list(y)

    if total_off['rush_epa'].min() < min_rush:
        min_rush = total_off['rush_epa'].min()
    if total_off['pass_epa'].min() < min_pass:
        min_pass = total_off['pass_epa'].min()
    if total_off['rush_epa'].max() > max_rush:
        max_rush = total_off['rush_epa'].max()
    if total_off['pass_epa'].max() > max_pass:
        max_pass = total_off['pass_epa'].max()

    logo_paths = [os.getcwd() + f'/Logo_Pack/{p}.png' for p in total_off[team_var]]

    mean_x, mean_y = np.mean(r_epas), np.mean(p_epas)
    std_x, std_y = np.std(r_epas), np.std(p_epas)

    distances = np.sqrt((x - mean_x) ** 2 + (y - mean_y) ** 2)
    std_dist = np.std(distances)
    mean_dist = np.mean(distances)
    threshold1 = mean_dist + 2 * std_dist
    threshold2 = mean_dist + 2.75 * std_dist
    x_thresh = [mean_x - 2.25 * std_x, mean_x + 2.25 * std_x]
    y_thresh = [mean_y - 2.25 * std_y, mean_y + 2.25 * std_y]

    for x0, y0, d, path in zip(x, y, distances, logo_paths):
        is_outlier_curr = (
                d > threshold1 or
                x0 < x_thresh[0] or x0 > x_thresh[1] or
                y0 < y_thresh[0] or y0 > y_thresh[1]
        )
        is_outlier_pre = (
                d > threshold2 or
                x0 < x_thresh[0] or x0 > x_thresh[1] or
                y0 < y_thresh[0] or y0 > y_thresh[1]
        )
        if year == max_year and is_outlier_curr:
            ab = AnnotationBbox(getImage(path, gray=False), (x0, y0), frameon=False, fontsize=4)
        else:
            ab = AnnotationBbox(getImage(path, gray=True), (x0, y0), frameon=False, fontsize=4)
            font_pt = 8
            if is_outlier_pre:
                if x0 > mean_x and y0 > mean_y:
                    ax.text(x0+right_spacer, y0 + down_spacer, str(year), fontsize=font_pt)
                elif x0 > mean_x and y0 < mean_y:
                    ax.text(x0+right_spacer, y0 - up_spacer, str(year), fontsize=font_pt)
                elif x0 < mean_x and y0 > mean_y:
                    ax.text(x0-left_spacer, y0 + down_spacer, str(year), fontsize=font_pt)
                elif x0 < mean_x and y0 < mean_y:
                    ax.text(x0-left_spacer, y0 - up_spacer, str(year), fontsize=font_pt)
        ax.add_artist(ab)

if plot_type in ["1", "3"]:
    ax.set_xlim([min_rush - 0.05, max_rush + 0.05])
    ax.set_ylim([min_pass - 0.05, max_pass + 0.05])
else:
    ax.set_xlim([max_rush+0.05, min_rush-0.05])
    ax.set_ylim([max_pass+0.05, min_pass-0.05])
ax.set_xlabel(f'{axis_append}Rush EPA/Play')
ax.set_ylabel(f'{axis_append}Pass EPA/Play')

fig.suptitle(f'Historical Team {plot_title} Performance Through Week {max_week}',
             y=0.95,
             weight='bold',
             fontsize=16)

fig.text(0.5, 0.905, f"{min_year}-{max_year} (Standout {max_year} Teams Highlighted)", ha='center', va='center', c='gray', fontsize=13,
         style='italic')

ax.axvline(np.mean(r_epas), linestyle='dashed', c='black', alpha=0.75)
ax.axhline(np.mean(p_epas), linestyle='dashed', c='black', alpha=0.75)
ax.set_facecolor('#faeed9')

fig.patch.set_facecolor('#F5DEB3')
plt.figtext(.8, 0.06, 'Credit: Jake Sanghavi', fontsize=10, ha='center', va='center')
plt.show()
