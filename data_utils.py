import pandas as pd
import requests
import json
import time
import os
from pathlib import Path
from datetime import date
import glob
import re
import urllib3
import bs4
import datetime


def safe_get(d, *keys):
    cur = d
    for k in keys:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(k)
        else:
            return None
    return cur


def key_exists(d, key):
    if isinstance(d, dict):
        if key in d:
            return True
        return any(key_exists(v, key) for v in d.values())
    elif isinstance(d, list):
        return any(key_exists(i, key) for i in d)
    return False


def save_file(data, directory, filename):
    cwd = Path.cwd()
    data_pack_dir = cwd / directory

    data_pack_dir.mkdir(parents=True, exist_ok=True)
    full_path = data_pack_dir / filename

    if isinstance(data, pd.DataFrame):
        if not str(full_path).lower().endswith('.csv'):
            full_path = Path(full_path).stem + '.csv'
        data.to_csv(full_path, index=False)
    elif isinstance(data, (dict, list)):
        if not str(full_path).lower().endswith('.json'):
            full_path = Path(full_path).stem + '.json'
        with open(full_path, 'w') as f:
            json.dump(data, f, indent=4)
    else:
        raise TypeError("Unsupported data type. Must be .json or .csv (Pandas DataFrame).")


def get_regular_season_fastr_only(year, filepath=None):
    if filepath is None:
        filepath = Path.cwd() / "DataPack" / "nflFastR" / str(year) / f"nflfastr_pbp_{year}.csv"
    data = pd.read_csv(filepath, low_memory=False, encoding='mac_roman')

    # Removes annoying/irrelevant warning messages
    pd.options.mode.chained_assignment = None

    # Get just regular season. This can be changed to 'POST' for postseason.
    data = data.loc[data.season_type == 'REG']

    # Remove plays where the play time is weird or the epa does not exist
    data = data.loc[(data.play_type.isin(['no_play', 'pass', 'run'])) & (data.epa.notna())]

    # Calls runs on no-plays runs
    data.loc[
        data.desc.str.contains(
            'left end|left tackle|left guard|up the middle|right guard|right tackle|right end|rushes'),
        'play_type'] = 'run'

    # Calls passes on no-plays passes
    data.loc[data.desc.str.contains('scrambles|sacked|pass'), 'play_type'] = 'pass'

    data = data[~data['desc'].str.upper().str.contains('TWO-POINT CONVERSION ATTEMPT')]

    # Update the play types and reset the index
    data.play_type.loc[data['pass'] == 1] = 'pass'
    data.play_type.loc[data.rush == 1] = 'run'
    data.reset_index(drop=True, inplace=True)

    out_dir = Path.cwd() / "DataPack" / "nflFastR" / str(year)
    out_file = f"reg_season_play_by_play_{year}.csv"

    save_file(data, out_dir, out_file)


def get_postseason_fastr_only(year, filepath=None):
    if filepath is None:
        filepath = Path.cwd() / "DataPack" / "nflFastR" / str(year) / f"nflfastr_pbp_{year}.csv"
    data = pd.read_csv(filepath, low_memory=False, encoding='mac_roman')

    # Removes annoying/irrelevant warning messages
    pd.options.mode.chained_assignment = None

    # Get just regular season. This can be changed to 'POST' for postseason.
    data = data.loc[data.season_type == 'POST']

    if len(data) == 0:
        return

    # Remove plays where the play time is weird or the epa does not exist
    data = data.loc[(data.play_type.isin(['no_play', 'pass', 'run'])) & (data.epa.notna())]

    # Calls runs on no-plays runs
    data.loc[
        data.desc.str.contains(
            'left end|left tackle|left guard|up the middle|right guard|right tackle|right end|rushes'),
        'play_type'] = 'run'

    # Calls passes on no-plays passes
    data.loc[data.desc.str.contains('scrambles|sacked|pass'), 'play_type'] = 'pass'

    data = data[~data['desc'].str.upper().str.contains('TWO-POINT CONVERSION ATTEMPT')]

    # Update the play types and reset the index
    data.play_type.loc[data['pass'] == 1] = 'pass'
    data.play_type.loc[data.rush == 1] = 'run'
    data.reset_index(drop=True, inplace=True)

    out_dir = Path.cwd() / "DataPack" / "nflFastR" / str(year)
    out_file = f"postseason_play_by_play_{year}.csv"

    save_file(data, out_dir, out_file)


def get_single_season_data(year):
    data = pd.read_csv(f'https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.csv.gz',
                       compression='gzip', low_memory=False)
    filename = f"nflfastr_pbp_{year}.csv"

    dirname = Path("DataPack") / "nflFastR" / str(year)

    save_file(data, dirname, filename)
    get_regular_season_fastr_only(year)
    get_postseason_fastr_only(year)

    return data


def get_multi_season_data(start_year, end_year):
    data = pd.DataFrame()

    for i in range(start_year, end_year + 1):
        year_data = get_single_season_data(i)

        data = data.append(year_data, sort=True)
        data = data.reset_index(drop=True)

    return data


def get_sportradar_schedule(year, api_key, access_level="trial"):
    for season_type in ["REG", "PST"]:
        url = f"https://api.sportradar.com/nfl/official/{access_level}/v7/en/games/{year}/{season_type}/schedule.json?api_key={api_key}"
        # url = f"https://api.sportradar.com/nfl/official/{access_level}/v7/en/games/current_season/schedule.json?api_key={api_key}"
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
                filename = f"sportradar_json_{season_type.replace('PST', 'POST')}_schedule_{year}.json"
                dirname = Path("DataPack") / "SportRadar" / str(year) / "Games" / season_type.replace('PST', 'POST')
                save_file(data, dirname, filename)

                games = [[]]

                for week in data['weeks']:
                    for game in week['games']:
                        games.append([game['id'], week['sequence']])

                df = pd.DataFrame(games[1:], columns=["game_id", "week"])
                # df = df.loc[df['week'] < 100]

                filename_csv = f"sportradar_{season_type.replace('PST', 'POST')}_schedule_{year}.csv"

                save_file(df, dirname, filename_csv)

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
    today = date.today()
    for season_type in ["REG", "PST"]:
        if ids_file is None:
            year = today.year
            ids_path = Path.cwd() / "DataPack" / "SportRadar" / str(
                year) / "Games" / season_type.replace('PST', 'POST') / f"sportradar_{season_type.replace('PST', 'POST')}_schedule_{year}.csv"
            ids_file = pd.read_csv(ids_path)
            ids_file = ids_file.loc[(ids_file['week'] <= max_week) & (ids_file['week'] >= min_week)]

        dirname = Path.cwd() / "DataPack" / "SportRadar" / str(year) / "Games" / season_type.replace('PST', 'POST')
        for _, row in ids_file.iterrows():
            game_id = row['game_id']
            filename = dirname / f'_{game_id}.json'

            # Don't write a new file if the file already exists AND
            # the game was over 1 week ago
            # Sometimes the sportradar data doesn't upload properly
            if os.path.isfile(filename):
                continue
            game_url = f"http://api.sportradar.us/nfl/official/{access_level}/v7/en/games/{game_id}/pbp.json?api_key={api_key}"

            data = extract_data(game_url)

            to_append = ""
            if key_exists(data, "pass_route"):
                to_append = "_"

            save_file(data, dirname, f'{to_append}{game_id}.json')

            # Sleep to avoid blocking
            time.sleep(1)

        ids_file = None


def get_nflfastr_ids(year):
    for season_type in ["REG", "POST"]:
        dirname = Path.cwd() / "DataPack" / "nflFastR" / str(year)
        filename = dirname / f"{season_type.lower()}_season_play_by_play_{year}.csv"
        if not os.path.isfile(filename):
            return
        data = pd.read_csv(filename, low_memory=False)
        pd.options.mode.chained_assignment = None

        pd.set_option('display.max_rows', 100)
        pd.set_option('display.max_columns', 300)

        data = data[['week', 'home_team', 'away_team', 'game_id']]

        data = data.drop_duplicates()
        outfile = f"nflfastr_{season_type.lower().replace('pst', 'post')}_{year}_game_ids.csv"

        save_file(data, dirname, outfile)


def find_stat_index_by_type(stats, stat_type):
    if not isinstance(stats, list):
        return None
    for i, s in enumerate(stats):
        if s.get('stat_type') == stat_type:
            return i
    return None


def find_def_target_index(stats):
    if not isinstance(stats, list):
        return None
    for i, s in enumerate(stats):
        if s.get('stat_type') == 'defense' and s.get('def_target'):
            return i
    return None


def extract_play_flat(ply, qtr_number, drv_sequence):
    stats = ply.get('statistics', []) or []
    rush_idx = find_stat_index_by_type(stats, 'rush')
    pass_idx = find_stat_index_by_type(stats, 'pass')
    rec_idx = find_stat_index_by_type(stats, 'receive')
    kick_idx = find_stat_index_by_type(stats, 'kick')
    def_idx = find_def_target_index(stats)

    # helper to fetch from stats[i] safely
    def sget(idx, field):
        if idx is None:
            return None
        entry = stats[idx]
        if entry is None:
            return None
        return entry.get(field)

    # def target player reference - in R they accessed ply$statistics[[def_tar_ID]]$player['reference']
    def_tar_ref = None
    if def_idx is not None:
        player_field = safe_get(stats[def_idx], 'player')
        if isinstance(player_field, dict):
            def_tar_ref = player_field.get('reference')

    out = {
        'qtr': qtr_number,
        'drv': drv_sequence,
        'play_ref': ply.get('reference'),
        'play_id': ply.get('id'),
        'play_type': ply.get('play_type'),
        'play_direction': ply.get('play_direction'),
        'playtime': ply.get('wall_clock'),
        'playclock': ply.get('play_clock'),
        'men_in_box': ply.get('men_in_box'),
        'screen_pass': ply.get('screen_pass'),
        'blitz': ply.get('blitz'),
        'players_rushed': ply.get('players_rushed'),
        'hash_mark': ply.get('hash_mark'),
        'left_tightends': ply.get('left_tightends'),
        'right_tightends': ply.get('right_tightends'),
        'running_lane': ply.get('running_lane'),
        'qb_at_snap': ply.get('qb_at_snap'),
        'play_action': ply.get('play_action'),
        'run_pass_option': ply.get('run_pass_option'),
        'rush_yards_after_contact': sget(rush_idx, 'yards_after_contact'),
        'broken_tackles': sget(rush_idx, 'broken_tackles'),
        'pass_route': ply.get('pass_route'),
        'incompletion_type': sget(pass_idx, 'incompletion_type'),
        'qb_on_target': sget(pass_idx, 'on_target_throw'),
        'pass_batted': sget(pass_idx, 'batted_pass'),
        'qb_hurry': sget(pass_idx, 'hurry'),
        'qb_knockdown': sget(pass_idx, 'knockdown'),
        'pocket_time': sget(pass_idx, 'pocket_time'),
        'pocket_location': ply.get('pocket_location'),
        'rec_drop': sget(rec_idx, 'dropped'),
        'rec_catchable': sget(rec_idx, 'catchable'),
        'rec_yards_after_contact': sget(rec_idx, 'yards_after_contact'),
        'rec_broken_tackles': sget(rec_idx, 'broken_tackles'),
        # mimic R column name 'def_tar_ID.reference'
        'def_tar_ID.reference': def_tar_ref,
        'squib_kick': sget(kick_idx, 'squib_kick'),
        'onside_attempt': sget(kick_idx, 'onside_attempt'),
        'onside_success': sget(kick_idx, 'onside_success'),
        # game_file will be added by caller (from filename)
        'game_file': None
    }

    return out


def list_json_files(sr_dir, char=""):
    if not os.path.isdir(sr_dir):
        return []
    # match .json files only
    pattern = os.path.join(sr_dir, f"{char}*.json")
    files = glob.glob(pattern)
    files.sort()
    return files


def basename_without_ext(path, char=""):
    base = os.path.basename(path)

    if len(char) > 0 and base.startswith(char):
        base = base[1:]

    return re.sub(r'\.json$', '', base, flags=re.IGNORECASE)


def normalize_team_abbrs(df, cols) -> pd.DataFrame:
    mapping = {
        'JAC': 'JAX',
        'OAK': 'LV',
        'SDG': 'LAC',
        'SD': 'LAC',
        'STL': 'LA'
    }
    for c in cols:
        if c in df.columns:
            df[c] = df[c].replace(mapping)
    return df


def merge_nflfastr_and_sportradar(year, nflfastr_dirname=None, sportradar_dirname=None):
    for season_type in ["REG", "PST"]:
        ALL_COL_NAMES = [
            'qtr', 'drv', 'play_ref', 'play_id', 'play_type', 'playtime', 'playclock',
            'screen_pass', 'hash_mark', 'play_direction', 'men_in_box', 'blitz',
            'left_tightends', 'right_tightends', 'qb_at_snap', 'play_action',
            'run_pass_option', 'running_lane', 'rush_yards_after_contact',
            'broken_tackles', 'players_rushed', 'pass_route', 'qb_on_target',
            'qb_hurry', 'qb_knockdown', 'pocket_time', 'pocket_location', 'rec_drop',
            'rec_catchable', 'def_tar_ID.reference', 'incompletion_type', 'pass_batted',
            'rec_yards_after_contact', 'rec_broken_tackles', 'game_file', 'squib_kick',
            'onside_attempt', 'onside_success'
        ]

        if nflfastr_dirname is None:
            nflfastr_dirname = Path.cwd() / "DataPack" / "nflFastR" / str(year)
        if sportradar_dirname is None:
            sportradar_dirname = Path.cwd() / "DataPack" / "SportRadar" / str(year) / "Games" / season_type.replace(
                'PST', 'POST')

        all_sportradar_jsons = list_json_files(sportradar_dirname, char="_")

        all_game_rows = []
        for jfile in all_sportradar_jsons:
            try:
                with open(jfile, 'r', encoding='utf-8') as fh:
                    pbp_json = json.load(fh)
            except Exception as e:
                print(f"Error reading {jfile}: {e}")
                continue

            periods = pbp_json.get('periods', []) or []
            for period in periods:
                qtr_number = period.get('number')
                drives = period.get('pbp', []) or []
                for drv in drives:
                    drv_sequence = drv.get('sequence')
                    events = drv.get('events', []) or []
                    for ply in events:
                        flat = extract_play_flat(ply, qtr_number, drv_sequence)
                        flat['game_file'] = basename_without_ext(jfile, char="_")
                        all_game_rows.append(flat)

        if len(all_game_rows) == 0:
            print("No plays extracted. Exiting.")
            return

        # Make pandas df
        full_pbp_df = pd.DataFrame(all_game_rows)

        # Keep col order
        for col in ALL_COL_NAMES:
            if col not in full_pbp_df.columns:
                full_pbp_df[col] = None
        full_pbp_df = full_pbp_df[ALL_COL_NAMES]

        save_file(full_pbp_df, sportradar_dirname, f"SportRadar_full_{season_type.replace('PST', 'POST')}_{year}.csv")

        full_pbp_df = full_pbp_df.loc[(full_pbp_df.play_type.isin(['penalty', 'pass', 'rush', 'conversion']))]

        schedule_path = sportradar_dirname / f"sportradar_json_{season_type.replace('PST', 'POST')}_schedule_{year}.json"

        if not os.path.isfile(schedule_path):
            print(f"Schedule JSON not found at {schedule_path}. Exiting.")
            return

        with open(schedule_path, 'r', encoding='utf-8') as fh:
            sched_json = json.load(fh)

        weeks = sched_json.get('weeks', []) or []
        gms_rows = []
        for wk in weeks:
            week_title = wk.get('title')
            games = wk.get('games', []) or []
            for gm in games:
                home = gm.get('home') or {}
                away = gm.get('away') or {}
                gms_rows.append({
                    'week': week_title,
                    'home_tm': home.get('alias'),
                    'away_tm': away.get('alias'),
                    'game_id_sprt': gm.get('id')
                })

        sport_gm_df = pd.DataFrame(gms_rows, columns=['week', 'home_tm', 'away_tm', 'game_id_sprt'])
        nflfastr_csv = nflfastr_dirname / f"nflfastr_{season_type.replace('PST', 'POST').lower()}_{year}_game_ids.csv"

        if not os.path.isfile(nflfastr_csv):
            print(f"nflfastr game ids CSV not found at {nflfastr_csv}. Exiting.")
            return
        scrp_gm_df = pd.read_csv(nflfastr_csv, dtype=str)

        sport_gm_df = normalize_team_abbrs(sport_gm_df, ['home_tm', 'away_tm'])
        scrp_gm_df = normalize_team_abbrs(scrp_gm_df, ['home_team', 'away_team'])
        join_cols_left = ['week', 'home_tm', 'away_tm']
        join_cols_right = ['week', 'home_team', 'away_team']

        # col checks
        for c in join_cols_left:
            if c not in sport_gm_df.columns:
                sport_gm_df[c] = None
        for c in join_cols_right:
            if c not in scrp_gm_df.columns:
                scrp_gm_df[c] = None

        for c in join_cols_left:
            sport_gm_df[c] = sport_gm_df[c].astype(str)
        for c in join_cols_right:
            scrp_gm_df[c] = scrp_gm_df[c].astype(str)

        full_gm_df = pd.merge(
            sport_gm_df,
            scrp_gm_df,
            left_on=join_cols_left,
            right_on=join_cols_right,
            how='left',
            suffixes=('_sprt', '_scrp')
        )

        if 'game_id_sprt' not in full_gm_df.columns and 'game_id_sprt' in sport_gm_df.columns:
            full_gm_df['game_id_sprt'] = sport_gm_df['game_id_sprt']
        if 'game_id' in scrp_gm_df.columns and 'game_id_scrp' not in full_gm_df.columns:
            full_gm_df['game_id_scrp'] = full_gm_df.get('game_id')

        if 'game_id_sprt' not in full_gm_df.columns:
            # attempt to find a column that corresponds to sprt id
            if 'game_id' in full_gm_df.columns:
                full_gm_df = full_gm_df.rename(columns={'game_id': 'game_id_sprt'})
            else:
                full_gm_df['game_id_sprt'] = None

        if 'game_id_scrp' not in full_gm_df.columns and 'game_id' in scrp_gm_df.columns:
            full_gm_df['game_id_scrp'] = full_gm_df.get('game_id')

        map_df = full_gm_df[['game_id_sprt', 'game_id_scrp']].drop_duplicates()

        all_gm_df = full_pbp_df.copy()

        # merge with all_gm_df by game_file (which contains sport radar file name)
        merged_all_gm_df = pd.merge(
            all_gm_df,
            map_df,
            left_on='game_file',
            right_on='game_id_sprt',
            how='left'
        )

        missing_map = merged_all_gm_df[merged_all_gm_df['game_id_scrp'].isna()]['game_file'].unique()
        if len(missing_map) > 0:
            print("Unique game_file entries with missing game_id_scrp (these plays may be ignored as in the R script):")
            print(missing_map.tolist())
        else:
            print("All game_file entries have a mapped game_id_scrp.")

        same_yr_pbp_path = nflfastr_dirname / f"{season_type.replace('PST', 'POST').lower()}_season_play_by_play_{year}.csv"

        if not os.path.isfile(same_yr_pbp_path):
            print(f"Regular season pbp CSV not found at {same_yr_pbp_path}. Exiting.")
            return

        same_yr_pbp = pd.read_csv(same_yr_pbp_path, dtype=str)

        if 'game_id_scrp' not in merged_all_gm_df.columns:
            merged_all_gm_df['game_id_scrp'] = None
        if 'play_ref' not in merged_all_gm_df.columns:
            merged_all_gm_df['play_ref'] = None

        same_yr_pbp['game_id'] = same_yr_pbp['game_id'].astype(str)
        same_yr_pbp['play_id'] = same_yr_pbp['play_id'].astype(str)

        same_yr_pbp['row_index1'] = (
                same_yr_pbp.groupby('game_id').cumcount() + 1
        )

        merged_all_gm_df['game_id_scrp'] = merged_all_gm_df['game_id_scrp'].astype(str)
        merged_all_gm_df['play_ref'] = merged_all_gm_df['play_ref'].astype(str)

        merged_all_gm_df['row_index2'] = (
                merged_all_gm_df.groupby('game_id_scrp').cumcount() + 1
        )

        # Final joining
        all_in_pbp = pd.merge(
            same_yr_pbp,
            merged_all_gm_df,
            left_on=['game_id', 'row_index1'],
            right_on=['game_id_scrp', 'row_index2'],
            how='left',
            suffixes=('', '_sportradar')
        )

        out_dir = Path("DataPack")

        all_filename = f"complete_{season_type.lower().replace('pst', 'post')}_pbp_{year}.csv"
        save_file(all_in_pbp, out_dir, all_filename)
        sportradar_dirname = None


def parse_row(row):
    other_data = row.find_all("td")
    if len(other_data) == 0:
        return []
    try:
        tid = other_data[0].find_all("a")[0]["href"].replace("/players/", "").replace(".htm", "").split("/")[-1]
    except IndexError:
        return []
    row_data = [td.string for td in other_data]
    row_data.append(tid)
    return row_data


def extract_column_names(table, dtype):
    columns = []
    if dtype == "receiving":
        columns = [col["aria-label"] for col in table.find_all("thead")[0].find_all("tr")[1].find_all("th")][1:]
    elif dtype == "passing":
        columns = [col["aria-label"] for col in table.find_all("thead")[0].find_all("tr")[0].find_all("th")][1:]
    columns.append("id")
    return columns


def extract_rows(table):
    rows = table.find_all("tbody")[0].find_all("tr")
    parsed_rows = []
    for r in rows:
        parsed = parse_row(r)
        if len(parsed) > 0:
            parsed_rows.append(parsed)
    return parsed_rows


def get_pfr_receiving_data(year):
    http = urllib3.PoolManager()
    columns = []
    rows = []

    receiving_page = f"https://www.pro-football-reference.com/years/{year}/receiving.htm"

    r = http.request('GET', receiving_page)  # Request the page
    soup = bs4.BeautifulSoup(r.data, "html.parser")  # Parse page with BeuatifulSoup
    f = soup.find("table", id="receiving")  # Find the talbe
    if len(f) > 0:  # Check to ensure the table is there
        columns = extract_column_names(f, "receiving")  # Extract column names from the table header
        rows = rows + extract_rows(f)  # Extract data from table rows

    frame = pd.DataFrame(rows)  # Convert rows to Dataframe

    frame.columns = columns
    dirname = Path.cwd() / "DataPack"
    filename = f"pfr_receiving_totals_{year}.csv"
    save_file(frame, dirname, filename)


def get_pfr_passing_data(year):
    http = urllib3.PoolManager()
    columns = []
    rows = []

    qb_page = f"https://www.pro-football-reference.com/years/{year}/passing.htm"

    r = http.request('GET', qb_page)  # Request the page
    soup = bs4.BeautifulSoup(r.data, "html.parser")  # Parse page with BeuatifulSoup
    f = soup.find("table", id="passing")  # Find the talbe
    if len(f) > 0:  # Check to ensure the table is there
        columns = extract_column_names(f, "passing")  # Extract column names from the table header
        rows = rows + extract_rows(f)  # Extract data from table rows

    frame = pd.DataFrame(rows)  # Convert rows to Dataframe

    frame.columns = columns
    dirname = Path.cwd() / "DataPack"
    filename = f"pfr_passing_totals_{year}.csv"
    save_file(frame, dirname, filename)


def get_all_data(year, api_key, sportradar=True, min_week=1):
    today = date.today()

    if today.year > year:
        max_week = 100
    elif today.year == year:
        # First NFL game of {year} season
        sept_first = datetime.date(year, 9, 1)
        days_to_add = (3 - sept_first.weekday()) % 7
        first_thursday_in_september = sept_first + datetime.timedelta(days=days_to_add)

        # Most recent Sunday to current day
        thursday_based_weekday = (today.weekday() + 1) % 7
        days_to_subtract = thursday_based_weekday
        recent_thursday = today - datetime.timedelta(days=days_to_subtract)

        if recent_thursday < first_thursday_in_september:
            raise ValueError(f"No data available yet for {year}.")
        time_difference = recent_thursday - first_thursday_in_september
        max_week = time_difference.days // 7 + 1
    else:
        raise ValueError("Year cannot be greater than current year.")

    get_single_season_data(year)
    get_nflfastr_ids(year)
    if sportradar:
        get_sportradar_schedule(year, api_key)
        get_sportradar_data(year, api_key, min_week, max_week)
        merge_nflfastr_and_sportradar(year)
    get_pfr_receiving_data(year)
    get_pfr_passing_data(year)
