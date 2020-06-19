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

rm -rf tmp/celery_*.pid

if [[ ! -f files/id_rsa ]]; then
    echo -e '\033[32m生成Ansible所需私钥，在files目录下\033[0m'
    ssh-keygen -t rsa -f files/id_rsa -P ''

fi
echo -e '\033[33m请将如下公钥内容（files/id_rsa.pub）写入远程主机 ~/.ssh/authorized_keys 文件内 \033[0m'
cat files/id_rsa.pub

celery multi start aui -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
python3 manage.py runserver 0.0.0.0:10089
