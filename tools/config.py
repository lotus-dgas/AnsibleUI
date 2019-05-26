#!/usr/bin/env python

import os

#### Ansible
ansible_remote_user = "root"
ansible_result_redis_db = 10
# ansible_callback_redis_addr = "10.20.88.215"
# ansible_callback_redis_port = 6379


#### Redis  ~~~ ansible 结果临时存放+Celery
REDIS_ADDR = "10.20.88.215"
REDIS_PORT = 6479
REDIS_PD = '310c8cabcdefghf2d8abcdefd44496ac80'

#### Celery
BROKER = "redis://:%s@10.20.88.215:6479/3" % REDIS_PD
BACKEND = "redis://:%s@10.20.88.215:6479/4" % REDIS_PD

##### MYSQL     
MYSQL_HOST = '10.20.88.215'
MYSQL_PORT = 23309
MYSQL_USER = 'root'
MYSQL_PASS = 'newpass'
