
import os

title = "纳兰秋水"


#### Ansible
ansible_remote_user = "root"
ansible_result_redis_db = 10
# ansible_callback_redis_addr = "10.20.88.215"
# ansible_callback_redis_port = 6379


#### Redis  ~~~ ansible 结果临时存放+Celery
REDIS_ADDR = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PD = ''

#### Celery
BROKER = "redis://:%s@127.0.0.1:6379/3" % REDIS_PD
BACKEND = "redis://:%s@127.0.0.1:6379/4" % REDIS_PD

##### MYSQL   
USE_MYSQL = False  # False; 忽略
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASS = 'newpass'

web_debug = True

note_base_dirt = 'notes'
inventory = 'inventory'
