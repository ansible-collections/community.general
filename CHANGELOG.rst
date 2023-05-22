===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 6.0.0.

v7.0.1
======

Release Summary
---------------

Bugfix release for Ansible 8.0.0rc1.

Bugfixes
--------

- nmcli - fix bond option ``xmit_hash_policy`` (https://github.com/ansible-collections/community.general/pull/6527).
- portage - fix ``changed_use`` and ``newuse`` not triggering rebuilds (https://github.com/ansible-collections/community.general/issues/6008, https://github.com/ansible-collections/community.general/pull/6548).
- proxmox_tasks_info - remove ``api_user`` + ``api_password`` constraint from ``required_together`` as it causes to require ``api_password`` even when API token param is used (https://github.com/ansible-collections/community.general/issues/6201).
- zypper - added handling of zypper exitcode 102. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook (https://github.com/ansible-collections/community.general/pull/6534).

v7.0.0
======

Release Summary
---------------

This is release 7.0.0 of ``community.general``, released on 2023-05-09.

Minor Changes
-------------

- apache2_module - add module argument ``warn_mpm_absent`` to control whether warning are raised in some edge cases (https://github.com/ansible-collections/community.general/pull/5793).
- apt_rpm - adds ``clean``, ``dist_upgrade`` and ``update_kernel``  parameters for clear caches, complete upgrade system, and upgrade kernel packages (https://github.com/ansible-collections/community.general/pull/5867).
- bitwarden lookup plugin - can now retrieve secrets from custom fields (https://github.com/ansible-collections/community.general/pull/5694).
- bitwarden lookup plugin - implement filtering results by ``collection_id`` parameter (https://github.com/ansible-collections/community.general/issues/5849).
- cmd_runner module utils - ``cmd_runner_fmt.as_bool()`` can now take an extra parameter to format when value is false (https://github.com/ansible-collections/community.general/pull/5647).
- cpanm - minor change, use feature from ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/6385).
- dconf - be forgiving about boolean values: convert them to GVariant booleans automatically (https://github.com/ansible-collections/community.general/pull/6206).
- dconf - if ``gi.repository.GLib`` is missing, try to respawn in a Python interpreter that has it (https://github.com/ansible-collections/community.general/pull/6491).
- dconf - minor refactoring improving parameters and dependencies validation (https://github.com/ansible-collections/community.general/pull/6336).
- dconf - parse GVariants for equality comparison when the Python module ``gi.repository`` is available (https://github.com/ansible-collections/community.general/pull/6049).
- deps module utils - add function ``failed()`` providing the ability to check the dependency check result without triggering an exception (https://github.com/ansible-collections/community.general/pull/6383).
- dig lookup plugin - Support multiple domains to be queried as indicated in docs (https://github.com/ansible-collections/community.general/pull/6334).
- dig lookup plugin - support CAA record type (https://github.com/ansible-collections/community.general/pull/5913).
- dnsimple - set custom User-Agent for API requests to DNSimple (https://github.com/ansible-collections/community.general/pull/5927).
- dnsimple_info - minor refactor in the code (https://github.com/ansible-collections/community.general/pull/6440).
- flatpak_remote - add new boolean option ``enabled``. It controls, whether the remote is enabled or not (https://github.com/ansible-collections/community.general/pull/5926).
- gconftool2 - refactor using ``ModuleHelper`` and ``CmdRunner`` (https://github.com/ansible-collections/community.general/pull/5545).
- gitlab_group_variable, gitlab_project_variable - refactor function out to module utils (https://github.com/ansible-collections/community.general/pull/6384).
- gitlab_project - add ``builds_access_level``, ``container_registry_access_level`` and ``forking_access_level`` options (https://github.com/ansible-collections/community.general/pull/5706).
- gitlab_project - add ``releases_access_level``, ``environments_access_level``, ``feature_flags_access_level``, ``infrastructure_access_level``, ``monitor_access_level``, and ``security_and_compliance_access_level`` options (https://github.com/ansible-collections/community.general/pull/5986).
- gitlab_project - add new option ``topics`` for adding topics to GitLab projects (https://github.com/ansible-collections/community.general/pull/6278).
- gitlab_runner - add new boolean option ``access_level_on_creation``. It controls, whether the value of ``access_level`` is used for runner registration or not. The option ``access_level`` has been ignored on registration so far and was only used on updates (https://github.com/ansible-collections/community.general/issues/5907, https://github.com/ansible-collections/community.general/pull/5908).
- gitlab_runner - allow to register group runner (https://github.com/ansible-collections/community.general/pull/3935).
- homebrew_cask - allows passing ``--greedy`` option to ``upgrade_all`` (https://github.com/ansible-collections/community.general/pull/6267).
- idrac_redfish_command - add ``job_id`` to ``CreateBiosConfigJob`` response (https://github.com/ansible-collections/community.general/issues/5603).
- ilo_redfish_utils module utils - change implementation of DNS Server IP and NTP Server IP update (https://github.com/ansible-collections/community.general/pull/5804).
- ipa_group - allow to add and remove external users with the ``external_user`` option (https://github.com/ansible-collections/community.general/pull/5897).
- ipa_hostgroup - add ``append`` parameter for adding a new hosts to existing hostgroups without changing existing hostgroup members (https://github.com/ansible-collections/community.general/pull/6203).
- iptables_state - minor refactoring within the module (https://github.com/ansible-collections/community.general/pull/5844).
- java_certs - add more detailed error output when extracting certificate from PKCS12 fails (https://github.com/ansible-collections/community.general/pull/5550).
- jc filter plugin - added the ability to use parser plugins (https://github.com/ansible-collections/community.general/pull/6043).
- jenkins_plugin - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5565).
- jira - add worklog functionality (https://github.com/ansible-collections/community.general/issues/6209, https://github.com/ansible-collections/community.general/pull/6210).
- keycloak_authentication - add flow type option to sub flows to allow the creation of 'form-flow' sub flows like in Keycloak's built-in registration flow (https://github.com/ansible-collections/community.general/pull/6318).
- keycloak_group - add new optional module parameter ``parents`` to properly handle keycloak subgroups (https://github.com/ansible-collections/community.general/pull/5814).
- keycloak_user_federation - make ``org.keycloak.storage.ldap.mappers.LDAPStorageMapper`` the default value for mappers ``providerType`` (https://github.com/ansible-collections/community.general/pull/5863).
- ldap modules - add ``ca_path`` option (https://github.com/ansible-collections/community.general/pull/6185).
- ldap modules - add ``xorder_discovery`` option (https://github.com/ansible-collections/community.general/issues/6045, https://github.com/ansible-collections/community.general/pull/6109).
- ldap_search - the new ``base64_attributes`` allows to specify which attribute values should be Base64 encoded (https://github.com/ansible-collections/community.general/pull/6473).
- lxd_container - add diff and check mode (https://github.com/ansible-collections/community.general/pull/5866).
- lxd_project - refactored code out to module utils to clear sanity check (https://github.com/ansible-collections/community.general/pull/5549).
- make - add ``command`` return value to the module output (https://github.com/ansible-collections/community.general/pull/6160).
- mattermost, rocketchat, slack - replace missing default favicon with docs.ansible.com favicon (https://github.com/ansible-collections/community.general/pull/5928).
- mksysb - improved the output of the module in case of errors (https://github.com/ansible-collections/community.general/issues/6263).
- modprobe - add ``persistent`` option (https://github.com/ansible-collections/community.general/issues/4028, https://github.com/ansible-collections/community.general/pull/542).
- module_helper module utils - updated the imports to make more MH features available at ``plugins/module_utils/module_helper.py`` (https://github.com/ansible-collections/community.general/pull/6464).
- mssql_script - allow for ``GO`` statement to be mixed-case for scripts not using strict syntax (https://github.com/ansible-collections/community.general/pull/6457).
- mssql_script - handle error condition for empty resultsets to allow for non-returning SQL statements (for example ``UPDATE`` and ``INSERT``) (https://github.com/ansible-collections/community.general/pull/6457).
- mssql_script - improve batching logic to allow a wider variety of input scripts. For example, SQL scripts slurped from Windows machines which may contain carriage return (''\r'') characters (https://github.com/ansible-collections/community.general/pull/6457).
- nmap inventory plugin - add new option ``open`` for only returning open ports (https://github.com/ansible-collections/community.general/pull/6200).
- nmap inventory plugin - add new option ``port`` for port specific scan (https://github.com/ansible-collections/community.general/pull/6165).
- nmap inventory plugin - add new options ``udp_scan``, ``icmp_timestamp``, and ``dns_resolve`` for different types of scans (https://github.com/ansible-collections/community.general/pull/5566).
- nmap inventory plugin - added environment variables for configure ``address`` and ``exclude`` (https://github.com/ansible-collections/community.general/issues/6351).
- nmcli - add ``default`` and ``default-or-eui64`` to the list of valid choices for ``addr_gen_mode6`` parameter (https://github.com/ansible-collections/community.general/pull/5974).
- nmcli - add ``macvlan`` connection type (https://github.com/ansible-collections/community.general/pull/6312).
- nmcli - add support for ``team.runner-fast-rate`` parameter for ``team`` connections (https://github.com/ansible-collections/community.general/issues/6065).
- nmcli - new module option ``slave_type`` added to allow creation of various types of slave devices (https://github.com/ansible-collections/community.general/issues/473, https://github.com/ansible-collections/community.general/pull/6108).
- one_vm - add a new ``updateconf`` option which implements the ``one.vm.updateconf`` API call (https://github.com/ansible-collections/community.general/pull/5812).
- openbsd_pkg - set ``TERM`` to ``'dumb'`` in ``execute_command()`` to make module less dependant on the ``TERM`` environment variable set on the Ansible controller (https://github.com/ansible-collections/community.general/pull/6149).
- opkg - allow installing a package in a certain version (https://github.com/ansible-collections/community.general/pull/5688).
- opkg - refactored module to use ``CmdRunner`` for executing ``opkg`` (https://github.com/ansible-collections/community.general/pull/5718).
- osx_defaults - include stderr in error messages (https://github.com/ansible-collections/community.general/pull/6011).
- pipx - add ``system_site_packages`` parameter to give application access to system-wide packages (https://github.com/ansible-collections/community.general/pull/6308).
- pipx - ensure ``include_injected`` parameter works with ``state=upgrade`` and ``state=latest`` (https://github.com/ansible-collections/community.general/pull/6212).
- pipx - optional ``install_apps`` parameter added to install applications from injected packages (https://github.com/ansible-collections/community.general/pull/6198).
- proxmox - added new module parameter ``tags`` for use with PVE 7+ (https://github.com/ansible-collections/community.general/pull/5714).
- proxmox - suppress urllib3 ``InsecureRequestWarnings`` when ``validate_certs`` option is ``false`` (https://github.com/ansible-collections/community.general/pull/5931).
- proxmox_kvm - add new ``archive`` parameter. This is needed to create a VM from an archive (backup) (https://github.com/ansible-collections/community.general/pull/6159).
- proxmox_kvm - adds ``migrate`` parameter to manage online migrations between hosts (https://github.com/ansible-collections/community.general/pull/6448)
- puppet - add new options ``skip_tags`` to exclude certain tagged resources during a puppet agent or apply (https://github.com/ansible-collections/community.general/pull/6293).
- puppet - refactored module to use ``CmdRunner`` for executing ``puppet`` (https://github.com/ansible-collections/community.general/pull/5612).
- rax_scaling_group - refactored out code to the ``rax`` module utils to clear the sanity check (https://github.com/ansible-collections/community.general/pull/5563).
- redfish_command - add ``PerformRequestedOperations`` command to perform any operations necessary to continue the update flow (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_command - add ``update_apply_time`` to ``SimpleUpdate`` command (https://github.com/ansible-collections/community.general/issues/3910).
- redfish_command - add ``update_status`` to output of ``SimpleUpdate`` command to allow a user monitor the update in progress (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_command - adding ``EnableSecureBoot`` functionality (https://github.com/ansible-collections/community.general/pull/5899).
- redfish_command - adding ``VerifyBiosAttributes`` functionality (https://github.com/ansible-collections/community.general/pull/5900).
- redfish_info - add ``GetUpdateStatus`` command to check the progress of a previous update request (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_info - adds commands to retrieve the HPE ThermalConfiguration and FanPercentMinimum settings from iLO (https://github.com/ansible-collections/community.general/pull/6208).
- redfish_utils module utils - added PUT (``put_request()``) functionality (https://github.com/ansible-collections/community.general/pull/5490).
- redhat_subscription - add a ``server_proxy_scheme`` parameter to configure the scheme for the proxy server (https://github.com/ansible-collections/community.general/pull/5662).
- redhat_subscription - adds ``token`` parameter for subscription-manager authentication using Red Hat API token (https://github.com/ansible-collections/community.general/pull/5725).
- redhat_subscription - credentials (``username``, ``activationkey``, and so on) are required now only if a system needs to be registered, or ``force_register`` is specified (https://github.com/ansible-collections/community.general/pull/5664).
- redhat_subscription - the registration is done using the D-Bus ``rhsm`` service instead of spawning a ``subscription-manager register`` command, if possible; this avoids passing plain-text credentials as arguments to ``subscription-manager register``, which can be seen while that command runs (https://github.com/ansible-collections/community.general/pull/6122).
- sefcontext - add support for path substitutions (https://github.com/ansible-collections/community.general/issues/1193).
- shutdown - if no shutdown commands are found in the ``search_paths`` then the module will attempt to shutdown the system using ``systemctl shutdown`` (https://github.com/ansible-collections/community.general/issues/4269, https://github.com/ansible-collections/community.general/pull/6171).
- slack - add option ``prepend_hash`` which allows to control whether a ``#`` is prepended to ``channel_id``. The current behavior (value ``auto``) is to prepend ``#`` unless some specific prefixes are found. That list of prefixes is incomplete, and there does not seem to exist a documented condition on when exactly ``#`` must not be prepended. We recommend to explicitly set ``prepend_hash=always`` or ``prepend_hash=never`` to avoid any ambiguity (https://github.com/ansible-collections/community.general/pull/5629).
- snap - minor refactor when executing module (https://github.com/ansible-collections/community.general/pull/5773).
- snap - refactor module to use ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6468).
- snap_alias - refactor code to module utils (https://github.com/ansible-collections/community.general/pull/6441).
- snap_alias - refactored module to use ``CmdRunner`` to execute ``snap`` (https://github.com/ansible-collections/community.general/pull/5486).
- spotinst_aws_elastigroup - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5553).
- ssh_config - add ``host_key_algorithms`` option (https://github.com/ansible-collections/community.general/pull/5605).
- ssh_config - add ``proxyjump`` option (https://github.com/ansible-collections/community.general/pull/5970).
- ssh_config - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5720).
- ssh_config - vendored StormSSH's config parser to avoid having to install StormSSH to use the module (https://github.com/ansible-collections/community.general/pull/6117).
- sudoers - add ``setenv`` parameters to support passing environment variables via sudo. (https://github.com/ansible-collections/community.general/pull/5883)
- sudoers - adds ``host`` parameter for setting hostname restrictions in sudoers rules (https://github.com/ansible-collections/community.general/issues/5702).
- terraform - remove state file check condition and error block, because in the native implementation of terraform will not cause errors due to the non-existent file (https://github.com/ansible-collections/community.general/pull/6296).
- udm_dns_record - minor refactor to the code (https://github.com/ansible-collections/community.general/pull/6382).
- udm_share - added ``elements`` attribute to ``list`` type parameters (https://github.com/ansible-collections/community.general/pull/5557).
- udm_user - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5559).
- znode module - optional ``use_tls`` parameter added for encrypted communication (https://github.com/ansible-collections/community.general/issues/6154).

Breaking Changes / Porting Guide
--------------------------------

- If you are not using this collection as part of Ansible, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.sap_libs`` if you are using any of the ``sapcar_extract``, ``sap_task_list_execute``, and ``hana_query`` modules.
  Without that collection installed, the redirects for these modules do not work.
- ModuleHelper module utils - when the module sets output variables named ``msg``, ``exception``, ``output``, ``vars``, or ``changed``, the actual output will prefix those names with ``_`` (underscore symbol) only when they clash with output variables generated by ModuleHelper itself, which only occurs when handling exceptions. Please note that this breaking change does not require a new major release since before this release, it was not possible to add such variables to the output `due to a bug <https://github.com/ansible-collections/community.general/pull/5755>`__ (https://github.com/ansible-collections/community.general/pull/5765).
- gconftool2 - fix processing of ``gconftool-2`` when ``key`` does not exist, returning ``null`` instead of empty string for both ``value`` and ``previous_value`` return values (https://github.com/ansible-collections/community.general/issues/6028).
- gitlab_runner - the default of ``access_level_on_creation`` changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/6428).
- ldap_search - convert all string-like values to UTF-8 (https://github.com/ansible-collections/community.general/issues/5704, https://github.com/ansible-collections/community.general/pull/6473).
- nmcli - the default of the ``hairpin`` option changed from ``true`` to ``false`` (https://github.com/ansible-collections/community.general/pull/6428).
- proxmox - the default of the ``unprivileged`` option changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/6428).

Deprecated Features
-------------------

- ModuleHelper module_utils - ``deps`` mixin for MH classes deprecated in favour of using the ``deps`` module_utils (https://github.com/ansible-collections/community.general/pull/6465).
- consul - deprecate using parameters unused for ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5772).
- gitlab_runner - the default of the new option ``access_level_on_creation`` will change from ``false`` to ``true`` in community.general 7.0.0. This will cause ``access_level`` to be used during runner registration as well, and not only during updates (https://github.com/ansible-collections/community.general/pull/5908).
- gitlab_runner - the option ``access_level`` will lose its default value in community.general 8.0.0. From that version on, you have set this option to ``ref_protected`` explicitly, if you want to have a protected runner (https://github.com/ansible-collections/community.general/issues/5925).
- manageiq_policies - deprecate ``state=list`` in favour of using ``community.general.manageiq_policies_info`` (https://github.com/ansible-collections/community.general/pull/5721).
- manageiq_tags - deprecate ``state=list`` in favour of using ``community.general.manageiq_tags_info`` (https://github.com/ansible-collections/community.general/pull/5727).
- rax - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax module utils - module utils code relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cbs - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cbs_attachments - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb_database - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb_user - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb_nodes - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb_ssl - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_dns - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_dns_record - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_facts - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_files - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_files_objects - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_identity - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_keypair - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_meta - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_alarm - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_check - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_entity - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_notification - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_notification_plan - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_network - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_queue - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_scaling_group - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_scaling_policy - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rhn_channel, rhn_register - RHN hosted at redhat.com was discontinued years
  ago, and Spacewalk 5 (which uses RHN) is EOL since 2020, May 31st;
  while these modules could work on Uyuni / SUSE Manager (fork of Spacewalk 5),
  we have not heard about anyone using them in those setups. Hence, these
  modules are deprecated, and will be removed in community.general 10.0.0
  in case there are no reports about being still useful, and potentially
  noone that steps up to maintain them
  (https://github.com/ansible-collections/community.general/pull/6493).

Removed Features (previously deprecated)
----------------------------------------

- All ``sap`` modules have been removed from this collection.
  They have been migrated to the `community.sap_libs <https://galaxy.ansible.com/community/sap_libs>`_ collection.
  Redirections have been provided.
  Following modules are affected:
  - sapcar_extract
  - sap_task_list_execute
  - hana_query
- cmd_runner module utils - the ``fmt`` alias of ``cmd_runner_fmt`` has been removed. Use ``cmd_runner_fmt`` instead (https://github.com/ansible-collections/community.general/pull/6428).
- newrelic_deployment - the ``appname`` and ``environment`` options have been removed. They did not do anything (https://github.com/ansible-collections/community.general/pull/6428).
- puppet - the alias ``show-diff`` of the ``show_diff`` option has been removed. Use ``show_diff`` instead (https://github.com/ansible-collections/community.general/pull/6428).
- xfconf - generating facts was deprecated in community.general 3.0.0, however three factoids, ``property``, ``channel`` and ``value`` continued to be generated by mistake. This behaviour has been removed and ``xfconf`` generate no facts whatsoever (https://github.com/ansible-collections/community.general/pull/5502).
- xfconf - generating facts was deprecated in community.general 3.0.0, however two factoids, ``previous_value`` and ``type`` continued to be generated by mistake. This behaviour has been removed and ``xfconf`` generate no facts whatsoever (https://github.com/ansible-collections/community.general/pull/5502).

Bugfixes
--------

- ModuleHelper - fix bug when adjusting the name of reserved output variables (https://github.com/ansible-collections/community.general/pull/5755).
- alternatives - support subcommands on Fedora 37, which uses ``follower`` instead of ``slave`` (https://github.com/ansible-collections/community.general/pull/5794).
- ansible_galaxy_install - set default to raise exception if command's return code is different from zero (https://github.com/ansible-collections/community.general/pull/5680).
- ansible_galaxy_install - try ``C.UTF-8`` and then fall back to ``en_US.UTF-8`` before failing (https://github.com/ansible-collections/community.general/pull/5680).
- archive - avoid deprecated exception class on Python 3 (https://github.com/ansible-collections/community.general/pull/6180).
- archive - reduce RAM usage by generating CRC32 checksum over chunks (https://github.com/ansible-collections/community.general/pull/6274).
- bitwarden lookup plugin - clarify what to do, if the bitwarden vault is not unlocked (https://github.com/ansible-collections/community.general/pull/5811).
- cartesian and flattened lookup plugins - adjust to parameter deprecation in ansible-core 2.14's ``listify_lookup_plugin_terms`` helper function (https://github.com/ansible-collections/community.general/pull/6074).
- chroot connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/5570).
- cloudflare_dns - fixed the idempotency for SRV DNS records (https://github.com/ansible-collections/community.general/pull/5972).
- cloudflare_dns - fixed the possiblity of setting a root-level SRV DNS record (https://github.com/ansible-collections/community.general/pull/5972).
- cmd_runner module utils - fixed bug when handling default cases in ``cmd_runner_fmt.as_map()`` (https://github.com/ansible-collections/community.general/pull/5538).
- cmd_runner module utils - formatting arguments ``cmd_runner_fmt.as_fixed()`` was expecting an non-existing argument (https://github.com/ansible-collections/community.general/pull/5538).
- dependent lookup plugin - avoid warning on deprecated parameter for ``Templar.template()`` (https://github.com/ansible-collections/community.general/pull/5543).
- deps module utils - do not fail when dependency cannot be found (https://github.com/ansible-collections/community.general/pull/6479).
- dig lookup plugin - correctly handle DNSKEY record type's ``algorithm`` field (https://github.com/ansible-collections/community.general/pull/5914).
- flatpak - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing Flatpaks because of a parameter witch only checks the installed apps (https://github.com/ansible-collections/community.general/pull/6289).
- gconftool2 - fix ``changed`` result always being ``true`` (https://github.com/ansible-collections/community.general/issues/6028).
- gconftool2 - remove requirement of parameter ``value`` when ``state=absent`` (https://github.com/ansible-collections/community.general/issues/6028).
- gem - fix force parameter not being passed to gem command when uninstalling (https://github.com/ansible-collections/community.general/pull/5822).
- gem - fix hang due to interactive prompt for confirmation on specific version uninstall (https://github.com/ansible-collections/community.general/pull/5751).
- github_webhook - fix always changed state when no secret is provided (https://github.com/ansible-collections/community.general/pull/5994).
- gitlab_deploy_key - also update ``title`` and not just ``can_push`` (https://github.com/ansible-collections/community.general/pull/5888).
- gitlab_group_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- gitlab_project_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- gitlab_runner - fix ``KeyError`` on runner creation and update (https://github.com/ansible-collections/community.general/issues/6112).
- icinga2_host - fix the data structure sent to Icinga to make use of host templates and template vars (https://github.com/ansible-collections/community.general/pull/6286).
- idrac_redfish_command - allow user to specify ``resource_id`` for ``CreateBiosConfigJob`` to specify an exact manager (https://github.com/ansible-collections/community.general/issues/2090).
- influxdb_user - fix running in check mode when the user does not exist yet (https://github.com/ansible-collections/community.general/pull/6111).
- ini_file - make ``section`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6404).
- interfaces_file - fix reading options in lines not starting with a space (https://github.com/ansible-collections/community.general/issues/6120).
- jail connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/6118).
- jenkins_build - fix the logical flaw when deleting a Jenkins build (https://github.com/ansible-collections/community.general/pull/5514).
- jenkins_plugin - fix error due to undefined variable when updates file is not downloaded (https://github.com/ansible-collections/community.general/pull/6100).
- keycloak - improve error messages (https://github.com/ansible-collections/community.general/pull/6318).
- keycloak_client - fix accidental replacement of value for attribute ``saml.signing.private.key`` with ``no_log`` in wrong contexts (https://github.com/ansible-collections/community.general/pull/5934).
- keycloak_client_rolemapping - calculate ``proposed`` and ``after`` return values properly (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_client_rolemapping - remove only listed mappings with ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_user_federation - fixes federation creation issue. When a new federation was created and at the same time a default / standard mapper was also changed / updated the creation process failed as a bad None set variable led to a bad malformed url request (https://github.com/ansible-collections/community.general/pull/5750).
- keycloak_user_federation - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing user federations because of a buggy seemingly superflous extra query parameter (https://github.com/ansible-collections/community.general/pull/5732).
- loganalytics callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logdna callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logstash callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- lxc_container - fix the arguments of the lxc command which broke the creation and cloning of containers (https://github.com/ansible-collections/community.general/issues/5578).
- lxd_* modules, lxd inventory plugin - fix TLS/SSL certificate validation problems by using the correct purpose when creating the TLS context (https://github.com/ansible-collections/community.general/issues/5616, https://github.com/ansible-collections/community.general/pull/6034).
- memset - fix memset urlerror handling (https://github.com/ansible-collections/community.general/pull/6114).
- nmcli - fix change handling of values specified as an integer 0 (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix failure to handle WIFI settings when connection type not specified (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix improper detection of changes to ``wifi.wake-on-wlan`` (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fixed idempotency issue for bridge connections. Module forced default value of ``bridge.priority`` to nmcli if not set; if ``bridge.stp`` is disabled nmcli ignores it and keep default (https://github.com/ansible-collections/community.general/issues/3216, https://github.com/ansible-collections/community.general/issues/4683).
- nmcli - fixed idempotency issue when module params is set to ``may_fail4=false`` and ``method4=disabled``; in this case nmcli ignores change and keeps their own default value ``yes`` (https://github.com/ansible-collections/community.general/pull/6106).
- nmcli - implemented changing mtu value on vlan interfaces (https://github.com/ansible-collections/community.general/issues/4387).
- nmcli - order is significant for lists of addresses (https://github.com/ansible-collections/community.general/pull/6048).
- nsupdate - fix zone lookup. The SOA record for an existing zone is returned as an answer RR and not as an authority RR (https://github.com/ansible-collections/community.general/issues/5817, https://github.com/ansible-collections/community.general/pull/5818).
- one_vm - avoid splitting labels that are ``None`` (https://github.com/ansible-collections/community.general/pull/5489).
- one_vm - fix syntax error when creating VMs with a more complex template (https://github.com/ansible-collections/community.general/issues/6225).
- onepassword lookup plugin - Changed to ignore errors from "op account get" calls. Previously, errors would prevent auto-signin code from executing (https://github.com/ansible-collections/community.general/pull/5942).
- onepassword_raw - add missing parameter to plugin documentation (https://github.com/ansible-collections/community.general/issues/5506).
- opkg - fix issue that ``force=reinstall`` would not reinstall an existing package (https://github.com/ansible-collections/community.general/pull/5705).
- opkg - fixes bug when using ``update_cache=true`` (https://github.com/ansible-collections/community.general/issues/6004).
- passwordstore lookup plugin - make compatible with ansible-core 2.16 (https://github.com/ansible-collections/community.general/pull/6447).
- pipx - fixed handling of ``install_deps=true`` with ``state=latest`` and ``state=upgrade`` (https://github.com/ansible-collections/community.general/pull/6303).
- portage - update the logic for generating the emerge command arguments to ensure that ``withbdeps: false`` results in a passing an ``n`` argument with the ``--with-bdeps`` emerge flag (https://github.com/ansible-collections/community.general/issues/6451, https://github.com/ansible-collections/community.general/pull/6456).
- proxmox inventory plugin - fix bug while templating when using templates for the ``url``, ``user``, ``password``, ``token_id``, or ``token_secret`` options (https://github.com/ansible-collections/community.general/pull/5640).
- proxmox inventory plugin - handle tags delimited by semicolon instead of comma, which happens from Proxmox 7.3 on (https://github.com/ansible-collections/community.general/pull/5602).
- proxmox_disk - avoid duplicate ``vmid`` reference (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5493).
- proxmox_disk - fixed issue with read timeout on import action (https://github.com/ansible-collections/community.general/pull/5803).
- proxmox_disk - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- proxmox_nic - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- puppet - handling ``noop`` parameter was not working at all, now it is has been fixed (https://github.com/ansible-collections/community.general/issues/6452, https://github.com/ansible-collections/community.general/issues/6458).
- redfish_utils - removed basic auth HTTP header when performing a GET on the service root resource and when performing a POST to the session collection (https://github.com/ansible-collections/community.general/issues/5886).
- redhat_subscription - do not ignore ``consumer_name`` and other variables if ``activationkey`` is specified (https://github.com/ansible-collections/community.general/issues/3486, https://github.com/ansible-collections/community.general/pull/5627).
- redhat_subscription - do not pass arguments to ``subscription-manager register`` for things already configured; now a specified ``rhsm_baseurl`` is properly set for subscription-manager (https://github.com/ansible-collections/community.general/pull/5583).
- redhat_subscription - do not use D-Bus for registering when ``environment`` is specified, so it possible to specify again the environment names for registering, as the D-Bus APIs work only with IDs (https://github.com/ansible-collections/community.general/pull/6319).
- redhat_subscription - try to unregister only when already registered when ``force_register`` is specified (https://github.com/ansible-collections/community.general/issues/6258, https://github.com/ansible-collections/community.general/pull/6259).
- redhat_subscription - use the right D-Bus options for environments when registering a CentOS Stream 8 system and using ``environment`` (https://github.com/ansible-collections/community.general/pull/6275).
- redhat_subscription, rhsm_release, rhsm_repository - cleanly fail when not running as root, rather than hanging on an interactive ``console-helper`` prompt; they all interact with ``subscription-manager``, which already requires to be run as root (https://github.com/ansible-collections/community.general/issues/734, https://github.com/ansible-collections/community.general/pull/6211).
- rhsm_release - make ``release`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6401).
- rundeck module utils - fix errors caused by the API empty responses (https://github.com/ansible-collections/community.general/pull/6300)
- rundeck_acl_policy - fix ``TypeError - byte indices must be integers or slices, not str`` error caused by empty API response. Update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/pull/5887, https://github.com/ansible-collections/community.general/pull/6300).
- rundeck_project - update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/issues/5742) (https://github.com/ansible-collections/community.general/pull/6300)
- snap_alias - module would only recognize snap names containing letter, numbers or the underscore character, failing to identify valid snap names such as ``lxd.lxc`` (https://github.com/ansible-collections/community.general/pull/6361).
- splunk callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- sumologic callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- syslog_json callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- terraform - fix ``current`` workspace never getting appended to the ``all`` key in the ``workspace_ctf`` object (https://github.com/ansible-collections/community.general/pull/5735).
- terraform - fix ``terraform init`` failure when there are multiple workspaces on the remote backend and when ``default`` workspace is missing by setting ``TF_WORKSPACE`` environmental variable to the value of ``workspace`` when used (https://github.com/ansible-collections/community.general/pull/5735).
- terraform - fix broken ``warn()`` call (https://github.com/ansible-collections/community.general/pull/6497).
- terraform and timezone - slight refactoring to avoid linter reporting potentially undefined variables (https://github.com/ansible-collections/community.general/pull/5933).
- terraform module - disable ANSI escape sequences during validation phase (https://github.com/ansible-collections/community.general/pull/5843).
- tss lookup plugin - allow to download secret attachments. Previously, we could not download secret attachments but now use ``fetch_attachments`` and ``file_download_path`` variables to download attachments (https://github.com/ansible-collections/community.general/issues/6224).
- unixy callback plugin - fix plugin to work with ansible-core 2.14 by using Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).
- unixy callback plugin - fix typo introduced when updating to use Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).
- various plugins and modules - remove unnecessary imports (https://github.com/ansible-collections/community.general/pull/5940).
- vdo - now uses ``yaml.safe_load()`` to parse command output instead of the deprecated ``yaml.load()`` which is potentially unsafe. Using ``yaml.load()`` without explicitely setting a ``Loader=`` is also an error in pyYAML 6.0 (https://github.com/ansible-collections/community.general/pull/5632).
- vmadm - fix for index out of range error in ``get_vm_uuid`` (https://github.com/ansible-collections/community.general/pull/5628).
- xenorchestra inventory plugin - fix failure to receive objects from server due to not checking the id of the response (https://github.com/ansible-collections/community.general/pull/6227).
- xfs_quota - in case of a project quota, the call to ``xfs_quota`` did not initialize/reset the project (https://github.com/ansible-collections/community.general/issues/5143).
- xml - fixed a bug where empty ``children`` list would not be set (https://github.com/ansible-collections/community.general/pull/5808).
- yarn - fix ``global=true`` to check for the configured global folder instead of assuming the default (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``global=true`` to not fail when `executable` wasn't specified (https://github.com/ansible-collections/community.general/pull/6132)
- yarn - fix ``state=absent`` not working with ``global=true`` when the package does not include a binary (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``state=latest`` not working with ``global=true`` (https://github.com/ansible-collections/community.general/issues/5712).
- yarn - fixes bug where yarn module tasks would fail when warnings were emitted from Yarn. The ``yarn.list`` method was not filtering out warnings (https://github.com/ansible-collections/community.general/issues/6127).
- zfs_delegate_admin - zfs allow output can now be parsed when uids/gids are not known to the host system (https://github.com/ansible-collections/community.general/pull/5943).
- zypper - make package managing work on readonly filesystem of openSUSE MicroOS (https://github.com/ansible-collections/community.general/pull/5615).

New Plugins
-----------

Lookup
~~~~~~

- merge_variables - merge variables with a certain suffix

New Modules
-----------

- btrfs_info - Query btrfs filesystem info
- btrfs_subvolume - Manage btrfs subvolumes
- gitlab_project_badge - Manage project badges on GitLab Server
- ilo_redfish_command - Manages Out-Of-Band controllers using Redfish APIs
- ipbase_info - Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API
- kdeconfig - Manage KDE configuration files
- keycloak_authz_authorization_scope - Allows administration of Keycloak client authorization scopes via Keycloak API
- keycloak_clientscope_type - Set the type of aclientscope in realm or client via Keycloak API
- keycloak_clientsecret_info - Retrieve client secret via Keycloak API
- keycloak_clientsecret_regenerate - Regenerate Keycloak client secret via Keycloak API
- ocapi_command - Manages Out-Of-Band controllers using Open Composable API (OCAPI)
- ocapi_info - Manages Out-Of-Band controllers using Open Composable API (OCAPI)
