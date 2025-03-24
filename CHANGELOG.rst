===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 8.0.0.

v9.5.6
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- consul_token - fix idempotency when ``policies`` or ``roles`` are supplied by name (https://github.com/ansible-collections/community.general/issues/9841, https://github.com/ansible-collections/community.general/pull/9845).

Bugfixes
--------

- cloudlare_dns - handle exhausted response stream in case of HTTP errors to show nice error message to the user (https://github.com/ansible-collections/community.general/issues/9782, https://github.com/ansible-collections/community.general/pull/9818).
- dnf_versionlock - add support for dnf5 (https://github.com/ansible-collections/community.general/issues/9556).
- homebrew_cask - handle unusual brew version strings (https://github.com/ansible-collections/community.general/issues/8432, https://github.com/ansible-collections/community.general/pull/9881).
- ipa_host - module revoked existing host certificates even if ``user_certificate`` was not given (https://github.com/ansible-collections/community.general/pull/9694).
- nmcli - enable changing only the order of DNS servers or search suffixes (https://github.com/ansible-collections/community.general/issues/8724, https://github.com/ansible-collections/community.general/pull/9880).
- proxmox_vm_info - the module no longer expects that the key ``template`` exists in a dictionary returned by Proxmox (https://github.com/ansible-collections/community.general/issues/9875, https://github.com/ansible-collections/community.general/pull/9910).
- sudoers - display stdout and stderr raised while failed validation (https://github.com/ansible-collections/community.general/issues/9674, https://github.com/ansible-collections/community.general/pull/9871).

v9.5.5
======

Release Summary
---------------

Regular bugfix release.

Bugfixes
--------

- apache2_mod_proxy - make compatible with Python 3 (https://github.com/ansible-collections/community.general/pull/9762).
- apache2_mod_proxy - passing the cluster's page as referer for the member's pages. This makes the module actually work again for halfway modern Apache versions. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 (https://github.com/ansible-collections/community.general/pull/9762).
- cloudflare_dns - fix crash when deleting a DNS record or when updating a record with ``solo=true`` (https://github.com/ansible-collections/community.general/issues/9652, https://github.com/ansible-collections/community.general/pull/9649).
- elasticsearch_plugin - fix ``ERROR: D is not a recognized option`` issue when configuring proxy settings (https://github.com/ansible-collections/community.general/pull/9774, https://github.com/ansible-collections/community.general/issues/9773).
- keycloak_client - fix and improve existing tests. The module showed a diff without actual changes, solved by improving the ``normalise_cr()`` function (https://github.com/ansible-collections/community.general/pull/9644).
- keycloak_client - in check mode, detect whether the lists in before client (for example redirect URI list) contain items that the lists in the desired client do not contain (https://github.com/ansible-collections/community.general/pull/9739).
- passwordstore lookup plugin - fix subkey creation even when ``create=false`` (https://github.com/ansible-collections/community.general/issues/9105, https://github.com/ansible-collections/community.general/pull/9106).
- proxmox inventory plugin - plugin did not update cache correctly after ``meta: refresh_inventory`` (https://github.com/ansible-collections/community.general/issues/9710, https://github.com/ansible-collections/community.general/pull/9760).
- redhat_subscription - use the "enable_content" option (when available) when
  registering using D-Bus, to ensure that subscription-manager enables the
  content on registration; this is particular important on EL 10+ and Fedora
  41+
  (https://github.com/ansible-collections/community.general/pull/9778).
- xml - ensure file descriptor is closed (https://github.com/ansible-collections/community.general/pull/9695).

v9.5.4
======

Security Fixes
--------------

- keycloak_client - Sanitize ``saml.encryption.private.key`` so it does not show in the logs (https://github.com/ansible-collections/community.general/pull/9621).

Bugfixes
--------

- redhat_subscription - do not try to unsubscribe (i.e. remove subscriptions)
  when unregistering a system: newer versions of subscription-manager, as
  available in EL 10 and Fedora 41+, do not support entitlements anymore, and
  thus unsubscribing will fail
  (https://github.com/ansible-collections/community.general/pull/9578).

v9.5.3
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- proxmox module utils - add method ``api_task_complete`` that can wait for task completion and return error message (https://github.com/ansible-collections/community.general/pull/9256).

Security Fixes
--------------

- keycloak_authentication - API calls did not properly set the ``priority`` during update resulting in incorrectly sorted authentication flows. This apparently only affects Keycloak 25 or newer (https://github.com/ansible-collections/community.general/pull/9263).

Bugfixes
--------

- dig lookup plugin - correctly handle ``NoNameserver`` exception (https://github.com/ansible-collections/community.general/pull/9363, https://github.com/ansible-collections/community.general/issues/9362).
- htpasswd - report changes when file permissions are adjusted (https://github.com/ansible-collections/community.general/issues/9485, https://github.com/ansible-collections/community.general/pull/9490).
- proxmox_disk - fix async method and make ``resize_disk`` method handle errors correctly (https://github.com/ansible-collections/community.general/pull/9256).
- proxmox_template - fix the wrong path called on ``proxmox_template.task_status`` (https://github.com/ansible-collections/community.general/issues/9276, https://github.com/ansible-collections/community.general/pull/9277).
- qubes connection plugin - fix the printing of debug information (https://github.com/ansible-collections/community.general/pull/9334).
- redfish_utils module utils - Fix ``VerifyBiosAttributes`` command on multi system resource nodes (https://github.com/ansible-collections/community.general/pull/9234).

v9.5.2
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- proxmox inventory plugin - fix urllib3 ``InsecureRequestWarnings`` not being suppressed when a token is used (https://github.com/ansible-collections/community.general/pull/9099).

Bugfixes
--------

- dnf_config_manager - fix hanging when prompting to import GPG keys (https://github.com/ansible-collections/community.general/pull/9124, https://github.com/ansible-collections/community.general/issues/8830).
- dnf_config_manager - forces locale to ``C`` before module starts. If the locale was set to non-English, the output of the ``dnf config-manager`` could not be parsed (https://github.com/ansible-collections/community.general/pull/9157, https://github.com/ansible-collections/community.general/issues/9046).
- flatpak - force the locale language to ``C`` when running the flatpak command (https://github.com/ansible-collections/community.general/pull/9187, https://github.com/ansible-collections/community.general/issues/8883).
- github_key - in check mode, a faulty call to ```datetime.strftime(...)``` was being made which generated an exception (https://github.com/ansible-collections/community.general/issues/9185).
- homebrew_cask - allow ``+`` symbol in Homebrew cask name validation regex (https://github.com/ansible-collections/community.general/pull/9128).
- keycloak_client - fix diff by removing code that turns the attributes dict which contains additional settings into a list (https://github.com/ansible-collections/community.general/pull/9077).
- keycloak_clientscope - fix diff and ``end_state`` by removing the code that turns the attributes dict, which contains additional config items, into a list (https://github.com/ansible-collections/community.general/pull/9082).
- keycloak_clientscope_type - sort the default and optional clientscope lists to improve the diff (https://github.com/ansible-collections/community.general/pull/9202).
- redfish_utils module utils - remove undocumented default applytime (https://github.com/ansible-collections/community.general/pull/9114).
- slack - fail if Slack API response is not OK with error message (https://github.com/ansible-collections/community.general/pull/9198).

v9.5.1
======

Release Summary
---------------

Regular bugfix release.

Minor Changes
-------------

- redfish_utils module utils - schedule a BIOS configuration job at next reboot when the BIOS config is changed (https://github.com/ansible-collections/community.general/pull/9012).

Bugfixes
--------

- bitwarden lookup plugin - support BWS v0.3.0 syntax breaking change (https://github.com/ansible-collections/community.general/pull/9028).
- collection_version lookup plugin - use ``importlib`` directly instead of the deprecated and in ansible-core 2.19 removed ``ansible.module_utils.compat.importlib`` (https://github.com/ansible-collections/community.general/pull/9084).
- gitlab_label - update label's color (https://github.com/ansible-collections/community.general/pull/9010).
- keycloak_clientscope_type - fix detect changes in check mode (https://github.com/ansible-collections/community.general/issues/9092, https://github.com/ansible-collections/community.general/pull/9093).
- keycloak_group - fix crash caused in subgroup creation. The crash was caused by a missing or empty ``subGroups`` property in Keycloak ≥23 (https://github.com/ansible-collections/community.general/issues/8788, https://github.com/ansible-collections/community.general/pull/8979).
- modprobe - fix check mode not being honored for ``persistent`` option (https://github.com/ansible-collections/community.general/issues/9051, https://github.com/ansible-collections/community.general/pull/9052).
- one_host - fix if statements for cases when ``ID=0`` (https://github.com/ansible-collections/community.general/issues/1199, https://github.com/ansible-collections/community.general/pull/8907).
- one_image - fix module failing due to a class method typo (https://github.com/ansible-collections/community.general/pull/9056).
- one_image_info - fix module failing due to a class method typo (https://github.com/ansible-collections/community.general/pull/9056).
- one_vnet - fix module failing due to a variable typo (https://github.com/ansible-collections/community.general/pull/9019).
- redfish_utils module utils - fix issue with URI parsing to gracefully handling trailing slashes when extracting member identifiers (https://github.com/ansible-collections/community.general/issues/9047, https://github.com/ansible-collections/community.general/pull/9057).

v9.5.0
======

Release Summary
---------------

Regular bugfix and feature release.

Please note that this is the last feature release for community.general 9.x.y.
From now on, new features will only go into community.general 10.x.y.

Minor Changes
-------------

- dig lookup plugin - add ``port`` option to specify DNS server port (https://github.com/ansible-collections/community.general/pull/8966).
- flatpak - improve the parsing of Flatpak application IDs based on official guidelines (https://github.com/ansible-collections/community.general/pull/8909).
- gio_mime - adjust code ahead of the old ``VardDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8855).
- gitlab_deploy_key - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_group - add many new parameters (https://github.com/ansible-collections/community.general/pull/8908).
- gitlab_group - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_issue - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_merge_request - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- gitlab_runner - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- icinga2_host - replace loop with dict comprehension (https://github.com/ansible-collections/community.general/pull/8876).
- jira - adjust code ahead of the old ``VardDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8856).
- keycloak_client - add ``client-x509`` choice to ``client_authenticator_type`` (https://github.com/ansible-collections/community.general/pull/8973).
- keycloak_user_federation - add the user federation config parameter ``referral`` to the module arguments (https://github.com/ansible-collections/community.general/pull/8954).
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
- one_image - add option ``persistent`` to manage image persistence (https://github.com/ansible-collections/community.general/issues/3578, https://github.com/ansible-collections/community.general/pull/8889).
- one_image - extend xsd scheme to make it return a lot more info about image (https://github.com/ansible-collections/community.general/pull/8889).
- one_image - refactor code to make it more similar to ``one_template`` and ``one_vnet`` (https://github.com/ansible-collections/community.general/pull/8889).
- one_image_info - extend xsd scheme to make it return a lot more info about image (https://github.com/ansible-collections/community.general/pull/8889).
- one_image_info - refactor code to make it more similar to ``one_template`` and ``one_vnet`` (https://github.com/ansible-collections/community.general/pull/8889).
- open_iscsi - allow login to a portal with multiple targets without specifying any of them (https://github.com/ansible-collections/community.general/pull/8719).
- opennebula.py - add VM ``id`` and VM ``host`` to inventory host data (https://github.com/ansible-collections/community.general/pull/8532).
- passwordstore lookup plugin - add subkey creation/update support (https://github.com/ansible-collections/community.general/pull/8952).
- proxmox inventory plugin - clean up authentication code (https://github.com/ansible-collections/community.general/pull/8917).
- redfish_command - add handling of the ``PasswordChangeRequired`` message from services in the ``UpdateUserPassword`` command to directly modify the user's password if the requested user is the one invoking the operation (https://github.com/ansible-collections/community.general/issues/8652, https://github.com/ansible-collections/community.general/pull/8653).
- redfish_confg - remove ``CapacityBytes`` from required paramaters of the ``CreateVolume`` command (https://github.com/ansible-collections/community.general/pull/8956).
- redfish_config - add parameter ``storage_none_volume_deletion`` to ``CreateVolume`` command in order to control the automatic deletion of non-RAID volumes (https://github.com/ansible-collections/community.general/pull/8990).
- redfish_info - adds ``RedfishURI`` and ``StorageId`` to Disk inventory (https://github.com/ansible-collections/community.general/pull/8937).
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
- scaleway_user_data - better construct when using ``dict.items()`` (https://github.com/ansible-collections/community.general/pull/8876).
- udm_dns_record - replace loop with ``dict.update()`` (https://github.com/ansible-collections/community.general/pull/8876).

Deprecated Features
-------------------

- hipchat - the hipchat service has been discontinued and the self-hosted variant has been End of Life since 2020. The module is therefore deprecated and will be removed from community.general 11.0.0 if nobody provides compelling reasons to still keep it (https://github.com/ansible-collections/community.general/pull/8919).

Bugfixes
--------

- cloudflare_dns - fix changing Cloudflare SRV records (https://github.com/ansible-collections/community.general/issues/8679, https://github.com/ansible-collections/community.general/pull/8948).
- cmd_runner module utils - call to ``get_best_parsable_locales()`` was missing parameter (https://github.com/ansible-collections/community.general/pull/8929).
- dig lookup plugin - fix using only the last nameserver specified (https://github.com/ansible-collections/community.general/pull/8970).
- django_command - option ``command`` is now split lexically before passed to underlying PythonRunner (https://github.com/ansible-collections/community.general/pull/8944).
- homectl - the module now tries to use ``legacycrypt`` on Python 3.13+ (https://github.com/ansible-collections/community.general/issues/4691, https://github.com/ansible-collections/community.general/pull/8987).
- ini_file - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- ipa_host - add ``force_create``, fix ``enabled`` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/1094, https://github.com/ansible-collections/community.general/pull/8920).
- ipa_hostgroup - fix ``enabled `` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/8408, https://github.com/ansible-collections/community.general/pull/8900).
- java_keystore - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- jenkins_plugin - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- kdeconfig - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- keycloak_realm - fix change detection in check mode by sorting the lists in the realms beforehand (https://github.com/ansible-collections/community.general/pull/8877).
- keycloak_user_federation - add module argument allowing users to configure the update mode for the parameter ``bindCredential`` (https://github.com/ansible-collections/community.general/pull/8898).
- keycloak_user_federation - minimize change detection by setting ``krbPrincipalAttribute`` to ``''`` in Keycloak responses if missing (https://github.com/ansible-collections/community.general/pull/8785).
- keycloak_user_federation - remove ``lastSync`` parameter from Keycloak responses to minimize diff/changes (https://github.com/ansible-collections/community.general/pull/8812).
- keycloak_userprofile - fix empty response when fetching userprofile component by removing ``parent=parent_id`` filter (https://github.com/ansible-collections/community.general/pull/8923).
- keycloak_userprofile - improve diff by deserializing the fetched ``kc.user.profile.config`` and serialize it only when sending back (https://github.com/ansible-collections/community.general/pull/8940).
- lxd_container - fix bug introduced in previous commit (https://github.com/ansible-collections/community.general/pull/8895, https://github.com/ansible-collections/community.general/issues/8888).
- one_service - fix service creation after it was deleted with ``unique`` parameter (https://github.com/ansible-collections/community.general/issues/3137, https://github.com/ansible-collections/community.general/pull/8887).
- pam_limits - pass absolute paths to ``module.atomic_move()`` (https://github.com/ansible/ansible/issues/83950, https://github.com/ansible-collections/community.general/pull/8925).
- python_runner module utils - parameter ``path_prefix`` was being handled as string when it should be a list (https://github.com/ansible-collections/community.general/pull/8944).
- udm_user - the module now tries to use ``legacycrypt`` on Python 3.13+ (https://github.com/ansible-collections/community.general/issues/4690, https://github.com/ansible-collections/community.general/pull/8987).

New Modules
-----------

- community.general.ipa_getkeytab - Manage keytab file in FreeIPA.

v9.4.0
======

Release Summary
---------------

Bugfix and feature release.

Minor Changes
-------------

- MH module utils - add parameter ``when`` to ``cause_changes`` decorator (https://github.com/ansible-collections/community.general/pull/8766).
- MH module utils - minor refactor in decorators (https://github.com/ansible-collections/community.general/pull/8766).
- alternatives - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- apache2_mod_proxy - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- apache2_mod_proxy - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- consul_acl - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- copr - Added ``includepkgs`` and ``excludepkgs`` parameters to limit the list of packages fetched or excluded from the repository(https://github.com/ansible-collections/community.general/pull/8779).
- credstash lookup plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- csv module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- deco MH module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- etcd3 - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- gio_mime - mute the  old ``VarDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8776).
- gitlab_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- gitlab_project - add option ``issues_access_level`` to enable/disable project issues (https://github.com/ansible-collections/community.general/pull/8760).
- gitlab_project - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- gitlab_project - sorted parameters in order to avoid future merge conflicts (https://github.com/ansible-collections/community.general/pull/8759).
- hashids filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- hwc_ecs_instance - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_evs_disk - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_eip - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_peering_connect - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_port - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- hwc_vpc_subnet - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- imc_rest - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- ipa_otptoken - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- jira - mute the  old ``VarDict`` deprecation (https://github.com/ansible-collections/community.general/pull/8776).
- jira - replace deprecated params when using decorator ``cause_changes`` (https://github.com/ansible-collections/community.general/pull/8791).
- keep_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- keycloak_client - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_clientscope - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_identity_provider - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_user_federation - add module argument allowing users to optout of the removal of unspecified mappers, for example to keep the keycloak default mappers (https://github.com/ansible-collections/community.general/pull/8764).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- keycloak_user_federation - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- linode - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- lxc_container - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- lxd_container - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- manageiq_provider - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- ocapi_utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- one_service - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- one_vm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- onepassword lookup plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pids - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pipx - added new states ``install_all``, ``uninject``, ``upgrade_shared``, ``pin``, and ``unpin`` (https://github.com/ansible-collections/community.general/pull/8809).
- pipx - added parameter ``global`` to module (https://github.com/ansible-collections/community.general/pull/8793).
- pipx - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pipx_info - added parameter ``global`` to module (https://github.com/ansible-collections/community.general/pull/8793).
- pipx_info - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- pkg5_publisher - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- proxmox - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox_disk - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox_kvm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- proxmox_kvm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- redfish_utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- redfish_utils module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- redis cache plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- remove_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- replace_keys filter plugin - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- scaleway - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- scaleway_compute - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_ip - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_lb - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_security_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- scaleway_security_group - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- scaleway_user_data - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- sensu_silence - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- snmp_facts - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- sorcery - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8833).
- ufw - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).
- unsafe plugin utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- vardict module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- vars MH module utils - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8814).
- vmadm - replace Python 2.6 construct with dict comprehensions (https://github.com/ansible-collections/community.general/pull/8822).

Deprecated Features
-------------------

- MH decorator cause_changes module utils - deprecate parameters ``on_success`` and ``on_failure`` (https://github.com/ansible-collections/community.general/pull/8791).
- pipx - support for versions of the command line tool ``pipx`` older than ``1.7.0`` is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/8793).
- pipx_info - support for versions of the command line tool ``pipx`` older than ``1.7.0`` is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/8793).

Bugfixes
--------

- gitlab_group_access_token - fix crash in check mode caused by attempted access to a newly created access token (https://github.com/ansible-collections/community.general/pull/8796).
- gitlab_project - fix ``container_expiration_policy`` not being applied when creating a new project (https://github.com/ansible-collections/community.general/pull/8790).
- gitlab_project - fix crash caused by old Gitlab projects not having a ``container_expiration_policy`` attribute (https://github.com/ansible-collections/community.general/pull/8790).
- gitlab_project_access_token - fix crash in check mode caused by attempted access to a newly created access token (https://github.com/ansible-collections/community.general/pull/8796).
- keycloak_realm_key - fix invalid usage of ``parent_id`` (https://github.com/ansible-collections/community.general/issues/7850, https://github.com/ansible-collections/community.general/pull/8823).
- keycloak_user_federation - fix key error when removing mappers during an update and new mappers are specified in the module args (https://github.com/ansible-collections/community.general/pull/8762).
- keycloak_user_federation - fix the ``UnboundLocalError`` that occurs when an ID is provided for a user federation mapper (https://github.com/ansible-collections/community.general/pull/8831).
- keycloak_user_federation - sort desired and after mapper list by name (analog to before mapper list) to minimize diff and make change detection more accurate (https://github.com/ansible-collections/community.general/pull/8761).
- proxmox inventory plugin - fixed a possible error on concatenating responses from proxmox. In case an API call unexpectedly returned an empty result, the inventory failed with a fatal error. Added check for empty response (https://github.com/ansible-collections/community.general/issues/8798, https://github.com/ansible-collections/community.general/pull/8794).

New Modules
-----------

- community.general.keycloak_userprofile - Allows managing Keycloak User Profiles.
- community.general.one_vnet - Manages OpenNebula virtual networks.

v9.3.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- cgroup_memory_recap, hipchat, jabber, log_plays, loganalytics, logentries, logstash, slack, splunk, sumologic, syslog_json callback plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8628).
- chef_databag, consul_kv, cyberarkpassword, dsv, etcd, filetree, hiera, onepassword, onepassword_doc, onepassword_raw, passwordstore, redis, shelvefile, tss lookup plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8626).
- chroot, funcd, incus, iocage, jail, lxc, lxd, qubes, zone connection plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8627).
- cobbler, linode, lxd, nmap, online, scaleway, stackpath_compute, virtualbox inventory plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8625).
- doas, dzdo, ksu, machinectl, pbrun, pfexec, pmrun, sesu, sudosu become plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8623).
- gconftool2 - make use of ``ModuleHelper`` features to simplify code (https://github.com/ansible-collections/community.general/pull/8711).
- gitlab_project - add option ``container_expiration_policy`` to schedule container registry cleanup (https://github.com/ansible-collections/community.general/pull/8674).
- gitlab_project - add option ``model_registry_access_level`` to disable model registry (https://github.com/ansible-collections/community.general/pull/8688).
- gitlab_project - add option ``pages_access_level`` to disable project pages (https://github.com/ansible-collections/community.general/pull/8688).
- gitlab_project - add option ``repository_access_level`` to disable project repository (https://github.com/ansible-collections/community.general/pull/8674).
- gitlab_project - add option ``service_desk_enabled`` to disable service desk (https://github.com/ansible-collections/community.general/pull/8688).
- locale_gen - add support for multiple locales (https://github.com/ansible-collections/community.general/issues/8677, https://github.com/ansible-collections/community.general/pull/8682).
- memcached, pickle, redis, yaml cache plugins - make sure that all options are typed (https://github.com/ansible-collections/community.general/pull/8624).
- opentelemetry callback plugin - fix default value for ``store_spans_in_file`` causing traces to be produced to a file named ``None`` (https://github.com/ansible-collections/community.general/issues/8566, https://github.com/ansible-collections/community.general/pull/8741).
- passwordstore lookup plugin - add the current user to the lockfile file name to address issues on multi-user systems (https://github.com/ansible-collections/community.general/pull/8689).
- pipx - add parameter ``suffix`` to module (https://github.com/ansible-collections/community.general/pull/8675, https://github.com/ansible-collections/community.general/issues/8656).
- pkgng - add option ``use_globs`` (default ``true``) to optionally disable glob patterns (https://github.com/ansible-collections/community.general/issues/8632, https://github.com/ansible-collections/community.general/pull/8633).
- proxmox inventory plugin - add new fact for LXC interface details (https://github.com/ansible-collections/community.general/pull/8713).
- redis, redis_info - add ``client_cert`` and ``client_key`` options to specify path to certificate for Redis authentication  (https://github.com/ansible-collections/community.general/pull/8654).

Bugfixes
--------

- gitlab_runner - fix ``paused`` parameter being ignored (https://github.com/ansible-collections/community.general/pull/8648).
- homebrew_cask - fix ``upgrade_all`` returns ``changed`` when nothing upgraded (https://github.com/ansible-collections/community.general/issues/8707, https://github.com/ansible-collections/community.general/pull/8708).
- keycloak_user_federation - get cleartext IDP ``clientSecret`` from full realm info to detect changes to it (https://github.com/ansible-collections/community.general/issues/8294, https://github.com/ansible-collections/community.general/pull/8735).
- keycloak_user_federation - remove existing user federation mappers if they are not present in the federation configuration and will not be updated (https://github.com/ansible-collections/community.general/issues/7169, https://github.com/ansible-collections/community.general/pull/8695).
- proxmox - fixed an issue where the new volume handling incorrectly converted ``null`` values into ``"None"`` strings (https://github.com/ansible-collections/community.general/pull/8646).
- proxmox - fixed an issue where volume strings where overwritten instead of appended to in the new ``build_volume()`` method (https://github.com/ansible-collections/community.general/pull/8646).
- proxmox - removed the forced conversion of non-string values to strings to be consistent with the module documentation (https://github.com/ansible-collections/community.general/pull/8646).

New Modules
-----------

- community.general.bootc_manage - Bootc Switch and Upgrade.
- community.general.homebrew_services - Services manager for Homebrew.
- community.general.keycloak_realm_keys_metadata_info - Allows obtaining Keycloak realm keys metadata via Keycloak API.

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
