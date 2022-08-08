..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Working with times
------------------

The ``to_time_unit`` filter allows to convert times from a human-readable string to a unit. For example, ``'4h 30min 12second' | community.general.to_time_unit('hour')`` gives the number of hours that correspond to 4 hours, 30 minutes and 12 seconds.

There are shorthands to directly convert to various units, like ``to_hours``, ``to_minutes``, ``to_seconds``, and so on. The following table lists all units that can be used:

.. list-table:: Units
   :widths: 25 25 25 25
   :header-rows: 1

   * - Unit name
     - Unit value in seconds
     - Unit strings for filter
     - Shorthand filter
   * - Millisecond
     - 1/1000 second
     - ``ms``, ``millisecond``, ``milliseconds``, ``msec``, ``msecs``, ``msecond``, ``mseconds``
     - ``to_milliseconds``
   * - Second
     - 1 second
     - ``s``, ``sec``, ``secs``, ``second``, ``seconds``
     - ``to_seconds``
   * - Minute
     - 60 seconds
     - ``m``, ``min``, ``mins``, ``minute``, ``minutes``
     - ``to_minutes``
   * - Hour
     - 60*60 seconds
     - ``h``, ``hour``, ``hours``
     - ``to_hours``
   * - Day
     - 24*60*60 seconds
     - ``d``, ``day``, ``days``
     - ``to_days``
   * - Week
     - 7*24*60*60 seconds
     - ``w``, ``week``, ``weeks``
     - ``to_weeks``
   * - Month
     - 30*24*60*60 seconds
     - ``mo``, ``month``, ``months``
     - ``to_months``
   * - Year
     - 365*24*60*60 seconds
     - ``y``, ``year``, ``years``
     - ``to_years``

Note that months and years are using a simplified representation: a month is 30 days, and a year is 365 days. If you need different definitions of months or years, you can pass them as keyword arguments. For example, if you want a year to be 365.25 days, and a month to be 30.5 days, you can write ``'11months 4' | community.general.to_years(year=365.25, month=30.5)``. These keyword arguments can be specified to ``to_time_unit`` and to all shorthand filters.

.. code-block:: yaml+jinja

    - name: Convert string to seconds
      debug:
        msg: "{{ '30h 20m 10s 123ms' | community.general.to_time_unit('seconds') }}"

    - name: Convert string to hours
      debug:
        msg: "{{ '30h 20m 10s 123ms' | community.general.to_hours }}"

    - name: Convert string to years (using 365.25 days == 1 year)
      debug:
        msg: "{{ '400d 15h' | community.general.to_years(year=365.25) }}"

This produces:

.. code-block:: ansible-output

    TASK [Convert string to seconds] **********************************************************
    ok: [localhost] => {
        "msg": "109210.123"
    }

    TASK [Convert string to hours] ************************************************************
    ok: [localhost] => {
        "msg": "30.336145277778"
    }

    TASK [Convert string to years (using 365.25 days == 1 year)] ******************************
    ok: [localhost] => {
        "msg": "1.096851471595"
    }

.. versionadded: 0.2.0
