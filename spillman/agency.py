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
from contextlib import contextmanager

err = setup_logger("agency", "agency")

class AgencyProcessor:
    def __init__(self):
        pass

    @staticmethod
    def fetch_active_agencies():
        try:
            with db_connection_read() as db_ro:
                cursor = db_ro.cursor()
                cursor.execute("SELECT agency_id, agency_type, active911_id FROM agency WHERE active = 1")
                agencies = cursor.fetchall()
                return agencies
        except Exception:
            err.error(traceback.format_exc())
            return []

    @staticmethod
    def process_agency(agency):
        try:
            agency_id, agency_type, agency_a911 = agency
            current_agency = s.IncidentsProcessor(str(agency_id), str(agency_type))
            agency_alerts = s.alerts(str(agency_id), str(agency_a911))

            agency_calls = current_agency.active()
            if agency_calls:
                current_agency.insert(agency_calls)
                agency_comments = s.comments(str(agency_id), str(agency_type))
                agency_comments.get(agency_calls)
                agency_alerts.incidents()
                agency_alerts.comments()

            non_agency_calls = current_agency.other()
            if non_agency_calls:
                current_agency.alerts(non_agency_calls)
                agency_alerts.incidents()
                agency_alerts.comments()

        except Exception:
            err.error(traceback.format_exc())

def process_all_agencies():
    try:
        agency_processor = AgencyProcessor()
        agencies = agency_processor.fetch_active_agencies()

        for agency in agencies:
            agency_processor.process_agency(agency)

    except Exception:
        err.error(traceback.format_exc())

@contextmanager
def db_connection_read():
    db_ro = connect_read()
    try:
        yield db_ro
    finally:
        db_ro.close()

if __name__ == "__main__":
    process_all_agencies()
