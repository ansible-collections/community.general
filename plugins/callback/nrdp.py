# Copyright (c) 2018 Remi Verchere <remi@verchere.fr>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Make coding more python3-ish
from __future__ import annotations

DOCUMENTATION = r"""
name: nrdp
type: notification
author: "Remi VERCHERE (@rverchere)"
short_description: Post task results to a Nagios server through nrdp
description:
  - This callback send playbook result to Nagios.
  - Nagios shall use NRDP to receive passive events.
  - The passive check is sent to a dedicated host/service for Ansible.
options:
  url:
    description: URL of the nrdp server.
    required: true
    env:
      - name: NRDP_URL
    ini:
      - section: callback_nrdp
        key: url
    type: string
  validate_certs:
    description: Validate the SSL certificate of the nrdp server. (Used for HTTPS URLs).
    env:
      - name: NRDP_VALIDATE_CERTS
    ini:
      - section: callback_nrdp
        key: validate_nrdp_certs
      - section: callback_nrdp
        key: validate_certs
    type: boolean
    default: false
    aliases: [validate_nrdp_certs]
  token:
    description: Token to be allowed to push nrdp events.
    required: true
    env:
      - name: NRDP_TOKEN
    ini:
      - section: callback_nrdp
        key: token
    type: string
  hostname:
    description: Hostname where the passive check is linked to.
    required: true
    env:
      - name: NRDP_HOSTNAME
    ini:
      - section: callback_nrdp
        key: hostname
    type: string
  servicename:
    description: Service where the passive check is linked to.
    required: true
    env:
      - name: NRDP_SERVICENAME
    ini:
      - section: callback_nrdp
        key: servicename
    type: string
"""

from urllib.parse import urlencode

from ansible.module_utils.common.text.converters import to_bytes
from ansible.module_utils.urls import open_url
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    send ansible-playbook to Nagios server using nrdp protocol
    """

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "community.general.nrdp"
    CALLBACK_NEEDS_WHITELIST = True

    # Nagios states
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self):
        super().__init__()

        self.printed_playbook = False
        self.playbook_name = None
        self.play = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super().set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        self.url = self.get_option("url")
        if not self.url.endswith("/"):
            self.url += "/"
        self.token = self.get_option("token")
        self.hostname = self.get_option("hostname")
        self.servicename = self.get_option("servicename")
        self.validate_nrdp_certs = self.get_option("validate_certs")

        if (self.url or self.token or self.hostname or self.servicename) is None:
            self._display.warning(
                "NRDP callback wants the NRDP_URL,"
                " NRDP_TOKEN, NRDP_HOSTNAME,"
                " NRDP_SERVICENAME"
                " environment variables'."
                " The NRDP callback plugin is disabled."
            )
            self.disabled = True

    def _send_nrdp(self, state, msg):
        """
        nrpd service check send XMLDATA like this:
        <?xml version='1.0'?>
            <checkresults>
                <checkresult type='service'>
                    <hostname>somehost</hostname>
                    <servicename>someservice</servicename>
                    <state>1</state>
                    <output>WARNING: Danger Will Robinson!|perfdata</output>
                </checkresult>
            </checkresults>
        """
        xmldata = "<?xml version='1.0'?>\n"
        xmldata += "<checkresults>\n"
        xmldata += "<checkresult type='service'>\n"
        xmldata += f"<hostname>{self.hostname}</hostname>\n"
        xmldata += f"<servicename>{self.servicename}</servicename>\n"
        xmldata += f"<state>{state}</state>\n"
        xmldata += f"<output>{msg}</output>\n"
        xmldata += "</checkresult>\n"
        xmldata += "</checkresults>\n"

        body = {"cmd": "submitcheck", "token": self.token, "XMLDATA": to_bytes(xmldata)}

        try:
            response = open_url(self.url, data=urlencode(body), method="POST", validate_certs=self.validate_nrdp_certs)
            return response.read()
        except Exception as ex:
            self._display.warning(f"NRDP callback cannot send result {ex}")

    def v2_playbook_on_play_start(self, play):
        """
        Display Playbook and play start messages
        """
        self.play = play

    def v2_playbook_on_stats(self, stats):
        """
        Display info about playbook statistics
        """
        name = self.play
        gstats = ""
        hosts = sorted(stats.processed.keys())
        critical = warning = 0
        for host in hosts:
            stat = stats.summarize(host)
            gstats += (
                f"'{host}_ok'={stat['ok']} '{host}_changed'={stat['changed']}"
                f" '{host}_unreachable'={stat['unreachable']} '{host}_failed'={stat['failures']} "
            )
            # Critical when failed tasks or unreachable host
            critical += stat["failures"]
            critical += stat["unreachable"]
            # Warning when changed tasks
            warning += stat["changed"]

        msg = f"{name} | {gstats}"
        if critical:
            # Send Critical
            self._send_nrdp(self.CRITICAL, msg)
        elif warning:
            # Send Warning
            self._send_nrdp(self.WARNING, msg)
        else:
            # Send OK
            self._send_nrdp(self.OK, msg)
