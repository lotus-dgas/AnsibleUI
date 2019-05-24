#!/bin/bash


export PYTHONOPTIMIZE=1
mkdir /root/.ssh
cp /data/files/id_rsa /root/.ssh/

# 开一个celery 
celery multi start 1 -A myCelery -l info -c4 --pidfile=/tmp/celery_%n.pid -f logs/celery.log

/usr/local/python3/bin/python3 manage.py runserver 0.0.0.0:10089
