..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_cmdrunner:

Command Runner guide
====================

Introduction
^^^^^^^^^^^^

The ``ansible_collections.community.general.plugins.module_utils.cmd_runner`` module util provides the
``CmdRunner`` class to help execute external commands. The class provides standard mechanisms around
the standard ``AnsibleModule.run_command()`` method, handling: command arguments, localization setting,
output processing output, check mode, and other features.

It is even more useful when one command is used in multiple modules, so that you can define all options
in a module util file, and each module will use the same runner with different arguments.

For the sake of clarity, throughout this guide, unless otherwise specified, we use the term *option* when referring to
Ansible module options, and the term *argument* when referring to the command line arguments for the external command.

Quickstart
""""""""""

A ``CmdRunner`` basically defines a command to be executed, and a set of coded instructions on how to format
the command-line arguments, in which specific order, for that particular command. There are other features like
automatic check of the command's exit code, forcing a specific localization encoding and environment variables.

It relies on ``ansible.module_utils.basic.AnsibleModule.run_command()`` to execute the command.

To use ``CmdRunner`` you must start by creating the ``CmdRunner`` object. The example below is a simplified
version of the actual code in ``ansible_collections.community.general.plugins.modules.ansible_galaxy_install``:

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
        )
    )

This is meant to be done once, then every time you need to execute the command you create a context and pass values as needed:

.. code-block:: python

        # Run the command with these arguments, when values exist for them
        with runner("type galaxy_cmd upgrade force no_deps dest requirements_file name", output_process=process) as ctx:
            ctx.run(galaxy_cmd="install", upgrade=upgrade)

        # Obtain the version
        with runner("version") as ctx:
            dummy, stdout, dummy = ctx.run()

        # Or simply
        dummy, stdout, dummy = runner("version").run()

Note that you can pass values for the arguments explicitly when calling ``run()``, otherwise ``CmdRunner`` will use the module
options with the exact same names as values for the runner arguments. If no value is passed and no module option is found
with the specified name, then an exception will be raised. The only exception to that rule is when using ``cmd_runner_fmt.as_fixed``,
as with the argument ``version`` in the runner above. See more about it below.

In the first example, values of ``type``, ``force``, ``no_deps`` and others will be taken straight from the module, whilst
``galaxy_cmd`` and ``upgrade`` are passed explicitly.

That will generate a resulting command line similar to (example taken from the output of an integration test):

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

Argument formats
^^^^^^^^^^^^^^^^

As seen in the example, ``CmdRunner`` expects a parameter named ``arg_formats`` defining how to format each CLI named argument.
An "argument format" is nothing but a function to transform the value of a variable into something formatted for the command line.


Argument format function
""""""""""""""""""""""""

An ``arg_format`` function should of the form:

.. code-block:: python

    def func(value):
        return ["--some-param-name", value]

The parameter ``value`` can be of any type - although there are convenience mechanisms
to help handling sequence and mapping objects.

The result is expected to be of the type ``Sequence[str]`` type (most commonly ``list[str]`` or ``tuple[str]``), otherwise
it will be considered to be a ``str``, and it will be coerced into ``list[str]``. This resulting sequence of strings will be added
to the command line when that argument is actually used.

For example, if ``func`` returns:

- ``["nee", 2, "shruberries"]``, the command line will include arguments ``"nee" "2" "shruberries"``.
- ``2 == 2``, the command line will include argument ``True``.
- ``None``, the command line will include argument ``None``.
- ``[]``, the command line will not include argument anything for that particular argument.

Convenience format functions
""""""""""""""""""""""""""""

Command Runner provides a set of convenience functions that return format arguments functions for commom
cases. In the first block of code in the `Quickstart`_ section you can see the ``from .. import`` of
``ansible_collections.community.general.plugins.module_utils.cmd_runner.cmd_runner_fmt``, and how to make
use of many these convenience functions in the instantiation of the ``CmdRunner`` object.

Unless noted otherwise, for the sake of consistency in the reference below it is assumed that every convenience function deals
with two parameters: ``arg``, usually specified during the creation of the ``CmdRunner`` object, and ``value``, specified
during the execution of the command.

+---------------+-----------------------+--------------------------------------+
| as_list()                                                                    |
+===============+=======================+======================================+
| Description   | Does not accept ``arg``, returns ``value`` as-is.            |
+---------------+-----------------------+--------------------------------------+
| Creation      | ``as_list()``                                                |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``["foo", "bar"]``  | * ``["foo", "bar"]``                 |
|               | * ``"foobar"``        | * ``["foobar"]``                     |
+---------------+-----------------------+--------------------------------------+

+---------------+-----------------------+--------------------------------------+
| as_bool()                                                                    |
+===============+=======================+======================================+
| Description   | It receives two different parameters: ``args_true`` and      |
|               | ``args_false``, which is optional. If ``value`` is           |
|               | ``True``-ish, the format function will return ``args_true``  |
|               | and, when ``args_false`` is passed, ``args_false`` will be   |
|               | returned when ``value`` is ``False``-ish.                    |
+---------------+-----------------------+--------------------------------------+
| Creation      | ``as_bool("--force")``                                       |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``True``            | * ``["--force"]``                    |
|               | * ``False``           | * ``[]``                             |
+---------------+-----------------------+--------------------------------------+

+---------------+--------------------------------------------------------------+
| as_bool_not()                                                                |
+===============+==============================================================+
| Description   | Returns ``arg`` when ``value`` is ``False``-ish.             |
+---------------+--------------------------------------------------------------+
| Creation      | ``as_bool_not("--no-deps")``                                 |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``True``            | * ``[]``                             |
|               | * ``False``           | * ``["--no-deps"]``                  |
+---------------+-----------------------+--------------------------------------+

+---------------+-----------------------+--------------------------------------+
| as_optval()                                                                  |
+===============+==============================================================+
| Description   | Concatenates ``arg`` and ``value`` as one string.            |
+---------------+--------------------------------------------------------------+
| Creation      | ``as_optval("-i")``                                          |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``3``               | * ``["-i3"]``                        |
|               | * ``foobar``          | * ``["-ifoobar"]``                   |
+---------------+-----------------------+--------------------------------------+

+---------------+-----------------------+--------------------------------------+
| as_opt_val()                                                                 |
+===============+==============================================================+
| Description   | Concatenates ``arg`` and ``value`` as one list.              |
+---------------+--------------------------------------------------------------+
| Creation      | ``as_opt_val("--name")``                                     |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``abc``             | * ``["--name", "abc"]``              |
+---------------+-----------------------+--------------------------------------+

+---------------+-----------------------+--------------------------------------+
| as_opt_eq_val()                                                              |
+===============+==============================================================+
| Description   | Concatenates ``arg=value`` as one string.                    |
+---------------+--------------------------------------------------------------+
| Creation      | ``as_opt_eq_val("--num-cpus")``                              |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``10``              | * ``["--num-cpus=10"]``              |
+---------------+-----------------------+--------------------------------------+

+---------------+-----------------------+---------------------------------------+
| as_fixed()                                                                    |
+===============+===============================================================+
| Description   | Fixed arguments added regardless of value.                    |
+---------------+---------------------------------------------------------------+
| Creation      | ``as_fixed("--version")``                                     |
+---------------+-----------------------+---------------------------------------+
| Value/Outcome |                       | * ``["--version"]``                   |
+---------------+-----------------------+---------------------------------------+
| Note          | This is the only special case in which a value can be missing.|
|               | The example also comes from the code in `Quickstart`_.        |
|               | In that case, the module has code to determine the command's  |
|               | version so that it can assert compatibility. There is no      |
|               | *value* to be passed for that CLI argument.                   |
+---------------+---------------------------------------------------------------+

+---------------+-----------------------+--------------------------------------+
| as_map()                                                                     |
+===============+==============================================================+
| Description   | Requires ``arg`` to be a dictionay from which it chooses the |
|               | resulting command line argument.                             |
+---------------+--------------------------------------------------------------+
| Creation      | ``as_map(dict(a=1, b=2, c=3), default=42)``                  |
+---------------+-----------------------+--------------------------------------+
| Value/Outcome | * ``"b"``             | * ``["2"]``                          |
|               | * ``"yabadabadoo"``   | * ``["42"]``                         |
+---------------+-----------------------+--------------------------------------+
| Note          | If ``default`` is not specified, invalid values will return  |
|               | an empty list, meaning they will be silently ignored.        |
+---------------+--------------------------------------------------------------+

+---------------+----------------------------------------------------------------------------------+
| as_func()                                                                                        |
+===============+==================================================================================+
| Description   | In this case ``arg`` itself is a format function. It must                        |
|               | abide by the rules described above.                                              |
+---------------+----------------------------------------------------------------------------------+
| Creation      | ``as_func(lambda v: [] if v == 'stable' else ['--channel', '{0}'.format(v)])``   |
+---------------+----------------------------------------------------------------------------------+
| Note          | The outcome for that depends entirely on the function provided by the developer. |
+---------------+----------------------------------------------------------------------------------+

Other features for argument formatting
""""""""""""""""""""""""""""""""""""""

Some additional features are available as decorators:

- ``cmd_runner_fmt.unpack args()``

  This decorator unpacks the incoming ``value`` as a list of elements.

  For example, in P(community.general.puppet,module_utils), it is used as:

  .. code-block:: python

        @cmd_runner_fmt.unpack_args
        def execute_func(execute, manifest):
            if execute:
                return ["--execute", execute]
            else:
                return [manifest]

        runner = CmdRunner(
            module,
            command=_prepare_base_cmd(),
            path_prefix=_PUPPET_PATH_PREFIX,
            arg_formats=dict(
                # ...
                _execute=cmd_runner_fmt.as_func(execute_func),
                # ...
            ),
        )

  Then, in M(community.general.puppet) it is put to use with:

  .. code-block:: python

        with runner(args_order) as ctx:
            rc, stdout, stderr = ctx.run(_execute=[p['execute'], p['manifest']])

- ``cmd_runner_fmt.unpack_kwargs()``

  Conversely, this decorator unpacks the incoming ``value`` as a ``dict``-like object.

- ``cmd_runner_fmt.stack()``

  This decorator will assume ``value`` is a sequence and will concatenate the output
  of the wrapped function applied to each element of the sequence.

  For example, in M(community.general.django_check), the database argument format
  is defined as:

  .. code-block:: python

        arg_formats = dict(
            database=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--database"),

  When receiving a list ``["abc", "def"]``, the output will be:

  .. code-block:: python

        ["--database", "abc", "--database", "def"]


Command Runner
^^^^^^^^^^^^^^

lang
environment
check_rc

Python Runner
^^^^^^^^^^^^^

Other features
^^^^^^^^^^^^^^

Processing results
^^^^^^^^^^^^^^^^^^



.. versionadded:: 6.1.0
