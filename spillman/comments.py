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
import json, traceback, requests
import uuid, re
from urllib.request import urlopen
import spillman as s
from datetime import datetime
from .settings import settings_data
from .settings import version_data
from .database import connect, connect_read
from .log import setup_logger

err = setup_logger("comments", "comments")


class comments:
    def __init__(self, agency, agency_type):
        self.version = version_data["version"]
        self.env = settings_data["global"]["env"]
        self.api_url = settings_data["spillman-api"]["url"]
        self.api_token = settings_data["spillman-api"]["token"]
        self.delay = settings_data["active911"]["update_delay"]
        self.agency = agency.upper()
        self.agency_type = agency_type.lower()
        self.units = s.units(self.agency)

    def get(self, calls):
        if type(calls) == dict:
            err.debug("Processing Comments for Call: " + calls["callid"])
            current_callid = calls["callid"]

            if calls["agency"] == self.agency:
                self.process(calls["callid"])

            else:
                err.debug(current_callid + " is not in agency: " + self.agency)

        else:
            try:
                agency_calls = [
                    active_calls
                    for active_calls in calls
                    if active_calls["agency"] == self.agency
                ]

                for active_calls in agency_calls:
                    self.process(active_calls["call_id"])

            except:
                err.error(traceback.format_exc())
                return

    def process(self, callid):
        api = f"{self.api_url}/cad/comments?callid={callid}&token={self.api_token}"
        try:
            try:
                response = urlopen(api)
                comments = json.loads(response.read())

            except Exception as e:
                error = format(str(e))

                if error.find("'NoneType'") != -1:
                    return

                else:
                    err.error(traceback.print_exc())
                    return

        except Exception as e:
            error = format(str(e))
            if error.find("'NoneType'") != -1:
                err.debug(f"No CAD comments for Call ID: {callid}")
                return

            else:
                err.error(traceback.format_exc())
                return

        try:
            units = self.units.get(callid)
        except:
            units = "Unknown"
            
            
        try:
            if units.find("dict") != -1:
                units = "Unknown"
        except:
            units = "Unknown"

        try:
            units = units.replace(" ", ", ")
        except:
            units = "Unknown"

        try:
            cad_comment = comments[0]["comments"]
        except Exception as e:
            error = format(str(e))

            if error.find("'NoneType'") != -1:
                return

            else:
                err.error(traceback.print_exc())
                return

        cad_comment = cad_comment.replace('"', "")
        cad_comment = cad_comment.replace("'", "")
        cad_comment = cad_comment.replace(":", "")

        try:
            proqa_str = str(
                re.findall("ProQA Code [0-9]+[0-9]+[A-Za-z]+[0-9]+[0-9]+", cad_comment)[
                    -1
                ]
            )
            response_cd = proqa_str[13:14]

        except Exception as e:
            error = format(str(e))

            if error.find("'NoneType'") != -1:
                response_cd = "Z"

            elif error.find("'list index out of range'") != -1:
                proqa_sr = str(
                    re.search(
                        "ProQA Code [0-9]+[0-9]+[A-Za-z]+[0-9]+[0-9]+", cad_comment
                    ).group()
                )
                response_cd = proqa_sr[13:14]

            else:
                response_cd = "Z"

        if response_cd == "A":
            response = "Alpha"
        elif response_cd == "B":
            response = "Bravo"
        elif response_cd == "C":
            response = "Charlie"
        elif response_cd == "D":
            response = "Delta"
        elif response_cd == "E":
            response = "Echo"
        else:
            response = "Zulu"

        cad_comment = re.sub(
            r"^[0-9]{6} [0-9]{2}/[0-9]{2}/[0-9]{4} - .*\n?",
            "<CRLF>",
            cad_comment,
            flags=re.MULTILINE,
        )
        
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            sql = f"select gps_x, gps_y from incidents where callid = '{callid}' and agency = '{self.agency}';"
            cursor.execute(sql)
            incident_results = cursor.fetchone()
            cursor.close()
            db_ro.close()

        except:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        try:
            db_gps_x = str(incident_results[0])
            db_gps_y = str(incident_results[1])
        except:
            db_gps_x = "0"
            db_gpx_y = "0"
        
        header = ("Preplan Map:\n"
        + "https://gis.sccity.org/resource/52/display?panel=none&zoom=19&lon=" + db_gps_x + "&lat=" + db_gps_y + "\n"
        + "Priority: "
        + response
        + "\n" 
        + "Responding Units: " 
        + units 
        + "\n")

        footer = (
            "Spillman Mobile:\n"
            + settings_data["spillman"]["touch_url"]
            + "secure/calldetail?longCallId="
            + callid + "&type=" + self.agency_type
            + "\n\n"
            + "Report an Issue:\n"
            + "https://help.scifr.net/index.php?a=add&catid=2&custom1="
            + self.agency
            + "&custom2="
            + callid
            + "\n\nSpillman Automation: v"
            + self.version
            + "\nCopyright Santa Clara City (UT)\nAll Rights Reserved\nEOM\n"
        )

        cad_comments = (
            "\n----------START CAD COMMENTS----------\n"
            + cad_comment
            + "\n-----------END CAD COMMENTS-----------\n\n"
            + footer
        )

        if cad_comments.find("A911-STOP") != -1:
            cad_comments = "CAD COMMENTS LOCKED"
            err.debug("Lockout command found for " + callid)

        if self.env == "DEV":
            cad_comment = (
                "***DEVELOPMENT/TESTING ENVIRONMENT***\n" + header + cad_comments
            )

        else:
            cad_comment = header + cad_comments

        cad_comment = cad_comment.splitlines()
        cad_comment = "<CRLF>".join(cad_comment)

        try:
            try:
                db_ro = connect_read()
                cursor = db_ro.cursor()
                cursor.execute(
                    f"SELECT * from comments where callid = '{callid}' and agency = '{self.agency}'"
                )

            except:
                cursor.close()
                db_ro.close()
                err.error(traceback.format_exc())
                return

            if cursor.rowcount == 0:
                cursor.close()
                db_ro.close()
                try:
                    current_time = datetime.now()
                    unique_id = uuid.uuid1()
                    sql = f"INSERT INTO comments(uuid,agency,callid,comment,processed,updated) values('{unique_id}','{self.agency}','{callid}','{cad_comment}',0,'{current_time}');"

                    try:
                        db = connect()
                        cursor = db.cursor()
                        cursor.execute(sql)

                    except Exception as e:
                        cursor.close()
                        db.close()
                        error = format(str(e))

                        if error.find("Duplicate entry") != -1:
                            err.debug(
                                "CAD comment already exists in alert database for "
                                + callid
                            )
                        else:
                            err.error(traceback.format_exc())
                            return

                    db.commit()
                    cursor.close()
                    db.close()

                except Exception as e:
                    err.error(traceback.format_exc())
                    return

            else:
                try:
                    try:
                        db_ro = connect_read()
                        cursor = db_ro.cursor()
                        cursor.execute(
                            f"SELECT comment, updated from comments where callid = '{callid}' and agency = '{self.agency}'"
                        )

                    except Exception as e:
                        cursor.close()
                        db_ro.close()
                        err.error(traceback.format_exc())
                        return

                    results = cursor.fetchone()
                    cursor.close()
                    db_ro.close()

                    db_comment = str(results[0].encode("utf-8"))
                    comment = str(cad_comment.encode("utf-8"))

                    updated = results[1]
                    current_time = datetime.now()
                    time_diff = current_time - updated
                    time_diff_seconds = time_diff.total_seconds()

                    if re.sub(r"\W+", "", db_comment) == re.sub(r"\W+", "", comment):
                        err.debug("No new CAD comments for " + callid)

                    elif time_diff_seconds < self.delay:
                        err.debug("Waiting to process alert for comments for " + callid)

                    elif re.sub(r"\W+", "", db_comment) != re.sub(r"\W+", "", comment):
                        try:
                            db = connect()
                            cursor = db.cursor()
                            cursor.execute(
                                f"update comments set comment = '{cad_comment}', processed = 0, updated = '{current_time}' where callid = '{callid}' and agency = '{self.agency}'"
                            )

                        except Exception as e:
                            cursor.close()
                            db.close()
                            err.error(traceback.format_exc())
                            return

                        db.commit()
                        cursor.close()
                        db.close()

                    else:
                        err.error(traceback.format_exc())
                        return

                except Exception as e:
                    err.error(traceback.format_exc())
                    return

        except Exception as e:
            err.error(traceback.format_exc())
            return
