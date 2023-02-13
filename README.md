# Spillman Automation [![Codacy Badge](https://app.codacy.com/project/badge/Grade/83e20eb1d6d548199948bb26a47ce936)](https://www.codacy.com/gh/sccity/spillman-automation/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sccity/spillman-automation&amp;utm_campaign=Badge_Grade)

The Spillman Automation program is an intermediary between Spillman and Active911, as well as other automatic functions. This program will not only push calls to Active911, but push CAD comments and refresh comments as they are entered. Furthermore, this program will handle radio log entries for cross staffed units. 


## REQUIREMENTS
*  Spillman server with proper access rights.
*  Spillman API 
*  A MySQL/MariaDB database with proper access rights. Currently, we are using Amazon AWS RDS.
*  Python 3.7+.

This project is still in the early development phase and we will update this document accordingly as required.

## INSTALL
run: pip install -r requirements.txt

Rename example.settings.yaml to settings.yaml and update with your credentials and information.

Install the service scripts.

## SETTINGS
In the settings.yaml file you will notice there are smtp, spillman, spillman API, and database settings. The smtp settings are for error reporting outside of file logging. The spillman settings are for your specific install, specifially needing Spillman Touch.

## USAGE
Will update this section soon!

## LICENSE
Copyright (c) Santa Clara City UT
Developed for Sanata Clara - Ivins Fire & Rescue

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.