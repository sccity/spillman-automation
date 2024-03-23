# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      COMMENTS.PY
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
import os, logging, requests
from logging.handlers import SMTPHandler
from .settings import *


formatter = logging.Formatter(
    "%(levelname)s - %(asctime)s\nFunction: %(funcName)s\nMessage:\n%(message)s\n"
)


class URLGetHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = {
            "app": "Spillman Automation " + env,
            "level": record.levelname,
            "function": record.funcName,
            "msg": record.getMessage(),
        }
        try:
            requests.get(self.url, params=log_entry)
        except Exception as e:
            print(f"Failed to send log message via GET to {self.url}: {e}")


def setup_logger(name, log_file, level=loglevel):
    handler = logging.FileHandler(f"./logs/{log_file}.log")
    handler.setFormatter(formatter)

    credentials = (
        smtp_user,
        smtp_pass,
    )

    mail_handler = SMTPHandler(
        mailhost=(
            smtp_host,
            smtp_port,
        ),
        fromaddr=smtp_from,
        toaddrs=smtp_to,
        subject="Spillman Automation - Application Error",
        credentials=credentials,
        secure=(),
    )
    mail_handler.setFormatter(formatter)

    url = jira_log_api
    url_get_handler = URLGetHandler(url)
    url_get_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    logger.propagate = False
    logger.addHandler(handler)
    logger.addHandler(url_get_handler)
    # logger.addHandler(mail_handler)

    return logger
