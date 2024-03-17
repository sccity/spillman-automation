# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      ACTIVE911.PY
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
import sys, os, time, click
import spillman as s
from spillman.database import connect_read


@click.command()
@click.option("--paging", is_flag=True, help="Start digital paging process.")
@click.option("--units", is_flag=True, help="Start unit status monitoring process.")
@click.option("--misc", is_flag=True, help="Execute miscellaneous functions.")
@click.option("--cleanup", is_flag=True, help="Perform cleanup operations.")
@click.option("--check-config", is_flag=True, help="Check configuration.")
@click.option("--test", is_flag=True, help="Test mode.")
def main(paging, units, misc, cleanup, check_config, test):
    syslog = s.setup_logger("system", "system")
    pid = str(os.getpid())

    if not any([paging, units, misc, cleanup, check_config]):
        syslog.info("No option provided")
        sys.exit(0)

    if paging:
        process_name = "paging"
        process_description = "Digital Paging"
        pidfile = (
            "/var/run/spillman-paging.pid"
            if os.access("/var/run", os.W_OK)
            else "/tmp/spillman-paging.pid"
        )

    elif units:
        process_name = "units"
        process_description = "Unit Status Monitoring"
        pidfile = (
            "/var/run/spillman-units.pid"
            if os.access("/var/run", os.W_OK)
            else "/tmp/spillman-units.pid"
        )

    elif misc:
        process_name = "misc"
        process_description = "Miscellaneous Functions"
        pidfile = (
            "/var/run/spillman-misc.pid"
            if os.access("/var/run", os.W_OK)
            else "/tmp/spillman-misc.pid"
        )

    elif cleanup:
        process_name = "cleanup"
        process_description = "Cleanup Operations"
        s.cleanup.main()
        sys.exit(0)

    elif check_config:
        print("Just making sure everything works!")
        syslog.info("Just making sure everything works!")
        sys.exit(0)

    s.checkPidFile(pidfile)

    if os.path.isfile(pidfile):
        syslog.info(f"{process_description} Process Already Running")
        sys.exit(0)

    open(pidfile, "w").write(pid)
    syslog.info(f"Starting {process_description}")

    if paging:
        while True:
            try:
                agency_list = s.AgencyProcessor.fetch_active_agencies()
                s.AgencyProcessor.process_agency(agency_list)
                if test:
                    break
            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                sys.exit(0)

    elif units:
        while True:
            try:
                db_ro = connect_read()
                cursor = db_ro.cursor()
                cursor.execute("select agency_id from agency where active = 1")
                agencies = list(cursor.fetchall())
                cursor.close()
                db_ro.close()

                for agency in agencies:
                    agency_id = agency[0]
                    syslog.debug(f"Processing {agency_id} Units")
                    current_agency = s.status(agency_id)
                    current_agency.unit()

                time.sleep(1)

            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                sys.exit(0)

        s.cleanup.main()

    elif misc:
        while True:
            try:
                s.wx.main()

                if test:
                    break

                time.sleep(300)

            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                sys.exit(0)

    os.unlink(pidfile)


if __name__ == "__main__":
    main()
