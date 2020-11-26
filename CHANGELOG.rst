===============================
Community General Release Notes
===============================

.. contents:: Topics


v1.3.0
======

Release Summary
---------------

This is the last minor 1.x.0 release. The next releases from the stable-1 branch will be 1.3.y patch releases.

Major Changes
-------------

- For community.general 2.0.0, the Hetzner Robot modules will be moved to the `community.hrobot <https://galaxy.ansible.com/community/hrobot>`_ collection.
  A redirection will be inserted so that users using ansible-base 2.10 or newer do not have to change anything.

  If you use Ansible 2.9 and explicitly use Hetzner Robot modules from this collection, you will need to adjust your playbooks and roles to use FQCNs starting with ``community.hrobot.`` instead of ``community.general.hetzner_``,
  for example replace ``community.general.hetzner_firewall_info`` in a task by ``community.hrobot.firewall_info``.

  If you use ansible-base and installed ``community.general`` manually and rely on the Hetzner Robot modules, you have to make sure to install the ``community.hrobot`` collection as well.
  If you are using FQCNs, i.e. ``community.general.hetzner_failover_ip`` instead of ``hetzner_failover_ip``, it will continue working, but we still recommend to adjust the FQCNs as well.
- For community.general 2.0.0, the ``docker`` modules and plugins will be moved to the `community.docker <https://galaxy.ansible.com/community/docker>`_ collection.
  A redirection will be inserted so that users using ansible-base 2.10 or newer do not have to change anything.

  If you use Ansible 2.9 and explicitly use ``docker`` content from this collection, you will need to adjust your playbooks and roles to use FQCNs starting with ``community.docker.`` instead of ``community.general.``,
  for example replace ``community.general.docker_container`` in a task by ``community.docker.docker_container``.

  If you use ansible-base and installed ``community.general`` manually and rely on the ``docker`` content, you have to make sure to install the ``community.docker`` collection as well.
  If you are using FQCNs, i.e. ``community.general.docker_container`` instead of ``docker_container``, it will continue working, but we still recommend to adjust the FQCNs as well.
- For community.general 2.0.0, the ``postgresql`` modules and plugins will be moved to the `community.postgresql <https://galaxy.ansible.com/community/postgresql>`_ collection.
  A redirection will be inserted so that users using ansible-base 2.10 or newer do not have to change anything.

  If you use Ansible 2.9 and explicitly use ``postgresql`` content from this collection, you will need to adjust your playbooks and roles to use FQCNs starting with ``community.postgresql.`` instead of ``community.general.``,
  for example replace ``community.general.postgresql_info`` in a task by ``community.postgresql.postgresql_info``.

  If you use ansible-base and installed ``community.general`` manually and rely on the ``postgresql`` content, you have to make sure to install the ``community.postgresql`` collection as well.
  If you are using FQCNs, i.e. ``community.general.postgresql_info`` instead of ``postgresql_info``, it will continue working, but we still recommend to adjust the FQCNs as well.
- The community.general collection no longer depends on the ansible.posix collection (https://github.com/ansible-collections/community.general/pull/1157).

Minor Changes
-------------

- Add new filter plugin ``dict_kv`` which returns a single key-value pair from two arguments. Useful for generating complex dictionaries without using loops. For example ``'value' | community.general.dict_kv('key'))`` evaluates to ``{'key': 'value'}`` (https://github.com/ansible-collections/community.general/pull/1264).
- archive - fix paramater types (https://github.com/ansible-collections/community.general/pull/1039).
- consul - added support for tcp checks (https://github.com/ansible-collections/community.general/issues/1128).
- datadog - mark ``notification_message`` as ``no_log`` (https://github.com/ansible-collections/community.general/pull/1338).
- datadog_monitor - add ``include_tags`` option (https://github.com/ansible/ansible/issues/57441).
- django_manage - renamed parameter ``app_path`` to ``project_path``, adding ``app_path`` and ``chdir`` as aliases (https://github.com/ansible-collections/community.general/issues/1044).
- docker_container - now supports the ``device_requests`` option, which allows to request additional resources such as GPUs (https://github.com/ansible/ansible/issues/65748, https://github.com/ansible-collections/community.general/pull/1119).
- docker_image - return docker build output (https://github.com/ansible-collections/community.general/pull/805).
- docker_secret - add a warning when the secret does not have an ``ansible_key`` label but the ``force`` parameter is not set (https://github.com/ansible-collections/community.docker/issues/30, https://github.com/ansible-collections/community.docker/pull/31).
- facter - added option for ``arguments`` (https://github.com/ansible-collections/community.general/pull/768).
- hashi_vault - support ``VAULT_SKIP_VERIFY`` environment variable for determining if to verify certificates (in addition to the ``validate_certs=`` flag supported today) (https://github.com/ansible-collections/community.general/pull/1024).
- hashi_vault lookup plugin - add support for JWT authentication (https://github.com/ansible-collections/community.general/pull/1213).
- infoblox inventory script - use stderr for reporting errors, and allow use of environment for configuration (https://github.com/ansible-collections/community.general/pull/436).
- ipa_host - silence warning about non-secret ``random_password`` option not having ``no_log`` set (https://github.com/ansible-collections/community.general/pull/1339).
- ipa_user - silence warning about non-secret ``krbpasswordexpiration`` and ``update_password`` options not having ``no_log`` set (https://github.com/ansible-collections/community.general/pull/1339).
- linode_v4 - added support for Linode StackScript usage when creating instances (https://github.com/ansible-collections/community.general/issues/723).
- lvol - fix idempotency issue when using lvol with ``%VG`` or ``%PVS`` size options and VG is fully allocated (https://github.com/ansible-collections/community.general/pull/229).
- maven_artifact - added ``client_cert`` and ``client_key`` parameters to the maven_artifact module (https://github.com/ansible-collections/community.general/issues/1123).
- module_helper - added ModuleHelper class and a couple of convenience tools for module developers (https://github.com/ansible-collections/community.general/pull/1322).
- nmcli - refactor internal methods for simplicity and enhance reuse to support existing and future connection types (https://github.com/ansible-collections/community.general/pull/1113).
- nmcli - remove Python DBus and GTK Object library dependencies (https://github.com/ansible-collections/community.general/issues/1112).
- nmcli - the ``dns4``, ``dns4_search``, ``dns6``, and ``dns6_search`` arguments are retained internally as lists (https://github.com/ansible-collections/community.general/pull/1113).
- odbc - added a parameter ``commit`` which allows users to disable the explicit commit after the execute call (https://github.com/ansible-collections/community.general/pull/1139).
- openbsd_pkg - added ``snapshot`` option (https://github.com/ansible-collections/community.general/pull/965).
- pacman - improve group expansion speed: query list of pacman groups once (https://github.com/ansible-collections/community.general/pull/349).
- parted - add ``resize`` option to resize existing partitions (https://github.com/ansible-collections/community.general/pull/773).
- passwordstore lookup plugin - added ``umask`` option to set the desired file permisions on creation. This is done via the ``PASSWORD_STORE_UMASK`` environment variable (https://github.com/ansible-collections/community.general/pull/1156).
- pkgin - add support for installation of full versioned package names (https://github.com/ansible-collections/community.general/pull/1256).
- pkgng - present the ``ignore_osver`` option to pkg (https://github.com/ansible-collections/community.general/pull/1243).
- portage - add ``getbinpkgonly`` option, remove unnecessary note on internal portage behaviour (getbinpkg=yes), and remove the undocumented exclusiveness of the pkg options as portage makes no such restriction (https://github.com/ansible-collections/community.general/pull/1169).
- postgresql_info - add ``in_recovery`` return value to show if a service in recovery mode or not (https://github.com/ansible-collections/community.general/issues/1068).
- postgresql_privs - add ``procedure`` type support (https://github.com/ansible-collections/community.general/issues/1002).
- postgresql_query - add ``query_list`` and ``query_all_results`` return values (https://github.com/ansible-collections/community.general/issues/838).
- proxmox - add new ``proxmox_default_behavior`` option (https://github.com/ansible-collections/community.general/pull/850).
- proxmox - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox - extract common code and documentation (https://github.com/ansible-collections/community.general/pull/1331).
- proxmox inventory plugin - ignore QEMU templates altogether instead of skipping the creation of the host in the inventory (https://github.com/ansible-collections/community.general/pull/1185).
- proxmox_kvm - add cloud-init support (new options: ``cicustom``, ``cipassword``, ``citype``, ``ciuser``, ``ipconfig``, ``nameservers``, ``searchdomains``, ``sshkeys``) (https://github.com/ansible-collections/community.general/pull/797).
- proxmox_kvm - add new ``proxmox_default_behavior`` option (https://github.com/ansible-collections/community.general/pull/850).
- proxmox_kvm - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox_template - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox_template - download proxmox applicance templates (pveam) (https://github.com/ansible-collections/community.general/pull/1046).
- redis cache plugin - add redis sentinel functionality to cache plugin (https://github.com/ansible-collections/community.general/pull/1055).
- redis cache plugin - make the redis cache keyset name configurable (https://github.com/ansible-collections/community.general/pull/1036).
- terraform - add ``init_reconfigure`` option, which controls the ``-reconfigure`` flag (backend reconfiguration) (https://github.com/ansible-collections/community.general/pull/823).
- xfconf - removed unnecessary second execution of ``xfconf-query`` (https://github.com/ansible-collections/community.general/pull/1305).

Deprecated Features
-------------------

- django_manage - the parameter ``liveserver`` relates to a no longer maintained third-party module for django. It is now deprecated, and will be remove in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/1154).
- proxmox - the default of the new ``proxmox_default_behavior`` option will change from ``compatibility`` to ``no_defaults`` in community.general 4.0.0. Set the option to an explicit value to avoid a deprecation warning (https://github.com/ansible-collections/community.general/pull/850).
- proxmox_kvm - the default of the new ``proxmox_default_behavior`` option will change from ``compatibility`` to ``no_defaults`` in community.general 4.0.0. Set the option to an explicit value to avoid a deprecation warning (https://github.com/ansible-collections/community.general/pull/850).
- syspatch - deprecate the redundant ``apply`` argument (https://github.com/ansible-collections/community.general/pull/360).

Bugfixes
--------

- apache2_module - amend existing module identifier workaround to also apply to updated Shibboleth modules (https://github.com/ansible-collections/community.general/issues/1379).
- beadm - fixed issue "list object has no attribute split" (https://github.com/ansible-collections/community.general/issues/791).
- capabilities - fix for a newer version of libcap release (https://github.com/ansible-collections/community.general/pull/1061).
- composer - fix bug in command idempotence with composer v2 (https://github.com/ansible-collections/community.general/issues/1179).
- docker_login - fix internal config file storage to handle credentials for more than one registry (https://github.com/ansible-collections/community.general/issues/1117).
- filesystem - add option ``state`` with default ``present``. When set to ``absent``, filesystem signatures are removed (https://github.com/ansible-collections/community.general/issues/355).
- flatpak - use of the ``--non-interactive`` argument instead of ``-y`` when possible (https://github.com/ansible-collections/community.general/pull/1246).
- gcp_storage_files lookup plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- gitlab_group - added description parameter to ``createGroup()`` call (https://github.com/ansible-collections/community.general/issues/138).
- gitlab_group_variable - support for GitLab pagination limitation by iterating over GitLab variable pages (https://github.com/ansible-collections/community.general/pull/968).
- gitlab_project_variable - support for GitLab pagination limitation by iterating over GitLab variable pages (https://github.com/ansible-collections/community.general/pull/968).
- hashi_vault - fix approle authentication without ``secret_id`` (https://github.com/ansible-collections/community.general/pull/1138).
- homebrew - fix package name validation for packages containing hypen ``-`` (https://github.com/ansible-collections/community.general/issues/1037).
- homebrew_cask - fix package name validation for casks containing hypen ``-`` (https://github.com/ansible-collections/community.general/issues/1037).
- influxdb - fix usage of path for older version of python-influxdb (https://github.com/ansible-collections/community.general/issues/997).
- iptables_state - fix race condition between module and its action plugin (https://github.com/ansible-collections/community.general/issues/1136).
- linode inventory plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- lxc_container - fix the type of the ``container_config`` parameter. It is now processed as a list and not a string (https://github.com/ansible-collections/community.general/pull/216).
- macports - fix failure to install a package whose name is contained within an already installed package's name or variant (https://github.com/ansible-collections/community.general/issues/1307).
- maven_artifact - handle timestamped snapshot version strings properly (https://github.com/ansible-collections/community.general/issues/709).
- memcached cache plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- monit - fix modules ability to determine the current state of the monitored process (https://github.com/ansible-collections/community.general/pull/1107).
- nios_fixed_address, nios_host_record, nios_zone - removed redundant parameter aliases causing warning messages to incorrectly appear in task output (https://github.com/ansible-collections/community.general/issues/852).
- nmcli - cannot modify ``ifname`` after connection creation (https://github.com/ansible-collections/community.general/issues/1089).
- nmcli - use consistent autoconnect parameters (https://github.com/ansible-collections/community.general/issues/459).
- omapi_host - fix compatibility with Python 3 (https://github.com/ansible-collections/community.general/issues/787).
- packet_net.py inventory script - fixed failure w.r.t. operating system retrieval by changing array subscription back to attribute access (https://github.com/ansible-collections/community.general/pull/891).
- postgresql_ext - fix the module crashes when available ext versions cannot be compared with current version (https://github.com/ansible-collections/community.general/issues/1095).
- postgresql_ext - fix version selection when ``version=latest`` (https://github.com/ansible-collections/community.general/pull/1078).
- postgresql_pg_hba - fix a crash when a new rule with an 'options' field replaces a rule without or vice versa (https://github.com/ansible-collections/community.general/issues/1108).
- postgresql_privs - fix module fails when ``type`` group and passing ``objs`` value containing hyphens (https://github.com/ansible-collections/community.general/issues/1058).
- proxmox_kvm - fix issue causing linked clones not being create by allowing ``format=unspecified`` (https://github.com/ansible-collections/community.general/issues/1027).
- proxmox_kvm - ignore unsupported ``pool`` parameter on update (https://github.com/ansible-collections/community.general/pull/1258).
- redis - fixes parsing of config values which should not be converted to bytes (https://github.com/ansible-collections/community.general/pull/1079).
- redis cache plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- slack - avoid trying to update existing message when sending messages that contain the string "ts" (https://github.com/ansible-collections/community.general/issues/1097).
- solaris_zone - fixed issue trying to configure zone in Python 3 (https://github.com/ansible-collections/community.general/issues/1081).
- syspatch - fix bug where not setting ``apply=true`` would result in error (https://github.com/ansible-collections/community.general/pull/360).
- xfconf - parameter ``value`` no longer required for state ``absent`` (https://github.com/ansible-collections/community.general/issues/1329).
- xfconf - xfconf no longer passing the command args as a string, but rather as a list (https://github.com/ansible-collections/community.general/issues/1328).
- zypper - force ``LANG=C`` to as zypper is looking in XML output where attribute could be translated (https://github.com/ansible-collections/community.general/issues/1175).

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_domain_info - Retrieve information about one or more Proxmox VE domains
- proxmox_group_info - Retrieve information about one or more Proxmox VE groups
- proxmox_user_info - Retrieve information about one or more Proxmox VE users

Clustering
~~~~~~~~~~

nomad
^^^^^

- nomad_job - Launch a Nomad Job
- nomad_job_info - Get Nomad Jobs info

Monitoring
~~~~~~~~~~

- pagerduty_change - Track a code or infrastructure change as a PagerDuty change event
- pagerduty_user - Manage a user account on PagerDuty

v1.2.0
======

Release Summary
---------------

Regular bimonthly minor release.

Minor Changes
-------------

- hashi_vault - support ``VAULT_NAMESPACE`` environment variable for namespaced lookups against Vault Enterprise (in addition to the ``namespace=`` flag supported today) (https://github.com/ansible-collections/community.general/pull/929).
- hashi_vault lookup - add ``VAULT_TOKEN_FILE`` as env option to specify ``token_file`` param (https://github.com/ansible-collections/community.general/issues/373).
- hashi_vault lookup - add ``VAULT_TOKEN_PATH`` as env option to specify ``token_path`` param (https://github.com/ansible-collections/community.general/issues/373).
- ipa_user - add ``userauthtype`` option (https://github.com/ansible-collections/community.general/pull/951).
- iptables_state - use FQCN when calling a module from action plugin (https://github.com/ansible-collections/community.general/pull/967).
- nagios - add the ``acknowledge`` action (https://github.com/ansible-collections/community.general/pull/820).
- nagios - add the ``host`` and ``all`` values for the ``forced_check`` action (https://github.com/ansible-collections/community.general/pull/998).
- nagios - add the ``service_check`` action (https://github.com/ansible-collections/community.general/pull/820).
- nagios - rename the ``service_check`` action to ``forced_check`` since we now are able to check both a particular service, all services of a particular host and the host itself (https://github.com/ansible-collections/community.general/pull/998).
- pkgutil - module can now accept a list of packages (https://github.com/ansible-collections/community.general/pull/799).
- pkgutil - module has a new option, ``force``, equivalent to the ``-f`` option to the `pkgutil <http://pkgutil.net/>`_ command (https://github.com/ansible-collections/community.general/pull/799).
- pkgutil - module now supports check mode (https://github.com/ansible-collections/community.general/pull/799).
- postgresql_privs - add the ``usage_on_types`` option (https://github.com/ansible-collections/community.general/issues/884).
- proxmox_kvm - improve code readability (https://github.com/ansible-collections/community.general/pull/934).
- pushover - add device parameter (https://github.com/ansible-collections/community.general/pull/802).
- redfish_command - add sub-command for ``EnableContinuousBootOverride`` and ``DisableBootOverride`` to allow setting BootSourceOverrideEnabled Redfish property (https://github.com/ansible-collections/community.general/issues/824).
- redfish_command - support same reset actions on Managers as on Systems (https://github.com/ansible-collections/community.general/issues/901).
- slack - add support for updating messages (https://github.com/ansible-collections/community.general/issues/304).
- xml - fixed issue were changed was returned when removing non-existent xpath (https://github.com/ansible-collections/community.general/pull/1007).
- zypper_repository - proper failure when python-xml is missing (https://github.com/ansible-collections/community.general/pull/939).

Bugfixes
--------

- aerospike_migrations - handle exception when unstable-cluster is returned (https://github.com/ansible-collections/community.general/pull/900).
- django_manage - fix idempotence for ``createcachetable`` (https://github.com/ansible-collections/community.general/pull/699).
- docker_container - fix idempotency problem with ``published_ports`` when strict comparison is used and list is empty (https://github.com/ansible-collections/community.general/issues/978).
- gem - fix get_installed_versions: correctly parse ``default`` version (https://github.com/ansible-collections/community.general/pull/783).
- hashi_vault - add missing ``mount_point`` parameter for approle auth (https://github.com/ansible-collections/community.general/pull/897).
- hashi_vault lookup - ``token_path`` in config file overridden by env ``HOME`` (https://github.com/ansible-collections/community.general/issues/373).
- homebrew_cask - fixed issue where a cask with ``@`` in the name is incorrectly reported as invalid (https://github.com/ansible-collections/community.general/issues/733).
- interfaces_file - escape regular expression characters in old value (https://github.com/ansible-collections/community.general/issues/777).
- launchd - fix for user-level services (https://github.com/ansible-collections/community.general/issues/896).
- nmcli - set ``C`` locale when executing ``nmcli`` (https://github.com/ansible-collections/community.general/issues/989).
- parted - fix creating partition when label is changed (https://github.com/ansible-collections/community.general/issues/522).
- pkg5 - now works when Python 3 is used on the target (https://github.com/ansible-collections/community.general/pull/789).
- postgresql_privs - allow to pass ``PUBLIC`` role written in lowercase letters (https://github.com/ansible-collections/community.general/issues/857).
- postgresql_privs - fix the module mistakes a procedure for a function (https://github.com/ansible-collections/community.general/issues/994).
- postgresql_privs - rollback if nothing changed (https://github.com/ansible-collections/community.general/issues/885).
- postgresql_privs - the module was attempting to revoke grant options even though ``grant_option`` was not specified (https://github.com/ansible-collections/community.general/pull/796).
- proxmox_kvm - defer error-checking for non-existent VMs in order to fix idempotency of tasks using ``state=absent`` and properly recognize a success (https://github.com/ansible-collections/community.general/pull/811).
- proxmox_kvm - improve handling of long-running tasks by creating a dedicated function (https://github.com/ansible-collections/community.general/pull/831).
- slack - fix ``xox[abp]`` token identification to capture everything after ``xox[abp]``, as the token is the only thing that should be in this argument (https://github.com/ansible-collections/community.general/issues/862).
- terraform - fix incorrectly reporting a status of unchanged when number of resources added or destroyed are multiples of 10 (https://github.com/ansible-collections/community.general/issues/561).
- timezone - support Python3 on macos/darwin (https://github.com/ansible-collections/community.general/pull/945).
- zfs - fixed ``invalid character '@' in pool name"`` error when working with snapshots on a root zvol (https://github.com/ansible-collections/community.general/issues/932).

New Plugins
-----------

Inventory
~~~~~~~~~

- proxmox - Proxmox inventory source
- stackpath_compute - StackPath Edge Computing inventory source

New Modules
-----------

Cloud
~~~~~

scaleway
^^^^^^^^

- scaleway_database_backup - Scaleway database backups management module

Source Control
~~~~~~~~~~~~~~

gitlab
^^^^^^

- gitlab_group_members - Manage group members on GitLab Server
- gitlab_group_variable - Creates, updates, or deletes GitLab groups variables

v1.1.0
======

Release Summary
---------------

Release for Ansible 2.10.0.


Minor Changes
-------------

- The collection dependencies where adjusted so that ``community.kubernetes`` and ``google.cloud`` are required to be of version 1.0.0 or newer (https://github.com/ansible-collections/community.general/pull/774).
- jc - new filter to convert the output of many shell commands and file-types to JSON. Uses the jc library at https://github.com/kellyjonbrazil/jc. For example, filtering the STDOUT output of ``uname -a`` via ``{{ result.stdout | community.general.jc('uname') }}``. Requires Python 3.6+ (https://github.com/ansible-collections/community.general/pull/750).
- xfconf - add support for ``double`` type (https://github.com/ansible-collections/community.general/pull/744).

Bugfixes
--------

- cobbler inventory plugin - ``name`` needed FQCN (https://github.com/ansible-collections/community.general/pull/722).
- dsv lookup - use correct dict usage (https://github.com/ansible-collections/community.general/pull/743).
- inventory plugins - allow FQCN in ``plugin`` option (https://github.com/ansible-collections/community.general/pull/722).
- ipa_hostgroup - fix an issue with load-balanced ipa and cookie handling with Python 3 (https://github.com/ansible-collections/community.general/issues/737).
- oc connection plugin - ``transport`` needed FQCN (https://github.com/ansible-collections/community.general/pull/722).
- postgresql_set - allow to pass an empty string to the ``value`` parameter (https://github.com/ansible-collections/community.general/issues/775).
- xfconf - make it work in non-english locales (https://github.com/ansible-collections/community.general/pull/744).

New Modules
-----------

Cloud
~~~~~

docker
^^^^^^

- docker_stack_task_info - Return information of the tasks on a docker stack

System
~~~~~~

- iptables_state - Save iptables state into a file or restore it from a file
- shutdown - Shut down a machine
- sysupgrade - Manage OpenBSD system upgrades

v1.0.0
======

Release Summary
---------------

This is release 1.0.0 of ``community.general``, released on 2020-07-31.


Minor Changes
-------------

- Add the ``gcpubsub``, ``gcpubsub_info`` and ``gcpubsub_facts`` (to be removed in 3.0.0) modules. These were originally in community.general, but removed on the assumption that they have been moved to google.cloud. Since this turned out to be incorrect, we re-added them for 1.0.0.
- Add the deprecated ``gcp_backend_service``, ``gcp_forwarding_rule`` and ``gcp_healthcheck`` modules, which will be removed in 2.0.0. These were originally in community.general, but removed on the assumption that they have been moved to google.cloud. Since this turned out to be incorrect, we re-added them for 1.0.0.
- The collection is now actively tested in CI with the latest Ansible 2.9 release.
- airbrake_deployment - add ``version`` param; clarified docs on ``revision`` param (https://github.com/ansible-collections/community.general/pull/583).
- apk - added ``no_cache`` option (https://github.com/ansible-collections/community.general/pull/548).
- firewalld - the module has been moved to the ``ansible.posix`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/623).
- gitlab_project - add support for merge_method on projects (https://github.com/ansible/ansible/pull/66813).
- gitlab_runners inventory plugin - permit environment variable input for ``server_url``, ``api_token`` and ``filter`` options (https://github.com/ansible-collections/community.general/pull/611).
- haproxy - add options to dis/enable health and agent checks.  When health and agent checks are enabled for a service, a disabled service will re-enable itself automatically.  These options also change the state of the agent checks to match the requested state for the backend (https://github.com/ansible-collections/community.general/issues/684).
- log_plays callback - use v2 methods (https://github.com/ansible-collections/community.general/pull/442).
- logstash callback - add ini config (https://github.com/ansible-collections/community.general/pull/610).
- lxd_container - added support of ``--target`` flag for cluster deployments (https://github.com/ansible-collections/community.general/issues/637).
- parted - accept negative numbers in ``part_start`` and ``part_end``
- pkgng - added ``stdout`` and ``stderr`` attributes to the result (https://github.com/ansible-collections/community.general/pull/560).
- pkgng - added support for upgrading all packages using ``name: *, state: latest``, similar to other package providers (https://github.com/ansible-collections/community.general/pull/569).
- postgresql_query - add search_path parameter (https://github.com/ansible-collections/community.general/issues/625).
- rundeck_acl_policy - add check for rundeck_acl_policy name parameter (https://github.com/ansible-collections/community.general/pull/612).
- slack - add support for sending messages built with block kit (https://github.com/ansible-collections/community.general/issues/380).
- splunk callback - add an option to allow not to validate certificate from HEC (https://github.com/ansible-collections/community.general/pull/596).
- xfconf - add arrays support (https://github.com/ansible/ansible/issues/46308).
- xfconf - add support for ``uint`` type (https://github.com/ansible-collections/community.general/pull/696).

Breaking Changes / Porting Guide
--------------------------------

- log_plays callback - add missing information to the logs generated by the callback plugin. This changes the log message format (https://github.com/ansible-collections/community.general/pull/442).
- pkgng - passing ``name: *`` with ``state: absent`` will no longer remove every installed package from the system. It is now a noop. (https://github.com/ansible-collections/community.general/pull/569).
- pkgng - passing ``name: *`` with ``state: latest`` or ``state: present`` will no longer install every package from the configured package repositories. Instead, ``name: *, state: latest`` will upgrade all already-installed packages, and ``name: *, state: present`` is a noop. (https://github.com/ansible-collections/community.general/pull/569).

Deprecated Features
-------------------

- The ldap_attr module has been deprecated and will be removed in a later release; use ldap_attrs instead.
- xbps - the ``force`` option never had any effect. It is now deprecated, and will be removed in 3.0.0 (https://github.com/ansible-collections/community.general/pull/568).

Removed Features (previously deprecated)
----------------------------------------

- conjur_variable lookup - has been moved to the ``cyberark.conjur`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/570).
- digital_ocean_* - all DigitalOcean modules have been moved to the ``community.digitalocean`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/622).
- infini_* - all infinidat modules have been moved to the ``infinidat.infinibox`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/607).
- logicmonitor - the module has been removed in 1.0.0 since it is unmaintained and the API used by the module has been turned off in 2017 (https://github.com/ansible-collections/community.general/issues/539, https://github.com/ansible-collections/community.general/pull/541).
- logicmonitor_facts - the module has been removed in 1.0.0 since it is unmaintained and the API used by the module has been turned off in 2017 (https://github.com/ansible-collections/community.general/issues/539, https://github.com/ansible-collections/community.general/pull/541).
- mysql_* - all MySQL modules have been moved to the ``community.mysql`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/633).
- proxysql_* - all ProxySQL modules have been moved to the ``community.proxysql`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/624).

Bugfixes
--------

- aix_filesystem - fix issues with ismount module_util pathing for Ansible 2.9 (https://github.com/ansible-collections/community.general/pull/567).
- consul_kv lookup - fix ``ANSIBLE_CONSUL_URL`` environment variable handling (https://github.com/ansible/ansible/issues/51960).
- consul_kv lookup - fix arguments handling (https://github.com/ansible-collections/community.general/pull/303).
- digital_ocean_tag_info - fix crash when querying for an individual tag (https://github.com/ansible-collections/community.general/pull/615).
- doas become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_flags`` and ``become_user`` were not explicitly specified (https://github.com/ansible-collections/community.general/pull/704).
- docker_compose - add a condition to prevent service startup if parameter ``stopped`` is true. Otherwise, the service will be started on each play and stopped again immediately due to the ``stopped`` parameter and breaks the idempotency of the module (https://github.com/ansible-collections/community.general/issues/532).
- docker_compose - disallow usage of the parameters ``stopped`` and ``restarted`` at the same time. This breaks also the idempotency (https://github.com/ansible-collections/community.general/issues/532).
- docker_container - use Config MacAddress by default instead of Networks. Networks MacAddress is empty in some cases (https://github.com/ansible/ansible/issues/70206).
- docker_container - various error fixes in string handling for Python 2 to avoid crashes when non-ASCII characters are used in strings (https://github.com/ansible-collections/community.general/issues/640).
- docker_swarm - removes ``advertise_addr`` from list of required arguments when ``state`` is ``"join"`` (https://github.com/ansible-collections/community.general/issues/439).
- dzdo become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_user`` was not explicitly specified (https://github.com/ansible-collections/community.general/pull/708).
- filesystem - resizefs of xfs filesystems is fixed. Filesystem needs to be mounted.
- jenkins_plugin - replace MD5 checksum verification with SHA1 due to MD5 being disabled on systems with FIPS-only algorithms enabled (https://github.com/ansible/ansible/issues/34304).
- jira - improve error message handling (https://github.com/ansible-collections/community.general/pull/311).
- jira - improve error message handling with multiple errors (https://github.com/ansible-collections/community.general/pull/707).
- kubevirt - Add aliases 'interface_name' for network_name (https://github.com/ansible/ansible/issues/55641).
- nmcli - fix idempotetency when modifying an existing connection (https://github.com/ansible-collections/community.general/issues/481).
- osx_defaults - fix handling negative integers (https://github.com/ansible-collections/community.general/issues/134).
- pacman - treat package names containing .zst as package files during installation (https://www.archlinux.org/news/now-using-zstandard-instead-of-xz-for-package-compression/, https://github.com/ansible-collections/community.general/pull/650).
- pbrun become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_user`` was not explicitly specified (https://github.com/ansible-collections/community.general/pull/708).
- postgresql_privs - fix crash when set privileges on schema with hyphen in the name (https://github.com/ansible-collections/community.general/issues/656).
- postgresql_set - only display a warning about restarts, when restarting is needed (https://github.com/ansible-collections/community.general/pull/651).
- redfish_info, redfish_config, redfish_command - Fix Redfish response payload decode on Python 3.5 (https://github.com/ansible-collections/community.general/issues/686)
- selective - mark task failed correctly (https://github.com/ansible/ansible/issues/63767).
- snmp_facts - skip ``EndOfMibView`` values (https://github.com/ansible/ansible/issues/49044).
- yarn - fixed an index out of range error when no outdated packages where returned by yarn executable (see https://github.com/ansible-collections/community.general/pull/474).
- yarn - fixed an too many values to unpack error when scoped packages are installed (see https://github.com/ansible-collections/community.general/pull/474).

New Plugins
-----------

Inventory
~~~~~~~~~

- cobbler - Cobbler inventory source

Lookup
~~~~~~

- dsv - Get secrets from Thycotic DevOps Secrets Vault
- tss - Get secrets from Thycotic Secret Server

New Modules
-----------

Cloud
~~~~~

docker
^^^^^^

- docker_stack_info - Return information on a docker stack

Database
~~~~~~~~

misc
^^^^

- odbc - Execute SQL via ODBC

System
~~~~~~

- launchd - Manage macOS services

v0.2.0
======

Release Summary
---------------

This is the first proper release of the ``community.general`` collection on 2020-06-20.
The changelog describes all changes made to the modules and plugins included in this
collection since Ansible 2.9.0.


Major Changes
-------------

- docker_container - the ``network_mode`` option will be set by default to the name of the first network in ``networks`` if at least one network is given and ``networks_cli_compatible`` is ``true`` (will be default from community.general 2.0.0 on). Set to an explicit value to avoid deprecation warnings if you specify networks and set ``networks_cli_compatible`` to ``true``. The current default (not specifying it) is equivalent to the value ``default``.
- docker_container - the module has a new option, ``container_default_behavior``, whose default value will change from ``compatibility`` to ``no_defaults``. Set to an explicit value to avoid deprecation warnings.
- gitlab_user - no longer requires ``name``, ``email`` and ``password`` arguments when ``state=absent``.

Minor Changes
-------------

- A new filter ``to_time_unit`` with specializations ``to_milliseconds``, ``to_seconds``, ``to_minutes``, ``to_hours``, ``to_days``, ``to_weeks``, ``to_months`` and ``to_years`` has been added. For example ``'2d 4h' | community.general.to_hours`` evaluates to 52.
- Add a make option to the make module to be able to choose a specific make executable
- Add information about changed packages in homebrew returned facts (https://github.com/ansible/ansible/issues/59376).
- Follow up changes in homebrew_cask (https://github.com/ansible/ansible/issues/34696).
- Moved OpenStack dynamic inventory script to Openstack Collection.
- Remove redundant encoding in json.load call in ipa module_utils (https://github.com/ansible/ansible/issues/66592).
- Updated documentation about netstat command requirement for listen_ports_facts module (https://github.com/ansible/ansible/issues/68077).
- airbrake_deployment - Allow passing ``project_id`` and ``project_key`` for v4 api deploy compatibility
- ali_instance - Add params ``unique_suffix``, ``tags``, ``purge_tags``, ``ram_role_name``, ``spot_price_limit``, ``spot_strategy``, ``period_unit``, ``dry_run``, ``include_data_disks``
- ali_instance and ali_instance_info - the required package footmark needs a version higher than 1.19.0
- ali_instance_info - Add params ``name_prefix``, ``filters``
- alicloud modules - Add authentication params to all modules
- alicloud modules - now only support Python 3.6, not support Python 2.x
- cisco_spark - the module has been renamed to ``cisco_webex`` (https://github.com/ansible-collections/community.general/pull/457).
- cloudflare_dns - Report unexpected failure with more detail (https://github.com/ansible-collections/community.general/pull/511).
- database - add support to unique indexes in postgresql_idx
- digital_ocean_droplet - add support for new vpc_uuid parameter
- docker connection plugin - run Powershell modules on Windows containers.
- docker_container - add ``cpus`` option (https://github.com/ansible/ansible/issues/34320).
- docker_container - add new ``container_default_behavior`` option (PR https://github.com/ansible/ansible/pull/63419).
- docker_container - allow to configure timeout when the module waits for a container's removal.
- docker_container - only passes anonymous volumes to docker daemon as ``Volumes``. This increases compatibility with the ``docker`` CLI program. Note that if you specify ``volumes: strict`` in ``comparisons``, this could cause existing containers created with docker_container from Ansible 2.9 or earlier to restart.
- docker_container - support for port ranges was adjusted to be more compatible to the ``docker`` command line utility: a one-port container range combined with a multiple-port host range will no longer result in only the first host port be used, but the whole range being passed to Docker so that a free port in that range will be used.
- docker_container.py - update a containers restart_policy without restarting the container (https://github.com/ansible/ansible/issues/65993)
- docker_stack - Added ``stdout``, ``stderr``, and ``rc`` to return values.
- docker_swarm_service - Added support for ``init`` option.
- docker_swarm_service - Sort lists when checking for changes.
- firewalld - new feature, can now set ``target`` for a ``zone`` (https://github.com/ansible-collections/community.general/pull/526).
- flatpak and flatpak_remote - use ``module.run_command()`` instead of ``subprocess.Popen()``.
- gitlab_project_variable - implement masked and protected attributes
- gitlab_project_variable - implemented variable_type attribute.
- hashi_vault - AWS IAM auth method added. Accepts standard ansible AWS params and only loads AWS libraries when needed.
- hashi_vault - INI and additional ENV sources made available for some new and old options.
- hashi_vault - ``secret`` can now be an unnamed argument if it's specified first in the term string (see examples).
- hashi_vault - ``token`` is now an explicit option (and the default) in the choices for ``auth_method``. This matches previous behavior (``auth_method`` omitted resulted in token auth) but makes the value clearer and allows it to be explicitly specified.
- hashi_vault - new option ``return_format`` added to control how secrets are returned, including options for multiple secrets and returning raw values with metadata.
- hashi_vault - previous (undocumented) behavior was to attempt to read token from ``~/.vault-token`` if not specified. This is now controlled through ``token_path`` and ``token_file`` options (defaults will mimic previous behavior).
- hashi_vault - previously all options had to be supplied via key=value pairs in the term string; now a mix of string and parameters can be specified (see examples).
- hashi_vault - uses newer authentication calls in the HVAC library and falls back to older ones with deprecation warnings.
- homebrew - Added environment variable to honor update_homebrew setting (https://github.com/ansible/ansible/issues/56650).
- homebrew - New option ``upgrade_options`` allows to pass flags to upgrade
- homebrew - ``install_options`` is now validated to be a list of strings.
- homebrew_tap - ``name`` is now validated to be a list of strings.
- idrac_redfish_config - Support for multiple manager attributes configuration
- java_keystore - add the private_key_passphrase parameter (https://github.com/ansible-collections/community.general/pull/276).
- jira - added search function with support for Jira JQL (https://github.com/ansible-collections/community.general/pull/22).
- jira - added update function which can update Jira Selects etc (https://github.com/ansible-collections/community.general/pull/22).
- lvg - add ``pvresize`` new parameter (https://github.com/ansible/ansible/issues/29139).
- mysql_db - add ``master_data`` parameter (https://github.com/ansible/ansible/pull/66048).
- mysql_db - add ``skip_lock_tables`` option (https://github.com/ansible/ansible/pull/66688).
- mysql_db - add the ``check_implicit_admin`` parameter (https://github.com/ansible/ansible/issues/24418).
- mysql_db - add the ``config_overrides_defaults`` parameter (https://github.com/ansible/ansible/issues/26919).
- mysql_db - add the ``dump_extra_args`` parameter (https://github.com/ansible/ansible/pull/67747).
- mysql_db - add the ``executed_commands`` returned value (https://github.com/ansible/ansible/pull/65498).
- mysql_db - add the ``force`` parameter (https://github.com/ansible/ansible/pull/65547).
- mysql_db - add the ``restrict_config_file`` parameter (https://github.com/ansible/ansible/issues/34488).
- mysql_db - add the ``unsafe_login_password`` parameter (https://github.com/ansible/ansible/issues/63955).
- mysql_db - add the ``use_shell`` parameter (https://github.com/ansible/ansible/issues/20196).
- mysql_info - add ``exclude_fields`` parameter (https://github.com/ansible/ansible/issues/63319).
- mysql_info - add ``global_status`` filter parameter option and return (https://github.com/ansible/ansible/pull/63189).
- mysql_info - add ``return_empty_dbs`` parameter to list empty databases (https://github.com/ansible/ansible/issues/65727).
- mysql_replication - add ``channel`` parameter (https://github.com/ansible/ansible/issues/29311).
- mysql_replication - add ``connection_name`` parameter (https://github.com/ansible/ansible/issues/46243).
- mysql_replication - add ``fail_on_error`` parameter (https://github.com/ansible/ansible/pull/66252).
- mysql_replication - add ``master_delay`` parameter (https://github.com/ansible/ansible/issues/51326).
- mysql_replication - add ``master_use_gtid`` parameter (https://github.com/ansible/ansible/pull/62648).
- mysql_replication - add ``queries`` return value (https://github.com/ansible/ansible/pull/63036).
- mysql_replication - add support of ``resetmaster`` choice to ``mode`` parameter (https://github.com/ansible/ansible/issues/42870).
- mysql_user - ``priv`` parameter can be string or dictionary (https://github.com/ansible/ansible/issues/57533).
- mysql_user - add ``plugin_auth_string`` parameter (https://github.com/ansible/ansible/pull/44267).
- mysql_user - add ``plugin_hash_string`` parameter (https://github.com/ansible/ansible/pull/44267).
- mysql_user - add ``plugin`` parameter (https://github.com/ansible/ansible/pull/44267).
- mysql_user - add the resource_limits parameter (https://github.com/ansible-collections/community.general/issues/133).
- mysql_variables - add ``mode`` parameter (https://github.com/ansible/ansible/issues/60119).
- nagios module - a start parameter has been added, allowing the time a Nagios outage starts to be set. It defaults to the current time if not provided, preserving the previous behavior and ensuring compatibility with existing playbooks.
- nsupdate - Use provided TSIG key to not only sign update queries but also lookup queries
- open_iscsi - allow ``portal`` parameter to be a domain name by resolving the portal ip address beforehand (https://github.com/ansible-collections/community.general/pull/461).
- packet_device - add ``tags`` parameter on device creation (https://github.com/ansible-collections/community.general/pull/418)
- pacman - Improve package state detection speed: Don't query for full details of a package.
- parted - add the ``fs_type`` parameter (https://github.com/ansible-collections/community.general/issues/135).
- pear - added ``prompts`` parameter to allow users to specify expected prompt that could hang Ansible execution (https://github.com/ansible-collections/community.general/pull/530).
- postgresql_copy - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/313).
- postgresql_db - add ``dump_extra_args`` parameter (https://github.com/ansible/ansible/pull/66717).
- postgresql_db - add support for .pgc file format for dump and restores.
- postgresql_db - add the ``executed_commands`` returned value (https://github.com/ansible/ansible/pull/65542).
- postgresql_db - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/issues/106).
- postgresql_ext - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/282).
- postgresql_ext - refactor to simplify and remove dead code (https://github.com/ansible-collections/community.general/pull/291)
- postgresql_ext - use query parameters with cursor object (https://github.com/ansible/ansible/pull/64994).
- postgresql_idx - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/264).
- postgresql_idx - refactor to simplify code (https://github.com/ansible-collections/community.general/pull/291)
- postgresql_info - add collecting info about logical replication publications in databases (https://github.com/ansible/ansible/pull/67614).
- postgresql_info - add collection info about replication subscriptions (https://github.com/ansible/ansible/pull/67464).
- postgresql_info - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/308).
- postgresql_lang - add ``owner`` parameter (https://github.com/ansible/ansible/pull/62999).
- postgresql_lang - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/272).
- postgresql_membership - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/158).
- postgresql_owner - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/198).
- postgresql_ping - add the ``session_role`` parameter (https://github.com/ansible-collections/community.general/pull/312).
- postgresql_ping - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/312).
- postgresql_privs - add support for TYPE as object types in postgresql_privs module (https://github.com/ansible/ansible/issues/62432).
- postgresql_privs - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/177).
- postgresql_publication - add the ``session_role`` parameter (https://github.com/ansible-collections/community.general/pull/279).
- postgresql_publication - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/279).
- postgresql_query - add the ``encoding`` parameter (https://github.com/ansible/ansible/issues/65367).
- postgresql_query - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/294).
- postgresql_schema - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/259).
- postgresql_sequence - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/295).
- postgresql_set - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/302).
- postgresql_slot - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/298).
- postgresql_subscription - add the ``session_role`` parameter (https://github.com/ansible-collections/community.general/pull/280).
- postgresql_subscription - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/280).
- postgresql_table - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/307).
- postgresql_tablespace - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/240).
- postgresql_user - add scram-sha-256 support (https://github.com/ansible/ansible/issues/49878).
- postgresql_user - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/116).
- postgresql_user - add the comment parameter (https://github.com/ansible/ansible/pull/66711).
- postgresql_user_obj_stat_info - add the ``trust_input`` parameter (https://github.com/ansible-collections/community.general/pull/310).
- postgresql_user_obj_stat_info - refactor to simplify code (https://github.com/ansible-collections/community.general/pull/291)
- proxmox - add the ``description`` and ``hookscript`` parameter (https://github.com/ansible-collections/community.general/pull/245).
- redfish_command - Support for virtual media insert and eject commands (https://github.com/ansible-collections/community.general/issues/493)
- redfish_config - New ``bios_attributes`` option to allow setting multiple BIOS attributes in one command.
- redfish_config, redfish_command - Add ``resource_id`` option to specify which System, Manager, or Chassis resource to modify.
- redis - add TLS support to redis cache plugin (https://github.com/ansible-collections/community.general/pull/410).
- rhn_channel - Added ``validate_certs`` option (https://github.com/ansible/ansible/issues/68374).
- rundeck modules - added new options ``client_cert``, ``client_key``, ``force``, ``force_basic_auth``, ``http_agent``, ``url_password``, ``url_username``, ``use_proxy``, ``validate_certs`` to allow changing fetch_url parameters.
- slack - Add support for user/bot/application tokens (using Slack WebAPI)
- slack - Return ``thread_id`` with thread timestamp when user/bot/application tokens are used
- syslogger - added new parameter ident to specify the name of application which is sending the message to syslog (https://github.com/ansible-collections/community.general/issues/319).
- terraform - Adds option ``backend_config_files``. This can accept a list of paths to multiple configuration files (https://github.com/ansible-collections/community.general/pull/394).
- terraform - Adds option ``variables_files`` for multiple var-files (https://github.com/ansible-collections/community.general/issues/224).
- ufw - accept ``interface_in`` and ``interface_out`` as parameters.
- zypper - Added ``allow_vendor_change`` and ``replacefiles`` zypper options (https://github.com/ansible-collections/community.general/issues/381)

Breaking Changes / Porting Guide
--------------------------------

- The environment variable for the auth context for the oc.py connection plugin has been corrected (K8S_CONTEXT).  It was using an initial lowercase k by mistake. (https://github.com/ansible-collections/community.general/pull/377).
- bigpanda - the parameter ``message`` was renamed to ``deployment_message`` since ``message`` is used by Ansible Core engine internally.
- cisco_spark - the module option ``message`` was renamed to ``msg``, as ``message`` is used internally in Ansible Core engine (https://github.com/ansible/ansible/issues/39295)
- datadog - the parameter ``message`` was renamed to ``notification_message`` since ``message`` is used by Ansible Core engine internally.
- docker_container - no longer passes information on non-anonymous volumes or binds as ``Volumes`` to the Docker daemon. This increases compatibility with the ``docker`` CLI program. Note that if you specify ``volumes: strict`` in ``comparisons``, this could cause existing containers created with docker_container from Ansible 2.9 or earlier to restart.
- docker_container - support for port ranges was adjusted to be more compatible to the ``docker`` command line utility: a one-port container range combined with a multiple-port host range will no longer result in only the first host port be used, but the whole range being passed to Docker so that a free port in that range will be used.
- hashi_vault lookup - now returns the latest version when using the KV v2 secrets engine. Previously, it returned all versions of the secret which required additional steps to extract and filter the desired version.

Deprecated Features
-------------------

- airbrake_deployment - Add deprecation notice for ``token`` parameter and v2 api deploys. This feature will be removed in community.general 3.0.0.
- clc_aa_policy - The ``wait`` option had no effect and will be removed in community.general 3.0.0.
- clc_aa_policy - the ``wait`` parameter will be removed. It has always been ignored by the module.
- docker_container - the ``trust_image_content`` option is now deprecated and will be removed in community.general 3.0.0. It has never been used by the module.
- docker_container - the ``trust_image_content`` option will be removed. It has always been ignored by the module.
- docker_container - the default of ``container_default_behavior`` will change from ``compatibility`` to ``no_defaults`` in community.general 3.0.0. Set the option to an explicit value to avoid a deprecation warning.
- docker_container - the default value for ``network_mode`` will change in community.general 3.0.0, provided at least one network is specified and ``networks_cli_compatible`` is ``true``. See porting guide, module documentation or deprecation warning for more details.
- docker_stack - Return values ``out`` and ``err`` have been deprecated and will be removed in community.general 3.0.0. Use ``stdout`` and ``stderr`` instead.
- docker_stack - the return values ``err`` and ``out`` have been deprecated. Use ``stdout`` and ``stderr`` from now on instead.
- helm - Put ``helm`` module to deprecated. New implementation is available in community.kubernetes collection.
- redfish_config - Deprecate ``bios_attribute_name`` and ``bios_attribute_value`` in favor of new `bios_attributes`` option.
- redfish_config - the ``bios_attribute_name`` and ``bios_attribute_value`` options will be removed. To maintain the existing behavior use the ``bios_attributes`` option instead.
- redfish_config and redfish_command - the behavior to select the first System, Manager, or Chassis resource to modify when multiple are present will be removed. Use the new ``resource_id`` option to specify target resource to modify.
- redfish_config, redfish_command - Behavior to modify the first System, Mananger, or Chassis resource when multiple are present is deprecated. Use the new ``resource_id`` option to specify target resource to modify.

Removed Features (previously deprecated)
----------------------------------------

- core - remove support for ``check_invalid_arguments`` in ``UTMModule``.
- pacman - Removed deprecated ``recurse`` option, use ``extra_args=--recursive`` instead

Security Fixes
--------------

- **SECURITY** - CVE-2019-14904 - solaris_zone module accepts zone name and performs actions related to that. However, there is no user input validation done while performing actions. A malicious user could provide a crafted zone name which allows executing commands into the server manipulating the module behaviour. Adding user input validation as per Solaris Zone documentation fixes this issue.
- **security issue** - Ansible: Splunk and Sumologic callback plugins leak sensitive data in logs (CVE-2019-14864)
- ldap_attr, ldap_entry - The ``params`` option has been removed in Ansible-2.10 as it circumvents Ansible's option handling.  Setting ``bind_pw`` with the ``params`` option was disallowed in Ansible-2.7, 2.8, and 2.9 as it was insecure.  For information about this policy, see the discussion at: https://meetbot.fedoraproject.org/ansible-meeting/2017-09-28/ansible_dev_meeting.2017-09-28-15.00.log.html This fixes CVE-2020-1746

Bugfixes
--------

- Convert MD5SUM to lowercase before comparison in maven_artifact module (https://github.com/ansible-collections/community.general/issues/186).
- Fix GitLab modules authentication by handling `python-gitlab` library version >= 1.13.0 (https://github.com/ansible/ansible/issues/64770)
- Fix SSL protocol references in the ``mqtt`` module to prevent failures on Python 2.6.
- Fix the ``xml`` module to use ``list(elem)`` instead of ``elem.getchildren()`` since it is being removed in Python 3.9
- Fix to return XML as a string even for python3 (https://github.com/ansible/ansible/pull/64032).
- Fixes the url handling in lxd_container module that url cannot be specified in lxd environment created by snap.
- Fixes the url handling in lxd_profile module that url cannot be specified in lxd environment created by snap.
- Redact GitLab Project variables which might include sensetive information such as password, api_keys and other project related details.
- Run command in absent state in atomic_image module.
- While deleting gitlab user, name, email and password is no longer required ini gitlab_user module (https://github.com/ansible/ansible/issues/61921).
- airbrake_deployment - Allow deploy notifications for Airbrake compatible v2 api (e.g. Errbit)
- apt_rpm - fix ``package`` type from ``str`` to ``list`` to fix invoking with list of packages (https://github.com/ansible-collections/community.general/issues/143).
- archive - make module compatible with older Ansible versions (https://github.com/ansible-collections/community.general/pull/306).
- become - Fix various plugins that still used play_context to get the become password instead of through the plugin - https://github.com/ansible/ansible/issues/62367
- cloudflare_dns - fix KeyError 'success' (https://github.com/ansible-collections/community.general/issues/236).
- cronvar - only run ``get_bin_path()`` once
- cronvar - use correct binary name (https://github.com/ansible/ansible/issues/63274)
- cronvar - use get_bin_path utility to locate the default crontab executable instead of the hardcoded /usr/bin/crontab. (https://github.com/ansible/ansible/pull/59765)
- cyberarkpassword - fix invalid attribute access (https://github.com/ansible/ansible/issues/66268)
- datadog_monitor - Corrects ``_update_monitor`` to use ``notification_message`` insteade of deprecated ``message`` (https://github.com/ansible-collections/community.general/pull/389).
- datadog_monitor - added missing ``log alert`` type to ``type`` choices (https://github.com/ansible-collections/community.general/issues/251).
- dense callback - fix plugin access to its configuration variables and remove a warning message (https://github.com/ansible/ansible/issues/64628).
- digital_ocean_droplet - Fix creation of DigitalOcean droplets using digital_ocean_droplet module (https://github.com/ansible/ansible/pull/61655)
- docker connection plugin - do not prefix remote path if running on Windows containers.
- docker_compose - fix issue where docker deprecation warning results in ansible erroneously reporting a failure
- docker_container - fix idempotency for IP addresses for networks. The old implementation checked the effective IP addresses assigned by the Docker daemon, and not the specified ones. This causes idempotency issues for containers which are not running, since they have no effective IP addresses assigned.
- docker_container - fix network idempotence comparison error.
- docker_container - improve error behavior when parsing port ranges fails.
- docker_container - make sure that when image is missing, check mode indicates a change (image will be pulled).
- docker_container - passing ``test: [NONE]`` now actually disables the image's healthcheck, as documented.
- docker_container - wait for removal of container if docker API returns early (https://github.com/ansible/ansible/issues/65811).
- docker_image - fix validation of build options.
- docker_image - improve file handling when loading images from disk.
- docker_image - make sure that deprecated options also emit proper deprecation warnings next to warnings which indicate how to replace them.
- docker_login - Use ``with`` statement when accessing files, to prevent that invalid JSON output is produced.
- docker_login - correct broken fix for https://github.com/ansible/ansible/pull/60381 which crashes for Python 3.
- docker_login - fix error handling when ``username`` or ``password`` is not specified when ``state`` is ``present``.
- docker_login - make sure that ``~/.docker/config.json`` is created with permissions ``0600``.
- docker_machine - fallback to ip subcommand output if IPAddress is missing (https://github.com/ansible-collections/community.general/issues/412).
- docker_network - fix idempotence comparison error.
- docker_network - fix idempotency for multiple IPAM configs of the same IP version (https://github.com/ansible/ansible/issues/65815).
- docker_network - validate IPAM config subnet CIDR notation on module setup and not during idempotence checking.
- docker_node_info - improve error handling when service inspection fails, for example because node name being ambiguous (https://github.com/ansible/ansible/issues/63353, PR https://github.com/ansible/ansible/pull/63418).
- docker_swarm_service - ``source`` must no longer be specified for ``tmpfs`` mounts.
- docker_swarm_service - fix task always reporting as changed when using ``healthcheck.start_period``.
- docker_swarm_service - passing ``test: [NONE]`` now actually disables the image's healthcheck, as documented.
- firewalld - enable the firewalld module to function offline with firewalld version 0.7.0 and newer (https://github.com/ansible/ansible/issues/63254)
- flatpak and flatpak_remote - fix command line construction to build commands as lists instead of strings.
- gcp_storage_file lookup - die gracefully when the ``google.cloud`` collection is not installed, or changed in an incompatible way.
- github_deploy_key - added support for pagination
- gitlab_user - Fix adding ssh key to new/changed user and adding group membership for new/changed user
- hashi_vault - Fix KV v2 lookup to always return latest version
- hashi_vault - Handle equal sign in key=value (https://github.com/ansible/ansible/issues/55658).
- hashi_vault - error messages are now user friendly and don't contain the secret name ( https://github.com/ansible-collections/community.general/issues/54 )
- hashi_vault - if used via ``with_hashi_vault`` and a list of n secrets to retrieve, only the first one would be retrieved and returned n times.
- hashi_vault - when a non-token authentication method like ldap or userpass failed, but a valid token was loaded anyway (via env or token file), the token was used to attempt authentication, hiding the failure of the requested auth method.
- homebrew - fix Homebrew module's some functions ignored check_mode option (https://github.com/ansible/ansible/pull/65387).
- influxdb_user - Don't grant admin privilege in check mode
- ipa modules - fix error when IPA_HOST is empty and fallback on DNS (https://github.com/ansible-collections/community.general/pull/241)
- java_keystore - make module compatible with older Ansible versions (https://github.com/ansible-collections/community.general/pull/306).
- jira - printing full error message from jira server (https://github.com/ansible-collections/community.general/pull/22).
- jira - transition issue not working (https://github.com/ansible-collections/community.general/issues/109).
- linode inventory plugin - fix parsing of access_token (https://github.com/ansible/ansible/issues/66874)
- manageiq_provider - fix serialization error when running on python3 environment.
- maven_artifact - make module compatible with older Ansible versions (https://github.com/ansible-collections/community.general/pull/306).
- mysql - dont mask ``mysql_connect`` function errors from modules (https://github.com/ansible/ansible/issues/64560).
- mysql_db - fix Broken pipe error appearance when state is import and the target file is compressed (https://github.com/ansible/ansible/issues/20196).
- mysql_db - fix bug in the ``db_import`` function introduced by https://github.com/ansible/ansible/pull/56721 (https://github.com/ansible/ansible/issues/65351).
- mysql_info - add parameter for __collect to get only what are wanted (https://github.com/ansible-collections/community.general/pull/136).
- mysql_replication - allow to pass empty values to parameters (https://github.com/ansible/ansible/issues/23976).
- mysql_user - Fix idempotence when long grant lists are used (https://github.com/ansible/ansible/issues/68044)
- mysql_user - Remove false positive ``no_log`` warning for ``update_password`` option
- mysql_user - add ``INVOKE LAMBDA`` privilege support (https://github.com/ansible-collections/community.general/issues/283).
- mysql_user - fix ``host_all`` arguments conversion string formatting error (https://github.com/ansible/ansible/issues/29644).
- mysql_user - fix support privileges with underscore (https://github.com/ansible/ansible/issues/66974).
- mysql_user - fix the error No database selected (https://github.com/ansible/ansible/issues/68070).
- mysql_user - make sure current_pass_hash is a string before using it in comparison (https://github.com/ansible/ansible/issues/60567).
- mysql_variable - fix the module doesn't support variables name with dot (https://github.com/ansible/ansible/issues/54239).
- nmcli - typecast parameters to string as required (https://github.com/ansible/ansible/issues/59095).
- nsupdate - Do not try fixing non-existing TXT values (https://github.com/ansible/ansible/issues/63364)
- nsupdate - Fix zone name lookup of internal/private zones (https://github.com/ansible/ansible/issues/62052)
- one_vm - improve file handling by using a context manager.
- ovirt - don't ignore ``instance_cpus`` parameter
- pacman - Fix pacman output parsing on localized environment. (https://github.com/ansible/ansible/issues/65237)
- pacman - fix module crash with ``IndexError: list index out of range`` (https://github.com/ansible/ansible/issues/63077)
- pamd - Bugfix for attribute error when removing the first or last line
- parted - added 'undefined' align option to support parted versions < 2.1 (https://github.com/ansible-collections/community.general/pull/405).
- parted - consider current partition state even in check mode (https://github.com/ansible-collections/community.general/issues/183).
- passwordstore lookup - Honor equal sign in userpass
- pmrun plugin - The success_command string was no longer quoted. This caused unusual use-cases like ``become_flags=su - root -c`` to fail.
- postgres - use query params with cursor.execute in module_utils.postgres.PgMembership class (https://github.com/ansible/ansible/pull/65164).
- postgres.py - add a new keyword argument ``query_params`` (https://github.com/ansible/ansible/pull/64661).
- postgres_user - Remove false positive ``no_log`` warning for ``no_password_changes`` option
- postgresql_db - Removed exception for 'LibraryError' (https://github.com/ansible/ansible/issues/65223).
- postgresql_db - allow to pass users names which contain dots (https://github.com/ansible/ansible/issues/63204).
- postgresql_idx.py - use the ``query_params`` arg of exec_sql function (https://github.com/ansible/ansible/pull/64661).
- postgresql_lang - use query params with cursor.execute (https://github.com/ansible/ansible/pull/65093).
- postgresql_membership - make the ``groups`` and ``target_roles`` parameters required (https://github.com/ansible/ansible/pull/67046).
- postgresql_membership - remove unused import of exec_sql function (https://github.com/ansible-collections/community.general/pull/178).
- postgresql_owner - use query_params with cursor object (https://github.com/ansible/ansible/pull/65310).
- postgresql_privs - fix sorting lists with None elements for python3 (https://github.com/ansible/ansible/issues/65761).
- postgresql_privs - sort results before comparing so that the values are compared and not the result of ``.sort()`` (https://github.com/ansible/ansible/pull/65125)
- postgresql_privs.py - fix reports as changed behavior of module when using ``type=default_privs`` (https://github.com/ansible/ansible/issues/64371).
- postgresql_publication - fix typo in module.warn method name (https://github.com/ansible/ansible/issues/64582).
- postgresql_publication - use query params arg with cursor object (https://github.com/ansible/ansible/issues/65404).
- postgresql_query - improve file handling by using a context manager.
- postgresql_query - the module doesn't support non-ASCII characters in SQL files with Python3 (https://github.com/ansible/ansible/issues/65367).
- postgresql_schema - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65679).
- postgresql_sequence - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65787).
- postgresql_set - fix converting value to uppercase (https://github.com/ansible/ansible/issues/67377).
- postgresql_set - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65791).
- postgresql_slot - make the ``name`` parameter required (https://github.com/ansible/ansible/pull/67046).
- postgresql_slot - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65791).
- postgresql_subscription - fix typo in module.warn method name (https://github.com/ansible/ansible/pull/64583).
- postgresql_subscription - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65791).
- postgresql_table - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65862).
- postgresql_tablespace - make the ``tablespace`` parameter required (https://github.com/ansible/ansible/pull/67046).
- postgresql_tablespace - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65862).
- postgresql_user - allow to pass user name which contains dots (https://github.com/ansible/ansible/issues/63204).
- postgresql_user - use query parameters with cursor object (https://github.com/ansible/ansible/pull/65862).
- proxmox - fix version detection of proxmox 6 and up (Fixes https://github.com/ansible/ansible/issues/59164)
- proxysql - fixed mysql dictcursor
- pulp_repo - the ``client_cert`` and ``client_key`` options were used for both requests to the Pulp instance and for the repo to sync with, resulting in errors when they were used. Use the new options ``feed_client_cert`` and ``feed_client_key`` for client certificates that should only be used for repo synchronisation, and not for communication with the Pulp instance. (https://github.com/ansible/ansible/issues/59513)
- puppet - fix command line construction for check mode and ``manifest:``
- pure - fix incorrect user_string setting in module_utils file (https://github.com/ansible/ansible/pull/66914)
- redfish_command - fix EnableAccount if Enabled property is not present in Account resource (https://github.com/ansible/ansible/issues/59822)
- redfish_command - fix error when deleting a disabled Redfish account (https://github.com/ansible/ansible/issues/64684)
- redfish_command - fix power ResetType mapping logic (https://github.com/ansible/ansible/issues/59804)
- redfish_config - fix support for boolean bios attrs (https://github.com/ansible/ansible/pull/68251)
- redfish_facts - fix KeyError exceptions in GetLogs (https://github.com/ansible/ansible/issues/59797)
- redhat_subscription - do not set the default quantity to ``1`` when no quantity is provided (https://github.com/ansible/ansible/issues/66478)
- replace use of deprecated functions from ``ansible.module_utils.basic``.
- rshm_repository - reduce execution time when changed is False (https://github.com/ansible-collections/community.general/pull/458).
- runas - Fix the ``runas`` ``become_pass`` variable fallback from ``ansible_runas_runas`` to ``ansible_runas_pass``
- scaleway - Fix bug causing KeyError exception on JSON http requests. (https://github.com/ansible-collections/community.general/pull/444)
- scaleway: use jsonify unmarshaller only for application/json requests to avoid breaking the multiline configuration with requests in text/plain (https://github.com/ansible/ansible/issues/65036)
- scaleway_compute - fix transition handling that could cause errors when removing a node (https://github.com/ansible-collections/community.general/pull/444).
- scaleway_compute(check_image_id): use get image instead loop on first page of images results
- sesu - make use of the prompt specified in the code
- slack - Fix ``thread_id`` data type
- slackpkg - fix matching some special cases in package names (https://github.com/ansible-collections/community.general/pull/505).
- slackpkg - fix name matching in package installation (https://github.com/ansible-collections/community.general/issues/450).
- spacewalk inventory - improve file handling by using a context manager.
- syslog_json callback - fix plugin exception when running (https://github.com/ansible-collections/community.general/issues/407).
- syslogger callback plugin - remove check mode support since it did nothing anyway
- terraform - adding support for absolute paths additionally to the relative path within project_path (https://github.com/ansible/ansible/issues/58578)
- terraform - reset out and err before plan creation (https://github.com/ansible/ansible/issues/64369)
- terraform module - fixes usage for providers not supporting workspaces
- yarn - Return correct values when running yarn in check mode (https://github.com/ansible-collections/community.general/pull/153).
- yarn - handle no version when installing module by name (https://github.com/ansible/ansible/issues/55097)
- zfs_delegate_admin - add missing choices diff/hold/release to the permissions parameter (https://github.com/ansible-collections/community.general/pull/278)

New Plugins
-----------

Callback
~~~~~~~~

- diy - Customize the output

Lookup
~~~~~~

- etcd3 - Get key values from etcd3 server
- lmdb_kv - fetch data from LMDB

New Modules
-----------

Cloud
~~~~~

huawei
^^^^^^

- hwc_ecs_instance - Creates a resource of Ecs/Instance in Huawei Cloud
- hwc_evs_disk - Creates a resource of Evs/Disk in Huawei Cloud
- hwc_vpc_eip - Creates a resource of Vpc/EIP in Huawei Cloud
- hwc_vpc_peering_connect - Creates a resource of Vpc/PeeringConnect in Huawei Cloud
- hwc_vpc_port - Creates a resource of Vpc/Port in Huawei Cloud
- hwc_vpc_private_ip - Creates a resource of Vpc/PrivateIP in Huawei Cloud
- hwc_vpc_route - Creates a resource of Vpc/Route in Huawei Cloud
- hwc_vpc_security_group - Creates a resource of Vpc/SecurityGroup in Huawei Cloud
- hwc_vpc_security_group_rule - Creates a resource of Vpc/SecurityGroupRule in Huawei Cloud
- hwc_vpc_subnet - Creates a resource of Vpc/Subnet in Huawei Cloud

ovh
^^^

- ovh_monthly_billing - Manage OVH monthly billing

packet
^^^^^^

- packet_ip_subnet - Assign IP subnet to a bare metal server.
- packet_project - Create/delete a project in Packet host.
- packet_volume - Create/delete a volume in Packet host.
- packet_volume_attachment - Attach/detach a volume to a device in the Packet host.

Database
~~~~~~~~

misc
^^^^

- redis_info - Gather information about Redis servers

mysql
^^^^^

- mysql_query - Run MySQL queries

postgresql
^^^^^^^^^^

- postgresql_subscription - Add, update, or remove PostgreSQL subscription
- postgresql_user_obj_stat_info - Gather statistics about PostgreSQL user objects

Files
~~~~~

- iso_create - Generate ISO file with specified files or folders

Net Tools
~~~~~~~~~

- hetzner_firewall - Manage Hetzner's dedicated server firewall
- hetzner_firewall_info - Manage Hetzner's dedicated server firewall
- ipwcli_dns - Manage DNS Records for Ericsson IPWorks via ipwcli

ldap
^^^^

- ldap_attrs - Add or remove multiple LDAP attribute values
- ldap_search - Search for entries in a LDAP server

Packaging
~~~~~~~~~

os
^^

- mas - Manage Mac App Store applications with mas-cli

System
~~~~~~

- dpkg_divert - Override a debian package's version of a file
- lbu - Local Backup Utility for Alpine Linux
