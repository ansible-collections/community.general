===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 2.0.0.

v3.8.3
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- lxd connection plugin - make sure that ``ansible_lxd_host``, ``ansible_executable``, and ``ansible_lxd_executable`` work (https://github.com/ansible-collections/community.general/pull/3798).

Bugfixes
--------

- interfaces_file - fixed the check for existing option in interface (https://github.com/ansible-collections/community.general/issues/3841).
- nmcli - fix returning "changed" when no mask set for IPv4 or IPv6 addresses on task rerun (https://github.com/ansible-collections/community.general/issues/3768).
- nmcli - pass ``flags``, ``ingress``, ``egress`` params to ``nmcli`` (https://github.com/ansible-collections/community.general/issues/1086).
- opentelemetry_plugin - honour ``ignore_errors`` when a task has failed instead of reporting an error (https://github.com/ansible-collections/community.general/pull/3837).
- pipx - passes the correct command line option ``--include-apps`` (https://github.com/ansible-collections/community.general/issues/3791).
- proxmox - fixed ``onboot`` parameter causing module failures when undefined (https://github.com/ansible-collections/community.general/issues/3844).

v3.8.2
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- counter_enabled callback plugin - fix output to correctly display host and task counters in serial mode (https://github.com/ansible-collections/community.general/pull/3709).
- ldap_search - allow it to be used even in check mode (https://github.com/ansible-collections/community.general/issues/3619).
- lvol - allows logical volumes to be created with certain size arguments prefixed with ``+`` to preserve behavior of older versions of this module (https://github.com/ansible-collections/community.general/issues/3665).
- nmcli - fixed falsely reported changed status when ``mtu`` is omitted with ``dummy`` connections (https://github.com/ansible-collections/community.general/issues/3612, https://github.com/ansible-collections/community.general/pull/3625).
- terraform - fix command options being ignored during planned/plan in function ``build_plan`` such as ``lock`` or ``lock_timeout`` (https://github.com/ansible-collections/community.general/issues/3707, https://github.com/ansible-collections/community.general/pull/3726).
- xattr - fix exception caused by ``_run_xattr()`` raising a ``ValueError`` due to a mishandling of base64-encoded value (https://github.com/ansible-collections/community.general/issues/3673).

v3.8.1
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- gitlab_deploy_key - fix the SSH Deploy Key being deleted accidentally while running task in check mode (https://github.com/ansible-collections/community.general/issues/3621, https://github.com/ansible-collections/community.general/pull/3622).
- gitlab_project_members - ``get_project_id`` return the project id by matching ``full_path`` or ``name`` (https://github.com/ansible-collections/community.general/pull/3602).
- ipa_* modules - fix environment fallback for ``ipa_host`` option (https://github.com/ansible-collections/community.general/issues/3560).
- nmcli - fixed ``dns6`` option handling so that it is treated as a list internally (https://github.com/ansible-collections/community.general/pull/3563).
- nmcli - fixed ``ipv4.route-metric`` being in properties of type list (https://github.com/ansible-collections/community.general/pull/3563).
- one_image - fix error message when renaming an image (https://github.com/ansible-collections/community.general/pull/3626).
- pipx - ``state=inject`` was failing to parse the list of injected packages (https://github.com/ansible-collections/community.general/pull/3611).
- pipx - set environment variable ``USE_EMOJI=0`` to prevent errors in platforms that do not support ``UTF-8`` (https://github.com/ansible-collections/community.general/pull/3611).
- pkgin - Fix exception encountered when all packages are already installed (https://github.com/ansible-collections/community.general/pull/3583).
- proxmox_group_info - fix module crash if a ``group`` parameter is used (https://github.com/ansible-collections/community.general/pull/3649).
- redfish_utils module utils - do not attempt to change the boot source override mode if not specified by the user (https://github.com/ansible-collections/community.general/issues/3509/).
- redfish_utils module utils - if a manager network property is not specified in the service, attempt to change the requested settings (https://github.com/ansible-collections/community.general/issues/3404/).

v3.8.0
======

Release Summary
---------------

Regular feature and bugfix release. Please note that this is the last minor 3.x.0 release; afterwards there will only be bugfix releases 3.8.y.

Minor Changes
-------------

- mail - added the ``ehlohost`` parameter which allows for manual override of the host used in SMTP EHLO (https://github.com/ansible-collections/community.general/pull/3425).
- nmcli - the option ``routing_rules4`` can now be specified as a list of strings, instead of as a single string (https://github.com/ansible-collections/community.general/issues/3401).
- open-iscsi - adding support for mutual authentication between target and initiator (https://github.com/ansible-collections/community.general/pull/3422).
- opentelemetry callback plugin - added option ``enable_from_environment`` to support enabling the plugin only if the given environment variable exists and it is set to true (https://github.com/ansible-collections/community.general/pull/3498).
- opentelemetry callback plugin - enriched the stacktrace information with the ``message``, ``exception`` and ``stderr`` fields from the failed task (https://github.com/ansible-collections/community.general/pull/3496).
- pkgng - packages being installed (or upgraded) are acted on in one command (per action) (https://github.com/ansible-collections/community.general/issues/2265).
- pkgng - status message specifies number of packages installed and/or upgraded separately. Previously, all changes were reported as one count of packages "added" (https://github.com/ansible-collections/community.general/pull/3393).
- terraform - add ``parallelism`` parameter (https://github.com/ansible-collections/community.general/pull/3540).
- ufw - if ``delete=true`` and ``insert`` option is present, then ``insert`` is now ignored rather than failing with a syntax error (https://github.com/ansible-collections/community.general/pull/3514).

Bugfixes
--------

- gitlab_deploy_key - fix idempotency on projects with multiple deploy keys (https://github.com/ansible-collections/community.general/pull/3473).
- gitlab_group - avoid passing wrong value for ``require_two_factor_authentication`` on creation when the option has not been specified (https://github.com/ansible-collections/community.general/pull/3453).
- gitlab_group_members - ``get_group_id`` return the group ID by matching ``full_path``, ``path`` or ``name`` (https://github.com/ansible-collections/community.general/pull/3400).
- jboss - fix the deployment file permission issue when Jboss server is running under non-root user. The deployment file is copied with file content only. The file permission is set to ``440`` and belongs to root user. When the JBoss ``WildFly`` server is running under non-root user, it is unable to read the deployment file (https://github.com/ansible-collections/community.general/pull/3426).
- keycloak_authentication - fix bug, the requirement was always on ``DISABLED`` when creating a new authentication flow (https://github.com/ansible-collections/community.general/pull/3330).
- keycloak_identity_provider - fix change detection when updating identity provider mappers (https://github.com/ansible-collections/community.general/pull/3538, https://github.com/ansible-collections/community.general/issues/3537).
- keycloak_role - quote role name when used in URL path to avoid errors when role names contain special characters (https://github.com/ansible-collections/community.general/issues/3535, https://github.com/ansible-collections/community.general/pull/3536).
- logstash callback plugin - replace ``_option`` with ``context.CLIARGS`` to fix the plugin on ansible-base and ansible-core (https://github.com/ansible-collections/community.general/issues/2692).
- macports - add ``stdout`` and ``stderr`` to return values (https://github.com/ansible-collections/community.general/issues/3499).
- opentelemetry callback plugin - validated the task result exception without crashing. Also simplifying code a bit (https://github.com/ansible-collections/community.general/pull/3450, https://github.com/ansible/ansible/issues/75726).
- yaml callback plugin - avoid modifying PyYAML so that other plugins using it on the controller, like the ``to_yaml`` filter, do not produce different output (https://github.com/ansible-collections/community.general/issues/3471, https://github.com/ansible-collections/community.general/pull/3478).
- zypper_repository - when an URL to a .repo file was provided in option ``repo=`` and ``state=present`` only the first run was successful, future runs failed due to missing checks prior starting zypper. Usage of ``state=absent`` in combination with a .repo file was not working either (https://github.com/ansible-collections/community.general/issues/1791, https://github.com/ansible-collections/community.general/issues/3466).

New Plugins
-----------

Callback
~~~~~~~~

- elastic - Create distributed traces for each Ansible task in Elastic APM

Inventory
~~~~~~~~~

- opennebula - OpenNebula inventory source

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_tasks_info - Retrieve information about one or more Proxmox VE tasks

Packaging
~~~~~~~~~

language
^^^^^^^^

- pipx - Manages applications installed with pipx

Web Infrastructure
~~~~~~~~~~~~~~~~~~

- rundeck_job_executions_info - Query executions for a Rundeck job
- rundeck_job_run - Run a Rundeck job

v3.7.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- gitlab_group - add new options ``project_creation_level``, ``auto_devops_enabled``, ``subgroup_creation_level`` (https://github.com/ansible-collections/community.general/pull/3248).
- gitlab_group - add new property ``require_two_factor_authentication`` (https://github.com/ansible-collections/community.general/pull/3367).
- gitlab_project - add new properties ``ci_config_path`` and ``shared_runners_enabled`` (https://github.com/ansible-collections/community.general/pull/3379).
- gitlab_project_members - ``gitlab_user`` can now also be a list of users (https://github.com/ansible-collections/community.general/pull/3319).
- gitlab_project_members - added functionality to set all members exactly as given (https://github.com/ansible-collections/community.general/pull/3319).
- gitlab_runner - support project-scoped gitlab.com runners registration (https://github.com/ansible-collections/community.general/pull/634).
- interfaces_file - minor refactor (https://github.com/ansible-collections/community.general/pull/3328).
- ipa_config - add ``ipaselinuxusermaporder`` option to set the SELinux user map order (https://github.com/ansible-collections/community.general/pull/3178).
- kernel_blacklist - revamped the module using ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/3329).
- lxd_container - add ``ignore_volatile_options`` option which allows to disable the behavior that the module ignores options starting with ``volatile.`` (https://github.com/ansible-collections/community.general/pull/3331).
- nmcli - add ``gsm`` support (https://github.com/ansible-collections/community.general/pull/3313).
- pids - refactor to add support for older ``psutil`` versions to the ``pattern`` option (https://github.com/ansible-collections/community.general/pull/3315).
- redfish_command and redfish_config and redfish_utils module utils - add parameter to strip etag of quotes before patch, since some vendors do not properly ``If-Match`` etag with quotes (https://github.com/ansible-collections/community.general/pull/3296).
- tss lookup plugin - added ``token`` parameter for token authorization; ``username`` and ``password`` are optional when ``token`` is provided (https://github.com/ansible-collections/community.general/pull/3327).
- zpool_facts - minor refactoring (https://github.com/ansible-collections/community.general/pull/3332).

Bugfixes
--------

- copr - fix chroot naming issues, ``centos-stream`` changed naming to ``centos-stream-<number>`` (for exmaple ``centos-stream-8``) (https://github.com/ansible-collections/community.general/issues/2084, https://github.com/ansible-collections/community.general/pull/3237).
- django_manage - parameters ``apps`` and ``fixtures`` are now splitted instead of being used as a single argument (https://github.com/ansible-collections/community.general/issues/3333).
- interfaces_file - no longer reporting change when none happened (https://github.com/ansible-collections/community.general/pull/3328).
- linode inventory plugin - fix default value of new option ``ip_style`` (https://github.com/ansible-collections/community.general/issues/3337).
- openbsd_pkg - fix crash from ``KeyError`` exception when package installs, but ``pkg_add`` returns with a non-zero exit code (https://github.com/ansible-collections/community.general/pull/3336).
- redfish_utils module utils - if given, add account ID of user that should be created to HTTP request (https://github.com/ansible-collections/community.general/pull/3343/).

New Plugins
-----------

Callback
~~~~~~~~

- opentelemetry - Create distributed traces with OpenTelemetry

Filter
~~~~~~

- unicode_normalize - Normalizes unicode strings to facilitate comparison of characters with normalized forms

Inventory
~~~~~~~~~

- icinga2 - Icinga2 inventory source

New Modules
-----------

Database
~~~~~~~~

misc
^^^^

- redis_data - Set key value pairs in Redis
- redis_data_info - Get value of key in Redis database

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_user_federation - Allows administration of Keycloak user federations via Keycloak API

v3.6.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- dig lookup plugin - add ``retry_servfail`` option (https://github.com/ansible-collections/community.general/pull/3247).
- gitlab_group_members - ``gitlab_user`` can now also be a list of users (https://github.com/ansible-collections/community.general/pull/3047).
- gitlab_group_members - added functionality to set all members exactly as given (https://github.com/ansible-collections/community.general/pull/3047).
- ini_file - add abbility to define multiple options with the same name but different values (https://github.com/ansible-collections/community.general/issues/273, https://github.com/ansible-collections/community.general/issues/1204).
- ini_file - add module option ``exclusive`` (boolean) for the ability to add/remove single ``option=value`` entries without overwriting existing options with the same name but different values (https://github.com/ansible-collections/community.general/pull/3033).
- keycloak_realm - add ``events_enabled`` parameter to allow activation or deactivation of login events (https://github.com/ansible-collections/community.general/pull/3231).
- linode inventory plugin - adds the ``ip_style`` configuration key. Set to ``api`` to get more detailed network details back from the remote Linode host (https://github.com/ansible-collections/community.general/pull/3203).
- module_helper cmd module utils - added the ``ArgFormat`` style ``BOOLEAN_NOT``, to add CLI parameters when the module argument is false-ish (https://github.com/ansible-collections/community.general/pull/3290).
- module_helper module_utils - added classmethod to trigger the execution of MH modules (https://github.com/ansible-collections/community.general/pull/3206).
- nmcli - add ``gre`` tunnel support (https://github.com/ansible-collections/community.general/issues/3105, https://github.com/ansible-collections/community.general/pull/3262).
- nmcli - query ``nmcli`` directly to determine available WiFi options (https://github.com/ansible-collections/community.general/pull/3141).
- open_iscsi - minor refactoring (https://github.com/ansible-collections/community.general/pull/3286).
- openwrt_init - minor refactoring (https://github.com/ansible-collections/community.general/pull/3284).
- pamd - minor refactorings (https://github.com/ansible-collections/community.general/pull/3285).
- redfish_info - include ``Status`` property for Thermal objects when querying Thermal properties via ``GetChassisThermals`` command (https://github.com/ansible-collections/community.general/issues/3232).
- scaleway plugin inventory - parse scw-cli config file for ``oauth_token`` (https://github.com/ansible-collections/community.general/pull/3250).
- slack - minor refactoring (https://github.com/ansible-collections/community.general/pull/3205).
- snap - improved module error handling, especially for the case when snap server is down (https://github.com/ansible-collections/community.general/issues/2970).
- tss lookup plugin - added new parameter for domain authorization (https://github.com/ansible-collections/community.general/pull/3228).
- tss lookup plugin - refactored to decouple the supporting third-party library (``python-tss-sdk``) (https://github.com/ansible-collections/community.general/pull/3252).
- vdo - minor refactoring of the code (https://github.com/ansible-collections/community.general/pull/3191).
- zfs - added diff mode support (https://github.com/ansible-collections/community.general/pull/502).
- zypper - prefix zypper commands with ``/sbin/transactional-update --continue --drop-if-no-change --quiet run`` if transactional updates are detected (https://github.com/ansible-collections/community.general/issues/3159).

Bugfixes
--------

- apache2_module - fix ``a2enmod``/``a2dismod`` detection, and error message when not found (https://github.com/ansible-collections/community.general/issues/3253).
- django_manage - argument ``command`` is being splitted again as it should (https://github.com/ansible-collections/community.general/issues/3215).
- keycloak_realm - element type for ``events_listeners`` parameter should be ``string`` instead of ``dict`` (https://github.com/ansible-collections/community.general/pull/3231).
- launchd - use private attribute to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- logdns callback plugin - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- maven_artifact - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- memcached cache plugin - change function argument names to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- netapp module utils - remove always-true conditional to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- nmcli - added ip4/ip6 configuration arguments for ``sit`` and ``ipip`` tunnels (https://github.com/ansible-collections/community.general/issues/3238, https://github.com/ansible-collections/community.general/pull/3239).
- one_template - change function argument name to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- online inventory plugin - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- online module utils - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- open_iscsi - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3286).
- openwrt_init - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3284).
- packet_device - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- packet_sshkey - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- pamd - code for ``state=updated`` when dealing with the pam module arguments, made no distinction between ``None`` and an empty list (https://github.com/ansible-collections/community.general/issues/3260).
- proxmox_kvm - clone operation should return the VMID of the target VM and not that of the source VM. This was failing when the target VM with the chosen name already existed (https://github.com/ansible-collections/community.general/pull/3266).
- saltstack connection plugin - fix function signature (https://github.com/ansible-collections/community.general/pull/3194).
- scaleway inventory script - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3195).
- scaleway module utils - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- tss lookup plugin - fixed backwards compatibility issue with ``python-tss-sdk`` version <=0.0.5 (https://github.com/ansible-collections/community.general/issues/3192, https://github.com/ansible-collections/community.general/pull/3199).
- udm_dns_record - fixed managing of PTR records, which can never have worked before (https://github.com/ansible-collections/community.general/pull/3256).
- ufw - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- vbox inventory script - change function argument name to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3195).
- vdo - boolean arguments now compared with proper ``true`` and ``false`` values instead of string representations like ``"yes"`` or ``"no"`` (https://github.com/ansible-collections/community.general/pull/3191).
- zfs - treated received properties as local (https://github.com/ansible-collections/community.general/pull/502).

New Modules
-----------

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_identity_provider - Allows administration of Keycloak identity providers via Keycloak API

v3.5.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- apache2_module - minor refactoring improving code quality, readability and speed (https://github.com/ansible-collections/community.general/pull/3106).
- dnsimple - module rewrite to include support for python-dnsimple>=2.0.0; also add ``sandbox`` parameter (https://github.com/ansible-collections/community.general/pull/2946).
- github_repo - add new option ``api_url``  to allow working with on premises installations (https://github.com/ansible-collections/community.general/pull/3038).
- gunicorn - search for ``gunicorn`` binary in more paths (https://github.com/ansible-collections/community.general/pull/3092).
- hana_query - added the abillity to use hdbuserstore (https://github.com/ansible-collections/community.general/pull/3125).
- hpilo_info - added ``host_power_status`` return value to report power state of machine with ``OFF``, ``ON`` or ``UNKNOWN`` (https://github.com/ansible-collections/community.general/pull/3079).
- nmcli - add ``dummy`` interface support (https://github.com/ansible-collections/community.general/issues/724).
- nmcli - add ``wifi-sec`` option change detection to support managing secure Wi-Fi connections (https://github.com/ansible-collections/community.general/pull/3136).
- nmcli - add ``wifi`` option to support managing Wi-Fi settings such as ``hidden`` or ``mode`` (https://github.com/ansible-collections/community.general/pull/3081).
- pkgin - in case of ``pkgin`` tool failue, display returned standard output ``stdout`` and standard error ``stderr`` to ease debugging (https://github.com/ansible-collections/community.general/issues/3146).
- proxmox inventory plugin - added snapshots to host facts (https://github.com/ansible-collections/community.general/pull/3044).
- redfish_command - add ``boot_override_mode`` argument to BootSourceOverride commands (https://github.com/ansible-collections/community.general/issues/3134).
- supervisorctl - using standard Ansible mechanism to validate ``signalled`` state required parameter (https://github.com/ansible-collections/community.general/pull/3068).

Security Fixes
--------------

- nmcli - do not pass WiFi secrets on the ``nmcli`` command line. Use ``nmcli con edit`` instead and pass secrets as ``stdin`` (https://github.com/ansible-collections/community.general/issues/3145).

Bugfixes
--------

- ali_instance_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- archive - fixing archive root determination when longest common root is ``/`` (https://github.com/ansible-collections/community.general/pull/3036).
- deploy_helper - improved parameter checking by using standard Ansible construct (https://github.com/ansible-collections/community.general/pull/3104).
- django_manage - refactor to call ``run_command()`` passing command as a list instead of string (https://github.com/ansible-collections/community.general/pull/3098).
- ejabberd_user - replaced in-code check with ``required_if``, using ``get_bin_path()`` for the command, passing args to ``run_command()`` as list instead of string (https://github.com/ansible-collections/community.general/pull/3093).
- gitlab_group_members - fixes issue when gitlab group has more then 20 members, pagination problem (https://github.com/ansible-collections/community.general/issues/3041).
- gitlab_project_members - fixes issue when gitlab group has more then 20 members, pagination problem (https://github.com/ansible-collections/community.general/issues/3041).
- idrac_redfish_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- ini_file - fix inconsistency between empty value and no value (https://github.com/ansible-collections/community.general/issues/3031).
- java_cert - import private key as well as public certificate from PKCS#12 (https://github.com/ansible-collections/community.general/issues/2460).
- memset_memstore_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- memset_server_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_datacenter_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_enclosure_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_ethernet_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_fc_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_fcoe_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_logical_interconnect_group_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_network_set_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_san_manager_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- openbsd_pkg - fix regexp matching crash. This bug could trigger on package names with special characters, for example ``g++`` (https://github.com/ansible-collections/community.general/pull/3161).
- pids - avoid crashes for older ``psutil`` versions, like on RHEL6 and RHEL7 (https://github.com/ansible-collections/community.general/pull/2808).
- proxmox inventory plugin - fixed plugin failure when a ``qemu`` guest has no ``template`` key (https://github.com/ansible-collections/community.general/pull/3052).
- proxmox_kvm - fix result of clone, now returns ``newid`` instead of ``vmid`` (https://github.com/ansible-collections/community.general/pull/3034).
- rax_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- redfish_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- smartos_image_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- snmp_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- supervisorctl - state ``signalled`` was not working (https://github.com/ansible-collections/community.general/pull/3068).
- taiga - some constructs in the module fixed to work also in Python 3 (https://github.com/ansible-collections/community.general/pull/3067).
- tss lookup plugin - fixed incompatibility with ``python-tss-sdk`` version 1.0.0 (https://github.com/ansible-collections/community.general/issues/3057, https://github.com/ansible-collections/community.general/pull/3139).
- utm_aaa_group_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_ca_host_key_cert_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_network_interface_address_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_proxy_frontend_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_proxy_location_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- xenserver_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- xfconf_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).

New Modules
-----------

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_client_rolemapping - Allows administration of Keycloak client_rolemapping with the Keycloak API

Packaging
~~~~~~~~~

language
^^^^^^^^

- ansible_galaxy_install - Install Ansible roles or collections using ansible-galaxy

System
~~~~~~

- sap_task_list_execute - Perform SAP Task list execution
- xfconf_info - Retrieve XFCE4 configurations

v3.4.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- archive - added ``dest_state`` return value to describe final state of ``dest`` after successful task execution (https://github.com/ansible-collections/community.general/pull/2913).
- archive - refactoring prior to fix for idempotency checks. The fix will be a breaking change and only appear in community.general 4.0.0 (https://github.com/ansible-collections/community.general/pull/2987).
- datadog_monitor - allow creation of composite datadog monitors (https://github.com/ansible-collections/community.general/issues/2956).
- filesystem - extend support for FreeBSD. Avoid potential data loss by checking existence of a filesystem with ``fstyp`` (native command) if ``blkid`` (foreign command) doesn't find one. Add support for character devices and ``ufs`` filesystem type (https://github.com/ansible-collections/community.general/pull/2902).
- gitlab_project - add new options ``allow_merge_on_skipped_pipeline``, ``only_allow_merge_if_all_discussions_are_resolved``, ``only_allow_merge_if_pipeline_succeeds``, ``packages_enabled``, ``remove_source_branch_after_merge``, ``squash_option`` (https://github.com/ansible-collections/community.general/pull/3002).
- jenkins_job_info - the ``password`` and ``token`` parameters can also be omitted to retrieve only public information (https://github.com/ansible-collections/community.general/pull/2948).
- keycloak_authentication - enhanced diff mode to also return before and after state when the authentication flow is updated (https://github.com/ansible-collections/community.general/pull/2963).
- keycloak_client - add ``authentication_flow_binding_overrides`` option (https://github.com/ansible-collections/community.general/pull/2949).
- module_helper module utils - added feature flag parameters to ``CmdMixin`` to control whether ``rc``, ``out`` and ``err`` are automatically added to the module output (https://github.com/ansible-collections/community.general/pull/2922).
- nmcli - add ``runner`` and ``runner_hwaddr_policy`` options (https://github.com/ansible-collections/community.general/issues/2901).
- rax_mon_notification_plan - fixed validation checks by specifying type ``str`` as the ``elements`` of parameters ``ok_state``, ``warning_state`` and ``critical_state`` (https://github.com/ansible-collections/community.general/pull/2955).

Bugfixes
--------

- launchd - fixed sanity check in the module's code (https://github.com/ansible-collections/community.general/pull/2960).
- pamd - fixed problem with files containing only one or two lines (https://github.com/ansible-collections/community.general/issues/2925).
- proxmox inventory plugin - fixed parsing failures when some cluster nodes are offline (https://github.com/ansible-collections/community.general/issues/2931).
- redfish_command - fix extraneous error caused by missing ``bootdevice`` argument when using the ``DisableBootOverride`` sub-command (https://github.com/ansible-collections/community.general/issues/3005).
- snap - fix formatting of ``--channel`` argument when the ``channel`` option is used (https://github.com/ansible-collections/community.general/pull/3028).

New Modules
-----------

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_clientscope - Allows administration of Keycloak client_scopes via Keycloak API
- keycloak_role - Allows administration of Keycloak roles via Keycloak API

Source Control
~~~~~~~~~~~~~~

gitlab
^^^^^^

- gitlab_protected_branch - (un)Marking existing branches for protection

v3.3.2
======

Release Summary
---------------

Extraordinary bugfix release to fix some annoying bugs.

Bugfixes
--------

- archive - fixed task failure when using the ``remove`` option with a ``path`` containing nested files for ``format``s other than ``zip`` (https://github.com/ansible-collections/community.general/issues/2919).
- lvol - honor ``check_mode`` on thinpool (https://github.com/ansible-collections/community.general/issues/2934).
- module_helper module utils - fixed change-tracking for dictionaries and lists (https://github.com/ansible-collections/community.general/pull/2951).
- npm - correctly handle cases where a dependency does not have a ``version`` property because it is either missing or invalid (https://github.com/ansible-collections/community.general/issues/2917).
- pacman - fix changed status when ignorepkg has been defined (https://github.com/ansible-collections/community.general/issues/1758).
- snap - fixed the order of the ``--classic`` parameter in the command line invocation (https://github.com/ansible-collections/community.general/issues/2916).

v3.3.1
======

Release Summary
---------------

Extraordinary bugfix release to fix a fatal bug in ``snap``.

Bugfixes
--------

- keycloak_authentication - fix bug when two identical executions are in the same authentication flow (https://github.com/ansible-collections/community.general/pull/2904).
- module_helper module utils - avoid failing when non-zero ``rc`` is present on regular exit (https://github.com/ansible-collections/community.general/pull/2912).
- snap - fix various bugs which prevented the module from working at all, and which resulted in ``state=absent`` fail on absent snaps (https://github.com/ansible-collections/community.general/issues/2835, https://github.com/ansible-collections/community.general/issues/2906, https://github.com/ansible-collections/community.general/pull/2912).

v3.3.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- Avoid internal ansible-core module_utils in favor of equivalent public API available since at least Ansible 2.9 (https://github.com/ansible-collections/community.general/pull/2877).
- datadog_event - adding parameter ``api_host`` to allow selecting a datadog API endpoint instead of using the default one (https://github.com/ansible-collections/community.general/issues/2774, https://github.com/ansible-collections/community.general/pull/2775).
- flatpak - allows installing or uninstalling a list of packages (https://github.com/ansible-collections/community.general/pull/2521).
- gem - add ``bindir`` option to specify an installation path for executables such as ``/home/user/bin`` or ``/home/user/.local/bin`` (https://github.com/ansible-collections/community.general/pull/2837).
- gem - add ``norc`` option to avoid loading any ``.gemrc`` file (https://github.com/ansible-collections/community.general/pull/2837).
- gitlab_project - projects can be created under other user's namespaces with the new ``username`` option (https://github.com/ansible-collections/community.general/pull/2824).
- gitlab_user - add functionality for adding external identity providers to a GitLab user (https://github.com/ansible-collections/community.general/pull/2691).
- gitlab_user - allow to reset an existing password with the new ``reset_password`` option (https://github.com/ansible-collections/community.general/pull/2691).
- gitlab_user - specifying a password is no longer necessary (https://github.com/ansible-collections/community.general/pull/2691).
- jenkins_build - support stopping a running jenkins build (https://github.com/ansible-collections/community.general/pull/2850).
- jenkins_plugin - add fallback url(s) for failure of plugin installation/download (https://github.com/ansible-collections/community.general/pull/1334).
- nmcli - add ``disabled`` value to ``method6`` option (https://github.com/ansible-collections/community.general/issues/2730).
- nmcli - add ``routing_rules4`` and ``may_fail4`` options (https://github.com/ansible-collections/community.general/issues/2730).
- nrdp callback plugin - parameters are now converted to strings, except ``validate_certs`` which is converted to boolean (https://github.com/ansible-collections/community.general/pull/2878).
- redhat_subscription - add ``server_prefix`` and ``server_port`` parameters (https://github.com/ansible-collections/community.general/pull/2779).
- redis - allow to use the term ``replica`` instead of ``slave``, which has been the official Redis terminology since 2018 (https://github.com/ansible-collections/community.general/pull/2867).
- snap - added ``enabled`` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/1990).
- splunk callback plugin - add ``batch`` option for user-configurable correlation ID's (https://github.com/ansible-collections/community.general/issues/2790).
- terraform - add ``check_destroy`` optional parameter to check for deletion of resources before it is applied (https://github.com/ansible-collections/community.general/pull/2874).
- timezone - print error message to debug instead of warning when timedatectl fails (https://github.com/ansible-collections/community.general/issues/1942).

Deprecated Features
-------------------

- ali_instance_info - marked removal version of deprecated parameters ``availability_zone`` and ``instance_names`` (https://github.com/ansible-collections/community.general/issues/2429).
- serverless - deprecating parameter ``functions`` because it was not used in the code (https://github.com/ansible-collections/community.general/pull/2845).

Bugfixes
--------

- _mount module utils - fixed the sanity checks (https://github.com/ansible-collections/community.general/pull/2883).
- archive - fixed ``exclude_path`` values causing incorrect archive root (https://github.com/ansible-collections/community.general/pull/2816).
- archive - fixed improper file names for single file zip archives (https://github.com/ansible-collections/community.general/issues/2818).
- archive - fixed incorrect ``state`` result value documentation (https://github.com/ansible-collections/community.general/pull/2816).
- gitlab_project - user projects are created using namespace ID now, instead of user ID (https://github.com/ansible-collections/community.general/pull/2881).
- ini_file - fix Unicode processing for Python 2 (https://github.com/ansible-collections/community.general/pull/2875).
- ipa_sudorule - call ``sudorule_add_allow_command`` method instead of  ``sudorule_add_allow_command_group`` (https://github.com/ansible-collections/community.general/issues/2442).
- java_keystore - add parameter ``keystore_type`` to control output file format and override ``keytool``'s default, which depends on Java version (https://github.com/ansible-collections/community.general/issues/2515).
- jenkins_build - examine presence of ``build_number`` before deleting a jenkins build (https://github.com/ansible-collections/community.general/pull/2850).
- modprobe - added additional checks to ensure module load/unload is effective (https://github.com/ansible-collections/community.general/issues/1608).
- nmcli - fixes team-slave configuration by adding connection.slave-type (https://github.com/ansible-collections/community.general/issues/766).
- npm - when the ``version`` option is used the comparison of installed vs missing will use name@version instead of just name, allowing version specific updates (https://github.com/ansible-collections/community.general/issues/2021).
- proxmox_kvm - fix parsing of Proxmox VM information with device info not containing a comma, like disks backed by ZFS zvols (https://github.com/ansible-collections/community.general/issues/2840).
- scaleway plugin inventory - fix ``JSON object must be str, not 'bytes'`` with Python 3.5 (https://github.com/ansible-collections/community.general/issues/2769).
- yum_versionlock - fix idempotency when using wildcard (asterisk) in ``name`` option (https://github.com/ansible-collections/community.general/issues/2761).

New Modules
-----------

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_authentication - Configure authentication in Keycloak

v3.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- Remove unnecessary ``__init__.py`` files from ``plugins/`` (https://github.com/ansible-collections/community.general/pull/2632).
- archive - added ``exclusion_patterns`` option to exclude files or subdirectories from archives (https://github.com/ansible-collections/community.general/pull/2616).
- cloud_init_data_facts - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- composer - add ``composer_executable`` option (https://github.com/ansible-collections/community.general/issues/2649).
- flatpak - add ``no_dependencies`` parameter (https://github.com/ansible/ansible/pull/55452, https://github.com/ansible-collections/community.general/pull/2751).
- ini_file - opening file with encoding ``utf-8-sig`` (https://github.com/ansible-collections/community.general/issues/2189).
- jira - add comment visibility parameter for comment operation (https://github.com/ansible-collections/community.general/pull/2556).
- maven_artifact - added ``checksum_alg`` option to support SHA1 checksums in order to support FIPS systems (https://github.com/ansible-collections/community.general/pull/2662).
- module_helper module utils - method ``CmdMixin.run_command()`` now accepts ``process_output`` specifying a function to process the outcome of the underlying ``module.run_command()`` (https://github.com/ansible-collections/community.general/pull/2564).
- nmcli - add new options to ignore automatic DNS servers and gateways (https://github.com/ansible-collections/community.general/issues/1087).
- onepassword lookup plugin - add ``domain`` option (https://github.com/ansible-collections/community.general/issues/2734).
- open_iscsi - add ``auto_portal_startup`` parameter to allow ``node.startup`` setting per portal (https://github.com/ansible-collections/community.general/issues/2685).
- open_iscsi - also consider ``portal`` and ``port`` to check if already logged in or not (https://github.com/ansible-collections/community.general/issues/2683).
- proxmox_group_info - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- proxmox_kvm - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- rhevm - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- serverless - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- stacki_host - minor refactoring (https://github.com/ansible-collections/community.general/pull/2681).
- terraform - add option ``overwrite_init`` to skip init if exists (https://github.com/ansible-collections/community.general/pull/2573).
- terraform - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).

Deprecated Features
-------------------

- All inventory and vault scripts will be removed from community.general in version 4.0.0. If you are referencing them, please update your references to the new `contrib-scripts GitHub repository <https://github.com/ansible-community/contrib-scripts>`_ so your workflow will not break once community.general 4.0.0 is released (https://github.com/ansible-collections/community.general/pull/2697).

Bugfixes
--------

- consul_kv lookup plugin - allow to set ``recurse``, ``index``, ``datacenter`` and ``token`` as keyword arguments (https://github.com/ansible-collections/community.general/issues/2124).
- cpanm - also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/pull/2731).
- influxdb_user - fix bug which removed current privileges instead of appending them to existing ones (https://github.com/ansible-collections/community.general/issues/2609, https://github.com/ansible-collections/community.general/pull/2614).
- iptables_state - call ``async_status`` action plugin rather than its module (https://github.com/ansible-collections/community.general/issues/2700).
- iptables_state - fix a broken query of ``async_status`` result with current ansible-core development version (https://github.com/ansible-collections/community.general/issues/2627, https://github.com/ansible-collections/community.general/pull/2671).
- java_cert - fix issue with incorrect alias used on PKCS#12 certificate import (https://github.com/ansible-collections/community.general/pull/2560).
- jenkins_plugin - use POST method for sending request to jenkins API when ``state`` option is one of ``enabled``, ``disabled``, ``pinned``, ``unpinned``, or ``absent`` (https://github.com/ansible-collections/community.general/issues/2510).
- json_query filter plugin - avoid 'unknown type' errors for more Ansible internal types (https://github.com/ansible-collections/community.general/pull/2607).
- keycloak_realm - ``ssl_required`` changed from a boolean type to accept the strings ``none``, ``external`` or ``all``. This is not a breaking change since the module always failed when a boolean was supplied (https://github.com/ansible-collections/community.general/pull/2693).
- keycloak_realm - remove warning that ``reset_password_allowed`` needs to be marked as ``no_log`` (https://github.com/ansible-collections/community.general/pull/2694).
- module_helper module utils - ``CmdMixin`` must also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/pull/2731).
- netcup_dns - use ``str(ex)`` instead of unreliable ``ex.message`` in exception handling to fix ``AttributeError`` in error cases (https://github.com/ansible-collections/community.general/pull/2590).
- ovir4 inventory script - improve configparser creation to avoid crashes for options without values (https://github.com/ansible-collections/community.general/issues/674).
- proxmox_kvm - fixed ``vmid`` return value when VM with ``name`` already exists (https://github.com/ansible-collections/community.general/issues/2648).
- redis cache - improved connection string parsing (https://github.com/ansible-collections/community.general/issues/497).
- rhsm_release - fix the issue that module considers 8, 7Client and 7Workstation as invalid releases (https://github.com/ansible-collections/community.general/pull/2571).
- ssh_config - reduce stormssh searches based on host (https://github.com/ansible-collections/community.general/pull/2568/).
- stacki_host - when adding a new server, ``rack`` and ``rank`` must be passed, and network parameters are optional (https://github.com/ansible-collections/community.general/pull/2681).
- terraform - ensure the workspace is set back to its previous value when the apply fails (https://github.com/ansible-collections/community.general/pull/2634).
- xfconf - also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/issues/2715).
- zypper_repository - fix idempotency on adding repository with ``$releasever`` and ``$basearch`` variables (https://github.com/ansible-collections/community.general/issues/1985).

New Plugins
-----------

Lookup
~~~~~~

- random_string - Generates random string

New Modules
-----------

Database
~~~~~~~~

saphana
^^^^^^^

- hana_query - Execute SQL on HANA

Files
~~~~~

- sapcar_extract - Manages SAP SAPCAR archives

Packaging
~~~~~~~~~

os
^^

- pacman_key - Manage pacman's list of trusted keys

v3.1.0
======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- ModuleHelper module utils - improved mechanism for customizing the calculation of ``changed`` (https://github.com/ansible-collections/community.general/pull/2514).
- chroot connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- cmd (Module Helper) module utils - ``CmdMixin`` now pulls the value for ``run_command()`` params from ``self.vars``, as opposed to previously retrieving those from ``self.module.params`` (https://github.com/ansible-collections/community.general/pull/2517).
- filesystem - cleanup and revamp module, tests and doc. Pass all commands to ``module.run_command()`` as lists. Move the device-vs-mountpoint logic to ``grow()`` method. Give to all ``get_fs_size()`` the same logic and error handling. (https://github.com/ansible-collections/community.general/pull/2472).
- funcd connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- gitlab_user - add ``expires_at`` option (https://github.com/ansible-collections/community.general/issues/2325).
- idrac_redfish_config - modified set_manager_attributes function to skip invalid attribute instead of returning. Added skipped attributes to output. Modified module exit to add warning variable (https://github.com/ansible-collections/community.general/issues/1995).
- influxdb_retention_policy - add ``state`` parameter with allowed values ``present`` and ``absent`` to support deletion of existing retention policies (https://github.com/ansible-collections/community.general/issues/2383).
- influxdb_retention_policy - simplify duration logic parsing (https://github.com/ansible-collections/community.general/pull/2385).
- iocage connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- jail connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- java_keystore - added ``ssl_backend`` parameter for using the cryptography library instead of the OpenSSL binary (https://github.com/ansible-collections/community.general/pull/2485).
- java_keystore - replace envvar by stdin to pass secret to ``keytool`` (https://github.com/ansible-collections/community.general/pull/2526).
- linode - added proper traceback when failing due to exceptions (https://github.com/ansible-collections/community.general/pull/2410).
- linode - parameter ``additional_disks`` is now validated as a list of dictionaries (https://github.com/ansible-collections/community.general/pull/2410).
- lxc connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- module_helper module utils - break down of the long file into smaller pieces (https://github.com/ansible-collections/community.general/pull/2393).
- nmcli - remove dead code, ``options`` never contains keys from ``param_alias`` (https://github.com/ansible-collections/community.general/pull/2417).
- pacman - add ``executable`` option to use an alternative pacman binary (https://github.com/ansible-collections/community.general/issues/2524).
- passwordstore lookup - add option ``missing`` to choose what to do if the password file is missing (https://github.com/ansible-collections/community.general/pull/2500).
- qubes connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- redfish_config - modified module exit to add warning variable (https://github.com/ansible-collections/community.general/issues/1995).
- redfish_utils module utils - modified set_bios_attributes function to skip invalid attribute instead of returning. Added skipped attributes to output (https://github.com/ansible-collections/community.general/issues/1995).
- saltstack connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- spotinst_aws_elastigroup - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/2355).
- zfs_delegate_admin - drop choices from permissions, allowing any permission supported by the underlying zfs commands (https://github.com/ansible-collections/community.general/pull/2540).
- zone connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).

Deprecated Features
-------------------

- The nios, nios_next_ip, nios_next_network lookup plugins, the nios documentation fragment, and the nios_host_record, nios_ptr_record, nios_mx_record, nios_fixed_address, nios_zone, nios_member, nios_a_record, nios_aaaa_record, nios_network, nios_dns_view, nios_txt_record, nios_naptr_record, nios_srv_record, nios_cname_record, nios_nsgroup, and nios_network_view module have been deprecated and will be removed from community.general 5.0.0. Please install the `infoblox.nios_modules <https://galaxy.ansible.com/infoblox/nios_modules>`_ collection instead and use its plugins and modules (https://github.com/ansible-collections/community.general/pull/2458).
- The vendored copy of ``ipaddress`` will be removed in community.general 4.0.0. Please switch to ``ipaddress`` from the Python 3 standard library, or `from pypi <https://pypi.org/project/ipaddress/>`_, if your code relies on the vendored version of ``ipaddress`` (https://github.com/ansible-collections/community.general/pull/2459).
- linode - parameter ``backupsenabled`` is deprecated and will be removed in community.general 5.0.0 (https://github.com/ansible-collections/community.general/pull/2410).
- lxd inventory plugin - the plugin will require ``ipaddress`` installed when used with Python 2 from community.general 4.0.0 on. ``ipaddress`` is part of the Python 3 standard library, but can be installed for Python 2 from pypi (https://github.com/ansible-collections/community.general/pull/2459).
- scaleway_security_group_rule - the module will require ``ipaddress`` installed when used with Python 2 from community.general 4.0.0 on. ``ipaddress`` is part of the Python 3 standard library, but can be installed for Python 2 from pypi (https://github.com/ansible-collections/community.general/pull/2459).

Bugfixes
--------

- consul_acl - update the hcl allowlist to include all supported options (https://github.com/ansible-collections/community.general/pull/2495).
- filesystem - repair ``reiserfs`` fstype support after adding it to integration tests (https://github.com/ansible-collections/community.general/pull/2472).
- influxdb_user - allow creation of admin users when InfluxDB authentication is enabled but no other user exists on the database. In this scenario, InfluxDB 1.x allows only ``CREATE USER`` queries and rejects any other query (https://github.com/ansible-collections/community.general/issues/2364).
- influxdb_user - fix bug where an influxdb user has no privileges for 2 or more databases (https://github.com/ansible-collections/community.general/pull/2499).
- iptables_state - fix a 'FutureWarning' in a regex and do some basic code clean up (https://github.com/ansible-collections/community.general/pull/2525).
- iptables_state - fix initialization of iptables from null state when adressing more than one table (https://github.com/ansible-collections/community.general/issues/2523).
- nmap inventory plugin - fix local variable error when cache is disabled (https://github.com/ansible-collections/community.general/issues/2512).

New Plugins
-----------

Filter
~~~~~~

- groupby_as_dict - Transform a sequence of dictionaries to a dictionary where the dictionaries are indexed by an attribute

Lookup
~~~~~~

- dependent - Composes a list with nested elements of other lists or dicts which can depend on previous loop variables
- random_pet - Generates random pet names

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_nic - Management of a NIC of a Qemu(KVM) VM in a Proxmox VE cluster.

Notification
~~~~~~~~~~~~

- discord - Send Discord messages

v3.0.2
======

Release Summary
---------------

Bugfix release for the first Ansible 4.0.0 release candidate.

Bugfixes
--------

- stackpath_compute inventory script - fix broken validation checks for client ID and client secret (https://github.com/ansible-collections/community.general/pull/2448).
- zfs - certain ZFS properties, especially sizes, would lead to a task being falsely marked as "changed" even when no actual change was made (https://github.com/ansible-collections/community.general/issues/975, https://github.com/ansible-collections/community.general/pull/2454).

v3.0.1
======

Release Summary
---------------

Bugfix release for the next Ansible 4.0.0 beta.

Bugfixes
--------

- composer - use ``no-interaction`` option when discovering available options to avoid an issue where composer hangs (https://github.com/ansible-collections/community.general/pull/2348).
- influxdb_retention_policy - fix bug where ``INF`` duration values failed parsing (https://github.com/ansible-collections/community.general/pull/2385).
- inventory and vault scripts - change file permissions to make vendored inventory and vault scripts exectuable (https://github.com/ansible-collections/community.general/pull/2337).
- linode_v4 - changed the error message to point to the correct bugtracker URL (https://github.com/ansible-collections/community.general/pull/2430).
- lvol - fixed rounding errors (https://github.com/ansible-collections/community.general/issues/2370).
- lvol - fixed size unit capitalization to match units used between different tools for comparison (https://github.com/ansible-collections/community.general/issues/2360).
- nmcli - compare MAC addresses case insensitively to fix idempotency issue (https://github.com/ansible-collections/community.general/issues/2409).
- nmcli - if type is ``bridge-slave`` add ``slave-type bridge`` to ``nmcli`` command (https://github.com/ansible-collections/community.general/issues/2408).
- one_vm - Allow missing NIC keys (https://github.com/ansible-collections/community.general/pull/2435).
- puppet - replace ``console` with ``stdout`` in ``logdest`` option when ``all`` has been chosen (https://github.com/ansible-collections/community.general/issues/1190).
- svr4pkg - convert string to a bytes-like object to avoid ``TypeError`` with Python 3 (https://github.com/ansible-collections/community.general/issues/2373).

v3.0.0
======

Release Summary
---------------

This is release 3.0.0 of ``community.general``, released on 2021-04-26.

Minor Changes
-------------

- apache2_mod_proxy - refactored/cleaned-up part of the code (https://github.com/ansible-collections/community.general/pull/2142).
- archive - refactored some reused code out into a couple of functions (https://github.com/ansible-collections/community.general/pull/2061).
- atomic_container - using ``get_bin_path()`` before calling ``run_command()`` (https://github.com/ansible-collections/community.general/pull/2144).
- atomic_host - using ``get_bin_path()`` before calling ``run_command()`` (https://github.com/ansible-collections/community.general/pull/2144).
- atomic_image - using ``get_bin_path()`` before calling ``run_command()`` (https://github.com/ansible-collections/community.general/pull/2144).
- beadm - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- bitbucket_pipeline_variable - removed unreachable code (https://github.com/ansible-collections/community.general/pull/2157).
- bundler - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- clc_* modules - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1771).
- consul - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- consul_acl - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- consul_io inventory script - conf options - allow custom configuration options via env variables (https://github.com/ansible-collections/community.general/pull/620).
- consul_session - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- cpanm - honor and install specified version when running in ``new`` mode; that feature is not available in ``compatibility`` mode (https://github.com/ansible-collections/community.general/issues/208).
- cpanm - rewritten using ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/2218).
- csv module utils - new module_utils for shared functions between ``from_csv`` filter and ``read_csv`` module (https://github.com/ansible-collections/community.general/pull/2037).
- datadog_monitor - add missing monitor types ``query alert``, ``trace-analytics alert``, ``rum alert`` (https://github.com/ansible-collections/community.general/pull/1723).
- datadog_monitor - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- dnsimple - add CAA records to the whitelist of valid record types (https://github.com/ansible-collections/community.general/pull/1814).
- dnsimple - elements of list parameters ``record_ids`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- gitlab_deploy_key - when the given key title already exists but has a different public key, the public key will now be updated to given value (https://github.com/ansible-collections/community.general/pull/1661).
- gitlab_runner - elements of list parameters ``tag_list`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- grove - the option ``message`` has been renamed to ``message_content``. The old name ``message`` is kept as an alias and will be removed for community.general 4.0.0. This was done because ``message`` is used internally by Ansible (https://github.com/ansible-collections/community.general/pull/1929).
- heroku_collaborator - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- hiera lookup - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- homebrew_tap - add support to specify search path for ``brew`` executable (https://github.com/ansible-collections/community.general/issues/1702).
- ipa_config - add new options ``ipaconfigstring``, ``ipadefaultprimarygroup``, ``ipagroupsearchfields``, ``ipahomesrootdir``, ``ipabrkauthzdata``, ``ipamaxusernamelength``, ``ipapwdexpadvnotify``, ``ipasearchrecordslimit``, ``ipasearchtimelimit``, ``ipauserauthtype``, and ``ipausersearchfields`` (https://github.com/ansible-collections/community.general/pull/2116).
- ipa_sudorule - add support for setting sudo runasuser (https://github.com/ansible-collections/community.general/pull/2031).
- ipa_user - fix ``userauthtype`` option to take in list of strings for the multi-select field instead of single string (https://github.com/ansible-collections/community.general/pull/2174).
- ipwcli_dns - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- java_cert - change ``state: present`` to check certificates by hash, not just alias name (https://github.com/ansible/ansible/issues/43249).
- java_keystore - add options ``certificate_path`` and ``private_key_path``, mutually exclusive with ``certificate`` and ``private_key`` respectively, and targetting files on remote hosts rather than their contents on the controller. (https://github.com/ansible-collections/community.general/issues/1669).
- jenkins_job - add a ``validate_certs`` parameter that allows disabling TLS/SSL certificate validation (https://github.com/ansible-collections/community.general/issues/255).
- jira - added ``attach`` operation, which allows a user to attach a file to an issue (https://github.com/ansible-collections/community.general/pull/2192).
- jira - added parameter ``account_id`` for compatibility with recent versions of JIRA (https://github.com/ansible-collections/community.general/issues/818, https://github.com/ansible-collections/community.general/pull/1978).
- jira - revamped the module as a class using ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/2208).
- keycloak_* modules - allow the keycloak modules to use a token for the authentication, the modules can take either a token or the credentials (https://github.com/ansible-collections/community.general/pull/2250).
- keycloak_client - elements of list parameters ``default_roles``, ``redirect_uris``, ``web_origins`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- kibana_plugin - add parameter for passing ``--allow-root`` flag to kibana and kibana-plugin commands (https://github.com/ansible-collections/community.general/pull/2014).
- known_hosts module utils - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- librato_annotation - elements of list parameters ``links`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- linode_v4 - add support for ``private_ip`` option (https://github.com/ansible-collections/community.general/pull/2249).
- linode_v4 - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- lvol - added proper support for ``+-`` options when extending or reducing the logical volume (https://github.com/ansible-collections/community.general/issues/1988).
- lxd_container - ``client_key`` and ``client_cert`` are now of type ``path`` and no longer ``str``. A side effect is that certain expansions are made, like ``~`` is replaced by the user's home directory, and environment variables like ``$HOME`` or ``$TEMP`` are evaluated (https://github.com/ansible-collections/community.general/pull/1741).
- lxd_container - elements of list parameter ``profiles`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- lxd_profile - ``client_key`` and ``client_cert`` are now of type ``path`` and no longer ``str``. A side effect is that certain expansions are made, like ``~`` is replaced by the user's home directory, and environment variables like ``$HOME`` or ``$TEMP`` are evaluated (https://github.com/ansible-collections/community.general/pull/1741).
- lxd_profile - added ``merge_profile`` parameter to merge configurations from the play to an existing profile (https://github.com/ansible-collections/community.general/pull/1813).
- mail - elements of list parameters ``to``, ``cc``, ``bcc``, ``attach``, ``headers`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- manageiq_alert_profiles - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- manageiq_policies - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- manageiq_tags - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- manageiq_tags and manageiq_policies - added new parameter ``resource_id``. This parameter can be used instead of parameter ``resource_name`` (https://github.com/ansible-collections/community.general/pull/719).
- module_helper module utils - ``CmdMixin.run_command()`` now accepts ``dict`` command arguments, providing the parameter and its value (https://github.com/ansible-collections/community.general/pull/1867).
- module_helper module utils - added management of facts and adhoc setting of the initial value for variables (https://github.com/ansible-collections/community.general/pull/2188).
- module_helper module utils - added mechanism to manage variables, providing automatic output of variables, change status and diff information (https://github.com/ansible-collections/community.general/pull/2162).
- na_ontap_gather_facts - elements of list parameters ``gather_subset`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- nexmo - elements of list parameters ``dest`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- nictagadm - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- nmcli - add ability to connect to a Wifi network and also to attach it to a master (bond) (https://github.com/ansible-collections/community.general/pull/2220).
- nmcli - do not set IP configuration on slave connection (https://github.com/ansible-collections/community.general/pull/2223).
- nmcli - don't restrict the ability to manually set the MAC address to the bridge (https://github.com/ansible-collections/community.general/pull/2224).
- npm - add ``no_bin_links`` option (https://github.com/ansible-collections/community.general/issues/2128).
- nsupdate - elements of list parameters ``value`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- oci_vcn - ``api_user_key_file`` is now of type ``path`` and no longer ``str``. A side effect is that certain expansions are made, like ``~`` is replaced by the user's home directory, and environment variables like ``$HOME`` or ``$TEMP`` are evaluated (https://github.com/ansible-collections/community.general/pull/1741).
- omapi_host - elements of list parameters ``statements`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- one_host - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- one_image_info - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- one_vm - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- oneandone_firewall_policy - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- oneandone_load_balancer - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- oneandone_monitoring_policy - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- oneandone_private_network - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- oneandone_server - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- onepassword_info - elements of list parameters ``search_terms`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- oneview_datacenter_info - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- oneview_enclosure_info - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- oneview_ethernet_network_info - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- oneview_network_set_info - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- ovh_ip_failover - removed unreachable code (https://github.com/ansible-collections/community.general/pull/2157).
- packet_device - elements of list parameters ``device_ids``, ``hostnames`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- pagerduty - elements of list parameters ``service`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- pids - new options ``pattern`` and  `ignore_case`` for retrieving PIDs of processes matching a supplied pattern (https://github.com/ansible-collections/community.general/pull/2280).
- plugins/module_utils/oracle/oci_utils.py - elements of list parameter ``key_by`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- profitbricks - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- profitbricks_volume - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- proxmox - added ``purge`` module parameter for use when deleting lxc's with HA options (https://github.com/ansible-collections/community.general/pull/2013).
- proxmox inventory plugin - added ``Constructable`` class to the inventory to provide options ``strict``, ``keyed_groups``, ``groups``, and ``compose`` (https://github.com/ansible-collections/community.general/pull/2180).
- proxmox inventory plugin - added ``proxmox_agent_interfaces`` fact describing network interfaces returned from a QEMU guest agent (https://github.com/ansible-collections/community.general/pull/2148).
- proxmox inventory plugin - added ``tags_parsed`` fact containing tags parsed as a list (https://github.com/ansible-collections/community.general/pull/1949).
- proxmox inventory plugin - allow to select whether ``ansible_host`` should be set for the proxmox nodes (https://github.com/ansible-collections/community.general/pull/2263).
- proxmox_kvm - added new module parameter ``tags`` for use with PVE 6+ (https://github.com/ansible-collections/community.general/pull/2000).
- proxmox_kvm module - actually implemented ``vmid`` and ``status`` return values. Updated documentation to reflect current situation (https://github.com/ansible-collections/community.general/issues/1410, https://github.com/ansible-collections/community.general/pull/1715).
- pubnub_blocks - elements of list parameters ``event_handlers`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- rax - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/2006).
- rax_cdb_user - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/2006).
- rax_scaling_group - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/2006).
- read_csv - refactored read_csv module to use shared csv functions from csv module_utils (https://github.com/ansible-collections/community.general/pull/2037).
- redfish modules - explicitly setting lists' elements to ``str`` (https://github.com/ansible-collections/community.general/pull/1761).
- redfish_* modules, redfish_utils module utils - add support for Redfish session create, delete, and authenticate (https://github.com/ansible-collections/community.general/issues/1975).
- redfish_config - case insensitive search for situations where the hostname/FQDN case on iLO doesn't match variable's case (https://github.com/ansible-collections/community.general/pull/1744).
- redhat_subscription - elements of list parameters ``pool_ids``, ``addons`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- rhevm - removed unreachable code (https://github.com/ansible-collections/community.general/pull/2157).
- rocketchat - elements of list parameters ``attachments`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- scaleway_compute - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- scaleway_lb - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1970).
- sendgrid - elements of list parameters ``to_addresses``, ``cc``, ``bcc``, ``attachments`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- sensu_check - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- sensu_client - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- sensu_handler - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- sl_vm - elements of list parameters ``disks``, ``ssh_keys`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- slack - elements of list parameters ``attachments`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- smartos_image_info - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- snmp_facts - added parameters ``timeout`` and ``retries`` to module (https://github.com/ansible-collections/community.general/issues/980).
- statusio_maintenance - elements of list parameters ``components``, ``containers`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- svr4pkg - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- terraform - add ``plugin_paths`` parameter which allows disabling Terraform from performing plugin discovery and auto-download (https://github.com/ansible-collections/community.general/pull/2308).
- timezone - add Gentoo and Alpine Linux support (https://github.com/ansible-collections/community.general/issues/781).
- twilio - elements of list parameters ``to_numbers`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- udm_dns_zone - elements of list parameters ``nameserver``, ``interfaces``, and ``mx`` are now validated (https://github.com/ansible-collections/community.general/pull/2268).
- vdo - add ``force`` option (https://github.com/ansible-collections/community.general/issues/2101).
- vmadm - elements of list parameters ``disks``, ``nics``, ``resolvers``, ``filesystems`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- webfaction_domain - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- webfaction_site - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/1885).
- xattr - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- xfconf - added option ``disable_facts`` to disable facts and its associated deprecation warning (https://github.com/ansible-collections/community.general/issues/1475).
- xfconf - changed implementation to use ``ModuleHelper`` new features (https://github.com/ansible-collections/community.general/pull/2188).
- xml - elements of list parameters ``add_children``, ``set_children`` are now validated (https://github.com/ansible-collections/community.general/pull/1795).
- yum_versionlock - Do the lock/unlock concurrently to speed up (https://github.com/ansible-collections/community.general/pull/1912).
- zfs_facts - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).
- zpool_facts - minor refactor converting multiple statements to a single list literal (https://github.com/ansible-collections/community.general/pull/2160).

Breaking Changes / Porting Guide
--------------------------------

- If you use Ansible 2.9 and these plugins or modules from this collection, community.general 3.0.0 results in errors when trying to use the DellEMC content by FQCN, like ``community.general.idrac_firmware``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``dellemc.openmanage.idrac_firmware`` for the previous example) and to make sure that you have ``dellemc.openmanage`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 4.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install the ``dellemc.openmanage`` collection if you are using any of these plugins or modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 3.0.0 adds, the collection they point to (such as dellemc.openmanage) must be installed for them to work.
- gitlab_deploy_key - if for an already existing key title a different public key was given as parameter nothing happened, now this changed so that the public key is updated to the new value (https://github.com/ansible-collections/community.general/pull/1661).
- java_keystore - instead of failing, now overwrites keystore if the alias (name) is changed. This was originally the intended behavior, but did not work due to a logic error. Make sure that your playbooks and roles do not depend on the old behavior of failing instead of overwriting (https://github.com/ansible-collections/community.general/issues/1671).
- java_keystore - instead of failing, now overwrites keystore if the passphrase is changed. Make sure that your playbooks and roles do not depend on the old behavior of failing instead of overwriting (https://github.com/ansible-collections/community.general/issues/1671).
- one_image - use pyone instead of python-oca (https://github.com/ansible-collections/community.general/pull/2032).
- utm_proxy_auth_profile - the ``frontend_cookie_secret`` return value now contains a placeholder string instead of the module's ``frontend_cookie_secret`` parameter (https://github.com/ansible-collections/community.general/pull/1736).

Deprecated Features
-------------------

- apt_rpm - deprecated invalid parameter alias ``update-cache``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- composer - deprecated invalid parameter aliases ``working-dir``, ``global-command``, ``prefer-source``, ``prefer-dist``, ``no-dev``, ``no-scripts``, ``no-plugins``, ``optimize-autoloader``, ``classmap-authoritative``, ``apcu-autoloader``, ``ignore-platform-reqs``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- cpanm - parameter ``system_lib`` deprecated in favor of using ``become`` (https://github.com/ansible-collections/community.general/pull/2218).
- github_deploy_key - deprecated invalid parameter alias ``2fa_token``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- grove - the option ``message`` will be removed in community.general 4.0.0. Use the new option ``message_content`` instead (https://github.com/ansible-collections/community.general/pull/1929).
- homebrew - deprecated invalid parameter alias ``update-brew``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- homebrew_cask - deprecated invalid parameter alias ``update-brew``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- opkg - deprecated invalid parameter alias ``update-cache``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- pacman - deprecated invalid parameter alias ``update-cache``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- puppet - deprecated undocumented parameter ``show_diff``, will be removed in 7.0.0. (https://github.com/ansible-collections/community.general/pull/1927).
- runit - unused parameter ``dist`` marked for deprecation (https://github.com/ansible-collections/community.general/pull/1830).
- slackpkg - deprecated invalid parameter alias ``update-cache``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- urpmi - deprecated invalid parameter aliases ``update-cache`` and ``no-recommends``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- xbps - deprecated invalid parameter alias ``update-cache``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
- xfconf - returning output as facts is deprecated, this will be removed in community.general 4.0.0. Please register the task output in a variable and use it instead. You can already switch to the new behavior now by using the new ``disable_facts`` option (https://github.com/ansible-collections/community.general/pull/1747).

Removed Features (previously deprecated)
----------------------------------------

- The ``ome_device_info``, ``idrac_firmware`` and ``idrac_server_config_profile``  modules have now been migrated from community.general to the `dellemc.openmanage <https://galaxy.ansible.com/dellemc/openmanage>`_ Ansible collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.idrac_firmware`` → ``dellemc.openmanage.idrac_firmware``) and make sure to install the dellemc.openmanage collection.
- The deprecated ali_instance_facts module has been removed. Use ali_instance_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated gluster_heal_info module has been removed. Use gluster.gluster.gluster_heal_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated gluster_peer module has been removed. Use gluster.gluster.gluster_peer instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated gluster_volume module has been removed. Use gluster.gluster.gluster_volume instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated helm module has been removed. Use community.kubernetes.helm instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated hpilo_facts module has been removed. Use hpilo_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated idrac_redfish_facts module has been removed. Use idrac_redfish_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated jenkins_job_facts module has been removed. Use jenkins_job_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ldap_attr module has been removed. Use ldap_attrs instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated memset_memstore_facts module has been removed. Use memset_memstore_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated memset_server_facts module has been removed. Use memset_server_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated na_ontap_gather_facts module has been removed. Use netapp.ontap.na_ontap_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated nginx_status_facts module has been removed. Use nginx_status_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated one_image_facts module has been removed. Use one_image_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated onepassword_facts module has been removed. Use onepassword_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_datacenter_facts module has been removed. Use oneview_datacenter_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_enclosure_facts module has been removed. Use oneview_enclosure_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_ethernet_network_facts module has been removed. Use oneview_ethernet_network_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_fc_network_facts module has been removed. Use oneview_fc_network_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_fcoe_network_facts module has been removed. Use oneview_fcoe_network_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_logical_interconnect_group_facts module has been removed. Use oneview_logical_interconnect_group_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_network_set_facts module has been removed. Use oneview_network_set_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated oneview_san_manager_facts module has been removed. Use oneview_san_manager_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated online_server_facts module has been removed. Use online_server_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated online_user_facts module has been removed. Use online_user_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt module has been removed. Use ovirt.ovirt.ovirt_vm instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_affinity_label_facts module has been removed. Use ovirt.ovirt.ovirt_affinity_label_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_api_facts module has been removed. Use ovirt.ovirt.ovirt_api_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_cluster_facts module has been removed. Use ovirt.ovirt.ovirt_cluster_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_datacenter_facts module has been removed. Use ovirt.ovirt.ovirt_datacenter_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_disk_facts module has been removed. Use ovirt.ovirt.ovirt_disk_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_event_facts module has been removed. Use ovirt.ovirt.ovirt_event_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_external_provider_facts module has been removed. Use ovirt.ovirt.ovirt_external_provider_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_group_facts module has been removed. Use ovirt.ovirt.ovirt_group_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_host_facts module has been removed. Use ovirt.ovirt.ovirt_host_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_host_storage_facts module has been removed. Use ovirt.ovirt.ovirt_host_storage_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_network_facts module has been removed. Use ovirt.ovirt.ovirt_network_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_nic_facts module has been removed. Use ovirt.ovirt.ovirt_nic_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_permission_facts module has been removed. Use ovirt.ovirt.ovirt_permission_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_quota_facts module has been removed. Use ovirt.ovirt.ovirt_quota_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_scheduling_policy_facts module has been removed. Use ovirt.ovirt.ovirt_scheduling_policy_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_snapshot_facts module has been removed. Use ovirt.ovirt.ovirt_snapshot_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_storage_domain_facts module has been removed. Use ovirt.ovirt.ovirt_storage_domain_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_storage_template_facts module has been removed. Use ovirt.ovirt.ovirt_storage_template_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_storage_vm_facts module has been removed. Use ovirt.ovirt.ovirt_storage_vm_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_tag_facts module has been removed. Use ovirt.ovirt.ovirt_tag_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_template_facts module has been removed. Use ovirt.ovirt.ovirt_template_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_user_facts module has been removed. Use ovirt.ovirt.ovirt_user_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_vm_facts module has been removed. Use ovirt.ovirt.ovirt_vm_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated ovirt_vmpool_facts module has been removed. Use ovirt.ovirt.ovirt_vmpool_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated purefa_facts module has been removed. Use purestorage.flasharray.purefa_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated purefb_facts module has been removed. Use purestorage.flasharray.purefb_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated python_requirements_facts module has been removed. Use python_requirements_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated redfish_facts module has been removed. Use redfish_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_image_facts module has been removed. Use scaleway_image_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_ip_facts module has been removed. Use scaleway_ip_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_organization_facts module has been removed. Use scaleway_organization_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_security_group_facts module has been removed. Use scaleway_security_group_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_server_facts module has been removed. Use scaleway_server_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_snapshot_facts module has been removed. Use scaleway_snapshot_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated scaleway_volume_facts module has been removed. Use scaleway_volume_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated smartos_image_facts module has been removed. Use smartos_image_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated vertica_facts module has been removed. Use vertica_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The deprecated xenserver_guest_facts module has been removed. Use xenserver_guest_info instead (https://github.com/ansible-collections/community.general/pull/1924).
- The ovirt_facts docs fragment has been removed (https://github.com/ansible-collections/community.general/pull/1924).
- airbrake_deployment - removed deprecated ``token`` parameter. Use ``project_id`` and ``project_key`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- bigpanda - the alias ``message`` has been removed. Use ``deployment_message`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- cisco_spark, cisco_webex - the alias ``message`` has been removed. Use ``msg`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- clc_aa_policy - the ``wait`` parameter has been removed. It did not have any effect (https://github.com/ansible-collections/community.general/pull/1926).
- datadog_monitor - the alias ``message`` has been removed. Use ``notification_message`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- django_manage - the parameter ``liveserver`` has been removed (https://github.com/ansible-collections/community.general/pull/1926).
- idrac_redfish_config - the parameters ``manager_attribute_name`` and ``manager_attribute_value`` have been removed. Use ``manager_attributes`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- iso_extract - the alias ``thirsty`` has been removed. Use ``force`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- ldap_entry - the ``params`` parameter is now completely removed. Using it already triggered an error since community.general 0.1.2 (https://github.com/ansible-collections/community.general/pull/2257).
- pulp_repo - the ``feed_client_cert`` parameter no longer defaults to the value of the ``client_cert`` parameter (https://github.com/ansible-collections/community.general/pull/1926).
- pulp_repo - the ``feed_client_key`` parameter no longer defaults to the value of the ``client_key`` parameter (https://github.com/ansible-collections/community.general/pull/1926).
- pulp_repo - the alias ``ca_cert`` has been removed. Use ``feed_ca_cert`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- rax - unused parameter ``service`` removed (https://github.com/ansible-collections/community.general/pull/2020).
- redfish modules - issuing a data modification command without specifying the ID of the target System, Chassis or Manager resource when there is more than one is no longer allowed. Use the ``resource_id`` option to specify the target ID (https://github.com/ansible-collections/community.general/pull/1926).
- redfish_config - the parameters ``bios_attribute_name`` and ``bios_attribute_value`` have been removed. Use ``bios_attributes`` instead (https://github.com/ansible-collections/community.general/pull/1926).
- syspatch - the ``apply`` parameter has been removed. This is the default mode, so simply removing it will not change the behavior (https://github.com/ansible-collections/community.general/pull/1926).
- xbps - the ``force`` parameter has been removed. It did not have any effect (https://github.com/ansible-collections/community.general/pull/1926).

Security Fixes
--------------

- dnsmadeeasy - mark the ``account_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- gitlab_runner - mark the ``registration_token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- hwc_ecs_instance - mark the ``admin_pass`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- ibm_sa_host - mark the ``iscsi_chap_secret`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- java_cert - remove password from ``run_command`` arguments (https://github.com/ansible-collections/community.general/pull/2008).
- java_keystore - pass secret to keytool through an environment variable to not expose it as a commandline argument (https://github.com/ansible-collections/community.general/issues/1668).
- keycloak_* modules - mark the ``auth_client_secret`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- keycloak_client - mark the ``registration_access_token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- librato_annotation - mark the ``api_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- logentries_msg - mark the ``token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- module_utils/_netapp, na_ontap_gather_facts - enabled ``no_log`` for the options ``api_key`` and ``secret_key`` to prevent accidental disclosure (CVE-2021-20191, https://github.com/ansible-collections/community.general/pull/1725).
- module_utils/identity/keycloak, keycloak_client, keycloak_clienttemplate, keycloak_group - enabled ``no_log`` for the option ``auth_client_secret`` to prevent accidental disclosure (CVE-2021-20191, https://github.com/ansible-collections/community.general/pull/1725).
- nios_nsgroup - mark the ``tsig_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- oneandone_firewall_policy, oneandone_load_balancer, oneandone_monitoring_policy, oneandone_private_network, oneandone_public_ip - mark the ``auth_token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- ovirt - mark the ``instance_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- ovirt - mark the ``instance_rootpw`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- pagerduty_alert - mark the ``api_key``, ``service_key`` and ``integration_key`` parameters as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- pagerduty_change - mark the ``integration_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- pingdom - mark the ``key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- pulp_repo - mark the ``feed_client_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- rax_clb_ssl - mark the ``private_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- redfish_command - mark the ``update_creds.password`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- rollbar_deployment - mark the ``token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- spotinst_aws_elastigroup - mark the ``multai_token`` and ``token`` parameters as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- stackdriver - mark the ``key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- utm_proxy_auth_profile - enabled ``no_log`` for the option ``frontend_cookie_secret`` to prevent accidental disclosure (CVE-2021-20191, https://github.com/ansible-collections/community.general/pull/1725).
- utm_proxy_auth_profile - mark the ``frontend_cookie_secret`` parameter as ``no_log`` to avoid leakage of secrets. This causes the ``utm_proxy_auth_profile`` return value to no longer containing the correct value, but a placeholder (https://github.com/ansible-collections/community.general/pull/1736).

Bugfixes
--------

- Mark various module options with ``no_log=False`` which have a name that potentially could leak secrets, but which do not (https://github.com/ansible-collections/community.general/pull/2001).
- aerospike_migration - fix typo that caused ``migrate_tx_key`` instead of ``migrate_rx_key`` being used (https://github.com/ansible-collections/community.general/pull/1739).
- alternatives - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- beadm - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- bigpanda - actually use the ``deployment_message`` option (https://github.com/ansible-collections/community.general/pull/1928).
- chef_databag lookup plugin - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- cloudforms inventory - fixed issue that non-existing (archived) VMs were synced (https://github.com/ansible-collections/community.general/pull/720).
- cobbler_sync, cobbler_system - fix SSL/TLS certificate check when ``validate_certs`` set to ``false`` (https://github.com/ansible-collections/community.general/pull/1880).
- consul_io inventory script - kv_groups - fix byte chain decoding for Python 3 (https://github.com/ansible-collections/community.general/pull/620).
- cronvar - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- dconf - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- deploy_helper - allow ``state=clean`` to be used without defining a ``release`` (https://github.com/ansible-collections/community.general/issues/1852).
- dimensiondata_network - bug when formatting message, instead of % a simple comma was used (https://github.com/ansible-collections/community.general/pull/2139).
- diy callback plugin - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- elasticsearch_plugin - ``state`` parameter choices must use ``list()`` in python3 (https://github.com/ansible-collections/community.general/pull/1830).
- filesystem - do not fail when ``resizefs=yes`` and ``fstype=xfs`` if there is nothing to do, even if the filesystem is not mounted. This only covers systems supporting access to unmounted XFS filesystems. Others will still fail (https://github.com/ansible-collections/community.general/issues/1457, https://github.com/ansible-collections/community.general/pull/1478).
- filesystem - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- filesystem - remove ``swap`` from list of FS supported by ``resizefs=yes`` (https://github.com/ansible-collections/community.general/issues/790).
- funcd connection plugin - can now load (https://github.com/ansible-collections/community.general/pull/2235).
- git_config - fixed scope ``file`` behaviour and added integraton test for it (https://github.com/ansible-collections/community.general/issues/2117).
- git_config - prevent ``run_command`` from expanding values (https://github.com/ansible-collections/community.general/issues/1776).
- github_repo - PyGithub bug does not allow explicit port in ``base_url``. Specifying port is not required (https://github.com/PyGithub/PyGithub/issues/1913).
- gitlab_runner - parameter ``registration_token`` was required but is used only when ``state`` is ``present`` (https://github.com/ansible-collections/community.general/issues/1714).
- gitlab_user - make updates to the ``isadmin``, ``password`` and ``confirm`` options of an already existing GitLab user work (https://github.com/ansible-collections/community.general/pull/1724).
- haproxy - fix a bug preventing haproxy from properly entering ``DRAIN`` mode (https://github.com/ansible-collections/community.general/issues/1913).
- hiera lookup plugin - converts the return type of plugin to unicode string (https://github.com/ansible-collections/community.general/pull/2329).
- hipchat - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- idrac_redfish_command - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- idrac_redfish_config - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- idrac_redfish_info - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- imc_rest - explicitly logging out instead of registering the call in ```atexit``` (https://github.com/ansible-collections/community.general/issues/1735).
- influxdb_retention_policy - ensure idempotent module execution with different duration and shard duration parameter values (https://github.com/ansible-collections/community.general/issues/2281).
- infoblox inventory script - make sure that the script also works with Ansible 2.9, and returns a more helpful error when community.general is not installed as part of Ansible 2.10/3 (https://github.com/ansible-collections/community.general/pull/1871).
- ini_file - allows an empty string as a value for an option (https://github.com/ansible-collections/community.general/pull/1972).
- interfaces_file - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- ipa_user - allow ``sshpubkey`` to permit multiple word comments (https://github.com/ansible-collections/community.general/pull/2159).
- iso_extract - use proper alias deprecation mechanism for ``thirsty`` alias of ``force`` (https://github.com/ansible-collections/community.general/pull/1830).
- java_cert - allow setting ``state: absent`` by providing just the ``cert_alias`` (https://github.com/ansible/ansible/issues/27982).
- java_cert - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- java_cert - properly handle proxy arguments when the scheme is provided (https://github.com/ansible/ansible/issues/54481).
- java_keystore - improve error handling and return ``cmd`` as documented. Force ``LANG``, ``LC_ALL`` and ``LC_MESSAGES`` environment variables to ``C`` to rely on ``keytool`` output parsing. Fix pylint's ``unused-variable`` and ``no-else-return`` hints (https://github.com/ansible-collections/community.general/pull/2183).
- java_keystore - use tempfile lib to create temporary files with randomized names, and remove the temporary PKCS#12 keystore as well as other materials (https://github.com/ansible-collections/community.general/issues/1667).
- jenkins_plugin - fixes Python 2 compatibility issue (https://github.com/ansible-collections/community.general/pull/2340).
- jira - fixed calling of ``isinstance`` (https://github.com/ansible-collections/community.general/issues/2234).
- jira - fixed error when loading base64-encoded content as attachment (https://github.com/ansible-collections/community.general/pull/2349).
- jira - fixed fields' update in ticket transitions (https://github.com/ansible-collections/community.general/issues/818).
- kibana_plugin - ``state`` parameter choices must use ``list()`` in python3 (https://github.com/ansible-collections/community.general/pull/1830).
- kibana_plugin - added missing parameters to ``remove_plugin`` when using ``state=present force=true``, and fix potential quoting errors when invoking ``kibana`` (https://github.com/ansible-collections/community.general/pull/2143).
- logstash_plugin - wrapped ``dict.keys()`` with ``list`` for use in ``choices`` setting (https://github.com/ansible-collections/community.general/pull/1830).
- lvg - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- lvol - fixed sizing calculation rounding to match the underlying tools (https://github.com/ansible-collections/community.general/issues/1988).
- lvol - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- lxc - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- lxc_container - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- lxc_container - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- lxd_container - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- manageiq_provider - wrapped ``dict.keys()`` with ``list`` for use in ``choices`` setting (https://github.com/ansible-collections/community.general/pull/1970).
- memcached cache plugin - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- meta/runtime.yml - improve deprecation messages (https://github.com/ansible-collections/community.general/pull/1918).
- module_helper module utils - actually ignoring formatting of parameters with value ``None`` (https://github.com/ansible-collections/community.general/pull/2024).
- module_helper module utils - fixed decorator ``cause_changes`` (https://github.com/ansible-collections/community.general/pull/2203).
- module_helper module utils - handling ``ModuleHelperException`` now properly calls ``fail_json()`` (https://github.com/ansible-collections/community.general/pull/2024).
- module_helper module utils - use the command name as-is in ``CmdMixin`` if it fails ``get_bin_path()`` - allowing full path names to be passed (https://github.com/ansible-collections/community.general/pull/2024).
- net_tools.nios.api module_utils - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- nios* modules - fix modules to work with ansible-core 2.11 (https://github.com/ansible-collections/community.general/pull/2057).
- nios_host_record - allow DNS Bypass for views other than default (https://github.com/ansible-collections/community.general/issues/1786).
- nmap inventory plugin - fix cache and constructed group support (https://github.com/ansible-collections/community.general/issues/2242).
- nmcli - add ``method4`` and ``method6`` options (https://github.com/ansible-collections/community.general/pull/1894).
- nmcli - ensure the ``slave-type`` option is passed to ``nmcli`` for type ``bond-slave`` (https://github.com/ansible-collections/community.general/pull/1882).
- nomad_job_info - fix module failure when nomad client returns no jobs (https://github.com/ansible-collections/community.general/pull/1721).
- nsot inventory script - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- oci_vcn - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- oneandone_monitoring_policy - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- packet_volume_attachment - removed extraneous ``print`` call - old debug? (https://github.com/ansible-collections/community.general/pull/1970).
- parted - change the regex that decodes the partition size to better support different formats that parted uses. Change the regex that validates parted's version string (https://github.com/ansible-collections/community.general/pull/1695).
- parted - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- pkgutil - fixed calls to ``list.extend()`` (https://github.com/ansible-collections/community.general/pull/2161).
- proxmox - removed requirement that root password is provided when containter state is ``present`` (https://github.com/ansible-collections/community.general/pull/1999).
- proxmox inventory - added handling of commas in KVM agent configuration string (https://github.com/ansible-collections/community.general/pull/2245).
- proxmox inventory - added handling of extra trailing slashes in the URL (https://github.com/ansible-collections/community.general/pull/1914).
- proxmox inventory - exclude qemu templates from inclusion to the inventory via pools (https://github.com/ansible-collections/community.general/issues/1986, https://github.com/ansible-collections/community.general/pull/1991).
- proxmox inventory plugin - allowed proxomox tag string to contain commas when returned as fact (https://github.com/ansible-collections/community.general/pull/1949).
- proxmox inventory plugin - support network interfaces without IP addresses, multiple network interfaces and unsupported/commanddisabled guest error (https://github.com/ansible-collections/community.general/pull/2263).
- proxmox lxc - only add the features flag when module parameter ``features`` is set. Before an empty string was send to proxmox in case the parameter was not used, which required to use ``root@pam`` for module execution (https://github.com/ansible-collections/community.general/pull/1763).
- proxmox* modules - refactored some parameter validation code into use of ``env_fallback``, ``required_if``, ``required_together``, ``required_one_of`` (https://github.com/ansible-collections/community.general/pull/1765).
- proxmox_kvm - do not add ``args`` if ``proxmox_default_behavior`` is set to no_defaults  (https://github.com/ansible-collections/community.general/issues/1641).
- proxmox_kvm - fix parameter ``vmid`` passed twice to ``exit_json`` while creating a virtual machine without cloning (https://github.com/ansible-collections/community.general/issues/1875, https://github.com/ansible-collections/community.general/pull/1895).
- proxmox_kvm - fix undefined local variable ``status`` when the parameter ``state`` is either ``stopped``, ``started``, ``restarted`` or ``absent`` (https://github.com/ansible-collections/community.general/pull/1847).
- proxmox_kvm - stop implicitly adding ``force`` equal to ``false``. Proxmox API requires not implemented parameters otherwise, and assumes ``force`` to be ``false`` by default anyways (https://github.com/ansible-collections/community.general/pull/1783).
- redfish_command - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- redfish_config - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- redfish_config module, redfish_utils module utils - fix IndexError in ``SetManagerNic`` command (https://github.com/ansible-collections/community.general/issues/1692).
- redfish_info module, redfish_utils module utils - add ``Name`` and ``Id`` properties to output of Redfish inventory commands (https://github.com/ansible-collections/community.general/issues/1650).
- redhat_subscription - ``mutually_exclusive`` was referring to parameter alias instead of name (https://github.com/ansible-collections/community.general/pull/1795).
- redhat_subscription - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- redis cache plugin - wrapped usages of ``keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- riak - parameters ``wait_for_handoffs`` and ``wait_for_ring`` are ``int`` but the default value was ``false`` (https://github.com/ansible-collections/community.general/pull/1830).
- rundeck_acl_policy - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- runit - removed unused code, and passing command as ``list`` instead of ``str`` to ``run_command()`` (https://github.com/ansible-collections/community.general/pull/1830).
- scaleway inventory plugin - fix pagination on scaleway inventory plugin (https://github.com/ansible-collections/community.general/pull/2036).
- selective callback plugin - adjust import so that the plugin also works with ansible-core 2.11 (https://github.com/ansible-collections/community.general/pull/1807).
- selective callback plugin - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- sensu-silence module - fix json parsing of sensu API responses on Python 3.5 (https://github.com/ansible-collections/community.general/pull/1703).
- sensu_check - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- spotinst_aws_elastigroup - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- stacki_host - replaced ``default`` to environment variables with ``fallback`` to them (https://github.com/ansible-collections/community.general/pull/2072).
- statusio_maintenance - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- terraform - fix issue that cause the destroy to fail because from Terraform 0.15 on, the ``terraform destroy -force`` option is replaced with ``terraform destroy -auto-approve`` (https://github.com/ansible-collections/community.general/issues/2247).
- terraform - fix issue that cause the execution fail because from Terraform 0.15 on, the ``-var`` and ``-var-file`` options are no longer available on ``terraform validate`` (https://github.com/ansible-collections/community.general/pull/2246).
- terraform - remove uses of ``use_unsafe_shell=True`` (https://github.com/ansible-collections/community.general/pull/2246).
- timezone - internal refactoring: replaced uses of ``_`` with ``dummy`` (https://github.com/ansible-collections/community.general/pull/1819).
- udm_dns_record - fixed default value of parameter ``data`` to match its type (https://github.com/ansible-collections/community.general/pull/2268).
- utm_utils module_utils - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- vdo - wrapped usages of ``dict.keys()`` in ``list()`` for Python 3 compatibility (https://github.com/ansible-collections/community.general/pull/1861).
- vmadm - correct type of list elements in ``resolvers`` parameter (https://github.com/ansible-collections/community.general/issues/2135).
- xfconf - module was not honoring check mode when ``state`` was ``absent`` (https://github.com/ansible-collections/community.general/pull/2185).
- xfs_quota - the feedback for initializing project quota using xfs_quota binary from ``xfsprogs`` has changed since the version it was written for (https://github.com/ansible-collections/community.general/pull/1596).
- zfs - some ZFS properties could be passed when the dataset/volume did not exist, but would fail if the dataset already existed, even if the property matched what was specified in the ansible task (https://github.com/ansible-collections/community.general/issues/868, https://github.com/ansible-collections/community.general/pull/1833).
- zfs_delegate_admin - the elements of ``users``, ``groups`` and ``permissions`` are now enforced to be strings (https://github.com/ansible-collections/community.general/pull/1766).
- zypper, zypper_repository - respect ``PATH`` environment variable when resolving zypper executable path (https://github.com/ansible-collections/community.general/pull/2094).

New Plugins
-----------

Become
~~~~~~

- sudosu - Run tasks using sudo su -

Callback
~~~~~~~~

- loganalytics - Posts task results to Azure Log Analytics

Filter
~~~~~~

- dict - The ``dict`` function as a filter: converts a list of tuples to a dictionary
- from_csv - Converts CSV text input into list of dicts
- hashids_decode - Decodes a sequence of numbers from a YouTube-like hash
- hashids_encode - Encodes YouTube-like hashes from a sequence of integers
- path_join - Redirects to ansible.builtin.path_join for ansible-base 2.10 or newer, and provides a compatible implementation for Ansible 2.9
- version_sort - Sort a list according to version order instead of pure alphabetical one

Inventory
~~~~~~~~~

- lxd - Returns Ansible inventory from lxd host

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_storage_info - Retrieve information about one or more Proxmox VE storages

opennebula
^^^^^^^^^^

- one_template - Manages OpenNebula templates

Files
~~~~~

- filesize - Create a file with a given size, or resize it if it exists

Identity
~~~~~~~~

ipa
^^^

- ipa_otpconfig - Manage FreeIPA OTP Configuration Settings
- ipa_otptoken - Manage FreeIPA OTPs

keycloak
^^^^^^^^

- keycloak_realm - Allows administration of Keycloak realm via Keycloak API

Monitoring
~~~~~~~~~~

- spectrum_model_attrs - Enforce a model's attributes in CA Spectrum.
- statsd - Send metrics to StatsD

Net Tools
~~~~~~~~~

- gandi_livedns - Manage Gandi LiveDNS records

pritunl
^^^^^^^

- pritunl_org - Manages Pritunl Organizations using the Pritunl API
- pritunl_org_info - List Pritunl Organizations using the Pritunl API
- pritunl_user - Manage Pritunl Users using the Pritunl API
- pritunl_user_info - List Pritunl Users using the Pritunl API

Remote Management
~~~~~~~~~~~~~~~~~

lenovoxcc
^^^^^^^^^

- xcc_redfish_command - Manages Lenovo Out-Of-Band controllers using Redfish APIs

Source Control
~~~~~~~~~~~~~~

github
^^^^^^

- github_repo - Manage your repositories on Github

gitlab
^^^^^^

- gitlab_project_members - Manage project members on GitLab Server

Web Infrastructure
~~~~~~~~~~~~~~~~~~

- jenkins_build - Manage jenkins builds
