#!/bin/bash
cd /app
rm -fR /tmp/spillman*
mkdir logs 
python -u app.py --misc &
python -u app.py --paging