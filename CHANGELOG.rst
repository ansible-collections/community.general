===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 8.0.0.

v9.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- CmdRunner module utils - the parameter ``force_lang`` now supports the special value ``auto`` which will automatically try and determine the best parsable locale in the system (https://github.com/ansible-collections/community.general/pull/8517).
- proxmox - add ``disk_volume`` and ``mount_volumes`` keys for better readability (https://github.com/ansible-collections/community.general/pull/8542).
- proxmox - translate the old ``disk`` and ``mounts`` keys to the new handling internally (https://github.com/ansible-collections/community.general/pull/8542).
- proxmox_template - small refactor in logic for determining whether a template exists or not (https://github.com/ansible-collections/community.general/pull/8516).
- redfish_* modules - adds ``ciphers`` option for custom cipher selection (https://github.com/ansible-collections/community.general/pull/8533).
- sudosu become plugin - added an option (``alt_method``) to enhance compatibility with more versions of ``su`` (https://github.com/ansible-collections/community.general/pull/8214).
- virtualbox inventory plugin - expose a new parameter ``enable_advanced_group_parsing`` to change how the VirtualBox dynamic inventory parses VM groups (https://github.com/ansible-collections/community.general/issues/8508, https://github.com/ansible-collections/community.general/pull/8510).
- wdc_redfish_command - minor change to handle upgrade file for Redfish WD platforms (https://github.com/ansible-collections/community.general/pull/8444).

Bugfixes
--------

- bitwarden lookup plugin - fix ``KeyError`` in ``search_field`` (https://github.com/ansible-collections/community.general/issues/8549, https://github.com/ansible-collections/community.general/pull/8557).
- keycloak_clientscope - remove IDs from clientscope and its protocol mappers on comparison for changed check (https://github.com/ansible-collections/community.general/pull/8545).
- nsupdate - fix 'index out of range' error when changing NS records by falling back to authority section of the response (https://github.com/ansible-collections/community.general/issues/8612, https://github.com/ansible-collections/community.general/pull/8614).
- proxmox - fix idempotency on creation of mount volumes using Proxmox' special ``<storage>:<size>`` syntax (https://github.com/ansible-collections/community.general/issues/8407, https://github.com/ansible-collections/community.general/pull/8542).
- redfish_utils module utils - do not fail when language is not exactly "en" (https://github.com/ansible-collections/community.general/pull/8613).

New Plugins
-----------

Filter
~~~~~~

- community.general.reveal_ansible_type - Return input type.

Test
~~~~

- community.general.ansible_type - Validate input type.

v9.1.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- CmdRunner module util - argument formats can be specified as plain functions without calling ``cmd_runner_fmt.as_func()`` (https://github.com/ansible-collections/community.general/pull/8479).
- ansible_galaxy_install - add upgrade feature (https://github.com/ansible-collections/community.general/pull/8431, https://github.com/ansible-collections/community.general/issues/8351).
- cargo - add option ``directory``, which allows source directory to be specified (https://github.com/ansible-collections/community.general/pull/8480).
- cmd_runner module utils - add decorator ``cmd_runner_fmt.stack`` (https://github.com/ansible-collections/community.general/pull/8415).
- cmd_runner_fmt module utils - simplify implementation of ``cmd_runner_fmt.as_bool_not()`` (https://github.com/ansible-collections/community.general/pull/8512).
- ipa_dnsrecord - adds ``SSHFP`` record type for managing SSH fingerprints in FreeIPA DNS (https://github.com/ansible-collections/community.general/pull/8404).
- keycloak_client - assign auth flow by name (https://github.com/ansible-collections/community.general/pull/8428).
- openbsd_pkg - adds diff support to show changes in installed package list. This does not yet work for check mode (https://github.com/ansible-collections/community.general/pull/8402).
- proxmox - allow specification of the API port when using proxmox_* (https://github.com/ansible-collections/community.general/issues/8440, https://github.com/ansible-collections/community.general/pull/8441).
- proxmox_vm_info - add ``network`` option to retrieve current network information (https://github.com/ansible-collections/community.general/pull/8471).
- redfish_command - add ``wait`` and ``wait_timeout`` options to allow a user to block a command until a service is accessible after performing the requested command (https://github.com/ansible-collections/community.general/issues/8051, https://github.com/ansible-collections/community.general/pull/8434).
- redfish_info - add command ``CheckAvailability`` to check if a service is accessible (https://github.com/ansible-collections/community.general/issues/8051, https://github.com/ansible-collections/community.general/pull/8434).
- redis_info - adds support for getting cluster info (https://github.com/ansible-collections/community.general/pull/8464).

Deprecated Features
-------------------

- CmdRunner module util - setting the value of the ``ignore_none`` parameter within a ``CmdRunner`` context is deprecated and that feature should be removed in community.general 12.0.0 (https://github.com/ansible-collections/community.general/pull/8479).
- git_config - the ``list_all`` option has been deprecated and will be removed in community.general 11.0.0. Use the ``community.general.git_config_info`` module instead (https://github.com/ansible-collections/community.general/pull/8453).
- git_config - using ``state=present`` without providing ``value`` is deprecated and will be disallowed in community.general 11.0.0. Use the ``community.general.git_config_info`` module instead to read a value (https://github.com/ansible-collections/community.general/pull/8453).

Bugfixes
--------

- git_config - fix behavior of ``state=absent`` if ``value`` is present (https://github.com/ansible-collections/community.general/issues/8436, https://github.com/ansible-collections/community.general/pull/8452).
- keycloak_realm - add normalizations for ``attributes`` and ``protocol_mappers`` (https://github.com/ansible-collections/community.general/pull/8496).
- launched - correctly report changed status in check mode (https://github.com/ansible-collections/community.general/pull/8406).
- opennebula inventory plugin - fix invalid reference to IP when inventory runs against NICs with no IPv4 address (https://github.com/ansible-collections/community.general/pull/8489).
- opentelemetry callback - do not save the JSON response when using the ``ansible.builtin.uri`` module (https://github.com/ansible-collections/community.general/pull/8430).
- opentelemetry callback - do not save the content response when using the ``ansible.builtin.slurp`` module (https://github.com/ansible-collections/community.general/pull/8430).
- paman - do not fail if an empty list of packages has been provided and there is nothing to do (https://github.com/ansible-collections/community.general/pull/8514).

Known Issues
------------

- homectl - the module does not work under Python 3.13 or newer, since it relies on the removed ``crypt`` standard library module (https://github.com/ansible-collections/community.general/issues/4691, https://github.com/ansible-collections/community.general/pull/8497).
- udm_user - the module does not work under Python 3.13 or newer, since it relies on the removed ``crypt`` standard library module (https://github.com/ansible-collections/community.general/issues/4690, https://github.com/ansible-collections/community.general/pull/8497).

New Plugins
-----------

Filter
~~~~~~

- community.general.keep_keys - Keep specific keys from dictionaries in a list.
- community.general.remove_keys - Remove specific keys from dictionaries in a list.
- community.general.replace_keys - Replace specific keys in a list of dictionaries.

New Modules
-----------

- community.general.consul_agent_check - Add, modify, and delete checks within a consul cluster.
- community.general.consul_agent_service - Add, modify and delete services within a consul cluster.
- community.general.django_check - Wrapper for C(django-admin check).
- community.general.django_createcachetable - Wrapper for C(django-admin createcachetable).

v9.0.1
======

Release Summary
---------------

Bugfix release for inclusion in Ansible 10.0.0rc1.

Minor Changes
-------------

- ansible_galaxy_install - minor refactor in the module (https://github.com/ansible-collections/community.general/pull/8413).

Bugfixes
--------

- cpanm - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- django module utils - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- gconftool2_info - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- homebrew - do not fail when brew prints warnings (https://github.com/ansible-collections/community.general/pull/8406, https://github.com/ansible-collections/community.general/issues/7044).
- hponcfg - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- kernel_blacklist - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- keycloak_client - fix TypeError when sanitizing the ``saml.signing.private.key`` attribute in the module's diff or state output. The ``sanitize_cr`` function expected a dict where in some cases a list might occur (https://github.com/ansible-collections/community.general/pull/8403).
- locale_gen - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- mksysb - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- pipx_info - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- snap - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- snap_alias - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).

v9.0.0
======

Release Summary
---------------

This is release 9.0.0 of ``community.general``, released on 2024-05-20.

Minor Changes
-------------

- PythonRunner module utils - specialisation of ``CmdRunner`` to execute Python scripts (https://github.com/ansible-collections/community.general/pull/8289).
- Use offset-aware ``datetime.datetime`` objects (with timezone UTC) instead of offset-naive UTC timestamps, which are deprecated in Python 3.12 (https://github.com/ansible-collections/community.general/pull/8222).
- aix_lvol - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- apt_rpm - add new states ``latest`` and ``present_not_latest``. The value ``latest`` is equivalent to the current behavior of ``present``, which will upgrade a package if a newer version exists. ``present_not_latest`` does what most users would expect ``present`` to do: it does not upgrade if the package is already installed. The current behavior of ``present`` will be deprecated in a later version, and eventually changed to that of ``present_not_latest`` (https://github.com/ansible-collections/community.general/issues/8217, https://github.com/ansible-collections/community.general/pull/8247).
- apt_rpm - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- bitwarden lookup plugin - add ``bw_session`` option, to pass session key instead of reading from env (https://github.com/ansible-collections/community.general/pull/7994).
- bitwarden lookup plugin - add support to filter by organization ID (https://github.com/ansible-collections/community.general/pull/8188).
- bitwarden lookup plugin - allows to fetch all records of a given collection ID, by allowing to pass an empty value for ``search_value`` when ``collection_id`` is provided (https://github.com/ansible-collections/community.general/pull/8013).
- bitwarden lookup plugin - when looking for items using an item ID, the item is now accessed directly with ``bw get item`` instead of searching through all items. This doubles the lookup speed (https://github.com/ansible-collections/community.general/pull/7468).
- btrfs_subvolume - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- cmd_runner module_utils - add validation for minimum and maximum length in the value passed to ``cmd_runner_fmt.as_list()`` (https://github.com/ansible-collections/community.general/pull/8288).
- consul_auth_method, consul_binding_rule, consul_policy, consul_role, consul_session, consul_token - added action group ``community.general.consul`` (https://github.com/ansible-collections/community.general/pull/7897).
- consul_policy - added support for diff and check mode (https://github.com/ansible-collections/community.general/pull/7878).
- consul_policy, consul_role, consul_session - removed dependency on ``requests`` and factored out common parts (https://github.com/ansible-collections/community.general/pull/7826, https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - ``node_identities`` now expects a ``node_name`` option to match the Consul API, the old ``name`` is still supported as alias (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - ``service_identities`` now expects a ``service_name`` option to match the Consul API, the old ``name`` is still supported as alias (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - added support for diff mode (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - added support for templated policies (https://github.com/ansible-collections/community.general/pull/7878).
- elastic callback plugin - close elastic client to not leak resources (https://github.com/ansible-collections/community.general/pull/7517).
- filesystem - add bcachefs support (https://github.com/ansible-collections/community.general/pull/8126).
- gandi_livedns - adds support for personal access tokens (https://github.com/ansible-collections/community.general/issues/7639, https://github.com/ansible-collections/community.general/pull/8337).
- gconftool2 - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).
- git_config - allow multiple git configs for the same name with the new ``add_mode`` option (https://github.com/ansible-collections/community.general/pull/7260).
- git_config - the ``after`` and ``before`` fields in the ``diff`` of the return value can be a list instead of a string in case more configs with the same key are affected (https://github.com/ansible-collections/community.general/pull/7260).
- git_config - when a value is unset, all configs with the same key are unset (https://github.com/ansible-collections/community.general/pull/7260).
- gitlab modules - add ``ca_path`` option (https://github.com/ansible-collections/community.general/pull/7472).
- gitlab modules - remove duplicate ``gitlab`` package check (https://github.com/ansible-collections/community.general/pull/7486).
- gitlab_deploy_key, gitlab_group_members, gitlab_group_variable, gitlab_hook, gitlab_instance_variable, gitlab_project_badge, gitlab_project_variable, gitlab_user - improve API pagination and compatibility with different versions of ``python-gitlab`` (https://github.com/ansible-collections/community.general/pull/7790).
- gitlab_hook - adds ``releases_events`` parameter for supporting Releases events triggers on GitLab hooks (https://github.com/ansible-collections/community.general/pull/7956).
- gitlab_runner - add support for new runner creation workflow (https://github.com/ansible-collections/community.general/pull/7199).
- homebrew - adds ``force_formula`` parameter to disambiguate a formula from a cask of the same name (https://github.com/ansible-collections/community.general/issues/8274).
- homebrew, homebrew_cask - refactor common argument validation logic into a dedicated ``homebrew`` module utils (https://github.com/ansible-collections/community.general/issues/8323, https://github.com/ansible-collections/community.general/pull/8324).
- icinga2 inventory plugin - add Jinja2 templating support to ``url``, ``user``, and ``password`` paramenters (https://github.com/ansible-collections/community.general/issues/7074, https://github.com/ansible-collections/community.general/pull/7996).
- icinga2 inventory plugin - adds new parameter ``group_by_hostgroups`` in order to make grouping by Icinga2 hostgroups optional (https://github.com/ansible-collections/community.general/pull/7998).
- ini_file - add an optional parameter ``section_has_values``. If the target ini file contains more than one ``section``, use ``section_has_values`` to specify which one should be updated (https://github.com/ansible-collections/community.general/pull/7505).
- ini_file - support optional spaces between section names and their surrounding brackets (https://github.com/ansible-collections/community.general/pull/8075).
- installp - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- ipa_config - adds ``passkey`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7588).
- ipa_dnsrecord - adds ability to manage NS record types (https://github.com/ansible-collections/community.general/pull/7737).
- ipa_pwpolicy - refactor module and exchange a sequence ``if`` statements with a ``for`` loop (https://github.com/ansible-collections/community.general/pull/7723).
- ipa_pwpolicy - update module to support ``maxrepeat``, ``maxsequence``, ``dictcheck``, ``usercheck``, ``gracelimit`` parameters in FreeIPA password policies (https://github.com/ansible-collections/community.general/pull/7723).
- ipa_sudorule - adds options to include denied commands or command groups (https://github.com/ansible-collections/community.general/pull/7415).
- ipa_user - adds ``idp`` and ``passkey`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7589).
- irc - add ``validate_certs`` option, and rename ``use_ssl`` to ``use_tls``, while keeping ``use_ssl`` as an alias. The default value for ``validate_certs`` is ``false`` for backwards compatibility. We recommend to every user of this module to explicitly set ``use_tls=true`` and `validate_certs=true`` whenever possible, especially when communicating to IRC servers over the internet (https://github.com/ansible-collections/community.general/pull/7550).
- java_cert - add ``cert_content`` argument (https://github.com/ansible-collections/community.general/pull/8153).
- java_cert - enable ``owner``, ``group``, ``mode``, and other generic file arguments (https://github.com/ansible-collections/community.general/pull/8116).
- kernel_blacklist - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).
- keycloak module utils - expose error message from Keycloak server for HTTP errors in some specific situations (https://github.com/ansible-collections/community.general/pull/7645).
- keycloak_client, keycloak_clientscope, keycloak_clienttemplate - added ``docker-v2`` protocol support, enhancing alignment with Keycloak's protocol options (https://github.com/ansible-collections/community.general/issues/8215, https://github.com/ansible-collections/community.general/pull/8216).
- keycloak_realm_key - the ``config.algorithm`` option now supports 8 additional key algorithms (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_realm_key - the ``config.certificate`` option value is no longer defined with ``no_log=True`` (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_realm_key - the ``provider_id`` option now supports RSA encryption key usage (value ``rsa-enc``) (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_user_federation - add option for ``krbPrincipalAttribute`` (https://github.com/ansible-collections/community.general/pull/7538).
- keycloak_user_federation - allow custom user storage providers to be set through ``provider_id`` (https://github.com/ansible-collections/community.general/pull/7789).
- ldap_attrs - module now supports diff mode, showing which attributes are changed within an operation (https://github.com/ansible-collections/community.general/pull/8073).
- lvg - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- lvol - change ``pvs`` argument type to list of strings (https://github.com/ansible-collections/community.general/pull/7676, https://github.com/ansible-collections/community.general/issues/7504).
- lvol - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- lxd connection plugin - tighten the detection logic for lxd ``Instance not found`` errors, to avoid false detection on unrelated errors such as ``/usr/bin/python3: not found`` (https://github.com/ansible-collections/community.general/pull/7521).
- lxd_container - uses ``/1.0/instances`` API endpoint, if available. Falls back to ``/1.0/containers`` or ``/1.0/virtual-machines``. Fixes issue when using Incus or LXD 5.19 due to migrating to ``/1.0/instances`` endpoint (https://github.com/ansible-collections/community.general/pull/7980).
- macports - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- mail - add ``Message-ID`` header; which is required by some mail servers (https://github.com/ansible-collections/community.general/pull/7740).
- mail module, mail callback plugin - allow to configure the domain name of the Message-ID header with a new ``message_id_domain`` option (https://github.com/ansible-collections/community.general/pull/7765).
- mssql_script - adds transactional (rollback/commit) support via optional boolean param ``transaction`` (https://github.com/ansible-collections/community.general/pull/7976).
- netcup_dns - adds support for record types ``OPENPGPKEY``, ``SMIMEA``, and ``SSHFP`` (https://github.com/ansible-collections/community.general/pull/7489).
- nmcli - add support for new connection type ``loopback`` (https://github.com/ansible-collections/community.general/issues/6572).
- nmcli - adds OpenvSwitch support with new ``type`` values ``ovs-port``, ``ovs-interface``, and ``ovs-bridge``, and new ``slave_type`` value ``ovs-port`` (https://github.com/ansible-collections/community.general/pull/8154).
- nmcli - allow for ``infiniband`` slaves of ``bond`` interface types (https://github.com/ansible-collections/community.general/pull/7569).
- nmcli - allow for the setting of ``MTU`` for ``infiniband`` and ``bond`` interface types (https://github.com/ansible-collections/community.general/pull/7499).
- nmcli - allow setting ``MTU`` for ``bond-slave`` interface types (https://github.com/ansible-collections/community.general/pull/8118).
- onepassword lookup plugin - support 1Password Connect with the opv2 client by setting the connect_host and connect_token parameters (https://github.com/ansible-collections/community.general/pull/7116).
- onepassword_raw lookup plugin - support 1Password Connect with the opv2 client by setting the connect_host and connect_token parameters (https://github.com/ansible-collections/community.general/pull/7116)
- opentelemetry - add support for HTTP trace_exporter and configures the behavior via ``OTEL_EXPORTER_OTLP_TRACES_PROTOCOL`` (https://github.com/ansible-collections/community.general/issues/7888, https://github.com/ansible-collections/community.general/pull/8321).
- opentelemetry - add support for exporting spans in a file via ``ANSIBLE_OPENTELEMETRY_STORE_SPANS_IN_FILE`` (https://github.com/ansible-collections/community.general/issues/7888, https://github.com/ansible-collections/community.general/pull/8363).
- opkg - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).
- osx_defaults - add option ``check_types`` to enable changing the type of existing defaults on the fly (https://github.com/ansible-collections/community.general/pull/8173).
- parted - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- passwordstore - adds ``timestamp`` and ``preserve`` parameters to modify the stored password format (https://github.com/ansible-collections/community.general/pull/7426).
- passwordstore lookup - add ``missing_subkey`` parameter defining the behavior of the lookup when a passwordstore subkey is missing (https://github.com/ansible-collections/community.general/pull/8166).
- pipx - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).
- pkg5 - add support for non-silent execution (https://github.com/ansible-collections/community.general/issues/8379, https://github.com/ansible-collections/community.general/pull/8382).
- pkgin - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- portage - adds the possibility to explicitely tell portage to write packages to world file (https://github.com/ansible-collections/community.general/issues/6226, https://github.com/ansible-collections/community.general/pull/8236).
- portinstall - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- proxmox - adds ``startup`` parameters to configure startup order, startup delay and shutdown delay (https://github.com/ansible-collections/community.general/pull/8038).
- proxmox - adds ``template`` value to the ``state`` parameter, allowing conversion of container to a template (https://github.com/ansible-collections/community.general/pull/7143).
- proxmox - adds ``update`` parameter, allowing update of an already existing containers configuration (https://github.com/ansible-collections/community.general/pull/7540).
- proxmox inventory plugin - adds an option to exclude nodes from the dynamic inventory generation. The new setting is optional, not using this option will behave as usual (https://github.com/ansible-collections/community.general/issues/6714, https://github.com/ansible-collections/community.general/pull/7461).
- proxmox* modules - there is now a ``community.general.proxmox`` module defaults group that can be used to set default options for all Proxmox modules (https://github.com/ansible-collections/community.general/pull/8334).
- proxmox_disk - add ability to manipulate CD-ROM drive (https://github.com/ansible-collections/community.general/pull/7495).
- proxmox_kvm - add parameter ``update_unsafe`` to avoid limitations when updating dangerous values (https://github.com/ansible-collections/community.general/pull/7843).
- proxmox_kvm - adds ``template`` value to the ``state`` parameter, allowing conversion of a VM to a template (https://github.com/ansible-collections/community.general/pull/7143).
- proxmox_kvm - adds``usb`` parameter for setting USB devices on proxmox KVM VMs (https://github.com/ansible-collections/community.general/pull/8199).
- proxmox_kvm - support the ``hookscript`` parameter (https://github.com/ansible-collections/community.general/issues/7600).
- proxmox_ostype - it is now possible to specify the ``ostype`` when creating an LXC container (https://github.com/ansible-collections/community.general/pull/7462).
- proxmox_vm_info - add ability to retrieve configuration info (https://github.com/ansible-collections/community.general/pull/7485).
- puppet - new feature to set ``--waitforlock`` option (https://github.com/ansible-collections/community.general/pull/8282).
- redfish_command - add command ``ResetToDefaults`` to reset manager to default state (https://github.com/ansible-collections/community.general/issues/8163).
- redfish_config - add command ``SetServiceIdentification`` to set service identification (https://github.com/ansible-collections/community.general/issues/7916).
- redfish_info - add boolean return value ``MultipartHttpPush`` to ``GetFirmwareUpdateCapabilities`` (https://github.com/ansible-collections/community.general/issues/8194, https://github.com/ansible-collections/community.general/pull/8195).
- redfish_info - add command ``GetServiceIdentification`` to get service identification (https://github.com/ansible-collections/community.general/issues/7882).
- redfish_info - adding the ``BootProgress`` property when getting ``Systems`` info (https://github.com/ansible-collections/community.general/pull/7626).
- revbitspss lookup plugin - removed a redundant unicode prefix. The prefix was not necessary for Python 3 and has been cleaned up to streamline the code (https://github.com/ansible-collections/community.general/pull/8087).
- rundeck module utils - allow to pass ``Content-Type`` to API requests (https://github.com/ansible-collections/community.general/pull/7684).
- slackpkg - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- ssh_config - adds ``controlmaster``, ``controlpath`` and ``controlpersist`` parameters (https://github.com/ansible-collections/community.general/pull/7456).
- ssh_config - allow ``accept-new`` as valid value for ``strict_host_key_checking`` (https://github.com/ansible-collections/community.general/pull/8257).
- ssh_config - new feature to set ``AddKeysToAgent`` option to ``yes`` or ``no`` (https://github.com/ansible-collections/community.general/pull/7703).
- ssh_config - new feature to set ``IdentitiesOnly`` option to ``yes`` or ``no`` (https://github.com/ansible-collections/community.general/pull/7704).
- sudoers - add support for the ``NOEXEC`` tag in sudoers rules (https://github.com/ansible-collections/community.general/pull/7983).
- svr4pkg - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- swdepot - refactor module to pass list of arguments to ``module.run_command()`` instead of relying on interpretation by a shell (https://github.com/ansible-collections/community.general/pull/8264).
- terraform - add support for ``diff_mode`` for terraform resource_changes (https://github.com/ansible-collections/community.general/pull/7896).
- terraform - fix ``diff_mode`` in state ``absent`` and when terraform ``resource_changes`` does not exist (https://github.com/ansible-collections/community.general/pull/7963).
- xcc_redfish_command - added support for raw POSTs (``command=PostResource`` in ``category=Raw``) without a specific action info (https://github.com/ansible-collections/community.general/pull/7746).
- xfconf - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).
- xfconf_info - use ``ModuleHelper`` with ``VarDict`` (https://github.com/ansible-collections/community.general/pull/8226).

Breaking Changes / Porting Guide
--------------------------------

- cpanm - the default of the ``mode`` option changed from ``compatibility`` to ``new`` (https://github.com/ansible-collections/community.general/pull/8198).
- django_manage - the module now requires Django >= 4.1 (https://github.com/ansible-collections/community.general/pull/8198).
- django_manage - the module will now fail if ``virtualenv`` is specified but no virtual environment exists at that location (https://github.com/ansible-collections/community.general/pull/8198).
- redfish_command, redfish_config, redfish_info - change the default for ``timeout`` from 10 to 60 (https://github.com/ansible-collections/community.general/pull/8198).

Deprecated Features
-------------------

- MH DependencyCtxMgr module_utils - deprecate ``module_utils.mh.mixin.deps.DependencyCtxMgr`` in favour of ``module_utils.deps`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.AnsibleModule`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.DependencyCtxMgr`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.StateMixin`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.VarDict,`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.VarMeta`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate ``plugins.module_utils.module_helper.VarsMixin`` (https://github.com/ansible-collections/community.general/pull/8280).
- ModuleHelper module_utils - deprecate use of ``VarsMixin`` in favor of using the ``VardDict`` module_utils (https://github.com/ansible-collections/community.general/pull/8226).
- ModuleHelper vars module_utils - bump deprecation of ``VarMeta``, ``VarDict`` and ``VarsMixin`` to version 11.0.0 (https://github.com/ansible-collections/community.general/pull/8226).
- apt_rpm - the behavior of ``state=present`` and ``state=installed`` is deprecated and will change in community.general 11.0.0. Right now the module will upgrade a package to the latest version if one of these two states is used. You should explicitly use ``state=latest`` if you want this behavior, and switch to ``state=present_not_latest`` if you do not want to upgrade the package if it is already installed. In community.general 11.0.0 the behavior of ``state=present`` and ``state=installed`` will change to that of ``state=present_not_latest`` (https://github.com/ansible-collections/community.general/issues/8217, https://github.com/ansible-collections/community.general/pull/8285).
- consul_acl - the module has been deprecated and will be removed in community.general 10.0.0. ``consul_token`` and ``consul_policy`` can be used instead (https://github.com/ansible-collections/community.general/pull/7901).
- django_manage - the ``ack_venv_creation_deprecation`` option has no more effect and will be removed from community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/8198).
- gitlab modules - the basic auth method on GitLab API have been deprecated and will be removed in community.general 10.0.0 (https://github.com/ansible-collections/community.general/pull/8383).
- hipchat callback plugin - the hipchat service has been discontinued and the self-hosted variant has been End of Life since 2020. The callback plugin is therefore deprecated and will be removed from community.general 10.0.0 if nobody provides compelling reasons to still keep it (https://github.com/ansible-collections/community.general/issues/8184, https://github.com/ansible-collections/community.general/pull/8189).
- irc - the defaults ``false`` for ``use_tls`` and ``validate_certs`` have been deprecated and will change to ``true`` in community.general 10.0.0 to improve security. You can already improve security now by explicitly setting them to ``true``. Specifying values now disables the deprecation warning (https://github.com/ansible-collections/community.general/pull/7578).

Removed Features (previously deprecated)
----------------------------------------

- The deprecated redirects for internal module names have been removed. These internal redirects were extra-long FQCNs like ``community.general.packaging.os.apt_rpm`` that redirect to the short FQCN ``community.general.apt_rpm``. They were originally needed to implement flatmapping; as various tooling started to recommend users to use the long names flatmapping was removed from the collection and redirects were added for users who already followed these incorrect recommendations (https://github.com/ansible-collections/community.general/pull/7835).
- ansible_galaxy_install - the ``ack_ansible29`` and ``ack_min_ansiblecore211`` options have been removed. They no longer had any effect (https://github.com/ansible-collections/community.general/pull/8198).
- cloudflare_dns - remove support for SPF records. These are no longer supported by CloudFlare (https://github.com/ansible-collections/community.general/pull/7782).
- django_manage - support for the ``command`` values ``cleanup``, ``syncdb``, and ``validate`` were removed. Use ``clearsessions``, ``migrate``, and ``check`` instead, respectively (https://github.com/ansible-collections/community.general/pull/8198).
- flowdock - this module relied on HTTPS APIs that do not exist anymore and was thus removed (https://github.com/ansible-collections/community.general/pull/8198).
- mh.mixins.deps module utils - the ``DependencyMixin`` has been removed. Use the ``deps`` module utils instead (https://github.com/ansible-collections/community.general/pull/8198).
- proxmox - the ``proxmox_default_behavior`` option has been removed (https://github.com/ansible-collections/community.general/pull/8198).
- rax* modules, rax module utils, rax docs fragment - the Rackspace modules relied on the deprecated package ``pyrax`` and were thus removed (https://github.com/ansible-collections/community.general/pull/8198).
- redhat module utils - the classes ``Rhsm``, ``RhsmPool``, and ``RhsmPools`` have been removed (https://github.com/ansible-collections/community.general/pull/8198).
- redhat_subscription - the alias ``autosubscribe`` of the ``auto_attach`` option was removed (https://github.com/ansible-collections/community.general/pull/8198).
- stackdriver - this module relied on HTTPS APIs that do not exist anymore and was thus removed (https://github.com/ansible-collections/community.general/pull/8198).
- webfaction_* modules - these modules relied on HTTPS APIs that do not exist anymore and were thus removed (https://github.com/ansible-collections/community.general/pull/8198).

Security Fixes
--------------

- cobbler, gitlab_runners, icinga2, linode, lxd, nmap, online, opennebula, proxmox, scaleway, stackpath_compute, virtualbox, and xen_orchestra inventory plugin - make sure all data received from the remote servers is marked as unsafe, so remote code execution by obtaining texts that can be evaluated as templates is not possible (https://www.die-welt.net/2024/03/remote-code-execution-in-ansible-dynamic-inventory-plugins/, https://github.com/ansible-collections/community.general/pull/8098).
- keycloak_identity_provider - the client secret was not correctly sanitized by the module. The return values ``proposed``, ``existing``, and ``end_state``, as well as the diff, did contain the client secret unmasked (https://github.com/ansible-collections/community.general/pull/8355).

Bugfixes
--------

- aix_filesystem - fix ``_validate_vg`` not passing VG name to ``lsvg_cmd`` (https://github.com/ansible-collections/community.general/issues/8151).
- aix_filesystem - fix issue with empty list items in crfs logic and option order (https://github.com/ansible-collections/community.general/pull/8052).
- apt-rpm - the module did not upgrade packages if a newer version exists. Now the package will be reinstalled if the candidate is newer than the installed version (https://github.com/ansible-collections/community.general/issues/7414).
- apt_rpm - when checking whether packages were installed after running ``apt-get -y install <packages>``, only the last package name was checked (https://github.com/ansible-collections/community.general/pull/8263).
- bitwarden_secrets_manager lookup plugin - implements retry with exponential backoff to avoid lookup errors when Bitwardn's API rate limiting is encountered (https://github.com/ansible-collections/community.general/issues/8230, https://github.com/ansible-collections/community.general/pull/8238).
- cargo - fix idempotency issues when using a custom installation path for packages (using the ``--path`` parameter). The initial installation runs fine, but subsequent runs use the ``get_installed()`` function which did not check the given installation location, before running ``cargo install``. This resulted in a false ``changed`` state. Also the removal of packeges using ``state: absent`` failed, as the installation check did not use the given parameter (https://github.com/ansible-collections/community.general/pull/7970).
- cloudflare_dns - fix Cloudflare lookup of SHFP records (https://github.com/ansible-collections/community.general/issues/7652).
- consul_token - fix token creation without ``accessor_id`` (https://github.com/ansible-collections/community.general/pull/8091).
- from_ini filter plugin - disabling interpolation of ``ConfigParser`` to allow converting values with a ``%`` sign (https://github.com/ansible-collections/community.general/issues/8183, https://github.com/ansible-collections/community.general/pull/8185).
- gitlab_group_members - fix gitlab constants call in ``gitlab_group_members`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_issue - fix behavior to search GitLab issue, using ``search`` keyword instead of ``title`` (https://github.com/ansible-collections/community.general/issues/7846).
- gitlab_issue, gitlab_label, gitlab_milestone - avoid crash during version comparison when the python-gitlab Python module is not installed (https://github.com/ansible-collections/community.general/pull/8158).
- gitlab_project_members - fix gitlab constants call in ``gitlab_project_members`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_protected_branches - fix gitlab constants call in ``gitlab_protected_branches`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_runner - fix pagination when checking for existing runners (https://github.com/ansible-collections/community.general/pull/7790).
- gitlab_user - fix gitlab constants call in ``gitlab_user`` module (https://github.com/ansible-collections/community.general/issues/7467).
- haproxy - fix an issue where HAProxy could get stuck in DRAIN mode when the backend was unreachable (https://github.com/ansible-collections/community.general/issues/8092).
- homebrew - detect already installed formulae and casks using JSON output from ``brew info`` (https://github.com/ansible-collections/community.general/issues/864).
- homebrew - error returned from brew command was ignored and tried to parse empty JSON. Fix now checks for an error and raises it to give accurate error message to users (https://github.com/ansible-collections/community.general/issues/8047).
- incus connection plugin - treats ``inventory_hostname`` as a variable instead of a literal in remote connections (https://github.com/ansible-collections/community.general/issues/7874).
- interface_files - also consider ``address_family`` when changing ``option=method`` (https://github.com/ansible-collections/community.general/issues/7610, https://github.com/ansible-collections/community.general/pull/7612).
- inventory plugins - add unsafe wrapper to avoid marking strings that do not contain ``{`` or ``}`` as unsafe, to work around a bug in AWX ((https://github.com/ansible-collections/community.general/issues/8212, https://github.com/ansible-collections/community.general/pull/8225).
- ipa - fix get version regex in IPA module_utils (https://github.com/ansible-collections/community.general/pull/8175).
- ipa_hbacrule - the module uses a string for ``ipaenabledflag`` for new FreeIPA versions while the returned value is a boolean (https://github.com/ansible-collections/community.general/pull/7880).
- ipa_otptoken - the module expect ``ipatokendisabled`` as string but the ``ipatokendisabled`` value is returned as a boolean (https://github.com/ansible-collections/community.general/pull/7795).
- ipa_sudorule - the module uses a string for ``ipaenabledflag`` for new FreeIPA versions while the returned value is a boolean (https://github.com/ansible-collections/community.general/pull/7880).
- iptables_state - fix idempotency issues when restoring incomplete iptables dumps (https://github.com/ansible-collections/community.general/issues/8029).
- irc - replace ``ssl.wrap_socket`` that was removed from Python 3.12 with code for creating a proper SSL context (https://github.com/ansible-collections/community.general/pull/7542).
- keycloak_* - fix Keycloak API client to quote ``/`` properly (https://github.com/ansible-collections/community.general/pull/7641).
- keycloak_authz_permission - resource payload variable for scope-based permission was constructed as a string, when it needs to be a list, even for a single item (https://github.com/ansible-collections/community.general/issues/7151).
- keycloak_client - add sorted ``defaultClientScopes`` and ``optionalClientScopes`` to normalizations (https://github.com/ansible-collections/community.general/pull/8223).
- keycloak_client - fixes issue when metadata is provided in desired state when task is in check mode (https://github.com/ansible-collections/community.general/issues/1226, https://github.com/ansible-collections/community.general/pull/7881).
- keycloak_identity_provider - ``mappers`` processing was not idempotent if the mappers configuration list had not been sorted by name (in ascending order). Fix resolves the issue by sorting mappers in the desired state using the same key which is used for obtaining existing state (https://github.com/ansible-collections/community.general/pull/7418).
- keycloak_identity_provider - it was not possible to reconfigure (add, remove) ``mappers`` once they were created initially. Removal was ignored, adding new ones resulted in dropping the pre-existing unmodified mappers. Fix resolves the issue by supplying correct input to the internal update call (https://github.com/ansible-collections/community.general/pull/7418).
- keycloak_realm - add normalizations for ``enabledEventTypes`` and ``supportedLocales`` (https://github.com/ansible-collections/community.general/pull/8224).
- keycloak_user - when ``force`` is set, but user does not exist, do not try to delete it (https://github.com/ansible-collections/community.general/pull/7696).
- keycloak_user_federation - fix diff of empty ``krbPrincipalAttribute`` (https://github.com/ansible-collections/community.general/pull/8320).
- ldap - previously the order number (if present) was expected to follow an equals sign in the DN. This makes it so the order number string is identified correctly anywhere within the DN (https://github.com/ansible-collections/community.general/issues/7646).
- linode inventory plugin - add descriptive error message for linode inventory plugin (https://github.com/ansible-collections/community.general/pull/8133).
- log_entries callback plugin - replace ``ssl.wrap_socket`` that was removed from Python 3.12 with code for creating a proper SSL context (https://github.com/ansible-collections/community.general/pull/7542).
- lvol - test for output messages in both ``stdout`` and ``stderr`` (https://github.com/ansible-collections/community.general/pull/7601, https://github.com/ansible-collections/community.general/issues/7182).
- merge_variables lookup plugin - fixing cross host merge: providing access to foreign hosts variables to the perspective of the host that is performing the merge (https://github.com/ansible-collections/community.general/pull/8303).
- modprobe - listing modules files or modprobe files could trigger a FileNotFoundError if ``/etc/modprobe.d`` or ``/etc/modules-load.d`` did not exist. Relevant functions now return empty lists if the directories do not exist to avoid crashing the module (https://github.com/ansible-collections/community.general/issues/7717).
- mssql_script - make the module work with Python 2 (https://github.com/ansible-collections/community.general/issues/7818, https://github.com/ansible-collections/community.general/pull/7821).
- nmcli - fix ``connection.slave-type`` wired to ``bond`` and not with parameter ``slave_type`` in case of connection type ``wifi`` (https://github.com/ansible-collections/community.general/issues/7389).
- ocapi_utils, oci_utils, redfish_utils module utils - replace ``type()`` calls with ``isinstance()`` calls (https://github.com/ansible-collections/community.general/pull/7501).
- onepassword lookup plugin - failed for fields that were in sections and had uppercase letters in the label/ID. Field lookups are now case insensitive in all cases (https://github.com/ansible-collections/community.general/pull/7919).
- onepassword lookup plugin - field and section titles are now case insensitive when using op CLI version two or later. This matches the behavior of version one (https://github.com/ansible-collections/community.general/pull/7564).
- opentelemetry callback plugin - close spans always (https://github.com/ansible-collections/community.general/pull/8367).
- opentelemetry callback plugin - honour the ``disable_logs`` option to avoid storing task results since they are not used regardless (https://github.com/ansible-collections/community.general/pull/8373).
- pacemaker_cluster - actually implement check mode, which the module claims to support. This means that until now the module also did changes in check mode (https://github.com/ansible-collections/community.general/pull/8081).
- pam_limits - when the file does not exist, do not create it in check mode (https://github.com/ansible-collections/community.general/issues/8050, https://github.com/ansible-collections/community.general/pull/8057).
- pipx module utils - change the CLI argument formatter for the ``pip_args`` parameter (https://github.com/ansible-collections/community.general/issues/7497, https://github.com/ansible-collections/community.general/pull/7506).
- pkgin - pkgin (pkgsrc package manager used by SmartOS) raises erratic exceptions and spurious ``changed=true`` (https://github.com/ansible-collections/community.general/pull/7971).
- proxmox - fix updating a container config if the setting does not already exist (https://github.com/ansible-collections/community.general/pull/7872).
- proxmox_kvm - fixed status check getting from node-specific API endpoint (https://github.com/ansible-collections/community.general/issues/7817).
- proxmox_kvm - running ``state=template`` will first check whether VM is already a template (https://github.com/ansible-collections/community.general/pull/7792).
- proxmox_pool_member - absent state for type VM did not delete VMs from the pools (https://github.com/ansible-collections/community.general/pull/7464).
- puppet - add option ``environment_lang`` to set the environment language encoding. Defaults to lang ``C``. It is recommended to set it to ``C.UTF-8`` or ``en_US.UTF-8`` depending on what is available on your system. (https://github.com/ansible-collections/community.general/issues/8000)
- redfish_command - fix usage of message parsing in ``SimpleUpdate`` and ``MultipartHTTPPushUpdate`` commands to treat the lack of a ``MessageId`` as no message (https://github.com/ansible-collections/community.general/issues/7465, https://github.com/ansible-collections/community.general/pull/7471).
- redfish_info - allow for a GET operation invoked by ``GetUpdateStatus`` to allow for an empty response body for cases where a service returns 204 No Content (https://github.com/ansible-collections/community.general/issues/8003).
- redfish_info - correct uncaught exception when attempting to retrieve ``Chassis`` information (https://github.com/ansible-collections/community.general/pull/7952).
- redhat_subscription - use the D-Bus registration on RHEL 7 only on 7.4 and
  greater; older versions of RHEL 7 do not have it
  (https://github.com/ansible-collections/community.general/issues/7622,
  https://github.com/ansible-collections/community.general/pull/7624).
- riak - support ``riak admin`` sub-command in newer Riak KV versions beside the legacy ``riak-admin`` main command (https://github.com/ansible-collections/community.general/pull/8211).
- statusio_maintenance - fix error caused by incorrectly formed API data payload. Was raising "Failed to create maintenance HTTP Error 400 Bad Request" caused by bad data type for date/time and deprecated dict keys (https://github.com/ansible-collections/community.general/pull/7754).
- terraform - fix multiline string handling in complex variables (https://github.com/ansible-collections/community.general/pull/7535).
- to_ini filter plugin - disabling interpolation of ``ConfigParser`` to allow converting values with a ``%`` sign (https://github.com/ansible-collections/community.general/issues/8183, https://github.com/ansible-collections/community.general/pull/8185).
- xml - make module work with lxml 5.1.1, which removed some internals that the module was relying on (https://github.com/ansible-collections/community.general/pull/8169).

New Plugins
-----------

Become
~~~~~~

- community.general.run0 - Systemd's run0.

Callback
~~~~~~~~

- community.general.default_without_diff - The default ansible callback without diff output.
- community.general.timestamp - Adds simple timestamp for each header.

Connection
~~~~~~~~~~

- community.general.incus - Run tasks in Incus instances via the Incus CLI.

Filter
~~~~~~

- community.general.from_ini - Converts INI text input into a dictionary.
- community.general.lists_difference - Difference of lists with a predictive order.
- community.general.lists_intersect - Intersection of lists with a predictive order.
- community.general.lists_symmetric_difference - Symmetric Difference of lists with a predictive order.
- community.general.lists_union - Union of lists with a predictive order.
- community.general.to_ini - Converts a dictionary to the INI file format.

Lookup
~~~~~~

- community.general.github_app_access_token - Obtain short-lived Github App Access tokens.
- community.general.onepassword_doc - Fetch documents stored in 1Password.

Test
~~~~

- community.general.fqdn_valid - Validates fully-qualified domain names against RFC 1123.

New Modules
-----------

- community.general.consul_acl_bootstrap - Bootstrap ACLs in Consul.
- community.general.consul_auth_method - Manipulate Consul auth methods.
- community.general.consul_binding_rule - Manipulate Consul binding rules.
- community.general.consul_token - Manipulate Consul tokens.
- community.general.django_command - Run Django admin commands.
- community.general.dnf_config_manager - Enable or disable dnf repositories using config-manager.
- community.general.git_config_info - Read git configuration.
- community.general.gitlab_group_access_token - Manages GitLab group access tokens.
- community.general.gitlab_issue - Create, update, or delete GitLab issues.
- community.general.gitlab_label - Creates/updates/deletes GitLab Labels belonging to project or group.
- community.general.gitlab_milestone - Creates/updates/deletes GitLab Milestones belonging to project or group.
- community.general.gitlab_project_access_token - Manages GitLab project access tokens.
- community.general.keycloak_client_rolescope - Allows administration of Keycloak client roles scope to restrict the usage of certain roles to a other specific client applications.
- community.general.keycloak_component_info - Retrive component info in Keycloak.
- community.general.keycloak_realm_rolemapping - Allows administration of Keycloak realm role mappings into groups with the Keycloak API.
- community.general.nomad_token - Manage Nomad ACL tokens.
- community.general.proxmox_node_info - Retrieve information about one or more Proxmox VE nodes.
- community.general.proxmox_storage_contents_info - List content from a Proxmox VE storage.
- community.general.usb_facts - Allows listing information about USB devices.
