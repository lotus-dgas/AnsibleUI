
#FROM py3:latest
FROM python

ADD . /data
#COPY dockerRun.sh /data/

WORKDIR /data/

RUN pip3 install --find-links files/ -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 10089
CMD ["./dockerRun.sh"]

# docker build -t ansible_ui .

