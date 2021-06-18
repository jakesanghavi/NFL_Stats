import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import sys

year = '2020'

data = pd.read_csv('reg_season_play_by_play_' + year + '.csv', low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

data = data[['week', 'home_team', 'away_team', 'game_id']]

data = data.drop_duplicates()

data.to_csv('nflfastr_' + year + '_game_ids.csv', index=False)