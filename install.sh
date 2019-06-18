

PYPATH='/usr/local/PyAnsibleUI/'
PORT=10089
# yum -y install epel-release
# yum -y install gcc-c++ openssl-devel python-pip python-devel make libffi-devel mysql-devel sqlite-devel


if [[ ! -f files/id_rsa ]]; then
    echo -e '\033[32m生成Ansible所需私钥，在files目录下\033[0m'
    ssh-keygen -t rsa -f files/id_rsa -P ''
fi
if [[ ! -d $PYPATH  ]]; then
    echo '安装Python环境'
    echo -e "\033[31m安装Python位置为${PYPATH}\033[0m"
    if [[ ! -f files/Python-3.7.3.tgz ]]; then
        echo "\033[33m============>Python包不存在，正在下载<============\033[0m"
        wget -O files/Python-3.7.3.tgz https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tgz
    fi
    cd files 
    tar zxf Python-3.7.3.tgz 
    cd Python-3.7.3
    ./configure --prefix=${PYPATH} && make && make install
else
    echo -e '\033[35m指定Python环境已安装\033[0m'
fi

echo -e '\033[34m============>安装所需Python模块<============\033[0m'
${PYPATH}bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

echo -e "\033[44m============>执行<============\033[0m\033[36m
export PYTHONOPTIMIZE=1 
${PYPATH}bin/celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
${PYPATH}bin/python3 manage.py runserver 0.0.0.0:${PORT}
\033[33m============>启动程序<============\033[0m"


# export PYTHONOPTIMIZE=1
# echo -e "\033[36m============>启动Celery<============\033[0m"
# ${PYPATH}bin/celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
# ${PYPATH}bin/celery -A myCelery worker -l info
# echo -e '\033[36m============>启动主程序<============\033[0m'
# echo -e "\033[33m程序启动，端口 ${PORT}\033[0m"
# ${PYPATH}/bin/python3 manage.py runserver 0.0.0.0:${PORT}

