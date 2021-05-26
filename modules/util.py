import requests
import json
from requests.auth import HTTPBasicAuth
from modules.settings import *


def get_user_phones():
    answer = requests.get(
        url=f"https://partners-api.999.md/phone_numbers",
        params={"lang": "ru"},
        auth=HTTPBasicAuth(username=TOKEN, password='101'))
    phone_list = json.loads(answer.text)
    if phone_list["phone_numbers"]:
        phone_number = phone_list["phone_numbers"][0]["phone_number"]
        return phone_number
    else:
        return None


def upload_images(file):
    # You can upload up to 1200 images per day.
    answer = requests.post(
        url=f"https://partners-api.999.md/images",
        files={'file': file},
        auth=HTTPBasicAuth(username=TOKEN, password='101'),
    )
    answer_dict = json.loads(answer.text)
    if answer_dict:
        return answer_dict["image_id"]
    else:
        return None


def get_depends_options(subcategory_id, dependency_feature_id, parent_option_id):
    answer = requests.get(
        url=f"https://partners-api.999.md/dependent_options",
        params={"lang": "ru",
                "subcategory_id": subcategory_id,
                "dependency_feature_id": dependency_feature_id,
                "parent_option_id": parent_option_id},
        auth=HTTPBasicAuth(username=TOKEN, password='101'))
    options = json.loads(answer.text)

    return options


def post_advert(advert):
    answer = requests.post(url="https://partners-api.999.md/adverts",
                           auth=HTTPBasicAuth(username=TOKEN, password='101'),
                           data=advert)
    return answer

