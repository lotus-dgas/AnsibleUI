
import os

title = "纳兰秋水"


#### Ansible
ansible_remote_user = "root"
ansible_result_redis_db = 10
# ansible_callback_redis_addr = "10.20.88.215"
# ansible_callback_redis_port = 6379


#### Redis  ~~~ ansible 结果临时存放+Celery

REDIS_ADDR = "redis" if os.getenv('ENV') == "Docker" else "127.0.0.1" 
REDIS_PORT = 6379
REDIS_PD = ''

#### Celery
task_db = broker_db = 11
result_db = 12
BROKER = "redis://:%s@%s:6379/%s" % (REDIS_PD, REDIS_ADDR, broker_db)
BACKEND = "redis://:%s@%s:6379/%s" % (REDIS_PD, REDIS_ADDR, result_db)

##### MYSQL   

USE_MYSQL = True if os.getenv('ENV') == "Docker" else False  # False; 忽略
MYSQL_HOST = 'mysql' if os.getenv('ENV') == "Docker" else "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASS = 'newpass'

#web_debug = True if os.getenv('ENV') == "Docker" else False
web_debug = True
note_base_dirt = 'notes'
inventory = 'scripts/inventory'
