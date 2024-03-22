#!/bin/bash
cd /app
exec python -u app.py --paging & 
exec python -u app.py --misc