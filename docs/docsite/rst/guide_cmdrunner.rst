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
the standard ``AnsibleModule.run_command()`` method, handling command arguments, localization setting,
output processing output, check mode, and other features.

It is even more useful when one command is used in multiple modules, so that you can define all options
in a module util file, and each module uses the same runner with different arguments.

For the sake of clarity, throughout this guide, unless otherwise specified, we use the term *option* when referring to
Ansible module options, and the term *argument* when referring to the command line arguments for the external command.


Quickstart
""""""""""

``CmdRunner`` defines a command and a set of coded instructions on how to format
the command-line arguments, in which specific order, for a particular execution.
It relies on ``ansible.module_utils.basic.AnsibleModule.run_command()`` to actually execute the command.
There are other features, see more details throughout this document.

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

        # version is fixed, requires no value
        with runner("version") as ctx:
            dummy, stdout, dummy = ctx.run()

        # passes arg 'data' to AnsibleModule.run_command()
        with runner("type name", data=stdin_data) as ctx:
            dummy, stdout, dummy = ctx.run()

        # Another way of expressing it
        dummy, stdout, dummy = runner("version").run()

Note that you can pass values for the arguments when calling ``run()``, otherwise ``CmdRunner``
uses the module options with the exact same names to provide values for the runner arguments.
If no value is passed and no module option is found for the name specified, then an exception is raised, unless
the argument is using ``cmd_runner_fmt.as_fixed`` as format function like the ``version`` in the example above.
See more about it below.

In the first example, values of ``type``, ``force``, ``no_deps`` and others
are taken straight from the module, whilst ``galaxy_cmd`` and ``upgrade`` are
passed explicitly.

.. note::

    It is not possible to automatically retrieve values of suboptions.

That generates a resulting command line similar to (example taken from the
output of an integration test):

.. code-block:: python

        [
            "<venv>/bin/ansible-galaxy",
            "collection",
            "install",
            "--upgrade",
            "-p",
            "<collection-install-path>",
            "netbox.netbox",
        ]


Argument formats
^^^^^^^^^^^^^^^^

As seen in the example, ``CmdRunner`` expects a parameter named ``arg_formats``
defining how to format each CLI named argument.
An "argument format" is nothing but a function to transform the value of a variable
into something formatted for the command line.


Argument format function
""""""""""""""""""""""""

An ``arg_format`` function is defined in the form similar to:

.. code-block:: python

    def func(value):
        return ["--some-param-name", value]

The parameter ``value`` can be of any type - although there are convenience
mechanisms to help handling sequence and mapping objects.

The result is expected to be of the type ``Sequence[str]`` type (most commonly
``list[str]`` or ``tuple[str]``), otherwise it is considered to be a ``str``,
and it is coerced into ``list[str]``.
This resulting sequence of strings is added to the command line when that
argument is actually used.

For example, if ``func`` returns:

- ``["nee", 2, "shruberries"]``, the command line adds arguments ``"nee" "2" "shruberries"``.
- ``2 == 2``, the command line adds argument ``True``.
- ``None``, the command line adds argument ``None``.
- ``[]``, the command line adds no command line argument for that particular argument.


Convenience format methods
""""""""""""""""""""""""""

In the same module as ``CmdRunner`` there is a class ``cmd_runner_fmt`` which
provides a set of convenience methods that return format functions for common cases.
In the first block of code in the `Quickstart`_ section you can see the importing of
that class:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.cmd_runner import CmdRunner, cmd_runner_fmt

The same example shows how to make use of some of them in the instantiation of the ``CmdRunner`` object.
A description of each one of the convenience methods available and examples of how to use them is found below.
In these descriptions ``value`` refers to the single parameter passed to the formatting function.

- ``cmd_runner_fmt.as_list()``
    This method does not receive any parameter, function returns ``value`` as-is.

    - Creation:
        ``cmd_runner_fmt.as_list()``
    - Examples:
        +----------------------+---------------------+
        | Value                | Outcome             |
        +======================+=====================+
        | ``["foo", "bar"]``   | ``["foo", "bar"]``  |
        +----------------------+---------------------+
        | ``"foobar"``         | ``["foobar"]``      |
        +----------------------+---------------------+

- ``cmd_runner_fmt.as_bool()``
    This method receives two different parameters: ``args_true`` and ``args_false``, latter being optional.
    If the boolean evaluation of ``value`` is ``True``, the format function returns ``args_true``.
    If the boolean evaluation is ``False``, then the function returns ``args_false`` if it was provided, or ``[]`` otherwise.

    - Creation (one arg):
        ``cmd_runner_fmt.as_bool("--force")``
    - Examples:
        +------------+--------------------+
        | Value      | Outcome            |
        +============+====================+
        | ``True``   | ``["--force"]``    |
        +------------+--------------------+
        | ``False``  | ``[]``             |
        +------------+--------------------+
    - Creation (two args, ``None`` treated as ``False``):
        ``cmd_runner_fmt.as_bool("--relax", "--dont-do-it")``
    - Examples:
        +------------+----------------------+
        | Value      | Outcome              |
        +============+======================+
        | ``True``   | ``["--relax"]``      |
        +------------+----------------------+
        | ``False``  | ``["--dont-do-it"]`` |
        +------------+----------------------+
        |            | ``["--dont-do-it"]`` |
        +------------+----------------------+
    - Creation (two args, ``None`` is ignored):
        ``cmd_runner_fmt.as_bool("--relax", "--dont-do-it", ignore_none=True)``
    - Examples:
        +------------+----------------------+
        | Value      | Outcome              |
        +============+======================+
        | ``True``   | ``["--relax"]``      |
        +------------+----------------------+
        | ``False``  | ``["--dont-do-it"]`` |
        +------------+----------------------+
        |            | ``[]``               |
        +------------+----------------------+

- ``cmd_runner_fmt.as_bool_not()``
    This method receives one parameter, which is returned by the function when the boolean evaluation
    of ``value`` is ``False``.

    - Creation:
        ``cmd_runner_fmt.as_bool_not("--no-deps")``
    - Examples:
        +-------------+---------------------+
        | Value       | Outcome             |
        +=============+=====================+
        | ``True``    | ``[]``              |
        +-------------+---------------------+
        | ``False``   | ``["--no-deps"]``   |
        +-------------+---------------------+

- ``cmd_runner_fmt.as_optval()``
    This method receives one parameter ``arg``, the function returns the string concatenation
    of ``arg`` and ``value``.

    - Creation:
        ``cmd_runner_fmt.as_optval("-i")``
    - Examples:
        +---------------+---------------------+
        | Value         | Outcome             |
        +===============+=====================+
        | ``3``         | ``["-i3"]``         |
        +---------------+---------------------+
        | ``foobar``    | ``["-ifoobar"]``    |
        +---------------+---------------------+

- ``cmd_runner_fmt.as_opt_val()``
    This method receives one parameter ``arg``, the function returns ``[arg, value]``.

    - Creation:
        ``cmd_runner_fmt.as_opt_val("--name")``
    - Examples:
        +--------------+--------------------------+
        | Value        | Outcome                  |
        +==============+==========================+
        | ``abc``      | ``["--name", "abc"]``    |
        +--------------+--------------------------+

- ``cmd_runner_fmt.as_opt_eq_val()``
    This method receives one parameter ``arg``, the function returns the string of the form
    ``{arg}={value}``.

    - Creation:
        ``cmd_runner_fmt.as_opt_eq_val("--num-cpus")``
    - Examples:
        +------------+-------------------------+
        | Value      | Outcome                 |
        +============+=========================+
        | ``10``     | ``["--num-cpus=10"]``   |
        +------------+-------------------------+

- ``cmd_runner_fmt.as_fixed()``
    This method defines one or more fixed arguments that are returned by the generated function
    regardless whether ``value`` is passed to it or not.

    This method accepts these arguments in one of three forms:

        * one scalar parameter ``arg``, which will be returned as ``[arg]`` by the function, or
        * one sequence parameter, such as a list, ``arg``, which will be returned by the function as ``arg[0]``, or
        * multiple parameters ``args``, which will be returned as ``args`` directly by the function.

    See the examples below for each one of those forms. And, stressing that the generated function expects no ``value`` - if one
    is provided then it is ignored.

    - Creation (one scalar argument):
        * ``cmd_runner_fmt.as_fixed("--version")``
    - Examples:
        +---------+--------------------------------------+
        | Value   | Outcome                              |
        +=========+======================================+
        |         | * ``["--version"]``                  |
        +---------+--------------------------------------+
        | 57      | * ``["--version"]``                  |
        +---------+--------------------------------------+

    - Creation (one sequence argument):
        * ``cmd_runner_fmt.as_fixed(["--list", "--json"])``
    - Examples:
        +---------+--------------------------------------+
        | Value   | Outcome                              |
        +=========+======================================+
        |         | * ``["--list", "--json"]``           |
        +---------+--------------------------------------+
        | True    | * ``["--list", "--json"]``           |
        +---------+--------------------------------------+

    - Creation (multiple arguments):
        * ``cmd_runner_fmt.as_fixed("--one", "--two", "--three")``
    - Examples:
        +---------+--------------------------------------+
        | Value   | Outcome                              |
        +=========+======================================+
        |         | * ``["--one", "--two", "--three"]``  |
        +---------+--------------------------------------+
        | False   | * ``["--one", "--two", "--three"]``  |
        +---------+--------------------------------------+

    - Note:
        This is the only special case in which a value can be missing for the formatting function.
        The first example here comes from the code in `Quickstart`_.
        In that case, the module has code to determine the command's version so that it can assert compatibility.
        There is no *value* to be passed for that CLI argument.

- ``cmd_runner_fmt.as_map()``
    This method receives one parameter ``arg`` which must be a dictionary, and an optional parameter ``default``.
    The function returns the evaluation of ``arg[value]``.
    If ``value not in arg``, then it returns ``default`` if defined, otherwise ``[]``.

    - Creation:
        ``cmd_runner_fmt.as_map(dict(a=1, b=2, c=3), default=42)``
    - Examples:
        +---------------------+---------------+
        | Value               | Outcome       |
        +=====================+===============+
        | ``"b"``             | ``["2"]``     |
        +---------------------+---------------+
        | ``"yabadabadoo"``   | ``["42"]``    |
        +---------------------+---------------+

    - Note:
        If ``default`` is not specified, invalid values return an empty list, meaning they are silently ignored.

- ``cmd_runner_fmt.as_func()``
    This method receives one parameter ``arg`` which is itself is a format function and it must abide by the rules described above.

    - Creation:
        ``cmd_runner_fmt.as_func(lambda v: [] if v == 'stable' else ['--channel', '{0}'.format(v)])``
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
    This decorator assumes ``value`` is a sequence and concatenates the output
    of the wrapped function applied to each element of the sequence.

    For example, in :ansplugin:`community.general.django_check#module`, the argument format for ``database``
    is defined as:

    .. code-block:: python

          arg_formats = dict(
              # ...
              database=cmd_runner_fmt.stack(cmd_runner_fmt.as_opt_val)("--database"),
              # ...
          )

    When receiving a list ``["abc", "def"]``, the output is:

    .. code-block:: python

          ["--database", "abc", "--database", "def"]


Command Runner
^^^^^^^^^^^^^^

Settings that can be passed to the ``CmdRunner`` constructor are:

- ``module: AnsibleModule``
    Module instance. Mandatory parameter.
- ``command: str | list[str]``
    Command to be executed. It can be a single string, the executable name, or a list
    of strings containing the executable name as the first element and, optionally, fixed parameters.
    Those parameters are used in all executions of the runner.
    The *executable* pointed by this parameter (whether itself when ``str`` or its first element when ``list``) is
    processed using ``AnsibleModule.get_bin_path()`` *unless* it is an absolute path or contains the character ``/``.
- ``arg_formats: dict``
    Mapping of argument names to formatting functions.
- ``default_args_order: str``
    As the name suggests, a default ordering for the arguments. When
    this is passed, the context can be created without specifying ``args_order``. Defaults to ``()``.
- ``check_rc: bool``
    When ``True``, if the return code from the command is not zero, the module exits
    with an error. Defaults to ``False``.
- ``path_prefix: list[str]``
    If the command being executed is installed in a non-standard directory path,
    additional paths might be provided to search for the executable. Defaults to ``None``.
- ``environ_update: dict``
    Pass additional environment variables to be set during the command execution.
    Defaults to ``None``.
- ``force_lang: str``
    It is usually important to force the locale to one specific value, so that responses are consistent and, therefore, parseable.
    Please note that using this option (which is enabled by default) overwrites the environment variables ``LANGUAGE`` and ``LC_ALL``.
    To disable this mechanism, set this parameter to ``None``.
    In community.general 9.1.0 a special value ``auto`` was introduced for this parameter, with the effect
    that ``CmdRunner`` then tries to determine the best parseable locale for the runtime.
    It should become the default value in the future, but for the time being the default value is ``C``.

When creating a context, the additional settings that can be passed to the call are:

- ``args_order: str``
    Establishes the order in which the arguments are rendered in the command line.
    This parameter is mandatory unless ``default_args_order`` was provided to the runner instance.
- ``output_process: func``
    Function to transform the output of the executable into different values or formats.
    See examples in section below.
- ``check_mode_skip: bool``
    Whether to skip the actual execution of the command when the module is in check mode.
    Defaults to ``False``.
- ``check_mode_return: any``
    If ``check_mode_skip=True``, then return this value instead.
- valid named arguments to ``AnsibleModule.run_command()``
    Other than ``args``, any valid argument to ``run_command()`` can be passed when setting up the run context.
    For example, ``data`` can be used to send information to the command's standard input.
    Or ``cwd`` can be used to run the command inside a specific working directory.

Additionally, any other valid parameters for ``AnsibleModule.run_command()`` may be passed, but unexpected behavior
might occur if redefining options already present in the runner or its context creation. Use with caution.


Processing results
^^^^^^^^^^^^^^^^^^

As mentioned, ``CmdRunner`` uses ``AnsibleModule.run_command()`` to execute the external command,
and it passes the return value from that method back to caller. That means that,
by default, the result is going to be a tuple ``(rc, stdout, stderr)``.

If you need to transform or process that output, you can pass a function to the context,
as the ``output_process`` parameter. It must be a function like:

.. code-block:: python

    def process(rc, stdout, stderr):
        # do some magic
        return processed_value    # whatever that is

In that case, the return of ``run()`` is the ``processed_value`` returned by the function.


PythonRunner
^^^^^^^^^^^^

The ``PythonRunner`` class is a specialized version of ``CmdRunner``, geared towards the execution of
Python scripts. It features two extra and  mutually exclusive parameters ``python`` and ``venv`` in its constructor:

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

You may provide the value of the ``command`` argument as a string (in that case the string is used as a script name)
or as a list, in which case the elements of the list must be valid arguments for the Python interpreter, as in the example above.
See `Command line and environment <https://docs.python.org/3/using/cmdline.html>`_ for more details.

If the parameter ``python`` is an absolute path, or contains directory separators, such as ``/``, then it is used
as-is, otherwise the runtime ``PATH`` is searched for that command name.

Other than that, everything else works as in ``CmdRunner``.

.. versionadded:: 4.8.0
