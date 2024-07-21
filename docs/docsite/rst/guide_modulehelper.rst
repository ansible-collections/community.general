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


Quickstart
""""""""""

The example from Ansible documentation written with ``ModuleHelper`` is below.
Bear in mind that it does **not** showcase all of MH's features:

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
            self.changed = bool(self.vars.new)
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")


    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()

From this example notice:

- Some convenience methods delegate straight into ``AnsibleModule``, like ``self.check_mode``.

These and other features are described in more detail below.


Module Helper
^^^^^^^^^^^^^

Introduction
""""""""""""

``ModuleHelper`` is a wrapper around the standard ``AnsibleModule``, providing some features.
The basic structure of a module using ``ModuleHelper`` is as shown in the `Quickstart`_ section above,
but there are more elements that will take part in it.

.. code-block:: python

    from ansible_collections.community.general.plugins.module_utils.module_helper import ModuleHelper

    class MyTest(ModuleHelper):
        output_params = ()
        change_params = ()
        diff_params = ()
        facts_name = None
        facts_params = ()
        use_old_vardict = True
        mute_vardict_deprecation = False
        module = dict(
            argument_spec=dict(...),
            ...
        )

After importing the ``ModuleHelper`` class, you need to declare your own class extending it.

.. seealso::

    There is a variation called ``StateModuleHelper``, which builds on top
    of the features provided by MH. See `StateModuleHelper`_ below for more details.

The easiest way of specifying the module is to create the class variable ``module`` with a dictionary
containing the exact arguments that would be passed as paramters to ``AnsibleModule``.
Keep in mind that ``module`` can be either a dictionary as show above, or it can be a proper ``AnsibleModule`` object.
MH also accepts a parameter ``module`` in its constructor, if that parameter is used used,
then it will override the class variable. The parameter can either be ``dict`` or ``AnsibleModule`` as well.

Beyond the definition of the module, there are other variables that can be used to control aspects
of MH's behavior. These variables should be set at the very beginning of the class, and their semantics are
explained through this document.

The main logic of the module happens in the ``ModuleHelper.run()`` method, which looks like:

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

The method ``ModuleHelper.__run__()`` must be implemented by the module.
Most modules will be able to perform their tasks using only that method.
However, in some cases, you might want to execute actions before or after the main tasks, in which cases
you should implement ``ModuleHelper.__init_module__()`` and ``ModuleHelper.__quit_module__()`` respectively.

Note that the output comes from ``self.output``, which is a ``@property`` method.
By default, that property will collect all the variables that are marked for output and return them in a dictionary with their values.
Moreover, the default ``self.output`` will also handle Ansible ``facts`` and *diff mode*.
Also note the changed status comes from ``self.has_changed()``, which is usually calculated from variables that are marked
to track changes in their content.

.. seealso::

    More details in sections `Parameters, variables, and output`_ and `Handling changes`_ below.

And last but not least, the method is decorated with ``@module_fails_on_exception``, which will
capture exceptions that are raised and call ``self.module.exit_json()`` with the exception text as message.

Given that, another way to write the example from the `Quickstart`_ would be:

.. code-block:: python

        def __init_module__(self):
            self.vars.original_message = ''
            self.vars.message = ''

        def __run__(self):
            if self.check_mode:
                return
            self.vars.original_message = self.vars.name
            self.vars.message = 'goodbye'
            self.changed = bool(self.vars.new)

        def __quit_module__(self):
            if self.vars.name == "fail me":
                self.do_raise("You requested this to fail")

There is no need to call ``module.exit_json()`` (or ``module.fail_json()`` for that matter), exceptions are used to cause the module to fail.
There is a generic method to raise exceptions called ``self.do_raise()``.
If no exception was raised, then the module has succeeded.


Ansible modules must have a ``main()`` function and the usual test for ``'__main__'``. When using MH that should look like:

.. code-block:: python

    def main():
        MyTest.execute()


    if __name__ == '__main__':
        main()


Parameters, variables, and output
"""""""""""""""""""""""""""""""""

All the parameters automatically become variables in the ``self.vars`` field, which is of the ``VarDict`` type.
By using ``self.vars``, you have a central mechanism to access the parameters but also to expose variables as return values of the module.
As described in :ref:`ansible_collections.community.general.docsite.guide_vardict`, variables in ``VarDict`` have metadata associated to them.
One of the fields in that metadata marks the variable for output, and MH makes use of that to generate the module's return values.

.. note::

    The ``VarDict`` feature from the documentation was introduced in community.general 7.1.0, but there was a first
    implementation of it embedded within ``ModuleHelper``.
    That older implementation is now deprecated and will be removed in community.general 11.0.0.
    After community.general 7.1.0, MH modules generate a deprecation message about *using the old VarDict*.
    There are two ways to prevent that from happening:

        #.  Set ``mute_vardict_deprecation = True`` and the deprecation will be silenced. If the module still uses the old ``VarDict``,
            it will not be able to update to community.general 11.0.0 (Spring 2026) upon its release.
        #.  Set ``use_old_vardict = False`` to make the MH module use the new ``VarDict`` immediatelly.
            The new ``VarDict`` and its use is documented.
            This is the recommended way to handle this.

    .. code-block:: python

        class MyTest(ModuleHelper):
            use_old_vardict = False
            mute_vardict_deprecation = True
            ...

    These two settings are mutually exclusive, but that is not enforced and the behavior when setting both is not specified.

By default, all variables created in ``VarDict`` are set with ``output=True``, but keep in mind that **module parameters are not set for output by default**.
If you want to include some module parameters in the output, list them in the ``output_params`` class variable.

.. code-block:: python

    class MyTest(ModuleHelper):
        output_params = ('state', 'name')
        ...

A neat feature provided by MH by using ``VarDict`` is the automatic tracking of changes in variables.
This is achieved by setting the metadata ``change=True``, as in:

.. code-block:: python

    # using __init_module__() as example, it works the same in __run__() and __quit_module__()
    def __init_module__(self):
        # example from community.general.ansible_galaxy_install
        self.vars.set("new_roles", {}, change=True)

        # example of "hidden" variable used only to track change in a value from community.general.gconftool2
        self.vars.set('_value', self.vars.previous_value, output=False, change=True)
        ...

If the end value of any variable marked ``change`` is different from its initial value, then the module task will return ``changed=True``.

Again, to track changes in variables created from module parameters, you must list them in the ``change_params`` class variable.

.. code-block:: python

    class MyTest(ModuleHelper):
        # example from community.general.xfconf
        change_params = ('value', )
        ...

.. seealso:: See more about this in `Handling Changes`_ below.

Similarly, if you want to use Ansible's diff mode, you can set the metadata ``diff=True`` and ``diff_params`` for module parameters.
With that, MH will automatically generate the diff output for variables that have changed.

.. code-block:: python

    def __run__(self):
        # example from community.general.gio_mime
        self.vars.set_meta("handler", initial_value=gio_mime_get(self.runner, self.vars.mime_type), diff=True, change=True)

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

    If ``facts_name`` is not set, the module does not generate any facts.


Handling changes
""""""""""""""""

- ``self.__changed__()``
- self.vars
- override ``self.has_changed()``


--------------------------------------------------------------------------------------------------------------------------------------------


Exceptions
""""""""""

StateModuleHelper
^^^^^^^^^^^^^^^^^



References
^^^^^^^^^^

- `Ansible Developer Guide <https://docs.ansible.com/ansible/latest/dev_guide/index.html>`_
- `Creating a module <https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#creating-a-module>`_
- `Returning ansible facts <https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#ansible-facts>`_

- :ref:`ansible_collections.community.general.docsite.guide_vardict`


.. versionadded:: 3.1.0
