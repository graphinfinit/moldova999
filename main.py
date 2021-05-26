from flask import Flask, render_template, redirect, url_for, Response
from functools import wraps
from flask import request

from flask import abort
from flask import jsonify
from apscheduler.schedulers.background import BackgroundScheduler


import requests
from requests.auth import HTTPBasicAuth


import datetime
import base64
import json
import logging


from modules.settings import *
from modules.features_parser import *
from modules.sql_connector import *
from modules.util import *
from modules.scheduler_utils import *


logging.basicConfig(filename="bot.log", filemode='w', level=30)
logging.warning(f"flask_bot started... ({datetime.datetime.today()})")

app = Flask(__name__)

UPLOAD_FOLDER = '/upload/images'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sqly = SqliteDb()
sqly.create_image_table()
sqly.create_text_table()
sqly.create_pool_table()
sqly.drop_settings()
sqly.create_settings_table()


def check_auth(username, password):
    """
    Простая проверка
    """
    return username == 'admin' and password == '999'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n''You have to login with proper credentials', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route("/", methods=['GET', 'POST'])
@requires_auth
def init():
    return redirect(url_for('index'))


@app.route("/index", methods=['GET', 'POST'])
@requires_auth
def index():
    # редактирование базовых настроек - токен и кол-во фото
    sqly = SqliteDb()
    if request.method == "GET":
        settings = sqly.select_settings()
        token = settings[0]['token']
        count = settings[0]['count_foto']
        return render_template("/index.html", title='index', count=count, token=token)
    else:
        count = request.form.to_dict()["count_foto"]
        token = request.form.to_dict()["token"]
        if count:
            sqly.insert_count(count_foto=count)
        if token and len(str(token)) > 22:
            sqly.insert_token(token=token)
        return redirect(url_for('index'))


@app.route("/upload_image", methods=['POST', 'GET'])
@requires_auth
def add_images():
    sqly = SqliteDb()
    if request.method == "GET":
        try:
            groupsql = sqly.get_images_group()
            groups = [i["image_pool"] for i in groupsql]
        except Exception as exc:
            groups = ["...", "..."]
        return render_template("/add_images.html", title='images', groups=groups)
    else:
        image_group = request.form.to_dict()["image_group"]
        #files = request.files

        files = request.files.getlist('img')
        for file in files:
            image_id = upload_images(file)
            db_ans = sqly.insert_image_table(image_pool=image_group,
                                             file_name=str(file.filename),
                                             image_id=str(image_id),
                                             add_datetime=str(datetime.datetime.now()))
        return redirect(url_for('add_images'))


@app.route("/upload_titles", methods=['POST', 'GET'])
@requires_auth
def add_titles():
    sqly = SqliteDb()
    if request.method == "GET":
        try:
            groupsql = sqly.get_texts_groups()
            groups = [i["texts_pool"] for i in groupsql]
        except Exception as exc:
            groups = ["...", "..."]
        return render_template("/add_titles.html", title='titles', groups=groups)
    else:
        # обрабатываем txt файл и сохраняем в базу.
        texts_pool = request.form.to_dict()["text_group"]
        try:
            file = request.files["text"]
            data = file.read()
            data_list = data.decode('cp1251').replace("\n", "").split(";")
            for t in data_list:
                sqly.insert_text(texts_pool=texts_pool, text_content=str(t), add_datetime=datetime.datetime.now())
        except Exception as exc:
            logging.error(f"failed to load file: {exc.args}")
        return redirect(url_for('add_titles'))


@app.route("/add", methods=['POST', 'GET'])
@requires_auth
def add_task():
    cat = request.args.get('category')
    subcat = request.args.get('subcategory')
    offer_type = request.args.get('offer_type')

    if request.method == "POST":
        data = request.form.to_dict()
        pool_name = request.form.to_dict()["pool_name"]
        sqly = SqliteDb()
        ans = sqly.insert_pool(category=int(cat),
                               subcategory=int(subcat),
                               offer_type=int(offer_type),
                               pool_name=str(pool_name),
                               add_datetime=str(datetime.datetime.now()),
                               features=base64.b64encode(json.dumps(data).encode('cp1251')).decode('cp1251'))

        if ans:
            return redirect(url_for('index'))
        else:
            return abort(500)

    else:
        if offer_type:
            answer = requests.get(url=f"https://partners-api.999.md/features?category_id={cat}&subcategory_id={subcat}&offer_type={offer_type}",
                                  params={"lang": "ru"},
                                  auth=HTTPBasicAuth(username=TOKEN, password='101'))

            features = json.loads(answer.text)
            forms = features_parser(features['features_groups'], subcategory_id=subcat)
            return render_template("/features.html",
                                   title='features',
                                   forms=forms)
        elif subcat:
            answer = requests.get(url=f"https://partners-api.999.md/categories/{cat}/subcategories/{subcat}/offer-types",
                                  params={"lang": "ru"},
                                  auth=HTTPBasicAuth(username=TOKEN, password='101'))
            offer_types = json.loads(answer.text)
            return render_template("/offer_type.html",
                                   title='add_task',
                                   offer_types=offer_types['offer_types'],
                                   subcategory=subcat,
                                   category=cat)
        elif cat:
            answer = requests.get(url=f"https://partners-api.999.md/categories/{cat}/subcategories",
                                  params={"lang": "ru"},
                                  auth=HTTPBasicAuth(username=TOKEN, password='101'))
            subcategories = json.loads(answer.text)
            return render_template("/subcategory.html",
                                   title='add_task',
                                   subcategories=subcategories["subcategories"],
                                   category=cat)
        else:
            answer = requests.get(url="https://partners-api.999.md/categories",
                                  params={"lang": "ru"},
                                  auth=HTTPBasicAuth(username=TOKEN, password='101'))
            categories = json.loads(answer.text)
            #{'categories': [{'url': 'transport', 'id': '658', 'title': 'Транспорт'}]}
            return render_template("/category.html",
                                   title='add_task',
                                   categories=categories["categories"])

@app.route('/get_extra_options', methods=['POST'])
@requires_auth
def get_extra_options():
    # ajax
    data = request.form.to_dict()
    parent_option_id = data['parent_option_id']
    dependency_feature_id = data['dependency_feature_id']

    response = get_depends_options(subcategory_id='659',
                                   dependency_feature_id=dependency_feature_id,
                                   parent_option_id=parent_option_id)
    return jsonify(response)

@app.route("/add_schedule", methods=['GET', 'POST'])
@requires_auth
def add_schedule():
    sqly = SqliteDb()
    if request.method == "GET":
        pools_names_row = sqly.get_pools_names()
        pools_names = [i["pool_name"] for i in pools_names_row]
        iter = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}

        # пулы с расписанием
        fullpools_names_row = sqly.get_fullpools_names()
        fullpools_names = [i["pool_name"] for i in fullpools_names_row]
        return render_template("/add_schedule.html", pools_names=pools_names, iter=iter, fullpools_names=fullpools_names)
    else:
        data = request.form.to_dict()
        pool_name = data["pool_name"]
        del data["pool_name"]
        sqly.update_pool(pool_name=pool_name, schedule=base64.b64encode(json.dumps(data).encode()).decode())
        return redirect(url_for('add_schedule'))


@app.route("/start", methods=['GET', 'POST'])
@requires_auth
def start_task():
    sqly = SqliteDb()
    if request.method == "GET":
        fullpools_names_row = sqly.get_fullpools_names()
        fullpools_names = [i["pool_name"] for i in fullpools_names_row]

        # получаем список запущенных задач и их имен
        jobs_list = sched.get_jobs()
        # ////
        # ////
        return render_template("/start_task.html", fullpools_names=fullpools_names, jobs_list=jobs_list)

    else:
        data = request.form.to_dict()
        if data["action"] == "start":
            pool_name = data["pool_name"]
            pool = sqly.get_pool(pool_name=pool_name)
            # запуск задачи с id = poolname !
            job_id = start_scheduler(pool=pool)
        else:
            # останавливаем задачу data[action]==stop
            sched.remove_job(job_id=data["pool_name"])
        return redirect(url_for('start_task'))


if __name__ == "__main__":
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)
    app.run(debug=True)

