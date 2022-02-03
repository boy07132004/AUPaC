#!/bin/bash
printenv > /etc/environment && chmod 755 /csv_dialy_cron && crontab /csv_dialy_cron && cron start
python3 esp_mesh_to_sql.py & uwsgi --ini /uwsgi.ini
