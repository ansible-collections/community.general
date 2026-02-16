#!/usr/bin/python
# Copyright (c) 2026 Aleksandr Gabidullin <qualittv@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
module: logrotate
version_added: 12.4.0
short_description: Manage logrotate configurations
description:
  - Manage C(logrotate) configuration files and settings.
  - Create, update, or remove C(logrotate) configurations for applications and services.
author: "Aleksandr Gabidullin (@a-gabidullin)"
requirements:
  - logrotate >= 3.8.0
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  name:
    description:
      - Name of the logrotate configuration.
      - This creates a file in O(config_dir) with this name.
    type: str
    required: true
    aliases: [config_name]
  state:
    description:
      - Whether the configuration should be present or absent.
    type: str
    choices: [present, absent]
  config_dir:
    description:
      - Directory where logrotate configurations are stored.
      - Default is V(/etc/logrotate.d) for system-wide configurations.
      - Use V(~/.logrotate.d) for user-specific configurations.
      - This directory must exist before using the module.
    type: path
  paths:
    description:
      - List of log file paths or patterns to rotate.
      - Can include wildcards (for example V(/var/log/app/*.log)).
      - Required when creating a new configuration (O(state=present) and config file does not exist).
      - Optional when modifying existing configuration (for example to enable/disable).
    type: list
    elements: path
  rotation_period:
    description:
      - How often to rotate the logs.
      - If not specified, existing value be preserved when modifying configuration.
      - When creating new configuration, be used if not specified.
    type: str
    choices: [daily, weekly, monthly, yearly]
  rotate_count:
    description:
      - Number of rotated log files to keep.
      - Set to V(0) to disable rotation (keep only current log).
      - Set to V(-1) to keep all rotated logs (not recommended).
    type: int
  compress:
    description:
      - Compress rotated log files.
    type: bool
  compress_options:
    description:
      - Options to pass to compression program.
      - For O(compression_method=gzip), use V(-9) for best compression, V(-1) for fastest.
      - For O(compression_method=xz), use V(-9) for best compression.
    type: str
  compression_method:
    description:
      - Compression method to use.
      - Requires logrotate 3.18.0 or later for V(xz) and V(zstd).
    type: str
    choices: [gzip, bzip2, xz, zstd, lzma, lz4]
  delay_compress:
    description:
      - Postpone compression of the previous log file to the next rotation cycle.
      - Useful for applications that keep writing to the old log file for some time.
    type: bool
  no_delay_compress:
    description:
      - Opposite of O(delay_compress). Ensure compression happens immediately.
      - Note that in logrotate, V(no_delay_compress) is the default behavior.
    type: bool
  shred:
    description:
      - Use shred to securely delete rotated log files.
      - Uses V(shred -u) to overwrite files before deleting.
    type: bool
  shred_cycles:
    description:
      - Number of times to overwrite files when using O(shred=true).
    type: int
  missing_ok:
    description:
      - Do not issue an error if the log file is missing.
    type: bool
  not_if_empty:
    description:
      - Do not rotate the log file if it is empty.
      - Set to V(false) to rotate even empty log files (equivalent to C(ifempty) in logrotate).
    type: bool
  create:
    description:
      - Create new log file with specified permissions after rotation.
      - Format is V(mode owner group) (for example V(0640 root adm)).
      - Set to V(null) or omit to use V(nocreate).
    type: str
  copy_truncate:
    description:
      - Copy the log file and then truncate it in place.
      - Useful for applications that cannot be told to close their logfile.
    type: bool
  copy:
    description:
      - Copy the log file but do not truncate the original.
      - Takes precedence over O(rename_copy) and O(copy_truncate).
    type: bool
  rename_copy:
    description:
      - Rename and copy the log file, leaving the original in place.
    type: bool
  size:
    description:
      - Rotate log file when it grows bigger than specified size.
      - Format is V(number[k|M|G]) (for example V(100M), V(1G)).
      - Overrides O(rotation_period) when set.
      - If not specified, existing value be preserved when modifying configuration.
      - When creating new configuration, this option be omitted if not specified.
    type: str
  min_size:
    description:
      - Rotate log file only if it has grown bigger than specified size.
      - Format is V(number[k|M|G]) (for example V(100M), V(1G)).
      - Used with time-based rotation to avoid rotating too small files.
    type: str
  max_size:
    description:
      - Rotate log file when it grows bigger than specified size, but at most once per O(rotation_period).
      - Format is V(number[k|M|G]) (for example V(100M), V(1G)).
    type: str
  max_age:
    description:
      - Remove rotated logs older than specified number of days.
    type: int
  date_ext:
    description:
      - Use date as extension for rotated files (using the date format specified in O(date_format) instead of sequential
        numbers).
    type: bool
  date_yesterday:
    description:
      - Use yesterday's date for O(date_ext) instead of today's date.
      - Useful for rotating logs that span midnight.
    type: bool
  date_format:
    description:
      - Format for date extension.
      - Use with O(date_ext=true).
      - Format specifiers are V(%Y) year, V(%m) month, V(%d) day, V(%s) seconds since epoch.
    type: str
  shared_scripts:
    description:
      - Run O(pre_rotate) and O(post_rotate) scripts only once for all matching log files.
    type: bool
  pre_rotate:
    description:
      - Commands to execute before rotating the log file.
      - Can be a single string or list of commands.
    type: list
    elements: str
  post_rotate:
    description:
      - Commands to execute after rotating the log file.
      - Can be a single string or list of commands.
    type: list
    elements: str
  first_action:
    description:
      - Commands to execute once before all log files that match the wildcard pattern are rotated.
    type: list
    elements: str
  last_action:
    description:
      - Commands to execute once after all log files that match the wildcard pattern are rotated.
    type: list
    elements: str
  pre_remove:
    description:
      - Commands to execute before removing rotated log files.
    type: list
    elements: str
  su:
    description:
      - Set user and group for rotated files.
      - Format is V(user group) (e.g., V(www-data adm)).
      - Set to V("") (empty string) to remove the directive from existing configurations.
      - Set to V(null) or omit to leave the existing value unchanged (when modifying) or not set (when creating).
    type: str
  old_dir:
    description:
      - Move rotated logs into specified directory.
    type: path
  create_old_dir:
    description:
      - Create O(old_dir) directory if it does not exist.
    type: bool
  no_old_dir:
    description:
      - Keep rotated logs in the same directory as the original log.
    type: bool
  extension:
    description:
      - Extension to use for rotated log files (including dot).
      - Useful when O(compress=false).
    type: str
  mail:
    description:
      - Mail logs to specified address when removed.
      - Set to V(null) or omit to not mail logs.
    type: str
  mail_first:
    description:
      - Mail just-created log file, not the about-to-expire one.
    type: bool
  mail_last:
    description:
      - Mail about-to-expire log file (default).
    type: bool
  include:
    description:
      - Include additional configuration files from specified directory.
    type: path
  taboo_ext:
    description:
      - List of extensions that logrotate should not touch.
      - Set to V(null) or empty list to clear defaults.
    type: list
    elements: str
  enabled:
    description:
      - Whether the configuration should be enabled.
      - When V(false), adds V(.disabled) extension to the config file.
    type: bool
  start:
    description:
      - Base number for rotated files. Allowed values are from V(0) to V(999).
      - For example, V(1) gives files C(.1), C(.2), and so on instead of C(.0), C(.1).
    type: int
  syslog:
    description:
      - Send logrotate messages to syslog.
    type: bool
extends_documentation_fragment:
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Ensure logrotate config directory exists
  ansible.builtin.file:
    path: /etc/logrotate.d
    state: directory
    mode: '0755'

- name: Configure log rotation for Nginx
  community.general.logrotate:
    name: nginx
    paths:
      - /var/log/nginx/*.log
    rotation_period: daily
    rotate_count: 14
    compress: true
    compress_options: "-9"
    delay_compress: true
    missing_ok: true
    not_if_empty: true
    create: "0640 www-data adm"
    shared_scripts: true
    post_rotate:
      - "[ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)"
      - "echo 'Nginx logs rotated'"

- name: Configure size-based rotation for application logs
  community.general.logrotate:
    name: myapp
    paths:
      - /var/log/myapp/app.log
      - /var/log/myapp/debug.log
    size: 100M
    rotate_count: 10
    compress: true
    compress_options: "-1"
    date_ext: true
    date_yesterday: true
    date_format: -%Y%m%d.%s
    missing_ok: true
    copy_truncate: true

- name: Configure log rotation with secure deletion
  community.general.logrotate:
    name: secure-app
    paths:
      - /var/log/secure-app/*.log
    rotation_period: weekly
    rotate_count: 4
    shred: true
    shred_cycles: 3
    compress: true
    compress_options: "-9"

- name: Configure log rotation with custom start number
  community.general.logrotate:
    name: custom-start
    paths:
      - /var/log/custom/*.log
    rotation_period: monthly
    rotate_count: 6
    start: 1
    compress: true

- name: Configure log rotation with old directory
  community.general.logrotate:
    name: with-old-dir
    paths:
      - /opt/app/logs/*.log
    rotation_period: weekly
    rotate_count: 4
    old_dir: /var/log/archives
    create_old_dir: true
    compress: true
    compression_method: zstd

- name: Disable logrotate configuration
  community.general.logrotate:
    name: old-service
    enabled: false

- name: Remove logrotate configuration
  community.general.logrotate:
    name: deprecated-app
    state: absent

- name: Complex configuration with multiple scripts
  community.general.logrotate:
    name: complex-app
    paths:
      - /var/log/complex/*.log
    rotation_period: monthly
    rotate_count: 6
    compress: true
    delay_compress: false
    pre_rotate:
      - "echo 'Starting rotation for complex app'"
      - "systemctl stop complex-app"
    post_rotate:
      - "systemctl start complex-app"
      - "echo 'Rotation completed'"
      - "logger -t logrotate 'Complex app logs rotated'"
    first_action:
      - "echo 'First action: Starting batch rotation'"
    last_action:
      - "echo 'Last action: Batch rotation complete'"

- name: User-specific logrotate configuration
  community.general.logrotate:
    name: myuser-apps
    config_dir: ~/.logrotate.d
    paths:
      - ~/app/*.log
      - ~/.cache/*/*.log
    rotation_period: daily
    rotate_count: 30
    compress: true
    su: "{{ ansible_user_id }} users"

- name: Configuration with copy instead of move
  community.general.logrotate:
    name: copy-config
    paths:
      - /var/log/copy-app/*.log
    rotation_period: daily
    rotate_count: 7
    copy: true

- name: Configuration with syslog notifications
  community.general.logrotate:
    name: syslog-config
    paths:
      - /var/log/syslog-app/*.log
    rotation_period: daily
    rotate_count: 14
    syslog: true
    compress: true

- name: Configuration without compression
  community.general.logrotate:
    name: nocompress-config
    paths:
      - /var/log/nocompress/*.log
    rotation_period: daily
    rotate_count: 7
    compress: false

- name: Configuration with custom taboo extensions
  community.general.logrotate:
    name: taboo-config
    paths:
      - /var/log/taboo/*.log
    rotation_period: daily
    rotate_count: 7
    taboo_ext: [".backup", ".tmp", ".temp"]
"""

RETURN = r"""
config_file:
  description: Path to the created/updated logrotate configuration file.
  type: str
  returned: success when O(state=present)
  sample: /etc/logrotate.d/nginx
config_content:
  description: The generated logrotate configuration content.
  type: str
  returned: success when O(state=present)
  sample: |
    /var/log/nginx/*.log {
        daily
        rotate 14
        compress
        compress_options -9
        delay_compress
        missing_ok
        notifempty
        create 0640 www-data adm
        shared_scripts
        post_rotate
            [ -f /var/run/nginx.pid ] && kill -USR1 $(cat /var/run/nginx.pid)
            echo 'Nginx logs rotated'
        endscript
    }
enabled_state:
  description: Current enabled state of the configuration.
  type: bool
  returned: success
  sample: true
backup_file:
  description: Path to the backup of the original configuration file, if it was backed up.
  type: str
  returned: success when backup was made
  sample: /etc/logrotate.d/nginx.20250101_120000
"""

import os
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.text.converters import to_native


class LogrotateConfig:
    """Logrotate configuration manager."""

    def __init__(self, module: AnsibleModule, logrotate_bin: str) -> None:
        self.module = module
        self.params = module.params
        self.logrotate_bin = logrotate_bin
        self.result: dict[str, object] = {
            "changed": False,
            "config_file": "",
            "config_content": "",
            "enabled_state": True,
        }

        self.config_dir = self.params["config_dir"]
        self.config_name = self.params["name"]
        self.disabled_suffix = ".disabled"

        self.config_file = self.get_config_path(self.params["enabled"])

    def get_config_path(self, enabled: bool) -> str:
        """Get config file path based on enabled state."""
        base_path = os.path.join(self.config_dir, self.config_name)
        if not enabled:
            return base_path + self.disabled_suffix
        return base_path

    def validate_parameters(self) -> None:
        """Validate module parameters."""
        if self.params.get("start") is not None:
            if self.params["start"] < 0 or self.params["start"] > 999:
                self.module.fail_json(msg="'start' must be between 0 and 999")

        if self.params.get("size") and self.params.get("max_size"):
            self.module.fail_json(msg="'size' and 'max_size' parameters are mutually exclusive")

        su_val = self.params.get("su")
        if su_val is not None:
            if su_val == "":
                pass
            else:
                su_parts = su_val.split()
                if len(su_parts) != 2:
                    self.module.fail_json(msg="'su' parameter must be in format 'user group' or empty string to remove")

        if self.params.get("shred_cycles", 1) < 1:
            self.module.fail_json(msg="'shred_cycles' must be a positive integer")

        for size_param in ["size", "min_size", "max_size"]:
            if self.params.get(size_param):
                if not re.match(r"^\d+[kMG]?$", self.params[size_param], re.I):
                    self.module.fail_json(
                        msg=f"'{size_param}' must be in format 'number[k|M|G]' (for example '100M', '1G')"
                    )

        if self.params.get("old_dir") and self.params.get("no_old_dir"):
            self.module.fail_json(msg="'old_dir' and 'no_old_dir' parameters are mutually exclusive")

        copy_params = [self.params.get("copy"), self.params.get("copy_truncate"), self.params.get("rename_copy")]
        if sum(1 for v in copy_params if v) > 1:
            self.module.fail_json(msg="'copy', 'copy_truncate', and 'rename_copy' parameters are mutually exclusive")

        if self.params.get("delay_compress") and self.params.get("no_delay_compress"):
            self.module.fail_json(msg="'delay_compress' and 'no_delay_compress' parameters are mutually exclusive")

        if self.params["state"] == "present":
            existing_content = self.read_existing_config(any_state=True)
            if not existing_content and not self.params.get("paths"):
                self.module.fail_json(msg="'paths' parameter is required when creating a new configuration")

    def read_existing_config(self, any_state: bool = False) -> str | None:
        """Read existing configuration file.

        Args:
            any_state: If True, check both enabled and disabled versions.
                      If False, only check based on current enabled param.
        """
        if any_state:
            for suffix in ["", self.disabled_suffix]:
                config_path = os.path.join(self.config_dir, self.config_name + suffix)
                if os.path.exists(config_path):
                    self.result["enabled_state"] = suffix == ""
                    try:
                        with open(config_path, "r") as f:
                            return f.read()
                    except Exception as e:
                        self.module.fail_json(msg=f"Failed to read config file {config_path}: {to_native(e)}")
        else:
            config_path = self.get_config_path(self.params["enabled"])
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as f:
                        return f.read()
                except Exception as e:
                    self.module.fail_json(msg=f"Failed to read config file {config_path}: {to_native(e)}")

        return None

    def generate_config_content(self) -> str:
        """Generate logrotate configuration content."""
        if not self.params.get("paths"):
            existing_content = self.read_existing_config(any_state=True)
            if existing_content:
                lines = existing_content.strip().split("\n")
                paths = []
                for line in lines:
                    line = line.strip()
                    if (
                        line
                        and not line.startswith("#")
                        and not line.startswith("{")
                        and not line.startswith("}")
                        and "/" in line
                    ):
                        if not any(
                            keyword in line
                            for keyword in [" ", "\t", "daily", "weekly", "monthly", "yearly", "rotate", "compress"]
                        ):
                            paths.append(line)

                if paths:
                    self.params["paths"] = paths
                else:
                    self.params["paths"] = []
            else:
                self.module.fail_json(
                    msg="Cannot generate configuration: no paths specified and no existing configuration found"
                )

        lines = []

        paths = self.params["paths"]
        if isinstance(paths, str):
            paths = [paths]

        for path in paths:
            lines.append(path)
        lines.append("{")
        lines.append("")

        rotation_period = self.params.get("rotation_period")
        if rotation_period is not None and not self.params.get("size") and not self.params.get("max_size"):
            lines.append(f"    {rotation_period}")

        if self.params.get("size") is not None:
            lines.append(f"    size {self.params['size']}")
        elif self.params.get("max_size") is not None:
            lines.append(f"    maxsize {self.params['max_size']}")

        if self.params.get("min_size") is not None:
            lines.append(f"    minsize {self.params['min_size']}")

        rotate_count = self.params.get("rotate_count")
        if rotate_count is not None:
            lines.append(f"    rotate {rotate_count}")

        start_val = self.params.get("start")
        if start_val is not None:
            lines.append(f"    start {start_val}")

        compress_val = self.params.get("compress")
        if compress_val is not None:
            if compress_val:
                comp_method = self.params.get("compression_method")
                if comp_method is not None and comp_method != "gzip":
                    lines.append(f"    compresscmd /usr/bin/{comp_method}")
                    if comp_method == "zstd":
                        lines.append(f"    uncompresscmd /usr/bin/{comp_method} -d")
                    elif comp_method == "lz4":
                        lines.append(f"    uncompresscmd /usr/bin/{comp_method} -d")
                    else:
                        lines.append(f"    uncompresscmd /usr/bin/{comp_method}un{comp_method}")
                    lines.append(f"    compressext .{comp_method}")
                lines.append("    compress")

                if self.params.get("compress_options") is not None:
                    lines.append(f"    compressoptions {self.params['compress_options']}")
            else:
                lines.append("    nocompress")

        delay_compress_val = self.params.get("delay_compress")
        if delay_compress_val is not None:
            if delay_compress_val:
                lines.append("    delaycompress")

        no_delay_compress_val = self.params.get("no_delay_compress")
        if no_delay_compress_val is not None:
            if no_delay_compress_val:
                lines.append("    nodelaycompress")

        shred_val = self.params.get("shred")
        if shred_val is not None and shred_val:
            lines.append("    shred")
            shred_cycles_val = self.params.get("shred_cycles")
            if shred_cycles_val is not None:
                lines.append(f"    shredcycles {shred_cycles_val}")

        missing_ok_val = self.params.get("missing_ok")
        if missing_ok_val is not None:
            if not missing_ok_val:
                lines.append("    nomissingok")
            else:
                lines.append("    missingok")

        not_if_empty_val = self.params.get("not_if_empty")
        if not_if_empty_val is not None:
            if not_if_empty_val:
                lines.append("    notifempty")
            else:
                lines.append("    ifempty")

        create_val = self.params.get("create")
        if create_val is not None:
            lines.append(f"    create {create_val}")

        copy_val = self.params.get("copy")
        rename_copy_val = self.params.get("rename_copy")
        copy_truncate_val = self.params.get("copy_truncate")

        if copy_val is not None and copy_val:
            lines.append("    copy")
        elif rename_copy_val is not None and rename_copy_val:
            lines.append("    renamecopy")
        elif copy_truncate_val is not None and copy_truncate_val:
            lines.append("    copytruncate")

        if self.params.get("max_age") is not None:
            lines.append(f"    maxage {self.params['max_age']}")

        date_ext_val = self.params.get("date_ext")
        if date_ext_val is not None and date_ext_val:
            lines.append("    dateext")
            date_yesterday_val = self.params.get("date_yesterday")
            if date_yesterday_val is not None and date_yesterday_val:
                lines.append("    dateyesterday")
            date_format_val = self.params.get("date_format")
            if date_format_val is not None:
                lines.append(f"    dateformat {date_format_val}")

        shared_scripts_val = self.params.get("shared_scripts")
        if shared_scripts_val is not None and shared_scripts_val:
            lines.append("    sharedscripts")

        su_val = self.params.get("su")
        if su_val is not None:
            if su_val != "":
                lines.append(f"    su {su_val}")

        no_old_dir_val = self.params.get("no_old_dir")
        old_dir_val = self.params.get("old_dir")

        if no_old_dir_val is not None and no_old_dir_val:
            lines.append("    noolddir")
        elif old_dir_val is not None:
            lines.append(f"    olddir {old_dir_val}")
            create_old_dir_val = self.params.get("create_old_dir")
            if create_old_dir_val is not None and create_old_dir_val:
                lines.append("    createolddir")

        if self.params.get("extension") is not None:
            lines.append(f"    extension {self.params['extension']}")

        mail_val = self.params.get("mail")
        if mail_val is not None:
            lines.append(f"    mail {mail_val}")
            mail_first_val = self.params.get("mail_first")
            mail_last_val = self.params.get("mail_last")
            if mail_first_val is not None and mail_first_val:
                lines.append("    mailfirst")
            elif mail_last_val is not None and mail_last_val:
                lines.append("    maillast")

        if self.params.get("include") is not None:
            lines.append(f"    include {self.params['include']}")

        if self.params.get("taboo_ext") is not None:
            taboo_ext = self.params["taboo_ext"]
            if isinstance(taboo_ext, list):
                taboo_ext = " ".join(taboo_ext)
            if taboo_ext.strip():
                lines.append(f"    tabooext {taboo_ext}")

        syslog_val = self.params.get("syslog")
        if syslog_val is not None and syslog_val:
            lines.append("    syslog")

        scripts = {
            "prerotate": self.params.get("pre_rotate"),
            "postrotate": self.params.get("post_rotate"),
            "firstaction": self.params.get("first_action"),
            "lastaction": self.params.get("last_action"),
            "preremove": self.params.get("pre_remove"),
        }

        for script_name, script_content in scripts.items():
            if script_content is not None:
                lines.append(f"    {script_name}")
                for command in script_content:
                    for line in command.strip().split("\n"):
                        if line.strip():
                            lines.append(f"        {line}")
                lines.append("    endscript")
                lines.append("")

        lines.append("}")

        return "\n".join(lines)

    def apply(self) -> dict[str, object]:
        """Apply logrotate configuration."""
        self.validate_parameters()
        state = self.params["state"]

        if not os.path.exists(self.config_dir):
            self.module.fail_json(
                msg=f"Config directory '{self.config_dir}' does not exist. "
                f"Please create it manually or ensure the correct path is specified."
            )

        if state == "absent":
            for suffix in ["", self.disabled_suffix]:
                config_path = os.path.join(self.config_dir, self.config_name + suffix)
                if os.path.exists(config_path):
                    if not self.module.check_mode:
                        os.remove(config_path)
                    self.result["changed"] = True
                    self.result["config_file"] = config_path
                    break
            return self.result

        existing_content = self.read_existing_config(any_state=True)
        current_enabled = self.result.get("enabled_state", True)

        target_enabled = self.params.get("enabled")
        if target_enabled is None:
            target_enabled = current_enabled

        only_changing_enabled = (
            existing_content is not None and not self.params.get("paths") and target_enabled != current_enabled
        )

        if only_changing_enabled:
            old_path = self.get_config_path(not target_enabled)
            new_path = self.get_config_path(target_enabled)

            if os.path.exists(old_path) and not os.path.exists(new_path):
                self.result["changed"] = True
                if not self.module.check_mode:
                    self.module.atomic_move(old_path, new_path, unsafe_writes=False)

                self.result["config_file"] = new_path
                self.result["enabled_state"] = target_enabled

                try:
                    with open(new_path, "r") as f:
                        self.result["config_content"] = f.read()
                except Exception:
                    self.result["config_content"] = existing_content

                return self.result

        new_content = self.generate_config_content()
        self.result["config_content"] = new_content
        self.result["config_file"] = self.get_config_path(target_enabled)

        needs_update = existing_content is None or existing_content != new_content or target_enabled != current_enabled

        if needs_update:
            if not self.module.check_mode:
                for suffix in ["", self.disabled_suffix]:
                    old_path = os.path.join(self.config_dir, self.config_name + suffix)
                    if os.path.exists(old_path):
                        backup_path = self.module.backup_local(old_path)
                        if backup_path:
                            self.result["backup_file"] = backup_path
                        os.remove(old_path)

                config_file_path = str(self.result["config_file"])
                try:
                    with open(config_file_path, "w") as f:
                        f.write(new_content)
                    os.chmod(config_file_path, 0o644)
                except Exception as e:
                    self.module.fail_json(msg=f"Failed to write config file {config_file_path}: {to_native(e)}")

                test_cmd = [self.logrotate_bin, "-d", config_file_path]
                rc, stdout, stderr = self.module.run_command(test_cmd)
                if rc != 0:
                    self.module.fail_json(
                        msg="logrotate configuration test failed",
                        stderr=stderr,
                        stdout=stdout,
                        config_file=config_file_path,
                    )

        self.result["changed"] = needs_update
        self.result["enabled_state"] = target_enabled
        return self.result


def main() -> None:
    """Main function."""
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="str", required=True, aliases=["config_name"]),
            state=dict(type="str", choices=["present", "absent"]),
            config_dir=dict(type="path"),
            paths=dict(type="list", elements="path"),
            rotation_period=dict(
                type="str",
                choices=["daily", "weekly", "monthly", "yearly"],
            ),
            rotate_count=dict(type="int"),
            compress=dict(type="bool"),
            compress_options=dict(type="str"),
            compression_method=dict(
                type="str",
                choices=["gzip", "bzip2", "xz", "zstd", "lzma", "lz4"],
            ),
            delay_compress=dict(type="bool"),
            no_delay_compress=dict(type="bool"),
            shred=dict(type="bool"),
            shred_cycles=dict(type="int"),
            missing_ok=dict(type="bool"),
            not_if_empty=dict(type="bool"),
            create=dict(type="str"),
            copy_truncate=dict(type="bool"),
            copy=dict(type="bool"),
            rename_copy=dict(type="bool"),
            size=dict(type="str"),
            min_size=dict(type="str"),
            max_size=dict(type="str"),
            max_age=dict(type="int"),
            date_ext=dict(type="bool"),
            date_yesterday=dict(type="bool"),
            date_format=dict(type="str"),
            shared_scripts=dict(type="bool"),
            pre_rotate=dict(type="list", elements="str"),
            post_rotate=dict(type="list", elements="str"),
            first_action=dict(type="list", elements="str"),
            last_action=dict(type="list", elements="str"),
            pre_remove=dict(type="list", elements="str"),
            su=dict(type="str"),
            old_dir=dict(type="path"),
            create_old_dir=dict(type="bool"),
            no_old_dir=dict(type="bool"),
            extension=dict(type="str"),
            mail=dict(type="str"),
            mail_first=dict(type="bool"),
            mail_last=dict(type="bool"),
            include=dict(type="path"),
            taboo_ext=dict(type="list", elements="str"),
            enabled=dict(type="bool"),
            start=dict(type="int"),
            syslog=dict(type="bool"),
        ),
        mutually_exclusive=[
            ["delay_compress", "no_delay_compress"],
            ["old_dir", "no_old_dir"],
            ["size", "max_size"],
            ["copy", "copy_truncate", "rename_copy"],
        ],
        supports_check_mode=True,
    )

    logrotate_bin = module.get_bin_path("logrotate", required=True)

    logrotate_config = LogrotateConfig(module, logrotate_bin)
    result = logrotate_config.apply()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
