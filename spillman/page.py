# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      PAGE.PY
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
import traceback
from re import search
from telnetlib import Telnet
from .settings import *
from .log import setup_logger

err = setup_logger("page", "page")

sendalerts = active911_send_alerts


def send_page(page, a911_id):
    unit = f"page {a911_id}"
    page = repr(page)
    mess = f"mess {page}"
    send = "send"
    exitcmd = "exit"

    if a911_id is None:
        err.warning("Missing Active911 ID!")
        return

    if sendalerts == "N":
        err.info("Page Message: " + page)
        return

    with Telnet(
        active911_snpp_host,
        active911_snpp_port,
        active911_snpp_timeout,
    ) as tn:
        try:
            tn.set_debuglevel(0)
            tn.read_until(
                b"220 Active911 SNPP ready, What is your emergency?\r", timeout=20
            ).decode("utf-8")
            tn.write(unit.encode("utf-8") + b"\r\n")
            tn.read_until(b"250 OK... \r\n", timeout=20).decode("utf-8")
            tn.write(mess.encode("utf-8") + b"\r\n")
            tn.read_until(b"250 Message OK\r\n", timeout=20).decode("utf-8")
            tn.write(send.encode("utf-8") + b"\r\n")
            success = tn.read_until(
                b"250 Message Sent Successfully\r\n", timeout=20
            ).decode("utf-8")

            if search("250 Message Sent Successfully", success):
                return_cd = 0
            else:
                return_cd = 1

            tn.write(exitcmd.encode("utf-8") + b"\r\n")

        except:
            err.error(traceback.format_exc())
            return_cd = 99

        return return_cd
