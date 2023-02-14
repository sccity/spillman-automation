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
import logging, requests, xmltodict, traceback
import spillman as s
from .database import connect_read
from .log import setup_logger

err = setup_logger("agency", "agency")


class agency:
    def __init__(self):
        return

    def get():
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute("select agency_id, agency_type, active911_id from agency where active = 1")

        except:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        agencies = list(cursor.fetchall())
        cursor.close()
        db_ro.close()
        return agencies

    def agency_process(agency):
        agency_id = agency[0]
        agency_type = agency[1]
        agency_a911 = agency[2]

        current_agency = s.incidents(agency_id, agency_type)
        agency_alerts = s.alerts(agency_id, agency_a911)
        agency_calls = current_agency.active()

        if agency_calls is None:
            err.debug(f"No Active Calls for {agency_id}")

        else:
            current_agency.insert(agency_calls)
            agency_comments = s.comments(agency_id)
            agency_comments.get(agency_calls)
            agency_alerts.incidents()
            agency_alerts.comments()

        non_agency_calls = current_agency.other()

        if not non_agency_calls:
            err.debug("No Active Other Agency Calls")

        else:
            current_agency.alerts(non_agency_calls)

    def paging(agency_list):
        try:
            for agency in agency_list:
                s.agency.agency_process(agency)

        except:
            err.error(traceback.format_exc())
            return
