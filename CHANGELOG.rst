===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 1.0.0.

v2.0.1
======

Release Summary
---------------

Bugfix and security bugfix (potential information leaks in multiple modules, CVE-2021-20191) release.

Major Changes
-------------

- For community.general 3.0.0, the ``ome_device_info``, ``idrac_firmware`` and ``idrac_server_config_profile`` modules will be moved to the `dellemc.openmanage <https://galaxy.ansible.com/dellemc/openmanage>`_ collection.
  A redirection will be inserted so that users using ansible-base 2.10 or newer do not have to change anything.

  If you use Ansible 2.9 and explicitly use the DellEMC modules mentioned above from this collection, you will need to adjust your playbooks and roles to use FQCNs starting with ``dellemc.openmanage.`` instead of ``community.general.``,
  for example replace ``community.general.ome_device_info`` in a task by ``dellemc.openmanage.ome_device_info``.

  If you use ansible-base and installed ``community.general`` manually and rely on the DellEMC modules mentioned above, you have to make sure to install the ``dellemc.openmanage`` collection as well.
  If you are using FQCNs, for example ``community.general.ome_device_info`` instead of ``ome_device_info``, it will continue working, but we still recommend to adjust the FQCNs as well.

Breaking Changes / Porting Guide
--------------------------------

- utm_proxy_auth_profile - the ``frontend_cookie_secret`` return value now contains a placeholder string instead of the module's ``frontend_cookie_secret`` parameter (https://github.com/ansible-collections/community.general/pull/1736).

Security Fixes
--------------

- dnsmadeeasy - mark the ``account_key`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- gitlab_runner - mark the ``registration_token`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- hwc_ecs_instance - mark the ``admin_pass`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
- ibm_sa_host - mark the ``iscsi_chap_secret`` parameter as ``no_log`` to avoid leakage of secrets (https://github.com/ansible-collections/community.general/pull/1736).
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

- filesystem - do not fail when ``resizefs=yes`` and ``fstype=xfs`` if there is nothing to do, even if the filesystem is not mounted. This only covers systems supporting access to unmounted XFS filesystems. Others will still fail (https://github.com/ansible-collections/community.general/issues/1457, https://github.com/ansible-collections/community.general/pull/1478).
- gitlab_user - make updates to the ``isadmin``, ``password`` and ``confirm`` options of an already existing GitLab user work (https://github.com/ansible-collections/community.general/pull/1724).
- parted - change the regex that decodes the partition size to better support different formats that parted uses. Change the regex that validates parted's version string (https://github.com/ansible-collections/community.general/pull/1695).
- redfish_info module, redfish_utils module utils - add ``Name`` and ``Id`` properties to output of Redfish inventory commands (https://github.com/ansible-collections/community.general/issues/1650).
- sensu-silence module - fix json parsing of sensu API responses on Python 3.5 (https://github.com/ansible-collections/community.general/pull/1703).

v2.0.0
======

Release Summary
---------------

This is release 2.0.0 of ``community.general``, released on 2021-01-28.

Major Changes
-------------

- The community.general collection no longer depends on the ansible.netcommon collection (https://github.com/ansible-collections/community.general/pull/1561).
- The community.general collection no longer depends on the ansible.posix collection (https://github.com/ansible-collections/community.general/pull/1157).

Minor Changes
-------------

- A new filter ``lists_mergeby`` to merge two lists of dictionaries by an attribute.
  For example:

  .. code-block:: yaml

      [{'n': 'n1', 'p1': 'A', 'p2': 'F'},
       {'n': 'n2', 'p2': 'B'}] | community.general.lists_mergeby(
      [{'n': 'n1', 'p1': 'C'},
       {'n': 'n2', 'p2': 'D'},
       {'n': 'n3', 'p3': 'E'}], 'n') | list

  evaluates to

  .. code-block:: yaml

      [{'n': 'n1', 'p1': 'C', 'p2': 'F'},
       {'n': 'n2', 'p2': 'D'},
       {'n': 'n3', 'p3': 'E'}]

  (https://github.com/ansible-collections/community.general/pull/604).
- Add new filter plugin ``dict_kv`` which returns a single key-value pair from two arguments. Useful for generating complex dictionaries without using loops. For example ``'value' | community.general.dict_kv('key'))`` evaluates to ``{'key': 'value'}`` (https://github.com/ansible-collections/community.general/pull/1264).
- The collection dependencies were adjusted so that ``community.kubernetes`` is required to be of version 1.0.0 or newer (https://github.com/ansible-collections/community.general/pull/774).
- The collection is now actively tested in CI with the latest Ansible 2.9 release.
- airbrake_deployment - add ``version`` param; clarified docs on ``revision`` param (https://github.com/ansible-collections/community.general/pull/583).
- apk - added ``no_cache`` option (https://github.com/ansible-collections/community.general/pull/548).
- archive - fix paramater types (https://github.com/ansible-collections/community.general/pull/1039).
- cloudflare_dns - add support for environment variable ``CLOUDFLARE_TOKEN`` (https://github.com/ansible-collections/community.general/pull/1238).
- consul - added support for tcp checks (https://github.com/ansible-collections/community.general/issues/1128).
- datadog - mark ``notification_message`` as ``no_log`` (https://github.com/ansible-collections/community.general/pull/1338).
- datadog_monitor - add ``include_tags`` option (https://github.com/ansible/ansible/issues/57441).
- dconf - update documentation and logic code refactor (https://github.com/ansible-collections/community.general/pull/1585).
- django_manage - renamed parameter ``app_path`` to ``project_path``, adding ``app_path`` and ``chdir`` as aliases (https://github.com/ansible-collections/community.general/issues/1044).
- facter - added option for ``arguments`` (https://github.com/ansible-collections/community.general/pull/768).
- firewalld - the module has been moved to the ``ansible.posix`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/623).
- git_config - added parameter and scope ``file`` allowing user to change parameters in a custom file (https://github.com/ansible-collections/community.general/issues/1021).
- gitlab_project - add parameter ``lfs_enabled`` to specify Git LFS (https://github.com/ansible-collections/community.general/issues/1506).
- gitlab_project - add support for merge_method on projects (https://github.com/ansible/ansible/pull/66813).
- gitlab_project_variable - add support for ``environment_scope`` on projects variables (https://github.com/ansible-collections/community.general/pull/1197).
- gitlab_runner - add ``owned`` option to allow non-admin use (https://github.com/ansible-collections/community.general/pull/1491).
- gitlab_runners inventory plugin - permit environment variable input for ``server_url``, ``api_token`` and ``filter`` options (https://github.com/ansible-collections/community.general/pull/611).
- haproxy - add options to dis/enable health and agent checks.  When health and agent checks are enabled for a service, a disabled service will re-enable itself automatically.  These options also change the state of the agent checks to match the requested state for the backend (https://github.com/ansible-collections/community.general/issues/684).
- homebrew_cask - Homebrew will be deprecating use of ``brew cask`` commands as of version 2.6.0, see https://brew.sh/2020/12/01/homebrew-2.6.0/. Added logic to stop using ``brew cask`` for brew version >= 2.6.0 (https://github.com/ansible-collections/community.general/pull/1481).
- homebrew_tap - provide error message to user when module fails (https://github.com/ansible-collections/community.general/issues/1411).
- influxdb_retention_policy - add shard group duration parameter ``shard_group_duration`` (https://github.com/ansible-collections/community.general/pull/1590).
- infoblox inventory script - use stderr for reporting errors, and allow use of environment for configuration (https://github.com/ansible-collections/community.general/pull/436).
- ini_file - module now can create an empty section (https://github.com/ansible-collections/community.general/issues/479).
- ipa_host - silence warning about non-secret ``random_password`` option not having ``no_log`` set (https://github.com/ansible-collections/community.general/pull/1339).
- ipa_sudorule - added option to use command groups inside sudo rules (https://github.com/ansible-collections/community.general/issues/1555).
- ipa_user - add ``userauthtype`` option (https://github.com/ansible-collections/community.general/pull/951).
- ipa_user - silence warning about non-secret ``krbpasswordexpiration`` and ``update_password`` options not having ``no_log`` set (https://github.com/ansible-collections/community.general/pull/1339).
- iptables_state - use FQCN when calling a module from action plugin (https://github.com/ansible-collections/community.general/pull/967).
- jc - new filter to convert the output of many shell commands and file-types to JSON. Uses the jc library at https://github.com/kellyjonbrazil/jc. For example, filtering the STDOUT output of ``uname -a`` via ``{{ result.stdout | community.general.jc('uname') }}``. Requires Python 3.6+ (https://github.com/ansible-collections/community.general/pull/750).
- jira - added the traceback output to ``fail_json()`` calls deriving from exceptions (https://github.com/ansible-collections/community.general/pull/1536).
- ldap modules - allow to configure referral chasing (https://github.com/ansible-collections/community.general/pull/1618).
- linode inventory plugin - add support for ``keyed_groups``, ``groups``, and ``compose`` options (https://github.com/ansible-collections/community.general/issues/1326).
- linode inventory plugin - add support for ``tags`` option to filter instances by tag (https://github.com/ansible-collections/community.general/issues/1549).
- linode_v4 - added support for Linode StackScript usage when creating instances (https://github.com/ansible-collections/community.general/issues/723).
- log_plays callback - use v2 methods (https://github.com/ansible-collections/community.general/pull/442).
- logstash callback - add ini config (https://github.com/ansible-collections/community.general/pull/610).
- logstash callback - improve logstash message structure, needs to be enabled with the ``format_version`` option (https://github.com/ansible-collections/community.general/pull/641).
- logstash callback - migrate to python3-logstash (https://github.com/ansible-collections/community.general/pull/641).
- lvol - fix idempotency issue when using lvol with ``%VG`` or ``%PVS`` size options and VG is fully allocated (https://github.com/ansible-collections/community.general/pull/229).
- lxd_container - added support of ``--target`` flag for cluster deployments (https://github.com/ansible-collections/community.general/issues/637).
- make - add ``jobs`` parameter to allow specification of number of simultaneous jobs for make to run (https://github.com/ansible-collections/community.general/pull/1550).
- maven_artifact - added ``client_cert`` and ``client_key`` parameters to the maven_artifact module (https://github.com/ansible-collections/community.general/issues/1123).
- module_helper - added ModuleHelper class and a couple of convenience tools for module developers (https://github.com/ansible-collections/community.general/pull/1322).
- module_helper module utils - multiple convenience features added (https://github.com/ansible-collections/community.general/pull/1480).
- nagios - add the ``acknowledge`` action (https://github.com/ansible-collections/community.general/pull/820).
- nagios - add the ``host`` and ``all`` values for the ``forced_check`` action (https://github.com/ansible-collections/community.general/pull/998).
- nagios - add the ``service_check`` action (https://github.com/ansible-collections/community.general/pull/820).
- nagios - rename the ``service_check`` action to ``forced_check`` since we now are able to check both a particular service, all services of a particular host and the host itself (https://github.com/ansible-collections/community.general/pull/998).
- nios modules - clean up module argument spec processing (https://github.com/ansible-collections/community.general/pull/1598).
- nios_network - no longer requires the ansible.netcommon collection (https://github.com/ansible-collections/community.general/pull/1561).
- nmcli - add ``ipv4.routes``,  ``ipv4.route-metric`` and ``ipv4.never-default`` support (https://github.com/ansible-collections/community.general/pull/1260).
- nmcli - add ``zone`` parameter (https://github.com/ansible-collections/community.general/issues/949, https://github.com/ansible-collections/community.general/pull/1426).
- nmcli - add infiniband type support (https://github.com/ansible-collections/community.general/pull/1260).
- nmcli - refactor internal methods for simplicity and enhance reuse to support existing and future connection types (https://github.com/ansible-collections/community.general/pull/1113).
- nmcli - remove Python DBus and GTK Object library dependencies (https://github.com/ansible-collections/community.general/issues/1112).
- nmcli - the ``dns4``, ``dns4_search``, ``dns6``, and ``dns6_search`` arguments are retained internally as lists (https://github.com/ansible-collections/community.general/pull/1113).
- npm - add ``no-optional`` option (https://github.com/ansible-collections/community.general/issues/1421).
- odbc - added a parameter ``commit`` which allows users to disable the explicit commit after the execute call (https://github.com/ansible-collections/community.general/pull/1139).
- openbsd_pkg - added ``snapshot`` option (https://github.com/ansible-collections/community.general/pull/965).
- pacman - improve group expansion speed: query list of pacman groups once (https://github.com/ansible-collections/community.general/pull/349).
- pam_limits - add support for nice and priority limits (https://github.com/ansible/ansible/pull/47680).
- pam_limits - adds check mode (https://github.com/ansible-collections/community.general/issues/827).
- pam_limits - adds diff mode (https://github.com/ansible-collections/community.general/issues/828).
- parted - accept negative numbers in ``part_start`` and ``part_end``
- parted - add ``resize`` option to resize existing partitions (https://github.com/ansible-collections/community.general/pull/773).
- passwordstore lookup plugin - added ``umask`` option to set the desired file permisions on creation. This is done via the ``PASSWORD_STORE_UMASK`` environment variable (https://github.com/ansible-collections/community.general/pull/1156).
- pkgin - add support for installation of full versioned package names (https://github.com/ansible-collections/community.general/pull/1256).
- pkgng - added ``stdout`` and ``stderr`` attributes to the result (https://github.com/ansible-collections/community.general/pull/560).
- pkgng - added support for upgrading all packages using ``name: *, state: latest``, similar to other package providers (https://github.com/ansible-collections/community.general/pull/569).
- pkgng - present the ``ignore_osver`` option to pkg (https://github.com/ansible-collections/community.general/pull/1243).
- pkgutil - module can now accept a list of packages (https://github.com/ansible-collections/community.general/pull/799).
- pkgutil - module has a new option, ``force``, equivalent to the ``-f`` option to the `pkgutil <http://pkgutil.net/>`_ command (https://github.com/ansible-collections/community.general/pull/799).
- pkgutil - module now supports check mode (https://github.com/ansible-collections/community.general/pull/799).
- portage - add ``getbinpkgonly`` option, remove unnecessary note on internal portage behaviour (getbinpkg=yes), and remove the undocumented exclusiveness of the pkg options as portage makes no such restriction (https://github.com/ansible-collections/community.general/pull/1169).
- proxmox - add ``features`` option to LXC (https://github.com/ansible-collections/community.general/issues/816).
- proxmox - add new ``proxmox_default_behavior`` option (https://github.com/ansible-collections/community.general/pull/850).
- proxmox - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox - extract common code and documentation (https://github.com/ansible-collections/community.general/pull/1331).
- proxmox - improve and extract more common documentation (https://github.com/ansible-collections/community.general/pull/1404).
- proxmox inventory plugin - add environment variable passthrough (https://github.com/ansible-collections/community.general/pull/1645).
- proxmox inventory plugin - ignore QEMU templates altogether instead of skipping the creation of the host in the inventory (https://github.com/ansible-collections/community.general/pull/1185).
- proxmox_kvm - add cloud-init support (new options: ``cicustom``, ``cipassword``, ``citype``, ``ciuser``, ``ipconfig``, ``nameservers``, ``searchdomains``, ``sshkeys``) (https://github.com/ansible-collections/community.general/pull/797).
- proxmox_kvm - add new ``proxmox_default_behavior`` option (https://github.com/ansible-collections/community.general/pull/850).
- proxmox_kvm - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox_kvm - improve and extract more common documentation (https://github.com/ansible-collections/community.general/pull/1404).
- proxmox_kvm - improve code readability (https://github.com/ansible-collections/community.general/pull/934).
- proxmox_template - add support for API tokens (https://github.com/ansible-collections/community.general/pull/1206).
- proxmox_template - download proxmox applicance templates (pveam) (https://github.com/ansible-collections/community.general/pull/1046).
- proxmox_template - improve documentation (https://github.com/ansible-collections/community.general/pull/1404).
- pushover - add device parameter (https://github.com/ansible-collections/community.general/pull/802).
- redfish_command - add sub-command for ``EnableContinuousBootOverride`` and ``DisableBootOverride`` to allow setting BootSourceOverrideEnabled Redfish property (https://github.com/ansible-collections/community.general/issues/824).
- redfish_command - support same reset actions on Managers as on Systems (https://github.com/ansible-collections/community.general/issues/901).
- redis cache plugin - add redis sentinel functionality to cache plugin (https://github.com/ansible-collections/community.general/pull/1055).
- redis cache plugin - make the redis cache keyset name configurable (https://github.com/ansible-collections/community.general/pull/1036).
- rhn_register - added ``force`` parameter to allow forced registering (https://github.com/ansible-collections/community.general/issues/1454).
- rundeck_acl_policy - add check for rundeck_acl_policy name parameter (https://github.com/ansible-collections/community.general/pull/612).
- scaleway modules and inventory plugin - update regions and zones to add the new ones (https://github.com/ansible-collections/community.general/pull/1690).
- slack - add support for sending messages built with block kit (https://github.com/ansible-collections/community.general/issues/380).
- slack - add support for updating messages (https://github.com/ansible-collections/community.general/issues/304).
- splunk callback - add an option to allow not to validate certificate from HEC (https://github.com/ansible-collections/community.general/pull/596).
- splunk callback - new parameter ``include_milliseconds`` to add milliseconds to existing timestamp field (https://github.com/ansible-collections/community.general/pull/1462).
- telegram - now can call any methods in Telegram bot API. Previously this module was hardcoded to use "SendMessage" only. Usage of "SendMessage" API method was also librated, and now you can specify any arguments you need, for example, "disable_notificaton" (https://github.com/ansible-collections/community.general/pull/1642).
- terraform - add ``init_reconfigure`` option, which controls the ``-reconfigure`` flag (backend reconfiguration) (https://github.com/ansible-collections/community.general/pull/823).
- xfconf - add arrays support (https://github.com/ansible/ansible/issues/46308).
- xfconf - add support for ``double`` type (https://github.com/ansible-collections/community.general/pull/744).
- xfconf - add support for ``uint`` type (https://github.com/ansible-collections/community.general/pull/696).
- xfconf - removed unnecessary second execution of ``xfconf-query`` (https://github.com/ansible-collections/community.general/pull/1305).
- xml - fixed issue were changed was returned when removing non-existent xpath (https://github.com/ansible-collections/community.general/pull/1007).
- zypper_repository - proper failure when python-xml is missing (https://github.com/ansible-collections/community.general/pull/939).

Breaking Changes / Porting Guide
--------------------------------

- If you use Ansible 2.9 and the Google cloud plugins or modules from this collection, community.general 2.0.0 results in errors when trying to use the Google cloud content by FQCN, like ``community.general.gce_img``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``community.google.gce_img`` for the previous example) and to make sure that you have ``community.google`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install the ``community.google`` or ``google.cloud`` collections if you are using any of the Google cloud plugins or modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (such as community.google) must be installed for them to work.
- If you use Ansible 2.9 and the Kubevirt plugins or modules from this collection, community.general 2.0.0 results in errors when trying to use the Kubevirt content by FQCN, like ``community.general.kubevirt_vm``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``community.kubevirt.kubevirt_vm`` for the previous example) and to make sure that you have ``community.kubevirt`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install the ``community.kubevirt`` collection if you are using any of the Kubevirt plugins or modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (such as community.google) must be installed for them to work.
- If you use Ansible 2.9 and the ``docker`` plugins or modules from this collections, community.general 2.0.0 results in errors when trying to use the docker content by FQCN, like ``community.general.docker_container``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``community.docker.docker_container`` for the previous example) and to make sure that you have ``community.docker`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.docker`` if you are using any of the ``docker`` plugins or modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (community.docker) must be installed for them to work.
- If you use Ansible 2.9 and the ``hashi_vault`` lookup plugin from this collections, community.general 2.0.0 results in errors when trying to use the Hashi Vault content by FQCN, like ``community.general.hashi_vault``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your inventories, variable files, playbooks and roles manually to use the new FQCN (``community.hashi_vault.hashi_vault``) and to make sure that you have ``community.hashi_vault`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.hashi_vault`` if you are using the ``hashi_vault`` plugin.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (community.hashi_vault) must be installed for them to work.
- If you use Ansible 2.9 and the ``hetzner`` modules from this collections, community.general 2.0.0 results in errors when trying to use the hetzner content by FQCN, like ``community.general.hetzner_firewall``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``community.hrobot.firewall`` for the previous example) and to make sure that you have ``community.hrobot`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.hrobot`` if you are using any of the ``hetzner`` modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (community.hrobot) must be installed for them to work.
- If you use Ansible 2.9 and the ``oc`` connection plugin from this collections, community.general 2.0.0 results in errors when trying to use the oc content by FQCN, like ``community.general.oc``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your inventories, variable files, playbooks and roles manually to use the new FQCN (``community.okd.oc``) and to make sure that you have ``community.okd`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.okd`` if you are using the ``oc`` plugin.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (community.okd) must be installed for them to work.
- If you use Ansible 2.9 and the ``postgresql`` modules from this collections, community.general 2.0.0 results in errors when trying to use the postgresql content by FQCN, like ``community.general.postgresql_info``.
  Since Ansible 2.9 is not able to use redirections, you will have to adjust your playbooks and roles manually to use the new FQCNs (``community.postgresql.postgresql_info`` for the previous example) and to make sure that you have ``community.postgresql`` installed.

  If you use ansible-base 2.10 or newer and did not install Ansible 3.0.0, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.postgresql`` if you are using any of the ``postgresql`` modules.
  While ansible-base 2.10 or newer can use the redirects that community.general 2.0.0 adds, the collection they point to (community.postgresql) must be installed for them to work.
- The Google cloud inventory script ``gce.py`` has been migrated to the ``community.google`` collection. Install the ``community.google`` collection in order to continue using it.
- archive - remove path folder itself when ``remove`` paramater is true (https://github.com/ansible-collections/community.general/issues/1041).
- log_plays callback - add missing information to the logs generated by the callback plugin. This changes the log message format (https://github.com/ansible-collections/community.general/pull/442).
- passwordstore lookup plugin - now parsing a password store entry as YAML if possible, skipping the first line (which by convention only contains the password and nothing else). If it cannot be parsed as YAML, the old ``key: value`` parser will be used to process the entry. Can break backwards compatibility if YAML formatted code was parsed in a non-YAML interpreted way, e.g. ``foo: [bar, baz]`` will become a list with two elements in the new version, but a string ``'[bar, baz]'`` in the old (https://github.com/ansible-collections/community.general/issues/1673).
- pkgng - passing ``name: *`` with ``state: absent`` will no longer remove every installed package from the system. It is now a noop. (https://github.com/ansible-collections/community.general/pull/569).
- pkgng - passing ``name: *`` with ``state: latest`` or ``state: present`` will no longer install every package from the configured package repositories. Instead, ``name: *, state: latest`` will upgrade all already-installed packages, and ``name: *, state: present`` is a noop. (https://github.com/ansible-collections/community.general/pull/569).
- proxmox_kvm - recognize ``force=yes`` in conjunction with ``state=absent`` to forcibly remove a running VM (https://github.com/ansible-collections/community.general/pull/849).

Deprecated Features
-------------------

- The ``gluster_heal_info``, ``gluster_peer`` and ``gluster_volume`` modules have migrated to the `gluster.gluster <https://galaxy.ansible.com/gluster/gluster>`_ collection. Ansible-base 2.10.1 adjusted the routing target to point to the modules in that collection, so we will remove these modules in community.general 3.0.0. If you use Ansible 2.9, or use FQCNs ``community.general.gluster_*`` in your playbooks and/or roles, please update them to use the modules from ``gluster.gluster`` instead.
- The ldap_attr module has been deprecated and will be removed in a later release; use ldap_attrs instead.
- django_manage - the parameter ``liveserver`` relates to a no longer maintained third-party module for django. It is now deprecated, and will be remove in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/1154).
- proxmox - the default of the new ``proxmox_default_behavior`` option will change from ``compatibility`` to ``no_defaults`` in community.general 4.0.0. Set the option to an explicit value to avoid a deprecation warning (https://github.com/ansible-collections/community.general/pull/850).
- proxmox_kvm - the default of the new ``proxmox_default_behavior`` option will change from ``compatibility`` to ``no_defaults`` in community.general 4.0.0. Set the option to an explicit value to avoid a deprecation warning (https://github.com/ansible-collections/community.general/pull/850).
- syspatch - deprecate the redundant ``apply`` argument (https://github.com/ansible-collections/community.general/pull/360).
- xbps - the ``force`` option never had any effect. It is now deprecated, and will be removed in 3.0.0 (https://github.com/ansible-collections/community.general/pull/568).

Removed Features (previously deprecated)
----------------------------------------

- All Google cloud modules and plugins have now been migrated away from this collection.
  They can be found in either the `community.google <https://galaxy.ansible.com/community/google>`_ or `google.cloud <https://galaxy.ansible.com/google/cloud>`_ collections.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.gce_img`` → ``community.google.gce_img``) and make sure to install the community.google or google.cloud collections as appropriate.
- All Kubevirt modules and plugins have now been migrated from community.general to the `community.kubevirt <https://galaxy.ansible.com/community/kubevirt>`_ Ansible collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.kubevirt_vm`` → ``community.kubevirt.kubevirt_vm``) and make sure to install the community.kubevirt collection.
- All ``docker`` modules and plugins have been removed from this collection.
  They have been migrated to the `community.docker <https://galaxy.ansible.com/community/docker>`_ collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.docker_container`` → ``community.docker.docker_container``) and make sure to install the community.docker collection.
- All ``hetzner`` modules have been removed from this collection.
  They have been migrated to the `community.hrobot <https://galaxy.ansible.com/community/hrobot>`_ collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.hetzner_firewall`` → ``community.hrobot.firewall``) and make sure to install the community.hrobot collection.
- All ``postgresql`` modules have been removed from this collection.
  They have been migrated to the `community.postgresql <https://galaxy.ansible.com/community/postgresql>`_ collection.

  If you use ansible-base 2.10 or newer, redirections have been provided.
  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.postgresql_info`` → ``community.postgresql.postgresql_info``) and make sure to install the community.postgresql collection.
- The Google cloud inventory script ``gce.py`` has been migrated to the ``community.google`` collection. Install the ``community.google`` collection in order to continue using it.
- The ``hashi_vault`` lookup plugin has been removed from this collection.
  It has been migrated to the `community.hashi_vault <https://galaxy.ansible.com/community/hashi_vault>`_ collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.hashi_vault`` → ``community.hashi_vault.hashi_vault``) and make sure to install the community.hashi_vault collection.
- The ``oc`` connection plugin has been removed from this collection.
  It has been migrated to the `community.okd <https://galaxy.ansible.com/community/okd>`_ collection.
  If you use ansible-base 2.10 or newer, redirections have been provided.

  If you use Ansible 2.9 and installed this collection, you need to adjust the FQCNs (``community.general.oc`` → ``community.okd.oc``) and make sure to install the community.okd collection.
- The deprecated ``actionable`` callback plugin has been removed. Use the ``ansible.builtin.default`` callback plugin with ``display_skipped_hosts = no`` and ``display_ok_hosts = no`` options instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``foreman`` module has been removed. Use the modules from the theforeman.foreman collection instead (https://github.com/ansible-collections/community.general/pull/1347) (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``full_skip`` callback plugin has been removed. Use the ``ansible.builtin.default`` callback plugin with ``display_skipped_hosts = no`` option instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``gcdns_record`` module has been removed. Use ``google.cloud.gcp_dns_resource_record_set`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcdns_zone`` module has been removed. Use ``google.cloud.gcp_dns_managed_zone`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gce`` module has been removed. Use ``google.cloud.gcp_compute_instance`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcp_backend_service`` module has been removed. Use ``google.cloud.gcp_compute_backend_service`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcp_forwarding_rule`` module has been removed. Use ``google.cloud.gcp_compute_forwarding_rule`` or ``google.cloud.gcp_compute_global_forwarding_rule`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcp_healthcheck`` module has been removed. Use ``google.cloud.gcp_compute_health_check``, ``google.cloud.gcp_compute_http_health_check`` or ``google.cloud.gcp_compute_https_health_check`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcp_target_proxy`` module has been removed. Use ``google.cloud.gcp_compute_target_http_proxy`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcp_url_map`` module has been removed. Use ``google.cloud.gcp_compute_url_map`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``gcspanner`` module has been removed. Use ``google.cloud.gcp_spanner_database`` and/or ``google.cloud.gcp_spanner_instance`` instead (https://github.com/ansible-collections/community.general/pull/1370).
- The deprecated ``github_hooks`` module has been removed. Use ``community.general.github_webhook`` and ``community.general.github_webhook_info`` instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``katello`` module has been removed. Use the modules from the theforeman.foreman collection instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_aggregate`` module has been removed. Use netapp.ontap.na_ontap_aggregate instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_license`` module has been removed. Use netapp.ontap.na_ontap_license instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_lun`` module has been removed. Use netapp.ontap.na_ontap_lun instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_qtree`` module has been removed. Use netapp.ontap.na_ontap_qtree instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_svm`` module has been removed. Use netapp.ontap.na_ontap_svm instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_user_role`` module has been removed. Use netapp.ontap.na_ontap_user_role instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_user`` module has been removed. Use netapp.ontap.na_ontap_user instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``na_cdot_volume`` module has been removed. Use netapp.ontap.na_ontap_volume instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``sf_account_manager`` module has been removed. Use netapp.elementsw.na_elementsw_account instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``sf_check_connections`` module has been removed. Use netapp.elementsw.na_elementsw_check_connections instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``sf_snapshot_schedule_manager`` module has been removed. Use netapp.elementsw.na_elementsw_snapshot_schedule instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``sf_volume_access_group_manager`` module has been removed. Use netapp.elementsw.na_elementsw_access_group instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``sf_volume_manager`` module has been removed. Use netapp.elementsw.na_elementsw_volume instead (https://github.com/ansible-collections/community.general/pull/1347).
- The deprecated ``stderr`` callback plugin has been removed. Use the ``ansible.builtin.default`` callback plugin with ``display_failed_stderr = yes`` option instead (https://github.com/ansible-collections/community.general/pull/1347).
- The redirect of the ``conjur_variable`` lookup plugin to ``cyberark.conjur.conjur_variable`` collection was removed (https://github.com/ansible-collections/community.general/pull/1346).
- The redirect of the ``firewalld`` module and the ``firewalld`` module_utils to the ``ansible.posix`` collection was removed (https://github.com/ansible-collections/community.general/pull/1346).
- The redirect to the ``community.digitalocean`` collection was removed for: the ``digital_ocean`` doc fragment, the ``digital_ocean`` module_utils, and the following modules: ``digital_ocean``, ``digital_ocean_account_facts``, ``digital_ocean_account_info``, ``digital_ocean_block_storage``, ``digital_ocean_certificate``, ``digital_ocean_certificate_facts``, ``digital_ocean_certificate_info``, ``digital_ocean_domain``, ``digital_ocean_domain_facts``, ``digital_ocean_domain_info``, ``digital_ocean_droplet``, ``digital_ocean_firewall_facts``, ``digital_ocean_firewall_info``, ``digital_ocean_floating_ip``, ``digital_ocean_floating_ip_facts``, ``digital_ocean_floating_ip_info``, ``digital_ocean_image_facts``, ``digital_ocean_image_info``, ``digital_ocean_load_balancer_facts``, ``digital_ocean_load_balancer_info``, ``digital_ocean_region_facts``, ``digital_ocean_region_info``, ``digital_ocean_size_facts``, ``digital_ocean_size_info``, ``digital_ocean_snapshot_facts``, ``digital_ocean_snapshot_info``, ``digital_ocean_sshkey``, ``digital_ocean_sshkey_facts``, ``digital_ocean_sshkey_info``, ``digital_ocean_tag``, ``digital_ocean_tag_facts``, ``digital_ocean_tag_info``, ``digital_ocean_volume_facts``, ``digital_ocean_volume_info`` (https://github.com/ansible-collections/community.general/pull/1346).
- The redirect to the ``community.mysql`` collection was removed for: the ``mysql`` doc fragment, the ``mysql`` module_utils, and the following modules: ``mysql_db``, ``mysql_info``, ``mysql_query``, ``mysql_replication``, ``mysql_user``, ``mysql_variables`` (https://github.com/ansible-collections/community.general/pull/1346).
- The redirect to the ``community.proxysql`` collection was removed for: the ``proxysql`` doc fragment, and the following modules: ``proxysql_backend_servers``, ``proxysql_global_variables``, ``proxysql_manage_config``, ``proxysql_mysql_users``, ``proxysql_query_rules``, ``proxysql_replication_hostgroups``, ``proxysql_scheduler`` (https://github.com/ansible-collections/community.general/pull/1346).
- The redirect to the ``infinidat.infinibox`` collection was removed for: the ``infinibox`` doc fragment, the ``infinibox`` module_utils, and the following modules: ``infini_export``, ``infini_export_client``, ``infini_fs``, ``infini_host``, ``infini_pool``, ``infini_vol`` (https://github.com/ansible-collections/community.general/pull/1346).
- conjur_variable lookup - has been moved to the ``cyberark.conjur`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/570).
- digital_ocean_* - all DigitalOcean modules have been moved to the ``community.digitalocean`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/622).
- infini_* - all infinidat modules have been moved to the ``infinidat.infinibox`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/607).
- iptables_state - the ``ANSIBLE_ASYNC_DIR`` environment is no longer supported, use the ``async_dir`` shell option instead (https://github.com/ansible-collections/community.general/pull/1371).
- logicmonitor - the module has been removed in 1.0.0 since it is unmaintained and the API used by the module has been turned off in 2017 (https://github.com/ansible-collections/community.general/issues/539, https://github.com/ansible-collections/community.general/pull/541).
- logicmonitor_facts - the module has been removed in 1.0.0 since it is unmaintained and the API used by the module has been turned off in 2017 (https://github.com/ansible-collections/community.general/issues/539, https://github.com/ansible-collections/community.general/pull/541).
- memcached cache plugin - do not import ``CacheModule``s directly. Use ``ansible.plugins.loader.cache_loader`` instead (https://github.com/ansible-collections/community.general/pull/1371).
- mysql_* - all MySQL modules have been moved to the ``community.mysql`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/633).
- proxysql_* - all ProxySQL modules have been moved to the ``community.proxysql`` collection. A redirection is active, which will be removed in version 2.0.0 (https://github.com/ansible-collections/community.general/pull/624).
- redis cache plugin - do not import ``CacheModule``s directly. Use ``ansible.plugins.loader.cache_loader`` instead (https://github.com/ansible-collections/community.general/pull/1371).
- xml - when ``content=attribute``, the ``attribute`` option is ignored (https://github.com/ansible-collections/community.general/pull/1371).

Security Fixes
--------------

- bitbucket_pipeline_variable - **CVE-2021-20180** - hide user sensitive information which are marked as ``secured`` from logging into the console (https://github.com/ansible-collections/community.general/pull/1635).
- snmp_facts - **CVE-2021-20178** - hide user sensitive information such as ``privkey`` and ``authkey`` from logging into the console (https://github.com/ansible-collections/community.general/pull/1621).

Bugfixes
--------

- aerospike_migrations - handle exception when unstable-cluster is returned (https://github.com/ansible-collections/community.general/pull/900).
- aix_filesystem - fix issues with ismount module_util pathing for Ansible 2.9 (https://github.com/ansible-collections/community.general/pull/567).
- apache2_module - amend existing module identifier workaround to also apply to updated Shibboleth modules (https://github.com/ansible-collections/community.general/issues/1379).
- beadm - fixed issue "list object has no attribute split" (https://github.com/ansible-collections/community.general/issues/791).
- bigpanda - removed the dynamic default for ``host`` param (https://github.com/ansible-collections/community.general/pull/1423).
- bitbucket_pipeline_variable - change pagination logic for pipeline variable get API (https://github.com/ansible-collections/community.general/issues/1425).
- capabilities - fix for a newer version of libcap release (https://github.com/ansible-collections/community.general/pull/1061).
- cobbler inventory plugin - ``name`` needed FQCN (https://github.com/ansible-collections/community.general/pull/722).
- cobbler inventory script - add Python 3 support (https://github.com/ansible-collections/community.general/issues/638).
- composer - fix bug in command idempotence with composer v2 (https://github.com/ansible-collections/community.general/issues/1179).
- consul_kv lookup - fix ``ANSIBLE_CONSUL_URL`` environment variable handling (https://github.com/ansible/ansible/issues/51960).
- consul_kv lookup - fix arguments handling (https://github.com/ansible-collections/community.general/pull/303).
- digital_ocean_tag_info - fix crash when querying for an individual tag (https://github.com/ansible-collections/community.general/pull/615).
- django_manage - fix idempotence for ``createcachetable`` (https://github.com/ansible-collections/community.general/pull/699).
- dnsmadeeasy - fix HTTP 400 errors when creating a TXT record (https://github.com/ansible-collections/community.general/issues/1237).
- doas become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_flags`` and ``become_user`` were not explicitly specified (https://github.com/ansible-collections/community.general/pull/704).
- dsv lookup - use correct dict usage (https://github.com/ansible-collections/community.general/pull/743).
- dzdo become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_user`` was not explicitly specified (https://github.com/ansible-collections/community.general/pull/708).
- filesystem - add option ``state`` with default ``present``. When set to ``absent``, filesystem signatures are removed (https://github.com/ansible-collections/community.general/issues/355).
- filesystem - resizefs of xfs filesystems is fixed. Filesystem needs to be mounted.
- flatpak - use of the ``--non-interactive`` argument instead of ``-y`` when possible (https://github.com/ansible-collections/community.general/pull/1246).
- gcp_storage_files lookup plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- gem - fix get_installed_versions: correctly parse ``default`` version (https://github.com/ansible-collections/community.general/pull/783).
- git_config - now raises an error for non-existent repository paths (https://github.com/ansible-collections/community.general/issues/630).
- git_config - using list instead of string as first parameter in the ``run_command()`` call (https://github.com/ansible-collections/community.general/issues/1021).
- gitlab_group - added description parameter to ``createGroup()`` call (https://github.com/ansible-collections/community.general/issues/138).
- gitlab_group_variable - support for GitLab pagination limitation by iterating over GitLab variable pages (https://github.com/ansible-collections/community.general/pull/968).
- gitlab_project_variable - support for GitLab pagination limitation by iterating over GitLab variable pages (https://github.com/ansible-collections/community.general/pull/968).
- gitlab_runner - fix compatiblity with some versions of python-gitlab (https://github.com/ansible-collections/community.general/pull/1491).
- homebrew - add default search path for ``brew`` on Apple silicon hardware (https://github.com/ansible-collections/community.general/pull/1679).
- homebrew - fix package name validation for packages containing hypen ``-`` (https://github.com/ansible-collections/community.general/issues/1037).
- homebrew_cask - add default search path for ``brew`` on Apple silicon hardware (https://github.com/ansible-collections/community.general/pull/1679).
- homebrew_cask - fix package name validation for casks containing hypen ``-`` (https://github.com/ansible-collections/community.general/issues/1037).
- homebrew_cask - fixed issue where a cask with ``@`` in the name is incorrectly reported as invalid (https://github.com/ansible-collections/community.general/issues/733).
- homebrew_tap - add default search path for ``brew`` on Apple silicon hardware (https://github.com/ansible-collections/community.general/pull/1679).
- icinga2_host - fix returning error codes (https://github.com/ansible-collections/community.general/pull/335).
- influxdb - fix usage of path for older version of python-influxdb (https://github.com/ansible-collections/community.general/issues/997).
- ini_file - check for parameter ``value`` if ``state`` is ``present`` and ``allow_no_value`` is ``false`` (https://github.com/ansible-collections/community.general/issues/479).
- interfaces_file - escape regular expression characters in old value (https://github.com/ansible-collections/community.general/issues/777).
- inventory plugins - allow FQCN in ``plugin`` option (https://github.com/ansible-collections/community.general/pull/722).
- ipa_hostgroup - fix an issue with load-balanced ipa and cookie handling with Python 3 (https://github.com/ansible-collections/community.general/issues/737).
- iptables_state - fix race condition between module and its action plugin (https://github.com/ansible-collections/community.general/issues/1136).
- jenkins_plugin - replace MD5 checksum verification with SHA1 due to MD5 being disabled on systems with FIPS-only algorithms enabled (https://github.com/ansible/ansible/issues/34304).
- jira - ``fetch`` and ``search`` no longer indicate that something changed (https://github.com/ansible-collections/community.general/pull/1536).
- jira - ensured parameter ``issue`` is mandatory for operation ``transition`` (https://github.com/ansible-collections/community.general/pull/1536).
- jira - improve error message handling (https://github.com/ansible-collections/community.general/pull/311).
- jira - improve error message handling with multiple errors (https://github.com/ansible-collections/community.general/pull/707).
- jira - module no longer incorrectly reports change for information gathering operations (https://github.com/ansible-collections/community.general/pull/1536).
- jira - provide error message raised from exception (https://github.com/ansible-collections/community.general/issues/1504).
- jira - replaced custom parameter validation with ``required_if`` (https://github.com/ansible-collections/community.general/pull/1536).
- json_query - handle ``AnsibleUnicode`` and ``AnsibleUnsafeText`` (https://github.com/ansible-collections/community.general/issues/320).
- keycloak module_utils - provide meaningful error message to user when auth URL does not start with http or https (https://github.com/ansible-collections/community.general/issues/331).
- launchd - fix for user-level services (https://github.com/ansible-collections/community.general/issues/896).
- launchd - handle deprecated APIs like ``readPlist`` and ``writePlist`` in ``plistlib`` (https://github.com/ansible-collections/community.general/issues/1552).
- ldap modules - add ``sasl_class`` parameter to support passwordless SASL authentication via GSSAPI (kerberos), next to external (https://github.com/ansible-collections/community.general/issues/1523).
- ldap_entry - improvements in documentation, simplifications and replaced code with better ``AnsibleModule`` arguments (https://github.com/ansible-collections/community.general/pull/1516).
- ldap_search - ignore returned referrals (https://github.com/ansible-collections/community.general/issues/1067).
- ldap_search - the module no longer incorrectly reports a change (https://github.com/ansible-collections/community.general/issues/1040).
- linode inventory plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- lldp - use ``get_bin_path`` to locate the ``lldpctl`` executable (https://github.com/ansible-collections/community.general/pull/1643).
- lxc_container - fix the type of the ``container_config`` parameter. It is now processed as a list and not a string (https://github.com/ansible-collections/community.general/pull/216).
- macports - fix failure to install a package whose name is contained within an already installed package's name or variant (https://github.com/ansible-collections/community.general/issues/1307).
- make - fixed ``make`` parameter used for check mode when running a non-GNU ``make`` (https://github.com/ansible-collections/community.general/pull/1574).
- mas - fix ``invalid literal`` when no app can be found (https://github.com/ansible-collections/community.general/pull/1436).
- maven_artifact - handle timestamped snapshot version strings properly (https://github.com/ansible-collections/community.general/issues/709).
- memcached cache plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- monit - add support for all monit service checks (https://github.com/ansible-collections/community.general/pull/1532).
- monit - fix modules ability to determine the current state of the monitored process (https://github.com/ansible-collections/community.general/pull/1107).
- nios_fixed_address, nios_host_record, nios_zone - removed redundant parameter aliases causing warning messages to incorrectly appear in task output (https://github.com/ansible-collections/community.general/issues/852).
- nios_host_record - fix to remove ``aliases`` (CNAMES) for configuration comparison (https://github.com/ansible-collections/community.general/issues/1335).
- nios_member - fix Python 3 compatibility with nios api ``member_normalize`` function (https://github.com/ansible-collections/community.general/issues/1526).
- nmcli - cannot modify ``ifname`` after connection creation (https://github.com/ansible-collections/community.general/issues/1089).
- nmcli - fix idempotetency when modifying an existing connection (https://github.com/ansible-collections/community.general/issues/481).
- nmcli - remove ``bridge-slave`` from list of IP based connections ((https://github.com/ansible-collections/community.general/issues/1500).
- nmcli - set ``C`` locale when executing ``nmcli`` (https://github.com/ansible-collections/community.general/issues/989).
- nmcli - use consistent autoconnect parameters (https://github.com/ansible-collections/community.general/issues/459).
- npm - handle json decode exception while parsing command line output (https://github.com/ansible-collections/community.general/issues/1614).
- oc connection plugin - ``transport`` needed FQCN (https://github.com/ansible-collections/community.general/pull/722).
- omapi_host - fix compatibility with Python 3 (https://github.com/ansible-collections/community.general/issues/787).
- onepassword lookup plugin - updated to support password items, which place the password field directly in the payload's ``details`` attribute (https://github.com/ansible-collections/community.general/pull/1610).
- osx_defaults - fix handling negative integers (https://github.com/ansible-collections/community.general/issues/134).
- osx_defaults - unquote values and unescape double quotes when reading array values (https://github.com/ansible-collections/community.general/pull/358).
- packet_net.py inventory script - fixed failure w.r.t. operating system retrieval by changing array subscription back to attribute access (https://github.com/ansible-collections/community.general/pull/891).
- pacman - treat package names containing .zst as package files during installation (https://www.archlinux.org/news/now-using-zstandard-instead-of-xz-for-package-compression/, https://github.com/ansible-collections/community.general/pull/650).
- pamd - added logic to retain the comment line (https://github.com/ansible-collections/community.general/issues/1394).
- parted - fix creating partition when label is changed (https://github.com/ansible-collections/community.general/issues/522).
- passwordstore lookup plugin - always use explicit ``show`` command to retrieve password. This ensures compatibility with ``gopass`` and avoids problems when password names equal ``pass`` commands (https://github.com/ansible-collections/community.general/pull/1493).
- passwordstore lookup plugin - fix compatibility with gopass when used with ``create=true``. While pass returns 1 on a non-existent password, gopass returns 10, or 11, depending on whether a similar named password was stored. We now just check standard output and that the return code is not zero (https://github.com/ansible-collections/community.general/pull/1589).
- pbrun become plugin - address a bug with the parameters handling that was breaking the plugin in community.general when ``become_user`` was not explicitly specified (https://github.com/ansible-collections/community.general/pull/708).
- pkg5 - now works when Python 3 is used on the target (https://github.com/ansible-collections/community.general/pull/789).
- profitbricks_nic - removed the dynamic default for ``name`` param (https://github.com/ansible-collections/community.general/pull/1423).
- profitbricks_nic - replaced code with ``required`` and ``required_if`` (https://github.com/ansible-collections/community.general/pull/1423).
- proxmox_kvm - defer error-checking for non-existent VMs in order to fix idempotency of tasks using ``state=absent`` and properly recognize a success (https://github.com/ansible-collections/community.general/pull/811).
- proxmox_kvm - fix issue causing linked clones not being create by allowing ``format=unspecified`` (https://github.com/ansible-collections/community.general/issues/1027).
- proxmox_kvm - ignore unsupported ``pool`` parameter on update (https://github.com/ansible-collections/community.general/pull/1258).
- proxmox_kvm - improve handling of long-running tasks by creating a dedicated function (https://github.com/ansible-collections/community.general/pull/831).
- redfish_info module, redfish_utils module utils - correct ``PartNumber`` property name in Redfish ``GetMemoryInventory`` command (https://github.com/ansible-collections/community.general/issues/1483).
- redfish_info, redfish_config, redfish_command - Fix Redfish response payload decode on Python 3.5 (https://github.com/ansible-collections/community.general/issues/686)
- redis - fixes parsing of config values which should not be converted to bytes (https://github.com/ansible-collections/community.general/pull/1079).
- redis cache plugin - make sure that plugin errors out on initialization if the required library is not found, and not on load-time (https://github.com/ansible-collections/community.general/pull/1297).
- rhn_channel - Python 2.7.5 fails if the certificate should not be validated. Fixed this by creating the correct ``ssl_context`` (https://github.com/ansible-collections/community.general/pull/470).
- saltstack connection plugin - use ``hashutil.base64_decodefile`` to ensure that the file checksum is preserved (https://github.com/ansible-collections/community.general/pull/1472).
- selective - mark task failed correctly (https://github.com/ansible/ansible/issues/63767).
- sendgrid - update documentation and warn user about sendgrid Python library version (https://github.com/ansible-collections/community.general/issues/1553).
- slack - avoid trying to update existing message when sending messages that contain the string "ts" (https://github.com/ansible-collections/community.general/issues/1097).
- slack - fix ``xox[abp]`` token identification to capture everything after ``xox[abp]``, as the token is the only thing that should be in this argument (https://github.com/ansible-collections/community.general/issues/862).
- snmp_facts - skip ``EndOfMibView`` values (https://github.com/ansible/ansible/issues/49044).
- solaris_zone - fixed issue trying to configure zone in Python 3 (https://github.com/ansible-collections/community.general/issues/1081).
- syslogger - update ``syslog.openlog`` API call for older Python versions, and improve error handling (https://github.com/ansible-collections/community.general/issues/953).
- syspatch - fix bug where not setting ``apply=true`` would result in error (https://github.com/ansible-collections/community.general/pull/360).
- terraform - fix ``init_reconfigure`` option for proper CLI args (https://github.com/ansible-collections/community.general/pull/1620).
- terraform - fix incorrectly reporting a status of unchanged when number of resources added or destroyed are multiples of 10 (https://github.com/ansible-collections/community.general/issues/561).
- terraform - improve result code checking when executing terraform commands (https://github.com/ansible-collections/community.general/pull/1632).
- timezone - support Python3 on macos/darwin (https://github.com/ansible-collections/community.general/pull/945).
- udm_user - removed the dynamic default for ``userexpiry`` param (https://github.com/ansible-collections/community.general/pull/1423).
- utm_network_interface_address - changed param type from invalid 'boolean' to valid 'bool' (https://github.com/ansible-collections/community.general/pull/1423).
- utm_proxy_exception - four parameters had elements types set as 'string' (invalid), changed to 'str' (https://github.com/ansible-collections/community.general/pull/1399).
- vmadm - simplification of code (https://github.com/ansible-collections/community.general/pull/1415).
- xfconf - add in missing return values that are specified in the documentation (https://github.com/ansible-collections/community.general/issues/1418).
- xfconf - make it work in non-english locales (https://github.com/ansible-collections/community.general/pull/744).
- xfconf - parameter ``value`` no longer required for state ``absent`` (https://github.com/ansible-collections/community.general/issues/1329).
- xfconf - xfconf no longer passing the command args as a string, but rather as a list (https://github.com/ansible-collections/community.general/issues/1328).
- yaml callback plugin - do not remove non-ASCII Unicode characters from multiline string output (https://github.com/ansible-collections/community.general/issues/1519).
- yarn - fixed an index out of range error when no outdated packages where returned by yarn executable (see https://github.com/ansible-collections/community.general/pull/474).
- yarn - fixed an too many values to unpack error when scoped packages are installed (see https://github.com/ansible-collections/community.general/pull/474).
- zfs - fixed ``invalid character '@' in pool name"`` error when working with snapshots on a root zvol (https://github.com/ansible-collections/community.general/issues/932).
- zypper - force ``LANG=C`` to as zypper is looking in XML output where attribute could be translated (https://github.com/ansible-collections/community.general/issues/1175).

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_snap - Snapshot management of instances in Proxmox VE cluster

Identity
~~~~~~~~

ipa
^^^

- ipa_pwpolicy - Manage FreeIPA password policies

Monitoring
~~~~~~~~~~

datadog
^^^^^^^

- datadog_downtime - Manages Datadog downtimes

Packaging
~~~~~~~~~

os
^^

- copr - Manage one of the Copr repositories
- rpm_ostree_pkg - Install or uninstall overlay additional packages
- yum_versionlock - Locks / unlocks a installed package(s) from being updated by yum package manager

System
~~~~~~

- ssh_config - Manage SSH config for user
- sysrc - Manage FreeBSD using sysrc
