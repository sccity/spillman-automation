# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      RLOG.PY
# **********************************************************
# Spillman Digital Paging & Automation
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.#
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import time, logging, traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .settings import settings_data
from .database import connect_read
from .log import setup_logger

err = setup_logger("rlog", "rlog")

s = Service(settings_data["global"]["webdriver"])
o = Options()
o.add_argument("--no-sandbox")
o.add_argument("--disable-extensions")
o.add_argument("--disable-dev-shm-usage")
o.add_argument("--headless")
o.add_argument("--remote-debugging-port=9222")

api_usr = settings_data["spillman"]["user"]
api_pwd = settings_data["spillman"]["password"]


def rlog(rlog_unit, rlog_status, rlog_comment):
    try:
        db_ro = connect_read()
        cursor = db_ro.cursor()
        cursor.execute(
            f"SELECT spillman_usr, spillman_pwd FROM units WHERE unit = '{rlog_unit}' and spillman_usr is not null and spillman_pwd is not null"
        )

    except:
        cursor.close()
        db_ro.close()
        err.error(traceback.format_exc())
        return

    if cursor.rowcount == 0:
        cursor.close()
        db_ro.close()
        rlog_user = api_usr
        rlog_pass = api_pwd

    else:
        results = cursor.fetchone()
        cursor.close()
        db_ro.close()
        rlog_user = results[0]
        rlog_pass = results[1]

    try:
        browser = webdriver.Chrome(service=s, options=o)
        browser.get(settings_data["spillman"]["touch_url"])

    except:
        err.error(traceback.format_exc())
        return

    time.sleep(0.1)

    username = browser.find_element(By.ID, "j_username")
    username.send_keys(rlog_user)
    password = browser.find_element(By.ID, "j_password")
    password.send_keys(rlog_pass)
    password = browser.find_element(By.ID, "unit")
    password.send_keys(rlog_unit)

    time.sleep(0.1)

    try:
        browser.find_element(By.XPATH, value='//input[@value="Login"]').submit()
    except:
        return

    time.sleep(0.1)

    try:
        browser.get(settings_data["spillman"]["touch_url"] + "secure/radiolog")
    except:
        return

    time.sleep(0.1)

    try:
        rlog = Select(browser.find_element(By.XPATH, "//select[@name='status']"))
        rlog.select_by_value(rlog_status)

    except:
        return

    try:
        comment = browser.find_element(By.NAME, "comment")
        comment.send_keys(rlog_comment + " - AUTO RLOG")

    except:
        return

    time.sleep(0.1)

    try:
        browser.find_element(By.XPATH, value='//input[@value="Submit"]').submit()

    except:
        return

    browser.quit()
    return
