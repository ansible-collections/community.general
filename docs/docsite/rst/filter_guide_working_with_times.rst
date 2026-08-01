..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Working with times
------------------

The :ansplugin:`community.general.to_time_unit filter <community.general.to_time_unit#filter>` allows to convert times from a human-readable string to a unit. For example, ``'4h 30min 12second' | community.general.to_time_unit('hour')`` gives the number of hours that correspond to 4 hours, 30 minutes and 12 seconds.

There are shorthands to directly convert to various units, like :ansplugin:`community.general.to_hours#filter`, :ansplugin:`community.general.to_minutes#filter`, :ansplugin:`community.general.to_seconds#filter`, and so on. The following table lists all units that can be used:

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
     - :ansplugin:`community.general.to_milliseconds#filter`
   * - Second
     - 1 second
     - ``s``, ``sec``, ``secs``, ``second``, ``seconds``
     - :ansplugin:`community.general.to_seconds#filter`
   * - Minute
     - 60 seconds
     - ``m``, ``min``, ``mins``, ``minute``, ``minutes``
     - :ansplugin:`community.general.to_minutes#filter`
   * - Hour
     - 60*60 seconds
     - ``h``, ``hour``, ``hours``
     - :ansplugin:`community.general.to_hours#filter`
   * - Day
     - 24*60*60 seconds
     - ``d``, ``day``, ``days``
     - :ansplugin:`community.general.to_days#filter`
   * - Week
     - 7*24*60*60 seconds
     - ``w``, ``week``, ``weeks``
     - :ansplugin:`community.general.to_weeks#filter`
   * - Month
     - 30*24*60*60 seconds
     - ``mo``, ``month``, ``months``
     - :ansplugin:`community.general.to_months#filter`
   * - Year
     - 365*24*60*60 seconds
     - ``y``, ``year``, ``years``
     - :ansplugin:`community.general.to_years#filter`

Note that months and years are using a simplified representation: a month is 30 days, and a year is 365 days. If you need different definitions of months or years, you can pass them as keyword arguments. For example, if you want a year to be 365.25 days, and a month to be 30.5 days, you can write ``'11months 4' | community.general.to_years(year=365.25, month=30.5)``. These keyword arguments can be specified to :ansplugin:`community.general.to_time_unit#filter` and to all shorthand filters.

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

.. ansible-output-data::

    variables:
      task:
        previous_code_block: yaml+jinja
    playbook: |-
      - hosts: localhost
        gather_facts: false
        tasks:
          @{{ task | indent(4) }}@

.. code-block:: ansible-output

    TASK [Convert string to seconds] **********************************************************
    ok: [localhost] => {
        "msg": 109210.123
    }

    TASK [Convert string to hours] ************************************************************
    ok: [localhost] => {
        "msg": 30.336145277778
    }

    TASK [Convert string to years (using 365.25 days == 1 year)] ******************************
    ok: [localhost] => {
        "msg": 1.096851471595
    }

.. versionadded: 0.2.0
