# Copyright (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = """
name: oneline
type: stdout
short_description: One-line Ansible screen output
version_added: 13.4.0
description:
  - This is a copy of ansible-core's P(ansible.builtin.oneline#callback) callback plugin, which has been deprecated
    in ansible-core 2.19 and will be removed from ansible-core 2.23.
"""

EXAMPLES = r"""
---
# Enable callback in ansible.cfg:
ansible_config: |-
  [defaults]
  stdout_callback = community.general.oneline
"""

import typing as t

from ansible import constants as C
from ansible.plugins.callback import CallbackBase
from ansible.template import Templar

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from ansible.executor.task_result import CallbackTaskResult
    from ansible.inventory.host import Host
    from ansible.playbook.task import Task

COLOR_ERROR = C.COLOR_ERROR  # type: ignore[attr-defined]
COLOR_CHANGED = C.COLOR_CHANGED  # type: ignore[attr-defined]
COLOR_OK = C.COLOR_OK  # type: ignore[attr-defined]
COLOR_UNREACHABLE = C.COLOR_UNREACHABLE  # type: ignore[attr-defined]
COLOR_SKIP = C.COLOR_SKIP  # type: ignore[attr-defined]


def get_result(result: CallbackTaskResult) -> Mapping[str, t.Any]:
    if not hasattr(result, "result"):
        # ansible-core 2.18 fallback
        return result._result
    return result.result


def get_host(result: CallbackTaskResult) -> Host:
    if not hasattr(result, "host"):
        # ansible-core 2.18 fallback
        return result._host
    return result.host


def get_task(result: CallbackTaskResult) -> Task:
    if not hasattr(result, "task"):
        # ansible-core 2.18 fallback
        return result._task
    return result.task


class CallbackModule(CallbackBase):
    """
    This is the default callback interface, which simply prints messages
    to stdout when new callback events are received.
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "community.general.oneline"

    def _command_generic_msg(self, hostname: str, result: Mapping[str, t.Any], caption: str) -> str:
        stdout = result.get("stdout", "").replace("\n", "\\n").replace("\r", "\\r")
        rc = result.get("rc", -1)
        if "stderr" in result and result["stderr"]:
            stderr = result.get("stderr", "").replace("\n", "\\n").replace("\r", "\\r")
            return f"{hostname} | {caption} | rc={rc} | (stdout) {stdout} (stderr) {stderr}"
        else:
            return f"{hostname} | {caption} | rc={rc} | (stdout) {stdout}"

    def v2_runner_on_failed(self, result: CallbackTaskResult, ignore_errors: bool = False) -> None:
        if "exception" in get_result(result):
            error_text = get_result(result)["exception"]
            if not isinstance(error_text, str):
                error_text = Templar().template(get_result(result)["exception"])  # transform to a string
            if self._display.verbosity < 3:
                # extract just the actual error message from the exception text
                error = error_text.strip().split("\n")[-1]
                msg = f"An exception occurred during task execution. To see the full traceback, use -vvv. The error was: {error}"
            else:
                msg = "An exception occurred during task execution. The full traceback is:\n" + error_text.replace(
                    "\n", ""
                )

            if get_task(result).action in C.MODULE_NO_JSON and "module_stderr" not in get_result(result):
                self._display.display(
                    self._command_generic_msg(get_host(result).get_name(), get_result(result), "FAILED"),
                    color=COLOR_ERROR,
                )
            else:
                self._display.display(msg, color=COLOR_ERROR)

        hostname = get_host(result).get_name()
        msg = self._dump_results(get_result(result), indent=0).replace("\n", "")
        self._display.display(f"{hostname} | FAILED! => {msg}", color=COLOR_ERROR)

    def v2_runner_on_ok(self, result: CallbackTaskResult) -> None:

        if get_result(result).get("changed", False):
            color = COLOR_CHANGED
            state = "CHANGED"
        else:
            color = COLOR_OK
            state = "SUCCESS"

        hostname = get_host(result).get_name()
        if get_task(result).action in C.MODULE_NO_JSON and "ansible_job_id" not in get_result(result):
            self._display.display(self._command_generic_msg(hostname, get_result(result), state), color=color)
        else:
            msg = self._dump_results(get_result(result), indent=0).replace("\n", "")
            self._display.display(f"{hostname} | {state} => {msg}", color=color)

    def v2_runner_on_unreachable(self, result: CallbackTaskResult) -> None:
        hostname = get_host(result).get_name()
        msg = get_result(result).get("msg", "")
        self._display.display(f"{hostname} | UNREACHABLE!: {msg}", color=COLOR_UNREACHABLE)

    def v2_runner_on_skipped(self, result: CallbackTaskResult) -> None:
        hostname = get_host(result).get_name()
        self._display.display(f"{hostname} | SKIPPED", color=COLOR_SKIP)
