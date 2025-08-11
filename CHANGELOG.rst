===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 9.0.0.

v10.7.3
=======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- apache2_module - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- apk - fix check for empty/whitespace-only package names (https://github.com/ansible-collections/community.general/pull/10532).
- apk - handle empty name strings properly (https://github.com/ansible-collections/community.general/issues/10441, https://github.com/ansible-collections/community.general/pull/10442).
- capabilities - using invalid path (symlink/directory/...) returned unrelated and incoherent error messages (https://github.com/ansible-collections/community.general/issues/5649, https://github.com/ansible-collections/community.general/pull/10455).
- cronvar - fix crash on missing ``cron_file`` parent directories (https://github.com/ansible-collections/community.general/issues/10460, https://github.com/ansible-collections/community.general/pull/10461).
- cronvar - handle empty strings on ``value`` properly  (https://github.com/ansible-collections/community.general/issues/10439, https://github.com/ansible-collections/community.general/pull/10445).
- doas become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/issues/9977, https://github.com/ansible-collections/community.general/pull/10537).
- htpasswd - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- irc - pass hostname to ``wrap_socket()`` if ``use_tls=true`` and ``validate_certs=true`` (https://github.com/ansible-collections/community.general/issues/10472, https://github.com/ansible-collections/community.general/pull/10491).
- json_query filter plugin - make compatible with lazy evaluation list and dictionary types of ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10539).
- listen_port_facts - avoid crash when required commands are missing (https://github.com/ansible-collections/community.general/issues/10457, https://github.com/ansible-collections/community.general/pull/10458).
- machinectl become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/pull/10537).
- merge_variables lookup plugin - avoid deprecated functionality from ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10566).
- proxmox inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.proxmox/pull/108, https://github.com/ansible-collections/community.general/pull/10553).
- proxmox_pct_remote connection plugin - avoid deprecated ansible-core paramiko import helper, import paramiko directly instead (https://github.com/ansible-collections/community.proxmox/issues/146, https://github.com/ansible-collections/community.proxmox/pull/151, https://github.com/ansible-collections/community.general/pull/10553).
- syspatch - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- sysrc - use ``shlex`` to improve parsing of ``sysrc -e -a`` output (https://github.com/ansible-collections/community.general/issues/10394, https://github.com/ansible-collections/community.general/pull/10400).
- sysupgrade - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- wsl connection plugin - avoid deprecated ansible-core paramiko import helper, import paramiko directly instead (https://github.com/ansible-collections/community.general/issues/10515, https://github.com/ansible-collections/community.general/pull/10531).
- zypper_repository - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).

v10.7.2
=======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- dependent lookup plugin - avoid deprecated ansible-core 2.19 functionality (https://github.com/ansible-collections/community.general/pull/10359).
- github_release - support multiple types of GitHub tokens; no longer failing when ``ghs_`` token type is provided (https://github.com/ansible-collections/community.general/issues/10338, https://github.com/ansible-collections/community.general/pull/10339).
- icinga2 inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- incus connection plugin - fix error handling to return more useful Ansible errors to the user (https://github.com/ansible-collections/community.general/issues/10344, https://github.com/ansible-collections/community.general/pull/10349).
- linode inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- logstash callback plugin - remove reference to Python 2 library (https://github.com/ansible-collections/community.general/pull/10345).

v10.7.1
=======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- git_config - remove redundant ``required=False`` from ``argument_spec`` (https://github.com/ansible-collections/community.general/pull/10177).
- proxmox_snap - correctly handle proxmox_snap timeout parameter (https://github.com/ansible-collections/community.proxmox/issues/73, https://github.com/ansible-collections/community.proxmox/issues/95, https://github.com/ansible-collections/community.general/pull/10176).

Deprecated Features
-------------------

- yaml callback plugin - the YAML callback plugin was deprecated for removal in community.general 13.0.0. Since it needs to use ansible-core internals since ansible-core 2.19 that are changing a lot, we will remove this plugin already from community.general 12.0.0 to ease the maintenance burden (https://github.com/ansible-collections/community.general/pull/10213).

Bugfixes
--------

- cobbler_system - update minimum version number to avoid wrong comparisons that happen in some cases using LooseVersion class which results in TypeError (https://github.com/ansible-collections/community.general/issues/8506, https://github.com/ansible-collections/community.general/pull/10145, https://github.com/ansible-collections/community.general/pull/10178).
- gitlab_group_access_token, gitlab_project_access_token - fix handling of group and project access tokens for changes in GitLab 17.10 (https://github.com/ansible-collections/community.general/pull/10196).
- keycloak - update more than 10 sub-groups (https://github.com/ansible-collections/community.general/issues/9690, https://github.com/ansible-collections/community.general/pull/9692).
- yaml callback plugin - adjust to latest changes in ansible-core devel (https://github.com/ansible-collections/community.general/pull/10212).
- yaml callback plugin - when using ansible-core 2.19.0b2 or newer, uses a new utility provided by ansible-core. This allows us to remove all hacks and vendored code that was part of the plugin for ansible-core versions with Data Tagging so far (https://github.com/ansible-collections/community.general/pull/10242).
- zypper_repository - make compatible with Python 3.12+ (https://github.com/ansible-collections/community.general/issues/10222, https://github.com/ansible-collections/community.general/pull/10223).
- zypper_repository - use ``metalink`` attribute to identify repositories without ``<url/>`` element (https://github.com/ansible-collections/community.general/issues/10224, https://github.com/ansible-collections/community.general/pull/10225).

v10.7.0
=======

Release Summary
---------------

Bugfix and feature release.
Note that this is the final minor 10.x.0 release.
The next release with new features will be 11.0.0.
From now on, there will only be bugfix 10.7.x releases for the community.general 10 release train.

Minor Changes
-------------

- cobbler inventory plugin - add ``connection_timeout`` option to specify the connection timeout to the cobbler server (https://github.com/ansible-collections/community.general/pull/11063).
- cobbler inventory plugin - add ``facts_level`` option to allow requesting fully rendered variables for Cobbler systems (https://github.com/ansible-collections/community.general/issues/9419, https://github.com/ansible-collections/community.general/pull/9975).
- ini_file - modify an inactive option also when there are spaces in front of the comment symbol (https://github.com/ansible-collections/community.general/pull/10102, https://github.com/ansible-collections/community.general/issues/8539).
- pipx - parameter ``name`` now accepts Python package specifiers (https://github.com/ansible-collections/community.general/issues/7815, https://github.com/ansible-collections/community.general/pull/10031).
- pipx module_utils - filtering application list by name now happens in the modules (https://github.com/ansible-collections/community.general/pull/10031).
- pipx_info - filtering application list by name now happens in the module  (https://github.com/ansible-collections/community.general/pull/10031).

Deprecated Features
-------------------

- The proxmox content (modules and plugins) is being moved to the `new collection community.proxmox <https://github.com/ansible-collections/community.proxmox>`__. In community.general 11.0.0, these modules and plugins will be replaced by deprecated redirections to community.proxmox. You need to explicitly install community.proxmox, for example with ``ansible-galaxy collection install community.proxmox``. We suggest to update your roles and playbooks to use the new FQCNs as soon as possible to avoid getting deprecation messages (https://github.com/ansible-collections/community.general/pull/10109).
- pipx module_utils - function ``make_process_list()`` is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10031).

Bugfixes
--------

- cobbler_system - fix bug with Cobbler >= 3.4.0 caused by giving more than 2 positional arguments to ``CobblerXMLRPCInterface.get_system_handle()`` (https://github.com/ansible-collections/community.general/issues/8506, https://github.com/ansible-collections/community.general/pull/10145).
- kdeconfig - allow option values beginning with a dash (https://github.com/ansible-collections/community.general/issues/10127, https://github.com/ansible-collections/community.general/pull/10128).
- keycloak_user_rolemapping - fix ``--diff`` mode (https://github.com/ansible-collections/community.general/issues/10067, https://github.com/ansible-collections/community.general/pull/10075).
- pickle cache plugin - avoid extra JSON serialization with ansible-core >= 2.19 (https://github.com/ansible-collections/community.general/pull/10136).
- proxmox - fix crash in module when the used on an existing LXC container with ``state=present`` and ``force=true`` (https://github.com/ansible-collections/community.proxmox/pull/91, https://github.com/ansible-collections/community.general/pull/10155).
- rundeck_acl_policy - ensure that project ACLs are sent to the correct endpoint (https://github.com/ansible-collections/community.general/pull/10097).
- sysrc - split the output of ``sysrc -e -a`` on the first ``=`` only (https://github.com/ansible-collections/community.general/issues/10120, https://github.com/ansible-collections/community.general/pull/10121).

New Plugins
-----------

Callback
~~~~~~~~

- community.general.print_task - Prints playbook task snippet to job output.

Filter
~~~~~~

- community.general.to_prettytable - Format a list of dictionaries as an ASCII table.

New Modules
-----------

- community.general.xdg_mime - Set default handler for MIME types, for applications using XDG tools.

v10.6.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- apache2_module - added workaround for new PHP module name, from ``php7_module`` to ``php_module`` (https://github.com/ansible-collections/community.general/pull/9951).
- gitlab_project - add option ``build_timeout`` (https://github.com/ansible-collections/community.general/pull/9960).
- gitlab_project_members - extend choices parameter ``access_level`` by missing upstream valid value ``owner`` (https://github.com/ansible-collections/community.general/pull/9953).
- hpilo_boot - add option to get an idempotent behavior while powering on server, resulting in success instead of failure when using ``state: boot_once`` option (https://github.com/ansible-collections/community.general/pull/9646).
- idrac_redfish_command, idrac_redfish_config, idrac_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- ilo_redfish_command, ilo_redfish_config, ilo_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- keycloak module_utils - user groups can now be referenced by their name, like ``staff``, or their path, like ``/staff/engineering``. The path syntax allows users to reference subgroups, which is not possible otherwise (https://github.com/ansible-collections/community.general/pull/9898).
- keycloak_user module - user groups can now be referenced by their name, like ``staff``, or their path, like ``/staff/engineering``. The path syntax allows users to reference subgroups, which is not possible otherwise (https://github.com/ansible-collections/community.general/pull/9898).
- nmcli - add support for Infiniband MAC setting when ``type`` is ``infiniband`` (https://github.com/ansible-collections/community.general/pull/9962).
- one_vm - update allowed values for ``updateconf`` to include new parameters as per the latest OpenNebula API documentation.
  Added parameters:

  * ``OS``: ``FIRMWARE``;
  * ``CPU_MODEL``: ``MODEL``, ``FEATURES``;
  * ``FEATURES``: ``VIRTIO_BLK_QUEUES``, ``VIRTIO_SCSI_QUEUES``, ``IOTHREADS``;
  * ``GRAPHICS``: ``PORT``, ``COMMAND``;
  * ``VIDEO``: ``ATS``, ``IOMMU``, ``RESOLUTION``, ``TYPE``, ``VRAM``;
  * ``RAW``: ``VALIDATE``;
  * ``BACKUP_CONFIG``: ``FS_FREEZE``, ``KEEP_LAST``, ``BACKUP_VOLATILE``, ``MODE``, ``INCREMENT_MODE``.

  (https://github.com/ansible-collections/community.general/pull/9959).
- proxmox and proxmox_kvm modules - allow uppercase characters in VM/container tags (https://github.com/ansible-collections/community.general/issues/9895, https://github.com/ansible-collections/community.general/pull/10024).
- puppet - improve parameter formatting, no impact to user (https://github.com/ansible-collections/community.general/pull/10014).
- redfish module utils - add ``REDFISH_COMMON_ARGUMENT_SPEC``, a corresponding ``redfish`` docs fragment, and support for its ``validate_certs``, ``ca_path``, and ``ciphers`` options (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- redfish_command, redfish_config, redfish_info - add ``validate_certs`` and ``ca_path`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- rocketchat - fix duplicate JSON conversion for Rocket.Chat < 7.4.0 (https://github.com/ansible-collections/community.general/pull/9965).
- wdc_redfish_command, wdc_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- xcc_redfish_command - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- zypper - adds ``skip_post_errors`` that allows to skip RPM post-install errors (Zypper return code 107) (https://github.com/ansible-collections/community.general/issues/9972).

Deprecated Features
-------------------

- manifold lookup plugin - plugin is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/10028).
- stackpath_compute inventory plugin - plugin is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/10026).

Bugfixes
--------

- dependent look plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- diy callback plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- github_deploy_key - check that key really exists on 422 to avoid masking other errors (https://github.com/ansible-collections/community.general/issues/6718, https://github.com/ansible-collections/community.general/pull/10011).
- hashids and unicode_normalize filter plugins - avoid deprecated ``AnsibleFilterTypeError`` on ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/9992).
- homebrew - emit a useful error message if ``brew info`` reports a package tap is ``null`` (https://github.com/ansible-collections/community.general/pull/10013, https://github.com/ansible-collections/community.general/issues/10012).
- java_cert - the module no longer fails if the optional parameters ``pkcs12_alias`` and ``cert_alias`` are not provided (https://github.com/ansible-collections/community.general/pull/9970).
- keycloak_authentication - fix authentification config duplication for Keycloak < 26.2.0 (https://github.com/ansible-collections/community.general/pull/9987).
- keycloak_client - fix the idempotency regression by normalizing the Keycloak response for ``after_client`` (https://github.com/ansible-collections/community.general/issues/9905, https://github.com/ansible-collections/community.general/pull/9976).
- proxmox inventory plugin - fix ``ansible_host`` staying empty for certain Proxmox nodes (https://github.com/ansible-collections/community.general/issues/5906, https://github.com/ansible-collections/community.general/pull/9952).
- proxmox_disk - fail gracefully if ``storage`` is required but not provided by the user (https://github.com/ansible-collections/community.general/issues/9941, https://github.com/ansible-collections/community.general/pull/9963).
- reveal_ansible_type filter plugin and ansible_type test plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- sysrc - no longer always reporting ``changed=true`` when ``state=absent``. This fixes the method ``exists()`` (https://github.com/ansible-collections/community.general/issues/10004, https://github.com/ansible-collections/community.general/pull/10005).
- yaml callback plugin - use ansible-core internals to avoid breakage with Data Tagging (https://github.com/ansible-collections/community.general/pull/9833).

Known Issues
------------

- reveal_ansible_type filter plugin and ansible_type test plugin - note that ansible-core's Data Tagging feature implements new aliases, such as ``_AnsibleTaggedStr`` for ``str``, ``_AnsibleTaggedInt`` for ``int``, and ``_AnsibleTaggedFloat`` for ``float`` (https://github.com/ansible-collections/community.general/pull/9833).

New Plugins
-----------

Connection
~~~~~~~~~~

- community.general.wsl - Run tasks in WSL distribution using wsl.exe CLI via SSH.

v10.5.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- CmdRunner module utils - the convenience method ``cmd_runner_fmt.as_fixed()`` now accepts multiple arguments as a list (https://github.com/ansible-collections/community.general/pull/9893).
- apache2_mod_proxy - code simplification, no change in functionality (https://github.com/ansible-collections/community.general/pull/9457).
- consul_token - fix idempotency when ``policies`` or ``roles`` are supplied by name (https://github.com/ansible-collections/community.general/issues/9841, https://github.com/ansible-collections/community.general/pull/9845).
- keycloak_realm - remove ID requirement when creating a realm to allow Keycloak generating its own realm ID (https://github.com/ansible-collections/community.general/pull/9768).
- nmap inventory plugin - adds ``dns_servers`` option for specifying DNS servers for name resolution. Accepts hostnames or IP addresses in the same format as the ``exclude`` option (https://github.com/ansible-collections/community.general/pull/9849).
- proxmox_kvm - add missing audio hardware device handling (https://github.com/ansible-collections/community.general/issues/5192, https://github.com/ansible-collections/community.general/pull/9847).
- redfish_config - add command ``SetPowerRestorePolicy`` to set the desired power state of the system when power is restored (https://github.com/ansible-collections/community.general/pull/9837).
- redfish_info - add command ``GetPowerRestorePolicy`` to get the desired power state of the system when power is restored (https://github.com/ansible-collections/community.general/pull/9824).
- rocketchat - option ``is_pre740`` has been added to control the format of the payload. For Rocket.Chat 7.4.0 or newer, it must be set to ``false`` (https://github.com/ansible-collections/community.general/pull/9882).
- slack callback plugin - add ``http_agent`` option to enable the user to set a custom user agent for slack callback plugin (https://github.com/ansible-collections/community.general/issues/9813, https://github.com/ansible-collections/community.general/pull/9836).
- systemd_info - add wildcard expression support in ``unitname`` option (https://github.com/ansible-collections/community.general/pull/9821).
- systemd_info - extend support to timer units (https://github.com/ansible-collections/community.general/pull/9891).
- vmadm - add new options ``flexible_disk_size`` and ``owner_uuid`` (https://github.com/ansible-collections/community.general/pull/9892).

Bugfixes
--------

- cloudlare_dns - handle exhausted response stream in case of HTTP errors to show nice error message to the user (https://github.com/ansible-collections/community.general/issues/9782, https://github.com/ansible-collections/community.general/pull/9818).
- dnf_versionlock - add support for dnf5 (https://github.com/ansible-collections/community.general/issues/9556).
- homebrew - fix crash when package names include tap (https://github.com/ansible-collections/community.general/issues/9777, https://github.com/ansible-collections/community.general/pull/9803).
- homebrew_cask - handle unusual brew version strings (https://github.com/ansible-collections/community.general/issues/8432, https://github.com/ansible-collections/community.general/pull/9881).
- nmcli - enable changing only the order of DNS servers or search suffixes (https://github.com/ansible-collections/community.general/issues/8724, https://github.com/ansible-collections/community.general/pull/9880).
- proxmox - add missing key selection of ``'status'`` key to ``get_lxc_status`` (https://github.com/ansible-collections/community.general/issues/9696, https://github.com/ansible-collections/community.general/pull/9809).
- proxmox_vm_info - the module no longer expects that the key ``template`` exists in a dictionary returned by Proxmox (https://github.com/ansible-collections/community.general/issues/9875, https://github.com/ansible-collections/community.general/pull/9910).
- sudoers - display stdout and stderr raised while failed validation (https://github.com/ansible-collections/community.general/issues/9674, https://github.com/ansible-collections/community.general/pull/9871).

New Modules
-----------

- community.general.pacemaker_resource - Manage pacemaker resources.

v10.4.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- bitwarden lookup plugin - add new option ``collection_name`` to filter results by collection name, and new option ``result_count`` to validate number of results (https://github.com/ansible-collections/community.general/pull/9728).
- incus connection plugin - adds ``remote_user`` and ``incus_become_method`` parameters for allowing a non-root user to connect to an Incus instance (https://github.com/ansible-collections/community.general/pull/9743).
- iocage inventory plugin - the new parameter ``hooks_results`` of the plugin is a list of files inside a jail that provide configuration parameters for the inventory. The inventory plugin reads the files from the jails and put the contents into the items of created variable ``iocage_hooks`` (https://github.com/ansible-collections/community.general/issues/9650, https://github.com/ansible-collections/community.general/pull/9651).
- jira - adds ``client_cert`` and ``client_key`` parameters for supporting client certificate authentification when connecting to Jira (https://github.com/ansible-collections/community.general/pull/9753).
- lldp - adds ``multivalues`` parameter to control behavior when lldpctl outputs an attribute multiple times (https://github.com/ansible-collections/community.general/pull/9657).
- lvg - add ``remove_extra_pvs`` parameter to control if ansible should remove physical volumes which are not in the ``pvs`` parameter (https://github.com/ansible-collections/community.general/pull/9698).
- lxd connection plugin - adds ``remote_user`` and ``lxd_become_method`` parameters for allowing a non-root user to connect to an LXD instance (https://github.com/ansible-collections/community.general/pull/9659).
- nmcli - adds VRF support with new ``type`` value ``vrf`` and new ``slave_type`` value ``vrf`` as well as new ``table`` parameter (https://github.com/ansible-collections/community.general/pull/9658, https://github.com/ansible-collections/community.general/issues/8014).
- proxmox_kvm - allow hibernation and suspending of VMs (https://github.com/ansible-collections/community.general/issues/9620, https://github.com/ansible-collections/community.general/pull/9653).
- redfish_command - add ``PowerFullPowerCycle`` to power command options (https://github.com/ansible-collections/community.general/pull/9729).
- ssh_config - add ``other_options`` option (https://github.com/ansible-collections/community.general/issues/8053, https://github.com/ansible-collections/community.general/pull/9684).
- xen_orchestra inventory plugin - add ``use_vm_uuid`` and ``use_host_uuid`` boolean options to allow switching over to using VM/Xen name labels instead of UUIDs as item names (https://github.com/ansible-collections/community.general/pull/9787).

Deprecated Features
-------------------

- profitbricks - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_datacenter - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_nic - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_volume - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_volume_attachments - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).

Bugfixes
--------

- apache2_mod_proxy - make compatible with Python 3 (https://github.com/ansible-collections/community.general/pull/9762).
- apache2_mod_proxy - passing the cluster's page as referer for the member's pages. This makes the module actually work again for halfway modern Apache versions. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 (https://github.com/ansible-collections/community.general/pull/9762).
- elasticsearch_plugin - fix ``ERROR: D is not a recognized option`` issue when configuring proxy settings (https://github.com/ansible-collections/community.general/pull/9774, https://github.com/ansible-collections/community.general/issues/9773).
- ipa_host - module revoked existing host certificates even if ``user_certificate`` was not given (https://github.com/ansible-collections/community.general/pull/9694).
- keycloak_client - in check mode, detect whether the lists in before client (for example redirect URI list) contain items that the lists in the desired client do not contain (https://github.com/ansible-collections/community.general/pull/9739).
- lldp - fix crash caused by certain lldpctl output where an attribute is defined as branch and leaf (https://github.com/ansible-collections/community.general/pull/9657).
- onepassword_doc lookup plugin - ensure that 1Password Connect support also works for this plugin (https://github.com/ansible-collections/community.general/pull/9625).
- passwordstore lookup plugin - fix subkey creation even when ``create=false`` (https://github.com/ansible-collections/community.general/issues/9105, https://github.com/ansible-collections/community.general/pull/9106).
- proxmox inventory plugin - plugin did not update cache correctly after ``meta: refresh_inventory`` (https://github.com/ansible-collections/community.general/issues/9710, https://github.com/ansible-collections/community.general/pull/9760).
- redhat_subscription - use the "enable_content" option (when available) when
  registering using D-Bus, to ensure that subscription-manager enables the
  content on registration; this is particular important on EL 10+ and Fedora
  41+
  (https://github.com/ansible-collections/community.general/pull/9778).
- zfs - fix handling of multi-line values of user-defined ZFS properties (https://github.com/ansible-collections/community.general/pull/6264).
- zfs_facts - parameter ``type`` now accepts multple values as documented (https://github.com/ansible-collections/community.general/issues/5909, https://github.com/ansible-collections/community.general/pull/9697).

New Modules
-----------

- community.general.systemd_info - Gather C(systemd) unit info.

v10.3.1
=======

Release Summary
---------------

Bugfix release.

Minor Changes
-------------

- onepassword_ssh_key - refactor to move code to lookup class (https://github.com/ansible-collections/community.general/pull/9633).

Bugfixes
--------

- cloudflare_dns - fix crash when deleting a DNS record or when updating a record with ``solo=true`` (https://github.com/ansible-collections/community.general/issues/9652, https://github.com/ansible-collections/community.general/pull/9649).
- homebrew - make package name parsing more resilient (https://github.com/ansible-collections/community.general/pull/9665, https://github.com/ansible-collections/community.general/issues/9641).
- keycloak module utils - replaces missing return in get_role_composites method which caused it to return None instead of composite roles (https://github.com/ansible-collections/community.general/issues/9678, https://github.com/ansible-collections/community.general/pull/9691).
- keycloak_client - fix and improve existing tests. The module showed a diff without actual changes, solved by improving the ``normalise_cr()`` function (https://github.com/ansible-collections/community.general/pull/9644).
- proxmox - adds the ``pubkey`` parameter (back to) the ``update`` state (https://github.com/ansible-collections/community.general/issues/9642, https://github.com/ansible-collections/community.general/pull/9645).
- proxmox - fixes a typo in the translation of the ``pubkey`` parameter to proxmox' ``ssh-public-keys`` (https://github.com/ansible-collections/community.general/issues/9642, https://github.com/ansible-collections/community.general/pull/9645).
- xml - ensure file descriptor is closed (https://github.com/ansible-collections/community.general/pull/9695).

v10.3.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- MH module utils - delegate ``debug`` to the underlying ``AnsibleModule`` instance or issues a warning if an attribute already exists with that name (https://github.com/ansible-collections/community.general/pull/9577).
- apache2_mod_proxy - better handling regexp extraction (https://github.com/ansible-collections/community.general/pull/9609).
- apache2_mod_proxy - change type of ``state`` to a list of strings. No change for the users (https://github.com/ansible-collections/community.general/pull/9600).
- apache2_mod_proxy - improve readability when using results from ``fecth_url()`` (https://github.com/ansible-collections/community.general/pull/9608).
- apache2_mod_proxy - refactor repeated code into method (https://github.com/ansible-collections/community.general/pull/9599).
- apache2_mod_proxy - remove unused parameter and code from ``Balancer`` constructor (https://github.com/ansible-collections/community.general/pull/9614).
- apache2_mod_proxy - simplified and improved string manipulation (https://github.com/ansible-collections/community.general/pull/9614).
- apache2_mod_proxy - use ``deps`` to handle dependencies (https://github.com/ansible-collections/community.general/pull/9612).
- cgroup_memory_recap callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- chroot connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- cloud_init_data_facts - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- cobbler inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- context_demo callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- counter filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- counter_enabled callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- cpanm - enable usage of option ``--with-recommends`` (https://github.com/ansible-collections/community.general/issues/9554, https://github.com/ansible-collections/community.general/pull/9555).
- cpanm - enable usage of option ``--with-suggests`` (https://github.com/ansible-collections/community.general/pull/9555).
- crc32 filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- cronvar - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- crypttab - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- default_without_diff callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dense callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dict filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- dict_kv filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- diy callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- doas become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dzdo become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- elastic callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- from_csv filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- from_ini filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- funcd connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- gitlab_runners inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- groupby_as_dict filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- hashids filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- icinga2 inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- incus connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- iocage connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- iocage inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- iocage inventory plugin - the new parameter ``sudo`` of the plugin lets the command ``iocage list -l`` to run as root on the iocage host. This is needed to get the IPv4 of a running DHCP jail (https://github.com/ansible-collections/community.general/issues/9572, https://github.com/ansible-collections/community.general/pull/9573).
- iptables_state action plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- jabber callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- jail connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- jc filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- jira - transition operation now has ``status_id`` to directly reference wanted transition (https://github.com/ansible-collections/community.general/pull/9602).
- json_query filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- keep_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- keycloak_* modules - ``refresh_token`` parameter added. When multiple authentication parameters are provided (``token``, ``refresh_token``, and ``auth_username``/``auth_password``), modules will now automatically retry requests upon authentication errors (401), using in order the token, refresh token, and username/password (https://github.com/ansible-collections/community.general/pull/9494).
- known_hosts - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- ksu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- linode inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lists filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- lists_mergeby filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- log_plays callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- loganalytics callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- logdna callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- logentries callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- logstash callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- lxc connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lxd connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lxd inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- machinectl become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- mail callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- memcached cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- nmap inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- nmcli - add a option ``fail_over_mac`` (https://github.com/ansible-collections/community.general/issues/9570, https://github.com/ansible-collections/community.general/pull/9571).
- nrdp callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- null callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- one_template - adds ``filter`` option for retrieving templates which are not owned by the user (https://github.com/ansible-collections/community.general/pull/9547, https://github.com/ansible-collections/community.general/issues/9278).
- online inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- opennebula inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- opentelemetry callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- parted - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- pbrun become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pfexec become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pickle cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pmrun become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- proxmox - refactors the proxmox module (https://github.com/ansible-collections/community.general/pull/9225).
- proxmox inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- proxmox_pct_remote connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- proxmox_template - add support for checksum validation with new options ``checksum_algorithm`` and ``checksum`` (https://github.com/ansible-collections/community.general/issues/9553, https://github.com/ansible-collections/community.general/pull/9601).
- pulp_repo - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- qubes connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- random_mac filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- redfish_info - add command ``GetAccountServiceConfig`` to get full information about AccountService configuration (https://github.com/ansible-collections/community.general/pull/9403).
- redhat_subscription - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- redis cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- remove_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- replace_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- reveal_ansible_type filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- run0 become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- saltstack connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- say callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- scaleway inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- selective callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- sesu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- shutdown action plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- slack callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- snap - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9598).
- snap_alias - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9598).
- solaris_zone - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- sorcery - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- splunk callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- stackpath_compute inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- sudosu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- sumologic callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- syslog_json callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- time filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- timestamp callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- timezone - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- to_ini filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- ufw - add support for ``vrrp`` protocol (https://github.com/ansible-collections/community.general/issues/9562, https://github.com/ansible-collections/community.general/pull/9582).
- unicode_normalize filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- unixy callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- version_sort filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- virtualbox inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- xen_orchestra inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- yaml cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- yaml callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- zone connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).

Deprecated Features
-------------------

- MH module utils - attribute ``debug`` definition in subclasses of MH is now deprecated, as that name will become a delegation to ``AnsibleModule`` in community.general 12.0.0, and any such attribute will be overridden by that delegation in that version (https://github.com/ansible-collections/community.general/pull/9577).
- proxmox - removes default value ``false`` of ``update`` parameter. This will be changed to a default of ``true`` in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9225).

Security Fixes
--------------

- keycloak_client - Sanitize ``saml.encryption.private.key`` so it does not show in the logs (https://github.com/ansible-collections/community.general/pull/9621).

Bugfixes
--------

- homebrew - fix incorrect handling of homebrew modules when a tap is requested (https://github.com/ansible-collections/community.general/pull/9546, https://github.com/ansible-collections/community.general/issues/9533).
- iocage inventory plugin - the plugin parses the IP4 tab of the jails list and put the elements into the new variable ``iocage_ip4_dict``. In multiple interface format the variable ``iocage_ip4`` keeps the comma-separated list of IP4 (https://github.com/ansible-collections/community.general/issues/9538).
- pipx - honor option ``global`` when ``state=latest`` (https://github.com/ansible-collections/community.general/pull/9623).
- proxmox - fixes idempotency of template conversions (https://github.com/ansible-collections/community.general/pull/9225, https://github.com/ansible-collections/community.general/issues/8811).
- proxmox - fixes incorrect parsing for bind-only mounts (https://github.com/ansible-collections/community.general/pull/9225, https://github.com/ansible-collections/community.general/issues/8982).
- proxmox - fixes issues with disk_volume variable (https://github.com/ansible-collections/community.general/pull/9225, https://github.com/ansible-collections/community.general/issues/9065).
- proxmox module utils - fixes ignoring of ``choose_first_if_multiple`` argument in ``get_vmid`` (https://github.com/ansible-collections/community.general/pull/9225).
- redhat_subscription - do not try to unsubscribe (i.e. remove subscriptions)
  when unregistering a system: newer versions of subscription-manager, as
  available in EL 10 and Fedora 41+, do not support entitlements anymore, and
  thus unsubscribing will fail
  (https://github.com/ansible-collections/community.general/pull/9578).

New Plugins
-----------

Connection
~~~~~~~~~~

- community.general.proxmox_pct_remote - Run tasks in Proxmox LXC container instances using pct CLI via SSH.

Filter
~~~~~~

- community.general.json_diff - Create a JSON patch by comparing two JSON files.
- community.general.json_patch - Apply a JSON-Patch (RFC 6902) operation to an object.
- community.general.json_patch_recipe - Apply JSON-Patch (RFC 6902) operations to an object.

Lookup
~~~~~~

- community.general.onepassword_ssh_key - Fetch SSH keys stored in 1Password.

New Modules
-----------

- community.general.proxmox_backup_info - Retrieve information on Proxmox scheduled backups.

v10.2.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- bitwarden lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- cgroup_memory_recap callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- chef_databag lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- chroot connection plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- chroot connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- cobbler inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- cobbler inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- collection_version lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- consul_kv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- context_demo callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- counter_enabled callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- credstash lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- cyberarkpassword lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- cyberarkpassword lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- dense callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- dependent lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- dig lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- dig lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- diy callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- dnstxt lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- dnstxt lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- doas become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- dsv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- dzdo become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- elastic callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- etcd lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- etcd3 lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- etcd3 lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- filetree lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- from_csv filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- from_ini filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- funcd connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- github_app_access_token lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- gitlab_instance_variable - add support for ``raw`` variables suboption (https://github.com/ansible-collections/community.general/pull/9425).
- gitlab_runners inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- gitlab_runners inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- hiera lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- icinga2 inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- incus connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- iocage connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- iocage inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- iptables_state action plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9318).
- jabber callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- jail connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- keycloak - add an action group for Keycloak modules to allow ``module_defaults`` to be set for Keycloak tasks (https://github.com/ansible-collections/community.general/pull/9284).
- keyring lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- ksu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- lastpass lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- linode inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- lmdb_kv lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- lmdb_kv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- locale_gen - invert the logic to determine ``ubuntu_mode``, making it look first for ``/etc/locale.gen`` (set ``ubuntu_mode`` to ``False``) and only then looking for ``/var/lib/locales/supported.d/`` (set ``ubuntu_mode`` to ``True``) (https://github.com/ansible-collections/community.general/pull/9238, https://github.com/ansible-collections/community.general/issues/9131, https://github.com/ansible-collections/community.general/issues/8487).
- locale_gen - new return value ``mechanism`` to better express the semantics of the ``ubuntu_mode``, with the possible values being either ``glibc`` (``ubuntu_mode=False``) or ``ubuntu_legacy`` (``ubuntu_mode=True``) (https://github.com/ansible-collections/community.general/pull/9238).
- log_plays callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- loganalytics callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- logdna callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- logentries callback plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- logentries callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- lxc connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- lxd connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- lxd inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- lxd inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- machinectl become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- mail callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- manageiq_alert_profiles - improve handling of parameter requirements (https://github.com/ansible-collections/community.general/pull/9449).
- manifold lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- manifold lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- memcached cache plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9320).
- merge_variables lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- nmap inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- nmap inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- nrdp callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- onepassword lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- onepassword lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- onepassword_doc lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- online inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- opennebula inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- opennebula inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- opentelemetry callback plugin - remove code handling Python versions prior to 3.7 (https://github.com/ansible-collections/community.general/pull/9482).
- opentelemetry callback plugin - remove code handling Python versions prior to 3.7 (https://github.com/ansible-collections/community.general/pull/9503).
- opentelemetry callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- pacemaker_cluster - remove unused code (https://github.com/ansible-collections/community.general/pull/9471).
- pacemaker_cluster - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/9471).
- passwordstore lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- pbrun become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- pfexec become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- pmrun become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- proxmox inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- proxmox inventory plugin - strip whitespace from ``user``, ``token_id``, and ``token_secret`` (https://github.com/ansible-collections/community.general/issues/9227, https://github.com/ansible-collections/community.general/pull/9228/).
- proxmox inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- proxmox module utils - add method ``api_task_complete`` that can wait for task completion and return error message (https://github.com/ansible-collections/community.general/pull/9256).
- proxmox_backup - refactor permission checking to improve code readability and maintainability (https://github.com/ansible-collections/community.general/pull/9239).
- qubes connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- random_pet lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- redis cache plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- redis cache plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9320).
- redis lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- revbitspss lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- saltstack connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- say callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- scaleway inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- scaleway inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- selective callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- sesu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- shelvefile lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- shutdown action plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- shutdown action plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9318).
- slack callback plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- slack callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- splunk callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- stackpath_compute inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- sudosu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- timestamp callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- to_ini filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- tss lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- tss lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- unixy callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- virtualbox inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- virtualbox inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- xbps - add ``root`` and ``repository`` options to enable bootstrapping new void installations (https://github.com/ansible-collections/community.general/pull/9174).
- xen_orchestra inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- xfconf - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9226).
- xfconf_info - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9226).
- yaml callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- zone connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- zypper - add ``quiet`` option (https://github.com/ansible-collections/community.general/pull/9270).
- zypper - add ``simple_errors`` option (https://github.com/ansible-collections/community.general/pull/9270).

Deprecated Features
-------------------

- atomic_container - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- atomic_host - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- atomic_image - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- facter - module is deprecated and will be removed in community.general 12.0.0, use ``community.general.facter_facts`` instead (https://github.com/ansible-collections/community.general/pull/9451).
- locale_gen - ``ubuntu_mode=True``, or ``mechanism=ubuntu_legacy`` is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9238).
- pure module utils - the module utils is deprecated and will be removed from community.general 12.0.0. The modules using this were removed in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/9432).
- purestorage doc fragments - the doc fragment is deprecated and will be removed from community.general 12.0.0. The modules using this were removed in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/9432).
- sensu_check - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_client - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_handler - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_silence - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_subscription - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- slack - the default value ``auto`` of the ``prepend_hash`` option is deprecated and will change to ``never`` in community.general 12.0.0 (https://github.com/ansible-collections/community.general/pull/9443).
- yaml callback plugin - deprecate plugin in favor of ``result_format=yaml`` in plugin ``ansible.bulitin.default`` (https://github.com/ansible-collections/community.general/pull/9456).

Security Fixes
--------------

- keycloak_authentication - API calls did not properly set the ``priority`` during update resulting in incorrectly sorted authentication flows. This apparently only affects Keycloak 25 or newer (https://github.com/ansible-collections/community.general/pull/9263).

Bugfixes
--------

- dig lookup plugin - correctly handle ``NoNameserver`` exception (https://github.com/ansible-collections/community.general/pull/9363, https://github.com/ansible-collections/community.general/issues/9362).
- homebrew - fix incorrect handling of aliased homebrew modules when the alias is requested (https://github.com/ansible-collections/community.general/pull/9255, https://github.com/ansible-collections/community.general/issues/9240).
- htpasswd - report changes when file permissions are adjusted (https://github.com/ansible-collections/community.general/issues/9485, https://github.com/ansible-collections/community.general/pull/9490).
- proxmox_backup - fix incorrect key lookup in vmid permission check (https://github.com/ansible-collections/community.general/pull/9223).
- proxmox_disk - fix async method and make ``resize_disk`` method handle errors correctly (https://github.com/ansible-collections/community.general/pull/9256).
- proxmox_template - fix the wrong path called on ``proxmox_template.task_status`` (https://github.com/ansible-collections/community.general/issues/9276, https://github.com/ansible-collections/community.general/pull/9277).
- qubes connection plugin - fix the printing of debug information (https://github.com/ansible-collections/community.general/pull/9334).
- redfish_utils module utils - Fix ``VerifyBiosAttributes`` command on multi system resource nodes (https://github.com/ansible-collections/community.general/pull/9234).

New Plugins
-----------

Inventory
~~~~~~~~~

- community.general.iocage - iocage inventory source.

New Modules
-----------

- community.general.android_sdk - Manages Android SDK packages.
- community.general.ldap_inc - Use the Modify-Increment LDAP V3 feature to increment an attribute value.
- community.general.systemd_creds_decrypt - C(systemd)'s C(systemd-creds decrypt) plugin.
- community.general.systemd_creds_encrypt - C(systemd)'s C(systemd-creds encrypt) plugin.

v10.1.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- alternatives - add ``family`` parameter that allows to utilize the ``--family`` option available in RedHat version of update-alternatives (https://github.com/ansible-collections/community.general/issues/5060, https://github.com/ansible-collections/community.general/pull/9096).
- cloudflare_dns - add support for ``comment`` and ``tags`` (https://github.com/ansible-collections/community.general/pull/9132).
- deps module utils - add ``deps.clear()`` to clear out previously declared dependencies (https://github.com/ansible-collections/community.general/pull/9179).
- homebrew - greatly speed up module when multiple packages are passed in the ``name`` option (https://github.com/ansible-collections/community.general/pull/9181).
- homebrew - remove duplicated package name validation (https://github.com/ansible-collections/community.general/pull/9076).
- iso_extract - adds ``password`` parameter that is passed to 7z (https://github.com/ansible-collections/community.general/pull/9159).
- launchd - add ``plist`` option for services such as sshd, where the plist filename doesn't match the service name (https://github.com/ansible-collections/community.general/pull/9102).
- nmcli - add ``sriov`` parameter that enables support for SR-IOV settings (https://github.com/ansible-collections/community.general/pull/9168).
- pipx - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9180).
- pipx_info - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9180).
- proxmox_template - add server side artifact fetching support (https://github.com/ansible-collections/community.general/pull/9113).
- redfish_command - add ``update_custom_oem_header``, ``update_custom_oem_params``, and ``update_custom_oem_mime_type`` options (https://github.com/ansible-collections/community.general/pull/9123).
- redfish_utils module utils - remove redundant code (https://github.com/ansible-collections/community.general/pull/9190).
- rpm_ostree_pkg - added the options ``apply_live`` (https://github.com/ansible-collections/community.general/pull/9167).
- rpm_ostree_pkg - added the return value ``needs_reboot`` (https://github.com/ansible-collections/community.general/pull/9167).
- scaleway_lb - minor simplification in the code (https://github.com/ansible-collections/community.general/pull/9189).
- ssh_config - add ``dynamicforward`` option (https://github.com/ansible-collections/community.general/pull/9192).

Deprecated Features
-------------------

- opkg - deprecate value ``""`` for parameter ``force`` (https://github.com/ansible-collections/community.general/pull/9172).
- redfish_utils module utils - deprecate method ``RedfishUtils._init_session()`` (https://github.com/ansible-collections/community.general/pull/9190).

Bugfixes
--------

- dnf_config_manager - fix hanging when prompting to import GPG keys (https://github.com/ansible-collections/community.general/pull/9124, https://github.com/ansible-collections/community.general/issues/8830).
- dnf_config_manager - forces locale to ``C`` before module starts. If the locale was set to non-English, the output of the ``dnf config-manager`` could not be parsed (https://github.com/ansible-collections/community.general/pull/9157, https://github.com/ansible-collections/community.general/issues/9046).
- flatpak - force the locale language to ``C`` when running the flatpak command (https://github.com/ansible-collections/community.general/pull/9187, https://github.com/ansible-collections/community.general/issues/8883).
- gio_mime - fix command line when determining version of ``gio`` (https://github.com/ansible-collections/community.general/pull/9171, https://github.com/ansible-collections/community.general/issues/9158).
- github_key - in check mode, a faulty call to ```datetime.strftime(...)``` was being made which generated an exception (https://github.com/ansible-collections/community.general/issues/9185).
- homebrew_cask - allow ``+`` symbol in Homebrew cask name validation regex (https://github.com/ansible-collections/community.general/pull/9128).
- keycloak_clientscope_type - sort the default and optional clientscope lists to improve the diff (https://github.com/ansible-collections/community.general/pull/9202).
- slack - fail if Slack API response is not OK with error message (https://github.com/ansible-collections/community.general/pull/9198).

New Plugins
-----------

Filter
~~~~~~

- community.general.accumulate - Produce a list of accumulated sums of the input list contents.

New Modules
-----------

- community.general.decompress - Decompresses compressed files.
- community.general.proxmox_backup - Start a VM backup in Proxmox VE cluster.

v10.0.1
=======

Release Summary
---------------

Bugfix release for inclusion in Ansible 11.0.0rc1.

Bugfixes
--------

- keycloak_client - fix diff by removing code that turns the attributes dict which contains additional settings into a list (https://github.com/ansible-collections/community.general/pull/9077).
- keycloak_clientscope - fix diff and ``end_state`` by removing the code that turns the attributes dict, which contains additional config items, into a list (https://github.com/ansible-collections/community.general/pull/9082).
- redfish_utils module utils - remove undocumented default applytime (https://github.com/ansible-collections/community.general/pull/9114).

v10.0.0
=======

Release Summary
---------------

This is release 10.0.0 of ``community.general``, released on 2024-11-04.

Minor Changes
-------------

- CmdRunner module util - argument formats can be specified as plain functions without calling ``cmd_runner_fmt.as_func()`` (https://github.com/ansible-collections/community.general/pull/8479).
- CmdRunner module utils - the parameter ``force_lang`` now supports the special value ``auto`` which will automatically try and determine the best parsable locale in the system (https://github.com/ansible-collections/community.general/pull/8517).
- MH module utils - add parameter ``when`` to ``cause_changes`` decorator (https://github.com/ansible-collections/community.general/pull/8766).
- MH module utils - minor refactor in decorators (https://github.com/ansible-collections/community.general/pull/8766).
- alternatives - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- ansible_galaxy_install - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9060).
- ansible_galaxy_install - add upgrade feature (https://github.com/ansible-collections/community.general/pull/8431, https://github.com/ansible-collections/community.general/issues/8351).
- ansible_galaxy_install - minor refactor in the module (https://github.com/ansible-collections/community.general/pull/8413).
- apache2_mod_proxy - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- apache2_mod_proxy - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- cargo - add option ``directory``, which allows source directory to be specified (https://github.com/ansible-collections/community.general/pull/8480).
- cgroup_memory_recap, hipchat, jabber, log_plays, loganalytics, logentries, logstash, slack, splunk, sumologic, syslog_json callback plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8628).
- chef_databag, consul_kv, cyberarkpassword, dsv, etcd, filetree, hiera, onepassword, onepassword_doc, onepassword_raw, passwordstore, redis, shelvefile, tss lookup plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8626).
- chroot, funcd, incus, iocage, jail, lxc, lxd, qubes, zone connection plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8627).
- cmd_runner module utils - add decorator ``cmd_runner_fmt.stack`` (https://github.com/ansible-collections/community.general/pull/8415).
- cmd_runner module utils - refactor argument formatting code to its own Python module (https://github.com/ansible-collections/community.general/pull/8964).
- cmd_runner_fmt module utils - simplify implementation of ``cmd_runner_fmt.as_bool_not()`` (https://github.com/ansible-collections/community.general/pull/8512).
- cobbler, linode, lxd, nmap, online, scaleway, stackpath_compute, virtualbox inventory plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8625).
- consul_acl - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- consul_kv - add argument for the datacenter option on Consul API (https://github.com/ansible-collections/community.general/pull/9026).
- copr - Added ``includepkgs`` and ``excludepkgs`` parameters to limit the list of packages fetched or excluded from the repository(https://github.com/ansible-collections/community.general/pull/8779).
- cpanm - add return value ``cpanm_version`` (https://github.com/ansible-collections/community.general/pull/9061).
- credstash lookup plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- csv module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- deco MH module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- dig lookup plugin - add ``port`` option to specify DNS server port (https://github.com/ansible-collections/community.general/pull/8966).
- django module utils - always retrieve version (https://github.com/ansible-collections/community.general/pull/9063).
- django_check - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9063).
- django_command - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9063).
- django_createcachetable - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9063).
- doas, dzdo, ksu, machinectl, pbrun, pfexec, pmrun, sesu, sudosu become plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8623).
- etcd3 - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- flatpak - improve the parsing of Flatpak application IDs based on official guidelines (https://github.com/ansible-collections/community.general/pull/8909).
- gconftool2 - make use of ``ModuleHelper`` features to simplify code (https://github.com/ansible-collections/community.general/pull/8711).
- gcontool2 - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9064).
- gcontool2 module utils - add argument formatter ``version`` (https://github.com/ansible-collections/community.general/pull/9064).
- gcontool2_info - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9064).
- gio_mime - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9067).
- gio_mime - adjust code ahead of the old ``VardDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8855).
- gio_mime - mute the  old ``VarDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8776).
- gio_mime module utils - add argument formatter ``version`` (https://github.com/ansible-collections/community.general/pull/9067).
- github_app_access_token lookup plugin - adds new ``private_key`` parameter (https://github.com/ansible-collections/community.general/pull/8989).
- gitlab_deploy_key - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_group - add many new parameters (https://github.com/ansible-collections/community.general/pull/8908).
- gitlab_group - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- gitlab_issue - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_merge_request - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_project - add option ``container_expiration_policy`` to schedule container registry cleanup (https://github.com/ansible-collections/community.general/pull/8674).
- gitlab_project - add option ``issues_access_level`` to enable/disable project issues (https://github.com/ansible-collections/community.general/pull/8760).
- gitlab_project - add option ``model_registry_access_level`` to disable model registry (https://github.com/ansible-collections/community.general/pull/8688).
- gitlab_project - add option ``pages_access_level`` to disable project pages (https://github.com/ansible-collections/community.general/pull/8688).
- gitlab_project - add option ``repository_access_level`` to disable project repository (https://github.com/ansible-collections/community.general/pull/8674).
- gitlab_project - add option ``service_desk_enabled`` to disable service desk (https://github.com/ansible-collections/community.general/pull/8688).
- gitlab_project - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- gitlab_project - sorted parameters in order to avoid future merge conflicts (https://github.com/ansible-collections/community.general/pull/8759).
- gitlab_runner - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- hashids filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- homebrew - speed up brew install and upgrade (https://github.com/ansible-collections/community.general/pull/9022).
- hwc_ecs_instance - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_evs_disk - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_eip - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_peering_connect - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_port - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_subnet - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- icinga2_host - replace loop with dict comprehension (https://github.com/ansible-collections/community.general/pull/8876).
- imc_rest - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- ipa_dnsrecord - adds ``SSHFP`` record type for managing SSH fingerprints in FreeIPA DNS (https://github.com/ansible-collections/community.general/pull/8404).
- ipa_otptoken - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- jenkins_node - add ``offline_message`` parameter for updating a Jenkins node offline cause reason when the state is "disabled" (offline) (https://github.com/ansible-collections/community.general/pull/9084)."
- jira - adjust code ahead of the old ``VardDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8856).
- jira - mute the  old ``VarDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8776).
- jira - replace deprecated params when using decorator ``cause_changes`` (https://github.com/ansible-collections/community.general/pull/8791).
- keep_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- keycloak_client - add ``client-x509`` choice to ``client_authenticator_type`` (https://github.com/ansible-collections/community.general/pull/8973).
- keycloak_client - assign auth flow by name (https://github.com/ansible-collections/community.general/pull/8428).
- keycloak_client - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_clientscope - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_identity_provider - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_realm - add boolean toggle to configure organization support for a given keycloak realm (https://github.com/ansible-collections/community.general/issues/9027, https://github.com/ansible-collections/community.general/pull/8927/).
- keycloak_user_federation - add module argument allowing users to optout of the removal of unspecified mappers, for example to keep the keycloak default mappers (https://github.com/ansible-collections/community.general/pull/8764).
- keycloak_user_federation - add the user federation config parameter ``referral`` to the module arguments (https://github.com/ansible-collections/community.general/pull/8954).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- linode - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- locale_gen - add support for multiple locales (https://github.com/ansible-collections/community.general/issues/8677, https://github.com/ansible-collections/community.general/pull/8682).
- lxc_container - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- lxd_container - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- manageiq_provider - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- mattermost - adds support for message priority (https://github.com/ansible-collections/community.general/issues/9068, https://github.com/ansible-collections/community.general/pull/9087).
- memcached, pickle, redis, yaml cache plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8624).
- memset_dns_reload - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- memset_memstore_info - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- memset_server_info - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- memset_zone - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- memset_zone_domain - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- memset_zone_record - replace loop with ``dict()`` (https://github.com/ansible-collections/community.general/pull/8876).
- nmcli - add ``conn_enable`` param to reload connection (https://github.com/ansible-collections/community.general/issues/3752, https://github.com/ansible-collections/community.general/issues/8704, https://github.com/ansible-collections/community.general/pull/8897).
- nmcli - add ``state=up`` and ``state=down`` to enable/disable connections (https://github.com/ansible-collections/community.general/issues/3752, https://github.com/ansible-collections/community.general/issues/8704, https://github.com/ansible-collections/community.general/issues/7152, https://github.com/ansible-collections/community.general/pull/8897).
- nmcli - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- npm - add ``force`` parameter to allow ``--force`` (https://github.com/ansible-collections/community.general/pull/8885).
- ocapi_utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- one_image - add ``create``, ``template`` and ``datastore_id`` arguments for image creation (https://github.com/ansible-collections/community.general/pull/9075).
- one_image - add ``wait_timeout`` argument for adjustable timeouts (https://github.com/ansible-collections/community.general/pull/9075).
- one_image - add option ``persistent`` to manage image persistence (https://github.com/ansible-collections/community.general/issues/3578, https://github.com/ansible-collections/community.general/pull/8889).
- one_image - extend xsd scheme to make it return a lot more info about image (https://github.com/ansible-collections/community.general/pull/8889).
- one_image - refactor code to make it more similar to ``one_template`` and ``one_vnet`` (https://github.com/ansible-collections/community.general/pull/8889).
- one_image_info - extend xsd scheme to make it return a lot more info about image (https://github.com/ansible-collections/community.general/pull/8889).
- one_image_info - refactor code to make it more similar to ``one_template`` and ``one_vnet`` (https://github.com/ansible-collections/community.general/pull/8889).
- one_service - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- one_vm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- onepassword lookup plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- open_iscsi - allow login to a portal with multiple targets without specifying any of them (https://github.com/ansible-collections/community.general/pull/8719).
- openbsd_pkg - adds diff support to show changes in installed package list. This does not yet work for check mode (https://github.com/ansible-collections/community.general/pull/8402).
- opennebula.py - add VM ``id`` and VM ``host`` to inventory host data (https://github.com/ansible-collections/community.general/pull/8532).
- opentelemetry callback plugin - fix default value for ``store_spans_in_file`` causing traces to be produced to a file named ``None`` (https://github.com/ansible-collections/community.general/issues/8566, https://github.com/ansible-collections/community.general/pull/8741).
- opkg - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9086).
- passwordstore lookup plugin - add subkey creation/update support (https://github.com/ansible-collections/community.general/pull/8952).
- passwordstore lookup plugin - add the current user to the lockfile file name to address issues on multi-user systems (https://github.com/ansible-collections/community.general/pull/8689).
- pids - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pipx - add parameter ``suffix`` to module (https://github.com/ansible-collections/community.general/pull/8675, https://github.com/ansible-collections/community.general/issues/8656).
- pipx - added new states ``install_all``, ``uninject``, ``upgrade_shared``, ``pin``, and ``unpin`` (https://github.com/ansible-collections/community.general/pull/8809).
- pipx - added parameter ``global`` to module (https://github.com/ansible-collections/community.general/pull/8793).
- pipx - refactor out parsing of ``pipx list`` output to module utils (https://github.com/ansible-collections/community.general/pull/9044).
- pipx - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pipx_info - add new return value ``pinned`` (https://github.com/ansible-collections/community.general/pull/9044).
- pipx_info - added parameter ``global`` to module (https://github.com/ansible-collections/community.general/pull/8793).
- pipx_info - refactor out parsing of ``pipx list`` output to module utils (https://github.com/ansible-collections/community.general/pull/9044).
- pipx_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pkg5_publisher - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pkgng - add option ``use_globs`` (default ``true``) to optionally disable glob patterns (https://github.com/ansible-collections/community.general/issues/8632, https://github.com/ansible-collections/community.general/pull/8633).
- proxmox - add ``disk_volume`` and ``mount_volumes`` keys for better readability (https://github.com/ansible-collections/community.general/pull/8542).
- proxmox - allow specification of the API port when using proxmox_* (https://github.com/ansible-collections/community.general/issues/8440, https://github.com/ansible-collections/community.general/pull/8441).
- proxmox - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox - translate the old ``disk`` and ``mounts`` keys to the new handling internally (https://github.com/ansible-collections/community.general/pull/8542).
- proxmox inventory plugin - add new fact for LXC interface details (https://github.com/ansible-collections/community.general/pull/8713).
- proxmox inventory plugin - clean up authentication code (https://github.com/ansible-collections/community.general/pull/8917).
- proxmox inventory plugin - fix urllib3 ``InsecureRequestWarnings`` not being suppressed when a token is used (https://github.com/ansible-collections/community.general/pull/9099).
- proxmox_disk - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox_kvm - adds the ``ciupgrade`` parameter to specify whether cloud-init should upgrade system packages at first boot (https://github.com/ansible-collections/community.general/pull/9066).
- proxmox_kvm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox_kvm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- proxmox_template - small refactor in logic for determining whether a template exists or not (https://github.com/ansible-collections/community.general/pull/8516).
- proxmox_vm_info - add ``network`` option to retrieve current network information (https://github.com/ansible-collections/community.general/pull/8471).
- redfish_* modules - adds ``ciphers`` option for custom cipher selection (https://github.com/ansible-collections/community.general/pull/8533).
- redfish_command - add ``UpdateUserAccountTypes`` command (https://github.com/ansible-collections/community.general/issues/9058, https://github.com/ansible-collections/community.general/pull/9059).
- redfish_command - add ``wait`` and ``wait_timeout`` options to allow a user to block a command until a service is accessible after performing the requested command (https://github.com/ansible-collections/community.general/issues/8051, https://github.com/ansible-collections/community.general/pull/8434).
- redfish_command - add handling of the ``PasswordChangeRequired`` message from services in the ``UpdateUserPassword`` command to directly modify the user's password if the requested user is the one invoking the operation (https://github.com/ansible-collections/community.general/issues/8652, https://github.com/ansible-collections/community.general/pull/8653).
- redfish_confg - remove ``CapacityBytes`` from required paramaters of the ``CreateVolume`` command (https://github.com/ansible-collections/community.general/pull/8956).
- redfish_config - add parameter ``storage_none_volume_deletion`` to ``CreateVolume`` command in order to control the automatic deletion of non-RAID volumes (https://github.com/ansible-collections/community.general/pull/8990).
- redfish_info - add command ``CheckAvailability`` to check if a service is accessible (https://github.com/ansible-collections/community.general/issues/8051, https://github.com/ansible-collections/community.general/pull/8434).
- redfish_info - adds ``RedfishURI`` and ``StorageId`` to Disk inventory (https://github.com/ansible-collections/community.general/pull/8937).
- redfish_utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- redfish_utils module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- redfish_utils module utils - schedule a BIOS configuration job at next reboot when the BIOS config is changed (https://github.com/ansible-collections/community.general/pull/9012).
- redis cache plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- redis, redis_info - add ``client_cert`` and ``client_key`` options to specify path to certificate for Redis authentication  (https://github.com/ansible-collections/community.general/pull/8654).
- redis_info - adds support for getting cluster info (https://github.com/ansible-collections/community.general/pull/8464).
- remove_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- replace_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- scaleway - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- scaleway_compute - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_container - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_container_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_container_namespace - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_container_namespace_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_container_registry - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_container_registry_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_function - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_function_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_function_namespace - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_function_namespace_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8858).
- scaleway_ip - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_lb - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_security_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- scaleway_security_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_user_data - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- scaleway_user_data - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- sensu_silence - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- snmp_facts - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- sorcery - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- sudosu become plugin - added an option (``alt_method``) to enhance compatibility with more versions of ``su`` (https://github.com/ansible-collections/community.general/pull/8214).
- udm_dns_record - replace loop with ``dict.update()`` (https://github.com/ansible-collections/community.general/pull/8876).
- ufw - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- unsafe plugin utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- vardict module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- vars MH module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- virtualbox inventory plugin - expose a new parameter ``enable_advanced_group_parsing`` to change how the VirtualBox dynamic inventory parses VM groups (https://github.com/ansible-collections/community.general/issues/8508, https://github.com/ansible-collections/community.general/pull/8510).
- vmadm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- wdc_redfish_command - minor change to handle upgrade file for Redfish WD platforms (https://github.com/ansible-collections/community.general/pull/8444).

Breaking Changes / Porting Guide
--------------------------------

- The collection no longer supports ansible-core 2.13 and ansible-core 2.14. While most (or even all) modules and plugins might still work with these versions, they are no longer tested in CI and breakages regarding them will not be fixed (https://github.com/ansible-collections/community.general/pull/8921).
- cmd_runner module utils - CLI arguments created directly from module parameters are no longer assigned a default formatter (https://github.com/ansible-collections/community.general/pull/8928).
- irc - the defaults of ``use_tls`` and ``validate_certs`` changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/8918).
- rhsm_repository - the states ``present`` and ``absent`` have been removed. Use ``enabled`` and ``disabled`` instead (https://github.com/ansible-collections/community.general/pull/8918).

Deprecated Features
-------------------

- CmdRunner module util - setting the value of the ``ignore_none`` parameter within a ``CmdRunner`` context is deprecated and that feature should be removed in community.general 12.0.0 (https://github.com/ansible-collections/community.general/pull/8479).
- MH decorator cause_changes module utils - deprecate parameters ``on_success`` and ``on_failure`` (https://github.com/ansible-collections/community.general/pull/8791).
- git_config - the ``list_all`` option has been deprecated and will be removed in community.general 11.0.0. Use the ``community.general.git_config_info`` module instead (https://github.com/ansible-collections/community.general/pull/8453).
- git_config - using ``state=present`` without providing ``value`` is deprecated and will be disallowed in community.general 11.0.0. Use the ``community.general.git_config_info`` module instead to read a value (https://github.com/ansible-collections/community.general/pull/8453).
- hipchat - the hipchat service has been discontinued and the self-hosted variant has been End of Life since 2020. The module is therefore deprecated and will be removed from community.general 11.0.0 if nobody provides compelling reasons to still keep it (https://github.com/ansible-collections/community.general/pull/8919).
- pipx - support for versions of the command line tool ``pipx`` older than ``1.7.0`` is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/8793).
- pipx_info - support for versions of the command line tool ``pipx`` older than ``1.7.0`` is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/8793).

Removed Features (previously deprecated)
----------------------------------------

- The consul_acl module has been removed. Use community.general.consul_token and/or community.general.consul_policy instead (https://github.com/ansible-collections/community.general/pull/8921).
- The hipchat callback plugin has been removed. The hipchat service has been discontinued and the self-hosted variant has been End of Life since 2020 (https://github.com/ansible-collections/community.general/pull/8921).
- The redhat module utils has been removed (https://github.com/ansible-collections/community.general/pull/8921).
- The rhn_channel module has been removed (https://github.com/ansible-collections/community.general/pull/8921).
- The rhn_register module has been removed (https://github.com/ansible-collections/community.general/pull/8921).
- consul - removed the ``ack_params_state_absent`` option. It had no effect anymore (https://github.com/ansible-collections/community.general/pull/8918).
- ejabberd_user - removed the ``logging`` option (https://github.com/ansible-collections/community.general/pull/8918).
- gitlab modules - remove basic auth feature (https://github.com/ansible-collections/community.general/pull/8405).
- proxmox_kvm - removed the ``proxmox_default_behavior`` option. Explicitly specify the old default values if you were using ``proxmox_default_behavior=compatibility``, otherwise simply remove it (https://github.com/ansible-collections/community.general/pull/8918).
- redhat_subscriptions - removed the ``pool`` option. Use ``pool_ids`` instead (https://github.com/ansible-collections/community.general/pull/8918).

Bugfixes
--------

- bitwarden lookup plugin - fix ``KeyError`` in ``search_field`` (https://github.com/ansible-collections/community.general/issues/8549, https://github.com/ansible-collections/community.general/pull/8557).
- bitwarden lookup plugin - support BWS v0.3.0 syntax breaking change (https://github.com/ansible-collections/community.general/pull/9028).
- cloudflare_dns - fix changing Cloudflare SRV records (https://github.com/ansible-collections/community.general/issues/8679, https://github.com/ansible-collections/community.general/pull/8948).
- cmd_runner module utils - call to ``get_best_parsable_locales()`` was missing parameter (https://github.com/ansible-collections/community.general/pull/8929).
- collection_version lookup plugin - use ``importlib`` directly instead of the deprecated and in ansible-core 2.19 removed ``ansible.module_utils.compat.importlib`` (https://github.com/ansible-collections/community.general/pull/9084).
- cpanm - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- dig lookup plugin - fix using only the last nameserver specified (https://github.com/ansible-collections/community.general/pull/8970).
- django module utils - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- django_command - option ``command`` is now split lexically before passed to underlying PythonRunner (https://github.com/ansible-collections/community.general/pull/8944).
- gconftool2_info - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- git_config - fix behavior of ``state=absent`` if ``value`` is present (https://github.com/ansible-collections/community.general/issues/8436, https://github.com/ansible-collections/community.general/pull/8452).
- gitlab_group_access_token - fix crash in check mode caused by attempted access to a newly created access token (https://github.com/ansible-collections/community.general/pull/8796).
- gitlab_label - update label's color (https://github.com/ansible-collections/community.general/pull/9010).
- gitlab_project - fix ``container_expiration_policy`` not being applied when creating a new project (https://github.com/ansible-collections/community.general/pull/8790).
- gitlab_project - fix crash caused by old Gitlab projects not having a ``container_expiration_policy`` attribute (https://github.com/ansible-collections/community.general/pull/8790).
- gitlab_project_access_token - fix crash in check mode caused by attempted access to a newly created access token (https://github.com/ansible-collections/community.general/pull/8796).
- gitlab_runner - fix ``paused`` parameter being ignored (https://github.com/ansible-collections/community.general/pull/8648).
- homebrew - do not fail when brew prints warnings (https://github.com/ansible-collections/community.general/pull/8406, https://github.com/ansible-collections/community.general/issues/7044).
- homebrew_cask - fix ``upgrade_all`` returns ``changed`` when nothing upgraded (https://github.com/ansible-collections/community.general/issues/8707, https://github.com/ansible-collections/community.general/pull/8708).
- homectl - the module now tries to use ``legacycrypt`` on Python 3.13+ (https://github.com/ansible-collections/community.general/issues/4691, https://github.com/ansible-collections/community.general/pull/8987).
- hponcfg - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- ini_file - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- ipa_host - add ``force_create``, fix ``enabled`` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/1094, https://github.com/ansible-collections/community.general/pull/8920).
- ipa_hostgroup - fix ``enabled `` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/8408, https://github.com/ansible-collections/community.general/pull/8900).
- java_keystore - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- jenkins_node - fixed ``enabled``, ``disable`` and ``absent`` node state redirect authorization issues, same as was present for ``present`` (https://github.com/ansible-collections/community.general/pull/9084).
- jenkins_plugin - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- kdeconfig - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- kernel_blacklist - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- keycloak_client - fix TypeError when sanitizing the ``saml.signing.private.key`` attribute in the module's diff or state output. The ``sanitize_cr`` function expected a dict where in some cases a list might occur (https://github.com/ansible-collections/community.general/pull/8403).
- keycloak_clientscope - remove IDs from clientscope and its protocol mappers on comparison for changed check (https://github.com/ansible-collections/community.general/pull/8545).
- keycloak_clientscope_type - fix detect changes in check mode (https://github.com/ansible-collections/community.general/issues/9092, https://github.com/ansible-collections/community.general/pull/9093).
- keycloak_group - fix crash caused in subgroup creation. The crash was caused by a missing or empty ``subGroups`` property in Keycloak ≥23 (https://github.com/ansible-collections/community.general/issues/8788, https://github.com/ansible-collections/community.general/pull/8979).
- keycloak_realm - add normalizations for ``attributes`` and ``protocol_mappers`` (https://github.com/ansible-collections/community.general/pull/8496).
- keycloak_realm - fix change detection in check mode by sorting the lists in the realms beforehand (https://github.com/ansible-collections/community.general/pull/8877).
- keycloak_realm_key - fix invalid usage of ``parent_id`` (https://github.com/ansible-collections/community.general/issues/7850, https://github.com/ansible-collections/community.general/pull/8823).
- keycloak_user_federation - add module argument allowing users to configure the update mode for the parameter ``bindCredential`` (https://github.com/ansible-collections/community.general/pull/8898).
- keycloak_user_federation - fix key error when removing mappers during an update and new mappers are specified in the module args (https://github.com/ansible-collections/community.general/pull/8762).
- keycloak_user_federation - fix the ``UnboundLocalError`` that occurs when an ID is provided for a user federation mapper (https://github.com/ansible-collections/community.general/pull/8831).
- keycloak_user_federation - get cleartext IDP ``clientSecret`` from full realm info to detect changes to it (https://github.com/ansible-collections/community.general/issues/8294, https://github.com/ansible-collections/community.general/pull/8735).
- keycloak_user_federation - minimize change detection by setting ``krbPrincipalAttribute`` to ``''`` in Keycloak responses if missing (https://github.com/ansible-collections/community.general/pull/8785).
- keycloak_user_federation - remove ``lastSync`` parameter from Keycloak responses to minimize diff/changes (https://github.com/ansible-collections/community.general/pull/8812).
- keycloak_user_federation - remove existing user federation mappers if they are not present in the federation configuration and will not be updated (https://github.com/ansible-collections/community.general/issues/7169, https://github.com/ansible-collections/community.general/pull/8695).
- keycloak_user_federation - sort desired and after mapper list by name (analog to before mapper list) to minimize diff and make change detection more accurate (https://github.com/ansible-collections/community.general/pull/8761).
- keycloak_userprofile - fix empty response when fetching userprofile component by removing ``parent=parent_id`` filter (https://github.com/ansible-collections/community.general/pull/8923).
- keycloak_userprofile - improve diff by deserializing the fetched ``kc.user.profile.config`` and serialize it only when sending back (https://github.com/ansible-collections/community.general/pull/8940).
- launched - correctly report changed status in check mode (https://github.com/ansible-collections/community.general/pull/8406).
- locale_gen - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- lxd_container - fix bug introduced in previous commit (https://github.com/ansible-collections/community.general/pull/8895, https://github.com/ansible-collections/community.general/issues/8888).
- mksysb - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- modprobe - fix check mode not being honored for ``persistent`` option (https://github.com/ansible-collections/community.general/issues/9051, https://github.com/ansible-collections/community.general/pull/9052).
- nsupdate - fix 'index out of range' error when changing NS records by falling back to authority section of the response (https://github.com/ansible-collections/community.general/issues/8612, https://github.com/ansible-collections/community.general/pull/8614).
- one_host - fix if statements for cases when ``ID=0`` (https://github.com/ansible-collections/community.general/issues/1199, https://github.com/ansible-collections/community.general/pull/8907).
- one_image - fix module failing due to a class method typo (https://github.com/ansible-collections/community.general/pull/9056).
- one_image_info - fix module failing due to a class method typo (https://github.com/ansible-collections/community.general/pull/9056).
- one_service - fix service creation after it was deleted with ``unique`` parameter (https://github.com/ansible-collections/community.general/issues/3137, https://github.com/ansible-collections/community.general/pull/8887).
- one_vnet - fix module failing due to a variable typo (https://github.com/ansible-collections/community.general/pull/9019).
- opennebula inventory plugin - fix invalid reference to IP when inventory runs against NICs with no IPv4 address (https://github.com/ansible-collections/community.general/pull/8489).
- opentelemetry callback - do not save the JSON response when using the ``ansible.builtin.uri`` module (https://github.com/ansible-collections/community.general/pull/8430).
- opentelemetry callback - do not save the content response when using the ``ansible.builtin.slurp`` module (https://github.com/ansible-collections/community.general/pull/8430).
- pam_limits - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- paman - do not fail if an empty list of packages has been provided and there is nothing to do (https://github.com/ansible-collections/community.general/pull/8514).
- pipx - it was ignoring ``global`` when listing existing applications (https://github.com/ansible-collections/community.general/pull/9044).
- pipx module utils - add missing command line formatter for argument ``spec_metadata`` (https://github.com/ansible-collections/community.general/pull/9044).
- pipx_info - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- proxmox - fix idempotency on creation of mount volumes using Proxmox' special ``<storage>:<size>`` syntax (https://github.com/ansible-collections/community.general/issues/8407, https://github.com/ansible-collections/community.general/pull/8542).
- proxmox - fixed an issue where the new volume handling incorrectly converted ``null`` values into ``"None"`` strings (https://github.com/ansible-collections/community.general/pull/8646).
- proxmox - fixed an issue where volume strings where overwritten instead of appended to in the new ``build_volume()`` method (https://github.com/ansible-collections/community.general/pull/8646).
- proxmox - removed the forced conversion of non-string values to strings to be consistent with the module documentation (https://github.com/ansible-collections/community.general/pull/8646).
- proxmox inventory plugin - fixed a possible error on concatenating responses from proxmox. In case an API call unexpectedly returned an empty result, the inventory failed with a fatal error. Added check for empty response (https://github.com/ansible-collections/community.general/issues/8798, https://github.com/ansible-collections/community.general/pull/8794).
- python_runner module utils - parameter ``path_prefix`` was being handled as string when it should be a list (https://github.com/ansible-collections/community.general/pull/8944).
- redfish_utils module utils - do not fail when language is not exactly "en" (https://github.com/ansible-collections/community.general/pull/8613).
- redfish_utils module utils - fix issue with URI parsing to gracefully handling trailing slashes when extracting member identifiers (https://github.com/ansible-collections/community.general/issues/9047, https://github.com/ansible-collections/community.general/pull/9057).
- snap - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- snap_alias - use new ``VarDict`` to prevent deprecation warning (https://github.com/ansible-collections/community.general/issues/8410, https://github.com/ansible-collections/community.general/pull/8411).
- udm_user - the module now tries to use ``legacycrypt`` on Python 3.13+ (https://github.com/ansible-collections/community.general/issues/4690, https://github.com/ansible-collections/community.general/pull/8987).

Known Issues
------------

- jenkins_node - the module is not able to update offline message when node is already offline due to internally using toggleOffline API (https://github.com/ansible-collections/community.general/pull/9084).

New Plugins
-----------

Filter
~~~~~~

- community.general.keep_keys - Keep specific keys from dictionaries in a list.
- community.general.remove_keys - Remove specific keys from dictionaries in a list.
- community.general.replace_keys - Replace specific keys in a list of dictionaries.
- community.general.reveal_ansible_type - Return input type.

Test
~~~~

- community.general.ansible_type - Validate input type.

New Modules
-----------

- community.general.bootc_manage - Bootc Switch and Upgrade.
- community.general.consul_agent_check - Add, modify, and delete checks within a consul cluster.
- community.general.consul_agent_service - Add, modify and delete services within a consul cluster.
- community.general.django_check - Wrapper for C(django-admin check).
- community.general.django_createcachetable - Wrapper for C(django-admin createcachetable).
- community.general.homebrew_services - Services manager for Homebrew.
- community.general.ipa_getkeytab - Manage keytab file in FreeIPA.
- community.general.jenkins_node - Manage Jenkins nodes.
- community.general.keycloak_component - Allows administration of Keycloak components via Keycloak API.
- community.general.keycloak_realm_keys_metadata_info - Allows obtaining Keycloak realm keys metadata via Keycloak API.
- community.general.keycloak_userprofile - Allows managing Keycloak User Profiles.
- community.general.krb_ticket - Kerberos utils for managing tickets.
- community.general.one_vnet - Manages OpenNebula virtual networks.
- community.general.zypper_repository_info - List Zypper repositories.
