# AnsibleUI

#### 介绍

AnsibleUI 是基于Django + Ansible + Celery 的Web平台，用以批量处理任务

#### 软件架构

软件架构说明

#### 安装教程

*   可直接使用docker部署启动，
    *   在代码目录下 docker build -t ansible_ui .
    *   docker run -it -p 10089:10089 -v `pwd`:/data ansible_ui
*   手动部署
    *   安装 Python 环境，开发环境版本为 Python 3.6.4
    *   安装相关pagkage `pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
    *   配置相关参数 config/tools.py，包括redis、mysql
    *   为数据库建表，`python3 manage.py makemigrations && python3 manage.py migrate`
    *   在代码目录下启动Celery，`celery -A myCelery worker -l info`，可参看myCelery.py文件尾注释部分
    *   启动主服务，`python3 manage.py runserver 0.0.0.0:10089`。
*   服务启动
    * Celery启动，`celery multi start 1 -A myCelery -l info -c4 --pidfile=tmp/celery_%n.pid -f logs/celery.log`
    * 主程序启动，`uwsgi --socket 127.0.0.1:9801 --module AnsibleUI.wsgi --py-autoreload=1 --daemonize=logs/uwsgi.log`
    * 静态资源及代理，nginx配置
    ```conf
        server {
            listen       10086;
            access_log logs/ansibleui.access.log;
            error_log  logs/ansibleui.error.log;
            location / {
                    include uwsgi_params;
                    uwsgi_pass 127.0.0.1:9801;
            }
            location /static {
                root /data/AnsibleUI/;
            }
            location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$ {
                expires      30d;
            }
        }
    ```

#### 配置项

tools/config.py
    ansible 远程连接用户
    Redis 存放Celery
    MYSLQ 

#### 使用说明

0. 需外部提供MySQl和Redis，参数在tools/config.py内修改
1. xxxx
2. xxxx
3. xxxx

#### UI

![](tmp/images/playbook.png)



![](tmp/images/tasks.png)




![](tmp/images/task_result.png)





```mermaid
graph LR 
	 a[AnsibleUI执行流程]
    style a fill:#ccf,stroke:#f66,stroke-width:2px,stroke-dasharray: 10,5
  
	AnsibleUI(AnsibleUI) 
    Celery[Celery]
    Celery 
    AnsibleApi[AnsibleApi]
    Redis[redis]
    MySQL[MySQL]
    AnsibleUI --> Celery
    Celery -- Broker/Backend --> Redis
    Celery -- 调用 --> AnsibleApi
    AnsibleApi -- 执行结果临时保存--> Redis
    AnsibleUI -- 后端 --> MySQL
    Celery -- 执行完成 --> MySQL
    
   


```