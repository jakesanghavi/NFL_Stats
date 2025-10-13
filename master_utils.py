import pandas as pd
import requests
import json
import time
import os
from pathlib import Path
from datetime import date


def save_file(data, directory, filename):
    cwd = Path.cwd()
    data_pack_dir = cwd / directory

    data_pack_dir.mkdir(parents=True, exist_ok=True)
    full_path = data_pack_dir / filename

    if isinstance(data, pd.DataFrame):
        if not full_path.lower().endswith('.csv'):
            full_path = Path(full_path).stem + '.csv'
        data.to_csv(full_path, index=False)
    elif isinstance(data, (dict, list)):
        if not full_path.lower().endswith('.json'):
            full_path = Path(full_path).stem + '.json'
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        raise TypeError("Unsupported data type. Must be .json or .csv (Pandas DataFrame).")


def get_single_season_data(year):
    data = pd.read_csv(f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.csv.gz',
                       compression='gzip', low_memory=False)
    filename = f"regular_season_pbp_{year}.csv"

    dirname = Path("DataPack") / "nflFastR"

    save_file(data, dirname, filename)
    return data


def get_multi_season_data(start_year, end_year):
    data = pd.DataFrame()

    for i in range(start_year, end_year+1):
        year_data = get_single_season_data(i)

        data = data.append(year_data, sort=True)
        data = data.reset_index(drop=True)

    return data


def get_current_sportradar_schedule(api_key, access_level="trial"):
    url = f"https://api.sportradar.com/nfl/official/{access_level}/v7/en/games/current_season/schedule.json?api_key={api_key}"
    headers = {
        'accept': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)

        # Raise an exception if needed
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            year = date.today().year
            filename = f"sportradar_json_schedule_{year}.csv"
            dirname = Path("DataPack") / "SportRadar"
            save_file(data, dirname, filename)

            games = [[]]

            for week in data['weeks']:
                for game in week['games']:
                    games.append([game['id'], week['sequence']])

            df = pd.DataFrame(games[1:], columns=["game_id", "week"])
            # Playoffs start after 100 I think
            df = df.loc[df['week'] < 100]

            filename_csv = f"sportradar_schedule_{year}.csv"

            save_file(df, dirname, filename_csv)

            return data

        else:
            print(f"Request failed with status code: {response.status_code}")

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")


def extract_data(url):
    header_data = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    }

    r = requests.get(url, headers=header_data)
    resp = r.json()
    return resp


def get_sportradar_data(year, api_key, min_week=1, max_week=17, access_level="trial", ids_file=None):
    if ids_file is None:
        year = date.today().year
        ids_path = Path.cwd() / "DataPack" / "SportRadar" / f"sportradar_schedule_{year}.csv"
        ids_file = pd.read_csv(ids_path)
        ids_file = ids_file.loc[(ids_file['week'] <= max_week) & (ids_file['week'] >= min_week)]
    for i, row in ids_file.iterrows():
        game_id = row['game_id']
        game_url = f"http://api.sportradar.us/nfl/official/{access_level}/v7/en/games/{game_id}/pbp.json?api_key={api_key}"

        data = extract_data(game_url)
        dirname = Path("DataPack") / "SportRadar" / str(year)

        save_file(data, dirname, f'{game_id}.json')

        # Sleep to avoid blocking
        time.sleep(1)
