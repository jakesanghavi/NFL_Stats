import data_utils

API_KEY = "[INSERT_SPORTRADAR_API_KEY]"

# Choose sportradar = False if only interested in nflFastR
data_utils.get_all_data(2025, API_KEY, sportradar=True)
