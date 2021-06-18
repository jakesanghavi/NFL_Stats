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
