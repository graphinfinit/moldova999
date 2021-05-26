"""
settings
"""

from modules.sql_connector import *
sqly = SqliteDb()
sqly.create_settings_table()
settings = sqly.select_settings()

TOKEN = settings[0]['token']
IMAGE_LIMIT = settings[0]['count_foto']

#TOKEN = "OuDNh4liWBnpWRogRUWX4OfkSLCI"

# количество фото прикрепляемых к объявлению
#IMAGE_LIMIT = 5




"""
+++
"""

