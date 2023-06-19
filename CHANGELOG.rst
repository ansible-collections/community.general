===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 5.0.0.

v6.6.2
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- csv module utils - detects and remove unicode BOM markers from incoming CSV content (https://github.com/ansible-collections/community.general/pull/6662).
- gitlab_group - the module passed parameters to the API call even when not set. The module is now filtering out ``None`` values to remediate this (https://github.com/ansible-collections/community.general/pull/6712).
- ini_file - fix a bug where the inactive options were not used when possible (https://github.com/ansible-collections/community.general/pull/6575).
- keycloak module utils - fix ``is_struct_included`` handling of lists of lists/dictionaries (https://github.com/ansible-collections/community.general/pull/6688).
- keycloak module utils - the function ``get_user_by_username`` now return the user representation or ``None`` as stated in the documentation (https://github.com/ansible-collections/community.general/pull/6758).

v6.6.1
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- dconf - if ``gi.repository.GLib`` is missing, try to respawn in a Python interpreter that has it (https://github.com/ansible-collections/community.general/pull/6491).

Bugfixes
--------

- deps module utils - do not fail when dependency cannot be found (https://github.com/ansible-collections/community.general/pull/6479).
- nmcli - fix bond option ``xmit_hash_policy`` (https://github.com/ansible-collections/community.general/pull/6527).
- passwordstore lookup plugin - make compatible with ansible-core 2.16 (https://github.com/ansible-collections/community.general/pull/6447).
- portage - fix ``changed_use`` and ``newuse`` not triggering rebuilds (https://github.com/ansible-collections/community.general/issues/6008, https://github.com/ansible-collections/community.general/pull/6548).
- portage - update the logic for generating the emerge command arguments to ensure that ``withbdeps: false`` results in a passing an ``n`` argument with the ``--with-bdeps`` emerge flag (https://github.com/ansible-collections/community.general/issues/6451, https://github.com/ansible-collections/community.general/pull/6456).
- proxmox_tasks_info - remove ``api_user`` + ``api_password`` constraint from ``required_together`` as it causes to require ``api_password`` even when API token param is used (https://github.com/ansible-collections/community.general/issues/6201).
- puppet - handling ``noop`` parameter was not working at all, now it is has been fixed (https://github.com/ansible-collections/community.general/issues/6452, https://github.com/ansible-collections/community.general/issues/6458).
- terraform - fix broken ``warn()`` call (https://github.com/ansible-collections/community.general/pull/6497).
- xfs_quota - in case of a project quota, the call to ``xfs_quota`` did not initialize/reset the project (https://github.com/ansible-collections/community.general/issues/5143).
- zypper - added handling of zypper exitcode 102. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook (https://github.com/ansible-collections/community.general/pull/6534).

v6.6.0
======

Release Summary
---------------

Bugfix and feature release.

Minor Changes
-------------

- cpanm - minor change, use feature from ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/6385).
- dconf - be forgiving about boolean values: convert them to GVariant booleans automatically (https://github.com/ansible-collections/community.general/pull/6206).
- dconf - minor refactoring improving parameters and dependencies validation (https://github.com/ansible-collections/community.general/pull/6336).
- deps module utils - add function ``failed()`` providing the ability to check the dependency check result without triggering an exception (https://github.com/ansible-collections/community.general/pull/6383).
- dig lookup plugin - Support multiple domains to be queried as indicated in docs (https://github.com/ansible-collections/community.general/pull/6334).
- gitlab_project - add new option ``topics`` for adding topics to GitLab projects (https://github.com/ansible-collections/community.general/pull/6278).
- homebrew_cask - allows passing ``--greedy`` option to ``upgrade_all`` (https://github.com/ansible-collections/community.general/pull/6267).
- idrac_redfish_command - add ``job_id`` to ``CreateBiosConfigJob`` response (https://github.com/ansible-collections/community.general/issues/5603).
- ipa_hostgroup - add ``append`` parameter for adding a new hosts to existing hostgroups without changing existing hostgroup members (https://github.com/ansible-collections/community.general/pull/6203).
- keycloak_authentication - add flow type option to sub flows to allow the creation of 'form-flow' sub flows like in Keycloak's built-in registration flow (https://github.com/ansible-collections/community.general/pull/6318).
- mksysb - improved the output of the module in case of errors (https://github.com/ansible-collections/community.general/issues/6263).
- nmap inventory plugin - added environment variables for configure ``address`` and ``exclude`` (https://github.com/ansible-collections/community.general/issues/6351).
- nmcli - add ``macvlan`` connection type (https://github.com/ansible-collections/community.general/pull/6312).
- pipx - add ``system_site_packages`` parameter to give application access to system-wide packages (https://github.com/ansible-collections/community.general/pull/6308).
- pipx - ensure ``include_injected`` parameter works with ``state=upgrade`` and ``state=latest`` (https://github.com/ansible-collections/community.general/pull/6212).
- puppet - add new options ``skip_tags`` to exclude certain tagged resources during a puppet agent or apply (https://github.com/ansible-collections/community.general/pull/6293).
- terraform - remove state file check condition and error block, because in the native implementation of terraform will not cause errors due to the non-existent file (https://github.com/ansible-collections/community.general/pull/6296).
- udm_dns_record - minor refactor to the code (https://github.com/ansible-collections/community.general/pull/6382).

Bugfixes
--------

- archive - reduce RAM usage by generating CRC32 checksum over chunks (https://github.com/ansible-collections/community.general/pull/6274).
- flatpak - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing Flatpaks because of a parameter witch only checks the installed apps (https://github.com/ansible-collections/community.general/pull/6289).
- icinga2_host - fix the data structure sent to Icinga to make use of host templates and template vars (https://github.com/ansible-collections/community.general/pull/6286).
- idrac_redfish_command - allow user to specify ``resource_id`` for ``CreateBiosConfigJob`` to specify an exact manager (https://github.com/ansible-collections/community.general/issues/2090).
- ini_file - make ``section`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6404).
- keycloak - improve error messages (https://github.com/ansible-collections/community.general/pull/6318).
- one_vm - fix syntax error when creating VMs with a more complex template (https://github.com/ansible-collections/community.general/issues/6225).
- pipx - fixed handling of ``install_deps=true`` with ``state=latest`` and ``state=upgrade`` (https://github.com/ansible-collections/community.general/pull/6303).
- redhat_subscription - do not use D-Bus for registering when ``environment`` is specified, so it possible to specify again the environment names for registering, as the D-Bus APIs work only with IDs (https://github.com/ansible-collections/community.general/pull/6319).
- redhat_subscription - try to unregister only when already registered when ``force_register`` is specified (https://github.com/ansible-collections/community.general/issues/6258, https://github.com/ansible-collections/community.general/pull/6259).
- redhat_subscription - use the right D-Bus options for environments when registering a CentOS Stream 8 system and using ``environment`` (https://github.com/ansible-collections/community.general/pull/6275).
- rhsm_release - make ``release`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6401).
- rundeck module utils - fix errors caused by the API empty responses (https://github.com/ansible-collections/community.general/pull/6300)
- rundeck_acl_policy - fix ``TypeError - byte indices must be integers or slices, not str`` error caused by empty API response. Update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/pull/5887, https://github.com/ansible-collections/community.general/pull/6300).
- rundeck_project - update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/issues/5742) (https://github.com/ansible-collections/community.general/pull/6300)
- snap_alias - module would only recognize snap names containing letter, numbers or the underscore character, failing to identify valid snap names such as ``lxd.lxc`` (https://github.com/ansible-collections/community.general/pull/6361).

New Modules
-----------

- btrfs_info - Query btrfs filesystem info
- btrfs_subvolume - Manage btrfs subvolumes
- ilo_redfish_command - Manages Out-Of-Band controllers using Redfish APIs
- keycloak_authz_authorization_scope - Allows administration of Keycloak client authorization scopes via Keycloak API
- keycloak_clientscope_type - Set the type of aclientscope in realm or client via Keycloak API

v6.5.0
======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- apt_rpm - adds ``clean``, ``dist_upgrade`` and ``update_kernel``  parameters for clear caches, complete upgrade system, and upgrade kernel packages (https://github.com/ansible-collections/community.general/pull/5867).
- dconf - parse GVariants for equality comparison when the Python module ``gi.repository`` is available (https://github.com/ansible-collections/community.general/pull/6049).
- gitlab_runner - allow to register group runner (https://github.com/ansible-collections/community.general/pull/3935).
- jira - add worklog functionality (https://github.com/ansible-collections/community.general/issues/6209, https://github.com/ansible-collections/community.general/pull/6210).
- ldap modules - add ``ca_path`` option (https://github.com/ansible-collections/community.general/pull/6185).
- make - add ``command`` return value to the module output (https://github.com/ansible-collections/community.general/pull/6160).
- nmap inventory plugin - add new option ``open`` for only returning open ports (https://github.com/ansible-collections/community.general/pull/6200).
- nmap inventory plugin - add new option ``port`` for port specific scan (https://github.com/ansible-collections/community.general/pull/6165).
- nmcli - add ``default`` and ``default-or-eui64`` to the list of valid choices for ``addr_gen_mode6`` parameter (https://github.com/ansible-collections/community.general/pull/5974).
- nmcli - add support for ``team.runner-fast-rate`` parameter for ``team`` connections (https://github.com/ansible-collections/community.general/issues/6065).
- openbsd_pkg - set ``TERM`` to ``'dumb'`` in ``execute_command()`` to make module less dependant on the ``TERM`` environment variable set on the Ansible controller (https://github.com/ansible-collections/community.general/pull/6149).
- pipx - optional ``install_apps`` parameter added to install applications from injected packages (https://github.com/ansible-collections/community.general/pull/6198).
- proxmox_kvm - add new ``archive`` parameter. This is needed to create a VM from an archive (backup) (https://github.com/ansible-collections/community.general/pull/6159).
- redfish_info - adds commands to retrieve the HPE ThermalConfiguration and FanPercentMinimum settings from iLO (https://github.com/ansible-collections/community.general/pull/6208).
- redhat_subscription - credentials (``username``, ``activationkey``, and so on) are required now only if a system needs to be registered, or ``force_register`` is specified (https://github.com/ansible-collections/community.general/pull/5664).
- redhat_subscription - the registration is done using the D-Bus ``rhsm`` service instead of spawning a ``subscription-manager register`` command, if possible; this avoids passing plain-text credentials as arguments to ``subscription-manager register``, which can be seen while that command runs (https://github.com/ansible-collections/community.general/pull/6122).
- ssh_config - add ``proxyjump`` option (https://github.com/ansible-collections/community.general/pull/5970).
- ssh_config - vendored StormSSH's config parser to avoid having to install StormSSH to use the module (https://github.com/ansible-collections/community.general/pull/6117).
- znode module - optional ``use_tls`` parameter added for encrypted communication (https://github.com/ansible-collections/community.general/issues/6154).

Bugfixes
--------

- archive - avoid deprecated exception class on Python 3 (https://github.com/ansible-collections/community.general/pull/6180).
- gitlab_runner - fix ``KeyError`` on runner creation and update (https://github.com/ansible-collections/community.general/issues/6112).
- influxdb_user - fix running in check mode when the user does not exist yet (https://github.com/ansible-collections/community.general/pull/6111).
- interfaces_file - fix reading options in lines not starting with a space (https://github.com/ansible-collections/community.general/issues/6120).
- jail connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/6118).
- memset - fix memset urlerror handling (https://github.com/ansible-collections/community.general/pull/6114).
- nmcli - fixed idempotency issue for bridge connections. Module forced default value of ``bridge.priority`` to nmcli if not set; if ``bridge.stp`` is disabled nmcli ignores it and keep default (https://github.com/ansible-collections/community.general/issues/3216, https://github.com/ansible-collections/community.general/issues/4683).
- nmcli - fixed idempotency issue when module params is set to ``may_fail4=false`` and ``method4=disabled``; in this case nmcli ignores change and keeps their own default value ``yes`` (https://github.com/ansible-collections/community.general/pull/6106).
- nmcli - implemented changing mtu value on vlan interfaces (https://github.com/ansible-collections/community.general/issues/4387).
- opkg - fixes bug when using ``update_cache=true`` (https://github.com/ansible-collections/community.general/issues/6004).
- redhat_subscription, rhsm_release, rhsm_repository - cleanly fail when not running as root, rather than hanging on an interactive ``console-helper`` prompt; they all interact with ``subscription-manager``, which already requires to be run as root (https://github.com/ansible-collections/community.general/issues/734, https://github.com/ansible-collections/community.general/pull/6211).
- xenorchestra inventory plugin - fix failure to receive objects from server due to not checking the id of the response (https://github.com/ansible-collections/community.general/pull/6227).
- yarn - fix ``global=true`` to not fail when `executable` wasn't specified (https://github.com/ansible-collections/community.general/pull/6132)
- yarn - fixes bug where yarn module tasks would fail when warnings were emitted from Yarn. The ``yarn.list`` method was not filtering out warnings (https://github.com/ansible-collections/community.general/issues/6127).

New Plugins
-----------

Lookup
~~~~~~

- merge_variables - merge variables with a certain suffix

New Modules
-----------

- kdeconfig - Manage KDE configuration files

v6.4.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- dnsimple - set custom User-Agent for API requests to DNSimple (https://github.com/ansible-collections/community.general/pull/5927).
- flatpak_remote - add new boolean option ``enabled``. It controls, whether the remote is enabled or not (https://github.com/ansible-collections/community.general/pull/5926).
- gitlab_project - add ``releases_access_level``, ``environments_access_level``, ``feature_flags_access_level``, ``infrastructure_access_level``, ``monitor_access_level``, and ``security_and_compliance_access_level`` options (https://github.com/ansible-collections/community.general/pull/5986).
- jc filter plugin - added the ability to use parser plugins (https://github.com/ansible-collections/community.general/pull/6043).
- keycloak_group - add new optional module parameter ``parents`` to properly handle keycloak subgroups (https://github.com/ansible-collections/community.general/pull/5814).
- keycloak_user_federation - make ``org.keycloak.storage.ldap.mappers.LDAPStorageMapper`` the default value for mappers ``providerType`` (https://github.com/ansible-collections/community.general/pull/5863).
- ldap modules - add ``xorder_discovery`` option (https://github.com/ansible-collections/community.general/issues/6045, https://github.com/ansible-collections/community.general/pull/6109).
- lxd_container - add diff and check mode (https://github.com/ansible-collections/community.general/pull/5866).
- mattermost, rocketchat, slack - replace missing default favicon with docs.ansible.com favicon (https://github.com/ansible-collections/community.general/pull/5928).
- modprobe - add ``persistent`` option (https://github.com/ansible-collections/community.general/issues/4028, https://github.com/ansible-collections/community.general/pull/542).
- osx_defaults - include stderr in error messages (https://github.com/ansible-collections/community.general/pull/6011).
- proxmox - suppress urllib3 ``InsecureRequestWarnings`` when ``validate_certs`` option is ``false`` (https://github.com/ansible-collections/community.general/pull/5931).
- redfish_command - adding ``EnableSecureBoot`` functionality (https://github.com/ansible-collections/community.general/pull/5899).
- redfish_command - adding ``VerifyBiosAttributes`` functionality (https://github.com/ansible-collections/community.general/pull/5900).
- sefcontext - add support for path substitutions (https://github.com/ansible-collections/community.general/issues/1193).

Deprecated Features
-------------------

- gitlab_runner - the option ``access_level`` will lose its default value in community.general 8.0.0. From that version on, you have set this option to ``ref_protected`` explicitly, if you want to have a protected runner (https://github.com/ansible-collections/community.general/issues/5925).

Bugfixes
--------

- cartesian and flattened lookup plugins - adjust to parameter deprecation in ansible-core 2.14's ``listify_lookup_plugin_terms`` helper function (https://github.com/ansible-collections/community.general/pull/6074).
- cloudflare_dns - fixed the idempotency for SRV DNS records (https://github.com/ansible-collections/community.general/pull/5972).
- cloudflare_dns - fixed the possiblity of setting a root-level SRV DNS record (https://github.com/ansible-collections/community.general/pull/5972).
- github_webhook - fix always changed state when no secret is provided (https://github.com/ansible-collections/community.general/pull/5994).
- jenkins_plugin - fix error due to undefined variable when updates file is not downloaded (https://github.com/ansible-collections/community.general/pull/6100).
- keycloak_client - fix accidental replacement of value for attribute ``saml.signing.private.key`` with ``no_log`` in wrong contexts (https://github.com/ansible-collections/community.general/pull/5934).
- lxd_* modules, lxd inventory plugin - fix TLS/SSL certificate validation problems by using the correct purpose when creating the TLS context (https://github.com/ansible-collections/community.general/issues/5616, https://github.com/ansible-collections/community.general/pull/6034).
- nmcli - fix change handling of values specified as an integer 0 (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix failure to handle WIFI settings when connection type not specified (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix improper detection of changes to ``wifi.wake-on-wlan`` (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - order is significant for lists of addresses (https://github.com/ansible-collections/community.general/pull/6048).
- onepassword lookup plugin - Changed to ignore errors from "op account get" calls. Previously, errors would prevent auto-signin code from executing (https://github.com/ansible-collections/community.general/pull/5942).
- terraform and timezone - slight refactoring to avoid linter reporting potentially undefined variables (https://github.com/ansible-collections/community.general/pull/5933).
- various plugins and modules - remove unnecessary imports (https://github.com/ansible-collections/community.general/pull/5940).
- yarn - fix ``global=true`` to check for the configured global folder instead of assuming the default (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``state=absent`` not working with ``global=true`` when the package does not include a binary (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``state=latest`` not working with ``global=true`` (https://github.com/ansible-collections/community.general/issues/5712).
- zfs_delegate_admin - zfs allow output can now be parsed when uids/gids are not known to the host system (https://github.com/ansible-collections/community.general/pull/5943).
- zypper - make package managing work on readonly filesystem of openSUSE MicroOS (https://github.com/ansible-collections/community.general/pull/5615).

v6.3.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- apache2_module - add module argument ``warn_mpm_absent`` to control whether warning are raised in some edge cases (https://github.com/ansible-collections/community.general/pull/5793).
- bitwarden lookup plugin - can now retrieve secrets from custom fields (https://github.com/ansible-collections/community.general/pull/5694).
- bitwarden lookup plugin - implement filtering results by ``collection_id`` parameter (https://github.com/ansible-collections/community.general/issues/5849).
- dig lookup plugin - support CAA record type (https://github.com/ansible-collections/community.general/pull/5913).
- gitlab_project - add ``builds_access_level``, ``container_registry_access_level`` and ``forking_access_level`` options (https://github.com/ansible-collections/community.general/pull/5706).
- gitlab_runner - add new boolean option ``access_level_on_creation``. It controls, whether the value of ``access_level`` is used for runner registration or not. The option ``access_level`` has been ignored on registration so far and was only used on updates (https://github.com/ansible-collections/community.general/issues/5907, https://github.com/ansible-collections/community.general/pull/5908).
- ilo_redfish_utils module utils - change implementation of DNS Server IP and NTP Server IP update (https://github.com/ansible-collections/community.general/pull/5804).
- ipa_group - allow to add and remove external users with the ``external_user`` option (https://github.com/ansible-collections/community.general/pull/5897).
- iptables_state - minor refactoring within the module (https://github.com/ansible-collections/community.general/pull/5844).
- one_vm - add a new ``updateconf`` option which implements the ``one.vm.updateconf`` API call (https://github.com/ansible-collections/community.general/pull/5812).
- opkg - refactored module to use ``CmdRunner`` for executing ``opkg`` (https://github.com/ansible-collections/community.general/pull/5718).
- redhat_subscription - adds ``token`` parameter for subscription-manager authentication using Red Hat API token (https://github.com/ansible-collections/community.general/pull/5725).
- snap - minor refactor when executing module (https://github.com/ansible-collections/community.general/pull/5773).
- snap_alias - refactored module to use ``CmdRunner`` to execute ``snap`` (https://github.com/ansible-collections/community.general/pull/5486).
- sudoers - add ``setenv`` parameters to support passing environment variables via sudo. (https://github.com/ansible-collections/community.general/pull/5883)

Breaking Changes / Porting Guide
--------------------------------

- ModuleHelper module utils - when the module sets output variables named ``msg``, ``exception``, ``output``, ``vars``, or ``changed``, the actual output will prefix those names with ``_`` (underscore symbol) only when they clash with output variables generated by ModuleHelper itself, which only occurs when handling exceptions. Please note that this breaking change does not require a new major release since before this release, it was not possible to add such variables to the output `due to a bug <https://github.com/ansible-collections/community.general/pull/5755>`__ (https://github.com/ansible-collections/community.general/pull/5765).

Deprecated Features
-------------------

- consul - deprecate using parameters unused for ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5772).
- gitlab_runner - the default of the new option ``access_level_on_creation`` will change from ``false`` to ``true`` in community.general 7.0.0. This will cause ``access_level`` to be used during runner registration as well, and not only during updates (https://github.com/ansible-collections/community.general/pull/5908).

Bugfixes
--------

- ModuleHelper - fix bug when adjusting the name of reserved output variables (https://github.com/ansible-collections/community.general/pull/5755).
- alternatives - support subcommands on Fedora 37, which uses ``follower`` instead of ``slave`` (https://github.com/ansible-collections/community.general/pull/5794).
- bitwarden lookup plugin - clarify what to do, if the bitwarden vault is not unlocked (https://github.com/ansible-collections/community.general/pull/5811).
- dig lookup plugin - correctly handle DNSKEY record type's ``algorithm`` field (https://github.com/ansible-collections/community.general/pull/5914).
- gem - fix force parameter not being passed to gem command when uninstalling (https://github.com/ansible-collections/community.general/pull/5822).
- gem - fix hang due to interactive prompt for confirmation on specific version uninstall (https://github.com/ansible-collections/community.general/pull/5751).
- gitlab_deploy_key - also update ``title`` and not just ``can_push`` (https://github.com/ansible-collections/community.general/pull/5888).
- keycloak_user_federation - fixes federation creation issue. When a new federation was created and at the same time a default / standard mapper was also changed / updated the creation process failed as a bad None set variable led to a bad malformed url request (https://github.com/ansible-collections/community.general/pull/5750).
- keycloak_user_federation - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing user federations because of a buggy seemingly superflous extra query parameter (https://github.com/ansible-collections/community.general/pull/5732).
- loganalytics callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logdna callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logstash callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- nsupdate - fix zone lookup. The SOA record for an existing zone is returned as an answer RR and not as an authority RR (https://github.com/ansible-collections/community.general/issues/5817, https://github.com/ansible-collections/community.general/pull/5818).
- proxmox_disk - fixed issue with read timeout on import action (https://github.com/ansible-collections/community.general/pull/5803).
- redfish_utils - removed basic auth HTTP header when performing a GET on the service root resource and when performing a POST to the session collection (https://github.com/ansible-collections/community.general/issues/5886).
- splunk callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- sumologic callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- syslog_json callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- terraform - fix ``current`` workspace never getting appended to the ``all`` key in the ``workspace_ctf`` object (https://github.com/ansible-collections/community.general/pull/5735).
- terraform - fix ``terraform init`` failure when there are multiple workspaces on the remote backend and when ``default`` workspace is missing by setting ``TF_WORKSPACE`` environmental variable to the value of ``workspace`` when used (https://github.com/ansible-collections/community.general/pull/5735).
- terraform module - disable ANSI escape sequences during validation phase (https://github.com/ansible-collections/community.general/pull/5843).
- xml - fixed a bug where empty ``children`` list would not be set (https://github.com/ansible-collections/community.general/pull/5808).

New Modules
-----------

- ocapi_command - Manages Out-Of-Band controllers using Open Composable API (OCAPI)
- ocapi_info - Manages Out-Of-Band controllers using Open Composable API (OCAPI)

v6.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- opkg - allow installing a package in a certain version (https://github.com/ansible-collections/community.general/pull/5688).
- proxmox - added new module parameter ``tags`` for use with PVE 7+ (https://github.com/ansible-collections/community.general/pull/5714).
- puppet - refactored module to use ``CmdRunner`` for executing ``puppet`` (https://github.com/ansible-collections/community.general/pull/5612).
- redhat_subscription - add a ``server_proxy_scheme`` parameter to configure the scheme for the proxy server (https://github.com/ansible-collections/community.general/pull/5662).
- ssh_config - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5720).
- sudoers - adds ``host`` parameter for setting hostname restrictions in sudoers rules (https://github.com/ansible-collections/community.general/issues/5702).

Deprecated Features
-------------------

- manageiq_policies - deprecate ``state=list`` in favour of using ``community.general.manageiq_policies_info`` (https://github.com/ansible-collections/community.general/pull/5721).
- rax - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_cbs - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_cbs_attachments - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_cdb - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_cdb_database - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_cdb_user - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_clb - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_clb_nodes - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_clb_ssl - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_dns - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_dns_record - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_facts - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_files - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_files_objects - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_identity - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_keypair - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_meta - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_mon_alarm - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_mon_check - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_mon_entity - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_mon_notification - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_mon_notification_plan - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_network - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_queue - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_scaling_group - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).
- rax_scaling_policy - module relies on deprecates library ``pyrax``. Unless maintainers step up to work on the module, it will be marked as deprecated in community.general 7.0.0 and removed in version 9.0.0 (https://github.com/ansible-collections/community.general/pull/5733).

Bugfixes
--------

- ansible_galaxy_install - set default to raise exception if command's return code is different from zero (https://github.com/ansible-collections/community.general/pull/5680).
- ansible_galaxy_install - try ``C.UTF-8`` and then fall back to ``en_US.UTF-8`` before failing (https://github.com/ansible-collections/community.general/pull/5680).
- gitlab_group_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- gitlab_project_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- lxc_container - fix the arguments of the lxc command which broke the creation and cloning of containers (https://github.com/ansible-collections/community.general/issues/5578).
- opkg - fix issue that ``force=reinstall`` would not reinstall an existing package (https://github.com/ansible-collections/community.general/pull/5705).
- proxmox_disk - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- proxmox_nic - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- unixy callback plugin - fix typo introduced when updating to use Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).

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
