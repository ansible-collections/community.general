===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 2.0.0.

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
- urmpi - deprecated invalid parameter aliases ``update-cache`` and ``no-recommends``, will be removed in 5.0.0 (https://github.com/ansible-collections/community.general/pull/1927).
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
