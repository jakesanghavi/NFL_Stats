from matplotlib import pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from pathlib import Path
import pandas as pd
import requests
from io import BytesIO
import plotting_utils

COLORS = {'ARI': '#97233F', 'ATL': '#A71930', 'BAL': '#241773', 'BUF': '#00338D', 'CAR': '#0085CA', 'CHI': '#00143F',
          'CIN': '#FB4F14', 'CLE': '#FB4F14', 'DAL': '#B0B7BC', 'DEN': '#002244', 'DET': '#046EB4', 'GB': '#24423C',
          'HOU': '#C9243F', 'IND': '#003D79', 'JAX': '#136677', 'KC': '#CA2430', 'LA': '#002147', 'LAC': '#2072BA',
          'LV': '#C4C9CC', 'MIA': '#0091A0', 'MIN': '#4F2E84', 'NE': '#0A2342', 'NO': '#A08A58', 'NYG': '#192E6C',
          'NYJ': '#203731', 'PHI': '#014A53', 'PIT': '#FFC20E', 'SEA': '#7AC142', 'SF': '#C9243F', 'TB': '#D40909',
          'TEN': '#4095D1', 'WAS': '#FFC20F'}

year = 2025

plt.rcParams["font.family"] = "serif"

filename = Path.cwd() / "DataPack" / f"complete_pbp_{year}.csv"

data = pd.read_csv(filename)

data['filter'] = data[['pass_route', 'receiver']].isna().any(axis=1)
data = data.loc[data['filter'] == False].drop(columns=['filter'])
data['pass_route'] = np.where((data['pass_route'] == 'Underneath Screen') | (data['pass_route'] == 'WR Screen'),
                              'Screen', data['pass_route'])

grp = data.groupby(by=['posteam', 'receiver', 'pass_route', 'receiver_id'], as_index=False).agg(
    {'play_id': 'size', 'complete_pass': 'sum', 'cpoe': 'sum', 'epa': ['mean', 'sum']})

grp.columns = ['posteam', 'player', 'route', 'rec_id', 'targets', 'receptions', 'CPOE', 'EPA_avg', 'EPA_tot']
min_targets = 3

fig, axes = plt.subplots(2, 2)

max_rec_ixs = grp.groupby('route')['targets'].idxmax()
rec_leaders = grp.loc[max_rec_ixs, ['route', 'player', 'posteam', 'rec_id']]
rec_leaders['targets'] = grp.groupby('route')['targets'].max().values

max_tot_epa_ixs = grp.groupby('route')['EPA_tot'].idxmax()
tot_epa_leaders = grp.loc[max_tot_epa_ixs, ['route', 'player', 'posteam', 'rec_id']]
tot_epa_leaders['tot_epa'] = grp.groupby('route')['EPA_tot'].max().values

max_cpoe_ixs = grp.groupby('route')['CPOE'].idxmax()
cpoe_leaders = grp.loc[max_cpoe_ixs, ['route', 'player', 'posteam', 'rec_id']]
cpoe_leaders['CPOE'] = grp.groupby('route')['CPOE'].max().values

max_avg_epa_ixs = grp.loc[grp['targets'] >= min_targets].groupby('route')['EPA_avg'].idxmax()
avg_epa_leaders = grp.loc[grp['targets'] >= min_targets].loc[max_avg_epa_ixs, ['route', 'player', 'posteam', 'rec_id']]
avg_epa_leaders['avg_epa'] = grp.loc[grp['targets'] >= min_targets].groupby('route')['EPA_avg'].max().values

common_width = 40


def plot_bar(ax, df, stat, title, y_title):
    bars = ax.bar(df['route'], df[stat], width=1)

    for i, bar in enumerate(bars):
        bar.set_color(COLORS[df['posteam'].iloc[i]])
        bar.set_edgecolor('black')
        bar.set_linewidth(1.2)

        path = Path.cwd() / "Logo_Pack" / f"{df['posteam'].iloc[i]}.png"
        try:
            img = plotting_utils.get_player_headshot(df['rec_id'].iloc[i])
        except requests.exceptions.HTTPError:
            img = plt.imread(path)

        imagebox = OffsetImage(img, zoom=common_width / img.shape[1])
        ab = AnnotationBbox(imagebox, (bar.get_x() + bar.get_width() / 2, bar.get_height() / 2), frameon=False)
        ax.add_artist(ab)

    # Add text annotations from the other DataFrame
    for i, bar in enumerate(ax.patches):
        text_value = df['player'].iloc[i]
        sign = 1 if bar.get_height() > 0 else -50
        bar_x = bar.get_x() + bar.get_width() / 2
        bar_y = bar.get_height() + sign * 0.01

        target_width_px = 100
        fontsize = 6
        txt = ax.text(bar_x, bar_y, text_value,
                      ha='center', va='bottom', fontsize=fontsize, fontweight='bold')

        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()

        bbox = txt.get_window_extent(renderer=renderer)
        current_width = bbox.width

        fontsize_new = fontsize * (target_width_px / current_width)
        fontsize_new = max(4.5, min(8, fontsize_new))
        txt.set_fontsize(fontsize_new)

    ax.set_title(title, weight='bold')
    ax.tick_params(axis='x', labelsize=7)
    ax.set_xlim(left=-0.5, right=10.5)
    ax.set_ylabel(y_title)
    ax.set_facecolor('#faeed9')


plot_bar(axes[0][0], rec_leaders, 'targets', 'Target Leaders', 'Targets')
plot_bar(axes[0][1], tot_epa_leaders, 'tot_epa', 'Total EPA Leaders', 'Total EPA')
plot_bar(axes[1][0], cpoe_leaders, 'CPOE', f'Aggregate CPOE Leaders', 'Aggregate CPOE')
plot_bar(axes[1][1], avg_epa_leaders, 'avg_epa', f'EPA/Play Leaders - Min. {min_targets} Targets', 'EPA/Play')

fig.patch.set_facecolor('#F5DEB3')
fig.suptitle(f'Top Receivers by Route Type - {year}',
             y=0.95,
             weight='bold',
             fontsize=16)

fig.text(0.5, 0.91, 'by Jake Sanghavi', fontsize=12, ha='center')
plt.subplots_adjust(wspace=0.15, hspace=0.15, left=0.05, right=0.95)

plt.show()
