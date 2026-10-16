# Copyright (c) 2020, Yevhen Khmelenko <ujenmr@gmail.com>
# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
author: Yevhen Khmelenko (@ujenmr)
name: logstash
type: notification
short_description: Sends events to Logstash
description:
  - This callback reports facts and task events to Logstash U(https://www.elastic.co/products/logstash).
requirements:
  - whitelisting in configuration
  - logstash (Python library)
options:
  server:
    description: Address of the Logstash server. Used with all O(protocol) choices.
    type: str
    env:
      - name: LOGSTASH_SERVER
        deprecated:
          why: E(LOGSTASH_SERVER) does not follow the recommended C(ANSIBLE_) environment variable naming convention.
          alternative: Use E(ANSIBLE_CALLBACK_LOGSTASH_SERVER) instead.
          version: '16.0.0'
          collection_name: community.general
      - name: ANSIBLE_CALLBACK_LOGSTASH_SERVER
        version_added: '14.0.0'
    ini:
      - section: callback_logstash
        key: server
        version_added: 1.0.0
    vars:
      - name: ansible_callback_logstash_server
        version_added: '14.0.0'
    default: localhost
  port:
    description: Port on which Logstash is listening. Used with all O(protocol) choices.
    type: int
    env:
      - name: LOGSTASH_PORT
        deprecated:
          why: E(LOGSTASH_PORT) does not follow the recommended C(ANSIBLE_) environment variable naming convention.
          alternative: Use E(ANSIBLE_CALLBACK_LOGSTASH_PORT) instead.
          version: '16.0.0'
          collection_name: community.general
      - name: ANSIBLE_CALLBACK_LOGSTASH_PORT
        version_added: '14.0.0'
    ini:
      - section: callback_logstash
        key: port
        version_added: 1.0.0
    vars:
      - name: ansible_callback_logstash_port
        version_added: '14.0.0'
    default: 5000
  protocol:
    description: Transport protocol to use when sending events to Logstash.
    type: str
    choices:
      - tcp
      - http
      - https
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_PROTOCOL
    ini:
      - section: callback_logstash
        key: protocol
    vars:
      - name: ansible_callback_logstash_protocol
    default: tcp
    version_added: '14.0.0'
  http_path:
    description: >-
      HTTP request path, for example when sending events through a reverse proxy. This option is used only with
      O(protocol=http) or O(protocol=https).
    type: str
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_HTTP_PATH
    ini:
      - section: callback_logstash
        key: http_path
    vars:
      - name: ansible_callback_logstash_http_path
    default: /
    version_added: '14.0.0'
  username:
    description: >-
      Username for HTTP Basic authentication. This option is used only with O(protocol=http) or O(protocol=https),
      and must be set together with O(password).
    type: str
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_USERNAME
    ini:
      - section: callback_logstash
        key: username
    vars:
      - name: ansible_callback_logstash_username
    version_added: '14.0.0'
  password:
    description: >-
      Password for HTTP Basic authentication. This option is used only with O(protocol=http) or O(protocol=https),
      and must be set together with O(username). Use HTTPS to protect credentials and events in transit.
    type: str
    secret: true
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_PASSWORD
    ini:
      - section: callback_logstash
        key: password
    vars:
      - name: ansible_callback_logstash_password
    version_added: '14.0.0'
  validate_certs:
    description: Whether to validate the TLS certificate of the Logstash server. This option is used only with O(protocol=https).
    type: bool
    default: true
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_VALIDATE_CERTS
    ini:
      - section: callback_logstash
        key: validate_certs
    vars:
      - name: ansible_callback_logstash_validate_certs
    version_added: '14.0.0'
  ca_path:
    description: PEM-formatted file containing the CA certificate used to validate the Logstash server. This option is used only with O(protocol=https).
    type: path
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_CA_PATH
    ini:
      - section: callback_logstash
        key: ca_path
    vars:
      - name: ansible_callback_logstash_ca_path
    version_added: '14.0.0'
  client_cert:
    description: PEM-formatted certificate chain file for TLS client authentication. This option is used only with O(protocol=https).
    type: path
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_CLIENT_CERT
    ini:
      - section: callback_logstash
        key: client_cert
    vars:
      - name: ansible_callback_logstash_client_cert
    version_added: '14.0.0'
  client_key:
    description: >-
      PEM-formatted private key file for TLS client authentication. The key can also be included in O(client_cert).
      This option is used only with O(protocol=https).
    type: path
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_CLIENT_KEY
    ini:
      - section: callback_logstash
        key: client_key
    vars:
      - name: ansible_callback_logstash_client_key
    version_added: '14.0.0'
  timeout:
    description: Maximum time in seconds to wait for an HTTP request to complete. This option is used only with O(protocol=http) or O(protocol=https).
    type: int
    default: 10
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_TIMEOUT
    ini:
      - section: callback_logstash
        key: timeout
    vars:
      - name: ansible_callback_logstash_timeout
    version_added: '14.0.0'
  retries:
    description: >-
      Number of retries for HTTP 429 (Too Many Requests) responses. Uses exponential backoff with jitter between attempts. This
      option is used only with O(protocol=http) or O(protocol=https).
    type: int
    default: 3
    env:
      - name: ANSIBLE_CALLBACK_LOGSTASH_RETRIES
    ini:
      - section: callback_logstash
        key: retries
    vars:
      - name: ansible_callback_logstash_retries
    version_added: '14.0.0'
  type:
    description: Message type. Used with all O(protocol) choices.
    type: str
    env:
      - name: LOGSTASH_TYPE
        deprecated:
          why: E(LOGSTASH_TYPE) does not follow the recommended C(ANSIBLE_) environment variable naming convention.
          alternative: Use E(ANSIBLE_CALLBACK_LOGSTASH_TYPE) instead.
          version: '16.0.0'
          collection_name: community.general
      - name: ANSIBLE_CALLBACK_LOGSTASH_TYPE
        version_added: '14.0.0'
    ini:
      - section: callback_logstash
        key: type
        version_added: 1.0.0
    vars:
      - name: ansible_callback_logstash_type
        version_added: '14.0.0'
    default: ansible
  pre_command:
    description: Executes command before run and adds its result to the C(ansible_pre_command_output) Logstash field. Used with all O(protocol) choices.
    type: str
    version_added: 2.0.0
    ini:
      - section: callback_logstash
        key: pre_command
    env:
      - name: LOGSTASH_PRE_COMMAND
        deprecated:
          why: E(LOGSTASH_PRE_COMMAND) does not follow the recommended C(ANSIBLE_) environment variable naming convention.
          alternative: Use E(ANSIBLE_CALLBACK_LOGSTASH_PRE_COMMAND) instead.
          version: '16.0.0'
          collection_name: community.general
      - name: ANSIBLE_CALLBACK_LOGSTASH_PRE_COMMAND
        version_added: '14.0.0'
    vars:
      - name: ansible_callback_logstash_pre_command
        version_added: '14.0.0'
  format_version:
    description: Logging format. Used with all O(protocol) choices.
    type: str
    version_added: 2.0.0
    ini:
      - section: callback_logstash
        key: format_version
    env:
      - name: LOGSTASH_FORMAT_VERSION
        deprecated:
          why: E(LOGSTASH_FORMAT_VERSION) does not follow the recommended C(ANSIBLE_) environment variable naming convention.
          alternative: Use E(ANSIBLE_CALLBACK_LOGSTASH_FORMAT_VERSION) instead.
          version: '16.0.0'
          collection_name: community.general
      - name: ANSIBLE_CALLBACK_LOGSTASH_FORMAT_VERSION
        version_added: '14.0.0'
    vars:
      - name: ansible_callback_logstash_format_version
        version_added: '14.0.0'
    default: v1
    choices:
      - v1
      - v2
"""

EXAMPLES = r"""
ansible.cfg: |
  # Enable Callback plugin
  [defaults]
      callback_whitelist = community.general.logstash

  [callback_logstash]
      server = logstash.example.com
      port = 5000
      protocol = tcp
      pre_command = git rev-parse HEAD
      type = ansible

  HTTP(S) configuration with Basic authentication:

    Store the password in the callback's environment variable or a secrets manager, not in the configuration file.

    [defaults]
      callbacks_enabled = community.general.logstash

    [callback_logstash]
      protocol = https
      server = logstash.example.com
      port = 8080
      http_path = /
      username = ansible

Logstash HTTP input configuration:

11-input-http.conf: |-
    input {
    http {
      port => 8080
      user => "${LOGSTASH_HTTP_USER}"
      password => "${LOGSTASH_HTTP_PASSWORD}"
      ssl_enabled => true
      ssl_certificate => "/etc/logstash/server.crt"
      ssl_key => "/etc/logstash/server.pkcs8.key"
    }
    }

11-input-tcp.conf: |-
  # Enable Logstash TCP Input
  input {
          tcp {
              port => 5000
              codec => json
              add_field => { "[@metadata][beat]" => "notify" }
              add_field => { "[@metadata][type]" => "ansible" }
          }
      }
"""

import json
import logging
import os
import random
import socket
import time
import uuid
from urllib.error import HTTPError

from ansible import context
from ansible.module_utils.urls import open_url
from ansible.utils.display import Display

try:
    import logstash
    from logstash.formatter import LogstashFormatterVersion1

    HAS_LOGSTASH = True
except ImportError:
    HAS_LOGSTASH = False
    LogstashFormatterVersion1 = None

from ansible.plugins.callback import CallbackBase

from ansible_collections.community.general.plugins.module_utils._datetime import (
    now,
)
from ansible_collections.community.general.plugins.module_utils._secrets import mask_secrets


class LogstashHTTPHandler(logging.Handler):
    def __init__(
        self,
        url,
        formatter,
        username=None,
        password=None,
        validate_certs=True,
        ca_path=None,
        client_cert=None,
        client_key=None,
        timeout=10,
        retries=3,
        display=None,
    ):
        super().__init__()
        self.url = url
        self.formatter = formatter
        self.username = username
        self.password = password
        self.validate_certs = validate_certs
        self.ca_path = ca_path
        self.client_cert = client_cert
        self.client_key = client_key
        self.timeout = timeout
        self.retries = retries
        self._display = display or Display()

    def emit(self, record):
        try:
            data = self.formatter.format(record)
        except Exception:
            self._display.warning("Could not format event for Logstash HTTP delivery.")
            return
        kwargs = {
            "data": data,
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "timeout": self.timeout,
            "validate_certs": self.validate_certs,
            "use_netrc": False,
            "follow_redirects": "none",
        }
        if self.username and self.password:
            kwargs.update(
                url_username=self.username,
                url_password=self.password,
                force_basic_auth=True,
            )
        if self.ca_path is not None:
            kwargs["ca_path"] = self.ca_path
        if self.client_cert is not None:
            kwargs["client_cert"] = self.client_cert
        if self.client_key is not None:
            kwargs["client_key"] = self.client_key

        status = None
        for attempt in range(self.retries + 1):
            try:
                response = open_url(self.url, **kwargs)
            except HTTPError as error:
                status = error.code
                error.close()
            except Exception:
                self._display.warning("Could not send event to Logstash over HTTP.")
                return
            else:
                try:
                    status = response.getcode()
                finally:
                    response.close()

            if status in (200, 201, 202, 204):
                return
            if status != 429 or attempt == self.retries:
                break
            time.sleep(0.5 * 2**attempt + random.uniform(0, 0.25))

        self._display.warning(f"Logstash HTTP request failed with status code {status}.")


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.logstash"
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super().__init__()

        if not HAS_LOGSTASH:
            self.disabled = True
            self._display.warning("The required python3-logstash is not installed.")

        self.start_time = now()

    def _init_plugin(self):
        if not self.disabled:
            self.logger = logging.getLogger("python-logstash-logger")
            self.logger.setLevel(logging.DEBUG)

            if self.ls_protocol == "tcp":
                self.handler = logstash.TCPLogstashHandler(
                    self.ls_server, self.ls_port, version=1, message_type=self.ls_type
                )
            else:
                server = self.ls_server
                if ":" in server and not server.startswith("["):
                    server = f"[{server}]"
                path = self.ls_http_path or "/"
                if not path.startswith("/"):
                    path = f"/{path}"
                url = f"{self.ls_protocol}://{server}:{self.ls_port}{path}"
                formatter = LogstashFormatterVersion1(message_type=self.ls_type)
                self.handler = LogstashHTTPHandler(
                    url=url,
                    formatter=formatter,
                    username=self.ls_username,
                    password=self.ls_password,
                    validate_certs=self.ls_validate_certs,
                    ca_path=self.ls_ca_path,
                    client_cert=self.ls_client_cert,
                    client_key=self.ls_client_key,
                    timeout=self.ls_timeout,
                    retries=self.ls_retries,
                    display=self._display,
                )

            self.logger.addHandler(self.handler)
            self.hostname = socket.gethostname()
            self.session = str(uuid.uuid4())
            self.errors = 0

            self.base_data = {"session": self.session, "host": self.hostname}

            if self.ls_pre_command is not None:
                self.base_data["ansible_pre_command_output"] = os.popen(self.ls_pre_command).read()

            if context.CLIARGS is not None:
                self.base_data["ansible_checkmode"] = context.CLIARGS.get("check")
                self.base_data["ansible_tags"] = context.CLIARGS.get("tags")
                self.base_data["ansible_skip_tags"] = context.CLIARGS.get("skip_tags")
                self.base_data["inventory"] = context.CLIARGS.get("inventory")

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.ls_server = self.get_option("server")
        self.ls_port = int(self.get_option("port"))
        self.ls_protocol = self.get_option("protocol")
        self.ls_http_path = self.get_option("http_path")
        self.ls_username = self.get_option("username")
        self.ls_password = self.get_option("password")
        self.ls_validate_certs = self.get_option("validate_certs")
        self.ls_ca_path = self.get_option("ca_path")
        self.ls_client_cert = self.get_option("client_cert")
        self.ls_client_key = self.get_option("client_key")
        self.ls_timeout = self.get_option("timeout")
        self.ls_retries = self.get_option("retries")
        self.ls_type = self.get_option("type")
        self.ls_pre_command = self.get_option("pre_command")
        self.ls_format_version = self.get_option("format_version")

        if self.ls_protocol != "tcp":
            if bool(self.ls_username) != bool(self.ls_password):
                self.disabled = True
                self._display.warning("Both Logstash HTTP username and password must be configured.")
            if self.ls_timeout <= 0:
                self.disabled = True
                self._display.warning("Logstash HTTP timeout must be greater than zero.")
            if self.ls_retries < 0:
                self.disabled = True
                self._display.warning("Logstash HTTP retries must be zero or greater.")
            if self.ls_protocol != "https" and (self.ls_ca_path or self.ls_client_cert or self.ls_client_key):
                self.disabled = True
                self._display.warning("Logstash TLS certificate options can only be used with HTTPS.")
            if self.ls_client_key and not self.ls_client_cert:
                self.disabled = True
                self._display.warning("Logstash client_key requires client_cert.")

        self._init_plugin()

    def v2_playbook_on_start(self, playbook):
        data = self.base_data.copy()
        data["ansible_type"] = "start"
        data["status"] = "OK"
        data["ansible_playbook"] = playbook._file_name

        if self.ls_format_version == "v2":
            self.logger.info("START PLAYBOOK | %s", data["ansible_playbook"], extra=data)
        else:
            self.logger.info("ansible start", extra=data)

    def v2_playbook_on_stats(self, stats):
        end_time = now()
        runtime = end_time - self.start_time
        summarize_stat = {}
        for host in stats.processed.keys():
            summarize_stat[host] = stats.summarize(host)

        if self.errors == 0:
            status = "OK"
        else:
            status = "FAILED"

        data = self.base_data.copy()
        data["ansible_type"] = "finish"
        data["status"] = status
        data["ansible_playbook_duration"] = runtime.total_seconds()
        data["ansible_result"] = json.dumps(summarize_stat)  # deprecated field

        if self.ls_format_version == "v2":
            self.logger.info("FINISH PLAYBOOK | %s", json.dumps(summarize_stat), extra=data)
        else:
            self.logger.info("ansible stats", extra=data)

    def v2_playbook_on_play_start(self, play):
        self.play_id = str(play._uuid)

        if play.name:
            self.play_name = play.name

        data = self.base_data.copy()
        data["ansible_type"] = "start"
        data["status"] = "OK"
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)

        if self.ls_format_version == "v2":
            self.logger.info("START PLAY | %s", mask_secrets(self.play_name), extra=data)
        else:
            self.logger.info("ansible play", extra=data)

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task_id = str(task._uuid)

    """
    Tasks and handler tasks are dealt with here
    """

    def v2_runner_on_ok(self, result, **kwargs):
        task_name = str(result._task).replace("TASK: ", "").replace("HANDLER: ", "")

        data = self.base_data.copy()
        if task_name == "setup":
            data["ansible_type"] = "setup"
            data["status"] = "OK"
            data["ansible_host"] = result._host.name
            data["ansible_play_id"] = self.play_id
            data["ansible_play_name"] = mask_secrets(self.play_name)
            data["ansible_task"] = mask_secrets(task_name)
            data["ansible_facts"] = self._dump_results(result._result)

            if self.ls_format_version == "v2":
                self.logger.info("SETUP FACTS | %s", self._dump_results(result._result), extra=data)
            else:
                self.logger.info("ansible facts", extra=data)
        else:
            if "changed" in result._result.keys():
                data["ansible_changed"] = result._result["changed"]
            else:
                data["ansible_changed"] = False

            data["ansible_type"] = "task"
            data["status"] = "OK"
            data["ansible_host"] = result._host.name
            data["ansible_play_id"] = self.play_id
            data["ansible_play_name"] = mask_secrets(self.play_name)
            data["ansible_task"] = mask_secrets(task_name)
            data["ansible_task_id"] = self.task_id
            data["ansible_result"] = self._dump_results(result._result)

            if self.ls_format_version == "v2":
                self.logger.info(
                    "TASK OK | %s | RESULT | %s",
                    mask_secrets(task_name),
                    self._dump_results(result._result),
                    extra=data,
                )
            else:
                self.logger.info("ansible ok", extra=data)

    def v2_runner_on_skipped(self, result, **kwargs):
        task_name = str(result._task).replace("TASK: ", "").replace("HANDLER: ", "")

        data = self.base_data.copy()
        data["ansible_type"] = "task"
        data["status"] = "SKIPPED"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["ansible_task"] = mask_secrets(task_name)
        data["ansible_task_id"] = self.task_id
        data["ansible_result"] = self._dump_results(result._result)

        if self.ls_format_version == "v2":
            self.logger.info("TASK SKIPPED | %s", mask_secrets(task_name), extra=data)
        else:
            self.logger.info("ansible skipped", extra=data)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        data = self.base_data.copy()
        data["ansible_type"] = "import"
        data["status"] = "IMPORTED"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["imported_file"] = mask_secrets(imported_file)

        if self.ls_format_version == "v2":
            self.logger.info("IMPORT | %s", mask_secrets(imported_file), extra=data)
        else:
            self.logger.info("ansible import", extra=data)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        data = self.base_data.copy()
        data["ansible_type"] = "import"
        data["status"] = "NOT IMPORTED"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["imported_file"] = mask_secrets(missing_file)

        if self.ls_format_version == "v2":
            self.logger.info("NOT IMPORTED | %s", mask_secrets(missing_file), extra=data)
        else:
            self.logger.info("ansible import", extra=data)

    def v2_runner_on_failed(self, result, **kwargs):
        task_name = str(result._task).replace("TASK: ", "").replace("HANDLER: ", "")

        data = self.base_data.copy()
        if "changed" in result._result.keys():
            data["ansible_changed"] = result._result["changed"]
        else:
            data["ansible_changed"] = False

        data["ansible_type"] = "task"
        data["status"] = "FAILED"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["ansible_task"] = mask_secrets(task_name)
        data["ansible_task_id"] = self.task_id
        data["ansible_result"] = self._dump_results(result._result)

        self.errors += 1
        if self.ls_format_version == "v2":
            self.logger.error(
                "TASK FAILED | %s | HOST | %s | RESULT | %s",
                mask_secrets(task_name),
                self.hostname,
                self._dump_results(result._result),
                extra=data,
            )
        else:
            self.logger.error("ansible failed", extra=data)

    def v2_runner_on_unreachable(self, result, **kwargs):
        task_name = str(result._task).replace("TASK: ", "").replace("HANDLER: ", "")

        data = self.base_data.copy()
        data["ansible_type"] = "task"
        data["status"] = "UNREACHABLE"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["ansible_task"] = mask_secrets(task_name)
        data["ansible_task_id"] = self.task_id
        data["ansible_result"] = self._dump_results(result._result)

        self.errors += 1
        if self.ls_format_version == "v2":
            self.logger.error(
                "UNREACHABLE | %s | HOST | %s | RESULT | %s",
                mask_secrets(task_name),
                self.hostname,
                self._dump_results(result._result),
                extra=data,
            )
        else:
            self.logger.error("ansible unreachable", extra=data)

    def v2_runner_on_async_failed(self, result, **kwargs):
        task_name = str(result._task).replace("TASK: ", "").replace("HANDLER: ", "")

        data = self.base_data.copy()
        data["ansible_type"] = "task"
        data["status"] = "FAILED"
        data["ansible_host"] = result._host.name
        data["ansible_play_id"] = self.play_id
        data["ansible_play_name"] = mask_secrets(self.play_name)
        data["ansible_task"] = mask_secrets(task_name)
        data["ansible_task_id"] = self.task_id
        data["ansible_result"] = self._dump_results(result._result)

        self.errors += 1
        if self.ls_format_version == "v2":
            self.logger.error(
                "ASYNC FAILED | %s | HOST | %s | RESULT | %s",
                mask_secrets(task_name),
                self.hostname,
                self._dump_results(result._result),
                extra=data,
            )
        else:
            self.logger.error("ansible async", extra=data)
