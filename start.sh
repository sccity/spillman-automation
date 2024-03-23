#!/bin/bash
cd /app
rm -fR /tmp/spillman*
mkdir logs
python -u app.py --paging & 
python -u app.py --misc