# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      FUNCTIONS.PY
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
import sys, json, logging, requests, xmltodict, traceback
from urllib.request import urlopen
from .settings import settings_data
from .database import connect, connect_read
from .log import setup_logger

err = setup_logger("units", "units")


class units:
    def __init__(self, agency):
        self.api_url = settings_data["spillman-api"]["url"]
        self.api_token = settings_data["spillman-api"]["token"]
        self.agency = agency.upper()

    def agency_units(self):
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(f"select unit from units where agency = '{self.agency}'")
            cursor.close()
            db_ro.close()

        except:
            cursor.close()
            db_ro.close()
            return

        units = [list[0] for list in cursor.fetchall()]
        units = ",".join(units)
        return units

    def update(self, callid):
        api = f"{self.api_url}/radiolog?agency={self.agency}&callid={callid}&token={self.api_token}"
        try:
            try:
                response = urlopen(api)
                input = json.loads(response.read())
                units = [
                    unit
                    for unit in input
                    if (unit["status"] != "CMPLT")
                    and (unit["status"] != "ONDT")
                    and (unit["status"] != "8")
                    and (unit["status"] != "NULL")
                ]

                if len(units) > 1:
                    units = {each["unit"]: each for each in units}.values()

                else:
                    for unit in units:
                        units = unit["unit"]

            except Exception as e:
                error = format(str(e))
                if error.find("'NoneType'") != -1:
                    err.debug(f"No paged units for {callid}")
                    return

                else:
                    err.error(traceback.format_exc())
                    return

            unit_list = ""

            try:
                if (len(units) == 1) or (type(units) == str):
                    if type(units) == str:
                        unit_list = units

                    else:
                        units = str(units)
                        units = units.replace("dict_values([{'unit': '", "")
                        units = units.replace("'}])", "")
                        unit_list = units

                else:
                    first = True
                    for unit in units:
                        if first:
                            unit_list = unit.get("unit")
                            first = False

                        else:
                            unit_list += " " + unit.get("unit")

                if (unit_list == "None") or (unit_list is None) or (unit_list == ""):
                    return

            except Exception as e:
                err.error(traceback.format_exc())
                return

            try:
                try:
                    db_ro = connect_read()
                    cursor = db_ro.cursor()
                    cursor.execute(
                        f"SELECT unit, uuid from incidents where callid = '{callid}' and agency = '{self.agency}'"
                    )
                    results = cursor.fetchone()
                    cursor.close()
                    db_ro.close()

                except:
                    cursor.close()
                    db_ro.close()
                    return

                try:
                    db_unit = repr(results[0])
                    db_uuid = results[1]

                except TypeError:
                    db_unit = ""
                    db_unit is None
                    return

                except Exception as e:
                    err.error(traceback.format_exc())

                if db_unit is None:
                    try:
                        db = connect()
                        cursor = db.cursor()
                        cursor.execute(
                            f"update incidents set unit = '{unit_list}' where uuid = '{db_uuid}'"
                        )
                        db.commit()
                        cursor.close()
                        db.close()

                    except Exception as e:
                        cursor.close()
                        db.close()
                        err.error(traceback.format_exc())
                        return

                else:
                    if db_unit == repr(unit_list):
                        err.debug("No new units for " + callid)

                    else:
                        try:
                            db = connect()
                            cursor = db.cursor()
                            cursor.execute(
                                f"update incidents set unit = '{unit_list}', alert_sent = 0 where uuid = '{db_uuid}'"
                            )
                            db.commit()
                            cursor.close()
                            db.close()

                        except:
                            cursor.close()
                            db.close()
                            return

            except Exception as e:
                err.error(traceback.format_exc())
                return

        except Exception as e:
            err.error(traceback.format_exc())
            return

    def get(self, callid):
        api = f"{self.api_url}/radiolog?callid={callid}&token={self.api_token}"
        try:
            try:
                response = urlopen(api)
                input = json.loads(response.read())
                units = [
                    unit
                    for unit in input
                    if (unit["status"] != "CMPLT")
                    and (unit["status"] != "ONDT")
                    and (unit["status"] != "8")
                    and (unit["status"] != "NULL")
                ]

                if len(units) > 1:
                    units = {each["unit"]: each for each in units}.values()

                else:
                    for unit in units:
                        units = unit["unit"]

            except Exception as e:
                error = format(str(e))
                if error.find("'NoneType'") != -1:
                    err.debug(f"No paged units for {callid}")
                    return

                else:
                    err.error(traceback.format_exc())
                    return

            unit_list = ""

            try:
                if (len(units) == 1) or (type(units) == str):
                    if type(units) == str:
                        unit_list = units

                    else:
                        units = str(units)
                        units = units.replace("dict_values([{'unit': '", "")
                        units = units.replace("'}])", "")
                        unit_list = units

                else:
                    first = True
                    for unit in units:
                        if first:
                            unit_list = unit.get("unit")
                            first = False

                        else:
                            unit_list += " " + unit.get("unit")

                if (unit_list == "None") or (unit_list is None) or (unit_list == ""):
                    return

            except Exception as e:
                err.error(traceback.format_exc())
                return

            return unit_list

        except Exception as e:
            err.error(traceback.format_exc())
            return
