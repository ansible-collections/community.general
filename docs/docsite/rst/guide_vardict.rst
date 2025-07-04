..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_vardict:

VarDict Guide
=============

Introduction
^^^^^^^^^^^^

The ``ansible_collections.community.general.plugins.module_utils.vardict`` module util provides the
``VarDict`` class to help manage the module variables. That class is a container for module variables,
especially the ones for which the module must keep track of state changes, and the ones that should
be published as return values.

Each variable has extra behaviors controlled by associated metadata, simplifying the generation of
output values from the module.

Quickstart
""""""""""

The simplest way of using ``VarDict`` is:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.vardict import VarDict

Then in ``main()``, or any other function called from there:

.. code-block:: python

    vars = VarDict()

    # Next 3 statements are equivalent
    vars.abc = 123
    vars["abc"] = 123
    vars.set("abc", 123)

    vars.xyz = "bananas"
    vars.ghi = False

And by the time the module is about to exit:

.. code-block:: python

    results = vars.output()
    module.exit_json(**results)

That makes the return value of the module:

.. code-block:: json

    {
        "abc": 123,
        "xyz": "bananas",
        "ghi": false
    }

Metadata
""""""""

The metadata values associated with each variable are:

- ``output: bool`` - marks the variable for module output as a module return value.
- ``fact: bool`` - marks the variable for module output as an Ansible fact.
- ``verbosity: int`` - sets the minimum level of verbosity for which the variable will be included in the output.
- ``change: bool`` - controls the detection of changes in the variable value.
- ``initial_value: any`` - when using ``change`` and need to forcefully set an intial value to the variable.
- ``diff: bool`` - used along with ``change``, this generates an Ansible-style diff ``dict``.

See the sections below for more details on how to use the metadata.


Using VarDict
^^^^^^^^^^^^^

Basic Usage
"""""""""""

As shown above, variables can be accessed using the ``[]`` operator, as in a ``dict`` object,
and also as an object attribute, such as ``vars.abc``. The form using the ``set()``
method is special in the sense that you can use it to set metadata values:

.. code-block:: python

    vars.set("abc", 123, output=False)
    vars.set("abc", 123, output=True, change=True)

Another way to set metadata after the variables have been created is:

.. code-block:: python

    vars.set_meta("abc", output=False)
    vars.set_meta("abc", output=True, change=True, diff=True)

You can use either operator and attribute forms to access the value of the variable. Other ways to
access its value and its metadata are:

.. code-block:: python

    print("abc value = {0}".format(vars.var("abc")["value"]))        # get the value
    print("abc output? {0}".format(vars.get_meta("abc")["output"]))  # get the metadata like this

The names of methods, such as ``set``, ``get_meta``, ``output`` amongst others, are reserved and
cannot be used as variable names. If you try to use a reserved name a ``ValueError`` exception
is raised with the message "Name <var> is reserved".

Generating output
"""""""""""""""""

By default, every variable create will be enable for output with minimum verbosity set to zero, in
other words, they will always be in the output by default.

You can control that when creating the variable for the first time or later in the code:

.. code-block:: python

    vars.set("internal", x + 4, output=False)
    vars.set_meta("internal", output=False)

You can also set the verbosity of some variable, like:

.. code-block:: python

    vars.set("abc", x + 4)
    vars.set("debug_x", x, verbosity=3)

    results = vars.output(module._verbosity)
    module.exit_json(**results)

If the module was invoked with verbosity lower than 3, then the output will only contain
the variable ``abc``. If running at higher verbosity, as in ``ansible-playbook -vvv``,
then the output will also contain ``debug_x``.

Generating facts is very similar to regular output, but variables are not marked as facts by default.

.. code-block:: python

    vars.set("modulefact", x + 4, fact=True)
    vars.set("debugfact", x, fact=True, verbosity=3)

    results = vars.output(module._verbosity)
    results["ansible_facts"] = {"module_name": vars.facts(module._verbosity)}
    module.exit_json(**results)

Handling change
"""""""""""""""

You can use ``VarDict`` to determine whether variables have had their values changed.

.. code-block:: python

    vars.set("abc", 42, change=True)
    vars.abc = 90

    results = vars.output()
    results["changed"] = vars.has_changed
    module.exit_json(**results)

If tracking changes in variables, you may want to present the difference between the initial and the final
values of it. For that, you want to use:

.. code-block:: python

    vars.set("abc", 42, change=True, diff=True)
    vars.abc = 90

    results = vars.output()
    results["changed"] = vars.has_changed
    results["diff"] = vars.diff()
    module.exit_json(**results)

.. versionadded:: 7.1.0
