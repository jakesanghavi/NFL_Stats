import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import sys
import urllib.request

year = '2020'

data = pd.read_csv('play_by_play_' + year + '.csv', low_memory=False, encoding='mac_roman')
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

data.drop(['passer_player_name', 'passer_player_id',
           'rusher_player_name', 'rusher_player_id',
           'receiver_player_name', 'receiver_player_id'],
          axis=1, inplace=True)

data = data.loc[data.season_type=='REG']

data = data.loc[(data.play_type.isin(['no_play','pass','run'])) & (data.epa.isna()==False)]

data = data.loc[data.timeout == 0]

# Calls runs on no plays runs
data.loc[data.desc.str.contains('left end|left tackle|left guard|up the middle|right guard|right tackle|right end|rushes'),
'play_type'] = 'run'
# Calls passes on no plays runs
data.loc[data.desc.str.contains('scrambles|sacked|pass'), 'play_type'] = 'pass'

data.play_type.loc[data['pass']==1] = 'pass'
data.play_type.loc[data.rush==1] = 'run'
data.reset_index(drop=True, inplace=True)

data.to_csv('reg_season_play_by_play_' + year + '.csv')

# HELPFUL COLUMNS
# posteam - the offensive team (possesion team)
# defteam - the defensive team
# game_id - a unique id given to each NFL game
# epa - expected points added
# wp - current win probability of the posteam
# def_wp - current win probability of the defteam
# yardline_100 - number of yards from the opponent's endzone
# passer - the player that passed the ball (on QB scramble plays, the QB is marked as a passer, not rusher)
# rusher - the player that ran the ball
# receiver - the player that was targeted on a pass
# passer_id, rusher_id, receiver_id - the player ID for the passer, rusher, or receiver on a play (useful for joining roster data)
# cpoe - completion percentage over expected on a given pass
# down - down of the play
# play_type - either run, pass, or no_play
# series_success - marked as a 1 if the series becomes successful (first down or a touchdown)
