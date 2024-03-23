#!/bin/bash
cd /app
rm -fR /tmp/spillman*
git pull origin prod
python -u app.py --misc &
python -u app.py --paging