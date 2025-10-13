import pandas as pd
from matplotlib import pyplot as plt
from adjustText import adjust_text
from pathlib import Path

COLORS = {'ARI': '#97233F', 'ATL': '#A71930', 'BAL': '#241773', 'BUF': '#00338D', 'CAR': '#0085CA', 'CHI': '#00143F',
          'CIN': '#FB4F14', 'CLE': '#FB4F14', 'DAL': '#B0B7BC', 'DEN': '#002244', 'DET': '#046EB4', 'GB': '#24423C',
          'HOU': '#C9243F', 'IND': '#003D79', 'JAX': '#136677', 'KC': '#CA2430', 'LA': '#002147', 'LAC': '#2072BA',
          'LV': '#C4C9CC', 'MIA': '#0091A0', 'MIN': '#4F2E84', 'NE': '#0A2342', 'NO': '#A08A58', 'NYG': '#192E6C',
          'NYJ': '#203731', 'PHI': '#014A53', 'PIT': '#FFC20E', 'SEA': '#7AC142', 'SF': '#C9243F', 'TB': '#D40909',
          'TEN': '#4095D1', 'WAS': '#FFC20F'}

plt.rcParams["font.family"] = "monospace"

year = 2025

filepath = Path.cwd() / "DataPack" / f"complete_pbp_{year}.csv"

data = pd.read_csv(filepath, low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

# Create QBs dataframe with avg epa, avg cpoe, and number of plays
qbs = data.groupby(['passer', 'posteam'], as_index=False).agg({'epa': 'mean',
                                                               'cpoe': 'mean',
                                                               'play_id': 'count'})

# Set minimum limit of 200 dropbacks
# qbs = qbs.loc[qbs.play_id>200]
qbs = qbs.loc[qbs.play_id >= int(data.week.iloc[-1] * 10)]

fig, ax = plt.subplots(figsize=(15, 15))

# Create vertical and horizontal lines for averages of each metric
ax.axvline(x=qbs.cpoe.mean(), linestyle='--', alpha=.5, color='black')
ax.axhline(y=qbs.epa.mean(), linestyle='--', alpha=.5, color='black')
# Create a dot for each player
# Find their team color in the COLORS dictionary
# s stands for size, the dot size is proportional to the QBs number of plays
for i in range(len(qbs)):
    ax.scatter(qbs.cpoe.iloc[i], qbs.epa.iloc[i],
               s=qbs.play_id.iloc[i], alpha=.7,
               color=COLORS[qbs.posteam.iloc[i]])

# Add text to each dot
texts = [plt.text(x0, y0, name, ha='right', va='bottom') for x0, y0, name in zip(
    qbs.cpoe, qbs.epa, qbs.passer)]

# Add grid
ax.grid(zorder=0, alpha=.4)
ax.set_axisbelow(True)

# Remove top and right boundary lines
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
adjust_text(texts)

# Add title, labels, and source
ax.set_title('QB Dropback Analysis - 2020' + '\n' + 'by Jake Sanghavi', fontsize=20, pad=15)
ax.set_xlabel('Completion % Over Expected (CPOE)', fontsize=16, labelpad=15)
ax.set_ylabel('EPA per Attempt', fontsize=16, labelpad=15)
plt.figtext(.8, .06, 'Data: nflfastR', fontsize=12)

ax.set_facecolor('peachpuff')
fig.patch.set_facecolor('wheat')

# Save figure
# plt.savefig('CPOEepa2.png',dpi=400)

plt.show()
