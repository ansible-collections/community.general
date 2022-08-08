..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

Paths
-----

The ``path_join`` filter has been added in ansible-base 2.10. If you want to use this filter, but also need to support Ansible 2.9, you can use ``community.general``'s ``path_join`` shim, ``community.general.path_join``. This filter redirects to ``path_join`` for ansible-base 2.10 and ansible-core 2.11 or newer, and re-implements the filter for Ansible 2.9.

.. code-block:: yaml+jinja

    # ansible-base 2.10 or newer:
    path: {{ ('/etc', path, 'subdir', file) | path_join }}

    # Also works with Ansible 2.9:
    path: {{ ('/etc', path, 'subdir', file) | community.general.path_join }}

.. versionadded:: 3.0.0
