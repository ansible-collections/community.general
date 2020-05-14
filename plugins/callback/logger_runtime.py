from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    options:
      output_limit:
        description: Number of tasks to display in the summary
        default: 20
        env:
          - name: LOGGER_RUNTIME_OUTPUT_LIMIT
        ini:
          - section: callback_logger_runtime
            key: task_output_limit
      sort_order:
        description: Adjust the sorting output of summary tasks
        choices: ['descending', 'ascending', 'none']
        default: 'descending'
        env:
          - name: LOGGER_RUNTIME_SORT_ORDER
        ini:
          - section: callback_logger_runtime
            key: sort_order
'''

import collections
import time
import logging

from ansible.module_utils.six.moves import reduce
from ansible.plugins.callback import CallbackBase


logging.basicConfig(format='[%(asctime)s] %(process)d %(pathname)s::%(lineno)d - %(message)s ', datefmt='%d-%b-%y %H:%M:%S', filename='/var/log/ansible_runtime.log', level=logging.DEBUG)

# define start time
t0 = tn = time.time()*1000


def timestamp(self):
    if self.current is not None:
        self.stats[self.current]['time'] = int((time.time()*1000) - self.stats[self.current]['time'])

def tasktime():
    global tn
    time_current = time.time()*1000
    time_elapsed = time.time() - tn
    time_total_elapsed = (time.time()*1000) - t0
    tn = time.time()*1000
    return int(time_total_elapsed)


class CallbackModule(CallbackBase):
    """
    This callback module provides per-task timing, ongoing playbook elapsed time
    and ordered list of top 20 longest running tasks at end.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'logger_runtime'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        self.stats = collections.OrderedDict()
        self.current = None

        self.sort_order = None
        self.task_output_limit = None

        super(CallbackModule, self).__init__()

    def set_options(self, task_keys=None, var_options=None, direct=None):

        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.sort_order = self.get_option('sort_order')
        if self.sort_order is not None:
            if self.sort_order == 'ascending':
                self.sort_order = False
            elif self.sort_order == 'descending':
                self.sort_order = True
            elif self.sort_order == 'none':
                self.sort_order = None

        self.task_output_limit = self.get_option('output_limit')
        if self.task_output_limit is not None:
            if self.task_output_limit == 'all':
                self.task_output_limit = None
            else:
                self.task_output_limit = int(self.task_output_limit)

    def _record_task(self, task):
        """
        Logs the start of each task
        """

        timestamp(self)

        # Record the start time of the current task
        self.current = task._uuid
        self.stats[self.current] = {'time': (time.time()*1000), 'name': task.get_name()}
        if self._display.verbosity >= 2:
            self.stats[self.current]['path'] = task.get_path()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._record_task(task)

    def v2_playbook_on_handler_task_start(self, task):
        self._record_task(task)

    def playbook_on_setup(self):
        log = "playbook_on_setup_execution_time " + str(tasktime())
        logging.info(log)

    def playbook_on_stats(self, stats):
        log = "playbook_execution_time " + str(tasktime())
        logging.info(log)


        timestamp(self)
        self.current = None

        results = self.stats.items()
        # Sort the tasks by the specified sort
        if self.sort_order is not None:
            results = sorted(
                self.stats.items(),
                key=lambda x: x[1]['time'],
                reverse=self.sort_order,
            )

        # Display the number of tasks specified or the default of 20
        results = results[:self.task_output_limit]

        # Print the timings
        for uuid, result in results:
            log = str(result['name']) + " " + str(result['time'])
            logging.info(log)

