# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      ACTIVE911.PY
# **********************************************************
# Spillman Digital Paging & Automation
# Copyright Santa Clara City
# Developed for Santa Clara - Ivins Fire & Rescue
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.#
#You may obtain a copy of the License at
#http://www.apache.org/licenses/LICENSE-2.0
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
import sys, os, time, traceback
import spillman as s
from spillman.database import connect_read

syslog = s.setup_logger("system", "system")

pid = str(os.getpid())

if len(sys.argv) == 1:
    args = sys.argv
    syslog.warning("No Option, use --help for options.")
    exit(0)

elif len(sys.argv) == 2:
    args = sys.argv
    arg1 = sys.argv[1]
    arg2 = ""

elif len(sys.argv) == 3:
    args = sys.argv
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]

else:
    syslog.debug("No Option, use --help for options.")
    exit(0)

if len(args) > 1:
    if arg1.lower() == "--paging":
        if os.access("/var/run", os.W_OK) is True:
            pidfile = "/var/run/spillman-paging.pid"

        else:
            pidfile = "/tmp/spillman-paging.pid"

        s.checkPidFile(pidfile)

        if os.path.isfile(pidfile):
            syslog.warning("Paging Process Already Running")
            sys.exit()

        open(pidfile, "w").write(pid)

        syslog.info("Starting Digital Paging")
        while True:
            try:
                agency_list = s.agency.get()
                s.agency.paging(agency_list)

                if arg2.lower() == "--test":
                    break
                  
                time.sleep(1)

            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                exit(0)

        os.unlink(pidfile)

    elif arg1.lower() == "--units":
        if os.access("/var/run", os.W_OK) is True:
            pidfile = "/var/run/spillman-units.pid"

        else:
            pidfile = "/tmp/spillman-units.pid"

        s.checkPidFile(pidfile)

        if os.path.isfile(pidfile):
            syslog.warning("Status Process Already Running")
            sys.exit()

        open(pidfile, "w").write(pid)

        syslog.info("Starting Unit Status Functions")
        while True:
            try:
                db_ro = connect_read()
                cursor = db_ro.cursor()
                cursor.execute(f"select agency_id from agency where active = 1")
                agencies = list(cursor.fetchall())
                cursor.close()
                db_ro.close()

                for agency in agencies:
                    agency_id = agency[0]
                    syslog.debug(f"Processing {agency_id} Units")
                    current_agency = s.status(agency_id)
                    current_agency.unit()

                if arg2.lower() == "--test":
                    break

                time.sleep(1)

            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                exit(0)

        os.unlink(pidfile)

    elif arg1.lower() == "--misc":
        if os.access("/var/run", os.W_OK) is True:
            pidfile = "/var/run/spillman-misc.pid"

        else:
            pidfile = "/tmp/spillman-misc.pid"

        s.checkPidFile(pidfile)

        if os.path.isfile(pidfile):
            syslog.warning("Misc Process Already Running")
            sys.exit()

        open(pidfile, "w").write(pid)

        syslog.info("Executing Misc Functions")
        while True:
            try:
                s.wx.main()

                if arg2.lower() == "--test":
                    break

                time.sleep(300)

            except KeyboardInterrupt:
                syslog.info("\nInterrupted!")
                os.unlink(pidfile)
                exit(0)

        os.unlink(pidfile)

    elif arg1.lower() == "--cleanup":
        s.cleanup.main()

    elif arg1.lower() == "--check-config":
        print("Just making sure everything works!")
        syslog.info("Just making sure everything works!")

    else:
        syslog.warning("No option provided")
else:
    syslog.warning("No option provided")

exit(0)
