import data_utils

API_KEY = "[INSERT_SPORTRADAR_API_KEY]"

data_utils.get_all_data(2025, API_KEY, max_week=5)