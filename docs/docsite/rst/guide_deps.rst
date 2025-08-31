..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_deps:

``deps`` Guide
==============


Using ``deps``
^^^^^^^^^^^^^^

The ``ansible_collections.community.general.plugins.module_utils.deps`` module util simplifies
the importing of code as described in :ref:`Importing and using shared code <shared_code>`.
Please notice that ``deps`` is meant to be used specifically with Ansible modules, and not other types of plugins.

The same example from the Developer Guide would become:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils import deps


    with deps.declare("foo"):
        import foo

Then in ``main()``, just after the argspec (or anywhere in the code, for that matter), do

.. code-block:: python

    deps.validate(module)  # assuming module is a valid AnsibleModule instance

By default, ``deps`` will rely on ``ansible.module_utils.basic.missing_required_lib`` to generate
a message about a failing import. That function accepts parameters ``reason`` and ``url``, and
and so does ``deps```:

.. code-block:: python

    with deps.declare("foo", reason="foo is needed to properly bar", url="https://foo.bar.io"):
        import foo

If you would rather write a custom message instead of using ``missing_required_lib`` then do:

.. code-block:: python

    with deps.declare("foo", msg="Custom msg explaining why foo is needed"):
        import foo

``deps`` allows for multiple dependencies to be declared:

.. code-block:: python

    with deps.declare("foo"):
        import foo

    with deps.declare("bar"):
        import bar

    with deps.declare("doe"):
        import doe

By default, ``deps.validate()`` will check on all the declared dependencies, but if so desired,
they can be validated selectively by doing:

.. code-block:: python

    deps.validate(module, "foo")       # only validates the "foo" dependency

    deps.validate(module, "doe:bar")   # only validates the "doe" and "bar" dependencies

    deps.validate(module, "-doe:bar")  # validates all dependencies except "doe" and "bar"

.. versionadded:: 6.1.0
