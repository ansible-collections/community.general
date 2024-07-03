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
``CmdRunner`` class to help execute external commands. The class is a wrapper around
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

To use ``CmdRunner`` you must start by creating an object. The example below is a simplified
version of the actual code in :ansplugin:`community.general.ansible_galaxy_install#module`:

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

An ``arg_format`` function should be of the form:

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

- ``cmd_runner_fmt.as_list()``
    Does not accept ``arg``, returns ``value`` as-is.

    - Creation:
        ``cmd_runner_fmt.as_list()``
    - Example:
        +----------------------+---------------------+
        | Value                | Outcome             |
        +======================+=====================+
        | ``["foo", "bar"]``   | ``["foo", "bar"]``  |
        +----------------------+---------------------+
        | ``"foobar"``         | ``["foobar"]``      |
        +----------------------+---------------------+

- ``cmd_runner_fmt.as_bool()``
    It receives two different parameters: ``args_true`` and ``args_false``, which is optional. If the boolean
    evaluation of ``value`` is ``True``, the format function will return ``args_true`` and, when ``args_false``
    is passed, ``args_false`` will be returned when ``value`` evaluates to ``False``.

    - Creation:
        ``cmd_runner_fmt.as_bool("--force")``
    - Example:
        +------------+--------------------+
        | Value      | Outcome            |
        +============+====================+
        | ``True``   | ``["--force"]``    |
        +------------+--------------------+
        | ``False``  | ``[]``             |
        +------------+--------------------+

- ``cmd_runner_fmt.as_bool_not()``
    Returns ``arg`` when ``value`` is ``False``-ish.

    - Creation:
        ``cmd_runner_fmt.as_bool_not("--no-deps")``
    - Example:
        +-------------+---------------------+
        | Value       | Outcome             |
        +=============+=====================+
        | ``True``    | ``[]``              |
        +-------------+---------------------+
        | ``False``   | ``["--no-deps"]``   |
        +-------------+---------------------+

- ``cmd_runner_fmt.as_optval()``
    Concatenates ``arg`` and ``value`` as one string.

    - Creation:
        ``cmd_runner_fmt.as_optval("-i")``
    - Example:
        +---------------+---------------------+
        | Value         | Outcome             |
        +===============+=====================+
        | ``3``         | ``["-i3"]``         |
        +---------------+---------------------+
        | ``foobar``    | ``["-ifoobar"]``    |
        +---------------+---------------------+

- ``cmd_runner_fmt.as_opt_val()``
    Concatenates ``arg`` and ``value`` as one list.

    - Creation:
        ``cmd_runner_fmt.as_opt_val("--name")``
    - Example:
        +--------------+--------------------------+
        | Value        | Outcome                  |
        +==============+==========================+
        | ``abc``      | ``["--name", "abc"]``    |
        +--------------+--------------------------+

- ``cmd_runner_fmt.as_opt_eq_val()``
    Concatenates ``arg=value`` as one string.

    - Creation:
        ``cmd_runner_fmt.as_opt_eq_val("--num-cpus")``
    - Example:
        +------------+-------------------------+
        | Value      | Outcome                 |
        +============+=========================+
        | ``10``     | ``["--num-cpus=10"]``   |
        +------------+-------------------------+

- ``cmd_runner_fmt.as_fixed()``
    Fixed arguments added regardless of value.

    - Creation:
        ``cmd_runner_fmt.as_fixed("--version")``
    - Example:
        +---------+-----------------------+
        | Value   | Outcome               |
        +=========+=======================+
        |         | ``["--version"]``     |
        +---------+-----------------------+

    - Note:
        This is the only special case in which a value can be missing. The example also comes from
        the code in `Quickstart`_. In that case, the module has code to determine the command's
        version so that it can assert compatibility. There is no *value* to be passed for that CLI argument.

- ``cmd_runner_fmt.as_map()``
    Requires ``arg`` to be a dictionay from which it chooses the resulting command line argument.

    - Creation:
        ``cmd_runner_fmt.as_map(dict(a=1, b=2, c=3), default=42)``
    - Example:
        +---------------------+---------------+
        | Value               | Outcome       |
        +=====================+===============+
        | ``"b"``             | ``["2"]``     |
        +---------------------+---------------+
        | ``"yabadabadoo"``   | ``["42"]``    |
        +---------------------+---------------+

    - Note:
        If ``default`` is not specified, invalid values will return an empty list, meaning they will be silently ignored.

- ``cmd_runner_fmt.as_func()``
    In this case ``arg`` itself is a format function. It must abide by the rules described above.

    - Creation: ``cmd_runner_fmt.as_func(lambda v: [] if v == 'stable' else ['--channel', '{0}'.format(v)])``
    - Example:
    - Note:
        The outcome for that depends entirely on the function provided by the developer.


Other features for argument formatting
""""""""""""""""""""""""""""""""""""""

Some additional features are available as decorators:

- ``cmd_runner_fmt.unpack args()``
    This decorator unpacks the incoming ``value`` as a list of elements.

    For example, in ``ansible_collections.community.general.plugins.module_utils.puppet``, it is used as:

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

    Then, in :ansplugin:`community.general.puppet#module` it is put to use with:

    .. code-block:: python

          with runner(args_order) as ctx:
              rc, stdout, stderr = ctx.run(_execute=[p['execute'], p['manifest']])

- ``cmd_runner_fmt.unpack_kwargs()``
    Conversely, this decorator unpacks the incoming ``value`` as a ``dict``-like object.

- ``cmd_runner_fmt.stack()``
    This decorator will assume ``value`` is a sequence and will concatenate the output
    of the wrapped function applied to each element of the sequence.

    For example, in :ansplugin:`community.general.django_check#module`, the argument format for ``database``
    is defined as:

    .. code-block:: python

          arg_formats = dict(
              database=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--database"),

    When receiving a list ``["abc", "def"]``, the output will be:

    .. code-block:: python

          ["--database", "abc", "--database", "def"]


Command Runner
^^^^^^^^^^^^^^

Settings that can be passed to the ``CmdRunner`` constructor are:

- ``module: AnsibleModule``
    Module instance. Mandatory parameter.
- ``command: str | list[str]``
    Command to be executed. It can be a single string, the executable name, or a list
    of strings containing the executable name as the first element and fixed parameters. Those parameters
    will be used in all executions of the runner.
- ``arg_formats: dict``
    Mapping of argument names to formatting functions.
- ``default_args_order: str``
    As the name suggests, a default ordering for the arguments. When
    this is passed, the context can be created without specifying ``args_order``. Defaults to ``()``.
- ``check_rc: bool``
    When ``True``, if the return code from the command is not zero, the module will exit
    with an error. Defaults to ``False``.
- ``path_prefix: list[str]``
    If the command being executed is installed in a non-standard directory path,
    additional paths might be provided to search for the executable. Defaults to ``None``.
- ``environ_update: dict``
    Pass additional environment variables to be set during the command execution.
    Defaults to ``None``.
- ``force_lang: str``
    Most of the times, it will be important to force the locale to one specific
    value, so that responses are consistent and, therefore, parseable. Please note that using this option (which
    is enabled by default) overwrites the environment variables ``LANGUAGE`` and ``LC_ALL``.
    To disable this mechanism, set this parameter to ``None``.
    In community.general 9.1.0 it was introduced a special value ``auto`` for this parameter, which will
    try to determine the best parseable locale for the runtime. It should become the default value in the
    future, but for the time being the default value is ``C``.

When creating a context, the additional settings that can be passed to the call are:

- ``args_order: str``
    Established the order in which the arguments will be rendered in the command line.
    This parameter is mandatory unless ``default_args_order`` was provided to the runner instance.
- ``output_process: func``
    Function to transform the output of the executable into different values or formats.
    See examples in section below.
- ``check_mode_skip: bool``
    Whether to skip the actual execution of the command when the module is in check mode.
    Defaults to ``False``.
- ``check_mode_return: any``
    If ``check_mode_skip=True``, then return this value instead.

Additionally, any other valid parameters for ``AnsibleModule.run_command()`` may be passed, but unexpected behavior
might occur if redefining options already present in the runner or its context creation. Use with caution.


Processing results
^^^^^^^^^^^^^^^^^^


PythonRunner
^^^^^^^^^^^^

The ``PythonRunner```class is a specialized version of ``CmdRunner``, geared towards the execution of
Python scripts. It feature two mutually exclusive extra parameters ``python`` and  ``venv`` in its constructor:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.python_runner import PythonRunner
    from ansible_collections.community.general.plugins.module_utils.cmd_runner import cmd_runner_fmt

    runner = PythonRunner(
        module,
        command=["-m", "django"],
        arg_formats=dict(...),
        python="python",
        venv="/path/to/some/venv",
    )

The default value for ``python`` is the string ``python``, and the for ``venv`` it is ``None``.

The command line produced by such a command with ``python="python3.12"`` is something like:

.. code-block:: shell

    /usr/bin/python3.12 -m django <arg1> <arg2> ...

And the command line for ``venv="/work/venv"`` is like:

.. code-block:: shell

    /work/venv/bin/python -m django <arg1> <arg2> ...

You may provide the value of the ``command`` argument as a string (in that case the string will be used as a script name)
or as a list, in which case the elements of the list must be valid arguments for the Python interpreter, as in the example above.
See `<https://docs.python.org/3/using/cmdline.html>` for more details.

If the parameter ``python```is an absolute path, or contains directory separators, such as ``/```, then it will be used
as-is, otherwise the runtime ``PATH`` will be searched for that command name.

Other than that, everything else works as in ``CmdRunner``.

Other features
^^^^^^^^^^^^^^




.. versionadded:: 6.1.0
