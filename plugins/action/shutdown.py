# Copyright (c) 2020, Amin Vakil <info@aminvakil.com>
# Copyright (c) 2016-2018, Matt Davis <mdavis@ansible.com>
# Copyright (c) 2018, Sam Doran <sdoran@redhat.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import typing as t

from ansible.errors import AnsibleConnectionFailure, AnsibleError
from ansible.module_utils.common.collections import is_string
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

if t.TYPE_CHECKING:

    class Distribution(t.TypedDict):
        name: str
        version: str
        family: str


display = Display()


class TimedOutException(Exception):
    pass


class ActionModule(ActionBase):
    TRANSFERS_FILES = False
    _VALID_ARGS = frozenset(("msg", "delay", "search_paths"))

    DEFAULT_CONNECT_TIMEOUT = None
    DEFAULT_PRE_SHUTDOWN_DELAY = 0
    DEFAULT_SHUTDOWN_MESSAGE = "Shut down initiated by Ansible"
    DEFAULT_SHUTDOWN_COMMAND = "shutdown"
    DEFAULT_SHUTDOWN_COMMAND_ARGS = '-h {delay_min} "{message}"'
    DEFAULT_SUDOABLE = True

    SHUTDOWN_COMMANDS = {
        "alpine": "poweroff",
        "vmkernel": "halt",
    }

    SHUTDOWN_COMMAND_ARGS = {
        "alpine": "",
        "void": '-h +{delay_min} "{message}"',
        "freebsd": '-p +{delay_sec}s "{message}"',
        "linux": DEFAULT_SHUTDOWN_COMMAND_ARGS,
        "macosx": '-h +{delay_min} "{message}"',
        "openbsd": '-h +{delay_min} "{message}"',
        "solaris": '-y -g {delay_sec} -i 5 "{message}"',
        "sunos": '-y -g {delay_sec} -i 5 "{message}"',
        "vmkernel": "-d {delay_sec}",
        "aix": "-Fh",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def delay(self):
        return self._check_delay("delay", self.DEFAULT_PRE_SHUTDOWN_DELAY)

    def _check_delay(self, key: str, default: int) -> int:
        """Ensure that the value is positive or zero"""
        value = int(self._task.args.get(key, default))
        if value < 0:
            value = 0
        return value

    @staticmethod
    def _get_value_from_facts(data: dict[str, str], distribution: Distribution, default_value: str) -> str:
        """Get dist+version specific args first, then distribution, then family, lastly use default"""
        return data.get(
            distribution["name"] + distribution["version"],
            data.get(distribution["name"], data.get(distribution["family"], default_value)),
        )

    def get_distribution(self, task_vars: dict[str, t.Any]) -> Distribution:
        # FIXME: only execute the module if we don't already have the facts we need
        display.debug(f"{self._task.action}: running setup module to get distribution")
        module_output = self._execute_module(
            task_vars=task_vars, module_name="ansible.legacy.setup", module_args={"gather_subset": "min"}
        )
        try:
            if module_output.get("failed", False):
                raise AnsibleError(
                    f"Failed to determine system distribution. {to_native(module_output['module_stdout'])}, {to_native(module_output['module_stderr'])}"
                )
            distribution: Distribution = {
                "name": module_output["ansible_facts"]["ansible_distribution"].lower(),
                "version": to_text(module_output["ansible_facts"]["ansible_distribution_version"].split(".")[0]),
                "family": to_text(module_output["ansible_facts"]["ansible_os_family"].lower()),
            }
            display.debug(f"{self._task.action}: distribution: {distribution}")
            return distribution
        except KeyError as ke:
            raise AnsibleError(f'Failed to get distribution information. Missing "{ke.args[0]}" in output.') from ke

    def get_shutdown_command(self, task_vars: dict[str, t.Any], distribution: Distribution) -> str:
        def find_command(command: str, find_search_paths: list[str]) -> list[str]:
            display.debug(
                f'{self._task.action}: running find module looking in {find_search_paths} to get path for "{command}"'
            )
            find_result = self._execute_module(
                task_vars=task_vars,
                # prevent collection search by calling with ansible.legacy (still allows library/ override of find)
                module_name="ansible.legacy.find",
                module_args={"paths": find_search_paths, "patterns": [command], "file_type": "any"},
            )
            return [x["path"] for x in find_result["files"]]

        shutdown_bin = self._get_value_from_facts(self.SHUTDOWN_COMMANDS, distribution, self.DEFAULT_SHUTDOWN_COMMAND)
        default_search_paths = ["/sbin", "/usr/sbin", "/usr/local/sbin"]
        search_paths = self._task.args.get("search_paths", default_search_paths)

        # FIXME: switch all this to user arg spec validation methods when they are available
        # Convert bare strings to a list
        if is_string(search_paths):
            search_paths = [search_paths]

        try:
            incorrect_type = any(not is_string(x) for x in search_paths)
            if not isinstance(search_paths, list) or incorrect_type:
                raise TypeError
        except TypeError as e:
            # Error if we didn't get a list
            err_msg = f"'search_paths' must be a string or flat list of strings, got {search_paths}"
            raise AnsibleError(err_msg) from e

        full_path = find_command(shutdown_bin, search_paths)  # find the path to the shutdown command
        if not full_path:  # if we could not find the shutdown command
            # tell the user we will try with systemd
            display.vvv(
                f'Unable to find command "{shutdown_bin}" in search paths: {search_paths}, will attempt a shutdown using systemd directly.'
            )
            systemctl_search_paths = ["/bin", "/usr/bin"]
            full_path = find_command("systemctl", systemctl_search_paths)  # find the path to the systemctl command
            if not full_path:  # if we couldn't find systemctl
                raise AnsibleError(
                    f'Could not find command "{shutdown_bin}" in search paths: {search_paths} or systemctl'
                    f" command in search paths: {systemctl_search_paths}, unable to shutdown."
                )  # we give up here
            else:
                return f"{full_path[0]} poweroff"  # done, since we cannot use args with systemd shutdown

        # systemd case taken care of, here we add args to the command
        args = self._get_value_from_facts(self.SHUTDOWN_COMMAND_ARGS, distribution, self.DEFAULT_SHUTDOWN_COMMAND_ARGS)
        # Convert seconds to minutes. If less that 60, set it to 0.
        delay_sec = self.delay
        shutdown_message = self._task.args.get("msg", self.DEFAULT_SHUTDOWN_MESSAGE)

        af = args.format(delay_sec=delay_sec, delay_min=delay_sec // 60, message=shutdown_message)
        return f"{full_path[0]} {af}"

    def perform_shutdown(self, task_vars, distribution) -> dict[str, t.Any]:
        result: dict[str, t.Any] = {}
        shutdown_result = {}
        shutdown_command_exec = self.get_shutdown_command(task_vars, distribution)

        self.cleanup(force=True)
        try:
            display.vvv(f"{self._task.action}: shutting down server...")
            display.debug(f"{self._task.action}: shutting down server with command '{shutdown_command_exec}'")
            if self._play_context.check_mode:
                shutdown_result["rc"] = 0
            else:
                shutdown_result = self._low_level_execute_command(shutdown_command_exec, sudoable=self.DEFAULT_SUDOABLE)
        except AnsibleConnectionFailure as e:
            # If the connection is closed too quickly due to the system being shutdown, carry on
            display.debug(f"{self._task.action}: AnsibleConnectionFailure caught and handled: {e}")
            shutdown_result["rc"] = 0

        if shutdown_result["rc"] != 0:
            result["failed"] = True
            result["shutdown"] = False
            result["msg"] = (
                f"Shutdown command failed. Error was {to_native(shutdown_result['stdout'])}, {to_native(shutdown_result['stderr'])}"
            )
            return result

        result["failed"] = False
        result["shutdown_command"] = shutdown_command_exec
        return result

    def run(self, tmp: str | None = None, task_vars: dict[str, t.Any] | None = None) -> dict[str, t.Any]:
        self._supports_check_mode = True
        self._supports_async = True

        # If running with local connection, fail so we don't shutdown ourself
        if self._connection.transport == "local" and (not self._play_context.check_mode):
            msg = f"Running {self._task.action} with local connection would shutdown the control node."
            return {"changed": False, "elapsed": 0, "shutdown": False, "failed": True, "msg": msg}

        if task_vars is None:
            task_vars = {}

        result = super().run(tmp, task_vars)

        if result.get("skipped", False) or result.get("failed", False):
            return result

        distribution = self.get_distribution(task_vars)

        # Initiate shutdown
        shutdown_result = self.perform_shutdown(task_vars, distribution)

        if shutdown_result["failed"]:
            result = shutdown_result
            return result

        result["shutdown"] = True
        result["changed"] = True
        result["shutdown_command"] = shutdown_result["shutdown_command"]

        return result
