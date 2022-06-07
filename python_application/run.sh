#!/bin/bash
printenv > /etc/environment && chmod 755 /code/cron_script && crontab /code/cron_script && cron start
python3 /code/esp_mesh_to_sql.py & uwsgi --ini /code/uwsgi.ini
