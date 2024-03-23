# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      SETTINGS.PY
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
import os, sys, yaml

env = os.environ["ENV"]
loglevel = os.environ["LOGLEVEL"]
nwsid = os.environ["NWSID"]
webdriver = os.environ["WEBDRIVER"]
jira_log_api = os.environ["JIRA_LOG_API"]

smtp_host = os.environ["SMTP_HOST"]
smtp_port = int(os.environ["SMTP_PORT"])
smtp_user = os.environ["SMTP_USER"]
smtp_pass = os.environ["SMTP_PASS"]
smtp_from = os.environ["SMTP_FROM"]
smtp_to = os.environ["SMTP_TO"]

db_schema = os.environ["DB_SCHEMA"]
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
db_host_ro = os.environ["DB_HOST_RO"]

spillman_api_url = os.environ["SPILLMAN_API_URL"]
spillman_api_token = os.environ["SPILLMAN_API_TOKEN"]
spillman_url = os.environ["SPILLMAN_URL"]
spillman_touch_url = os.environ["SPILLMAN_TOUCH_URL"]
spillman_user = os.environ["SPILLMAN_USER"]
spillman_password = os.environ["SPILLMAN_PASSWORD"]
spillman_send_rlog = os.environ["SPILLMAN_SEND_RLOG"]

active911_send_alerts = os.environ["ACTIVE911_SEND_ALERTS"]
active911_update_delay = int(os.environ["ACTIVE911_UPDATE_DELAY"])
active911_snpp_host = os.environ["ACTIVE911_SNPP_HOST"]
active911_snpp_port = int(os.environ["ACTIVE911_SNPP_PORT"])
active911_snpp_timeout = int(os.environ["ACTIVE911_SNPP_TIMEOUT"])

version_file = "./spillman/version.yaml"
if not os.path.exists(version_file):
    print("version.yaml not found!")
    sys.exit()

with open(version_file, "r") as f:
    version_data = yaml.load(f, Loader=yaml.FullLoader)
