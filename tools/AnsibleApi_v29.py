
__author__ = '独孤傲世'


import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.inventory.host import Host
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
from ansible.utils.ssh_functions import check_for_controlpersist
from ansible.executor.playbook_executor import PlaybookExecutor
import logging, logging.handlers
import datetime
try:
    from rich import print
except:
    pass
from collections import namedtuple
from collections import defaultdict
import redis

# redis callback 写入 db
from tools.config import REDIS_ADDR, REDIS_PORT,REDIS_PD, ansible_remote_user, ansible_result_redis_db


Options = namedtuple('Options', [
    'listtags', 'listtasks', 'listhosts', 'syntax', 'connection',
    'module_path', 'forks', 'remote_user', 'private_key_file', 'timeout',
    'ssh_common_args', 'ssh_extra_args', 'sftp_extra_args',
    'scp_extra_args', 'become', 'become_method', 'become_user',
    'verbosity', 'check', 'extra_vars', 'playbook_path', 'passwords',
    'diff', 'gathering', 'remote_tmp',
])


def get_default_options():
    options = dict(
        syntax=False,
        timeout=30,
        connection='ssh',
        forks=10,
        remote_user='root',
        private_key_file='files/id_rsa',
        become=None,
        become_method=None,
        become_user=None,
        verbosity=1,
        check=False,
        diff=False,
        start_at_task=None,
        gathering='implicit',
        remote_tmp='/tmp/.ansible'
    )
    return options


class BaseHost(Host):
    def __init__(self, host_data):
        self.host_data = host_data
        hostname = host_data.get('hostname') or host_data.get('ip')
        port = host_data.get('port') or 22
        super().__init__(hostname, port)
        self.__set_required_variables()
        self.__set_extra_variables()

    def __set_required_variables(self):
        print('BaseHost.__set_required_variables')
        host_data = self.host_data
        self.set_variable('ansible_host', host_data['ip'])
        self.set_variable('ansible_port', host_data.get('port', 22))

        if host_data.get('username'):
            self.set_variable('ansible_user', host_data['username'])

        if host_data.get('private_key'):
            self.set_variable('ansible_ssh_private_key_file', host_data['private_key'])
        if host_data.get('password'):
            self.set_variable('ansible_ssh_pass', host_data['password'])

        become = host_data.get("become", False)
        if become:
            self.set_variable("ansible_become", True)
            self.set_variable("ansible_become_method", become.get('method', 'sudo'))
            self.set_variable("ansible_become_user", become.get('user', 'root'))
            self.set_variable("ansible_become_pass", become.get('pass', ''))
        else:
            self.set_variable("ansible_become", False)

    def __set_extra_variables(self):
        for k, v in self.host_data.get('vars', {}).items():
            self.set_variable(k, v)

    def __repr__(self):
        return self.name


# 处理主机与组关系
class BaseInventory(InventoryManager):
    loader_class = DataLoader
    variable_manager_class = VariableManager
    host_manager_class = BaseHost

    def __init__(self, host_list=[], group_list=[], inventory_file=None):
        self.host_list = host_list
        self.group_list = group_list
        self.loader = self.loader_class()
        self.variable_manager = self.variable_manager_class()
        super().__init__(self.loader, inventory_file)

    def get_groups(self):
        return self._inventory.groups

    def get_group(self, name):
        return self._inventory.groups.get(name, None)

    def get_or_create_group(self, name):
        group = self.get_group(name)
        if not group:
            self.add_group(name)
            return self.get_or_create_group(name)
        else:
            return group

    def parse_groups(self):
        for g in self.group_list:
            parent = self.get_or_create_group(g.get("name"))
            children = [self.get_or_create_group(n) for n in g.get('children', [])]
            for child in children:
                parent.add_child_group(child)

    def parse_hosts(self):
        group_all = self.get_or_create_group('all')
        ungrouped = self.get_or_create_group('ungrouped')
        for host_data in self.host_list:
            print('host_data： %s' % host_data)
            host = self.host_manager_class(host_data=host_data)
            self.hosts[host_data.get('hostname') or host_data.get('ip')] = host
            groups_data = host_data.get('groups')
            if groups_data:
                for group_name in groups_data:
                    group = self.get_or_create_group(group_name)
                    group.add_host(host)
            else:
                ungrouped.add_host(host)
            group_all.add_host(host)

    def parse_sources(self, cache=False):
        self.parse_groups()
        self.parse_hosts()

    def get_matched_hosts(self, pattern):
        return self.get_hosts(pattern)


class AnsibleError(Exception):
    pass


class RedisCallBack(CallbackBase):
    def __init__(self, task_id):
        super().__init__()
        self.id = task_id
        self.results = []
        self.r = redis.Redis(host=REDIS_ADDR, port=REDIS_PORT, password=REDIS_PD, db=ansible_result_redis_db)
        self.log = logging.getLogger('AnsibleApiLog')
        self.log.propagate = False
        spath = logging.handlers.RotatingFileHandler("logs/ansible_api.log", "a", 0, 1)
        spath.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.log.addHandler(spath)
        self.log.setLevel(logging.DEBUG)

    def __del__(self):  # 设置生存时间
        # self.log.info("Ansible API Self Redis __del__")
        print('__del__: %s' % self.results)
        # self._write_to_save(json.dumps({"msg": "执行完成"}, ensure_ascii=False))
        # super(ResultCallback, self).__del__()

    def _write_to_save(self, data):
        msg = json.dumps(data, ensure_ascii=False)
        self.log.info(msg)
        self.r.rpush(self.id, msg)
        print('[bold magenta]RedisCallBack [/bold magenta]', self.id, '*'*20, self.r ,data)

    def v2_playbook_on_start(self, playbook, *k, **kw):
        print('v2_playbook_on_start', playbook.__dict__)

    def v2_playbook_on_play_start(self, play):
        # print('v2_playbook_on_play_start: %s' % play.__dict__)
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name
        print("v2_playbook_on_play_start ，开始执行主机: %s" % msg)

    def v2_runner_on_ok(self, result, **kwargs):    #执行成功，
        "处理成功任务，跳过 setup 模块的结果"
        host = result._host
        if "ansible_facts" in result._result.keys():    # 我们忽略 setup 操作的结果
            print("[blue underline]SetUp 操作，不Save结果")
        else:
            self._write_to_save({
                "host": host.name,
                "result": result._result,
                "task": result.task_name,
                "status": "success"
            })

    def v2_runner_on_failed(self, result, ignore_errors=False, *k, **kwargs):    # 执行失败
        """处理执行失败的任务，有些任务失败会被忽略，所有有两种状态"""
        self.log.error("%s - %s - %s " % (result, k, kwargs))
        host = result._host
        if ignore_errors:
            status = "ignoring"
        else:
            status = 'failed'
        self._write_to_save({
                "host": host.name, "result": result._result,
                "task": result.task_name, "status": status
            })

    def v2_runner_on_skipped(self, result, *args, **kwargs):    # 任务跳过
        """处理跳过的任务"""
        self.log.info("%s - %s" % ('v2_runner_on_skipped', result))
        self._write_to_save({
                "host": result._host.get_name(), "result": result._result,
                "task": result.task_name, "status": "skipped"}
            )

    def v2_runner_on_unreachable(self, result, **kwargs):   ##  主机不可达
        """处理主机不可达的任务"""
        self._write_to_save({
                "host": result._host.get_name(), "status": "unreachable",
                "task": result.task_name, "result": {"msg": "UNREACHABLE"}}
            )

    def v2_playbook_on_task_start(self, task, is_conditional):
        print(u"v2_playbook_on_task_start, 开始任务： uuid: %s ---- task_name:%s" % (task._uuid, task.get_name().strip()))

    def v2_runner_on_start(self, host, task, *k, **kw):
        print('[yellow on blue]v2_runner_on_start: ',host, task)

    def v2_playbook_on_stats(self, stats, *k, **kw):
        print('v2_playbook_on_stats: ', stats.__dict__)

    def v2_playbook_on_notify(self, handler, host):
        print('v2_playbook_on_notify: ', handler, host)

    def v2_playbook_on_no_hosts_matched(self, *k, **kw):
        print('v2_playbook_on_no_hosts_matched: ', k, kw)

    def v2_playbook_on_no_hosts_remaining(self, *k, **kw):
        print('v2_playbook_on_no_hosts_remaining: ', k, kw)


class PlayBookTaskQueueManager_V2(TaskQueueManager):

    def __init__(self, inventory, variable_manager, loader, passwords, stdout_callback=None, run_additional_callbacks=True, run_tree=False):
        super().__init__(inventory, variable_manager, loader, passwords, stdout_callback, run_additional_callbacks, run_tree)

        self.forks = context.CLIARGS.get('forks')
        self._stdout_callback = stdout_callback

    def load_callbacks(self):   # 为callback 设置存储id
        pass


# 重新封装 PlaybookExecutor ， 传入 task_id
class MyPlaybookExecutor_V2(PlaybookExecutor):

    def __init__(self, task_id, playbooks, inventory, variable_manager, loader, passwords):
        self._playbooks = playbooks
        self._inventory = inventory
        self._variable_manager = variable_manager
        self._loader = loader
        self.passwords = passwords
        self._unreachable_hosts = dict()

        if context.CLIARGS.get('listhosts') or context.CLIARGS.get('listtasks') or \
                context.CLIARGS.get('listtags') or context.CLIARGS.get('syntax'):
            self._tqm = None
        else:
            self._tqm = PlayBookTaskQueueManager_V2(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=self.passwords,
                stdout_callback=RedisCallBack(task_id)
            )
        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)


class MyTaskQueueManager(TaskQueueManager):
    # def load_callbacks(self):   # 截断callback，只保留自定义
        pass


# 执行 ansible 模块任务
def AnsibleExecApi29(task_id, tasks=[], inventory_data=None):
    options = get_default_options()
    context.CLIARGS = ImmutableDict(options)

    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    results_callback = RedisCallBack(task_id)
    # inventory = InventoryManager(loader=loader, sources='localhost,')
    inventory = BaseInventory(inventory_data)
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    play_source = dict(
            name="Ansible Play",
            hosts='localhost',
            gather_facts='no',
            tasks=tasks,
        )
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
    tqm = None
    try:
        tqm = MyTaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=passwords,
                stdout_callback=results_callback,
            )
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()

        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)


# Ansible 2.9 版本的 vars/manager.py: VariableManager 未有 extra_vars.setter
class VariableManagerVars(VariableManager):

    @property
    def extra_vars(self):
        return self._extra_vars

    @extra_vars.setter
    def extra_vars(self, value):
        self._extra_vars = value.copy()


# 执行 Ansible Playbook
def AnsiblePlaybookExecApi29(task_id, playbook_path, inventory_data=[], extra_vars={}):
    # playbook_path = ['playbooks/test_debug.yml']
    passwords = ""
    options = get_default_options()
    inventory = BaseInventory(inventory_data)
    loader = DataLoader()
    variable_manager = VariableManagerVars(loader=loader, inventory=inventory)
    variable_manager.extra_vars = extra_vars
    executor = MyPlaybookExecutor_V2(
        task_id=task_id,
        playbooks=playbook_path,
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        passwords={"conn_pass": passwords},
    )

    context.CLIARGS = ImmutableDict(options)
    executor.run()


if __name__ == '__main__':
    # task_id = "AnsibleExec_%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    # tasks = [
    #     dict(action=dict(module='shell', args='ls'), register='shell_out'),
    #     dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
    # ]
    # AnsibleExecApi29(task_id, tasks)
    data = [
        {'ip': '127.0.0.1', }
    ]
    print(data)
    AnsiblePlaybookExecApi29(
        'AnsiblePlaybook_%s' % datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        ['playbooks/test_debug.yml'],
        data, {}
    )
