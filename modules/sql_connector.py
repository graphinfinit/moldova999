import logging
import sqlite3


DATABASE_URL = "spamer.db"
IMAGES = "images"
TEXTS = "texts"
MAINPOOL = "mainpool"
SETTINGS = "settings"


class SqliteDb(object):
    def __init__(self, db_path=DATABASE_URL):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def create_image_table(self, table_name=IMAGES):
        with self.connection:
            try:
                self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, image_pool TEXT, image_id TEXT UNIQUE, file_name TEXT, add_datetime TEXT, flag TEXT)")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def insert_image_table(self, image_pool, image_id, file_name, add_datetime, flag='False', table_name=IMAGES):
        with self.connection:
            try:
                self.cursor.execute(f"INSERT INTO {table_name} (image_pool, image_id, file_name, add_datetime, flag) VALUES ('{image_pool}', '{image_id}', '{file_name}', '{add_datetime}', '{flag}')")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def get_images_id(self, image_pool, table_name=IMAGES):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE image_pool = '{image_pool}'")
                pool = self.cursor.fetchall()
                return pool
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def get_images_group(self, table_name=IMAGES):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT image_pool FROM {table_name} GROUP BY image_pool")
                groups = self.cursor.fetchall()
                return groups
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def get_images_for_send(self, image_pool, limit, table_name=IMAGES):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT id, image_id FROM {table_name} WHERE image_pool = '{image_pool}' AND flag='False' LIMIT {limit}")
                images = self.cursor.fetchall()
                if images:
                    for image in images:
                        self.cursor.execute(f"UPDATE {table_name} SET flag='True' WHERE id = {image['id']}")
                    return images
                else:
                    print("Новый фото круг")
                    # видимо начинаем новый круг если все заголовки кончились
                    self.cursor.execute(f"UPDATE {table_name} SET flag='False' WHERE image_pool = '{image_pool}'")
                    self.cursor.execute(
                        f"SELECT id, image_id FROM {table_name} WHERE image_pool = '{image_pool}' AND flag='False' LIMIT {limit}")
                    images = self.cursor.fetchall()
                    return images
            except Exception as exc:
                logging.error(f"db func:get_images_for_send: {exc.args}")

    # text

    def create_text_table(self, table_name=TEXTS):
        with self.connection:
            try:
                self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, texts_pool TEXT, text_content TEXT UNIQUE, add_datetime TEXT, flag TEXT)")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def insert_text(self,texts_pool, text_content, add_datetime, flag='False', table_name=TEXTS):
        with self.connection:
            try:
                self.cursor.execute(f"INSERT INTO {table_name} (texts_pool, text_content, add_datetime, flag) VALUES ('{texts_pool}', '{text_content}', '{add_datetime}', '{flag}')")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def get_texts(self, texts_pool, table_name=TEXTS):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE texts_pool = '{texts_pool}'")
                pool = self.cursor.fetchall()
                return pool
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def get_texts_groups(self, table_name=TEXTS):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT texts_pool FROM {table_name} GROUP BY texts_pool")
                groups = self.cursor.fetchall()
                return groups
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def get_text_for_send(self, texts_pool, table_name=TEXTS):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT id, text_content FROM {table_name} WHERE texts_pool='{texts_pool}' AND flag ='False' LIMIT 1")
                r = self.cursor.fetchall()
                if r:

                    id = r[0]["id"]
                    self.cursor.execute(f"UPDATE {table_name} SET flag='True' WHERE id = {id}")
                    return r
                else:
                    # видимо начинаем новый круг если все заголовки кончились
                    self.cursor.execute(f"UPDATE {table_name} SET flag='False' WHERE texts_pool = '{texts_pool}'")
                    self.cursor.execute(
                        f"SELECT id, text_content FROM {table_name} WHERE texts_pool='{texts_pool}' AND flag ='False' LIMIT 1")
                    r = self.cursor.fetchall()
                    return r

            except Exception as exc:
                logging.error(f"db func:get_text_for_send(): {exc.args}")

    # main pool

    def create_pool_table(self, table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, category INTEGER, subcategory INTEGER, offer_type INTEGER, features TEXT, pool_name TEXT, add_datetime TEXT, schedule TEXT, flag BOOLEAN)")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def insert_pool(self, category, subcategory, offer_type, pool_name, add_datetime, schedule='None', flag=False, features='None', table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"""INSERT INTO {table_name} (category, subcategory, offer_type, features, pool_name, add_datetime, schedule, flag) VALUES ("{category}", "{subcategory}", "{offer_type}", "{features}", "{pool_name}", "{add_datetime}", "{schedule}", {flag})""")
                return True
            except Exception as exc:
                logging.error(f"db_*: {exc.args}")

    def get_pools_names(self, table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT pool_name FROM {table_name}")
                pools = self.cursor.fetchall()
                return pools
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def get_fullpools_names(self, table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT pool_name FROM {table_name} WHERE schedule != 'None'")
                pools = self.cursor.fetchall()
                return pools
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def update_pool(self, schedule, pool_name, table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"""UPDATE {table_name} SET schedule = "{schedule}" WHERE pool_name = "{pool_name}" """)
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    def get_pool(self,pool_name ,table_name=MAINPOOL):
        with self.connection:
            try:
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE pool_name = '{pool_name}'")
                pool = self.cursor.fetchall()
                return pool
            except Exception as exc:
                logging.error(f"db: {exc.args}")


    #settings

    def create_settings_table(self, count_foto=3, token="OuDNh4liWBnpWRogRUWX4OfkSLCI", table_name=SETTINGS):
        with self.connection:
            try:
                self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, count_foto INTEGER, token TEXT)")
                self.cursor.execute(f"""INSERT INTO {table_name} (count_foto, token) VALUES ({count_foto}, '{token}')""")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")

    def insert_count(self, count_foto, table_name=SETTINGS):
        with self.connection:
            try:
                self.cursor.execute(f"""UPDATE {table_name} SET count_foto ={count_foto} WHERE id=1""")

                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")
    def insert_token(self, token, table_name=SETTINGS):
        with self.connection:
            try:
                self.cursor.execute(f"""UPDATE {table_name} SET token='{token}' WHERE id=1""")
                return True
            except Exception as exc:
                logging.error(f"db: {exc.args}")
    def select_settings(self, table_name=SETTINGS):
        with self.connection:
            try:
                self.cursor.execute(f"""SELECT token, count_foto FROM {table_name} WHERE id=1""")
                sett = self.cursor.fetchall()
                return sett
            except Exception as exc:
                logging.error(f"db: {exc.args}")
    def drop_settings(self, table_name=SETTINGS):
        with self.connection:
            try:
                self.cursor.execute(f"""DROP TABLE {table_name}""")
                sett = self.cursor.fetchall()
                return sett
            except Exception as exc:
                logging.error(f"db: {exc.args}")













