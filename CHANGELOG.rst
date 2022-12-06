===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 5.0.0.

v6.1.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- cmd_runner module utils - ``cmd_runner_fmt.as_bool()`` can now take an extra parameter to format when value is false (https://github.com/ansible-collections/community.general/pull/5647).
- gconftool2 - refactor using ``ModuleHelper`` and ``CmdRunner`` (https://github.com/ansible-collections/community.general/pull/5545).
- java_certs - add more detailed error output when extracting certificate from PKCS12 fails (https://github.com/ansible-collections/community.general/pull/5550).
- jenkins_plugin - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5565).
- lxd_project - refactored code out to module utils to clear sanity check (https://github.com/ansible-collections/community.general/pull/5549).
- nmap inventory plugin - add new options ``udp_scan``, ``icmp_timestamp``, and ``dns_resolve`` for different types of scans (https://github.com/ansible-collections/community.general/pull/5566).
- rax_scaling_group - refactored out code to the ``rax`` module utils to clear the sanity check (https://github.com/ansible-collections/community.general/pull/5563).
- redfish_command - add ``PerformRequestedOperations`` command to perform any operations necessary to continue the update flow (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_command - add ``update_apply_time`` to ``SimpleUpdate`` command (https://github.com/ansible-collections/community.general/issues/3910).
- redfish_command - add ``update_status`` to output of ``SimpleUpdate`` command to allow a user monitor the update in progress (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_info - add ``GetUpdateStatus`` command to check the progress of a previous update request (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_utils module utils - added PUT (``put_request()``) functionality (https://github.com/ansible-collections/community.general/pull/5490).
- slack - add option ``prepend_hash`` which allows to control whether a ``#`` is prepended to ``channel_id``. The current behavior (value ``auto``) is to prepend ``#`` unless some specific prefixes are found. That list of prefixes is incomplete, and there does not seem to exist a documented condition on when exactly ``#`` must not be prepended. We recommend to explicitly set ``prepend_hash=always`` or ``prepend_hash=never`` to avoid any ambiguity (https://github.com/ansible-collections/community.general/pull/5629).
- spotinst_aws_elastigroup - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5553).
- ssh_config - add ``host_key_algorithms`` option (https://github.com/ansible-collections/community.general/pull/5605).
- udm_share - added ``elements`` attribute to ``list`` type parameters (https://github.com/ansible-collections/community.general/pull/5557).
- udm_user - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5559).

Deprecated Features
-------------------

- The ``sap`` modules ``sapcar_extract``, ``sap_task_list_execute``, and ``hana_query``, will be removed from this collection in community.general 7.0.0 and replaced with redirects to ``community.sap_libs``. If you want to continue using these modules, make sure to also install ``community.sap_libs`` (it is part of the Ansible package) (https://github.com/ansible-collections/community.general/pull/5614).

Bugfixes
--------

- chroot connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/5570).
- cmd_runner module utils - fixed bug when handling default cases in ``cmd_runner_fmt.as_map()`` (https://github.com/ansible-collections/community.general/pull/5538).
- cmd_runner module utils - formatting arguments ``cmd_runner_fmt.as_fixed()`` was expecting an non-existing argument (https://github.com/ansible-collections/community.general/pull/5538).
- keycloak_client_rolemapping - calculate ``proposed`` and ``after`` return values properly (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_client_rolemapping - remove only listed mappings with ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5619).
- proxmox inventory plugin - fix bug while templating when using templates for the ``url``, ``user``, ``password``, ``token_id``, or ``token_secret`` options (https://github.com/ansible-collections/community.general/pull/5640).
- proxmox inventory plugin - handle tags delimited by semicolon instead of comma, which happens from Proxmox 7.3 on (https://github.com/ansible-collections/community.general/pull/5602).
- redhat_subscription - do not ignore ``consumer_name`` and other variables if ``activationkey`` is specified (https://github.com/ansible-collections/community.general/issues/3486, https://github.com/ansible-collections/community.general/pull/5627).
- redhat_subscription - do not pass arguments to ``subscription-manager register`` for things already configured; now a specified ``rhsm_baseurl`` is properly set for subscription-manager (https://github.com/ansible-collections/community.general/pull/5583).
- unixy callback plugin - fix plugin to work with ansible-core 2.14 by using Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).
- vdo - now uses ``yaml.safe_load()`` to parse command output instead of the deprecated ``yaml.load()`` which is potentially unsafe. Using ``yaml.load()`` without explicitely setting a ``Loader=`` is also an error in pyYAML 6.0 (https://github.com/ansible-collections/community.general/pull/5632).
- vmadm - fix for index out of range error in ``get_vm_uuid`` (https://github.com/ansible-collections/community.general/pull/5628).

New Modules
-----------

- gitlab_project_badge - Manage project badges on GitLab Server
- keycloak_clientsecret_info - Retrieve client secret via Keycloak API
- keycloak_clientsecret_regenerate - Regenerate Keycloak client secret via Keycloak API

v6.0.1
======

Release Summary
---------------

Bugfix release for Ansible 7.0.0.

Bugfixes
--------

- dependent lookup plugin - avoid warning on deprecated parameter for ``Templar.template()`` (https://github.com/ansible-collections/community.general/pull/5543).
- jenkins_build - fix the logical flaw when deleting a Jenkins build (https://github.com/ansible-collections/community.general/pull/5514).
- one_vm - avoid splitting labels that are ``None`` (https://github.com/ansible-collections/community.general/pull/5489).
- onepassword_raw - add missing parameter to plugin documentation (https://github.com/ansible-collections/community.general/issues/5506).
- proxmox_disk - avoid duplicate ``vmid`` reference (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5493).

v6.0.0
======

Release Summary
---------------

New major release of community.general with lots of bugfixes, new features, some removed deprecated features, and some other breaking changes. Please check the coresponding sections of the changelog for more details.

Major Changes
-------------

- The internal structure of the collection was changed for modules and action plugins. These no longer live in a directory hierarchy ordered by topic, but instead are now all in a single (flat) directory. This has no impact on users *assuming they did not use internal FQCNs*. These will still work, but result in deprecation warnings. They were never officially supported and thus the redirects are kept as a courtsey, and this is not labelled as a breaking change. Note that for example the Ansible VScode plugin started recommending these internal names. If you followed its recommendation, you will now have to change back to the short names to avoid deprecation warnings, and potential errors in the future as these redirects will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5461).
- newrelic_deployment - removed New Relic v1 API, added support for v2 API (https://github.com/ansible-collections/community.general/pull/5341).

Minor Changes
-------------

- Added MIT license as ``LICENSES/MIT.txt`` for tests/unit/plugins/modules/packaging/language/test_gem.py (https://github.com/ansible-collections/community.general/pull/5065).
- All software licenses are now in the ``LICENSES/`` directory of the collection root (https://github.com/ansible-collections/community.general/pull/5065, https://github.com/ansible-collections/community.general/pull/5079, https://github.com/ansible-collections/community.general/pull/5080, https://github.com/ansible-collections/community.general/pull/5083, https://github.com/ansible-collections/community.general/pull/5087, https://github.com/ansible-collections/community.general/pull/5095, https://github.com/ansible-collections/community.general/pull/5098, https://github.com/ansible-collections/community.general/pull/5106).
- ModuleHelper module utils - added property ``verbosity`` to base class (https://github.com/ansible-collections/community.general/pull/5035).
- ModuleHelper module utils - improved ``ModuleHelperException``, using ``to_native()`` for the exception message (https://github.com/ansible-collections/community.general/pull/4755).
- The collection repository conforms to the `REUSE specification <https://reuse.software/spec/>`__ except for the changelog fragments (https://github.com/ansible-collections/community.general/pull/5138).
- ali_instance - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5240).
- ali_instance_info - minor refactor when checking for installed dependency (https://github.com/ansible-collections/community.general/pull/5240).
- alternatives - add ``state=absent`` to be able to remove an alternative (https://github.com/ansible-collections/community.general/pull/4654).
- alternatives - add ``subcommands`` parameter (https://github.com/ansible-collections/community.general/pull/4654).
- ansible_galaxy_install - minor refactoring using latest ``ModuleHelper`` updates (https://github.com/ansible-collections/community.general/pull/4752).
- ansible_galaxy_install - refactored module to use ``CmdRunner`` to execute ``ansible-galaxy`` (https://github.com/ansible-collections/community.general/pull/5477).
- apk - add ``world`` parameter for supporting a custom world file (https://github.com/ansible-collections/community.general/pull/4976).
- bitwarden lookup plugin - add option ``search`` to search for other attributes than name (https://github.com/ansible-collections/community.general/pull/5297).
- cartesian lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- cmd_runner module util - added parameters ``check_mode_skip`` and ``check_mode_return`` to ``CmdRunner.context()``, so that the command is not executed when ``check_mode=True`` (https://github.com/ansible-collections/community.general/pull/4736).
- cmd_runner module utils - add ``__call__`` method to invoke context (https://github.com/ansible-collections/community.general/pull/4791).
- consul - adds ``ttl`` parameter for session  (https://github.com/ansible-collections/community.general/pull/4996).
- consul - minor refactoring (https://github.com/ansible-collections/community.general/pull/5367).
- consul_session - adds ``token`` parameter for session (https://github.com/ansible-collections/community.general/pull/5193).
- cpanm - refactored module to use ``CmdRunner`` to execute ``cpanm`` (https://github.com/ansible-collections/community.general/pull/5485).
- cpanm - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- credstash lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- dependent lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- dig lookup plugin - add option ``fail_on_error`` to allow stopping execution on lookup failures (https://github.com/ansible-collections/community.general/pull/4973).
- dig lookup plugin - start using Ansible's configuration manager to parse options. All documented options can now also be passed as lookup parameters (https://github.com/ansible-collections/community.general/pull/5440).
- dnstxt lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- filetree lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- flattened lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
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
- hiera lookup plugin - start using Ansible's configuration manager to parse options. The Hiera executable and config file can now also be passed as lookup parameters (https://github.com/ansible-collections/community.general/pull/5440).
- homebrew, homebrew_tap - added Homebrew on Linux path to defaults (https://github.com/ansible-collections/community.general/pull/5241).
- hponcfg - refactored module to use ``CmdRunner`` to execute ``hponcfg`` (https://github.com/ansible-collections/community.general/pull/5483).
- keycloak_* modules - add ``http_agent`` parameter with default value ``Ansible`` (https://github.com/ansible-collections/community.general/issues/5023).
- keyring lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- lastpass - use config manager for handling plugin options (https://github.com/ansible-collections/community.general/pull/5022).
- ldap_attrs - allow for DNs to have ``{x}`` prefix on first RDN (https://github.com/ansible-collections/community.general/issues/977, https://github.com/ansible-collections/community.general/pull/5450).
- linode inventory plugin - simplify option handling (https://github.com/ansible-collections/community.general/pull/5438).
- listen_ports_facts - add new ``include_non_listening`` option which adds ``-a`` option to ``netstat`` and ``ss``. This shows both listening and non-listening (for TCP this means established connections) sockets, and returns ``state`` and ``foreign_address`` (https://github.com/ansible-collections/community.general/issues/4762, https://github.com/ansible-collections/community.general/pull/4953).
- lmdb_kv lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- lxc_container - minor refactoring (https://github.com/ansible-collections/community.general/pull/5358).
- machinectl become plugin - can now be used with a password from another user than root, if a polkit rule is present (https://github.com/ansible-collections/community.general/pull/4849).
- machinectl become plugin - combine the success command when building the become command to be consistent with other become plugins (https://github.com/ansible-collections/community.general/pull/5287).
- manifold lookup plugin - start using Ansible's configuration manager to parse options (https://github.com/ansible-collections/community.general/pull/5440).
- maven_artifact - add a new ``unredirected_headers`` option that can be used with ansible-core 2.12 and above. The default value is to not use ``Authorization`` and ``Cookie`` headers on redirects for security reasons. With ansible-core 2.11, all headers are still passed on for redirects (https://github.com/ansible-collections/community.general/pull/4812).
- mksysb - refactored module to use ``CmdRunner`` to execute ``mksysb`` (https://github.com/ansible-collections/community.general/pull/5484).
- mksysb - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- nagios - minor refactoring on parameter validation for different actions (https://github.com/ansible-collections/community.general/pull/5239).
- netcup_dnsapi - add ``timeout`` parameter (https://github.com/ansible-collections/community.general/pull/5301).
- nmcli - add ``transport_mode`` configuration for Infiniband devices (https://github.com/ansible-collections/community.general/pull/5361).
- nmcli - add bond option ``xmit_hash_policy`` to bond options (https://github.com/ansible-collections/community.general/issues/5148).
- nmcli - adds ``vpn`` type and parameter for supporting VPN with service type L2TP and PPTP (https://github.com/ansible-collections/community.general/pull/4746).
- nmcli - honor IP options for VPNs (https://github.com/ansible-collections/community.general/pull/5228).
- onepassword - support version 2 of the OnePassword CLI (https://github.com/ansible-collections/community.general/pull/4728)
- opentelemetry callback plugin - allow configuring opentelementry callback via config file (https://github.com/ansible-collections/community.general/pull/4916).
- opentelemetry callback plugin - send logs. This can be disabled by setting ``disable_logs=false`` (https://github.com/ansible-collections/community.general/pull/4175).
- pacman - added parameters ``reason`` and ``reason_for`` to set/change the install reason of packages (https://github.com/ansible-collections/community.general/pull/4956).
- passwordstore lookup plugin - allow options to be passed lookup options instead of being part of the term strings (https://github.com/ansible-collections/community.general/pull/5444).
- passwordstore lookup plugin - allow using alternative password managers by detecting wrapper scripts, allow explicit configuration of pass and gopass backends (https://github.com/ansible-collections/community.general/issues/4766).
- passwordstore lookup plugin - improve error messages to include stderr (https://github.com/ansible-collections/community.general/pull/5436)
- pipx - added state ``latest`` to the module (https://github.com/ansible-collections/community.general/pull/5105).
- pipx - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/5085).
- pipx - module fails faster when ``name`` is missing for states ``upgrade`` and ``reinstall`` (https://github.com/ansible-collections/community.general/pull/5100).
- pipx - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- pipx module utils - created new module util ``pipx`` providing a ``cmd_runner`` specific for the ``pipx`` module (https://github.com/ansible-collections/community.general/pull/5085).
- portage - add knobs for Portage's ``--backtrack`` and ``--with-bdeps`` options (https://github.com/ansible-collections/community.general/pull/5349).
- portage - use Portage's python module instead of calling gentoolkit-provided program in shell (https://github.com/ansible-collections/community.general/pull/5349).
- proxmox inventory plugin - added new flag ``qemu_extended_statuses`` and new groups ``<group_prefix>prelaunch``, ``<group_prefix>paused``. They will be populated only when ``want_facts=true``, ``qemu_extended_statuses=true`` and only for ``QEMU`` machines (https://github.com/ansible-collections/community.general/pull/4723).
- proxmox inventory plugin - simplify option handling code (https://github.com/ansible-collections/community.general/pull/5437).
- proxmox module utils, the proxmox* modules - add ``api_task_ok`` helper to standardize API task status checks across all proxmox modules (https://github.com/ansible-collections/community.general/pull/5274).
- proxmox_kvm - allow ``agent`` argument to be a string (https://github.com/ansible-collections/community.general/pull/5107).
- proxmox_snap - add ``unbind`` param to support snapshotting containers with configured mountpoints (https://github.com/ansible-collections/community.general/pull/5274).
- puppet - adds ``confdir`` parameter to configure a custom confir location (https://github.com/ansible-collections/community.general/pull/4740).
- redfish - added new command GetVirtualMedia, VirtualMediaInsert and VirtualMediaEject to Systems category due to Redfish spec changes the virtualMedia resource location from Manager to System (https://github.com/ansible-collections/community.general/pull/5124).
- redfish_config - add ``SetSessionService`` to set default session timeout policy (https://github.com/ansible-collections/community.general/issues/5008).
- redfish_info - add ``GetManagerInventory`` to report list of Manager inventory information (https://github.com/ansible-collections/community.general/issues/4899).
- seport - added new argument ``local`` (https://github.com/ansible-collections/community.general/pull/5203)
- snap - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- sudoers - will attempt to validate the proposed sudoers rule using visudo if available, optionally skipped, or required (https://github.com/ansible-collections/community.general/pull/4794, https://github.com/ansible-collections/community.general/issues/4745).
- terraform - adds capability to handle complex variable structures for ``variables`` parameter in the module. This must be enabled with the new ``complex_vars`` parameter (https://github.com/ansible-collections/community.general/pull/4797).
- terraform - run ``terraform init`` with ``-no-color`` not to mess up the stdout of the task (https://github.com/ansible-collections/community.general/pull/5147).
- wdc_redfish_command - add ``IndicatorLedOn`` and ``IndicatorLedOff`` commands for ``Chassis`` category (https://github.com/ansible-collections/community.general/pull/5059).
- wdc_redfish_command - add ``PowerModeLow`` and ``PowerModeNormal`` commands for ``Chassis`` category (https://github.com/ansible-collections/community.general/pull/5145).
- xfconf - add ``stdout``, ``stderr`` and ``cmd`` to the module results (https://github.com/ansible-collections/community.general/pull/5037).
- xfconf - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/4776).
- xfconf - use ``do_raise()`` instead of defining custom exception class (https://github.com/ansible-collections/community.general/pull/4975).
- xfconf - using ``do_raise()`` to raise exceptions in ``ModuleHelper`` derived modules (https://github.com/ansible-collections/community.general/pull/4674).
- xfconf module utils - created new module util ``xfconf`` providing a ``cmd_runner`` specific for ``xfconf`` modules (https://github.com/ansible-collections/community.general/pull/4776).
- xfconf_info - changed implementation to use ``cmd_runner`` (https://github.com/ansible-collections/community.general/pull/4776).
- xfconf_info - use ``do_raise()`` instead of defining custom exception class (https://github.com/ansible-collections/community.general/pull/4975).
- znode - possibility to use ZooKeeper ACL authentication (https://github.com/ansible-collections/community.general/pull/5306).

Breaking Changes / Porting Guide
--------------------------------

- newrelic_deployment - ``revision`` is required for v2 API (https://github.com/ansible-collections/community.general/pull/5341).
- scaleway_container_registry_info - no longer replace ``secret_environment_variables`` in the output by ``SENSITIVE_VALUE`` (https://github.com/ansible-collections/community.general/pull/5497).

Deprecated Features
-------------------

- ArgFormat module utils - deprecated along ``CmdMixin``, in favor of the ``cmd_runner_fmt`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdMixin module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdModuleHelper module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- CmdStateModuleHelper module utils - deprecated in favor of the ``CmdRunner`` module util (https://github.com/ansible-collections/community.general/pull/5370).
- cmd_runner module utils - deprecated ``fmt`` in favour of ``cmd_runner_fmt`` as the parameter format object (https://github.com/ansible-collections/community.general/pull/4777).
- django_manage - support for Django releases older than 4.1 has been deprecated and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5400).
- django_manage - support for the commands ``cleanup``, ``syncdb`` and ``validate`` that have been deprecated in Django long time ago will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5400).
- django_manage - the behavior of "creating the virtual environment when missing" is being deprecated and will be removed in community.general version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5405).
- gconftool2 - deprecates ``state=get`` in favor of using the module ``gconftool2_info`` (https://github.com/ansible-collections/community.general/pull/4778).
- lxc_container - the module will no longer make any effort to support Python 2 (https://github.com/ansible-collections/community.general/pull/5304).
- newrelic_deployment - ``appname`` and ``environment`` are no longer valid options in the v2 API. They will be removed in community.general 7.0.0 (https://github.com/ansible-collections/community.general/pull/5341).
- proxmox - deprecated the current ``unprivileged`` default value, will be changed to ``true`` in community.general 7.0.0 (https://github.com/pull/5224).
- xfconf - deprecated parameter ``disable_facts``, as since version 4.0.0 it only allows value ``true`` (https://github.com/ansible-collections/community.general/pull/4520).

Removed Features (previously deprecated)
----------------------------------------

- bitbucket* modules - ``username`` is no longer an alias of ``workspace``, but of ``user`` (https://github.com/ansible-collections/community.general/pull/5326).
- gem - the default of the ``norc`` option changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/5326).
- gitlab_group_members - ``gitlab_group`` must now always contain the full path, and no longer just the name or path (https://github.com/ansible-collections/community.general/pull/5326).
- keycloak_authentication - the return value ``flow`` has been removed. Use ``end_state`` instead (https://github.com/ansible-collections/community.general/pull/5326).
- keycloak_group - the return value ``group`` has been removed. Use ``end_state`` instead (https://github.com/ansible-collections/community.general/pull/5326).
- lxd_container - the default of the ``ignore_volatile_options`` option changed from ``true`` to ``false`` (https://github.com/ansible-collections/community.general/pull/5326).
- mail callback plugin - the ``sender`` option is now required (https://github.com/ansible-collections/community.general/pull/5326).
- module_helper module utils - remove the ``VarDict`` attribute from ``ModuleHelper``. Import ``VarDict`` from ``ansible_collections.community.general.plugins.module_utils.mh.mixins.vars`` instead (https://github.com/ansible-collections/community.general/pull/5326).
- proxmox inventory plugin - the default of the ``want_proxmox_nodes_ansible_host`` option changed from ``true`` to ``false`` (https://github.com/ansible-collections/community.general/pull/5326).
- vmadm - the ``debug`` option has been removed. It was not used anyway (https://github.com/ansible-collections/community.general/pull/5326).

Bugfixes
--------

- Include ``PSF-license.txt`` file for ``plugins/module_utils/_mount.py``.
- Include ``simplified_bsd.txt`` license file for various module utils, the ``lxca_common`` docs fragment, and the ``utm_utils`` unit tests.
- alternatives - do not set the priority if the priority was not set by the user (https://github.com/ansible-collections/community.general/pull/4810).
- alternatives - only pass subcommands when they are specified as module arguments (https://github.com/ansible-collections/community.general/issues/4803, https://github.com/ansible-collections/community.general/issues/4804, https://github.com/ansible-collections/community.general/pull/4836).
- alternatives - when ``subcommands`` is specified, ``link`` must be given for every subcommand. This was already mentioned in the documentation, but not enforced by the code (https://github.com/ansible-collections/community.general/pull/4836).
- apache2_mod_proxy - avoid crash when reporting inability to parse balancer_member_page HTML caused by using an undefined variable in the error message (https://github.com/ansible-collections/community.general/pull/5111).
- archive - avoid crash when ``lzma`` is not present and ``format`` is not ``xz`` (https://github.com/ansible-collections/community.general/pull/5393).
- cmd_runner module utils - fix bug caused by using the ``command`` variable instead of ``self.command`` when looking for binary path (https://github.com/ansible-collections/community.general/pull/4903).
- consul - fixed bug introduced in PR 4590 (https://github.com/ansible-collections/community.general/issues/4680).
- credstash lookup plugin - pass plugin options to credstash for all terms, not just for the first (https://github.com/ansible-collections/community.general/pull/5440).
- dig lookup plugin - add option to return empty result without empty strings, and return empty list instead of ``NXDOMAIN`` (https://github.com/ansible-collections/community.general/pull/5439, https://github.com/ansible-collections/community.general/issues/5428).
- dig lookup plugin - fix evaluation of falsy values for boolean parameters ``fail_on_error`` and ``retry_servfail`` (https://github.com/ansible-collections/community.general/pull/5129).
- dnsimple_info - correctly report missing library as ``requests`` and not ``another_library`` (https://github.com/ansible-collections/community.general/pull/5111).
- dnstxt lookup plugin - add option to return empty result without empty strings, and return empty list instead of ``NXDOMAIN`` (https://github.com/ansible-collections/community.general/pull/5457, https://github.com/ansible-collections/community.general/issues/5428).
- dsv lookup plugin - do not ignore the ``tld`` parameter (https://github.com/ansible-collections/community.general/pull/4911).
- filesystem - handle ``fatresize --info`` output lines without ``:`` (https://github.com/ansible-collections/community.general/pull/4700).
- filesystem - improve error messages when output cannot be parsed by including newlines in escaped form (https://github.com/ansible-collections/community.general/pull/4700).
- funcd connection plugin - fix signature of ``exec_command`` (https://github.com/ansible-collections/community.general/pull/5111).
- ini_file - minor refactor fixing a python lint error (https://github.com/ansible-collections/community.general/pull/5307).
- iso_create - the module somtimes failed to add folders for Joliet and UDF formats (https://github.com/ansible-collections/community.general/issues/5275).
- keycloak_realm - fix default groups and roles (https://github.com/ansible-collections/community.general/issues/4241).
- keyring_info - fix the result from the keyring library never getting returned (https://github.com/ansible-collections/community.general/pull/4964).
- ldap_attrs - fix bug which caused a ``Bad search filter`` error. The error was occuring when the ldap attribute value contained special characters such as ``(`` or ``*`` (https://github.com/ansible-collections/community.general/issues/5434, https://github.com/ansible-collections/community.general/pull/5435).
- ldap_attrs - fix ordering issue by ignoring the ``{x}`` prefix on attribute values (https://github.com/ansible-collections/community.general/issues/977, https://github.com/ansible-collections/community.general/pull/5385).
- listen_ports_facts - removed leftover ``EnvironmentError`` . The ``else`` clause had a wrong indentation. The check is now handled in the ``split_pid_name`` function (https://github.com/ansible-collections/community.general/pull/5202).
- locale_gen - fix support for Ubuntu (https://github.com/ansible-collections/community.general/issues/5281).
- lxc_container - the module has been updated to support Python 3 (https://github.com/ansible-collections/community.general/pull/5304).
- lxd connection plugin - fix incorrect ``inventory_hostname`` in ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/issues/4886).
- manageiq_alert_profiles - avoid crash when reporting unknown profile caused by trying to return an undefined variable (https://github.com/ansible-collections/community.general/pull/5111).
- nmcli - avoid changed status for most cases with VPN connections (https://github.com/ansible-collections/community.general/pull/5126).
- nmcli - fix error caused by adding undefined module arguments for list options (https://github.com/ansible-collections/community.general/issues/4373, https://github.com/ansible-collections/community.general/pull/4813).
- nmcli - fix error when setting previously unset MAC address, ``gsm.apn`` or ``vpn.data``: current values were being normalized without checking if they might be ``None`` (https://github.com/ansible-collections/community.general/pull/5291).
- nmcli - fix int options idempotence (https://github.com/ansible-collections/community.general/issues/4998).
- nsupdate - compatibility with NS records (https://github.com/ansible-collections/community.general/pull/5112).
- nsupdate - fix silent failures when updating ``NS`` entries from Bind9 managed DNS zones (https://github.com/ansible-collections/community.general/issues/4657).
- opentelemetry callback plugin - support opentelemetry-api 1.13.0 that removed support for ``_time_ns`` (https://github.com/ansible-collections/community.general/pull/5342).
- osx_defaults - no longer expand ``~`` in ``value`` to the user's home directory, or expand environment variables (https://github.com/ansible-collections/community.general/issues/5234, https://github.com/ansible-collections/community.general/pull/5243).
- packet_ip_subnet - fix error reporting in case of invalid CIDR prefix lengths (https://github.com/ansible-collections/community.general/pull/5111).
- pacman - fixed name resolution of URL packages (https://github.com/ansible-collections/community.general/pull/4959).
- passwordstore lookup plugin - fix ``returnall`` for gopass (https://github.com/ansible-collections/community.general/pull/5027).
- passwordstore lookup plugin - fix password store path detection for gopass (https://github.com/ansible-collections/community.general/pull/4955).
- pfexec become plugin - remove superflous quotes preventing exe wrap from working as expected (https://github.com/ansible-collections/community.general/issues/3671, https://github.com/ansible-collections/community.general/pull/3889).
- pip_package_info - remove usage of global variable (https://github.com/ansible-collections/community.general/pull/5111).
- pkgng - fix case when ``pkg`` fails when trying to upgrade all packages (https://github.com/ansible-collections/community.general/issues/5363).
- proxmox - fix error handling when getting VM by name when ``state=absent`` (https://github.com/ansible-collections/community.general/pull/4945).
- proxmox inventory plugin - fix crash when ``enabled=1`` is used in agent config string (https://github.com/ansible-collections/community.general/pull/4910).
- proxmox inventory plugin - fixed extended status detection for qemu (https://github.com/ansible-collections/community.general/pull/4816).
- proxmox_kvm - fix ``agent`` parameter when boolean value is specified (https://github.com/ansible-collections/community.general/pull/5198).
- proxmox_kvm - fix error handling when getting VM by name when ``state=absent`` (https://github.com/ansible-collections/community.general/pull/4945).
- proxmox_kvm - fix exception when no ``agent`` argument is specified (https://github.com/ansible-collections/community.general/pull/5194).
- proxmox_kvm - fix wrong condition (https://github.com/ansible-collections/community.general/pull/5108).
- proxmox_kvm - replace new condition with proper condition to allow for using ``vmid`` on update (https://github.com/ansible-collections/community.general/pull/5206).
- rax_clb_nodes - fix code to be compatible with Python 3 (https://github.com/ansible-collections/community.general/pull/4933).
- redfish_command - fix the check if a virtual media is unmounted to just check for ``instered= false`` caused by Supermicro hardware that does not clear the ``ImageName`` (https://github.com/ansible-collections/community.general/pull/4839).
- redfish_command - the Supermicro Redfish implementation only supports the ``image_url`` parameter in the underlying API calls to ``VirtualMediaInsert`` and ``VirtualMediaEject``. Any values set (or the defaults) for ``write_protected`` or ``inserted`` will be ignored (https://github.com/ansible-collections/community.general/pull/4839).
- redfish_info - fix to ``GetChassisPower`` to correctly report power information when multiple chassis exist, but not all chassis report power information (https://github.com/ansible-collections/community.general/issues/4901).
- redfish_utils module utils - centralize payload checking when performing modification requests to a Redfish service (https://github.com/ansible-collections/community.general/issues/5210/).
- redhat_subscription - fix unsubscribing on RHEL 9 (https://github.com/ansible-collections/community.general/issues/4741).
- redhat_subscription - make module idempotent when ``pool_ids`` are used (https://github.com/ansible-collections/community.general/issues/5313).
- redis* modules - fix call to ``module.fail_json`` when failing because of missing Python libraries (https://github.com/ansible-collections/community.general/pull/4733).
- slack - fix incorrect channel prefix ``#`` caused by incomplete pattern detection by adding ``G0`` and ``GF`` as channel ID patterns (https://github.com/ansible-collections/community.general/pull/5019).
- slack - fix message update for channels which start with ``CP``. When ``message-id`` was passed it failed for channels which started with ``CP`` because the ``#`` symbol was added before the ``channel_id`` (https://github.com/ansible-collections/community.general/pull/5249).
- snap - allow values in the ``options`` parameter to contain whitespaces (https://github.com/ansible-collections/community.general/pull/5475).
- sudoers - ensure sudoers config files are created with the permissions requested by sudoers (0440) (https://github.com/ansible-collections/community.general/pull/4814).
- sudoers - fix incorrect handling of ``state: absent`` (https://github.com/ansible-collections/community.general/issues/4852).
- tss lookup plugin - adding support for updated Delinea library (https://github.com/DelineaXPM/python-tss-sdk/issues/9, https://github.com/ansible-collections/community.general/pull/5151).
- virtualbox inventory plugin - skip parsing values with keys that have both a value and nested data. Skip parsing values that are nested more than two keys deep (https://github.com/ansible-collections/community.general/issues/5332, https://github.com/ansible-collections/community.general/pull/5348).
- xcc_redfish_command - for compatibility due to Redfish spec changes the virtualMedia resource location changed from Manager to System (https://github.com/ansible-collections/community.general/pull/4682).
- xenserver_facts - fix broken ``AnsibleModule`` call that prevented the module from working at all (https://github.com/ansible-collections/community.general/pull/5383).
- xfconf - fix setting of boolean values (https://github.com/ansible-collections/community.general/issues/4999, https://github.com/ansible-collections/community.general/pull/5007).
- zfs - fix wrong quoting of properties (https://github.com/ansible-collections/community.general/issues/4707, https://github.com/ansible-collections/community.general/pull/4726).

New Plugins
-----------

Filter
~~~~~~

- counter - Counts hashable elements in a sequence

Lookup
~~~~~~

- bitwarden - Retrieve secrets from Bitwarden

New Modules
-----------

- gconftool2_info - Retrieve GConf configurations
- iso_customize - Add/remove/change files in ISO file
- keycloak_user_rolemapping - Allows administration of Keycloak user_rolemapping with the Keycloak API
- keyring - Set or delete a passphrase using the Operating System's native keyring
- keyring_info - Get a passphrase using the Operating System's native keyring
- manageiq_policies_info - Listing of resource policy_profiles in ManageIQ
- manageiq_tags_info - Retrieve resource tags in ManageIQ
- pipx_info - Rretrieves information about applications installed with pipx
- proxmox_disk - Management of a disk of a Qemu(KVM) VM in a Proxmox VE cluster.
- scaleway_compute_private_network - Scaleway compute - private network management
- scaleway_container - Scaleway Container management
- scaleway_container_info - Retrieve information on Scaleway Container
- scaleway_container_namespace - Scaleway Container namespace management
- scaleway_container_namespace_info - Retrieve information on Scaleway Container namespace
- scaleway_container_registry - Scaleway Container registry management module
- scaleway_container_registry_info - Scaleway Container registry info module
- scaleway_function - Scaleway Function management
- scaleway_function_info - Retrieve information on Scaleway Function
- scaleway_function_namespace - Scaleway Function namespace management
- scaleway_function_namespace_info - Retrieve information on Scaleway Function namespace
- wdc_redfish_command - Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
- wdc_redfish_info - Manages WDC UltraStar Data102 Out-Of-Band controllers using Redfish APIs
