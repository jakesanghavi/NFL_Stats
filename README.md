# NFL_Stats
Repository for Scraping and Analyzing NFL Data

**Steps to Download Data** \
If you would like, you can simply download all of the data files you need from this repository. Note that the data files are all zipped because they exceed GitHub's filesize limit. If you would like to know how to do it yourself if this repository ever goes down, I have left steps below for you to get it yourself.

1. Using get_nflfastR_pbp_data.R, download play by play data from as many seasons as you would like.
2. In order to get the SportRadar data: create a SportRadar account, download the .xml/.json file for the season schedule, convert that file into .csv format, and the feed that file into scrape_SportRadar_games.py.
3. To prepare your new files for merging, feed the nflfastR data into get_reg_season_only.py, and feed the SportRadar data into SportRadar_updater.py.
4. In order to merge the nflfastR and SportRadar data together, use nflfastR_SportRadar_concatenator.py.

**Acknowledgements** \
Thank you to the entire nflfastR team for the code to grab play-by-play data, check out their GitHub at https://github.com/nflverse/nflfastR. \
Thank you to Anthony Reinhardt for his code to merge nflfastR and SportRadar data together, check out his NFL GitHub repository at https://github.com/ajreinhard/NFL-public. \
And, thank you to Pavel Vab for his NFL Field Plot. His NFL GitHub repository can be found here: https://github.com/pavelvab/Football-Analytics.
