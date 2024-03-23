#!/bin/bash
cd /app
rm -fR /tmp/spillman*
python -u app.py --paging & 
python -u app.py --misc