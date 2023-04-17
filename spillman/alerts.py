# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      ALERTS.PY
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
import traceback, uuid
from .database import connect, connect_read
from .settings import version_data
from .page import send_page
from .log import setup_logger

err = setup_logger("alerts", "alerts")


class alerts:
    def __init__(self, agency, a911_id):
        self.agency = agency.upper()
        self.a911_id = a911_id
        self.version = version_data["version"]

    def incidents(self):
        try:
            try:
                db_ro = connect_read()
                cursor = db_ro.cursor()
                cursor.execute(
                    f"select i.*, c.comment from incidents i left join comments c on i.callid = c.callid where i.alert_sent = 0 and i.unit is not null and i.agency = '{self.agency}'"
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

            else:
                try:
                    results = cursor.fetchall()
                    cursor.close()
                    db_ro.close()
                    incidents_list = [row for row in results if row[5] is not None]

                    for row in incidents_list:
                        self.send_incident(
                            row[1],
                            row[3],
                            row[5],
                            row[6],
                            row[7],
                            row[8],
                            row[9],
                            row[10],
                            row[11],
                            row[13],
                        )

                except:
                    cursor.close()
                    db_ro.close()
                    err.error(traceback.format_exc())
                    return

        except:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

    def comments(self):
        try:
            try:
                db_ro = connect_read()
                cursor = db_ro.cursor()
                cursor.execute(
                    f"select c.callid, c.comment from comments c left join incidents i on (c.callid = i.callid and c.agency = i.agency) where c.processed = 0 and i.alert_sent = 1 and c.agency = '{self.agency}' and i.uuid is not null and i.unit is not null"
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

            else:
                try:
                    results = cursor.fetchall()
                    cursor.close()
                    db_ro.close()

                    for row in results:
                        self.send_comment(row[0], row[1])

                except:
                    cursor.close()
                    db_ro.close()
                    err.error(traceback.format_exc())
                    return

        except:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

    def send_incident(
        self, callid, nature, unit, city, zone, address, gps_x, gps_y, date, comment
    ):
        if unit is None:
            return

        elif unit == "":
            return

        elif unit == " ":
            return

        elif address is None:
            return

        elif nature is None:
            return

        elif comment is None:
            comment = (
                "CAD COMMENTS PENDING<CRLF><CRLF>"
                + "Report an Issue:<CRLF>"
                + "https://help.scifr.net/index.php?a=add&catid=2&custom1="
                + self.agency
                + "&custom2="
                + callid
                + "<CRLF><CRLF>Spillman Automation: v"
                + self.version
                + "<CRLF>Copyright Santa Clara City (UT)<CRLF>All Rights Reserved"
            )

        else:
            comment = comment

        page = f"""CALLID: {callid} CALL: {nature} GPS: {gps_y}, {gps_x} PLACE: {address} CITY: {city} ZONE: {zone} UNIT: {unit} DATE: {date} COMMENT:{comment}"""
        page.replace("'", "")
        page.replace('"', '')

        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(f"select * from page where callid = '{callid}' and agency = '{self.agency}'")

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        if cursor.rowcount == 0:
            cursor.close()
            db_ro.close()
            
            unique_id = uuid.uuid1()
            
            try:
                db = connect()
                cursor = db.cursor()
                callid = callid.replace('"', "")
                callid = callid.replace("'", "")
                page = page.replace('"', "")
                page = page.replace("'", "")
                sql = f"insert into page (uuid, agency, callid, data) values ('{unique_id}', '{self.agency}', '{callid}', '{page}')"
                cursor.execute(sql)
                db.commit()
                cursor.close()
                db.close()
            except:
                cursor.close()
                db.close()
                err.error(traceback.format_exc())
                return 
              
            return_code = send_page(page, self.a911_id)

        else:
            results = cursor.fetchone()
            cursor.close()
            db_page = results[3]
            
            if page == db_page:
                return_code = 0
                err.info("Page data identical, not repaging")
            else:
                try:
                    db = connect()
                    cursor = db.cursor()
                    cursor.execute(f"update page set data = '{page}' where callid = '{callid}' and agency = '{self.agency}'")
                    db.commit()
                    cursor.close()
                    db.close()
                except:
                    cursor.close()
                    db.close()
                    err.error(traceback.format_exc())
                    return 
                  
                return_code = send_page(page, self.a911_id)

        if return_code == 0:
            try:    
                db = connect()
                cursor = db.cursor()
                cursor.execute(f"update incidents set alert_sent = 1 where callid = '{callid}' and agency = '{self.agency}'")
                db.commit()
                cursor.close()
                db.close()

                if comment is not None:
                    try:
                        db = connect()
                        cursor = db.cursor()
                        cursor.execute(
                            f"update comments set processed = 1 where callid = '{callid}' and agency = '{self.agency}'"
                        )
                        db.commit()
                        cursor.close()
                        db.close()
                
                    except:
                        cursor.close()
                        db.close()
                        err.error(traceback.format_exc())
                        return

            except Exception as e:
                cursor.close()
                db.close()
                err.error(traceback.format_exc())
                return

    def send_comment(self, callid, comment):
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(
                f"select * from incidents where callid = '{callid}' and agency = '{self.agency}' and unit is not null"
            )

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        if cursor.rowcount == 0:
            cursor.close()
            db_ro.close()
            return

        else:
            results = cursor.fetchone()
            cursor.close()
            db_unit = repr(results[5])
            db_nature = repr(results[3])
            gps_y = repr(results[10])
            gps_x = repr(results[9])
            address = repr(results[8])
            city = repr(results[6])
            zone = repr(results[7])
            date = results[11]

        unit_list = db_unit.replace("'", "")

        if (
            (unit_list is None)
            or (unit_list == "")
            or (db_unit is None)
            or (unit_list == "unit_list")
        ):
            try:
                db = connect()
                cursor = db.cursor()
                cursor.execute(
                    f"update comments set processed = 1 where callid = '{callid}' and agency = '{self.agency}'"
                )
                db.commit()
                cursor.close()
                db.close()

            except Exception as e:
                cursor.close()
                db.close()
                err.error(traceback.format_exc())
                return

        nature = db_nature.replace("'", "")

        page = f"""CALLID: {callid} CALL: {nature} GPS: {gps_y}, {gps_x} PLACE: {address} CITY: {city} ZONE: {zone} UNIT: {unit_list} DATE: {date} COMMENT:{comment}"""
        page = page.replace("'", "")
        
        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(f"select * from page where callid = '{callid}' and agency = '{self.agency}'")

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        if cursor.rowcount == 0:
            cursor.close()
            db_ro.close()
            
            unique_id = uuid.uuid1()
            
            try:
                db = connect()
                cursor = db.cursor()
                sql = f"insert into page (uuid, agency, callid, data) values ('{unique_id}', '{self.agency}', '{callid}', '{page}')"
                cursor.execute(sql)
                db.commit()
                cursor.close()
                db.close()
            except:
                cursor.close()
                db.close()
                err.error(traceback.format_exc())
                return 
              
            return_code = send_page(page, self.a911_id)

        else:
            results = cursor.fetchone()
            cursor.close()
            db_page = results[3]
            
            if page == db_page:
                return_code = 0
                err.info("Page data identical, not repaging")
            else:
                try:
                    db = connect()
                    cursor = db.cursor()
                    cursor.execute(f"update page set data = '{page}' where callid = '{callid}' and agency = '{self.agency}'")
                    db.commit()
                    cursor.close()
                    db.close()
                except:
                    cursor.close()
                    db.close()
                    err.error(traceback.format_exc())
                    return 
                  
                return_code = send_page(page, self.a911_id)

        if return_code == 0:
            try:
                db = connect()
                cursor = db.cursor()
                cursor.execute(
                    f"update comments set processed = 1 where callid = '{callid}' and agency = '{self.agency}'"
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
            return

    @staticmethod
    def send(
        agency, callid, nature, unit, city, zone, address, gps_x, gps_y, date, comment
    ):
        if unit is None:
            return

        elif unit == "":
            return

        elif unit == " ":
            return

        elif address is None:
            return

        elif nature is None:
            return

        elif comment is None:
            comment = (
                "CAD COMMENTS PENDING<CRLF><CRLF>"
                + "Report an Issue:<CRLF>"
                + "https://help.scifr.net/index.php?a=add&catid=2&custom1="
                + self.agency
                + "&custom2="
                + callid
                + "<CRLF><CRLF>Spillman Automation: v"
                + self.version
                + "<CRLF>Copyright Santa Clara City (UT)<CRLF>All Rights Reserved"
            )

        else:
            comment = comment
            
        page = f"""CALLID: {callid} CALL: {nature} GPS: {gps_y}, {gps_x} PLACE: {address} CITY: {city} ZONE: {zone} UNIT: {unit} DATE: {date} COMMENT:{comment}"""
        page = page.replace("'", "")

        try:
            db_ro = connect_read()
            cursor = db_ro.cursor()
            cursor.execute(
                f"SELECT active911_id from agency where agency_id = '{agency}'"
            )
            db_response = cursor.fetchone()
            cursor.close()
            db_ro.close()

        except Exception as e:
            cursor.close()
            db_ro.close()
            err.error(traceback.format_exc())
            return

        a911_id = db_response[0]
        
        send_page(page, a911_id)
        return
