import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible import context
import ansible.constants as C
from ansible.utils.ssh_functions import check_for_controlpersist
from ansible.executor.playbook_executor import PlaybookExecutor

import logging, logging.handlers
import datetime

class RedisCallBack(CallbackBase):
    def __init__(self, task_id):
        super().__init__()
        self.id = task_id
        self.results = []
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

    def _write_to_save(self, data):
        msg = json.dumps(data, ensure_ascii=False)
        self.log.info(msg)
        print('RedisCallBack ', self.id, '*'*20, data)

    def playbook_on_start(self):
        self.log.info('开始执行PlayBook')
        print("开始执行PlayBook")

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            msg = u"PLAY"
        else:
            msg = u"PLAY [%s]" % name
        print("\33[44mv2_playbook_on_play_start \33[0m，开始执行主机: %s， %s" % (play, msg))

    def v2_on_any(self,result, *args, **kwargs):
        print("\33[44mv2_on_any\33[0m", json.dumps(result, indent=4))

    def v2_runner_on_ok(self, result, **kwargs):    #执行成功，
        "处理成功任务，跳过 setup 模块的结果"
        host = result._host
        if "ansible_facts" in result._result.keys():    # 我们忽略 setup 操作的结果
            print("\33[32mSetUp 操作，不Save结果\33[0m")
        else:
            self._write_to_save({
                "host": host.name,
                "result": result._result,
                "task": result.task_name,
                "status": "success"
            })

    def v2_runner_on_failed(self, result, ignore_errors=False, *k, **kwargs):    # 执行失败
        "处理执行失败的任务，有些任务失败会被忽略，所有有两种状态"
        self.log.error("%s - %s - %s " % (result, k, kwargs))
        host = result._host
        if ignore_errors:
            status = "ignoring"
        else:
            status = 'failed'
        self._write_to_save({
                "host": host.name,"result": result._result,
                "task": result.task_name,"status": status
            })

    def v2_runner_on_skipped(self, result, *args, **kwargs):    # 任务跳过
        "处理跳过的任务"
        self.log.info("%s - %s" % ('v2_runner_on_skipped', result))
        self._write_to_save({
                "host": result._host.get_name(), "result": result._result,
                "task": result.task_name, "status": "skipped"}
            )

    def v2_runner_on_unreachable(self, result, **kwargs):   ##  主机不可达
        "处理主机不可达的任务"
        self._write_to_save({
                "host": result._host.get_name(), "status": "unreachable",
                "task": result.task_name, "result": {"msg": "UNREACHABLE"}}
            )

    def v2_playbook_on_task_start(self, task, is_conditional):
        print(u"v2_playbook_on_task_start, 任务： %s----%s" % (task._uuid, task.get_name().strip()))

    def v2_runner_on_start(self, *k, **kw): pass 

    def v2_playbook_on_stats(self, *k, **kw):
        pass

    def v2_playbook_on_notify(self, handler, host):
        pass

    def v2_playbook_on_no_hosts_matched(self, *k, **kw):
        pass

    def v2_playbook_on_no_hosts_remaining(self, *k, **kw):
        pass

    def v2_playbook_on_start(self, playbook, *k, **kw):
        pass

class MyTaskQueueManager(TaskQueueManager):
    # def load_callbacks(self):   # 截断callback，只保留自定义
        pass

def AnsibleExecApi(task_id, tasks=[]):
    context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules'], forks=10, become=None,
                                    become_method=None, become_user=None, check=False, diff=False)
    loader = DataLoader()
    passwords = dict(vault_pass='secret')
    results_callback = RedisCallBack(task_id)
    inventory = InventoryManager(loader=loader, sources='localhost,')
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    play_source =  dict(
            name = "Ansible Play",
            hosts = 'localhost',
            gather_facts = 'no',
            tasks = tasks, 
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

class PalyBookTaskQueueManager_V2(TaskQueueManager):
    def __init__(self, inventory, variable_manager, loader, passwords, stdout_callback=None, run_additional_callbacks=True, run_tree=False):
        super().__init__(inventory, variable_manager, loader, passwords, stdout_callback, run_additional_callbacks, run_tree)

        self.forks=context.CLIARGS.get('forks')
        self._stdout_callback = stdout_callback
    def load_callbacks(self):   # 为callback 设置存储id
        pass


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
            self._tqm = PalyBookTaskQueueManager_V2(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=self.passwords,
                stdout_callback=RedisCallBack(task_id)
            )
        check_for_controlpersist(C.ANSIBLE_SSH_EXECUTABLE)


def AnsiblePlaybookApi_V2(task_id, playbooks):
    context.CLIARGS = ImmutableDict(connection='local', module_path=['/to/mymodules'], forks=10, become=None,
                                    become_method=None, become_user=None, check=False, diff=False, 
                                    start_at_task=None,syntax=None)

    loader = DataLoader() 
    passwords = dict(vault_pass='secret')
    inventory = InventoryManager(loader=loader, sources='localhost,')
    variable_manager = VariableManager(loader=loader, inventory=inventory)
    pb = MyPlaybookExecutor_V2(task_id, playbooks, inventory, variable_manager, loader, passwords)
    result = pb.run()
    print(result)


if __name__ == "__main__":

    task_id = "AnsibleExecApi-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    tasks = [
                dict(action=dict(module='shell', args='ls'), register='shell_out'),
                dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
            ]
    extra_vars = {}
    AnsibleExecApi(task_id=task_id, tasks=tasks)

    # PB
    task_id = "AnsiblePlayBookApi-%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    AnsiblePlaybookApi_V2(task_id=task_id, playbooks=['playbooks/test_debug.yml'])