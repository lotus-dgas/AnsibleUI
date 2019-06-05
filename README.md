# AnsibleUI

#### 介绍

AnsibleUI 是基于Django + Ansible + Celery 的WEB平台，用以批量处理任务

#### 软件架构

软件架构说明

#### 安装教程

*   可直接使用docker部署启动，
    *   在代码目录下 docker build -t ansible_ui .
    *   docker run -it -p 10089:10089 -v `pwd`:/data ansible_ui
*   手动部署

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

