import pandas as pd
import os

# Choose the year your want
year = '2022'

# This is the relative path for a Mac
data = pd.read_csv(os.getcwd() + '/Data/nfl_' + year + '_pbp.csv', low_memory=False, encoding='mac_roman')

# Below is the relative path for a PC
# data = pd.read_csv(os.getcwd() + "\Data"'\\nfl_' + year + '+pbp.csv', low_memory=False, encoding='mac_roman')

# These lines removes annoying/irrelevant warning messages
pd.options.mode.chained_assignment = None

# Get just regular season. This can be changed to 'POST' for postseason.
data = data.loc[data.season_type == 'REG']

# Remove plays where the play time is weird or the epa does not exist
data = data.loc[(data.play_type.isin(['no_play', 'pass', 'run'])) & (data.epa.notna())]

# Remove "plays" that are just timeouts
data = data.loc[data.timeout == 0]

# Calls runs on no-plays runs
data.loc[
    data.desc.str.contains('left end|left tackle|left guard|up the middle|right guard|right tackle|right end|rushes'),
    'play_type'] = 'run'

# Calls passes on no-plays passes
data.loc[data.desc.str.contains('scrambles|sacked|pass'), 'play_type'] = 'pass'

# Update the play types and reset the index
data.play_type.loc[data['pass'] == 1] = 'pass'
data.play_type.loc[data.rush == 1] = 'run'
data.reset_index(drop=True, inplace=True)

# Write your output to CSV to your desired path. Again, this is the Mac relative path. Update to PC if needed.
data.to_csv(os.getcwd() + '/Data/nfl_' + year + '_pbp_reg.csv')


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
