# Copyright (c) 2020, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import time

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail, AnsibleConnectionFailure
from ansible.utils.vars import merge_hash
from ansible.utils.display import Display

display = Display()


class ActionModule(ActionBase):
    # Keep internal params away from user interactions
    _VALID_ARGS = frozenset(("path", "state", "table", "noflush", "counters", "modprobe", "ip_version", "wait"))
    DEFAULT_SUDOABLE = True

    @staticmethod
    def msg_error__async_and_poll_not_zero(task_poll, task_async, max_timeout):
        return (
            "This module doesn't support async>0 and poll>0 when its 'state' param "
            "is set to 'restored'. To enable its rollback feature (that needs the "
            "module to run asynchronously on the remote), please set task attribute "
            f"'poll' (={task_poll}) to 0, and 'async' (={task_async}) to a value >2 and not greater than "
            f"'ansible_timeout' (={max_timeout}) (recommended)."
        )

    @staticmethod
    def msg_warning__no_async_is_no_rollback(task_poll, task_async, max_timeout):
        return (
            "Attempts to restore iptables state without rollback in case of mistake "
            "may lead the ansible controller to loose access to the hosts and never "
            "regain it before fixing firewall rules through a serial console, or any "
            f"other way except SSH. Please set task attribute 'poll' (={task_poll}) to 0, and "
            f"'async' (={task_async}) to a value >2 and not greater than 'ansible_timeout' (={max_timeout}) "
            "(recommended)."
        )

    @staticmethod
    def msg_warning__async_greater_than_timeout(task_poll, task_async, max_timeout):
        return (
            "You attempt to restore iptables state with rollback in case of mistake, "
            "but with settings that will lead this rollback to happen AFTER that the "
            "controller will reach its own timeout. Please set task attribute 'poll' "
            f"(={task_poll}) to 0, and 'async' (={task_async}) to a value >2 and not greater than "
            f"'ansible_timeout' (={max_timeout}) (recommended)."
        )

    def _async_result(self, async_status_args, task_vars, timeout):
        """
        Retrieve results of the asynchronous task, and display them in place of
        the async wrapper results (those with the ansible_job_id key).
        """
        async_status = self._task.copy()
        async_status.args = async_status_args
        async_status.action = "ansible.builtin.async_status"
        async_status.async_val = 0
        async_action = self._shared_loader_obj.action_loader.get(
            async_status.action,
            task=async_status,
            connection=self._connection,
            play_context=self._play_context,
            loader=self._loader,
            templar=self._templar,
            shared_loader_obj=self._shared_loader_obj,
        )

        if async_status.args["mode"] == "cleanup":
            return async_action.run(task_vars=task_vars)

        # At least one iteration is required, even if timeout is 0.
        for dummy in range(max(1, timeout)):
            async_result = async_action.run(task_vars=task_vars)
            if async_result.get("finished", 0) == 1:
                break
            time.sleep(min(1, timeout))

        return async_result

    def run(self, tmp=None, task_vars=None):
        self._supports_check_mode = True
        self._supports_async = True

        result = super().run(tmp, task_vars)
        del tmp  # tmp no longer has any effect

        if not result.get("skipped"):
            # FUTURE: better to let _execute_module calculate this internally?
            wrap_async = self._task.async_val and not self._connection.has_native_async

            # Set short names for values we'll have to compare or reuse
            task_poll = self._task.poll
            task_async = self._task.async_val
            check_mode = self._play_context.check_mode
            max_timeout = self._connection._play_context.timeout
            module_args = self._task.args

            async_status_args = {}
            starter_cmd = None
            confirm_cmd = None

            if module_args.get("state", None) == "restored":
                if not wrap_async:
                    if not check_mode:
                        display.warning(self.msg_error__async_and_poll_not_zero(task_poll, task_async, max_timeout))
                elif task_poll:
                    raise AnsibleActionFail(
                        self.msg_warning__no_async_is_no_rollback(task_poll, task_async, max_timeout)
                    )
                else:
                    if task_async > max_timeout and not check_mode:
                        display.warning(
                            self.msg_warning__async_greater_than_timeout(task_poll, task_async, max_timeout)
                        )

                    # inject the async directory based on the shell option into the
                    # module args
                    async_dir = self.get_shell_option("async_dir", default="~/.ansible_async")

                    # Bind the loop max duration to consistent values on both
                    # remote and local sides (if not the same, make the loop
                    # longer on the controller); and set a backup file path.
                    module_args["_timeout"] = task_async
                    module_args["_back"] = f"{async_dir}/iptables.state"
                    async_status_args = dict(mode="status")
                    confirm_cmd = f"rm -f {module_args['_back']}"
                    starter_cmd = f"touch {module_args['_back']}.starter"
                    remaining_time = max(task_async, max_timeout)

            # do work!
            result = merge_hash(
                result, self._execute_module(module_args=module_args, task_vars=task_vars, wrap_async=wrap_async)
            )

            # Then the 3-steps "go ahead or rollback":
            # 1. Catch early errors of the module (in asynchronous task) if any.
            #    Touch a file on the target to signal the module to process now.
            # 2. Reset connection to ensure a persistent one will not be reused.
            # 3. Confirm the restored state by removing the backup on the remote.
            #    Retrieve the results of the asynchronous task to return them.
            if "_back" in module_args:
                async_status_args["jid"] = result.get("ansible_job_id", None)
                if async_status_args["jid"] is None:
                    raise AnsibleActionFail("Unable to get 'ansible_job_id'.")

                # Catch early errors due to missing mandatory option, bad
                # option type/value, missing required system command, etc.
                result = merge_hash(result, self._async_result(async_status_args, task_vars, 0))

                # The module is aware to not process the main iptables-restore
                # command before finding (and deleting) the 'starter' cookie on
                # the host, so the previous query will not reach ssh timeout.
                dummy = self._low_level_execute_command(starter_cmd, sudoable=self.DEFAULT_SUDOABLE)

                # As the main command is not yet executed on the target, here
                # 'finished' means 'failed before main command be executed'.
                if not result["finished"]:
                    try:
                        self._connection.reset()
                    except AttributeError:
                        pass

                    for dummy in range(max_timeout):
                        time.sleep(1)
                        remaining_time -= 1
                        # - AnsibleConnectionFailure covers rejected requests (i.e.
                        #   by rules with '--jump REJECT')
                        # - ansible_timeout is able to cover dropped requests (due
                        #   to a rule or policy DROP) if not lower than async_val.
                        try:
                            dummy = self._low_level_execute_command(confirm_cmd, sudoable=self.DEFAULT_SUDOABLE)
                            break
                        except AnsibleConnectionFailure:
                            continue

                    result = merge_hash(result, self._async_result(async_status_args, task_vars, remaining_time))

                # Cleanup async related stuff and internal params
                for key in ("ansible_job_id", "results_file", "started", "finished"):
                    if result.get(key):
                        del result[key]

                if result.get("invocation", {}).get("module_args"):
                    for key in ("_back", "_timeout", "_async_dir", "jid"):
                        if result["invocation"]["module_args"].get(key):
                            del result["invocation"]["module_args"][key]

                async_status_args["mode"] = "cleanup"
                dummy = self._async_result(async_status_args, task_vars, 0)

        if not wrap_async:
            # remove a temporary path we created
            self._remove_tmp_path(self._connection._shell.tmpdir)

        return result
