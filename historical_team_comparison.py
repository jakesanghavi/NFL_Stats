import pandas as pd
from matplotlib import pyplot as plt
import os
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
from pathlib import Path
from datetime import date

curr_year = date.today().year
years = [y for y in range(1999, curr_year+1)]
common_width = 25
alpha = 0.1
r_epas = []
p_epas = []
plt.rcParams["font.family"] = "serif"
filename = Path.cwd() / "DataPack" / "nflFastR" / str(curr_year) / f"reg_season_play_by_play_{curr_year}.csv"
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

for year in years:
    filename = Path.cwd() / "DataPack" / "nflFastR" / str(year) / f"reg_season_play_by_play_{year}.csv"
    df = pd.read_csv(filename, low_memory=False)
    df = df.loc[df['week'] <= max_week]
    df = df[~df['desc'].str.upper().str.contains('TWO-POINT CONVERSION ATTEMPT')]
    df = df.loc[(df.qb_kneel == 0) & (df.qb_spike == 0)]

    total_off = df.loc[df['pass'] == 1].groupby('defteam', as_index=False)[['epa']].mean()

    # Do the same but for rushing plays
    total_off['rush_epa'] = df.loc[df.rush == 1].groupby('defteam', as_index=False)[['epa']].mean()['epa']
    del df

    total_off.columns = ['posteam', 'pass_epa', 'rush_epa']

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

    logo_paths = [os.getcwd() + f'/Logo_Pack/{p}.png' for p in total_off.posteam]

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
        is_outlier_2025 = (
                d > threshold1 or
                x0 < x_thresh[0] or x0 > x_thresh[1] or
                y0 < y_thresh[0] or y0 > y_thresh[1]
        )
        is_outlier_pre = (
                d > threshold2 or
                x0 < x_thresh[0] or x0 > x_thresh[1] or
                y0 < y_thresh[0] or y0 > y_thresh[1]
        )
        if year == curr_year and is_outlier_2025:
            ab = AnnotationBbox(getImage(path, gray=False), (x0, y0), frameon=False, fontsize=4)
        else:
            ab = AnnotationBbox(getImage(path, gray=True), (x0, y0), frameon=False, fontsize=4)
            left_spacer = 0.01
            down_spacer = 0.03
            right_spacer = 0.03
            up_spacer = 0.015
            if is_outlier_pre:
                if x0 > mean_x and y0 > mean_y:
                    ax.text(x0+right_spacer, y0 + down_spacer, str(year), fontsize=10)
                elif x0 > mean_x and y0 < mean_y:
                    ax.text(x0+right_spacer, y0 - up_spacer, str(year), fontsize=10)
                elif x0 < mean_x and y0 > mean_y:
                    ax.text(x0-left_spacer, y0 + down_spacer, str(year), fontsize=10)
                elif x0 < mean_x and y0 < mean_y:
                    ax.text(x0-left_spacer, y0 - up_spacer, str(year), fontsize=10)
        ax.add_artist(ab)

ax.set_xlim([max_rush+0.05, min_rush-0.05])
ax.set_ylim([max_pass+0.05, min_pass-0.05])
ax.set_xlabel('Rush EPA/Play')
ax.set_ylabel('Pass EPA/Play')

fig.suptitle(f'Historical Team Defensive Performance Through Week {max_week}',
             y=0.95,
             weight='bold',
             fontsize=16)

fig.text(0.5, 0.905, f"{years[0]}-{curr_year} (Standout {curr_year} Teams Highlighted)", ha='center', va='center', c='gray', fontsize=13,
         style='italic')

ax.axvline(np.mean(r_epas), linestyle='dashed', c='black', alpha=0.75)
ax.axhline(np.mean(p_epas), linestyle='dashed', c='black', alpha=0.75)
plt.figtext(.8, 0.06, 'Author: Jake Sanghavi\nData: nflfastR', fontsize=10, ha='center', va='center')
plt.show()
