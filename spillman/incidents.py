# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      INCIDENTS.PY
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
import json, xmltodict, traceback, collections, uuid
import spillman as s
from urllib.request import urlopen
from .settings import settings_data
from .database import connect, connect_read
from .log import setup_logger

err = setup_logger("incidents", "incidents")


class incidents:
    def __init__(self, agency, agency_type):
        self.api_url = settings_data["spillman-api"]["url"]
        self.api_token = settings_data["spillman-api"]["token"]
        self.agency = agency.upper()
        self.agency_type = agency_type.lower()
        self.units = s.units(self.agency)
        self.agency_units = self.units.agency_units()

    def active(self):
        api = f"{self.api_url}/cad/active?agency={self.agency}&token={self.api_token}"
        try:
            try:
                response = urlopen(api)
                input_json = json.loads(response.read())
                calls = [
                    call
                    for call in input_json
                    if (call["status"] != "RCVD")
                    and (call["status"] != "ASSGN")
                    and (call["status"] != "ONRPT")
                    and (call["status"] != "NULL")
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.format_exc())
                    return

        except:
            err.error(traceback.format_exc())
            return

        return calls

    def other(self):
        api = f"{self.api_url}/cad/active?token={self.api_token}"
        try:
            try:
                response = urlopen(api)
                input_json = json.loads(response.read())
                calls = [
                    call
                    for call in input_json
                    if (call["status"] != "RCVD")
                    and (call["status"] != "ASSGN")
                    and (call["status"] != "ONRPT")
                    and (call["status"] != "NULL")
                    and (call["agency"] != self.agency)
                ]

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.print_exc())
                    return

        except:
            err.error(traceback.print_exc())

        return calls

    def insert(self, calls):
        if type(calls) == dict:
            self.insert_data(calls)

        else:
            for active_calls in calls:
                self.insert_data(active_calls)

    def insert_data(self, active_calls):
        try:
            callid = active_calls["call_id"]

            try:
                recid = active_calls["incident_id"]
            except:
                recid = active_calls["call_id"]

            agency_id = active_calls["agency"]
            zone = active_calls["zone"]
            address = active_calls["address"]
            gps_x = active_calls["longitude"]
            gps_y = active_calls["latitude"]
            reported = active_calls["date"]
            status = active_calls["status"]

            try:
                unit = active_calls["responsible_unit"]

            except:
                if status == "RCVD":
                    if (zone is None) or (zone == ""):
                        unit = "PRE"
                    else:
                        unit = zone + "*"
                else:
                    unit = ""

            try:
                try:
                    db_ro = connect_read()
                    cursor = db_ro.cursor()
                    cursor.execute(
                        f"SELECT `desc` from nature where abbr = '{active_calls['nature']}'"
                    )

                except:
                    cursor.close()
                    db_ro.close()
                    nature = {active_calls["nature"]}

                db_nature = cursor.fetchone()
                cursor.close()
                db_ro.close()
                nature = db_nature[0]

            except:
                nature = {active_calls["nature"]}

            if nature is None:
                nature = "Unknown"

            try:
                if status == "RCVD":
                    nature = "PRE ALERT - " + nature + " - " + zone
                    callid = "PRE_" + callid

                else:
                    nature = nature + " - " + zone

            except:
                nature = nature

            try:
                try:
                    db_ro = connect_read()
                    cursor = db_ro.cursor()
                    cursor.execute(
                        f"SELECT name from cities where abbr = '{active_calls['city']}'"
                    )

                except KeyError:
                    try:
                        cursor.execute("SELECT name from cities where abbr = 'WCO'")

                    except:
                        cursor.close()
                        db_ro.close()
                        city = {active_calls["city"]}

                except:
                    cursor.close()
                    db_ro.close()
                    err.error(traceback.format_exc())
                    return

                db_city = cursor.fetchone()
                cursor.close()
                db_ro.close()
                city = db_city[0]

            except:
                city = {active_calls["city"]}

        except KeyError:
            err.debug("CallID: " + callid + " missing incident ID")
            return

        except Exception as e:
            err.error(traceback.format_exc())
            return

        if (unit == "") or (unit is None):
            err.debug(callid + " is missing a unit")
            return

        else:
            self.process(
                callid,
                recid,
                nature,
                agency_id,
                city,
                zone,
                address,
                gps_x,
                gps_y,
                reported,
            )

            if unit[0:3] == "PRE":
                try:
                    db = connect()
                    cursor = db.cursor()
                    sql = f"update incidents set unit = '{unit}' where callid = '{callid}' and agency = '{self.agency}';"
                    cursor.execute(sql)

                except:
                    cursor.close()
                    db.close()
                    err.error(traceback.format_exc())
                    return
                db.commit()
                cursor.close()
                db.close()

    def alerts(self, calls):
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(
                f"select pre_alert_zones from agency where agency_id = '{self.agency}'"
            )

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        pre_alert_zones = [list[0] for list in cursor.fetchall()]
        cursor.close()
        db_ro.close()

        try:
            pre_alert_zones = ",".join(pre_alert_zones)
        except TypeError:
            pre_alert_zones = ""

        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(
                f"select pre_alert_natures from agency where agency_id = '{self.agency}'"
            )

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        pre_alert_natures = [list[0] for list in cursor.fetchall()]
        cursor.close()
        db_ro.close()

        try:
            pre_alert_natures = ",".join(pre_alert_natures)
        except TypeError:
            pre_alert_natures = ""

        comments = s.comments(self.agency)

        if type(calls) == dict:
            try:
                callid = calls.get("call_id")

                try:
                    recid = calls.get("incident_id")
                except:
                    recid = calls.get("call_id")

                agency_id = calls.get("agency")

                try:
                    zone = calls.get("zone")
                except:
                    zone = "NONE"

                try:
                    unit = calls.get("responsible_unit")
                except:
                    unit = ""

                address = calls.get("address")
                gps_x = calls.get("longitude")
                gps_y = calls.get("latitude")
                reported = calls.get("date")
                call_type = calls.get("type")

                try:
                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(
                            f"SELECT `desc` from nature where abbr = '{calls.get('nature')}'"
                        )

                    except Exception as e:
                        cursor.close()
                        db_ro.close()
                        err.error(traceback.format_exc())
                        return

                    db_nature = cursor.fetchone()
                    cursor.close()
                    db_ro.close()
                    nature = db_nature[0]

                except:
                    nature = calls.get("nature")

                if nature is None:
                    nature = "Unknown"

                try:
                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(
                            f"SELECT name from cities where abbr = '{calls.get('city')}'"
                        )

                    except KeyError:
                        try:
                            cursor.execute("SELECT name from cities where abbr = 'WCO'")
                        except:
                            cursor.close()
                            db_ro.close()
                            city = calls.get("city")

                    except Exception as e:
                        cursor.close()
                        db_ro.close()
                        err.error(traceback.format_exc())
                        return

                    db_city = cursor.fetchone()
                    cursor.close()
                    db_ro.close()
                    city = db_city[0]

                except:
                    city = calls.get("city")

            except KeyError:
                err.debug("CallID: " + callid + " missing incident ID")
                return

            except Exception as e:
                err.error(traceback.format_exc())
                return

            if unit == "":
                err.debug(callid + " is missing a unit")
                return

            elif unit is None:
                err.debug(callid + " is missing a unit")
                return

            else:
                units = self.units.get(callid)

                try:
                    units = units.replace(" ", ",")
                except:
                    return

                mutual_aid_units = ""

                first = True
                mutual_aid = False

                try:
                    for unit in units.split(","):
                        for agency_unit in self.agency_units.split(","):
                            if unit == agency_unit:
                                mutual_aid = True
                                if first:
                                    mutual_aid_units = agency_unit
                                    first = False
                                else:
                                    mutual_aid_units += " " + agency_unit
                except:
                    return

                if call_type == "Fire":
                    call_type_short = "f"
                elif call_type == "EMS":
                    call_type_short = "e"
                elif call_type == "Law":
                    call_type_short = "l"
                else:
                    call_type_short = "o"

                if units is None:
                    return
                  
                elif units == "":
                    return

                elif (
                    (mutual_aid is True)
                    and (call_type_short == self.agency_type)
                    and (self.agency != agency_id)
                ):
                    err.debug(callid + " is a mutual aid call for " + self.agency)
                    if nature is None:
                        nature = "Unknown"
                    if city is None:
                        city = "Unknown"
                    nature = "MUTUAL AID - " + nature + " - " + city
                    self.process(
                        callid,
                        recid,
                        nature,
                        self.agency,
                        city,
                        zone,
                        address,
                        gps_x,
                        gps_y,
                        reported,
                    )
                    comments.process(callid)

                    try:
                        mutual_aid_units = mutual_aid_units.replace(" ", ",")
                        db = connect()
                        cursor = db.cursor()

                        try:
                            mutual_aid_units = mutual_aid_units.replace(",", " ")
                        except:
                            mutual_aid_units = ""

                        sql = f"update incidents set unit = '{mutual_aid_units}' where callid = '{callid}' and agency = '{self.agency}';"
                        cursor.execute(sql)

                    except:
                        cursor.close()
                        db.close()
                        err.error(traceback.format_exc())
                        return

                    db.commit()
                    cursor.close()
                    db.close()
                    return

                else:
                    err.debug(callid + " is not a mutual aid call for " + self.agency)

                if (zone in pre_alert_zones) and (nature in pre_alert_natures):
                    err.debug(callid + " is a pre alert call for " + self.agency)
                    nature = "PRE ALERT - " + nature + " - " + city
                    self.process(
                        callid,
                        recid,
                        nature,
                        self.agency,
                        city,
                        zone,
                        address,
                        gps_x,
                        gps_y,
                        reported,
                    )
                    comments.process(callid)

                    try:
                        db = connect()
                        cursor = db.cursor()
                        sql = f"""update incidents set unit = 'PRE' where callid = '{callid}' and agency = '{self.agency}';"""
                        cursor.execute(sql)

                    except:
                        cursor.close()
                        db.close()
                        err.error(traceback.format_exc())
                        return

                    db.commit()
                    cursor.close()
                    db.close()
                    return

                else:
                    err.debug(callid + " is not a pre alert call for " + self.agency)

        else:
            for active_calls in calls:
                try:
                    callid = active_calls["call_id"]

                    try:
                        recid = active_calls["incident_id"]
                    except:
                        recid = active_calls["call_id"]

                    agency_id = active_calls["agency"]

                    try:
                        zone = active_calls["zone"]
                    except:
                        zone = "NONE"

                    try:
                        unit = active_calls["responsible_unit"]
                    except:
                        unit = ""

                    address = active_calls["address"]
                    gps_x = active_calls["longitude"]
                    gps_y = active_calls["latitude"]
                    reported = active_calls["date"]
                    call_type = active_calls["type"]

                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(
                            f"SELECT `desc` from nature where abbr = '{active_calls['nature']}'"
                        )

                        db_nature = cursor.fetchone()
                        cursor.close()
                        db_ro.close()
                        
                        try:
                            nature = db_nature[0]
                        except:
                            nature = "Unknown"

                    except:
                        try:
                            cursor.close()
                            db_ro.close()
                        except:
                            err.info(traceback.format_exc())
                            
                        try:
                            nature = active_calls["nature"]
                        except:
                            nature = "Unknown"

                    if nature == "Unknown":
                        try:
                            nature = active_calls["nature"]
                        except:
                            nature = "Unknown"
                            
                    if nature is None:
                        nature = "Unknown"

                    try:
                        try:
                            db_ro = connect_read()
                            cursor = db_ro.cursor()
                            cursor.execute(
                                f"SELECT name from cities where abbr = '{active_calls['city']}'"
                            )

                        except KeyError:
                            try:
                                cursor.execute("SELECT name from cities where abbr = 'WCO'")

                            except:
                                cursor.close()
                                db_ro.close()
                                city = active_calls["city"]

                        except Exception as e:
                            err.error(traceback.format_exc())
                            continue

                        db_city = cursor.fetchone()
                        cursor.close()
                        db_ro.close()
                        city = db_city[0]

                    except:
                        city = active_calls["city"]

                except Exception as e:
                    err.error(traceback.format_exc())
                    continue

                if unit == "":
                    err.debug(callid + " is missing a unit")
                    continue

                elif unit is None:
                    err.debug(callid + " is missing a unit")
                    continue
                    
                else:
                    units = self.units.get(callid)

                    try:
                        units = units.replace(" ", ",")
                    except:
                        continue

                    mutual_aid_units = ""

                    first = True
                    mutual_aid = False

                    try:
                        for unit in units.split(","):
                            for agency_unit in self.agency_units.split(","):
                                if unit == agency_unit:
                                    mutual_aid = True
                                    if first:
                                        mutual_aid_units = agency_unit
                                        first = False
                                    else:
                                        mutual_aid_units += " " + agency_unit
                    except:
                        continue

                    if call_type == "Fire":
                        call_type_short = "f"
                    elif call_type == "EMS":
                        call_type_short = "e"
                    elif call_type == "Law":
                        call_type_short = "l"
                    else:
                        call_type_short = "o"

                    if units is None:
                        continue

                    elif (
                        (mutual_aid is True)
                        and (call_type_short == self.agency_type)
                        and (self.agency != agency_id)
                        and (unit is not None)
                    ):

                        err.debug(callid + " is a mutual aid call for " + self.agency)

                        nature = "MUTUAL AID - " + nature + " - " + city

                        self.process(
                            callid,
                            recid,
                            nature,
                            self.agency,
                            city,
                            zone,
                            address,
                            gps_x,
                            gps_y,
                            reported,
                        )

                        comments.process(callid)

                        try:
                            db = connect()
                            cursor = db.cursor()

                            try:
                                mutual_aid_units = mutual_aid_units.replace(",", " ")
                            except:
                                mutual_aid_units = ""

                            sql = f"update incidents set unit = '{mutual_aid_units}' where callid = '{callid}' and agency = '{self.agency}';"
                            cursor.execute(sql)

                        except:
                            cursor.close()
                            db.close()
                            err.error(traceback.format_exc())
                            continue

                        db.commit()
                        cursor.close()
                        db.close()
                        continue

                    elif (zone in pre_alert_zones) and (nature in pre_alert_natures):
                        err.debug(callid + " is a pre alert call for " + self.agency)

                        nature = "PRE ALERT - " + nature + " - " + city
                        self.process(
                            callid,
                            recid,
                            nature,
                            self.agency,
                            city,
                            zone,
                            address,
                            gps_x,
                            gps_y,
                            reported,
                        )
                        comments.process(callid)

                        try:
                            db = connect()
                            cursor = db.cursor()
                            sql = ""
                            sql = f"""update incidents set unit = 'PRE' where callid = '{callid}' and agency = '{self.agency}';"""
                            cursor.execute(sql)

                        except:
                            cursor.close()
                            db.close()
                            err.error(traceback.format_exc())
                            continue

                        db.commit()
                        cursor.close()
                        db.close()
                        continue

                    else:
                        err.debug(
                            callid
                            + " is not a pre alert or mutual aid call for "
                            + self.agency
                        )

    def process(
        self, callid, recid, nature, agency, city, zone, address, gps_x, gps_y, date
    ):
        try:
            unique_id = uuid.uuid1()
            sql = ""
            sql = f"""
            INSERT INTO
            incidents(
                uuid,
                callid,
                incidentid,
                nature,
                agency,
                city,
                zone,
                address,
                gps_x,
                gps_y,
                reported,
                alert_sent)
            values(
                '{unique_id}',
                '{callid}',
                '{recid}',
                '{nature}',
                '{agency}',
                '{city}',
                '{zone}',
                '{address}',
                '{gps_x}',
                '{gps_y}',
                '{date}',
                0);
            """

            try:
                db = connect()
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
                cursor.close()
                db.close()

            except Exception as e:
                cursor.close()
                db.close()
                error = format(str(e))

                if error.find("Lock wait timeout exceeded") != -1:
                    return
                    err.error(traceback.format_exc())

                if error.find("Duplicate entry") != -1:
                    try:
                        try:
                            db_ro = connect_read()
                            cursor = db_ro.cursor()
                            sql = f"SELECT uuid, nature, city, address, incidentid from incidents where callid = '{callid}' and agency = '{self.agency}';"
                            cursor.execute(sql)
                            incident_results = cursor.fetchone()
                            cursor.close()
                            db_ro.close()

                        except:
                            cursor.close()
                            db_ro.close()
                            err.error(traceback.format_exc())
                            return

                        db_uuid = incident_results[0]
                        db_nature = incident_results[1]
                        db_city = incident_results[2]
                        db_address = incident_results[3]
                        db_incidentid = incident_results[4]

                        if nature != db_nature:
                            try:
                                db = connect()
                                cursor = db.cursor()
                                cursor.execute(
                                    f"update incidents set nature = '{nature}', alert_sent = 0 where uuid = '{db_uuid}'"
                                )
                                db.commit()
                                cursor.close()
                                db.close()

                            except:
                                cursor.close()
                                db.close()
                                err.error(traceback.format_exc())
                                return

                        if city != db_city:
                            try:
                                db = connect()
                                cursor = db.cursor()
                                cursor.execute(
                                    f"update incidents set city = '{city}', alert_sent = 0 where uuid = '{db_uuid}'"
                                )
                                db.commit()
                                cursor.close()
                                db.close()

                            except:
                                cursor.close()
                                db.close()
                                err.error(traceback.format_exc())
                                return

                        if address != db_address:
                            try:
                                db = connect()
                                cursor = db.cursor()
                                cursor.execute(
                                    f"update incidents set address = '{address}', alert_sent = 0 where uuid = '{db_uuid}'"
                                )
                                db.commit()
                                cursor.close()
                                db.close()

                            except:
                                cursor.close()
                                db.close()
                                err.error(traceback.format_exc())
                                return

                        if recid != db_incidentid:
                            try:
                                db = connect()
                                cursor = db.cursor()
                                cursor.execute(
                                    f"update incidents set incidentid = '{recid}' where uuid = '{db_uuid}'"
                                )
                                db.commit()
                                cursor.close()
                                db.close()

                            except:
                                cursor.close()
                                db.close()
                                err.error(traceback.format_exc())
                                return

                    except:
                        err.debug(
                            "Incident already exists in alert database for "
                            + callid
                            + " reported "
                            + date
                        )

                else:
                    err.error(traceback.format_exc())

            self.units.update(callid)

        except Exception as e:
            err.error(traceback.format_exc())
