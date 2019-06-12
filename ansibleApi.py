#coding: utf8

import json
import shutil
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.utils.ssh_functions import check_for_controlpersist
import ansible.constants as C
import redis
import datetime
from tools.config import REDIS_ADDR, REDIS_PORT,REDIS_PD, ansible_remote_user, ansible_result_redis_db
import logging, logging.handlers

class ResultCallback(CallbackBase):
    "Ansible Api 和 Ansible Playbook V2 api 调用该CallBack"
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    def __init__(self, id):
        super(ResultCallback, self).__init__()
        self.id = id
        self.results = []
        self.r = redis.Redis(host=REDIS_ADDR, port=REDIS_PORT, password=REDIS_PD, db=ansible_result_redis_db)
        self.log = logging.getLogger('AnsibleApiLog')
        self.log.propagate = False
        spath = logging.handlers.RotatingFileHandler("logs/ansible_api.log", "a", 0, 1)
        spath.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.log.addHandler(spath)
        self.log.setLevel(logging.DEBUG)

    def __del__(self):  # 设置生存时间
        self.log.info("Ansible API Self Redis __del__")
        # self._write_to_save(json.dumps({"msg": "执行完成"}, ensure_ascii=False))
        # super(ResultCallback, self).__del__()
        self.r.expire(self.id, 3600)
    def _write_to_save(self, v):
        # self.log.info("\33[31mSave To API Redis: %s:%s/%s,  %s\33[0m" % (REDIS_ADDR,REDIS_PORT,10, self.id))
        # self.log.debug("Save Data: %s" % v)
        self.r.rpush(self.id, v)
    def playbook_on_start(self):
        self.log.info('开始执行PlayBook')
        print("开始执行PlayBook")
    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name
        print(msg)
    def v2_on_any(self,result, *args, **kwargs):
        print("v2_on_any", json.dumps(result, indent=4))
    def v2_runner_on_ok(self, result, **kwargs):    #执行成功，
        host = result._host
        if "ansible_facts" in result._result.keys():
            print("SetUp 操作，不Save结果")
        else:
            self.log.info("%s: %s, %s" % ("v2_runner_on_ok", host.name, result._result))
            self._write_to_save(json.dumps({"host": host.name, "result": result._result, "task": result.task_name, "status": "success"}))
    def v2_runner_on_failed(self, result, ignore_errors=False, **kwargs):    # 执行失败
        host = result._host
        self.log.error("%s: %s, %s" % ("v2_runner_on_failed", host.name, result._result))
        if ignore_errors:
            status = "ignoring"
        else:
            status = 'failed'
        self._write_to_save(json.dumps({"host": host.name, "result": result._result, "task": result.task_name, "status": status}))
    def v2_runner_on_skipped(self, result, *args, **kwargs):    # 任务跳过
        print("v2_runner_on_skipped", args, kwargs)
        self._write_to_save(json.dumps({"host": result._host.get_name(), "result": result._result, "task": result.task_name, "status": "skipped"}))
    def v2_runner_on_unreachable(self, result, **kwargs):   ##  主机不可达
        self._write_to_save(json.dumps({"host": result._host.get_name(), "status": "unreachable", "task": result.task_name, "result": {"msg": "UNREACHABLE"}}))
    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name
        print("v2_playbook_on_play_start，开始执行主机: %s， %s" % (play, msg))
    def v2_playbook_on_task_start(self, task, is_conditional):
        print(u"v2_playbook_on_task_start, 任务： %s----%s" % (task._uuid, task.get_name().strip()))

# Begin Ansible API ###########
class MyTaskQueueManager(TaskQueueManager):
    def load_callbacks(self):   # 截断callback，只保留自定义
        pass
def AnsibleApi(tid, hosts, tasks, sources, add_vars):
    Options = namedtuple('Options', ['remote_user','connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
    options = Options(remote_user=ansible_remote_user, connection='paramiko', module_path=['/to/mymodules'], forks=10, become=None, become_method=None, become_user=None, check=False, diff=False)
    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    inventory = InventoryManager(loader=loader, sources=sources)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    variable_manager.extra_vars=add_vars
    play_source =  dict(name = "Ansible Play",hosts = hosts,gather_facts = 'no',tasks = tasks)
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    try:
        tqm = MyTaskQueueManager(
                  inventory=inventory,
                  variable_manager=variable_manager,
                  loader=loader,
                  options=options,
                  passwords=passwords,
                  stdout_callback=ResultCallback(tid),
              )
        result = tqm.run(play)
        print(result)
    finally:
        if tqm is not None:
            tqm.cleanup()
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
# End Ansible API ###########
# Begin Ansible Playbook API ##################
class PalyBookTaskQueueManager(TaskQueueManager):   #忘了为啥写这个了，
    def __init__(self, tid, inventory, variable_manager, loader, options, passwords, stdout_callback=None, run_additional_callbacks=True, run_tree=False):
        super(PalyBookTaskQueueManager, self).__init__(inventory, variable_manager, loader, options, passwords, stdout_callback, run_additional_callbacks, run_tree)
        self.id = tid
    def load_callbacks(self):   # 为callback 设置存储id
        super(PalyBookTaskQueueManager, self).load_callbacks()
        for c in self._callback_plugins:
            if hasattr(c, "_reload_id"):
                c._reload_id(self.id)
class MyPlaybookExecutor(PlaybookExecutor):     #为了艾迪
    def __init__(self, tid, playbooks, inventory, variable_manager, loader, options, passwords):
        self._playbooks = playbooks
        self._inventory = inventory
        self._variable_manager = variable_manager
        self._loader = loader
        self._options = options
        self.passwords = passwords
        self._unreachable_hosts = dict()
        if options.listhosts or options.listtasks or options.listtags or options.syntax:
            self._tqm = None
        else:
            self._tqm = PalyBookTaskQueueManager(
                    tid, inventory=inventory,
                    variable_manager=variable_manager,
                    loader=loader,
                    options=options,
                    passwords=self.passwords,
                )
        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)
        self.id = tid
def AnsiblePlaybookApi(tid, playbooks, sources):
    Options = namedtuple('Options', [
        'remote_user',
        'connection',
        'module_path',
        'forks',
        'become',
        'become_method',
        'become_user',
        'check',
        'diff',
        'listhosts',
        'listtasks',
        'listtags',
        'syntax',
        ])
    options = Options(
        remote_user=ansible_remote_user,
        connection='paramiko',
        module_path=['/to/mymodules'],
        forks=10,
        become=None,
        become_method=None,
        become_user=None,
        check=False,
        diff=False,
        listhosts=None,
        listtasks=None,
        listtags=None,
        syntax=None
        )
    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    inventory = InventoryManager(loader=loader, sources=sources)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    pb = MyPlaybookExecutor(tid, playbooks=playbooks,inventory=inventory, variable_manager=variable_manager, loader=loader, options=options,passwords=passwords)
    result = pb.run()
    print(result)
# End Ansible Playbook API ##################

#Begin Ansible Playbook V2 API ####################
class PalyBookTaskQueueManager_V2(TaskQueueManager):   #忘了为啥写这个了，
    def __init__(self, inventory, variable_manager, loader, options, passwords, stdout_callback=None, run_additional_callbacks=True, run_tree=False):
        super(PalyBookTaskQueueManager_V2, self).__init__(inventory, variable_manager, loader, options, passwords, stdout_callback, run_additional_callbacks, run_tree)
        self._stdout_callback = stdout_callback
    def load_callbacks(self):   # 为callback 设置存储id
        pass

class MyPlaybookExecutor_V2(PlaybookExecutor):  #PlaybookExecutor 本身
    def __init__(self, tid, playbooks, inventory, variable_manager, loader, options, passwords):
        self._playbooks = playbooks
        self._inventory = inventory
        self._variable_manager = variable_manager
        self._loader = loader
        self._options = options
        self.passwords = passwords
        self._unreachable_hosts = dict()
        if options.listhosts or options.listtasks or options.listtags or options.syntax:
            self._tqm = None
        else:
            self._tqm = PalyBookTaskQueueManager_V2(
                    inventory=inventory,
                    variable_manager=variable_manager,
                    loader=loader,
                    options=options,
                    passwords=self.passwords,
                    stdout_callback=ResultCallback(tid)
                )
        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)

def AnsiblePlaybookApi_v2(tid, playbooks, sources, extra_vars={}): # 最终调用
    print('\33[33mansibleApi.py extra_vars:%s\33[0m' % extra_vars)
    Options = namedtuple('Options', [
        'remote_user',
        'connection',
        'module_path',
        'forks',
        'become',
        'become_method',
        'become_user',
        'check',
        'diff',
        'listhosts',
        'listtasks',
        'listtags',
        'syntax',
        ])
    options = Options(
        remote_user=ansible_remote_user,
        connection='paramiko',
        module_path=['/to/mymodules'],
        forks=10,
        become=None,
        become_method=None,
        become_user=None,
        check=False,
        diff=False,
        listhosts=None,
        listtasks=None,
        listtags=None,
        syntax=None
        )
    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    inventory = InventoryManager(loader=loader, sources=sources)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    variable_manager.extra_vars=extra_vars
    pb = MyPlaybookExecutor_V2(tid, playbooks=playbooks,inventory=inventory, variable_manager=variable_manager, loader=loader, options=options,passwords=passwords)
    result = pb.run()
    print(result)
#End  Ansible Playbook V2 API ####################

if __name__ == "__main__":
    sources = "script/etcd_exec.py"

    # tasks = []  #任务列表
    # tasks.append(dict(action=dict(module='shell', args='hostname'), register='shell_out'))
    # vars = {"project": "Lotus"} #额外参数
    # AnsibleApi("AnsibleApi-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), "t", tasks, sources, vars)
    # AnsiblePlaybookApi("AnsiblePlayBookApi-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), ["playbooks/t.yml"], sources)
    AnsiblePlaybookApi_v2("AnsiblePlayBookApi-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), ["playbooks/test_debug.yml"], sources)
