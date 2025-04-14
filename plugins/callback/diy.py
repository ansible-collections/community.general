# -*- coding: utf-8 -*-

# Copyright (c) 2019, Trevor Highfill <trevor.highfill@outlook.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

DOCUMENTATION = r"""
name: diy
type: stdout
short_description: Customize the output
version_added: 0.2.0
description:
  - Callback plugin that allows you to supply your own custom callback templates to be output.
author: Trevor Highfill (@theque5t)
extends_documentation_fragment:
  - default_callback
notes:
  - Uses the P(ansible.builtin.default#callback) callback plugin output when a custom callback V(message(msg\)) is not provided.
  - Makes the callback event data available using the C(ansible_callback_diy) dictionary, which can be used in the templating
    context for the options. The dictionary is only available in the templating context for the options. It is not a variable
    that is available using the other various execution contexts, such as playbook, play, task, and so on so forth.
  - Options being set by their respective variable input can only be set using the variable if the variable was set in a context
    that is available to the respective callback. Use the C(ansible_callback_diy) dictionary to see what is available to a
    callback. Additionally, C(ansible_callback_diy.top_level_var_names) will output the top level variable names available
    to the callback.
  - Each option value is rendered as a template before being evaluated. This allows for the dynamic usage of an option. For
    example, C("{{ 'yellow' if ansible_callback_diy.result.is_changed else 'bright green' }}").
  - 'B(Condition) for all C(msg) options: if value C(is None or omit), then the option is not being used. B(Effect): use
    of the C(default) callback plugin for output.'
  - 'B(Condition) for all C(msg) options: if value C(is not None and not omit and length is not greater than 0), then the
    option is being used without output. B(Effect): suppress output.'
  - 'B(Condition) for all C(msg) options: if value C(is not None and not omit and length is greater than 0), then the option
    is being used with output. B(Effect): render value as template and output.'
  - 'Valid color values: V(black), V(bright gray), V(blue), V(white), V(green), V(bright blue), V(cyan), V(bright green),
    V(red), V(bright cyan), V(purple), V(bright red), V(yellow), V(bright purple), V(dark gray), V(bright yellow), V(magenta),
    V(bright magenta), V(normal).'
seealso:
  - name: default – default Ansible screen output
    description: The official documentation on the B(default) callback plugin.
    link: https://docs.ansible.com/ansible/latest/plugins/callback/default.html
requirements:
  - set as stdout_callback in configuration
options:
  on_any_msg:
    description: Output to be used for callback on_any.
    ini:
      - section: callback_diy
        key: on_any_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_ON_ANY_MSG
    vars:
      - name: ansible_callback_diy_on_any_msg
    type: str

  on_any_msg_color:
    description:
      - Output color to be used for O(on_any_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: on_any_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_ON_ANY_MSG_COLOR
    vars:
      - name: ansible_callback_diy_on_any_msg_color
    type: str

  runner_on_failed_msg:
    description: Output to be used for callback runner_on_failed.
    ini:
      - section: callback_diy
        key: runner_on_failed_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_FAILED_MSG
    vars:
      - name: ansible_callback_diy_runner_on_failed_msg
    type: str

  runner_on_failed_msg_color:
    description:
      - Output color to be used for O(runner_on_failed_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_failed_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_FAILED_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_failed_msg_color
    type: str

  runner_on_ok_msg:
    description: Output to be used for callback runner_on_ok.
    ini:
      - section: callback_diy
        key: runner_on_ok_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_OK_MSG
    vars:
      - name: ansible_callback_diy_runner_on_ok_msg
    type: str

  runner_on_ok_msg_color:
    description:
      - Output color to be used for O(runner_on_ok_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_ok_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_OK_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_ok_msg_color
    type: str

  runner_on_skipped_msg:
    description: Output to be used for callback runner_on_skipped.
    ini:
      - section: callback_diy
        key: runner_on_skipped_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_SKIPPED_MSG
    vars:
      - name: ansible_callback_diy_runner_on_skipped_msg
    type: str

  runner_on_skipped_msg_color:
    description:
      - Output color to be used for O(runner_on_skipped_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_skipped_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_SKIPPED_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_skipped_msg_color
    type: str

  runner_on_unreachable_msg:
    description: Output to be used for callback runner_on_unreachable.
    ini:
      - section: callback_diy
        key: runner_on_unreachable_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_UNREACHABLE_MSG
    vars:
      - name: ansible_callback_diy_runner_on_unreachable_msg
    type: str

  runner_on_unreachable_msg_color:
    description:
      - Output color to be used for O(runner_on_unreachable_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_unreachable_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_UNREACHABLE_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_unreachable_msg_color
    type: str

  playbook_on_start_msg:
    description: Output to be used for callback playbook_on_start.
    ini:
      - section: callback_diy
        key: playbook_on_start_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_START_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_start_msg
    type: str

  playbook_on_start_msg_color:
    description:
      - Output color to be used for O(playbook_on_start_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_start_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_START_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_start_msg_color
    type: str

  playbook_on_notify_msg:
    description: Output to be used for callback playbook_on_notify.
    ini:
      - section: callback_diy
        key: playbook_on_notify_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NOTIFY_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_notify_msg
    type: str

  playbook_on_notify_msg_color:
    description:
      - Output color to be used for O(playbook_on_notify_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_notify_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NOTIFY_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_notify_msg_color
    type: str

  playbook_on_no_hosts_matched_msg:
    description: Output to be used for callback playbook_on_no_hosts_matched.
    ini:
      - section: callback_diy
        key: playbook_on_no_hosts_matched_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NO_HOSTS_MATCHED_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_no_hosts_matched_msg
    type: str

  playbook_on_no_hosts_matched_msg_color:
    description:
      - Output color to be used for O(playbook_on_no_hosts_matched_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_no_hosts_matched_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NO_HOSTS_MATCHED_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_no_hosts_matched_msg_color
    type: str

  playbook_on_no_hosts_remaining_msg:
    description: Output to be used for callback playbook_on_no_hosts_remaining.
    ini:
      - section: callback_diy
        key: playbook_on_no_hosts_remaining_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NO_HOSTS_REMAINING_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_no_hosts_remaining_msg
    type: str

  playbook_on_no_hosts_remaining_msg_color:
    description:
      - Output color to be used for O(playbook_on_no_hosts_remaining_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_no_hosts_remaining_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_NO_HOSTS_REMAINING_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_no_hosts_remaining_msg_color
    type: str

  playbook_on_task_start_msg:
    description: Output to be used for callback playbook_on_task_start.
    ini:
      - section: callback_diy
        key: playbook_on_task_start_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_TASK_START_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_task_start_msg
    type: str

  playbook_on_task_start_msg_color:
    description:
      - Output color to be used for O(playbook_on_task_start_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_task_start_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_TASK_START_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_task_start_msg_color
    type: str

  playbook_on_handler_task_start_msg:
    description: Output to be used for callback playbook_on_handler_task_start.
    ini:
      - section: callback_diy
        key: playbook_on_handler_task_start_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_HANDLER_TASK_START_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_handler_task_start_msg
    type: str

  playbook_on_handler_task_start_msg_color:
    description:
      - Output color to be used for O(playbook_on_handler_task_start_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_handler_task_start_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_HANDLER_TASK_START_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_handler_task_start_msg_color
    type: str

  playbook_on_vars_prompt_msg:
    description: Output to be used for callback playbook_on_vars_prompt.
    ini:
      - section: callback_diy
        key: playbook_on_vars_prompt_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_VARS_PROMPT_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_vars_prompt_msg
    type: str

  playbook_on_vars_prompt_msg_color:
    description:
      - Output color to be used for O(playbook_on_vars_prompt_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_vars_prompt_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_VARS_PROMPT_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_vars_prompt_msg_color
    type: str

  playbook_on_play_start_msg:
    description: Output to be used for callback playbook_on_play_start.
    ini:
      - section: callback_diy
        key: playbook_on_play_start_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_PLAY_START_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_play_start_msg
    type: str

  playbook_on_play_start_msg_color:
    description:
      - Output color to be used for O(playbook_on_play_start_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_play_start_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_PLAY_START_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_play_start_msg_color
    type: str

  playbook_on_stats_msg:
    description: Output to be used for callback playbook_on_stats.
    ini:
      - section: callback_diy
        key: playbook_on_stats_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_STATS_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_stats_msg
    type: str

  playbook_on_stats_msg_color:
    description:
      - Output color to be used for O(playbook_on_stats_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_stats_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_STATS_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_stats_msg_color
    type: str

  on_file_diff_msg:
    description: Output to be used for callback on_file_diff.
    ini:
      - section: callback_diy
        key: on_file_diff_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_ON_FILE_DIFF_MSG
    vars:
      - name: ansible_callback_diy_on_file_diff_msg
    type: str

  on_file_diff_msg_color:
    description:
      - Output color to be used for O(on_file_diff_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: on_file_diff_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_ON_FILE_DIFF_MSG_COLOR
    vars:
      - name: ansible_callback_diy_on_file_diff_msg_color
    type: str

  playbook_on_include_msg:
    description: Output to be used for callback playbook_on_include.
    ini:
      - section: callback_diy
        key: playbook_on_include_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_INCLUDE_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_include_msg
    type: str

  playbook_on_include_msg_color:
    description:
      - Output color to be used for O(playbook_on_include_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_include_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_INCLUDE_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_include_msg_color
    type: str

  runner_item_on_ok_msg:
    description: Output to be used for callback runner_item_on_ok.
    ini:
      - section: callback_diy
        key: runner_item_on_ok_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_OK_MSG
    vars:
      - name: ansible_callback_diy_runner_item_on_ok_msg
    type: str

  runner_item_on_ok_msg_color:
    description:
      - Output color to be used for O(runner_item_on_ok_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_item_on_ok_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_OK_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_item_on_ok_msg_color
    type: str

  runner_item_on_failed_msg:
    description: Output to be used for callback runner_item_on_failed.
    ini:
      - section: callback_diy
        key: runner_item_on_failed_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_FAILED_MSG
    vars:
      - name: ansible_callback_diy_runner_item_on_failed_msg
    type: str

  runner_item_on_failed_msg_color:
    description:
      - Output color to be used for O(runner_item_on_failed_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_item_on_failed_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_FAILED_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_item_on_failed_msg_color
    type: str

  runner_item_on_skipped_msg:
    description: Output to be used for callback runner_item_on_skipped.
    ini:
      - section: callback_diy
        key: runner_item_on_skipped_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_SKIPPED_MSG
    vars:
      - name: ansible_callback_diy_runner_item_on_skipped_msg
    type: str

  runner_item_on_skipped_msg_color:
    description:
      - Output color to be used for O(runner_item_on_skipped_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_item_on_skipped_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ITEM_ON_SKIPPED_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_item_on_skipped_msg_color
    type: str

  runner_retry_msg:
    description: Output to be used for callback runner_retry.
    ini:
      - section: callback_diy
        key: runner_retry_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_RETRY_MSG
    vars:
      - name: ansible_callback_diy_runner_retry_msg
    type: str

  runner_retry_msg_color:
    description:
      - Output color to be used for O(runner_retry_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_retry_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_RETRY_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_retry_msg_color
    type: str

  runner_on_start_msg:
    description: Output to be used for callback runner_on_start.
    ini:
      - section: callback_diy
        key: runner_on_start_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_START_MSG
    vars:
      - name: ansible_callback_diy_runner_on_start_msg
    type: str

  runner_on_start_msg_color:
    description:
      - Output color to be used for O(runner_on_start_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_start_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_START_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_start_msg_color
    type: str

  runner_on_no_hosts_msg:
    description: Output to be used for callback runner_on_no_hosts.
    ini:
      - section: callback_diy
        key: runner_on_no_hosts_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_NO_HOSTS_MSG
    vars:
      - name: ansible_callback_diy_runner_on_no_hosts_msg
    type: str

  runner_on_no_hosts_msg_color:
    description:
      - Output color to be used for O(runner_on_no_hosts_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: runner_on_no_hosts_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_RUNNER_ON_NO_HOSTS_MSG_COLOR
    vars:
      - name: ansible_callback_diy_runner_on_no_hosts_msg_color
    type: str

  playbook_on_setup_msg:
    description: Output to be used for callback playbook_on_setup.
    ini:
      - section: callback_diy
        key: playbook_on_setup_msg
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_SETUP_MSG
    vars:
      - name: ansible_callback_diy_playbook_on_setup_msg
    type: str

  playbook_on_setup_msg_color:
    description:
      - Output color to be used for O(playbook_on_setup_msg).
      - Template should render a L(valid color value,#notes).
    ini:
      - section: callback_diy
        key: playbook_on_setup_msg_color
    env:
      - name: ANSIBLE_CALLBACK_DIY_PLAYBOOK_ON_SETUP_MSG_COLOR
    vars:
      - name: ansible_callback_diy_playbook_on_setup_msg_color
    type: str
"""

EXAMPLES = r"""
ansible.cfg: >
  # Enable plugin
  [defaults]
  stdout_callback=community.general.diy

  [callback_diy]
  # Output when playbook starts
  playbook_on_start_msg="DIY output(via ansible.cfg): playbook example: {{ ansible_callback_diy.playbook.file_name }}"
  playbook_on_start_msg_color=yellow

  # Comment out to allow default plugin output
  # playbook_on_play_start_msg="PLAY: starting play {{ ansible_callback_diy.play.name }}"

  # Accept on_skipped_msg or ansible_callback_diy_runner_on_skipped_msg as input vars
  # If neither are supplied, omit the option
  runner_on_skipped_msg="{{ on_skipped_msg | default(ansible_callback_diy_runner_on_skipped_msg) | default(omit) }}"

  # Newline after every callback
  # on_any_msg='{{ " " | join("\n") }}'

playbook.yml: >-
  ---
  - name: "Default plugin output: play example"
    hosts: localhost
    gather_facts: false
    tasks:
      - name:  Default plugin output
        ansible.builtin.debug:
          msg: default plugin output

  - name: Override from play vars
    hosts: localhost
    gather_facts: false
    vars:
      ansible_connection: local
      green: "\e[0m\e[38;5;82m"
      yellow: "\e[0m\e[38;5;11m"
      bright_purple: "\e[0m\e[38;5;105m"
      cyan: "\e[0m\e[38;5;51m"
      green_bg_black_fg: "\e[0m\e[48;5;40m\e[38;5;232m"
      yellow_bg_black_fg: "\e[0m\e[48;5;226m\e[38;5;232m"
      purple_bg_white_fg: "\e[0m\e[48;5;57m\e[38;5;255m"
      cyan_bg_black_fg: "\e[0m\e[48;5;87m\e[38;5;232m"
      magenta: "\e[38;5;198m"
      white: "\e[0m\e[38;5;255m"
      ansible_callback_diy_playbook_on_play_start_msg: "\n{{green}}DIY output(via play vars): play example: {{magenta}}{{ansible_callback_diy.play.name}}\n\n"
      ansible_callback_diy_playbook_on_task_start_msg: "DIY output(via play vars): task example: {{ ansible_callback_diy.task.name }}"
      ansible_callback_diy_playbook_on_task_start_msg_color: cyan
      ansible_callback_diy_playbook_on_stats_msg: |+2
                CUSTOM STATS
        ==============================
        {% for key in ansible_callback_diy.stats | sort %}
        {% if ansible_callback_diy.stats[key] %}
        {% if key == 'ok' %}
        {% set color_one = lookup('vars','green_bg_black_fg') %}
        {% set prefix = '      ' %}
        {% set suffix = '     ' %}
        {% set color_two = lookup('vars','green') %}
        {% elif key == 'changed' %}
        {% set color_one = lookup('vars','yellow_bg_black_fg') %}
        {% set prefix = '   ' %}
        {% set suffix = '   ' %}
        {% set color_two = lookup('vars','yellow') %}
        {% elif key == 'processed' %}
        {% set color_one = lookup('vars','purple_bg_white_fg') %}
        {% set prefix = '  ' %}
        {% set suffix = '  ' %}
        {% set color_two = lookup('vars','bright_purple') %}
        {% elif key == 'skipped' %}
        {% set color_one = lookup('vars','cyan_bg_black_fg') %}
        {% set prefix = '   ' %}
        {% set suffix = '   ' %}
        {% set color_two = lookup('vars','cyan') %}
        {% else %}
        {% set color_one = "" %}
        {% set prefix = "" %}
        {% set suffix = "" %}
        {% set color_two = "" %}
        {% endif %}
        {{ color_one }}{{ "%s%s%s" | format(prefix,key,suffix) }}{{ color_two }}: {{ ansible_callback_diy.stats[key] | to_nice_yaml }}
        {% endif %}
        {% endfor %}

    tasks:
      - name: Custom banner with default plugin result output
        ansible.builtin.debug:
          msg: "default plugin output: result example"

      - name: Override from task vars
        ansible.builtin.debug:
          msg: "example {{ two }}"
        changed_when: true
        vars:
          white_fg_red_bg: "\e[0m\e[48;5;1m"
          two: "{{ white_fg_red_bg }}    2    "
          ansible_callback_diy_playbook_on_task_start_msg: "\nDIY output(via task vars): task example: {{ ansible_callback_diy.task.name }}"
          ansible_callback_diy_playbook_on_task_start_msg_color: bright magenta
          ansible_callback_diy_runner_on_ok_msg: "DIY output(via task vars): result example: \n{{ ansible_callback_diy.result.output.msg }}\n"
          ansible_callback_diy_runner_on_ok_msg_color: "{{ 'yellow' if ansible_callback_diy.result.is_changed else 'bright green' }}"

      - name: Suppress output
        ansible.builtin.debug:
          msg: i should not be displayed
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: ""
          ansible_callback_diy_runner_on_ok_msg: ""

      - name: Using alias vars (see ansible.cfg)
        ansible.builtin.debug:
          msg:
        when: false
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: ""
          on_skipped_msg: "DIY output(via task vars): skipped example:\n\e[0m\e[38;5;4m\u25b6\u25b6 {{ ansible_callback_diy.result.task.name }}\n"
          on_skipped_msg_color: white

      - name: Just stdout
        ansible.builtin.command: echo some stdout
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: "\n"
          ansible_callback_diy_runner_on_ok_msg: "{{ ansible_callback_diy.result.output.stdout }}\n"

      - name: Multiline output
        ansible.builtin.debug:
          msg: "{{ multiline }}"
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: "\nDIY output(via task vars): task example: {{ ansible_callback_diy.task.name }}"
          multiline: "line\nline\nline"
          ansible_callback_diy_runner_on_ok_msg: |+2
            some
            {{ ansible_callback_diy.result.output.msg }}
            output

          ansible_callback_diy_playbook_on_task_start_msg_color: bright blue

      - name: Indentation
        ansible.builtin.debug:
          msg: "{{ item.msg }}"
        with_items:
          - { indent: 1, msg: one., color: red }
          - { indent: 2, msg: two.., color: yellow }
          - { indent: 3, msg: three..., color: bright yellow }
        vars:
          ansible_callback_diy_runner_item_on_ok_msg: "{{ ansible_callback_diy.result.output.msg | indent(item.indent, True) }}"
          ansible_callback_diy_runner_item_on_ok_msg_color: "{{ item.color }}"
          ansible_callback_diy_runner_on_ok_msg: "GO!!!"
          ansible_callback_diy_runner_on_ok_msg_color: bright green

      - name: Using lookup and template as file
        ansible.builtin.shell: "echo {% raw %}'output from {{ file_name }}'{% endraw %} > {{ file_name }}"
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: "\nDIY output(via task vars): task example: {{ ansible_callback_diy.task.name }}"
          file_name: diy_file_template_example
          ansible_callback_diy_runner_on_ok_msg: "{{ lookup('template', file_name) }}"

      - name: 'Look at top level vars available to the "runner_on_ok" callback'
        ansible.builtin.debug:
          msg: ''
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: "\nDIY output(via task vars): task example: {{ ansible_callback_diy.task.name }}"
          ansible_callback_diy_runner_on_ok_msg: |+2
            {% for var in (ansible_callback_diy.top_level_var_names|reject('match','vars|ansible_callback_diy.*')) | sort %}
            {{ green }}{{ var }}:
              {{ white }}{{ lookup('vars', var) }}

            {% endfor %}
          ansible_callback_diy_runner_on_ok_msg_color: white

      - name: 'Look at event data available to the "runner_on_ok" callback'
        ansible.builtin.debug:
          msg: ''
        vars:
          ansible_callback_diy_playbook_on_task_start_msg: "\nDIY output(via task vars): task example: {{ ansible_callback_diy.task.name }}"
          ansible_callback_diy_runner_on_ok_msg: |+2
            {% for key in ansible_callback_diy | sort %}
            {{ green }}{{ key }}:
              {{ white }}{{ ansible_callback_diy[key] }}

            {% endfor %}
"""

import sys
from contextlib import contextmanager
from ansible.template import Templar
from ansible.vars.manager import VariableManager
from ansible.plugins.callback.default import CallbackModule as Default
from ansible.module_utils.common.text.converters import to_text

try:
    from ansible.template import trust_as_template  # noqa: F401, pylint: disable=unused-import
    SUPPORTS_DATA_TAGGING = True
except ImportError:
    SUPPORTS_DATA_TAGGING = False


class DummyStdout(object):
    def flush(self):
        pass

    def write(self, b):
        pass

    def writelines(self, l):
        pass


class CallbackModule(Default):
    """
    Callback plugin that allows you to supply your own custom callback templates to be output.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'community.general.diy'

    DIY_NS = 'ansible_callback_diy'

    @contextmanager
    def _suppress_stdout(self, enabled):
        saved_stdout = sys.stdout
        if enabled:
            sys.stdout = DummyStdout()
        yield
        sys.stdout = saved_stdout

    def _get_output_specification(self, loader, variables):
        _ret = {}
        _calling_method = sys._getframe(1).f_code.co_name
        _callback_type = (_calling_method[3:] if _calling_method[:3] == "v2_" else _calling_method)
        _callback_options = ['msg', 'msg_color']

        for option in _callback_options:
            _option_name = f'{_callback_type}_{option}'
            _option_template = variables.get(
                f"{self.DIY_NS}_{_option_name}",
                self.get_option(_option_name)
            )
            _ret.update({option: self._template(
                loader=loader,
                template=_option_template,
                variables=variables
            )})

        _ret.update({'vars': variables})

        return _ret

    def _using_diy(self, spec):
        sentinel = object()
        omit = spec['vars'].get('omit', sentinel)
        # With Data Tagging, omit is sentinel
        return (spec['msg'] is not None) and (spec['msg'] != omit or omit is sentinel)

    def _parent_has_callback(self):
        return hasattr(super(CallbackModule, self), sys._getframe(1).f_code.co_name)

    def _template(self, loader, template, variables):
        _templar = Templar(loader=loader, variables=variables)
        return _templar.template(
            template,
            preserve_trailing_newlines=True,
            convert_data=False,
            escape_backslashes=True
        )

    def _output(self, spec, stderr=False):
        _msg = to_text(spec['msg'])
        if len(_msg) > 0:
            self._display.display(msg=_msg, color=spec['msg_color'], stderr=stderr)

    def _get_vars(self, playbook, play=None, host=None, task=None, included_file=None,
                  handler=None, result=None, stats=None, remove_attr_ref_loop=True):
        def _get_value(obj, attr=None, method=None):
            if attr:
                return getattr(obj, attr, getattr(obj, f"_{attr}", None))

            if method:
                _method = getattr(obj, method)
                return _method()

        def _remove_attr_ref_loop(obj, attributes):
            _loop_var = getattr(obj, 'loop_control', None)
            _loop_var = (_loop_var or 'item')

            for attr in attributes:
                if str(_loop_var) in str(_get_value(obj=obj, attr=attr)):
                    attributes.remove(attr)

            return attributes

        class CallbackDIYDict(dict):
            def __deepcopy__(self, memo):
                return self

        _ret = {}

        _variable_manager = VariableManager(loader=playbook.get_loader())

        _all = _variable_manager.get_vars()
        if play:
            _all = play.get_variable_manager().get_vars(
                play=play,
                host=(host if host else getattr(result, '_host', None)),
                task=(handler if handler else task)
            )
        _ret.update(_all)

        _ret.update(_ret.get(self.DIY_NS, {self.DIY_NS: {} if SUPPORTS_DATA_TAGGING else CallbackDIYDict()}))

        _ret[self.DIY_NS].update({'playbook': {}})
        _playbook_attributes = ['entries', 'file_name', 'basedir']

        for attr in _playbook_attributes:
            _ret[self.DIY_NS]['playbook'].update({attr: _get_value(obj=playbook, attr=attr)})

        if play:
            _ret[self.DIY_NS].update({'play': {}})
            _play_attributes = ['any_errors_fatal', 'become', 'become_flags', 'become_method',
                                'become_user', 'check_mode', 'collections', 'connection',
                                'debugger', 'diff', 'environment', 'fact_path', 'finalized',
                                'force_handlers', 'gather_facts', 'gather_subset',
                                'gather_timeout', 'handlers', 'hosts', 'ignore_errors',
                                'ignore_unreachable', 'included_conditional', 'included_path',
                                'max_fail_percentage', 'module_defaults', 'name', 'no_log',
                                'only_tags', 'order', 'port', 'post_tasks', 'pre_tasks',
                                'remote_user', 'removed_hosts', 'roles', 'run_once', 'serial',
                                'skip_tags', 'squashed', 'strategy', 'tags', 'tasks', 'uuid',
                                'validated', 'vars_files', 'vars_prompt']

            for attr in _play_attributes:
                _ret[self.DIY_NS]['play'].update({attr: _get_value(obj=play, attr=attr)})

        if host:
            _ret[self.DIY_NS].update({'host': {}})
            _host_attributes = ['name', 'uuid', 'address', 'implicit']

            for attr in _host_attributes:
                _ret[self.DIY_NS]['host'].update({attr: _get_value(obj=host, attr=attr)})

        if task:
            _ret[self.DIY_NS].update({'task': {}})
            _task_attributes = ['action', 'any_errors_fatal', 'args', 'async', 'async_val',
                                'become', 'become_flags', 'become_method', 'become_user',
                                'changed_when', 'check_mode', 'collections', 'connection',
                                'debugger', 'delay', 'delegate_facts', 'delegate_to', 'diff',
                                'environment', 'failed_when', 'finalized', 'ignore_errors',
                                'ignore_unreachable', 'loop', 'loop_control', 'loop_with',
                                'module_defaults', 'name', 'no_log', 'notify', 'parent', 'poll',
                                'port', 'register', 'remote_user', 'retries', 'role', 'run_once',
                                'squashed', 'tags', 'untagged', 'until', 'uuid', 'validated',
                                'when']

            # remove arguments that reference a loop var because they cause templating issues in
            # callbacks that do not have the loop context(e.g. playbook_on_task_start)
            if task.loop and remove_attr_ref_loop:
                _task_attributes = _remove_attr_ref_loop(obj=task, attributes=_task_attributes)

            for attr in _task_attributes:
                _ret[self.DIY_NS]['task'].update({attr: _get_value(obj=task, attr=attr)})

        if included_file:
            _ret[self.DIY_NS].update({'included_file': {}})
            _included_file_attributes = ['args', 'filename', 'hosts', 'is_role', 'task']

            for attr in _included_file_attributes:
                _ret[self.DIY_NS]['included_file'].update({attr: _get_value(
                    obj=included_file,
                    attr=attr
                )})

        if handler:
            _ret[self.DIY_NS].update({'handler': {}})
            _handler_attributes = ['action', 'any_errors_fatal', 'args', 'async', 'async_val',
                                   'become', 'become_flags', 'become_method', 'become_user',
                                   'changed_when', 'check_mode', 'collections', 'connection',
                                   'debugger', 'delay', 'delegate_facts', 'delegate_to', 'diff',
                                   'environment', 'failed_when', 'finalized', 'ignore_errors',
                                   'ignore_unreachable', 'listen', 'loop', 'loop_control',
                                   'loop_with', 'module_defaults', 'name', 'no_log',
                                   'notified_hosts', 'notify', 'parent', 'poll', 'port',
                                   'register', 'remote_user', 'retries', 'role', 'run_once',
                                   'squashed', 'tags', 'untagged', 'until', 'uuid', 'validated',
                                   'when']

            if handler.loop and remove_attr_ref_loop:
                _handler_attributes = _remove_attr_ref_loop(obj=handler,
                                                            attributes=_handler_attributes)

            for attr in _handler_attributes:
                _ret[self.DIY_NS]['handler'].update({attr: _get_value(obj=handler, attr=attr)})

            _ret[self.DIY_NS]['handler'].update({'is_host_notified': handler.is_host_notified(host)})

        if result:
            _ret[self.DIY_NS].update({'result': {}})
            _result_attributes = ['host', 'task', 'task_name']

            for attr in _result_attributes:
                _ret[self.DIY_NS]['result'].update({attr: _get_value(obj=result, attr=attr)})

            _result_methods = ['is_changed', 'is_failed', 'is_skipped', 'is_unreachable']

            for method in _result_methods:
                _ret[self.DIY_NS]['result'].update({method: _get_value(obj=result, method=method)})

            _ret[self.DIY_NS]['result'].update({'output': getattr(result, '_result', None)})

            _ret.update(result._result)

        if stats:
            _ret[self.DIY_NS].update({'stats': {}})
            _stats_attributes = ['changed', 'custom', 'dark', 'failures', 'ignored',
                                 'ok', 'processed', 'rescued', 'skipped']

            for attr in _stats_attributes:
                _ret[self.DIY_NS]['stats'].update({attr: _get_value(obj=stats, attr=attr)})

        _ret[self.DIY_NS].update({'top_level_var_names': list(_ret.keys())})

        return _ret

    def v2_on_any(self, *args, **kwargs):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._diy_spec['vars']
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_on_any(*args, **kwargs)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec, stderr=(not ignore_errors))

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_on_failed(result, ignore_errors)

    def v2_runner_on_ok(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_on_ok(result)

    def v2_runner_on_skipped(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_on_skipped(result)

    def v2_runner_on_unreachable(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_on_unreachable(result)

    # not implemented as the call to this is not implemented yet
    def v2_runner_on_async_poll(self, result):
        pass

    # not implemented as the call to this is not implemented yet
    def v2_runner_on_async_ok(self, result):
        pass

    # not implemented as the call to this is not implemented yet
    def v2_runner_on_async_failed(self, result):
        pass

    def v2_runner_item_on_ok(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result,
                remove_attr_ref_loop=False
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_item_on_ok(result)

    def v2_runner_item_on_failed(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result,
                remove_attr_ref_loop=False
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_item_on_failed(result)

    def v2_runner_item_on_skipped(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result,
                remove_attr_ref_loop=False
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_item_on_skipped(result)

    def v2_runner_retry(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_retry(result)

    def v2_runner_on_start(self, host, task):
        self._diy_host = host
        self._diy_task = task

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                host=self._diy_host,
                task=self._diy_task
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_runner_on_start(host, task)

    def v2_playbook_on_start(self, playbook):
        self._diy_playbook = playbook
        self._diy_loader = self._diy_playbook.get_loader()

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_start(playbook)

    def v2_playbook_on_notify(self, handler, host):
        self._diy_handler = handler
        self._diy_host = host

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                host=self._diy_host,
                handler=self._diy_handler
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_notify(handler, host)

    def v2_playbook_on_no_hosts_matched(self):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._diy_spec['vars']
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_no_hosts_matched()

    def v2_playbook_on_no_hosts_remaining(self):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._diy_spec['vars']
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_no_hosts_remaining()

    def v2_playbook_on_task_start(self, task, is_conditional):
        self._diy_task = task

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)

    # not implemented as the call to this is not implemented yet
    def v2_playbook_on_cleanup_task_start(self, task):
        pass

    def v2_playbook_on_handler_task_start(self, task):
        self._diy_task = task

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_handler_task_start(task)

    def v2_playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None,
                                   confirm=False, salt_size=None, salt=None, default=None,
                                   unsafe=None):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._diy_spec['vars']
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_vars_prompt(
                    varname, private, prompt, encrypt,
                    confirm, salt_size, salt, default,
                    unsafe
                )

    # not implemented as the call to this is not implemented yet
    def v2_playbook_on_import_for_host(self, result, imported_file):
        pass

    # not implemented as the call to this is not implemented yet
    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        pass

    def v2_playbook_on_play_start(self, play):
        self._diy_play = play

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_play_start(play)

    def v2_playbook_on_stats(self, stats):
        self._diy_stats = stats

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                stats=self._diy_stats
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_stats(stats)

    def v2_playbook_on_include(self, included_file):
        self._diy_included_file = included_file

        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_included_file._task,
                included_file=self._diy_included_file
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_playbook_on_include(included_file)

    def v2_on_file_diff(self, result):
        self._diy_spec = self._get_output_specification(
            loader=self._diy_loader,
            variables=self._get_vars(
                playbook=self._diy_playbook,
                play=self._diy_play,
                task=self._diy_task,
                result=result
            )
        )

        if self._using_diy(spec=self._diy_spec):
            self._output(spec=self._diy_spec)

        if self._parent_has_callback():
            with self._suppress_stdout(enabled=self._using_diy(spec=self._diy_spec)):
                super(CallbackModule, self).v2_on_file_diff(result)
