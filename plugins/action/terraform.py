#!/usr/bin/python
# Make coding more python3-ish, this is required for contributions to Ansible
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import socket
import os
from ansible.plugins.action import ActionBase
import multiprocessing
from ansible.utils.display import Display
from ansible import constants as C

display = Display()


def host_andPort():
    """
    Returns the host and a randomly available port for streaming
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as socket_server:
        socket_server.bind((os.environ.get("TERRAFORM_STREAM_HOST"), 0))
        return socket_server.getsockname()


def sample_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))

    try:
        while True:
            message, address = server_socket.recvfrom(1024)
            message = message
            msg = "{}".format(message.decode("utf-8"))
            display.display(msg, color=C.COLOR_OK, stderr=False)
    finally:
        server_socket.close()


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        module_args = self._task.args.copy()
        if "stream_output" not in module_args or module_args["stream_output"] is False:
            self._display.display("Not streaming long running tasks")
            module_return = self._execute_module(
                module_name="terraform",
                module_args=module_args,
                task_vars=task_vars,
                tmp=tmp,
            )
        else:
            try:
                module_args["socket_host"] = host_andPort()[0]
                module_args["socket_port"] = host_andPort()[1]
                server = multiprocessing.Process(
                    name="terraform_stream",
                    target=sample_server,
                    args=(module_args["socket_host"], module_args["socket_port"]),
                )
                server.daemon = True
                server.start()
                self._display.display("Streaming long running tasks")
                module_return = self._execute_module(
                    module_name="terraform",
                    module_args=module_args,
                    task_vars=task_vars,
                    tmp=tmp,
                )
            finally:
                server.terminate()

        if module_return.get("failed"):
            display.display(module_return.get("msg"), color=C.COLOR_ERROR, stderr=True)
        return dict(module_return)
