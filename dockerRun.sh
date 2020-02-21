#!/bin/bash


export PYTHONOPTIMIZE=1

echo '检测 redis 是否启动'
while ! nc redis 6379;
do
    echo '等待 redis 启动'
    sleep 2
done

echo '检测 Mysql 是否启动'
while ! nc mysql 3306;
do
    echo '等待 MySQL 启动'
    sleep 2
done

python3 manage.py makemigrations
python3 manage.py migrate
python3 insert_data.py

celery multi start aui -A myCelery -l info -c4 --pidfile=/tmp/celery_%n.pid -f logs/celery.log
python3 manage.py runserver 0.0.0.0:10089
