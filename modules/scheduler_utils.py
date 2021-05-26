
"""
$ ..  .   ..  .   .
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
#from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

import base64
import json
import logging
import datetime
import copy

from modules.util import post_advert
from modules.sql_connector import *
from modules.settings import *


"""
daemon=True
$____$
 _  _
 ____
  
"""
sched = BackgroundScheduler(daemon=False)
sched.start()


def send_advert(advert_row):
    logging.info(f"send_advert: {datetime.datetime.now()}")
    adv = copy.deepcopy(advert_row)
    sqly = SqliteDb()
    for featur in adv["features"]:
        if featur["id"] == "12":
            texts_pool = featur["value"]
            text = sqly.get_text_for_send(texts_pool)
            tex = text[0]["text_content"]
            # подставляем новый заголовок
            featur["value"] = tex
        if featur["id"] == "14":
            # сюда вставляем список id фото
            image_list_row = sqly.get_images_for_send(limit=IMAGE_LIMIT, image_pool=featur["value"])
            image_list = [i["image_id"] for i in image_list_row]
            featur["value"] = image_list
    # выкладываем объявление
    # ///
    answer = post_advert(json.dumps(adv))
    del adv


def subtask(advert_row, schedule):
    logging.info(f"init_subtask*: {datetime.datetime.now()}")
    weekday = datetime.datetime.today().weekday()
    for key in schedule:
        if key[:1] == str(weekday):
            start = datetime.datetime.strptime(schedule[f"{key[:1]}_from"], "%H:%M")
            end = datetime.datetime.strptime(schedule[f"{key[:1]}_to"], "%H:%M")
            interval = schedule[f"{key[:1]}_int"]
            delta = end - start
            end_date = datetime.datetime.now() + delta
            job = sched.add_job(send_advert, args=(advert_row,), trigger='interval', minutes=int(interval), end_date=end_date)
            break
    logging.info(f"start_subtask: {datetime.datetime.now()}")

def start_scheduler(pool):

    schedule_b64 = pool[0]["schedule"]
    schedule_full = json.loads(base64.urlsafe_b64decode(schedule_b64.encode()).decode())
    schedule = {k: v for k, v in schedule_full.items() if v}

    # переформатируем объявление и запустим задачу для заданных дней недели
    flag = pool[0]['flag']

    advert_row = {}
    advert_row["category_id"] = str(pool[0]['category'])
    advert_row["subcategory_id"] = str(pool[0]['subcategory'])
    advert_row["offer_type"] = str(pool[0]['offer_type'])
    advert_row["features"] = []

    features = pool[0]['features']
    features_row = json.loads(base64.urlsafe_b64decode(features.encode('cp1251')).decode('cp1251'))

    price = {"id": "2", "value": int(features_row["2"]), "unit": features_row["unit2"]}
    advert_row["features"].append(price)

    task_id = features_row["pool_name"]
    del features_row["2"]
    del features_row["unit2"]
    del features_row["pool_name"]

    copy_feature_row = features_row.copy()
    for fea in copy_feature_row:
        if fea.startswith("unit"):
            unit = features_row[fea]
            value = features_row[fea[4:]]
            advert_row["features"].append({"id": fea[4:], "value": value, "unit": unit})
            del features_row[fea[4:]]
            del features_row[fea]


    for key in features_row:
        if key.startswith("texts_pool"):
            fea = {"id": key[11:], "value": features_row[key]}
            advert_row["features"].append(fea)
        elif key.startswith("image_group"):
            fea = {"id": key[12:], "value": features_row[key]}
            advert_row["features"].append(fea)
        else:
            if features_row[key] == 'true':
                fea = {"id": key, "value": True}
            else:
                fea = {"id": key, "value": features_row[key]}
            advert_row["features"].append(fea)

    # days_of_week = "1,3,5" пример
    # получим список дней недели
    days_of_week = list(set([key[:1] for key in schedule]))

    cron_list = []
    for day in days_of_week:
        start = datetime.datetime.strptime(schedule[f"{day}_from"], "%H:%M")
        end = datetime.datetime.strptime(schedule[f"{day}_to"], "%H:%M")
        interval = schedule[f"{day}_int"]
        cron_list.append(CronTrigger(day_of_week=day, hour=start.hour, minute=start.minute))

    trigger = OrTrigger(cron_list)
    job = sched.add_job(subtask, args=(advert_row, schedule,), trigger=trigger, id=task_id)

    logging.info(f"start_scheduler* {job}: {datetime.datetime.today()}")
    return job.id



