# -*- coding: utf-8 -*-

# Copyright (c) 2024, kurokobo <kurokobo@protonmail.com>
# Copyright (c) 2014, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
  name: timestamp
  type: stdout
  short_description: Adds simple timestamp for each header
  version_added: 9.0.0
  description:
    - This callback adds simple timestamp for each header.
  author: kurokobo (@kurokobo)
  options:
    timezone:
      description:
        - Timezone to use for the timestamp in IANA time zone format.
        - For example C(America/New_York), C(Asia/Tokyo)). Ignored on Python < 3.9.
      ini:
        - section: callback_timestamp
          key: timezone
      env:
        - name: ANSIBLE_CALLBACK_TIMESTAMP_TIMEZONE
      type: string
    format_string:
      description:
        - Format of the timestamp shown to user in 1989 C standard format.
        - >
          Refer to L(the Python documentation,https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes)
          for the available format codes.
      ini:
        - section: callback_timestamp
          key: format_string
      env:
        - name: ANSIBLE_CALLBACK_TIMESTAMP_FORMAT_STRING
      default: "%H:%M:%S"
      type: string
  seealso:
    - plugin: ansible.posix.profile_tasks
      plugin_type: callback
      description: >
        You can use P(ansible.posix.profile_tasks#callback) callback plugin to time individual tasks and overall execution time
        with detailed timestamps.
  extends_documentation_fragment:
    - ansible.builtin.default_callback
    - ansible.builtin.result_format_callback
"""


from ansible.plugins.callback.default import CallbackModule as Default
from ansible.utils.display import get_text_width
from ansible.module_utils.common.text.converters import to_text
from datetime import datetime
import types
import sys

# Store whether the zoneinfo module is available
_ZONEINFO_AVAILABLE = sys.version_info >= (3, 9)


def get_datetime_now(tz):
    """
    Returns the current timestamp with the specified timezone
    """
    return datetime.now(tz=tz)


def banner(self, msg, color=None, cows=True):
    """
    Prints a header-looking line with cowsay or stars with length depending on terminal width (3 minimum) with trailing timestamp

    Based on the banner method of Display class from ansible.utils.display

    https://github.com/ansible/ansible/blob/4403519afe89138042108e237aef317fd5f09c33/lib/ansible/utils/display.py#L511
    """
    timestamp = get_datetime_now(self.timestamp_tzinfo).strftime(self.timestamp_format_string)
    timestamp_len = get_text_width(timestamp) + 1  # +1 for leading space

    msg = to_text(msg)
    if self.b_cowsay and cows:
        try:
            self.banner_cowsay("%s @ %s" % (msg, timestamp))
            return
        except OSError:
            self.warning("somebody cleverly deleted cowsay or something during the PB run.  heh.")

    msg = msg.strip()
    try:
        star_len = self.columns - get_text_width(msg) - timestamp_len
    except EnvironmentError:
        star_len = self.columns - len(msg) - timestamp_len
    if star_len <= 3:
        star_len = 3
    stars = "*" * star_len
    self.display("\n%s %s %s" % (msg, stars, timestamp), color=color)


class CallbackModule(Default):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = "stdout"
    CALLBACK_NAME = "community.general.timestamp"

    def __init__(self):
        super(CallbackModule, self).__init__()

        # Replace the banner method of the display object with the custom one
        self._display.banner = types.MethodType(banner, self._display)

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        # Store zoneinfo for specified timezone if available
        tzinfo = None
        if _ZONEINFO_AVAILABLE and self.get_option("timezone"):
            from zoneinfo import ZoneInfo

            tzinfo = ZoneInfo(self.get_option("timezone"))

        # Inject options into the display object
        setattr(self._display, "timestamp_tzinfo", tzinfo)
        setattr(self._display, "timestamp_format_string", self.get_option("format_string"))
