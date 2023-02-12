# **********************************************************
# * CATEGORY  SOFTWARE
# * GROUP     DISPATCH
# * AUTHOR    LANCE HAYNIE <LHAYNIE@SCCITY.ORG>
# * FILE      WX.PY
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
import json, logging, requests, xmltodict, traceback
import uuid
from lxml import etree
from datetime import datetime
from .settings import settings_data
from .database import db, db_ro
from .log import setup_logger

wxlog = setup_logger("wx", "wx")

nwsid = settings_data["global"]["nwsid"]


def main():
    req = requests.get(f"https://alerts.weather.gov/cap/wwaatmget.php?x={nwsid}&y=0")
    xml = req.content

    ns = {"atom": "http://www.w3.org/2005/Atom"}

    try:
        atom = etree.fromstring(xml)

    except:
        wxlog.error(traceback.format_exc())
        return

    for element in atom.xpath("//atom:entry", namespaces=ns):
        title = ""
        text = ""
        published = ""
        try:
            for node in element.iterchildren():
                if node.tag.find("event") > -1:
                    title = node.text

                elif node.tag.find("summary") > -1:
                    text = node.text
                    text = text.replace("...", "")
                    text = text.replace("* WHAT", "<CRLF><CRLF>WHAT: ")
                    text = text.replace("* WHERE", "<CRLF><CRLF>WHERE: ")
                    text = text.replace("* WHEN", "<CRLF><CRLF>WHEN: ")
                    text = text.replace("* IMPACTS", "<CRLF><CRLF>IMPACTS: ")
                    text = text.replace("* Until", "<CRLF><CRLF>UNTIL: ")
                    text = text.replace(" * ", " ")

                elif node.tag.find("published") > -1:
                    published = node.text

                elif node.tag.find("effective") > -1:
                    effective = node.text

                elif node.tag.find("expires") > -1:
                    expires = node.text

                elif node.tag.find("id") > -1:
                    id = node.text
                    id = id.split("SLC.", 1)[1]

        except IndexError:
            return

        try:
            nature = "NWS Alert - " + title
            comment = (
                text
                + "<CRLF><CRLF>"
                + "Effective: "
                + effective
                + "<CRLF>Expires: "
                + expires
                + "\nEOM"
            )
            now = datetime.now()
            sql_date = now.strftime("%Y-%m-%d %H:%M:%S")

        except Exception as e:
            wxlog.error(traceback.format_exc())
            return

    try:
        cursor = db_ro.cursor()
        cursor.execute(
            f"select agency_id, agency_type, active911_id from agency where active = 1 and nws_alerts = 1"
        )
        agencies = list(cursor.fetchall())
        cursor.close()

    except:
        cursor.close()
        wxlog.error(traceback.format_exc())
        return

    for agency in agencies:
        agency_id = agency[0]

        wxlog.debug(agency_id)

        try:
            unique_id = uuid.uuid1()
            sql = f"""
            INSERT INTO
            incidents(
                uuid,
                callid,
                incidentid,
                nature,
                agency,
                unit,
                city,
                zone,
                address,
                gps_x,
                gps_y,
                reported,
                alert_sent)
            values(
                '{unique_id}',
                '{agency_id}{id}',
                '{agency_id}{id}',
                '{nature}',
                '{agency_id}',
                'NWS',
                'County',
                '{agency_id}',
                '{nature}',
                '0',
                '0',
                '{sql_date}',
                0);
            """

            try:
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
                cursor.close()

            except Exception as e:
                cursor.close()
                error = format(str(e))
                if error.find("Duplicate entry") != -1:
                    wxlog.debug(
                        "Incident already exists in alert database for "
                        + id
                        + " reported "
                        + sql_date
                        + "."
                    )
                    return

                else:
                    wxlog.error(traceback.format_exc())
                    return

            unique_id = uuid.uuid1()
            sql = f"""
            INSERT INTO
            comments(
                uuid,
                agency,
                callid,
                comment,
                processed,
                updated)
            values(
                '{unique_id}',
                '{agency_id}',
                '{agency_id}{id}',
                '{comment}',
                1,
                '{sql_date}');
            """

            try:
                cursor = db.cursor()
                cursor.execute(sql)
                db.commit()
                cursor.close()

            except Exception as e:
                cursor.close()
                error = format(str(e))

                if error.find("Duplicate entry") != -1:
                    wxlog.debug(
                        "CAD comment already exists in alert database for "
                        + callid
                        + "."
                    )

                else:
                    wxlog.error(traceback.format_exc())
                    return

        except Exception as e:
            wxlog.error(traceback.format_exc())
            return

    return
