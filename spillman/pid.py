# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      PID.PY
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
import os, signal, traceback
from datetime import datetime
import spillman as s

err = s.setup_logger("system", "system")

def checkPidFile(pid_file):
    try:
        stat = os.path.getmtime(pid_file)
    except FileNotFoundError:
        return

    now = datetime.now()
    duration = now - datetime.fromtimestamp(stat)
    duration_in_s = duration.total_seconds()
    diff = divmod(duration_in_s, 60)[0]

    try:
        with open(pid_file, "r") as f:
            current_pid = f.readline().strip()
            current_pid = int(current_pid)
        
        if diff >= 1:
            err.info("Stale process found... Terminating.")
            
            try:
                os.kill(current_pid, signal.SIGTERM)
            except ProcessLookupError:
                pass  # Process already terminated or not found
            except Exception as e:
                err.info(f"Error while terminating process: {e}")
            
            os.unlink(pid_file)
    
    except Exception as e:
        err.info(f"Error while checking PID file: {e}")
