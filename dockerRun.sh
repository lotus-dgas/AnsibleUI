#!/bin/bash


export PYTHONOPTIMIZE=1

python3 manage.py makemigrations
python3 manage.py migrate
python3 insert_data.py

celery multi start aui -A myCelery -l info -c4 --pidfile=/tmp/celery_%n.pid -f logs/celery.log
python3 manage.py runserver 0.0.0.0:10089
