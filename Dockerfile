FROM centos:7

ENV LANG en_US.utf8
ADD . /data

WORKDIR /data/

RUN set -ex \
    && echo -e 'export LANG="zh_CN.UTF-8"\nexport LC_ALL="zh_CN.UTF-8"' > /etc/locale.confsource /etc/locale.conf \
    && yum -y install epel-release  \
    && yum -y install gcc-c++ nc python3-devel mysql-devel \
    && pip3 install --find-links files/ -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 10089
COPY dockerRun.sh .
CMD ["./dockerRun.sh"]

# docker build -t ansible_ui .