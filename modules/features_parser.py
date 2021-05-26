"""
Здесь грусть.
Парсим параметры объявлений
Для заголовков и фотографий указываем возможные пулы из базы данных.
"""
from modules.util import get_user_phones
from modules.sql_connector import *


def features_parser(features_list, subcategory_id):
    sqly = SqliteDb()
    html_form = """
<h1>Создание пула</h1>
Выберите группы фотографий и заголовков и остальные параметры.
<hr>
<form action = ""  method = "post" >
Название пула.(eng)
<br><input type='text' id='q' name='pool_name'><br><br><hr>
"""

    for i in features_list:
        features = i["features"]

        for n in features:
            html_form += n["title"]
            if n["required"] == True:
                html_form += "(required)"
            if n["type"] == "check_box":
                if n["options"]:
                    for m in n["options"]:
                        html_form += f"<p><input type='checkbox' name='{n['id']}' checked>{n['title']}<Br>"
                else:
                    html_form += f"<p><input type='checkbox' name='{n['id']}' value='true' checked>{n['title']}<Br>"

            if n["type"] == "textarea_text":
                html_form += f"<br><input type='text' id='q' name='{n['id']}'><br>"
            if n["type"] == "textbox_text":

                # Заголовок объявления
                if n['id'] == "12":
                    try:
                        groupsql = sqly.get_texts_groups()
                        groups = []
                        for i in groupsql:
                            groups.append(i["texts_pool"])
                    except Exception as exc:
                        groups = ["None", "None"]
                        logging.error(f"features_parser: {exc.args}")
                    html_form += f"<select name='texts_pool_{n['id']}' id='q'>"
                    for group in groups:
                        html_form += f"<option value='{group}'>{group}</option>"
                    html_form += "</select>"
                else:
                    html_form += f"<br><input type='text' id='q' name='{n['id']}'><br>"
            if n["type"] == "textbox_numeric":
                html_form += f"<input type='number' id='q' name='{n['id']}'>"
            if n["type"] == "textbox_numeric_measurement":
                html_form += f"<input type='number' id='q' name='{n['id']}'>"
                html_form += f"<select name='unit{n['id']}' id='q'>"
                for m in n["units"]:
                    html_form += f"<option value='{m}'>{m}</option>"
                html_form += "</select>"
            if n["type"] == "drop_down_options":
                if n["depends_on"] is None or n['depends_on'] == '5':
                    if n["options"]:
                        html_form += f"<select name='{n['id']}' id='{n['id']}'>"
                        for m in n["options"]:
                            html_form += f"<option value='{m['id']}'>{m['title']}</option>"
                        html_form += "</select><hr>"
                else:
                    html_form += f"(depends_on)<select name='{n['id']}' class='depends_on' id='{n['depends_on']}'></select><hr>"

            if n["type"] == "upload_images":
                html_form += f"<br> id({n['id']})"
                html_form += "<br> Выбрать пул фотографий"
                try:
                    groupsql = sqly.get_images_group()
                    groups = []
                    for i in groupsql:
                        groups.append(i["image_pool"])
                except Exception as exc:
                    groups = ["None", "None"]
                    logging.error(f"features_parser: {exc.args}")
                html_form += f"<select name='image_group_{n['id']}' id='q'>"
                for group in groups:
                    html_form += f"<option value='{group}'>{group}</option>"
                html_form += "</select>"

            if n["type"] == "upload_videos":
                html_form += "<br>Добавление видео не доступно"
            if n["type"] == "contacts":
                # нужно добавить выбор
                user_phone = get_user_phones()
                html_form += f"<br>id({n['id']})"
                html_form += f"<br><input type='text' name='{n['id']}' value='{user_phone}'><br> user_phone:{user_phone}"

            html_form += "<hr>"
    html_form += "<p><input type='submit'></p></form>"
    return html_form
