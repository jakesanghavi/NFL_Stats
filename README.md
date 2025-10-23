# NFL_Stats
Repository for Scraping and Analyzing NFL Data

## Steps to Download Data (Takes Just 10 Minutes Total!)
1. Clone this GitHub repo: `git clone https://github.com/jakesanghavi/NFL_Stats [PROJECT_FOLDER_NAME]`
2. Sign up for a Sportradar account (free): [https://developer.sportradar.com/getting-started/docs/get-started](https://developer.sportradar.com/getting-started/docs/get-started) Choose the 30-day free trial plan for NFL data, which can be continually renewed for free. (Save your API Key somewhere you won't lose it!)
3. Set up your Python environment to include the below dependencies
4. Run `get_all_data.py` to get all relevant data for a given season, using your API key. This will save to various local files in `[PROJECT_FOLDER_NAME]/DataPack/...` (You should run this every Tuesday morning during the season to refresh your data)
5. Use any of the files in the repo to perform some analysis! They will all work straight out of the box.

**Wasn't that easy?**

### Plotting Files Guide

**QB Info**: Use `QB_dropback_analysis.py` for a classic EPA/CPOE plot, and `best_qb_by_route.py` to break things up by route.

**Receiver Info**: use `best_wr_by_route.py` to break things up by route, and `receiver_field_overlay.py` to plot things over a field background.

**Team Info**: use `historical_team_comparison.py` to show a current year's offense/defense/net performance by team as compared to historical squads.

**Game Info**: use `win_probability_graphs.py` to plot the win probability for a given game as a time series.

#### Python Dependencies

```
adjustText
bs4
matplotlib
numpy
pandas
PIL
requests
seaborn
svgpath2mpl
termcolor
urllib3
```

#### Example Outputs

<img alt="wr_plot" src="https://github.com/user-attachments/assets/33e0b8e0-cbb6-4a76-b99e-557ad9974900" />
<img alt="qb_plot" src="https://github.com/user-attachments/assets/e3296bdf-a260-4689-bd29-b196401282be" />
<img alt="hist" src="https://github.com/user-attachments/assets/ee230b7c-26e9-42c7-bac9-aa4d5a7de233" />
<img alt="wr_field_plot" src="https://user-images.githubusercontent.com/57878447/144541900-d92356ca-2603-449e-b8c2-b4aacc678c21.png" width=700/>
<img alt="wp_graph" src="https://user-images.githubusercontent.com/57878447/144541663-cd8c6139-0b30-4504-8697-868d6329301d.png" width=500/>

#### Acknowledgements. 
Thank you to the entire nflfastR team for the code to grab play-by-play data, check out their GitHub at https://github.com/nflverse/nflfastR.  
Thank you to Anthony Reinhardt for his code to merge nflfastR and SportRadar data together, check out his NFL GitHub repository at https://github.com/ajreinhard/NFL-public.  
And, thank you to Pavel Vab for the base code provided to make an NFL Field Plot. His NFL GitHub repository can be found here: https://github.com/pavelvab/Football-Analytics.
