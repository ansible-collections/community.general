#!/usr/bin/python

# Copyright (c) 2026, Dexter Le <dextersydney2001@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: kopia_notification
short_description: Manage Kopia notification profiles and templates
author:
  - Dexter Le (@munchtoast)
version_added: "13.1.0"
description:
  - Manage Kopia notification profiles and message templates using the Kopia CLI.
  - Supports configuring email, Pushover, and webhook notification profiles,
    as well as listing, showing, deleting, and testing profiles.
  - Supports listing, showing, setting, and removing notification message templates.
extends_documentation_fragment:
  - community.general._attributes
  - community.general._kopia
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  state:
    description:
      - Desired state of the notification resource.
    type: str
    choices:
      profile_email: >-
        Creates or updates an email notification profile.
        Requires O(profile_name), O(smtp_server), O(mail_to), and O(mail_from).
      profile_pushover: >-
        Creates or updates a Pushover notification profile.
        Requires O(profile_name), O(pushover_app_token), and O(pushover_user_key).
      profile_webhook: >-
        Creates or updates a webhook notification profile.
        Requires O(profile_name) and O(webhook_endpoint).
      profile_deleted: Removes a notification profile. Requires O(profile_name).
      profile_tested: >-
        Sends a test notification via the named profile.
        Requires O(profile_name).
      profiles_listed: Lists all configured notification profiles.
      profile_shown: Displays a specific notification profile. Requires O(profile_name).
      template_set: >-
        Sets a notification message template.
        Requires O(template_name) and O(template_file).
      template_removed: Removes a notification message template. Requires O(template_name).
      templates_listed: Lists all notification message templates.
      template_shown: >-
        Displays a specific notification message template.
        Requires O(template_name).
    default: profiles_listed
  profile_name:
    description:
      - Name of the notification profile to create, update, delete, test, or show.
      - Required if O(state=profile_email), O(state=profile_pushover),
        O(state=profile_webhook), O(state=profile_deleted), O(state=profile_tested),
        or O(state=profile_shown).
    type: str
  min_severity:
    description:
      - Minimum notification severity level that triggers this profile.
      - Optional for O(state=profile_email), O(state=profile_pushover),
        or O(state=profile_webhook).
    type: str
    choices: [verbose, info, warning, error]
  format:
    description:
      - Message format for notifications.
      - Optional for O(state=profile_email), O(state=profile_pushover),
        or O(state=profile_webhook).
    type: str
    choices: [html, md, txt]
  send_test:
    description:
      - When V(true), send a test notification immediately after configuring the profile.
      - Optional for O(state=profile_email), O(state=profile_pushover),
        or O(state=profile_webhook).
    type: bool
    default: false
  smtp_server:
    description:
      - SMTP server hostname or IP address.
      - Required if O(state=profile_email).
    type: str
  smtp_port:
    description:
      - SMTP server port.
      - Optional if O(state=profile_email).
    type: int
  smtp_username:
    description:
      - SMTP authentication username.
      - Optional if O(state=profile_email).
    type: str
  smtp_password:
    description:
      - SMTP authentication password.
      - Optional if O(state=profile_email).
    type: str
  smtp_identity:
    description:
      - SMTP SASL identity string.
      - Optional if O(state=profile_email).
    type: str
  mail_from:
    description:
      - Sender email address.
      - Required if O(state=profile_email).
    type: str
  mail_to:
    description:
      - Recipient email address.
      - Required if O(state=profile_email).
    type: str
  mail_cc:
    description:
      - CC email address.
      - Optional if O(state=profile_email).
    type: str
  pushover_app_token:
    description:
      - Pushover application token.
      - Required if O(state=profile_pushover).
    type: str
  pushover_user_key:
    description:
      - Pushover user key.
      - Required if O(state=profile_pushover).
    type: str
  webhook_endpoint:
    description:
      - Webhook destination URL.
      - Required if O(state=profile_webhook).
    type: str
  webhook_method:
    description:
      - HTTP method to use when calling the webhook.
      - Optional if O(state=profile_webhook).
    type: str
    choices: [GET, POST, PUT, PATCH]
  webhook_headers:
    description:
      - List of HTTP headers to include with webhook requests, each in C(key:value) format.
      - Optional if O(state=profile_webhook).
    type: list
    elements: str
  template_name:
    description:
      - Name of the notification template to set, remove, or show.
      - Required if O(state=template_set), O(state=template_removed),
        or O(state=template_shown).
    type: str
  template_file:
    description:
      - Path to a file containing the template body to set.
      - Required if O(state=template_set).
    type: path
"""

EXAMPLES = r"""
- name: Configure an email notification profile
  community.general.kopia_notification:
    state: profile_email
    profile_name: ops-email
    smtp_server: smtp.example.com
    smtp_port: 587
    smtp_username: notify@example.com
    smtp_password: smtpsecret
    mail_from: notify@example.com
    mail_to: ops@example.com
    min_severity: warning
    config: /etc/kopia/root.config

- name: Configure a Pushover notification profile
  community.general.kopia_notification:
    state: profile_pushover
    profile_name: ops-pushover
    pushover_app_token: "aToken123"
    pushover_user_key: "uKey456"
    min_severity: error
    config: /etc/kopia/root.config

- name: Configure a webhook notification profile
  community.general.kopia_notification:
    state: profile_webhook
    profile_name: ops-webhook
    webhook_endpoint: https://hooks.example.com/kopia
    webhook_method: POST
    webhook_headers:
      - "Authorization:Bearer mytoken"
    format: html
    config: /etc/kopia/root.config

- name: Send a test notification
  community.general.kopia_notification:
    state: profile_tested
    profile_name: ops-email
    config: /etc/kopia/root.config

- name: Show a notification profile
  community.general.kopia_notification:
    state: profile_shown
    profile_name: ops-email
    config: /etc/kopia/root.config

- name: List all notification profiles
  community.general.kopia_notification:
    state: profiles_listed
    config: /etc/kopia/root.config

- name: Delete a notification profile
  community.general.kopia_notification:
    state: profile_deleted
    profile_name: ops-email
    config: /etc/kopia/root.config

- name: Set a notification template from a file
  community.general.kopia_notification:
    state: template_set
    template_name: snapshot-complete
    template_file: /etc/kopia/templates/snapshot-complete.html
    config: /etc/kopia/root.config

- name: List all notification templates
  community.general.kopia_notification:
    state: templates_listed
    config: /etc/kopia/root.config

- name: Show a notification template
  community.general.kopia_notification:
    state: template_shown
    template_name: snapshot-complete
    config: /etc/kopia/root.config

- name: Remove a notification template
  community.general.kopia_notification:
    state: template_removed
    template_name: snapshot-complete
    config: /etc/kopia/root.config
"""

RETURN = r"""
kopia_notification:
  description: Output from the Kopia notification command.
  type: str
  sample: ""
  returned: always
"""

from ansible_collections.community.general.plugins.module_utils._cmd_runner import cmd_runner_fmt
from ansible_collections.community.general.plugins.module_utils._kopia import (
    KOPIA_COMMON_ARGUMENT_SPEC,
    kopia_runner,
)
from ansible_collections.community.general.plugins.module_utils._module_helper import StateModuleHelper

# Maps each module state to the kopia CLI words that follow `kopia notification`.
# profile configure email  → ("profile", "configure", "email")
# profile delete           → ("profile", "delete")
# template set             → ("template", "set")
# etc.
_STATE_CLI_MAP = {
    "profile_email": ("profile", "configure", "email"),
    "profile_pushover": ("profile", "configure", "pushover"),
    "profile_webhook": ("profile", "configure", "webhook"),
    "profile_deleted": ("profile", "delete"),
    "profile_tested": ("profile", "test"),
    "profiles_listed": ("profile", "list"),
    "profile_shown": ("profile", "show"),
    "template_set": ("template", "set"),
    "template_removed": ("template", "remove"),
    "templates_listed": ("template", "list"),
    "template_shown": ("template", "show"),
}

# Read-only states that must not be skipped in check mode.
_READONLY_STATES = frozenset(["profiles_listed", "profile_shown", "templates_listed", "template_shown"])


def _fmt_webhook_headers(value):
    """Expand a list of key:value strings into repeated --http-header flags."""
    if not value:
        return []
    result = []
    for header in value:
        result.extend(["--http-header", header])
    return result


class KopiaNotification(StateModuleHelper):
    module = dict(
        supports_check_mode=True,
        argument_spec=dict(
            **KOPIA_COMMON_ARGUMENT_SPEC,
            state=dict(
                type="str",
                default="profiles_listed",
                choices=[
                    "profile_email",
                    "profile_pushover",
                    "profile_webhook",
                    "profile_deleted",
                    "profile_tested",
                    "profiles_listed",
                    "profile_shown",
                    "template_set",
                    "template_removed",
                    "templates_listed",
                    "template_shown",
                ],
            ),
            profile_name=dict(type="str"),
            min_severity=dict(type="str", choices=["verbose", "info", "warning", "error"]),
            format=dict(type="str", choices=["html", "md", "txt"]),
            send_test=dict(type="bool", default=False),
            # email
            smtp_server=dict(type="str"),
            smtp_port=dict(type="int"),
            smtp_username=dict(type="str"),
            smtp_password=dict(type="str", no_log=True),
            smtp_identity=dict(type="str"),
            mail_from=dict(type="str"),
            mail_to=dict(type="str"),
            mail_cc=dict(type="str"),
            # pushover
            pushover_app_token=dict(type="str", no_log=True),
            pushover_user_key=dict(type="str", no_log=True),
            # webhook
            webhook_endpoint=dict(type="str"),
            webhook_method=dict(type="str", choices=["GET", "POST", "PUT", "PATCH"]),
            webhook_headers=dict(type="list", elements="str"),
            # template
            template_name=dict(type="str"),
            template_file=dict(type="path"),
        ),
        required_if=[
            ("state", "profile_email", ["profile_name", "smtp_server", "mail_from", "mail_to"]),
            ("state", "profile_pushover", ["profile_name", "pushover_app_token", "pushover_user_key"]),
            ("state", "profile_webhook", ["profile_name", "webhook_endpoint"]),
            ("state", "profile_deleted", ["profile_name"]),
            ("state", "profile_tested", ["profile_name"]),
            ("state", "profile_shown", ["profile_name"]),
            ("state", "template_set", ["template_name", "template_file"]),
            ("state", "template_removed", ["template_name"]),
            ("state", "template_shown", ["template_name"]),
        ],
    )

    def __init_module__(self):
        self.runner = kopia_runner(
            self.module,
            extra_formats=dict(
                list_profiles=cmd_runner_fmt.as_fixed("notification", "profile", "list"),
                notif_group=cmd_runner_fmt.as_list(),
                notif_subcommand=cmd_runner_fmt.as_list(),
                notif_provider=cmd_runner_fmt.as_list(),
                profile_name=cmd_runner_fmt.as_opt_val("--profile-name"),
                min_severity=cmd_runner_fmt.as_opt_val("--min-severity"),
                format=cmd_runner_fmt.as_opt_val("--format"),
                send_test=cmd_runner_fmt.as_bool("--send-test-notification"),
                smtp_server=cmd_runner_fmt.as_opt_val("--smtp-server"),
                smtp_port=cmd_runner_fmt.as_opt_val("--smtp-port"),
                smtp_username=cmd_runner_fmt.as_opt_val("--smtp-username"),
                smtp_password=cmd_runner_fmt.as_opt_val("--smtp-password"),
                smtp_identity=cmd_runner_fmt.as_opt_val("--smtp-identity"),
                mail_from=cmd_runner_fmt.as_opt_val("--mail-from"),
                mail_to=cmd_runner_fmt.as_opt_val("--mail-to"),
                mail_cc=cmd_runner_fmt.as_opt_val("--mail-cc"),
                pushover_app_token=cmd_runner_fmt.as_opt_val("--app-token"),
                pushover_user_key=cmd_runner_fmt.as_opt_val("--user-key"),
                webhook_endpoint=cmd_runner_fmt.as_opt_val("--endpoint"),
                webhook_method=cmd_runner_fmt.as_opt_val("--method"),
                webhook_headers=cmd_runner_fmt.as_func(_fmt_webhook_headers),
                template_name=cmd_runner_fmt.as_list(),
                template_file=cmd_runner_fmt.as_list(),
            ),
        )
        self.vars.set("previous_value", self._get()["out"])
        self.vars.set("value", self.vars.previous_value, change=True, diff=True)

    def __quit_module__(self):
        self.vars.set("value", self._get()["out"])

    def _get(self):
        with self.runner("list_profiles config") as ctx:
            result = ctx.run()
            return dict(
                rc=result[0],
                out=(result[1].rstrip() if result[1] else None),
                err=result[2],
            )

    def _process_command_output(self, fail_on_err, ignore_err_msg=""):
        def process(rc, out, err):
            if fail_on_err and rc != 0 and err and ignore_err_msg not in err:
                self.do_raise(f"kopia failed with error (rc={rc}): {err}")
            out = out.rstrip() if out else ""
            return None if out == "" else out

        return process

    def _run_notif_cmd(self, args_order, ignore_err_msg="", **run_kwargs):
        cli_words = _STATE_CLI_MAP[self.vars.state]
        notif_group = cli_words[0]
        notif_subcommand = cli_words[1]
        notif_provider = cli_words[2] if len(cli_words) == 3 else None
        check_mode_skip = self.vars.state not in _READONLY_STATES
        with self.runner(
            args_order,
            output_process=self._process_command_output(True, ignore_err_msg),
            check_mode_skip=check_mode_skip,
        ) as ctx:
            ctx.run(
                cli_action="notification",
                notif_group=notif_group,
                notif_subcommand=notif_subcommand,
                notif_provider=notif_provider,
                **run_kwargs,
            )

    def state_profile_email(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand notif_provider"
            " profile_name smtp_server smtp_port smtp_username smtp_password"
            " smtp_identity mail_from mail_to mail_cc"
            " min_severity format send_test config",
        )

    def state_profile_pushover(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand notif_provider"
            " profile_name pushover_app_token pushover_user_key"
            " min_severity format send_test config",
        )

    def state_profile_webhook(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand notif_provider"
            " profile_name webhook_endpoint webhook_method webhook_headers"
            " min_severity format send_test config",
        )

    def state_profile_deleted(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand profile_name config",
            ignore_err_msg="no such profile",
        )

    def state_profile_tested(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand profile_name config",
        )

    def state_profiles_listed(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand config",
        )

    def state_profile_shown(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand profile_name config",
        )

    def state_template_set(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand template_name template_file config",
        )

    def state_template_removed(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand template_name config",
            ignore_err_msg="no such template",
        )

    def state_templates_listed(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand config",
        )

    def state_template_shown(self):
        self._run_notif_cmd(
            "cli_action notif_group notif_subcommand template_name config",
        )


def main():
    KopiaNotification.execute()


if __name__ == "__main__":
    main()
