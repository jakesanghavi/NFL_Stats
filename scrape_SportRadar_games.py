import urllib.request, json
import pandas as pd
import sys
from urllib.request import Request, urlopen
import requests
import time


def extract_data(url):
    print(url)
    r = requests.get(url, headers=header_data)
    resp = r.json()
    return(resp)


header_data  = {
   'Connection': 'keep-alive',
   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
}

# Put your API key here
key = ""

ids = pd.read_csv('GAME_API_IDS')
ids = pd.DataFrame(ids.index.values)
for x in range(0,len(ids)):
    game_id = str(ids.iloc[x][0])
    game_url = "http://api.sportradar.us/nfl/official/trial/v5/en/games/" + game_id + "/pbp.json?api_key=" + key
    # with urllib.request.urlopen("http://api.sportradar.us/nfl/official/trial/v5/en/games/" + game_id + "/pbp.json?api_key=" + key) as url:
    # data = json.loads(game_url.read().decode())
    data = extract_data(game_url)
    with open("C:\\Users\\jakes\\OneDrive\\Desktop\\NFL_API_Data\\SportRadar\\game_number_" + str(x+1) + '.txt', 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print(data)
    # file2write=open("C:\\Users\\jakes\\OneDrive\\Desktop\\NFL_API_Data\\SportRadar\\game_number_" + str(x+1) + '.txt','w')
    # file2write.write(data)
    # file2write.close()
    time.sleep(1)
