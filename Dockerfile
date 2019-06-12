
FROM centos

ADD . /data
COPY ./files/CentOS7-Base-163.repo /etc/yum.repos.d/CentOS-Base.repo
COPY ./files/yum.conf /etc/

#RUN yum makecache
RUN yum -y install epel-release
RUN yum -y install gcc-c++ openssl-devel python-pip python-devel make libffi-devel mysql-devel sqlite-devel
#RUN yum clean all

ADD ./files/Python-3.7.3.tgz /usr/local/src/
WORKDIR /usr/local/src/Python-3.7.3
RUN ./configure --prefix=/usr/local/PyAnsibleUI && make && make install

WORKDIR /data/
ENV PATH /usr/local/PyAnsibleUI/bin:$PATH

# RUN /usr/local/PyAnsibleUI/bin/pip3 install --find-links=/data/files --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
RUN /usr/local/PyAnsibleUI/bin/pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 数据库建表
# RUN /usr/local/python3/bin/python3 manage.py makemigrations     
# RUN /usr/local/python3/bin/python3 manage.py migrate


EXPOSE 10089

CMD ["/data/dockerRun.sh"]

#docker build -t ansible_ui .
#docker run -it -p 10089:10089 -v `pwd`:/data ansible_ui
#docker run --privileged -it -p 10090:10089 -v `pwd`:/data ansible_ui /usr/sbin/init
