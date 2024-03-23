# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      CLEANUP.PY
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
from .database import connect, connect_read
from .log import setup_logger

err = setup_logger("cleanup", "cleanup")


def main():
    try:
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(
                "select agency, callid from incidents where alert_sent = 0 and TIMEDIFF(now(), reported) > '24:00:00'"
            )

        except:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        if cursor.rowcount == 0:
            cursor.close()
            db_ro.close()
            return

        try:
            results = cursor.fetchall()
            cursor.close()
            db_ro.close()
            incidents_list = [row for row in results if row[0] is not None]

            for row in incidents_list:
                try:
                    db = connect()
                    cursor = db.cursor()
                    cursor.execute(
                        f"update incidents set alert_sent = 1 where callid = '{row[1]}' and agency = '{row[0]}'"
                    )
                    cursor.execute(
                        f"update comments set processed = 1 where callid = '{row[1]}' and agency = '{row[0]}'"
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
            cursor.close()
            db.close()
            err.error(traceback.format_exc())
            return

    except:
        err.error(traceback.format_exc())
        return
