..
  Copyright (c) Ansible Project
  GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
  SPDX-License-Identifier: GPL-3.0-or-later

.. _ansible_collections.community.general.docsite.guide_modulehelper:

Module Helper guide
===================


Introduction
^^^^^^^^^^^^

Writing a module for Ansible is largely described in existing documentation.
However, a good part of that is boilerplate code that needs to be repeated every single time.
That is where ``ModuleHelper`` comes to assistance: a lot of that boilerplate code is done.

.. _ansible_collections.community.general.docsite.guide_modulehelper.quickstart:

Quickstart
""""""""""

See the `example from Ansible documentation <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-a-module>`_
written with ``ModuleHelper``.
But bear in mind that it does not showcase all of MH's features:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


    class MyTest(ModuleHelper):
        module = dict(
            argument_spec=dict(
                name=dict(type='str', required=True),
                new=dict(type='bool', required=False, default=False),
            ),
            supports_check_mode=True,
        )

        def __run__(self):
            self.vars.original_message = ''
            self.vars.message = ''
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'
            self.changed = self.vars['new']
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")


    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()


Module Helper
^^^^^^^^^^^^^

Introduction
""""""""""""

``ModuleHelper`` is a wrapper around the standard ``AnsibleModule``, providing extra features and conveniences.
The basic structure of a module using ``ModuleHelper`` is as shown in the
:ref:`ansible_collections.community.general.docsite.guide_modulehelper.quickstart`
section above, but there are more elements that will take part in it.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper


    class MyTest(ModuleHelper):
        # behavior for module paramaters ONLY, see below for further information
        output_params = ()
        change_params = ()
        diff_params = ()
        facts_params = ()

        facts_name = None   # used if generating facts, from parameters or otherwise

        module = dict(
            argument_spec=dict(...),
            # ...
        )

After importing the ``ModuleHelper`` class, you need to declare your own class extending it.

.. seealso::

    There is a variation called ``StateModuleHelper``, which builds on top of the features provided by MH.
    See :ref:`ansible_collections.community.general.docsite.guide_modulehelper.statemh` below for more details.

The easiest way of specifying the module is to create the class variable ``module`` with a dictionary
containing the exact arguments that would be passed as parameters to ``AnsibleModule``.
If you prefer to create the ``AnsibleModule`` object yourself, just assign it to the ``module`` class variable.
MH also accepts a parameter ``module`` in its constructor, if that parameter is used used,
then it will override the class variable. The parameter can either be ``dict`` or ``AnsibleModule`` as well.

Beyond the definition of the module, there are other variables that can be used to control aspects
of MH's behavior. These variables should be set at the very beginning of the class, and their semantics are
explained through this document.

The main logic of MH happens in the ``ModuleHelper.run()`` method, which looks like:

.. code-block:: python

    @module_fails_on_exception
    def run(self):
        self.__init_module__()
        self.__run__()
        self.__quit_module__()
        output = self.output
        if 'failed' not in output:
            output['failed'] = False
        self.module.exit_json(changed=self.has_changed(), **output)

The method ``ModuleHelper.__run__()`` must be implemented by the module and most
modules will be able to perform their actions implementing only that MH method.
However, in some cases, you might want to execute actions before or after the main tasks, in which cases
you should implement ``ModuleHelper.__init_module__()`` and ``ModuleHelper.__quit_module__()`` respectively.

Note that the output comes from ``self.output``, which is a ``@property`` method.
By default, that property will collect all the variables that are marked for output and return them in a dictionary with their values.
Moreover, the default ``self.output`` will also handle Ansible ``facts`` and *diff mode*.
Also note the changed status comes from ``self.has_changed()``, which is usually calculated from variables that are marked
to track changes in their content.

.. seealso::

    More details in sections
    :ref:`ansible_collections.community.general.docsite.guide_modulehelper.paramvaroutput` and
    :ref:`ansible_collections.community.general.docsite.guide_modulehelper.changes` below.

.. seealso::

    See more about the decorator
    :ref:`ansible_collections.community.general.docsite.guide_modulehelper.modulefailsdeco` below.


Another way to write the example from the
:ref:`ansible_collections.community.general.docsite.guide_modulehelper.quickstart`
would be:

.. code-block:: python

        def __init_module__(self):
            self.vars.original_message = ''
            self.vars.message = ''

        def __run__(self):
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'
            self.changed = self.vars['new']

        def __quit_module__(self):
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")

Notice that there are no calls to ``module.exit_json()`` nor ``module.fail_json()``: if the module fails, raise an exception.
You can use the convenience method ``self.do_raise()`` or raise the exception as usual in Python to do that.
If no exception is raised, then the module succeeds.

.. seealso::

    See more about exceptions in section
    :ref:`ansible_collections.community.general.docsite.guide_modulehelper.exceptions` below.

Ansible modules must have a ``main()`` function and the usual test for ``'__main__'``. When using MH that should look like:

.. code-block:: python

    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()

The class method ``execute()`` is nothing more than a convenience shorcut for:

.. code-block:: python

    m = MyTest()
    m.run()

Optionally, an ``AnsibleModule`` may be passed as parameter to ``execute()``.

.. _ansible_collections.community.general.docsite.guide_modulehelper.paramvaroutput:

Parameters, variables, and output
"""""""""""""""""""""""""""""""""

All the parameters automatically become variables in the ``self.vars`` attribute, which is of the ``VarDict`` type.
By using ``self.vars``, you get a central mechanism to access the parameters but also to expose variables as return values of the module.
As described in :ref:`ansible_collections.community.general.docsite.guide_vardict`, variables in ``VarDict`` have metadata associated to them.
One of the attributes in that metadata marks the variable for output, and MH makes use of that to generate the module's return values.

.. note::

    The ``VarDict`` class was introduced in community.general 7.1.0, as part of ``ModuleHelper`` itself.
    However, it has been factored out to become an utility on its own, described in :ref:`ansible_collections.community.general.docsite.guide_vardict`,
    and the older implementation was removed in community.general 11.0.0.

    Some code might still refer to the class variables ``use_old_vardict`` and ``mute_vardict_deprecation``, used for the transtition to the new
    implementation but from community.general 11.0.0 onwards they are no longer used and can be safely removed from the code.

Contrary to new variables created in ``VarDict``, module parameters are not set for output by default.
If you want to include some module parameters in the output, list them in the ``output_params`` class variable.

.. code-block:: python

    class MyTest(ModuleHelper):
        output_params = ('state', 'name')
        ...

.. important::

    The variable names listed in ``output_params`` **must be module parameters**, as in parameters listed in the module's ``argument_spec``.
    Names not found in ``argument_spec`` are silently ignored.

Another neat feature provided by MH by using ``VarDict`` is the automatic tracking of changes when setting the metadata ``change=True``.
Again, to enable this feature for module parameters, you must list them in the ``change_params`` class variable.

.. code-block:: python

    class MyTest(ModuleHelper):
        # example from community.general.xfconf
        change_params = ('value', )
        ...

.. important::

    The variable names listed in ``change_params`` **must be module parameters**, as in parameters listed in the module's ``argument_spec``.
    Names not found in ``argument_spec`` are silently ignored.

.. seealso::

    See more about this in
    :ref:`ansible_collections.community.general.docsite.guide_modulehelper.changes` below.

Similarly, if you want to use Ansible's diff mode, you can set the metadata ``diff=True`` and ``diff_params`` for module parameters.
With that, MH will automatically generate the diff output for variables that have changed.

.. code-block:: python

    class MyTest(ModuleHelper):
        diff_params = ('value', )

        def __run__(self):
            # example from community.general.gio_mime
            self.vars.set_meta("handler", initial_value=gio_mime_get(self.runner, self.vars.mime_type), diff=True, change=True)

.. important::

    The variable names listed in ``diff_params`` **must be module parameters**, as in parameters listed in the module's ``argument_spec``.
    Names not found in ``argument_spec`` are silently ignored.

Moreover, if a module is set to return *facts* instead of return values, then again use the metadata ``fact=True`` and ``fact_params`` for module parameters.
Additionally, you must specify ``facts_name``, as in:

.. code-block:: python

    class VolumeFacts(ModuleHelper):
        facts_name = 'volume_facts'

        def __init_module__(self):
            self.vars.set("volume", 123, fact=True)

That generates an Ansible fact like:

.. code-block:: yaml+jinja

    - name: Obtain volume facts
      some.collection.volume_facts:
        # parameters

    - name: Print volume facts
      debug:
        msg: Volume fact is {{ ansible_facts.volume_facts.volume }}

.. important::

    The variable names listed in ``fact_params`` **must be module parameters**, as in parameters listed in the module's ``argument_spec``.
    Names not found in ``argument_spec`` are silently ignored.

.. important::

    If ``facts_name`` is not set, the module does not generate any facts.


.. _ansible_collections.community.general.docsite.guide_modulehelper.changes:

Handling changes
""""""""""""""""

In MH there are many ways to indicate change in the module execution. Here they are:

Tracking changes in variables
-----------------------------

As explained above, you can enable change tracking in any number of variables in ``self.vars``.
By the end of the module execution, if any of those variables has a value different then the first value assigned to them,
then that will be picked up by MH and signalled as changed at the module output.
See the example below to learn how you can enabled change tracking in variables:

.. code-block:: python

    # using __init_module__() as example, it works the same in __run__() and __quit_module__()
    def __init_module__(self):
        # example from community.general.ansible_galaxy_install
        self.vars.set("new_roles", {}, change=True)

        # example of "hidden" variable used only to track change in a value from community.general.gconftool2
        self.vars.set('_value', self.vars.previous_value, output=False, change=True)

        # enable change-tracking without assigning value
        self.vars.set_meta("new_roles", change=True)

        # if you must forcibly set an initial value to the variable
        self.vars.set_meta("new_roles", initial_value=[])
        ...

If the end value of any variable marked ``change`` is different from its initial value, then MH will return ``changed=True``.

Indicating changes with ``changed``
-----------------------------------

If you want to indicate change directly in the code, then use the ``self.changed`` property in MH.
Beware that this is a ``@property`` method in MH, with both a *getter* and a *setter*.
By default, that hidden field is set to ``False``.

Effective change
----------------

The effective outcome for the module is determined in the ``self.has_changed()`` method, and it consists of the logical *OR* operation
between ``self.changed`` and the change calculated from ``self.vars``.

.. _ansible_collections.community.general.docsite.guide_modulehelper.exceptions:

Exceptions
""""""""""

In MH, instead of calling ``module.fail_json()`` you can just raise an exception.
The output variables are collected the same way they would be for a successful execution.
However, you can set output variables specifically for that exception, if you so choose.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelperException

    def __init_module__(self):
        if not complex_validation():
            self.do_raise("Validation failed!")

        # Or passing output variables
        awesomeness = calculate_awesomeness()
        if awesomeness > 1000:
            self.do_raise("Over awesome, I cannot handle it!", update_output={"awesomeness": awesomeness})
            # which is just a convenience shortcut for
            raise ModuleHelperException("...", update_output={...})

All exceptions derived from ``Exception`` are captured and translated into a ``fail_json()`` call.
However, if you do want to call ``self.module.fail_json()`` yourself it will work,
just keep in mind that there will be no automatic handling of output variables in that case.

Behind the curtains, all ``do_raise()`` does is to raise a ``ModuleHelperException``.
If you want to create specialized error handling for your code, the best way is to extend that clas and raise it when needed.

.. _ansible_collections.community.general.docsite.guide_modulehelper.statemh:

StateModuleHelper
^^^^^^^^^^^^^^^^^

Many modules use a parameter ``state`` that effectively controls the exact action performed by the module, such as
``state=present`` or ``state=absent`` for installing or removing packages.
By using ``StateModuleHelper`` you can make your code like the excerpt from the ``gconftool2`` below:

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import StateModuleHelper

    class GConftool(StateModuleHelper):
        ...
        module = dict(
            ...
        )

        def __init_module__(self):
            self.runner = gconftool2_runner(self.module, check_rc=True)
            ...

            self.vars.set('previous_value', self._get(), fact=True)
            self.vars.set('value_type', self.vars.value_type)
            self.vars.set('_value', self.vars.previous_value, output=False, change=True)
            self.vars.set_meta('value', initial_value=self.vars.previous_value)
            self.vars.set('playbook_value', self.vars.value, fact=True)

        ...

        def state_absent(self):
            with self.runner("state key", output_process=self._make_process(False)) as ctx:
                ctx.run()
                self.vars.set('run_info', ctx.run_info, verbosity=4)
            self.vars.set('new_value', None, fact=True)
            self.vars._value = None

        def state_present(self):
            with self.runner("direct config_source value_type state key value", output_process=self._make_process(True)) as ctx:
                ctx.run()
                self.vars.set('run_info', ctx.run_info, verbosity=4)
            self.vars.set('new_value', self._get(), fact=True)
            self.vars._value = self.vars.new_value

Note that the method ``__run__()`` is implemented in ``StateModuleHelper``, all you need to implement are the methods ``state_<state_value>``.
In the example above, :ansplugin:`community.general.gconftool2#module` only has two states, ``present`` and ``absent``, thus, ``state_present()`` and ``state_absent()``.

If the controlling parameter is not called ``state``, like in :ansplugin:`community.general.jira#module` module, just let SMH know about it:

.. code-block:: python

    class JIRA(StateModuleHelper):
        state_param = 'operation'

        def operation_create(self):
            ...

        def operation_search(self):
            ...

Lastly, if the module is called with ``state=somevalue`` and the method ``state_somevalue``
is not implemented, SMH will resort to call a method called ``__state_fallback__()``.
By default, this method will raise a ``ValueError`` indicating the method was not found.
Naturally, you can override that method to write a default implementation, as in :ansplugin:`community.general.locale_gen#module`:

.. code-block:: python

        def __state_fallback__(self):
            if self.vars.state_tracking == self.vars.state:
                return
            if self.vars.ubuntu_mode:
                self.apply_change_ubuntu(self.vars.state, self.vars.name)
            else:
                self.apply_change(self.vars.state, self.vars.name)

That module has only the states ``present`` and ``absent`` and the code for both is the one in the fallback method.

.. note::

    The name of the fallback method **does not change** if you set a different value of ``state_param``.


Other Conveniences
^^^^^^^^^^^^^^^^^^

Delegations to AnsibleModule
""""""""""""""""""""""""""""

The MH properties and methods below are delegated as-is to the underlying ``AnsibleModule`` instance in ``self.module``:

- ``check_mode``
- ``get_bin_path()``
- ``warn()``
- ``deprecate()``

Additionally, MH will also delegate:

- ``diff_mode`` to ``self.module._diff``
- ``verbosity`` to ``self.module._verbosity``

Starting in community.general 10.3.0, MH will also delegate the method ``debug`` to ``self.module``.
If any existing module already has a ``debug`` attribute defined, a warning message will be generated,
requesting it to be renamed. Upon the release of community.general 12.0.0, the delegation will be
preemptive and will override any existing method or property in the subclasses.

Decorators
""""""""""

The following decorators should only be used within ``ModuleHelper`` class.

@cause_changes
--------------

This decorator will control whether the outcome of the method will cause the module to signal change in its output.
If the method completes without raising an exception it is considered to have succeeded, otherwise, it will have failed.

The decorator has a parameter ``when`` that accepts three different values: ``success``, ``failure``, and ``always``.
There are also two legacy parameters, ``on_success`` and ``on_failure``, that will be deprecated, so do not use them.
The value of ``changed`` in the module output will be set to ``True``:

- ``when="success"`` and the method completes without raising an exception.
- ``when="failure"`` and the method raises an exception.
- ``when="always"``, regardless of the method raising an exception or not.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import cause_changes

    # adapted excerpt from the community.general.jira module
    class JIRA(StateModuleHelper):
        @cause_changes(when="success")
        def operation_create(self):
            ...

If ``when`` has a different value or no parameters are specificied, the decorator will have no effect whatsoever.

.. _ansible_collections.community.general.docsite.guide_modulehelper.modulefailsdeco:

@module_fails_on_exception
--------------------------

In a method using this decorator, if an exception is raised, the text message of that exception will be captured
by the decorator and used to call ``self.module.fail_json()``.
In most of the cases there will be no need to use this decorator, because ``ModuleHelper.run()`` already uses it.

@check_mode_skip
----------------

If the module is running in check mode, this decorator will prevent the method from executing.
The return value in that case is ``None``.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import check_mode_skip

    # adapted excerpt from the community.general.locale_gen module
    class LocaleGen(StateModuleHelper):
        @check_mode_skip
        def __state_fallback__(self):
            ...


@check_mode_skip_returns
------------------------

This decorator is similar to the previous one, but the developer can control the return value for the method when running in check mode.
It is used with one of two parameters. One is ``callable`` and the return value in check mode will be ``callable(self, *args, **kwargs)``,
where ``self`` is the ``ModuleHelper`` instance and the union of ``args`` and ``kwargs`` will contain all the parameters passed to the method.

The other option is to use the parameter ``value``, in which case the method will return ``value`` when in check mode.


References
^^^^^^^^^^

- `Ansible Developer Guide <https://docs.ansible.com/ansible/latest/dev_guide/index.html>`_
- `Creating a module <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-a-module>`_
- `Returning ansible facts <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#ansible-facts>`_
- :ref:`ansible_collections.community.general.docsite.guide_vardict`


.. versionadded:: 3.1.0
