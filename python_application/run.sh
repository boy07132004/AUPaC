#!/bin/bash
printenv > /etc/environment && chmod 755 /code/csv_dialy_cron && crontab /code/csv_dialy_cron && cron start
python3 /code/esp_mesh_to_sql.py & uwsgi --ini /code/uwsgi.ini
