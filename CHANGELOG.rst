===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 4.0.0.

v5.8.3
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- keycloak_client_rolemapping - calculate ``proposed`` and ``after`` return values properly (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_client_rolemapping - remove only listed mappings with ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5619).
- proxmox inventory plugin - handle tags delimited by semicolon instead of comma, which happens from Proxmox 7.3 on (https://github.com/ansible-collections/community.general/pull/5602).
- vdo - now uses ``yaml.safe_load()`` to parse command output instead of the deprecated ``yaml.load()`` which is potentially unsafe. Using ``yaml.load()`` without explicitely setting a ``Loader=`` is also an error in pyYAML 6.0 (https://github.com/ansible-collections/community.general/pull/5632).
- vmadm - fix for index out of range error in ``get_vm_uuid`` (https://github.com/ansible-collections/community.general/pull/5628).

v5.8.2
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- chroot connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/5570).
- cmd_runner module utils - fixed bug when handling default cases in ``cmd_runner_fmt.as_map()`` (https://github.com/ansible-collections/community.general/pull/5538).
- cmd_runner module utils - formatting arguments ``cmd_runner_fmt.as_fixed()`` was expecting an non-existing argument (https://github.com/ansible-collections/community.general/pull/5538).
- unixy callback plugin - fix plugin to work with ansible-core 2.14 by using Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).

v5.8.1
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- passwordstore lookup plugin - improve error messages to include stderr (https://github.com/ansible-collections/community.general/pull/5436)

Deprecated Features
-------------------

- Please note that some tools, like the VScode plugin (https://github.com/ansible/vscode-ansible/issues/573), or ``ansible-doc --list --type module``, suggest to replace the correct FQCNs for modules and actions in community.general with internal names that have more than three components. For example, ``community.general.ufw`` is suggested to be replaced by ``community.general.system.ufw``. While these longer names do work, they are considered **internal names** by the collection and are subject to change and be removed at all time. They **will** be removed in community.general 6.0.0 and result in deprecation messages. Avoid using these internal names, and use general three-component FQCNs (``community.general.<name_of_module>``) instead (https://github.com/ansible-collections/community.general/pull/5373).

Bugfixes
--------

- dependent lookup plugin - avoid warning on deprecated parameter for ``Templar.template()`` (https://github.com/ansible-collections/community.general/pull/5543).
- iso_create - the module somtimes failed to add folders for Joliet and UDF formats (https://github.com/ansible-collections/community.general/issues/5275).
- ldap_attrs - fix bug which caused a ``Bad search filter`` error. The error was occuring when the ldap attribute value contained special characters such as ``(`` or ``*`` (https://github.com/ansible-collections/community.general/issues/5434, https://github.com/ansible-collections/community.general/pull/5435).
- nmcli - fix int options idempotence (https://github.com/ansible-collections/community.general/issues/4998).
- nsupdate - fix silent failures when updating ``NS`` entries from Bind9 managed DNS zones (https://github.com/ansible-collections/community.general/issues/4657).
- one_vm - avoid splitting labels that are ``None`` (https://github.com/ansible-collections/community.general/pull/5489).
- proxmox_disk - avoid duplicate ``vmid`` reference (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5493).
- snap - allow values in the ``options`` parameter to contain whitespaces (https://github.com/ansible-collections/community.general/pull/5475).

v5.8.0
======

Release Summary
---------------

Regular feature and bugfix release.

Major Changes
-------------

- newrelic_deployment - removed New Relic v1 API, added support for v2 API (https://github.com/ansible-collections/community.general/pull/5341).

Minor Changes
-------------

- consul - minor refactoring (https://github.com/ansible-collections/community.general/pull/5367).
- lxc_container - minor refactoring (https://github.com/ansible-collections/community.general/pull/5358).
- nmcli - add ``transport_mode`` configuration for Infiniband devices (https://github.com/ansible-collections/community.general/pull/5361).
- opentelemetry callback plugin - send logs. This can be disabled by setting ``disable_logs=false`` (https://github.com/ansible-collections/community.general/pull/4175).
- portage - add knobs for Portage's ``--backtrack`` and ``--with-bdeps`` options (https://github.com/ansible-collections/community.general/pull/5349).
- portage - use Portage's python module instead of calling gentoolkit-provided program in shell (https://github.com/ansible-collections/community.general/pull/5349).
- znode - possibility to use ZooKeeper ACL authentication (https://github.com/ansible-collections/community.general/pull/5306).

Breaking Changes / Porting Guide
--------------------------------

- newrelic_deployment - ``revision`` is required for v2 API (https://github.com/ansible-collections/community.general/pull/5341).

Deprecated Features
-------------------

- ArgFormat module utils - deprecated along ``CmdMixin``, in favor of the ``cmd_runner_fmt`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdMixin module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdModuleHelper module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdStateModuleHelper module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- django_manage - support for Django releases older than 4.1 has been deprecated and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5400).
- django_manage - support for the commands ``cleanup``, ``syncdb`` and ``validate`` that have been deprecated in Django long time ago will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5400).
- django_manage - the behavior of "creating the virtual environment when missing" is being deprecated and will be removed in community.general version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5405).
- newrelic_deployment - ``appname`` and ``environment`` are no longer valid options in the v2 API. They will be removed in community.general 7.0.0 (https://github.com/ansible-collections/community.general/pull/5341).

Bugfixes
--------

- archive - avoid crash when ``lzma`` is not present and ``format`` is not ``xz`` (https://github.com/ansible-collections/community.general/pull/5393).
- ldap_attrs - fix ordering issue by ignoring the ``{x}`` prefix on attribute values (https://github.com/ansible-collections/community.general/issues/977, https://github.com/ansible-collections/community.general/pull/5385).
- opentelemetry callback plugin - support opentelemetry-api 1.13.0 that removed support for ``_time_ns`` (https://github.com/ansible-collections/community.general/pull/5342).
- pfexec become plugin - remove superflous quotes preventing exe wrap from working as expected (https://github.com/ansible-collections/community.general/issues/3671, https://github.com/ansible-collections/community.general/pull/3889).
- pkgng - fix case when ``pkg`` fails when trying to upgrade all packages (https://github.com/ansible-collections/community.general/issues/5363).
- proxmox_kvm - fix ``agent`` parameter when boolean value is specified (https://github.com/ansible-collections/community.general/pull/5198).
- virtualbox inventory plugin - skip parsing values with keys that have both a value and nested data. Skip parsing values that are nested more than two keys deep (https://github.com/ansible-collections/community.general/issues/5332, https://github.com/ansible-collections/community.general/pull/5348).
- xenserver_facts - fix broken ``AnsibleModule`` call that prevented the module from working at all (https://github.com/ansible-collections/community.general/pull/5383).

New Modules
-----------

Cloud
~~~~~

scaleway
^^^^^^^^

- scaleway_container_registry - Scaleway Container registry management module
- scaleway_container_registry_info - Scaleway Container registry info module

Files
~~~~~

- iso_customize - Add/remove/change files in ISO file

Remote Management
~~~~~~~~~~~~~~~~~

manageiq
^^^^^^^^

- manageiq_policies_info - Listing of resource policy_profiles in ManageIQ
- manageiq_tags_info - Retrieve resource tags in ManageIQ

v5.7.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- bitwarden lookup plugin - add option ``search`` to search for other attributes than name (https://github.com/ansible-collections/community.general/pull/5297).
- machinectl become plugin - combine the success command when building the become command to be consistent with other become plugins (https://github.com/ansible-collections/community.general/pull/5287).
- netcup_dnsapi - add ``timeout`` parameter (https://github.com/ansible-collections/community.general/pull/5301).
- proxmox module utils, the proxmox* modules - add ``api_task_ok`` helper to standardize API task status checks across all proxmox modules (https://github.com/ansible-collections/community.general/pull/5274).
- proxmox_snap - add ``unbind`` param to support snapshotting containers with configured mountpoints (https://github.com/ansible-collections/community.general/pull/5274).
- redfish_config - add ``SetSessionService`` to set default session timeout policy (https://github.com/ansible-collections/community.general/issues/5008).
- terraform - adds capability to handle complex variable structures for ``variables`` parameter in the module. This must be enabled with the new ``complex_vars`` parameter (https://github.com/ansible-collections/community.general/pull/4797).
- terraform - run ``terraform init`` with ``-no-color`` not to mess up the stdout of the task (https://github.com/ansible-collections/community.general/pull/5147).

Deprecated Features
-------------------

- lxc_container - the module will no longer make any effort to support Python 2 (https://github.com/ansible-collections/community.general/pull/5304).

Bugfixes
--------

- ini_file - minor refactor fixing a python lint error (https://github.com/ansible-collections/community.general/pull/5307).
- locale_gen - fix support for Ubuntu (https://github.com/ansible-collections/community.general/issues/5281).
- lxc_container - the module has been updated to support Python 3 (https://github.com/ansible-collections/community.general/pull/5304).
- nmcli - fix error when setting previously unset MAC address, ``gsm.apn`` or ``vpn.data``: current values were being normalized without checking if they might be ``None`` (https://github.com/ansible-collections/community.general/pull/5291).
- redhat_subscription - make module idempotent when ``pool_ids`` are used (https://github.com/ansible-collections/community.general/issues/5313).

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_disk - Management of a disk of a Qemu(KVM) VM in a Proxmox VE cluster.

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_user_rolemapping - Allows administration of Keycloak user_rolemapping with the Keycloak API

v5.6.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- ali_instance - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5240).
- ali_instance_info - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5240).
- consul_session - adds ``token`` parameter for session (https://github.com/ansible-collections/community.general/pull/5193).
- gitlab module util - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_branch - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_deploy_key - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_group - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_group_members - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_group_variable - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_hook - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_hook - minor refactoring (https://github.com/ansible-collections/community.general/pull/5271).
- gitlab_project - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_project_members - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_project_variable - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_protected_branch - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_runner - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- gitlab_user - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5259).
- homebrew, homebrew_tap - added Homebrew on Linux path to defaults (https://github.com/ansible-collections/community.general/pull/5241).
- nagios - minor refactoring on parameter validation for different actions (https://github.com/ansible-collections/community.general/pull/5239).
- nmcli - add bond option ``xmit_hash_policy`` to bond options (https://github.com/ansible-collections/community.general/issues/5148).
- nmcli - honor IP options for VPNs (https://github.com/ansible-collections/community.general/pull/5228).
- redfish - added new command GetVirtualMedia, VirtualMediaInsert and VirtualMediaEject to Systems category due to Redfish spec changes the virtualMedia resource location from Manager to System (https://github.com/ansible-collections/community.general/pull/5124).
- seport - added new argument ``local`` (https://github.com/ansible-collections/community.general/pull/5203)
- wdc_redfish_command - add ``PowerModeLow`` and ``PowerModeNormal`` commands for ``Chassis`` category (https://github.com/ansible-collections/community.general/pull/5145).

Deprecated Features
-------------------

- proxmox - deprecated the current ``unprivileged`` default value, will be changed to ``true`` in community.general 7.0.0 (https://github.com/pull/5224).

Bugfixes
--------

- listen_ports_facts - removed leftover ``EnvironmentError`` . The ``else`` clause had a wrong indentation. The check is now handled in the ``split_pid_name`` function (https://github.com/ansible-collections/community.general/pull/5202).
- nmcli - avoid changed status for most cases with VPN connections (https://github.com/ansible-collections/community.general/pull/5126).
- osx_defaults - no longer expand ``~`` in ``value`` to the user's home directory, or expand environment variables (https://github.com/ansible-collections/community.general/issues/5234, https://github.com/ansible-collections/community.general/pull/5243).
- proxmox_kvm - fix exception when no ``agent`` argument is specified (https://github.com/ansible-collections/community.general/pull/5194).
- proxmox_kvm - replace new condition with proper condition to allow for using ``vmid`` on update (https://github.com/ansible-collections/community.general/pull/5206).
- slack - fix message update for channels which start with ``CP``. When ``message-id`` was passed it failed for channels which started with ``CP`` because the ``#`` symbol was added before the ``channel_id`` (https://github.com/ansible-collections/community.general/pull/5249).
- tss lookup plugin - adding support for updated Delinea library (https://github.com/DelineaXPM/python-tss-sdk/issues/9, https://github.com/ansible-collections/community.general/pull/5151).

New Modules
-----------

Packaging
~~~~~~~~~

language
^^^^^^^^

- pipx_info - Rretrieves information about applications installed with pipx

v5.5.0
======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- Added MIT license as ``LICENSES/MIT.txt`` for tests/unit/plugins/modules/packaging/language/test_gem.py (https://github.com/ansible-collections/community.general/pull/5065).
- All software licenses are now in the ``LICENSES/`` directory of the collection root (https://github.com/ansible-collections/community.general/pull/5065, https://github.com/ansible-collections/community.general/pull/5079, https://github.com/ansible-collections/community.general/pull/5080, https://github.com/ansible-collections/community.general/pull/5083, https://github.com/ansible-collections/community.general/pull/5087, https://github.com/ansible-collections/community.general/pull/5095, https://github.com/ansible-collections/community.general/pull/5098, https://github.com/ansible-collections/community.general/pull/5106).
- The collection repository conforms to the `REUSE specification <https://reuse.software/spec/>`__ except for the changelog fragments (https://github.com/ansible-collections/community.general/pull/5138).
- pipx - added state ``latest`` to the module (https://github.com/ansible-collections/community.general/pull/5105).
- pipx - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/5085).
- pipx - module fails faster when ``name`` is missing for states ``upgrade`` and ``reinstall`` (https://github.com/ansible-collections/community.general/pull/5100).
- pipx module utils - created new module util ``pipx`` providing a ``cmd_runner`` specific for the ``pipx`` module (https://github.com/ansible-collections/community.general/pull/5085).
- proxmox_kvm - allow ``agent`` argument to be a string (https://github.com/ansible-collections/community.general/pull/5107).
- wdc_redfish_command - add ``IndicatorLedOn`` and ``IndicatorLedOff`` commands for ``Chassis`` category (https://github.com/ansible-collections/community.general/pull/5059).

Bugfixes
--------

- apache2_mod_proxy - avoid crash when reporting inability to parse balancer_member_page HTML caused by using an undefined variable in the error message (https://github.com/ansible-collections/community.general/pull/5111).
- dig lookup plugin - fix evaluation of falsy values for boolean parameters ``fail_on_error`` and ``retry_servfail`` (https://github.com/ansible-collections/community.general/pull/5129).
- dnsimple_info - correctly report missing library as ``requests`` and not ``another_library`` (https://github.com/ansible-collections/community.general/pull/5111).
- funcd connection plugin - fix signature of ``exec_command`` (https://github.com/ansible-collections/community.general/pull/5111).
- manageiq_alert_profiles - avoid crash when reporting unknown profile caused by trying to return an undefined variable (https://github.com/ansible-collections/community.general/pull/5111).
- nsupdate - compatibility with NS records (https://github.com/ansible-collections/community.general/pull/5112).
- packet_ip_subnet - fix error reporting in case of invalid CIDR prefix lengths (https://github.com/ansible-collections/community.general/pull/5111).
- pip_package_info - remove usage of global variable (https://github.com/ansible-collections/community.general/pull/5111).
- proxmox_kvm - fix wrong condition (https://github.com/ansible-collections/community.general/pull/5108).

v5.4.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- ModuleHelper module utils - added property ``verbosity`` to base class (https://github.com/ansible-collections/community.general/pull/5035).
- apk - add ``world`` parameter for supporting a custom world file (https://github.com/ansible-collections/community.general/pull/4976).
- consul - adds ``ttl`` parameter for session  (https://github.com/ansible-collections/community.general/pull/4996).
- dig lookup plugin - add option ``fail_on_error`` to allow stopping execution on lookup failures (https://github.com/ansible-collections/community.general/pull/4973).
- keycloak_* modules - add ``http_agent`` parameter with default value ``Ansible`` (https://github.com/ansible-collections/community.general/issues/5023).
- lastpass - use config manager for handling plugin options (https://github.com/ansible-collections/community.general/pull/5022).
- listen_ports_facts - add new ``include_non_listening`` option which adds ``-a`` option to ``netstat`` and ``ss``. This shows both listening and non-listening (for TCP this means established connections) sockets, and returns ``state`` and ``foreign_address`` (https://github.com/ansible-collections/community.general/issues/4762, https://github.com/ansible-collections/community.general/pull/4953).
- maven_artifact - add a new ``unredirected_headers`` option that can be used with ansible-core 2.12 and above. The default value is to not use ``Authorization`` and ``Cookie`` headers on redirects for security reasons. With ansible-core 2.11, all headers are still passed on for redirects (https://github.com/ansible-collections/community.general/pull/4812).
- pacman - added parameters ``reason`` and ``reason_for`` to set/change the install reason of packages (https://github.com/ansible-collections/community.general/pull/4956).
- xfconf - add ``stdout``, ``stderr`` and ``cmd`` to the module results (https://github.com/ansible-collections/community.general/pull/5037).
- xfconf - use ``do_raise()`` instead of defining custom exception class (https://github.com/ansible-collections/community.general/pull/4975).
- xfconf_info - use ``do_raise()`` instead of defining custom exception class (https://github.com/ansible-collections/community.general/pull/4975).

Bugfixes
--------

- keyring_info - fix the result from the keyring library never getting returned (https://github.com/ansible-collections/community.general/pull/4964).
- pacman - fixed name resolution of URL packages (https://github.com/ansible-collections/community.general/pull/4959).
- passwordstore lookup plugin - fix ``returnall`` for gopass (https://github.com/ansible-collections/community.general/pull/5027).
- passwordstore lookup plugin - fix password store path detection for gopass (https://github.com/ansible-collections/community.general/pull/4955).
- proxmox - fix error handling when getting VM by name when ``state=absent`` (https://github.com/ansible-collections/community.general/pull/4945).
- proxmox_kvm - fix error handling when getting VM by name when ``state=absent`` (https://github.com/ansible-collections/community.general/pull/4945).
- slack - fix incorrect channel prefix ``#`` caused by incomplete pattern detection by adding ``G0`` and ``GF`` as channel ID patterns (https://github.com/ansible-collections/community.general/pull/5019).
- xfconf - fix setting of boolean values (https://github.com/ansible-collections/community.general/issues/4999, https://github.com/ansible-collections/community.general/pull/5007).

New Plugins
-----------

Lookup
~~~~~~

- bitwarden - Retrieve secrets from Bitwarden

New Modules
-----------

Remote Management
~~~~~~~~~~~~~~~~~

redfish
^^^^^^^

- wdc_redfish_command - Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
- wdc_redfish_info - Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs

v5.3.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- machinectl become plugin - can now be used with a password from another user than root, if a polkit rule is present (https://github.com/ansible-collections/community.general/pull/4849).
- opentelemetry callback plugin - allow configuring opentelementry callback via config file (https://github.com/ansible-collections/community.general/pull/4916).
- redfish_info - add ``GetManagerInventory`` to report list of Manager inventory information (https://github.com/ansible-collections/community.general/issues/4899).

Bugfixes
--------

- cmd_runner module utils - fix bug caused by using the ``command`` variable instead of ``self.command`` when looking for binary path (https://github.com/ansible-collections/community.general/pull/4903).
- dsv lookup plugin - do not ignore the ``tld`` parameter (https://github.com/ansible-collections/community.general/pull/4911).
- lxd connection plugin - fix incorrect ``inventory_hostname`` in ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/issues/4886).
- proxmox inventory plugin - fix crash when ``enabled=1`` is used in agent config string (https://github.com/ansible-collections/community.general/pull/4910).
- rax_clb_nodes - fix code to be compatible with Python 3 (https://github.com/ansible-collections/community.general/pull/4933).
- redfish_info - fix to ``GetChassisPower`` to correctly report power information when multiple chassis exist, but not all chassis report power information (https://github.com/ansible-collections/community.general/issues/4901).

v5.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- cmd_runner module utils - add ``__call__`` method to invoke context (https://github.com/ansible-collections/community.general/pull/4791).
- passwordstore lookup plugin - allow using alternative password managers by detecting wrapper scripts, allow explicit configuration of pass and gopass backends (https://github.com/ansible-collections/community.general/issues/4766).
- sudoers - will attempt to validate the proposed sudoers rule using visudo if available, optionally skipped, or required (https://github.com/ansible-collections/community.general/pull/4794, https://github.com/ansible-collections/community.general/issues/4745).

Bugfixes
--------

- Include ``PSF-license.txt`` file for ``plugins/module_utils/_mount.py``.
- redfish_command - fix the check if a virtual media is unmounted to just check for ``instered= false`` caused by Supermicro hardware that does not clear the ``ImageName`` (https://github.com/ansible-collections/community.general/pull/4839).
- redfish_command - the Supermicro Redfish implementation only supports the ``image_url`` parameter in the underlying API calls to ``VirtualMediaInsert`` and ``VirtualMediaEject``. Any values set (or the defaults) for ``write_protected`` or ``inserted`` will be ignored (https://github.com/ansible-collections/community.general/pull/4839).
- sudoers - fix incorrect handling of ``state: absent`` (https://github.com/ansible-collections/community.general/issues/4852).

New Modules
-----------

Cloud
~~~~~

scaleway
^^^^^^^^

- scaleway_compute_private_network - Scaleway compute - private network management

System
~~~~~~

- keyring - Set or delete a passphrase using the Operating System's native keyring
- keyring_info - Get a passphrase using the Operating System's native keyring

v5.1.1
======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- alternatives - do not set the priority if the priority was not set by the user (https://github.com/ansible-collections/community.general/pull/4810).
- alternatives - only pass subcommands when they are specified as module arguments (https://github.com/ansible-collections/community.general/issues/4803, https://github.com/ansible-collections/community.general/issues/4804, https://github.com/ansible-collections/community.general/pull/4836).
- alternatives - when ``subcommands`` is specified, ``link`` must be given for every subcommand. This was already mentioned in the documentation, but not enforced by the code (https://github.com/ansible-collections/community.general/pull/4836).
- nmcli - fix error caused by adding undefined module arguments for list options (https://github.com/ansible-collections/community.general/issues/4373, https://github.com/ansible-collections/community.general/pull/4813).
- proxmox inventory plugin - fixed extended status detection for qemu (https://github.com/ansible-collections/community.general/pull/4816).
- redhat_subscription - fix unsubscribing on RHEL 9 (https://github.com/ansible-collections/community.general/issues/4741).
- sudoers - ensure sudoers config files are created with the permissions requested by sudoers (0440) (https://github.com/ansible-collections/community.general/pull/4814).

v5.1.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- ModuleHelper module utils - improved ``ModuleHelperException``, using ``to_native()`` for the exception message (https://github.com/ansible-collections/community.general/pull/4755).
- alternatives - add ``state=absent`` to be able to remove an alternative (https://github.com/ansible-collections/community.general/pull/4654).
- alternatives - add ``subcommands`` parameter (https://github.com/ansible-collections/community.general/pull/4654).
- ansible_galaxy_install - minor refactoring using latest ``ModuleHelper`` updates (https://github.com/ansible-collections/community.general/pull/4752).
- cmd_runner module util - added parameters ``check_mode_skip`` and ``check_mode_return`` to ``CmdRunner.context()``, so that the command is not executed when ``check_mode=True`` (https://github.com/ansible-collections/community.general/pull/4736).
- nmcli - adds ``vpn`` type and parameter for supporting VPN with service type L2TP and PPTP (https://github.com/ansible-collections/community.general/pull/4746).
- proxmox inventory plugin - added new flag ``qemu_extended_statuses`` and new groups ``<group_prefix>prelaunch``, ``<group_prefix>paused``. They will be populated only when ``want_facts=true``, ``qemu_extended_statuses=true`` and only for ``QEMU`` machines (https://github.com/ansible-collections/community.general/pull/4723).
- puppet - adds ``confdir`` parameter to configure a custom confir location (https://github.com/ansible-collections/community.general/pull/4740).
- xfconf - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/4776).
- xfconf module utils - created new module util ``xfconf`` providing a ``cmd_runner`` specific for ``xfconf`` modules (https://github.com/ansible-collections/community.general/pull/4776).
- xfconf_info - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/4776).

Deprecated Features
-------------------

- cmd_runner module utils - deprecated ``fmt`` in favour of ``cmd_runner_fmt`` as the parameter format object (https://github.com/ansible-collections/community.general/pull/4777).

New Modules
-----------

System
~~~~~~

- gconftool2_info - Retrieve GConf configurations

v5.0.2
======

Release Summary
---------------

Maintenance and bugfix release for Ansible 6.0.0.

Bugfixes
--------

- Include ``simplified_bsd.txt`` license file for various module utils, the ``lxca_common`` docs fragment, and the ``utm_utils`` unit tests.

v5.0.1
======

Release Summary
---------------

Regular bugfix release for inclusion in Ansible 6.0.0.

Minor Changes
-------------

- cpanm - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- mksysb - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- pipx - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- snap - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- xfconf - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).

Bugfixes
--------

- consul - fixed bug introduced in PR 4590 (https://github.com/ansible-collections/community.general/issues/4680).
- filesystem - handle ``fatresize --info`` output lines without ``:`` (https://github.com/ansible-collections/community.general/pull/4700).
- filesystem - improve error messages when output cannot be parsed by including newlines in escaped form (https://github.com/ansible-collections/community.general/pull/4700).
- keycloak_realm - fix default groups and roles (https://github.com/ansible-collections/community.general/issues/4241).
- redis* modules - fix call to ``module.fail_json`` when failing because of missing Python libraries (https://github.com/ansible-collections/community.general/pull/4733).
- xcc_redfish_command - for compatibility due to Redfish spec changes the virtualMedia resource location changed from Manager to System (https://github.com/ansible-collections/community.general/pull/4682).
- zfs - fix wrong quoting of properties (https://github.com/ansible-collections/community.general/issues/4707, https://github.com/ansible-collections/community.general/pull/4726).

v5.0.0
======

Release Summary
---------------

This is release 5.0.0 of ``community.general``, released on 2022-05-17.

Major Changes
-------------

- The community.general collection no longer supports Ansible 2.9 and ansible-base 2.10. While we take no active measures to prevent usage, we will remove a lot of compatibility code and other compatility measures that will effectively prevent using most content from this collection with Ansible 2.9, and some content of this collection with ansible-base 2.10. Both Ansible 2.9 and ansible-base 2.10 will very soon be End of Life and if you are still using them, you should consider upgrading to ansible-core 2.11 or later as soon as possible (https://github.com/ansible-collections/community.general/pull/4548).

Minor Changes
-------------

- Avoid internal ansible-core module_utils in favor of equivalent public API available since at least Ansible 2.9. This fixes some instances added since the last time this was fixed (https://github.com/ansible-collections/community.general/pull/4232).
- ModuleHelper module utils - ``ModuleHelperBase` now delegates the attributes ``check_mode``, ``get_bin_path``, ``warn``, and ``deprecate`` to the underlying ``AnsibleModule`` instance (https://github.com/ansible-collections/community.general/pull/4600).
- ModuleHelper module utils - ``ModuleHelperBase`` now has a convenience method ``do_raise`` (https://github.com/ansible-collections/community.general/pull/4660).
- Remove vendored copy of ``distutils.version`` in favor of vendored copy included with ansible-core 2.12+. For ansible-core 2.11, uses ``distutils.version`` for Python < 3.12. There is no support for ansible-core 2.11 with Python 3.12+ (https://github.com/ansible-collections/community.general/pull/3988).
- aix_filesystem - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3833).
- aix_lvg - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3834).
- alternatives - add ``state`` parameter, which provides control over whether the alternative should be set as the active selection for its alternatives group (https://github.com/ansible-collections/community.general/issues/4543, https://github.com/ansible-collections/community.general/pull/4557).
- ansible_galaxy_install - added option ``no_deps`` to the module (https://github.com/ansible-collections/community.general/issues/4174).
- atomic_container - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- clc_alert_policy - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- clc_group - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- clc_loadbalancer - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- clc_server - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- cmd_runner module util - reusable command runner with consistent argument formatting and sensible defaults (https://github.com/ansible-collections/community.general/pull/4476).
- cobbler inventory plugin - add ``include_profiles`` option (https://github.com/ansible-collections/community.general/pull/4068).
- datadog_monitor - support new datadog event monitor of type `event-v2 alert` (https://github.com/ansible-collections/community.general/pull/4457)
- filesystem - add support for resizing btrfs (https://github.com/ansible-collections/community.general/issues/4465).
- gitlab - add more token authentication support with the new options ``api_oauth_token`` and ``api_job_token`` (https://github.com/ansible-collections/community.general/issues/705).
- gitlab - clean up modules and utils (https://github.com/ansible-collections/community.general/pull/3694).
- gitlab_group, gitlab_project - add new option ``avatar_path`` (https://github.com/ansible-collections/community.general/pull/3792).
- gitlab_group_variable - new ``variables`` parameter (https://github.com/ansible-collections/community.general/pull/4038 and https://github.com/ansible-collections/community.general/issues/4074).
- gitlab_project - add new option ``default_branch`` to gitlab_project (if ``readme = true``) (https://github.com/ansible-collections/community.general/pull/3792).
- gitlab_project_variable - new ``variables`` parameter (https://github.com/ansible-collections/community.general/issues/4038).
- hponcfg - revamped module using ModuleHelper (https://github.com/ansible-collections/community.general/pull/3840).
- icinga2 inventory plugin - added the ``display_name`` field to variables (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- icinga2 inventory plugin - implemented constructed interface (https://github.com/ansible-collections/community.general/pull/4088).
- icinga2 inventory plugin - inventory object names are changable using ``inventory_attr`` in your config file to the host object name, address, or display_name fields (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- ip_netns - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3822).
- ipa_dnsrecord - add new argument ``record_values``, mutually exclusive to ``record_value``, which supports multiple values for one record (https://github.com/ansible-collections/community.general/pull/4578).
- ipa_dnszone - ``dynamicupdate`` is now a boolean parameter, instead of a string parameter accepting ``"true"`` and ``"false"``. Also the module is now idempotent with respect to ``dynamicupdate`` (https://github.com/ansible-collections/community.general/pull/3374).
- ipa_dnszone - add DNS zone synchronization support (https://github.com/ansible-collections/community.general/pull/3374).
- ipa_service - add ``skip_host_check`` parameter. (https://github.com/ansible-collections/community.general/pull/4417).
- ipmi_boot - add support for user-specified IPMI encryption key (https://github.com/ansible-collections/community.general/issues/3698).
- ipmi_power - add ``machine`` option to ensure the power state via the remote target address (https://github.com/ansible-collections/community.general/pull/3968).
- ipmi_power - add support for user-specified IPMI encryption key (https://github.com/ansible-collections/community.general/issues/3698).
- iso_extract - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3805).
- java_cert - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3835).
- jira - add support for Bearer token auth (https://github.com/ansible-collections/community.general/pull/3838).
- jira - when creating a comment, ``fields`` now is used for additional data (https://github.com/ansible-collections/community.general/pull/4304).
- keycloak_* modules - added connection timeout parameter when calling server (https://github.com/ansible-collections/community.general/pull/4168).
- keycloak_client - add ``always_display_in_console`` parameter (https://github.com/ansible-collections/community.general/issues/4390).
- keycloak_client - add ``default_client_scopes`` and ``optional_client_scopes`` parameters. (https://github.com/ansible-collections/community.general/pull/4385).
- keycloak_user_federation - add sssd user federation support (https://github.com/ansible-collections/community.general/issues/3767).
- ldap_entry - add support for recursive deletion (https://github.com/ansible-collections/community.general/issues/3613).
- linode inventory plugin - add support for caching inventory results (https://github.com/ansible-collections/community.general/pull/4179).
- linode inventory plugin - allow templating of ``access_token`` variable in Linode inventory plugin (https://github.com/ansible-collections/community.general/pull/4040).
- listen_ports_facts - add support for ``ss`` command besides ``netstat`` (https://github.com/ansible-collections/community.general/pull/3708).
- lists_mergeby filter plugin - add parameters ``list_merge`` and ``recursive``. These are only supported when used with ansible-base 2.10 or ansible-core, but not with Ansible 2.9 (https://github.com/ansible-collections/community.general/pull/4058).
- logentries - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3807).
- logstash_plugin - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3808).
- lxc_container - added ``wait_for_container`` parameter. If ``true`` the module will wait until the running task reports success as the status (https://github.com/ansible-collections/community.general/pull/4039).
- lxc_container - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3851).
- lxd connection plugin - make sure that ``ansible_lxd_host``, ``ansible_executable``, and ``ansible_lxd_executable`` work (https://github.com/ansible-collections/community.general/pull/3798).
- lxd inventory plugin - support virtual machines (https://github.com/ansible-collections/community.general/pull/3519).
- lxd_container - adds ``project`` option to allow selecting project for LXD instance (https://github.com/ansible-collections/community.general/pull/4479).
- lxd_container - adds ``type`` option which also allows to operate on virtual machines and not just containers (https://github.com/ansible-collections/community.general/pull/3661).
- lxd_profile - adds ``project`` option to allow selecting project for LXD profile (https://github.com/ansible-collections/community.general/pull/4479).
- mail callback plugin - add ``Message-ID`` and ``Date`` headers (https://github.com/ansible-collections/community.general/issues/4055, https://github.com/ansible-collections/community.general/pull/4056).
- mail callback plugin - properly use Ansible's option handling to split lists (https://github.com/ansible-collections/community.general/pull/4140).
- mattermost - add the possibility to send attachments instead of text messages (https://github.com/ansible-collections/community.general/pull/3946).
- mksysb - revamped the module using ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/3295).
- module_helper module utils - added decorators ``check_mode_skip`` and ``check_mode_skip_returns`` for skipping methods when ``check_mode=True`` (https://github.com/ansible-collections/community.general/pull/3849).
- monit - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3821).
- nmap inventory plugin - add ``sudo`` option in plugin in order to execute ``sudo nmap`` so that ``nmap`` runs with elevated privileges (https://github.com/ansible-collections/community.general/pull/4506).
- nmcli - add ``wireguard`` connection type (https://github.com/ansible-collections/community.general/pull/3985).
- nmcli - add missing connection aliases ``802-3-ethernet`` and ``802-11-wireless`` (https://github.com/ansible-collections/community.general/pull/4108).
- nmcli - add multiple addresses support for ``ip4`` parameter (https://github.com/ansible-collections/community.general/issues/1088, https://github.com/ansible-collections/community.general/pull/3738).
- nmcli - add multiple addresses support for ``ip6`` parameter (https://github.com/ansible-collections/community.general/issues/1088).
- nmcli - add support for ``eui64`` and ``ipv6privacy`` parameters (https://github.com/ansible-collections/community.general/issues/3357).
- nmcli - adds ``routes6`` and ``route_metric6`` parameters for supporting IPv6 routes (https://github.com/ansible-collections/community.general/issues/4059).
- nmcli - remove nmcli modify dependency on ``type`` parameter (https://github.com/ansible-collections/community.general/issues/2858).
- nomad_job - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- nomad_job_info - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- npm - add ability to use ``production`` flag when ``ci`` is set (https://github.com/ansible-collections/community.general/pull/4299).
- open_iscsi - extended module to allow rescanning of established session for one or all targets (https://github.com/ansible-collections/community.general/issues/3763).
- opennebula - add the release action for VMs in the ``HOLD`` state (https://github.com/ansible-collections/community.general/pull/4036).
- opentelemetry_plugin - enrich service when using the ``docker_login`` (https://github.com/ansible-collections/community.general/pull/4104).
- opentelemetry_plugin - enrich service when using the ``jenkins``, ``hetzner`` or ``jira`` modules (https://github.com/ansible-collections/community.general/pull/4105).
- packet_device - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- packet_sshkey - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- packet_volume - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- pacman - add ``remove_nosave`` parameter to avoid saving modified configuration files as ``.pacsave`` files. (https://github.com/ansible-collections/community.general/pull/4316, https://github.com/ansible-collections/community.general/issues/4315).
- pacman - add ``stdout`` and ``stderr`` as return values (https://github.com/ansible-collections/community.general/pull/3758).
- pacman - now implements proper change detection for ``update_cache=true``. Adds ``cache_updated`` return value to when ``update_cache=true`` to report this result independently of the module's overall changed return value (https://github.com/ansible-collections/community.general/pull/4337).
- pacman - the module has been rewritten and is now much faster when using ``state=latest``. Operations are now done all packages at once instead of package per package and the configured output format of ``pacman`` no longer affect the module's operation. (https://github.com/ansible-collections/community.general/pull/3907, https://github.com/ansible-collections/community.general/issues/3783, https://github.com/ansible-collections/community.general/issues/4079)
- passwordstore lookup plugin - add configurable ``lock`` and ``locktimeout`` options to avoid race conditions in itself and in the ``pass`` utility it calls. By default, the plugin now locks on write operations (https://github.com/ansible-collections/community.general/pull/4194).
- pipx - added options ``editable`` and ``pip_args`` (https://github.com/ansible-collections/community.general/issues/4300).
- pritunl_user - add ``mac_addresses`` parameter (https://github.com/ansible-collections/community.general/pull/4535).
- profitbricks - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- proxmox - add ``clone`` parameter (https://github.com/ansible-collections/community.general/pull/3930).
- proxmox - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- proxmox inventory plugin - add support for client-side jinja filters (https://github.com/ansible-collections/community.general/issues/3553).
- proxmox inventory plugin - add support for templating the ``url``, ``user``, and ``password`` options (https://github.com/ansible-collections/community.general/pull/4418).
- proxmox inventory plugin - add token authentication as an alternative to username/password (https://github.com/ansible-collections/community.general/pull/4540).
- proxmox inventory plugin - parse LXC configs returned by the proxmox API (https://github.com/ansible-collections/community.general/pull/4472).
- proxmox modules - move ``HAS_PROXMOXER`` check into ``module_utils`` (https://github.com/ansible-collections/community.general/pull/4030).
- proxmox modules - move common code into ``module_utils`` (https://github.com/ansible-collections/community.general/pull/4029).
- proxmox_kvm - added EFI disk support when creating VM with OVMF UEFI BIOS with new ``efidisk0`` option (https://github.com/ansible-collections/community.general/pull/4106, https://github.com/ansible-collections/community.general/issues/1638).
- proxmox_kwm - add ``win11`` to ``ostype`` parameter for Windows 11 and Windows Server 2022 support (https://github.com/ansible-collections/community.general/issues/4023, https://github.com/ansible-collections/community.general/pull/4191).
- proxmox_snap - add restore snapshot option (https://github.com/ansible-collections/community.general/pull/4377).
- proxmox_snap - fixed timeout value to correctly reflect time in seconds. The timeout was off by one second (https://github.com/ansible-collections/community.general/pull/4377).
- puppet - remove deprecation for ``show_diff`` parameter. Its alias ``show-diff`` is still deprecated and will be removed in community.general 7.0.0 (https://github.com/ansible-collections/community.general/pull/3980).
- python_requirements_info - returns python version broken down into its components, and some minor refactoring (https://github.com/ansible-collections/community.general/pull/3797).
- rax_files_objects - minor refactoring improving code quality (https://github.com/ansible-collections/community.general/pull/4649).
- redfish_* modules - the contents of ``@Message.ExtendedInfo`` will be returned as a string in the event that ``@Message.ExtendedInfo.Messages`` does not exist. This is likely more useful than the standard HTTP error (https://github.com/ansible-collections/community.general/pull/4596).
- redfish_command - add ``GetHostInterfaces`` command to enable reporting Redfish Host Interface information (https://github.com/ansible-collections/community.general/issues/3693).
- redfish_command - add ``IndicatorLedOn``, ``IndicatorLedOff``, and ``IndicatorLedBlink`` commands to the Systems category for controling system LEDs (https://github.com/ansible-collections/community.general/issues/4084).
- redfish_command - add ``SetHostInterface`` command to enable configuring the Redfish Host Interface (https://github.com/ansible-collections/community.general/issues/3632).
- redis - add authentication parameters ``login_user``, ``tls``, ``validate_certs``, and ``ca_certs`` (https://github.com/ansible-collections/community.general/pull/4207).
- scaleway inventory plugin - add profile parameter ``scw_profile`` (https://github.com/ansible-collections/community.general/pull/4049).
- scaleway_compute - add possibility to use project identifier (new ``project`` option) instead of deprecated organization identifier (https://github.com/ansible-collections/community.general/pull/3951).
- scaleway_volume - all volumes are systematically created on par1 (https://github.com/ansible-collections/community.general/pull/3964).
- seport - minor refactoring (https://github.com/ansible-collections/community.general/pull/4471).
- smartos_image_info - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- snap - add option ``options`` permitting to set options using the ``snap set`` command (https://github.com/ansible-collections/community.general/pull/3943).
- sudoers - add support for ``runas`` parameter (https://github.com/ansible-collections/community.general/issues/4379).
- svc - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3829).
- syslog_json - add option to skip logging of ``gather_facts`` playbook tasks; use v2 callback API (https://github.com/ansible-collections/community.general/pull/4223).
- terraform - adds ``terraform_upgrade`` parameter which allows ``terraform init`` to satisfy new provider constraints in an existing Terraform project (https://github.com/ansible-collections/community.general/issues/4333).
- to_time_unit filter plugins - the time filters has been extended to also allow ``0`` as input (https://github.com/ansible-collections/community.general/pull/4612).
- udm_group - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- udm_share - minor refactoring (https://github.com/ansible-collections/community.general/pull/4556).
- vmadm - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- vmadm - minor refactoring and improvement on the module (https://github.com/ansible-collections/community.general/pull/4581).
- vmadm - minor refactoring and improvement on the module (https://github.com/ansible-collections/community.general/pull/4648).
- webfaction_app - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- webfaction_db - minor refactoring (https://github.com/ansible-collections/community.general/pull/4567).
- xattr - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3806).
- xfconf - added missing value types ``char``, ``uchar``, ``int64`` and ``uint64`` (https://github.com/ansible-collections/community.general/pull/4534).
- xfconf - minor refactor on the base class for the module (https://github.com/ansible-collections/community.general/pull/3919).
- zfs - minor refactoring in the code (https://github.com/ansible-collections/community.general/pull/4650).
- zypper - add support for ``--clean-deps`` option to remove packages that depend on a package being removed (https://github.com/ansible-collections/community.general/pull/4195).

Breaking Changes / Porting Guide
--------------------------------

- Parts of this collection do not work with ansible-core 2.11 on Python 3.12+. Please either upgrade to ansible-core 2.12+, or use Python 3.11 or earlier (https://github.com/ansible-collections/community.general/pull/3988).
- The symbolic links used to implement flatmapping for all modules were removed and replaced by ``meta/runtime.yml`` redirects. This effectively breaks compatibility with Ansible 2.9 for all modules (without using their "long" names, which is discouraged and which can change without previous notice since they are considered an implementation detail) (https://github.com/ansible-collections/community.general/pull/4548).
- a_module test plugin - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- archive - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- git_config - remove Ansible 2.9 and early ansible-base 2.10 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- java_keystore - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- lists_mergeby and groupby_as_dict filter plugins - adjust filter plugin filename. This change is not visible to end-users, it only affects possible other collections importing Python paths (https://github.com/ansible-collections/community.general/pull/4625).
- lists_mergeby filter plugin - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- maven_artifact - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- memcached cache plugin - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- path_join filter plugin shim - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- redis cache plugin - remove Ansible 2.9 compatibility code (https://github.com/ansible-collections/community.general/pull/4548).
- yarn - remove unsupported and unnecessary ``--no-emoji`` flag (https://github.com/ansible-collections/community.general/pull/4662).

Deprecated Features
-------------------

- ansible_galaxy_install - deprecated support for ``ansible`` 2.9 and ``ansible-base`` 2.10 (https://github.com/ansible-collections/community.general/pull/4601).
- dig lookup plugin - the ``DLV`` record type has been decommissioned in 2017 and support for it will be removed from community.general 6.0.0 (https://github.com/ansible-collections/community.general/pull/4618).
- gem - the default of the ``norc`` option has been deprecated and will change to ``true`` in community.general 6.0.0. Explicitly specify a value to avoid a deprecation warning (https://github.com/ansible-collections/community.general/pull/4517).
- mail callback plugin - not specifying ``sender`` is deprecated and will be disallowed in community.general 6.0.0 (https://github.com/ansible-collections/community.general/pull/4140).
- module_helper module utils - deprecated the attribute ``ModuleHelper.VarDict`` (https://github.com/ansible-collections/community.general/pull/3801).
- nmcli - deprecate default hairpin mode for a bridge. This so we can change it to ``false`` in community.general 7.0.0, as this is also the default in ``nmcli`` (https://github.com/ansible-collections/community.general/pull/4334).
- pacman - from community.general 5.0.0 on, the ``changed`` status of ``update_cache`` will no longer be ignored if ``name`` or ``upgrade`` is specified. To keep the old behavior, add something like ``register: result`` and ``changed_when: result.packages | length > 0`` to your task (https://github.com/ansible-collections/community.general/pull/4329).
- proxmox inventory plugin - the current default ``true`` of the ``want_proxmox_nodes_ansible_host`` option has been deprecated. The default will change to ``false`` in community.general 6.0.0. To keep the current behavior, explicitly set ``want_proxmox_nodes_ansible_host`` to ``true`` in your inventory configuration. We suggest to already switch to the new behavior by explicitly setting it to ``false``, and by using ``compose:`` to set ``ansible_host`` to the correct value. See the examples in the plugin documentation for details (https://github.com/ansible-collections/community.general/pull/4466).
- vmadm - deprecated module parameter ``debug`` that was not used anywhere (https://github.com/ansible-collections/community.general/pull/4580).

Removed Features (previously deprecated)
----------------------------------------

- ali_instance_info - removed the options ``availability_zone``, ``instance_ids``, and ``instance_names``. Use filter item ``zone_id`` instead of ``availability_zone``, filter item ``instance_ids`` instead of ``instance_ids``, and filter item ``instance_name`` instead of ``instance_names`` (https://github.com/ansible-collections/community.general/pull/4516).
- apt_rpm - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- compose - removed various deprecated aliases. Use the version with ``_`` instead of ``-`` instead (https://github.com/ansible-collections/community.general/pull/4516).
- dnsimple - remove support for dnsimple < 2.0.0 (https://github.com/ansible-collections/community.general/pull/4516).
- github_deploy_key - removed the deprecated alias ``2fa_token`` of ``otp`` (https://github.com/ansible-collections/community.general/pull/4516).
- homebrew, homebrew_cask - removed the deprecated alias ``update-brew`` of ``update_brew`` (https://github.com/ansible-collections/community.general/pull/4516).
- linode - removed the ``backupsenabled`` option. Use ``backupweeklyday`` or ``backupwindow`` to enable backups (https://github.com/ansible-collections/community.general/pull/4516).
- opkg - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- pacman - if ``update_cache=true`` is used with ``name`` or ``upgrade``, the changed state will now also indicate if only the cache was updated. To keep the old behavior - only indicate ``changed`` when a package was installed/upgraded -, use ``changed_when`` as indicated in the module examples (https://github.com/ansible-collections/community.general/pull/4516).
- pacman - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- proxmox, proxmox_kvm, proxmox_snap - no longer allow to specify a VM name that matches multiple VMs. If this happens, the modules now fail (https://github.com/ansible-collections/community.general/pull/4516).
- serverless - removed the ``functions`` option. It was not used by the module (https://github.com/ansible-collections/community.general/pull/4516).
- slackpkg - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- urpmi - removed the deprecated alias ``no-recommends`` of ``no_recommends`` (https://github.com/ansible-collections/community.general/pull/4516).
- urpmi - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- xbps - removed the deprecated alias ``update-cache`` of ``update_cache`` (https://github.com/ansible-collections/community.general/pull/4516).
- xfconf - the ``get`` state has been removed. Use the ``xfconf_info`` module instead (https://github.com/ansible-collections/community.general/pull/4516).

Bugfixes
--------

- Various modules and plugins - use vendored version of ``distutils.version`` instead of the deprecated Python standard library ``distutils`` (https://github.com/ansible-collections/community.general/pull/3936).
- a_module test plugin - fix crash when testing a module name that was tombstoned (https://github.com/ansible-collections/community.general/pull/3660).
- alternatives - fix output parsing for alternatives groups (https://github.com/ansible-collections/community.general/pull/3976).
- cargo - fix detection of outdated packages when ``state=latest`` (https://github.com/ansible-collections/community.general/pull/4052).
- cargo - fix incorrectly reported changed status for packages with a name containing a hyphen (https://github.com/ansible-collections/community.general/issues/4044, https://github.com/ansible-collections/community.general/pull/4052).
- consul - fixed bug where class ``ConsulService`` was overwriting the field ``checks``, preventing the addition of checks to a service (https://github.com/ansible-collections/community.general/pull/4590).
- counter_enabled callback plugin - fix output to correctly display host and task counters in serial mode (https://github.com/ansible-collections/community.general/pull/3709).
- dconf - skip processes that disappeared while we inspected them (https://github.com/ansible-collections/community.general/issues/4151).
- dnsmadeeasy - fix failure on deleting DNS entries when API response does not contain monitor value (https://github.com/ansible-collections/community.general/issues/3620).
- dsv lookup plugin - raise an Ansible error if the wrong ``python-dsv-sdk`` version is installed (https://github.com/ansible-collections/community.general/pull/4422).
- filesize - add support for busybox dd implementation, that is used by default on Alpine linux (https://github.com/ansible-collections/community.general/pull/4288, https://github.com/ansible-collections/community.general/issues/4259).
- gconftool2 - properly escape values when passing them to ``gconftool-2`` (https://github.com/ansible-collections/community.general/pull/4647).
- git_branch - remove deprecated and unnecessary branch ``unprotect`` method (https://github.com/ansible-collections/community.general/pull/4496).
- github_repo - ``private`` and ``description`` attributes should not be set to default values when the repo already exists (https://github.com/ansible-collections/community.general/pull/2386).
- gitlab_group - improve searching for projects inside group on deletion (https://github.com/ansible-collections/community.general/pull/4491).
- gitlab_group_members - handle more than 20 groups when finding a group (https://github.com/ansible-collections/community.general/pull/4491, https://github.com/ansible-collections/community.general/issues/4460, https://github.com/ansible-collections/community.general/issues/3729).
- gitlab_group_variable - add missing documentation about GitLab versions that support ``environment_scope`` and ``variable_type`` (https://github.com/ansible-collections/community.general/pull/4038).
- gitlab_group_variable - allow to set same variable name under different environment scopes. Due this change, the return value ``group_variable`` differs from previous version in check mode. It was counting ``updated`` values, because it was accidentally overwriting environment scopes (https://github.com/ansible-collections/community.general/pull/4038).
- gitlab_group_variable - fix idempotent change behaviour for float and integer variables (https://github.com/ansible-collections/community.general/pull/4038).
- gitlab_hook - avoid errors during idempotency check when an attribute does not exist (https://github.com/ansible-collections/community.general/pull/4668).
- gitlab_hook - handle more than 20 hooks when finding a hook (https://github.com/ansible-collections/community.general/pull/4491).
- gitlab_project - handle more than 20 namespaces when finding a namespace (https://github.com/ansible-collections/community.general/pull/4491).
- gitlab_project_members - handle more than 20 projects and users when finding a project resp. user (https://github.com/ansible-collections/community.general/pull/4491).
- gitlab_project_variable - ``value`` is not necessary when deleting variables (https://github.com/ansible-collections/community.general/pull/4150).
- gitlab_project_variable - add missing documentation about GitLab versions that support ``environment_scope`` and ``variable_type`` (https://github.com/ansible-collections/community.general/issues/4038).
- gitlab_project_variable - allow to set same variable name under different environment scopes. Due this change, the return value ``project_variable`` differs from previous version in check mode. It was counting ``updated`` values, because it was accidentally overwriting environment scopes (https://github.com/ansible-collections/community.general/issues/4038).
- gitlab_project_variable - fix idempotent change behaviour for float and integer variables (https://github.com/ansible-collections/community.general/issues/4038).
- gitlab_runner - make ``project`` and ``owned`` mutually exclusive (https://github.com/ansible-collections/community.general/pull/4136).
- gitlab_runner - use correct API endpoint to create and retrieve project level runners when using ``project`` (https://github.com/ansible-collections/community.general/pull/3965).
- gitlab_user - handle more than 20 users and SSH keys when finding a user resp. SSH key (https://github.com/ansible-collections/community.general/pull/4491).
- homebrew_cask - fix force install operation (https://github.com/ansible-collections/community.general/issues/3703).
- icinga2 inventory plugin - handle 404 error when filter produces no results (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- imc_rest - fixes the module failure due to the usage of ``itertools.izip_longest`` which is not available in Python 3 (https://github.com/ansible-collections/community.general/issues/4206).
- ini_file - when removing nothing do not report changed (https://github.com/ansible-collections/community.general/issues/4154).
- interfaces_file - fixed the check for existing option in interface (https://github.com/ansible-collections/community.general/issues/3841).
- jail connection plugin - replace deprecated ``distutils.spawn.find_executable`` with Ansible's ``get_bin_path`` to find the executable (https://github.com/ansible-collections/community.general/pull/3934).
- jira - fixed bug where module returns error related to dictionary key ``body`` (https://github.com/ansible-collections/community.general/issues/3419).
- keycloak - fix parameters types for ``defaultDefaultClientScopes`` and ``defaultOptionalClientScopes`` from list of dictionaries to list of strings (https://github.com/ansible-collections/community.general/pull/4526).
- keycloak_* - the documented ``validate_certs`` parameter was not taken into account when calling the ``open_url`` function in some cases, thus enforcing certificate validation even when ``validate_certs`` was set to ``false``. (https://github.com/ansible-collections/community.general/pull/4382)
- keycloak_user_federation - creating a user federation while specifying an ID (that does not exist yet) no longer fail with a 404 Not Found (https://github.com/ansible-collections/community.general/pull/4212).
- keycloak_user_federation - mappers auto-created by keycloak are matched and merged by their name and no longer create duplicated entries (https://github.com/ansible-collections/community.general/pull/4212).
- ldap_search - allow it to be used even in check mode (https://github.com/ansible-collections/community.general/issues/3619).
- linode inventory plugin - fix configuration handling relating to inventory filtering (https://github.com/ansible-collections/community.general/pull/4336).
- listen_ports_facts - local port regex was not handling well IPv6 only binding. Fixes the regex for ``ss`` (https://github.com/ansible-collections/community.general/pull/4092).
- lvol - allows logical volumes to be created with certain size arguments prefixed with ``+`` to preserve behavior of older versions of this module (https://github.com/ansible-collections/community.general/issues/3665).
- lxd connection plugin - replace deprecated ``distutils.spawn.find_executable`` with Ansible's ``get_bin_path`` to find the ``lxc`` executable (https://github.com/ansible-collections/community.general/pull/3934).
- lxd inventory plugin - do not crash if OS and release metadata are not present
  (https://github.com/ansible-collections/community.general/pull/4351).
- mail callback plugin - fix crash on Python 3 (https://github.com/ansible-collections/community.general/issues/4025, https://github.com/ansible-collections/community.general/pull/4026).
- mail callback plugin - fix encoding of the name of sender and recipient (https://github.com/ansible-collections/community.general/issues/4060, https://github.com/ansible-collections/community.general/pull/4061).
- mksysb - fixed bug for parameter ``backup_dmapi_fs`` was passing the wrong CLI argument (https://github.com/ansible-collections/community.general/pull/3295).
- nmcli - fix returning "changed" when no mask set for IPv4 or IPv6 addresses on task rerun (https://github.com/ansible-collections/community.general/issues/3768).
- nmcli - fix returning "changed" when routes parameters set, also suggest new routes4 and routes6 format (https://github.com/ansible-collections/community.general/issues/4131).
- nmcli - fixed falsely reported changed status when ``mtu`` is omitted with ``dummy`` connections (https://github.com/ansible-collections/community.general/issues/3612, https://github.com/ansible-collections/community.general/pull/3625).
- nmcli - pass ``flags``, ``ingress``, ``egress`` params to ``nmcli`` (https://github.com/ansible-collections/community.general/issues/1086).
- nrdp callback plugin - fix error ``string arguments without an encoding`` (https://github.com/ansible-collections/community.general/issues/3903).
- onepassword - search all valid configuration locations and use the first found (https://github.com/ansible-collections/community.general/pull/4640).
- opennebula inventory plugin - complete the implementation of ``constructable`` for opennebula inventory plugin. Now ``keyed_groups``, ``compose``, ``groups`` actually work (https://github.com/ansible-collections/community.general/issues/4497).
- opentelemetry - fix generating a trace with a task containing ``no_log: true`` (https://github.com/ansible-collections/community.general/pull/4043).
- opentelemetry callback plugin - fix task message attribute that is reported failed regardless of the task result (https://github.com/ansible-collections/community.general/pull/4624).
- opentelemetry callback plugin - fix warning for the include_tasks (https://github.com/ansible-collections/community.general/pull/4623).
- opentelemetry_plugin - honour ``ignore_errors`` when a task has failed instead of reporting an error (https://github.com/ansible-collections/community.general/pull/3837).
- pacman - Use ``--groups`` instead of ``--group`` (https://github.com/ansible-collections/community.general/pull/4312).
- pacman - fix URL based package installation (https://github.com/ansible-collections/community.general/pull/4286, https://github.com/ansible-collections/community.general/issues/4285).
- pacman - fix ``upgrade=yes`` (https://github.com/ansible-collections/community.general/pull/4275, https://github.com/ansible-collections/community.general/issues/4274).
- pacman - fixed bug where ``absent`` state did not work for locally installed packages (https://github.com/ansible-collections/community.general/pull/4464).
- pacman - make sure that ``packages`` is always returned when ``name`` or ``upgrade`` is specified, also if nothing is done (https://github.com/ansible-collections/community.general/pull/4329).
- pacman - when the ``update_cache`` option is combined with another option such as ``upgrade``, report ``changed`` based on the actions performed by the latter option. This was the behavior in community.general 4.4.0 and before. In community.general 4.5.0, a task combining these options would always report ``changed`` (https://github.com/ansible-collections/community.general/pull/4318).
- passwordstore lookup plugin - fix error detection for non-English locales (https://github.com/ansible-collections/community.general/pull/4219).
- passwordstore lookup plugin - prevent returning path names as passwords by accident (https://github.com/ansible-collections/community.general/issues/4185, https://github.com/ansible-collections/community.general/pull/4192).
- passwordstore lookup plugin - replace deprecated ``distutils.util.strtobool`` with Ansible's ``convert_bool.boolean`` to interpret values for the ``create``, ``returnall``, ``overwrite``, 'backup``, and ``nosymbols`` options (https://github.com/ansible-collections/community.general/pull/3934).
- pipx - passes the correct command line option ``--include-apps`` (https://github.com/ansible-collections/community.general/issues/3791).
- pritunl - fixed bug where pritunl plugin api add unneeded data in ``auth_string`` parameter (https://github.com/ansible-collections/community.general/issues/4527).
- proxmox - fixed ``onboot`` parameter causing module failures when undefined (https://github.com/ansible-collections/community.general/issues/3844).
- proxmox inventory plugin - always convert strings that follow the ``key=value[,key=value[...]]`` form into dictionaries (https://github.com/ansible-collections/community.general/pull/4349).
- proxmox inventory plugin - fix error when parsing container with LXC configs (https://github.com/ansible-collections/community.general/issues/4472, https://github.com/ansible-collections/community.general/pull/4472).
- proxmox inventory plugin - fixed the ``description`` field being ignored if it contained a comma (https://github.com/ansible-collections/community.general/issues/4348).
- proxmox inventory plugin - fixed the ``tags_parsed`` field when Proxmox returns a single space for the ``tags`` entry (https://github.com/ansible-collections/community.general/pull/4378).
- proxmox_kvm - fix a bug when getting a state of VM without name will fail (https://github.com/ansible-collections/community.general/pull/4508).
- proxmox_kvm - fix error in check when creating or cloning (https://github.com/ansible-collections/community.general/pull/4306).
- proxmox_kvm - fix error when checking whether Proxmox VM exists (https://github.com/ansible-collections/community.general/pull/4287).
- python_requirements_info - fails if version operator used without version (https://github.com/ansible-collections/community.general/pull/3785).
- python_requirements_info - store ``mismatched`` return values per package as documented in the module (https://github.com/ansible-collections/community.general/pull/4078).
- redfish_command - the iLO4 Redfish implementation only supports the ``image_url`` parameter in the underlying API calls to ``VirtualMediaInsert`` and ``VirtualMediaEject``. Any values set (or the defaults) for ``write_protected`` or ``inserted`` will be ignored (https://github.com/ansible-collections/community.general/pull/4596).
- say callback plugin - replace deprecated ``distutils.spawn.find_executable`` with Ansible's ``get_bin_path`` to find the ``say`` resp. ``espeak`` executables (https://github.com/ansible-collections/community.general/pull/3934).
- scaleway_user_data - fix double-quote added where no double-quote is needed to user data in scaleway's server (``Content-type`` -> ``Content-Type``) (https://github.com/ansible-collections/community.general/pull/3940).
- slack - add ``charset`` to HTTP headers to avoid Slack API warning (https://github.com/ansible-collections/community.general/issues/3932).
- terraform - fix command options being ignored during planned/plan in function ``build_plan`` such as ``lock`` or ``lock_timeout`` (https://github.com/ansible-collections/community.general/issues/3707, https://github.com/ansible-collections/community.general/pull/3726).
- terraform - fix list initialization to support both Python 2 and Python 3 (https://github.com/ansible-collections/community.general/issues/4531).
- vdo - fix options error (https://github.com/ansible-collections/community.general/pull/4163).
- xattr - fix exception caused by ``_run_xattr()`` raising a ``ValueError`` due to a mishandling of base64-encoded value (https://github.com/ansible-collections/community.general/issues/3673).
- xbps - fix error message that is reported when installing packages fails (https://github.com/ansible-collections/community.general/pull/4438).
- yarn - fix incorrect handling of ``yarn list`` and ``yarn global list`` output that could result in fatal error (https://github.com/ansible-collections/community.general/pull/4050).
- yarn - fix incorrectly reported status when installing a package globally (https://github.com/ansible-collections/community.general/issues/4045, https://github.com/ansible-collections/community.general/pull/4050).
- yarn - fix missing ``~`` expansion in yarn global install folder which resulted in incorrect task status (https://github.com/ansible-collections/community.general/issues/4045, https://github.com/ansible-collections/community.general/pull/4048).
- yum_versionlock - fix matching of existing entries with names passed to the module. Match yum and dnf lock format (https://github.com/ansible-collections/community.general/pull/4183).
- zone connection plugin - replace deprecated ``distutils.spawn.find_executable`` with Ansible's ``get_bin_path`` to find the executable (https://github.com/ansible-collections/community.general/pull/3934).
- zypper - fix undefined variable when running in check mode (https://github.com/ansible-collections/community.general/pull/4667).
- zypper - fixed bug that caused zypper to always report [ok] and do nothing on ``state=present`` when all packages in ``name`` had a version specification (https://github.com/ansible-collections/community.general/issues/4371, https://github.com/ansible-collections/community.general/pull/4421).

Known Issues
------------

- pacman - ``update_cache`` cannot differentiate between up to date and outdated package lists and will report ``changed`` in both situations (https://github.com/ansible-collections/community.general/pull/4318).
- pacman - binaries specified in the ``executable`` parameter must support ``--print-format`` in order to be used by this module. In particular, AUR helper ``yay`` is known not to currently support it (https://github.com/ansible-collections/community.general/pull/4312).

New Plugins
-----------

Filter
~~~~~~

- counter - Counts hashable elements in a sequence
