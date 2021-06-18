import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import sys

year = '2020'

data = pd.read_csv('SportRadar_full_' + year + '.csv', low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

# data = data.loc[(data.play_type.isin(['no_play','pass','run'])) & (data.epa.isna()==False)]
data = data.loc[(data.play_type.isin(['penalty','pass','rush', 'conversion']))]

data.to_csv('SportRadar_' + year + '.csv', index=False)

# data.drop(['play_id', 'play_type'],
#           axis=1, inplace=True)

# data.rename(columns={'play_ref':'play_id'}, inplace=True)

# r_data = pd.read_csv('reg_season_play_by_play_2019.csv', low_memory=False)
#
# r_data = r_data.loc[r_data.play_type_nfl != 'TIMEOUT']
#
# r_data.to_csv('regular_season_play_by_play_2019.csv')
#
# print(len(r_data))
# print(len(data))

# full_reg_pbp_2019 = pd.merge(data, r_data, on='play_id', how='left')
#
# print(full_reg_pbp_2019)
