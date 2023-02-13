# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      STATUS.PY
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
import json, logging, requests, xmltodict, traceback
from urllib.request import urlopen
from datetime import datetime
from .rlog import rlog
from .alerts import alerts
from .settings import settings_data
from .database import connect, connect_read
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from .log import setup_logger

err = setup_logger("status", "status")

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class status:
    def __init__(self, agency):
        self.api_url = settings_data["spillman"]["url"]
        self.api_usr = settings_data["spillman"]["user"]
        self.api_pwd = settings_data["spillman"]["password"]
        self.api_url = settings_data["spillman-api"]["url"]
        self.api_token = settings_data["spillman-api"]["token"]
        self.agency = agency.upper()

    def unit(self):
        api = f"{self.api_url}/spillman/unit/status?agency={self.agency}&token={self.api_token}"
        try:
            response = urlopen(api)
            try:
                status = json.loads(response.read())
            except Exception as e:
                error = format(str(e))
                if error.find("'NoneType'") != -1:
                    err.debug(f"No units for {self.agency}")
                    return
                else:
                    err.error(traceback.format_exc())
                    return

            for units in status:
                try:
                    err.debug(
                        "Processing Unit: " + units["unit"] + " " + units["status"]
                    )

                    unit = units["unit"]
                    status = units["status"]
                    time_str = units["status_time"]
                    time_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    now = datetime.now()

                    duration = now - time_obj
                    duration_in_s = duration.total_seconds()
                    hours = divmod(duration_in_s, 3600)[0]

                    if hours < 1:
                        status_time = str(int(divmod(duration_in_s, 60)[0])) + " min(s)"
                    elif (hours >= 1) and (hours < 24):
                        status_time = str(int(hours)) + " hour(s)"
                    elif hours >= 24:
                        status_time = (
                            str(int(divmod(duration_in_s, 86400)[0])) + " day(s)"
                        )
                    else:
                        status_time = str(int(divmod(duration_in_s, 60)[0])) + " min(s)"

                    try:
                        message = units["desc"]

                    except:
                        message = ""

                    cross_staff_flag = 0
                    cross_staff_units = None

                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(f"SELECT auto_rlog_flag from agency where agency_id = '{self.agency}'")

                        db_response = cursor.fetchone()
                        rlog_flag = db_response[0]
                        cursor.close()
                        db_ro.close()
                    except:
                        cursor.close()
                        db_ro.close()
                        err.error(traceback.format_exc())
                        continue

                    if rlog_flag == 0:
                        continue
                    else:
                        pass

                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(f"SELECT unit, cross_staff_flag, cross_staff_units, always_on_flag from units where unit = '{unit}' and agency = '{self.agency}'")
                        db_response = cursor.fetchone()
                        cross_staff_flag = db_response[1]
                        cross_staff_units = db_response[2]
                        cursor.close()
                        db_ro.close()

                    except:
                        cursor.close()
                        db_ro.close()
                        try:
                            db = connect()
                            cursor = db.cursor()
                            cursor.execute(
                                f"insert into units (unit,agency) values ('{unit}','{self.agency}')"
                            )
                            db.commit()
                            cursor.close()
                            db.close()
                        except:
                            cursor.close()
                            db.close()
                            err.error(traceback.format_exc())
                            continue

                    try:
                        db = connect()
                        cursor = db.cursor()
                        cursor.execute(
                            f"update units set status = '{status}', status_time = '{status_time}', status_desc = '{message}' where unit = '{unit}' and agency = '{self.agency}'"
                        )
                        db.commit()
                        cursor.close()
                        db.close()
                    except:
                        cursor.close()
                        db.close()
                        err.error(traceback.format_exc())
                        continue

                    if (status == "ONAIR") and (hours >= 1):
                        err.debug(f"{self.agency}:{unit} - ONAIR Timeout 1hr")

                        rlog(unit, "ONDT", "ONAIR TIMEOUT")
                        callid = (
                            unit
                            + "-"
                            + f"{stime[15:19]}-{stime[9:11]}-{stime[12:14]}{stime[0:8]}"
                        )

                        alerts.send(
                            self.agency,
                            callid,
                            f"ONAIR TIMEOUT - {unit}",
                            unit,
                            self.agency,
                            self.agency,
                            self.agency,
                            "0.0",
                            "0.0",
                            now,
                            f"{unit} ONAIR GREATER THAN 1HR; AUTOMATICALLY RESET TO AIQ/ONDT",
                        )

                    elif (status == "ONAIR") and ("AOA" not in message):
                        err.debug(f"{unit} updated AOA description")
                        rlog(unit, "ONAIR", "AOA - AVAILABLE NOT IN QUARTERS")

                    elif (cross_staff_flag == 1) and (
                        status in "PAGED, ENRT, ARRVD, ARVDH, ENRTH, STAGE, ONAIR"
                    ):
                        for cs_units in cross_staff_units.split(","):
                            cs_unit = cs_units.strip()

                            try:
                                c_stat = self.current(cs_unit)

                            except:
                                c_stat = "ERR"

                            if (c_stat in "PAGED, 8, ONDT, BUSY, ERR") and (
                                c_stat != "XBSY"
                            ):
                                if c_stat != "XBSY":
                                    err.debug(f"{cs_unit} set to XBSY")
                                    rlog(cs_unit, "XBSY", "CROSS STAFF W/" + unit)
                                else:
                                    err.debug(f"{cs_unit} already XBSY")

                    elif (cross_staff_flag == 1) and (status in "ONDT, 8"):
                        try:
                            for cs_units in cross_staff_units.split(","):
                                cs_unit = cs_units.strip()

                                try:
                                    c_stat = self.current(cs_unit)

                                except:
                                    c_stat = "ERR"

                                if c_stat == "XBSY":
                                    err.debug(f"{unit} set to ONDT")
                                    rlog(cs_unit, "ONDT", "CROSS STAFF ADJUSTMENT")
                        except:
                            return

                except Exception as e:
                    error = format(str(e))
                    if error.find("'None'") != -1:
                        pass

                    else:
                        err.error(traceback.format_exc())
                        return

        except Exception as e:
            err.error(traceback.format_exc())
            return

    def current(self, unit):
        api = f"{self.api_url}/spillman/unit/status?agency={self.agency}&unit={unit}&token={self.api_token}"
        try:
            response = urlopen(api)
            try:
                cstatus = json.loads(response.read())
            except Exception as e:
                error = format(str(e))
                if error.find("'NoneType'") != -1:
                    err.debug(f"No units for {self.agency}")
                    return

                else:
                    err.error(traceback.format_exc())
                    return

            return cstatus[0]["status"]

        except:
            err.error(traceback.format_exc())
            return
