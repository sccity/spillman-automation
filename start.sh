#!/bin/bash
cd /app
rm -fR /tmp/spillman*
python -u app.py --misc &
python -u app.py --paging