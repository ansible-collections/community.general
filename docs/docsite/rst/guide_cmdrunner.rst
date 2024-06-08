..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_cmdrunner:

``CmdRunner`` Guide
===================

Introduction
^^^^^^^^^^^^

The ``ansible_collections.community.general.plugins.module_utils.cmd_runner`` module util provides the
``CmdRunner`` class to help execute external commands. The class provides standard mechanisms to handle:
the command arguments, the localization setting, processing the output, check mode, etc.

This is even more useful when one command is used in multiple modules, so that you can define all options
in a module util file, and each module will then only use the ones that make sense to it.

Quickstart
""""""""""

The simplest way of using ``CmdRunner`` is (this is a simplified example based on
``ansible_collections.community.general.plugins.modules.ansible_galaxy_install``):

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

    runner = CmdRunner(
        module,
        command="ansible-galaxy",
        arg_formats=dict(
            type=cmd_runner_fmt.as_func(lambda v: [] if v == 'both' else [v]),
            galaxy_cmd=cmd_runner_fmt.as_list(),
            upgrade=cmd_runner_fmt.as_bool("--upgrade"),
            requirements_file=cmd_runner_fmt.as_opt_val('-r'),
            dest=cmd_runner_fmt.as_opt_val('-p'),
            force=cmd_runner_fmt.as_bool("--force"),
            no_deps=cmd_runner_fmt.as_bool("--no-deps"),
            version=cmd_runner_fmt.as_fixed("--version"),
            name=cmd_runner_fmt.as_list(),
        ),
        check_rc=True
    )

Then later in the code, you can write something like:

.. code-block:: python

        with self.runner("type galaxy_cmd upgrade force no_deps dest requirements_file name", output_process=process) as ctx:
            ctx.run(galaxy_cmd="install", upgrade=upgrade)

That will generate a resulting command line similar to (again, taken from the output of an integration test):

.. code-block:: javascript

        [
            "<venv>/bin/ansible-galaxy",
            "collection",
            "install",
            "--upgrade",
            "-p",
            "<collection-install-path>",
            "netbox.netbox"
        ]

Argument Formats
^^^^^^^^^^^^^^^^

As seen in the example, ``CmdRunner`` expects a parameter named ``arg_formats`` defining how to format each CLI named argument. 



Command Runner
^^^^^^^^^^^^^^

Python Runner
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

.. versionadded:: 6.1.0
