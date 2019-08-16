if [[ `whoami` != "root" ]]; then
    echo '执行请使用 root' 
    exit
else
    echo 'root 正在进行安装操作'
fi

PWD=`pwd`

echo ''

PYPATH='/usr/local/PyAnsibleUI/'
PORT=10089

if [[ -f  /usr/bin/yum ]]; then
    echo -e '\033[31myum 安装必要插件\033[0m'
    yum -y install epel-release
    yum -y install gcc-c++ wget openssl-devel python-pip python-devel make libffi-devel mysql-devel sqlite-devel
fi

if [[ ! -f files/id_rsa ]]; then
    echo -e '\033[32m生成Ansible所需私钥，在files目录下\033[0m'
    ssh-keygen -t rsa -f files/id_rsa -P ''
fi

if [[ `whereis redis-server | wc -l` != 0 ]]; then
    echo -e '\033[32m检测到存在 redis 命令，请开启实例，修改 tools/config.py 中相关配置\033[0m' 
else
    echo -e '\033[32m未检测到 redis 命令，正在下载安装\033[0m'
    if [[ ! -f files/redis-5.0.5.tar.gz ]]; then
        echo -e '\033[32mdownload redis package\033[0m'
        wget -O files/redis-5.0.5.tar.gz http://download.redis.io/releases/redis-5.0.5.tar.gz
    fi
    cd files
    tar zxf redis-5.0.5.tar.gz
    cd redis-5.0.5
    make
    cp src/redis-server src/redis-cli src/redis-sentinel /usr/bin/
    cd ../../
    echo '启动 Redis '
    cp files/redis.conf /tmp/redis.conf
    /usr/bin/redis-server /tmp/redis.conf
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
    cd ../../
else
    echo -e '\033[35m指定Python环境已安装\033[0m'
fi

echo -e '\033[34m============>安装所需Python模块<============\033[0m'
${PYPATH}bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

echo '创建数据库表结构'
${PYPATH}bin/python3 manage.py makemigrations
${PYPATH}bin/python3 manage.py migrate
${PYPATH}bin/python3 insert_data.py


echo 'export PYTHONOPTIMIZE=1' >> /etc/profile

echo -e "\033[44m============>执行<============\033[0m\033[36m
export PYTHONOPTIMIZE=1 
${PYPATH}bin/celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log
${PYPATH}bin/python3 manage.py runserver 0.0.0.0:${PORT}
\033[33m============>启动程序<============\033[0m"


