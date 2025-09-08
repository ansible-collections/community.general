===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 10.0.0.

v11.2.1
=======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- Avoid deprecated functionality in ansible-core 2.20 (https://github.com/ansible-collections/community.general/pull/10687).
- apache2_module - check the ``cgi`` module restrictions only during activation (https://github.com/ansible-collections/community.general/pull/10423).
- composer - fix broken command lines (https://github.com/ansible-collections/community.general/issues/10662, https://github.com/ansible-collections/community.general/pull/10669).
- pacemaker_resource - fix ``resource_type`` parameter formatting (https://github.com/ansible-collections/community.general/issues/10426, https://github.com/ansible-collections/community.general/pull/10663).
- pids - prevent error when an empty string is provided for ``name`` (https://github.com/ansible-collections/community.general/issues/10672, https://github.com/ansible-collections/community.general/pull/10688).

v11.2.0
=======

Release Summary
---------------

Regular bugfix and features release.

Minor Changes
-------------

- apk - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/issues/10479, https://github.com/ansible-collections/community.general/pull/10520).
- bzr - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10523).
- capabilities - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10524).
- composer - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10525).
- django module utils - remove deprecated parameter ``_DjangoRunner`` call (https://github.com/ansible-collections/community.general/pull/10574).
- easy_install - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10526).
- imgadm - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10536).
- jenkins_plugin - install dependencies for specific version (https://github.com/ansible-collections/community.general/issue/4995, https://github.com/ansible-collections/community.general/pull/10346).
- keycloak_identity_provider – add support for ``fromUrl`` to automatically fetch OIDC endpoints from the well-known discovery URL, simplifying identity provider configuration (https://github.com/ansible-collections/community.general/pull/10527).
- keycloak_realm - add support for ``brute_force_strategy`` and ``max_temporary_lockouts`` (https://github.com/ansible-collections/community.general/issues/10412, https://github.com/ansible-collections/community.general/pull/10415).
- keycloak_realm - add support for client-related options and Oauth2 device (https://github.com/ansible-collections/community.general/pull/10538).
- logstash_plugin - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/issues/10479, https://github.com/ansible-collections/community.general/pull/10520).
- nagios - make parameter ``services`` a ``list`` instead of a ``str`` (https://github.com/ansible-collections/community.general/pull/10493).
- open_iscsi - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10599).
- pear - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10601).
- portage - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10602).
- riak - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10603).
- scaleway_* modules, scaleway inventory plugin - update available zones and API URLs (https://github.com/ansible-collections/community.general/issues/10383, https://github.com/ansible-collections/community.general/pull/10424).
- sensu_subscription - normalize quotes in the module output (https://github.com/ansible-collections/community.general/pull/10483).
- solaris_zone - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10604).
- swupd - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10605).
- tasks_only callback plugin - add ``result_format`` and ``pretty_results`` options similarly to the default callback (https://github.com/ansible-collections/community.general/pull/10422).
- timezone - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10612).
- urpmi - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10606).
- xbps - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10608).
- xfs_quota - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10609).

Deprecated Features
-------------------

- bearychat - module is deprecated and will be removed in community.general 12.0.0 (https://github.com/ansible-collections/community.general/issues/10514).
- cpanm - deprecate ``mode=compatibility``, ``mode=new`` should be used instead (https://github.com/ansible-collections/community.general/pull/10434).
- github_repo - deprecate ``force_defaults=true`` (https://github.com/ansible-collections/community.general/pull/10435).
- rocketchat - the default value for ``is_pre740``, currently ``true``, is deprecated and will change to ``false`` in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10490).

Bugfixes
--------

- jenkins_plugin - install latest compatible version instead of latest (https://github.com/ansible-collections/community.general/issues/854, https://github.com/ansible-collections/community.general/pull/10346).
- jenkins_plugin - separate Jenkins and external URL credentials (https://github.com/ansible-collections/community.general/issues/4419, https://github.com/ansible-collections/community.general/pull/10346).
- lvm_pv - properly detect SCSI or NVMe devices to rescan (https://github.com/ansible-collections/community.general/issues/10444, https://github.com/ansible-collections/community.general/pull/10596).

New Plugins
-----------

Lookup
~~~~~~

- community.general.binary_file - Read binary file and return it Base64 encoded.

New Modules
-----------

- community.general.lvm_pv_move_data - Move data between LVM Physical Volumes (PVs).
- community.general.pacemaker_info - Gather information about Pacemaker cluster.

v11.1.2
=======

Release Summary
---------------

Bugfix release.

Minor Changes
-------------

- gem - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- git_config_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_deploy_key - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_repo - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_webhook - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_webhook_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_branch - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_group_access_token - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_group_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_hook - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_instance_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_issue - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_label - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_merge_request - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_milestone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project_access_token - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- grove - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- hg - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew_cask - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew_tap - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- honeybadger_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- htpasswd - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- icinga2_host - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- influxdb_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ini_file - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipa_dnsrecord - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipa_dnszone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipa_service - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipbase_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipwcli_dns - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- irc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jabber - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jenkins_credential - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jenkins_job - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jenkins_script - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- keycloak_authz_authorization_scope - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_authz_permission - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_role - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_userprofile - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keyring - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- kibana_plugin - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- layman - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- ldap_attrs - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- ldap_inc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- librato_annotation - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- lldp - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- logentries - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- lxca_cmms - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- lxca_nodes - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- macports - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mail - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_alerts - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_group - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_policies - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_policies_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_tags - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_tenant - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- matrix - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mattermost - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- maven_artifact - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_dns_reload - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_zone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_zone_record - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mqtt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mssql_db - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mssql_script - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- netcup_dns - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- newrelic_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- nsupdate - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- oci_vcn - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_image_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_template - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_vnet - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- onepassword_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- oneview_fc_network_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- opendj_backendprop - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- ovh_monthly_billing - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pagerduty - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pagerduty_change - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pagerduty_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pam_limits - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pear - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pkgng - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pnpm - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- portage - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_org - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_org_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_user_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pubnub_blocks - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pushbullet - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pushover - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- redis_data - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- redis_data_incr - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- riak - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- rocketchat - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- rollbar_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- say - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- scaleway_database_backup - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sendgrid - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sensu_silence - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sorcery - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- ssh_config - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- statusio_maintenance - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- svr4pkg - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- swdepot - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- syslogger - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sysrc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- systemd_creds_decrypt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- systemd_creds_encrypt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- taiga_issue - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- twilio - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_aaa_group - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_ca_host_key_cert - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_dns_host - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_network_interface_address - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_proxy_auth_profile - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_proxy_exception - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_proxy_frontend - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- utm_proxy_location - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- vertica_configuration - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- vertica_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- vertica_role - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- xbps - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- yarn - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- zypper - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- zypper_repository - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).

Bugfixes
--------

- apk - fix check for empty/whitespace-only package names (https://github.com/ansible-collections/community.general/pull/10532).
- capabilities - using invalid path (symlink/directory/...) returned unrelated and incoherent error messages (https://github.com/ansible-collections/community.general/issues/5649, https://github.com/ansible-collections/community.general/pull/10455).
- doas become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/issues/9977, https://github.com/ansible-collections/community.general/pull/10537).
- json_query filter plugin - make compatible with lazy evaluation list and dictionary types of ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10539).
- machinectl become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/pull/10537).
- merge_variables lookup plugin - avoid deprecated functionality from ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10566).
- wsl connection plugin - avoid deprecated ansible-core paramiko import helper, import paramiko directly instead (https://github.com/ansible-collections/community.general/issues/10515, https://github.com/ansible-collections/community.general/pull/10531).

v11.1.1
=======

Release Summary
---------------

Bugfix release for the next Ansible 12 pre-release.

Minor Changes
-------------

- aerospike_migrations - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- airbrake_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bigpanda - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bootc_manage - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bower - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- btrfs_subvolume - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bundler - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- campfire - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- cargo - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- catapult - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- cisco_webex - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- consul_kv - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- consul_policy - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- copr - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- datadog_downtime - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- datadog_monitor - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dconf - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dimensiondata_network - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dimensiondata_vlan - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dnf_config_manager - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dnsmadeeasy - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dpkg_divert - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- easy_install - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- elasticsearch_plugin - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- facter - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- filesystem - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- sysrc - adjustments to the code (https://github.com/ansible-collections/community.general/pull/10417).

Bugfixes
--------

- apache2_module - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- apk - handle empty name strings properly (https://github.com/ansible-collections/community.general/issues/10441, https://github.com/ansible-collections/community.general/pull/10442).
- cronvar - fix crash on missing ``cron_file`` parent directories (https://github.com/ansible-collections/community.general/issues/10460, https://github.com/ansible-collections/community.general/pull/10461).
- cronvar - handle empty strings on ``value`` properly  (https://github.com/ansible-collections/community.general/issues/10439, https://github.com/ansible-collections/community.general/pull/10445).
- htpasswd - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- irc - pass hostname to ``wrap_socket()`` if ``use_tls=true`` and ``validate_certs=true`` (https://github.com/ansible-collections/community.general/issues/10472, https://github.com/ansible-collections/community.general/pull/10491).
- listen_port_facts - avoid crash when required commands are missing (https://github.com/ansible-collections/community.general/issues/10457, https://github.com/ansible-collections/community.general/pull/10458).
- syspatch - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- sysrc - fixes parsing with multi-line variables (https://github.com/ansible-collections/community.general/issues/10394, https://github.com/ansible-collections/community.general/pull/10417).
- sysupgrade - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- zypper_repository - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).

v11.1.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- cloudflare_dns - adds support for PTR records (https://github.com/ansible-collections/community.general/pull/10267).
- cloudflare_dns - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- cloudflare_dns - simplify validations and refactor some code, no functional changes (https://github.com/ansible-collections/community.general/pull/10269).
- crypttab - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- datadog_monitor - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- dense callback plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- gitlab_deploy_key - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_group_access_token - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_hook - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_project_access_token - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_runner - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- iocage inventory plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- ipa_group - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- jc filter plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- jenkins_build - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- jenkins_build_info - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- keycloak - add support for ``grant_type=client_credentials`` to all keycloak modules, so that specifying ``auth_client_id`` and ``auth_client_secret`` is sufficient for authentication (https://github.com/ansible-collections/community.general/pull/10231).
- keycloak module utils - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- logstash callback plugin - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- mail callback plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- nmcli - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- nmcli - simplify validations and refactor some code, no functional changes (https://github.com/ansible-collections/community.general/pull/10323).
- oneandone_firewall_policy - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- oneandone_load_balancer - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- oneandone_monitoring_policy - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- onepassword_info - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- osx_defaults - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- ovh_ip_loadbalancing_backend - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pacemaker_cluster - add ``state=maintenance`` for managing pacemaker maintenance mode (https://github.com/ansible-collections/community.general/issues/10200, https://github.com/ansible-collections/community.general/pull/10227).
- pacemaker_cluster - rename ``node`` to ``name`` and add ``node`` alias (https://github.com/ansible-collections/community.general/pull/10227).
- pacemaker_resource - enhance module by removing duplicative code (https://github.com/ansible-collections/community.general/pull/10227).
- packet_device - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pagerduty - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pingdom - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- python_runner module utils - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- rhevm - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- rocketchat - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- sensu_silence - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- sl_vm - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- urpmi - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- wsl connection plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- xattr - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- xen_orchestra inventory plugin - use f-strings instead of concatenation (https://github.com/ansible-collections/community.general/pull/10285).
- xfconf - minor adjustments the the code (https://github.com/ansible-collections/community.general/pull/10311).
- xml - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).

Deprecated Features
-------------------

- catapult - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/issues/10318, https://github.com/ansible-collections/community.general/pull/10329).
- pacemaker_cluster - the parameter ``state`` will become a required parameter in community.general 12.0.0 (https://github.com/ansible-collections/community.general/pull/10227).

Bugfixes
--------

- dependent lookup plugin - avoid deprecated ansible-core 2.19 functionality (https://github.com/ansible-collections/community.general/pull/10359).
- github_release - support multiple types of GitHub tokens; no longer failing when ``ghs_`` token type is provided (https://github.com/ansible-collections/community.general/issues/10338, https://github.com/ansible-collections/community.general/pull/10339).
- icinga2 inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- incus connection plugin - fix error handling to return more useful Ansible errors to the user (https://github.com/ansible-collections/community.general/issues/10344, https://github.com/ansible-collections/community.general/pull/10349).
- linode inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- logstash callback plugin - remove reference to Python 2 library (https://github.com/ansible-collections/community.general/pull/10345).

New Plugins
-----------

Callback
~~~~~~~~

- community.general.tasks_only - Only show tasks.

New Modules
-----------

- community.general.jenkins_credential - Manage Jenkins credentials and domains via API.

v11.0.0
=======

Release Summary
---------------

This is release 11.0.0 of ``community.general``, released on 2025-06-16.

Minor Changes
-------------

- CmdRunner module utils - the convenience method ``cmd_runner_fmt.as_fixed()`` now accepts multiple arguments as a list (https://github.com/ansible-collections/community.general/pull/9893).
- MH module utils - delegate ``debug`` to the underlying ``AnsibleModule`` instance or issues a warning if an attribute already exists with that name (https://github.com/ansible-collections/community.general/pull/9577).
- alternatives - add ``family`` parameter that allows to utilize the ``--family`` option available in RedHat version of update-alternatives (https://github.com/ansible-collections/community.general/issues/5060, https://github.com/ansible-collections/community.general/pull/9096).
- apache2_mod_proxy - better handling regexp extraction (https://github.com/ansible-collections/community.general/pull/9609).
- apache2_mod_proxy - change type of ``state`` to a list of strings. No change for the users (https://github.com/ansible-collections/community.general/pull/9600).
- apache2_mod_proxy - code simplification, no change in functionality (https://github.com/ansible-collections/community.general/pull/9457).
- apache2_mod_proxy - improve readability when using results from ``fecth_url()`` (https://github.com/ansible-collections/community.general/pull/9608).
- apache2_mod_proxy - refactor repeated code into method (https://github.com/ansible-collections/community.general/pull/9599).
- apache2_mod_proxy - remove unused parameter and code from ``Balancer`` constructor (https://github.com/ansible-collections/community.general/pull/9614).
- apache2_mod_proxy - simplified and improved string manipulation (https://github.com/ansible-collections/community.general/pull/9614).
- apache2_mod_proxy - use ``deps`` to handle dependencies (https://github.com/ansible-collections/community.general/pull/9612).
- apache2_module - added workaround for new PHP module name, from ``php7_module`` to ``php_module`` (https://github.com/ansible-collections/community.general/pull/9951).
- bitwarden lookup plugin - add new option ``collection_name`` to filter results by collection name, and new option ``result_count`` to validate number of results (https://github.com/ansible-collections/community.general/pull/9728).
- bitwarden lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- cargo - add ``features`` parameter to allow activating specific features when installing Rust packages (https://github.com/ansible-collections/community.general/pull/10198).
- cartesian lookup plugin - removed compatibility code for ansible-core < 2.14 (https://github.com/ansible-collections/community.general/pull/10160).
- cgroup_memory_recap callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- cgroup_memory_recap callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- chef_databag lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- chroot connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- chroot connection plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- chroot connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- cloud_init_data_facts - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- cloudflare_dns - add support for ``comment`` and ``tags`` (https://github.com/ansible-collections/community.general/pull/9132).
- cobbler inventory plugin - add ``connection_timeout`` option to specify the connection timeout to the cobbler server (https://github.com/ansible-collections/community.general/pull/11063).
- cobbler inventory plugin - add ``facts_level`` option to allow requesting fully rendered variables for Cobbler systems (https://github.com/ansible-collections/community.general/issues/9419, https://github.com/ansible-collections/community.general/pull/9975).
- cobbler inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- cobbler inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- cobbler inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- collection_version lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- consul_kv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- consul_token - fix idempotency when ``policies`` or ``roles`` are supplied by name (https://github.com/ansible-collections/community.general/issues/9841, https://github.com/ansible-collections/community.general/pull/9845).
- context_demo callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- context_demo callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- counter filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- counter_enabled callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- counter_enabled callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- cpanm - enable usage of option ``--with-recommends`` (https://github.com/ansible-collections/community.general/issues/9554, https://github.com/ansible-collections/community.general/pull/9555).
- cpanm - enable usage of option ``--with-suggests`` (https://github.com/ansible-collections/community.general/pull/9555).
- crc32 filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- credstash lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- cronvar - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- crypttab - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- cyberarkpassword lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- cyberarkpassword lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- default_without_diff callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dense callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dense callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- dependent lookup plugin - removed compatibility code for ansible-core < 2.14 (https://github.com/ansible-collections/community.general/pull/10160).
- dependent lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- deps module utils - add ``deps.clear()`` to clear out previously declared dependencies (https://github.com/ansible-collections/community.general/pull/9179).
- dict filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- dict_kv filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- dig lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- dig lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- diy callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- diy callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- dnstxt lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- dnstxt lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- doas become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- doas become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- dsv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- dzdo become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- dzdo become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- elastic callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- elastic callback plugin - instead of trying to extract the ansible-core version from task data, use ansible-core's actual version (https://github.com/ansible-collections/community.general/pull/10193).
- elastic callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- etcd lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- etcd3 lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- etcd3 lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- filetree lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- flattened lookup plugin - removed compatibility code for ansible-core < 2.14 (https://github.com/ansible-collections/community.general/pull/10160).
- from_csv filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- from_csv filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- from_ini filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- from_ini filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- funcd connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- funcd connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- git_config - remove redundant ``required=False`` from ``argument_spec`` (https://github.com/ansible-collections/community.general/pull/10177).
- github_app_access_token lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- github_key - add ``api_url`` parameter to support GitHub Enterprise Server installations (https://github.com/ansible-collections/community.general/pull/10191).
- gitlab_instance_variable - add support for ``raw`` variables suboption (https://github.com/ansible-collections/community.general/pull/9425).
- gitlab_project - add option ``build_timeout`` (https://github.com/ansible-collections/community.general/pull/9960).
- gitlab_project_members - extend choices parameter ``access_level`` by missing upstream valid value ``owner`` (https://github.com/ansible-collections/community.general/pull/9953).
- gitlab_runners inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- gitlab_runners inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- gitlab_runners inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- groupby_as_dict filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- hashids filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- hiera lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- homebrew - greatly speed up module when multiple packages are passed in the ``name`` option (https://github.com/ansible-collections/community.general/pull/9181).
- homebrew - remove duplicated package name validation (https://github.com/ansible-collections/community.general/pull/9076).
- hpilo_boot - add option to get an idempotent behavior while powering on server, resulting in success instead of failure when using ``state: boot_once`` option (https://github.com/ansible-collections/community.general/pull/9646).
- icinga2 inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- icinga2 inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- idrac_redfish_command, idrac_redfish_config, idrac_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- ilo_redfish_command, ilo_redfish_config, ilo_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- incus connection plugin - adds ``remote_user`` and ``incus_become_method`` parameters for allowing a non-root user to connect to an Incus instance (https://github.com/ansible-collections/community.general/pull/9743).
- incus connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- incus connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- ini_file - modify an inactive option also when there are spaces in front of the comment symbol (https://github.com/ansible-collections/community.general/pull/10102, https://github.com/ansible-collections/community.general/issues/8539).
- iocage connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- iocage connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- iocage inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- iocage inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- iocage inventory plugin - the new parameter ``hooks_results`` of the plugin is a list of files inside a jail that provide configuration parameters for the inventory. The inventory plugin reads the files from the jails and put the contents into the items of created variable ``iocage_hooks`` (https://github.com/ansible-collections/community.general/issues/9650, https://github.com/ansible-collections/community.general/pull/9651).
- iocage inventory plugin - the new parameter ``inventory_hostname_tag`` of the plugin provides the name of the tag in the C(iocage properties notes) that contains the jails alias. The new parameter ``inventory_hostname_required``, if enabled, makes the tag mandatory (https://github.com/ansible-collections/community.general/issues/10206, https://github.com/ansible-collections/community.general/pull/10207).
- iocage inventory plugin - the new parameter ``sudo`` of the plugin lets the command ``iocage list -l`` to run as root on the iocage host. This is needed to get the IPv4 of a running DHCP jail (https://github.com/ansible-collections/community.general/issues/9572, https://github.com/ansible-collections/community.general/pull/9573).
- iptables_state action plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- iptables_state action plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9318).
- iso_extract - adds ``password`` parameter that is passed to 7z (https://github.com/ansible-collections/community.general/pull/9159).
- jabber callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- jabber callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- jail connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- jail connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- jc filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- jira - adds ``client_cert`` and ``client_key`` parameters for supporting client certificate authentification when connecting to Jira (https://github.com/ansible-collections/community.general/pull/9753).
- jira - transition operation now has ``status_id`` to directly reference wanted transition (https://github.com/ansible-collections/community.general/pull/9602).
- json_query filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- keep_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- keycloak - add an action group for Keycloak modules to allow ``module_defaults`` to be set for Keycloak tasks (https://github.com/ansible-collections/community.general/pull/9284).
- keycloak module_utils - user groups can now be referenced by their name, like ``staff``, or their path, like ``/staff/engineering``. The path syntax allows users to reference subgroups, which is not possible otherwise (https://github.com/ansible-collections/community.general/pull/9898).
- keycloak_* modules - ``refresh_token`` parameter added. When multiple authentication parameters are provided (``token``, ``refresh_token``, and ``auth_username``/``auth_password``), modules will now automatically retry requests upon authentication errors (401), using in order the token, refresh token, and username/password (https://github.com/ansible-collections/community.general/pull/9494).
- keycloak_realm - remove ID requirement when creating a realm to allow Keycloak generating its own realm ID (https://github.com/ansible-collections/community.general/pull/9768).
- keycloak_user module - user groups can now be referenced by their name, like ``staff``, or their path, like ``/staff/engineering``. The path syntax allows users to reference subgroups, which is not possible otherwise (https://github.com/ansible-collections/community.general/pull/9898).
- keyring lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- known_hosts - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- ksu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- ksu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- lastpass lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- launchd - add ``plist`` option for services such as sshd, where the plist filename doesn't match the service name (https://github.com/ansible-collections/community.general/pull/9102).
- linode inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- linode inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- lists filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- lists_mergeby filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- lldp - adds ``multivalues`` parameter to control behavior when lldpctl outputs an attribute multiple times (https://github.com/ansible-collections/community.general/pull/9657).
- lmdb_kv lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- lmdb_kv lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- locale_gen - invert the logic to determine ``ubuntu_mode``, making it look first for ``/etc/locale.gen`` (set ``ubuntu_mode`` to ``False``) and only then looking for ``/var/lib/locales/supported.d/`` (set ``ubuntu_mode`` to ``True``) (https://github.com/ansible-collections/community.general/pull/9238, https://github.com/ansible-collections/community.general/issues/9131, https://github.com/ansible-collections/community.general/issues/8487).
- locale_gen - new return value ``mechanism`` to better express the semantics of the ``ubuntu_mode``, with the possible values being either ``glibc`` (``ubuntu_mode=False``) or ``ubuntu_legacy`` (``ubuntu_mode=True``) (https://github.com/ansible-collections/community.general/pull/9238).
- log_plays callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- log_plays callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- loganalytics callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- loganalytics callback plugin - instead of trying to extract the ansible-core version from task data, use ansible-core's actual version (https://github.com/ansible-collections/community.general/pull/10193).
- loganalytics callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- logdna callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- logdna callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- logentries callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- logentries callback plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- logentries callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- logstash callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- lvg - add ``remove_extra_pvs`` parameter to control if ansible should remove physical volumes which are not in the ``pvs`` parameter (https://github.com/ansible-collections/community.general/pull/9698).
- lxc connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lxc connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- lxd connection plugin - adds ``remote_user`` and ``lxd_become_method`` parameters for allowing a non-root user to connect to an LXD instance (https://github.com/ansible-collections/community.general/pull/9659).
- lxd connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lxd connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- lxd inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- lxd inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- lxd inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- machinectl become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- machinectl become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- mail callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- mail callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- manageiq_alert_profiles - improve handling of parameter requirements (https://github.com/ansible-collections/community.general/pull/9449).
- manifold lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- manifold lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- maven_artifact - removed compatibility code for ansible-core < 2.12 (https://github.com/ansible-collections/community.general/pull/10192).
- memcached cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- memcached cache plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9320).
- merge_variables lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- nmap inventory plugin - adds ``dns_servers`` option for specifying DNS servers for name resolution. Accepts hostnames or IP addresses in the same format as the ``exclude`` option (https://github.com/ansible-collections/community.general/pull/9849).
- nmap inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- nmap inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- nmap inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- nmcli - add ``sriov`` parameter that enables support for SR-IOV settings (https://github.com/ansible-collections/community.general/pull/9168).
- nmcli - add a option ``fail_over_mac`` (https://github.com/ansible-collections/community.general/issues/9570, https://github.com/ansible-collections/community.general/pull/9571).
- nmcli - add support for Infiniband MAC setting when ``type`` is ``infiniband`` (https://github.com/ansible-collections/community.general/pull/9962).
- nmcli - adds VRF support with new ``type`` value ``vrf`` and new ``slave_type`` value ``vrf`` as well as new ``table`` parameter (https://github.com/ansible-collections/community.general/pull/9658, https://github.com/ansible-collections/community.general/issues/8014).
- nmcli - adds ``autoconnect_priority`` and ``autoconnect_retries`` options to support autoconnect logic (https://github.com/ansible-collections/community.general/pull/10134).
- nrdp callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- nrdp callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- null callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- one_template - adds ``filter`` option for retrieving templates which are not owned by the user (https://github.com/ansible-collections/community.general/pull/9547, https://github.com/ansible-collections/community.general/issues/9278).
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
- onepassword lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- onepassword lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- onepassword_doc lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- onepassword_ssh_key - refactor to move code to lookup class (https://github.com/ansible-collections/community.general/pull/9633).
- online inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- online inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- opennebula inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- opennebula inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- opennebula inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- opentelemetry callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- opentelemetry callback plugin - instead of trying to extract the ansible-core version from task data, use ansible-core's actual version (https://github.com/ansible-collections/community.general/pull/10193).
- opentelemetry callback plugin - remove code handling Python versions prior to 3.7 (https://github.com/ansible-collections/community.general/pull/9482).
- opentelemetry callback plugin - remove code handling Python versions prior to 3.7 (https://github.com/ansible-collections/community.general/pull/9503).
- opentelemetry callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- pacemaker_cluster - remove unused code (https://github.com/ansible-collections/community.general/pull/9471).
- pacemaker_cluster - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/9471).
- pacemaker_resource - add maintenance mode support for handling resource creation and deletion (https://github.com/ansible-collections/community.general/issues/10180, https://github.com/ansible-collections/community.general/pull/10194).
- pacman_key - support verifying that keys are trusted and not expired (https://github.com/ansible-collections/community.general/issues/9949, https://github.com/ansible-collections/community.general/pull/9950).
- parted - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- passwordstore lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- pbrun become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pbrun become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- pfexec become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pfexec become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- pickle cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pipx - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9180).
- pipx - parameter ``name`` now accepts Python package specifiers (https://github.com/ansible-collections/community.general/issues/7815, https://github.com/ansible-collections/community.general/pull/10031).
- pipx module_utils - filtering application list by name now happens in the modules (https://github.com/ansible-collections/community.general/pull/10031).
- pipx_info - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9180).
- pipx_info - filtering application list by name now happens in the module  (https://github.com/ansible-collections/community.general/pull/10031).
- pmrun become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- pmrun become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- pulp_repo - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- puppet - improve parameter formatting, no impact to user (https://github.com/ansible-collections/community.general/pull/10014).
- qubes connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- qubes connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- random_mac filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- random_pet lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- redfish module utils - add ``REDFISH_COMMON_ARGUMENT_SPEC``, a corresponding ``redfish`` docs fragment, and support for its ``validate_certs``, ``ca_path``, and ``ciphers`` options (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- redfish module utils - removed compatibility code for ansible-core < 2.14 (https://github.com/ansible-collections/community.general/pull/10160).
- redfish_command - add ``PowerFullPowerCycle`` to power command options (https://github.com/ansible-collections/community.general/pull/9729).
- redfish_command - add ``update_custom_oem_header``, ``update_custom_oem_params``, and ``update_custom_oem_mime_type`` options (https://github.com/ansible-collections/community.general/pull/9123).
- redfish_command, redfish_config, redfish_info - add ``validate_certs`` and ``ca_path`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- redfish_config - add command ``SetPowerRestorePolicy`` to set the desired power state of the system when power is restored (https://github.com/ansible-collections/community.general/pull/9837).
- redfish_info - add command ``GetAccountServiceConfig`` to get full information about AccountService configuration (https://github.com/ansible-collections/community.general/pull/9403).
- redfish_info - add command ``GetPowerRestorePolicy`` to get the desired power state of the system when power is restored (https://github.com/ansible-collections/community.general/pull/9824).
- redfish_utils module utils - remove redundant code (https://github.com/ansible-collections/community.general/pull/9190).
- redhat_subscription - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- redis cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- redis cache plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- redis cache plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9320).
- redis lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- remove_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- replace_keys filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- revbitspss lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- reveal_ansible_type filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- rocketchat - fix duplicate JSON conversion for Rocket.Chat < 7.4.0 (https://github.com/ansible-collections/community.general/pull/9965).
- rocketchat - option ``is_pre740`` has been added to control the format of the payload. For Rocket.Chat 7.4.0 or newer, it must be set to ``false`` (https://github.com/ansible-collections/community.general/pull/9882).
- rpm_ostree_pkg - added the options ``apply_live`` (https://github.com/ansible-collections/community.general/pull/9167).
- rpm_ostree_pkg - added the return value ``needs_reboot`` (https://github.com/ansible-collections/community.general/pull/9167).
- run0 become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- saltstack connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- saltstack connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- say callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- say callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- scaleway inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- scaleway inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- scaleway inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- scaleway_lb - minor simplification in the code (https://github.com/ansible-collections/community.general/pull/9189).
- selective callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- selective callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- sesu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- sesu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- shelvefile lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- shutdown action plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- shutdown action plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- shutdown action plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9318).
- slack callback plugin - add ``http_agent`` option to enable the user to set a custom user agent for slack callback plugin (https://github.com/ansible-collections/community.general/issues/9813, https://github.com/ansible-collections/community.general/pull/9836).
- slack callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- slack callback plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- slack callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- snap - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9598).
- snap_alias - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9598).
- solaris_zone - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- sorcery - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- splunk callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- splunk callback plugin - instead of trying to extract the ansible-core version from task data, use ansible-core's actual version (https://github.com/ansible-collections/community.general/pull/10193).
- splunk callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- ssh_config - add ``dynamicforward`` option (https://github.com/ansible-collections/community.general/pull/9192).
- ssh_config - add ``other_options`` option (https://github.com/ansible-collections/community.general/issues/8053, https://github.com/ansible-collections/community.general/pull/9684).
- stackpath_compute inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- stackpath_compute inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- sudosu become plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- sudosu become plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9319).
- sumologic callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- sumologic callback plugin - instead of trying to extract the ansible-core version from task data, use ansible-core's actual version (https://github.com/ansible-collections/community.general/pull/10193).
- syslog_json callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- systemd_info - add wildcard expression support in ``unitname`` option (https://github.com/ansible-collections/community.general/pull/9821).
- systemd_info - extend support to timer units (https://github.com/ansible-collections/community.general/pull/9891).
- terraform - adds the ``no_color`` parameter, which suppresses or allows color codes in stdout from Terraform commands (https://github.com/ansible-collections/community.general/pull/10154).
- time filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- timestamp callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- timestamp callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- timezone - open file using ``open()`` as a context manager (https://github.com/ansible-collections/community.general/pull/9579).
- to_ini filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- to_ini filter plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- tss lookup plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- tss lookup plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9324).
- ufw - add support for ``vrrp`` protocol (https://github.com/ansible-collections/community.general/issues/9562, https://github.com/ansible-collections/community.general/pull/9582).
- unicode_normalize filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- unixy callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- unixy callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- version_sort filter plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9585).
- virtualbox inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- virtualbox inventory plugin - clean up string conversions (https://github.com/ansible-collections/community.general/pull/9379).
- virtualbox inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- vmadm - add new options ``flexible_disk_size`` and ``owner_uuid`` (https://github.com/ansible-collections/community.general/pull/9892).
- wdc_redfish_command, wdc_redfish_info - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- xbps - add ``root`` and ``repository`` options to enable bootstrapping new void installations (https://github.com/ansible-collections/community.general/pull/9174).
- xcc_redfish_command - add ``validate_certs``, ``ca_path``, and ``ciphers`` options to configure TLS/SSL (https://github.com/ansible-collections/community.general/issues/3686, https://github.com/ansible-collections/community.general/pull/9964).
- xen_orchestra inventory plugin - add ``use_vm_uuid`` and ``use_host_uuid`` boolean options to allow switching over to using VM/Xen name labels instead of UUIDs as item names (https://github.com/ansible-collections/community.general/pull/9787).
- xen_orchestra inventory plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- xen_orchestra inventory plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9323).
- xfconf - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9226).
- xfconf_info - add return value ``version`` (https://github.com/ansible-collections/community.general/pull/9226).
- xml - support adding value of children when creating with subnodes (https://github.com/ansible-collections/community.general/pull/8437).
- yaml cache plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- yaml callback plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9583).
- yaml callback plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9321).
- zone connection plugin - adjust standard preamble for Python 3 (https://github.com/ansible-collections/community.general/pull/9584).
- zone connection plugin - use f-strings instead of interpolations or ``format`` (https://github.com/ansible-collections/community.general/pull/9322).
- zypper - add ``quiet`` option (https://github.com/ansible-collections/community.general/pull/9270).
- zypper - add ``simple_errors`` option (https://github.com/ansible-collections/community.general/pull/9270).
- zypper - adds ``skip_post_errors`` that allows to skip RPM post-install errors (Zypper return code 107) (https://github.com/ansible-collections/community.general/issues/9972).

Deprecated Features
-------------------

- MH module utils - attribute ``debug`` definition in subclasses of MH is now deprecated, as that name will become a delegation to ``AnsibleModule`` in community.general 12.0.0, and any such attribute will be overridden by that delegation in that version (https://github.com/ansible-collections/community.general/pull/9577).
- atomic_container - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- atomic_host - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- atomic_image - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9487).
- facter - module is deprecated and will be removed in community.general 12.0.0, use ``community.general.facter_facts`` instead (https://github.com/ansible-collections/community.general/pull/9451).
- locale_gen - ``ubuntu_mode=True``, or ``mechanism=ubuntu_legacy`` is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9238).
- manifold lookup plugin - plugin is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/10028).
- opkg - deprecate value ``""`` for parameter ``force`` (https://github.com/ansible-collections/community.general/pull/9172).
- pipx module_utils - function ``make_process_list()`` is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10031).
- profitbricks - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_datacenter - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_nic - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_volume - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- profitbricks_volume_attachments - module is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/9733).
- pure module utils - the module utils is deprecated and will be removed from community.general 12.0.0. The modules using this were removed in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/9432).
- purestorage doc fragments - the doc fragment is deprecated and will be removed from community.general 12.0.0. The modules using this were removed in community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/9432).
- redfish_utils module utils - deprecate method ``RedfishUtils._init_session()`` (https://github.com/ansible-collections/community.general/pull/9190).
- sensu_check - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_client - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_handler - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_silence - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- sensu_subscription - module is deprecated and will be removed in community.general 13.0.0, use collection ``sensu.sensu_go`` instead (https://github.com/ansible-collections/community.general/pull/9483).
- slack - the default value ``auto`` of the ``prepend_hash`` option is deprecated and will change to ``never`` in community.general 12.0.0 (https://github.com/ansible-collections/community.general/pull/9443).
- stackpath_compute inventory plugin - plugin is deprecated and will be removed in community.general 11.0.0 (https://github.com/ansible-collections/community.general/pull/10026).
- yaml callback plugin - deprecate plugin in favor of ``result_format=yaml`` in plugin ``ansible.bulitin.default`` (https://github.com/ansible-collections/community.general/pull/9456).
- yaml callback plugin - the YAML callback plugin was deprecated for removal in community.general 13.0.0. Since it needs to use ansible-core internals since ansible-core 2.19 that are changing a lot, we will remove this plugin already from community.general 12.0.0 to ease the maintenance burden (https://github.com/ansible-collections/community.general/pull/10213).

Removed Features (previously deprecated)
----------------------------------------

- Dropped support for ansible-core 2.15. The collection now requires ansible-core 2.16 or newer. This means that on the controller, Python 3.10+ is required. On the target side, Python 2.7 and Python 3.6+ are supported (https://github.com/ansible-collections/community.general/pull/10160, https://github.com/ansible-collections/community.general/pull/10192).
- The Proxmox content (modules and plugins) has been moved to the `new collection community.proxmox <https://github.com/ansible-collections/community.proxmox>`__. Since community.general 11.0.0, these modules and plugins have been replaced by deprecated redirections to community.proxmox. You need to explicitly install community.proxmox, for example with ``ansible-galaxy collection install community.proxmox``, or by installing a new enough version of the Ansible community package. We suggest to update your roles and playbooks to use the new FQCNs as soon as possible to avoid getting deprecation messages (https://github.com/ansible-collections/community.general/pull/10110).
- apt_rpm - the ``present`` and ``installed`` states are no longer equivalent to ``latest``, but to ``present_not_latest`` (https://github.com/ansible-collections/community.general/pull/10126).
- clc_* modules and doc fragment - the modules were removed since CenturyLink Cloud services went EOL in September 2023 (https://github.com/ansible-collections/community.general/pull/10126).
- django_manage - the ``ack_venv_creation_deprecation`` option has been removed. It had no effect anymore anyway (https://github.com/ansible-collections/community.general/pull/10126).
- git_config - it is no longer allowed to use ``state=present`` with no value to read the config value. Use the ``community.general.git_config_info`` module instead (https://github.com/ansible-collections/community.general/pull/10126).
- git_config - the ``list_all`` option has been removed. Use the ``community.general.git_config_info`` module instead (https://github.com/ansible-collections/community.general/pull/10126).
- hipchat - the module was removed since the hipchat service has been discontinued and the self-hosted variant has been End of Life since 2020 (https://github.com/ansible-collections/community.general/pull/10126).
- manifold lookup plugin - the plugin was removed since the company was acquired in 2021 and service was ceased afterwards (https://github.com/ansible-collections/community.general/pull/10126).
- mh.mixins.deps module utils - this module utils has been removed. Use the ``deps`` module utils instead (https://github.com/ansible-collections/community.general/pull/10126).
- mh.mixins.vars module utils - this module utils has been removed. Use ``VarDict`` from the ``vardict`` module utils instead (https://github.com/ansible-collections/community.general/pull/10126).
- mh.module_helper module utils - ``AnsibleModule`` and ``VarsMixin`` are no longer provided (https://github.com/ansible-collections/community.general/pull/10126).
- mh.module_helper module utils - ``VarDict`` is now imported from the ``vardict`` module utils and no longer from the removed ``mh.mixins.vars`` module utils (https://github.com/ansible-collections/community.general/pull/10126).
- mh.module_helper module utils - the attributes ``use_old_vardict`` and ``mute_vardict_deprecation`` from ``ModuleHelper`` have been removed. We suggest to remove them from your modules if you no longer support community.general < 11.0.0 (https://github.com/ansible-collections/community.general/pull/10126).
- module_helper module utils - ``StateMixin``, ``DependencyCtxMgr``, ``VarMeta``, ``VarDict``, and ``VarsMixin`` are no longer provided (https://github.com/ansible-collections/community.general/pull/10126).
- pipx - module no longer supports ``pipx`` older than 1.7.0 (https://github.com/ansible-collections/community.general/pull/10137).
- pipx_info - module no longer supports ``pipx`` older than 1.7.0 (https://github.com/ansible-collections/community.general/pull/10137).
- profitbrick* modules - the modules were removed since the supporting library is unsupported since 2021 (https://github.com/ansible-collections/community.general/pull/10126).
- redfish_utils module utils - the ``_init_session`` method has been removed (https://github.com/ansible-collections/community.general/pull/10126).
- stackpath_compute inventory plugin - the plugin was removed since the company and the service were sunset in June 2024 (https://github.com/ansible-collections/community.general/pull/10126).

Security Fixes
--------------

- keycloak_authentication - API calls did not properly set the ``priority`` during update resulting in incorrectly sorted authentication flows. This apparently only affects Keycloak 25 or newer (https://github.com/ansible-collections/community.general/pull/9263).
- keycloak_client - Sanitize ``saml.encryption.private.key`` so it does not show in the logs (https://github.com/ansible-collections/community.general/pull/9621).

Bugfixes
--------

- apache2_mod_proxy - make compatible with Python 3 (https://github.com/ansible-collections/community.general/pull/9762).
- apache2_mod_proxy - passing the cluster's page as referer for the member's pages. This makes the module actually work again for halfway modern Apache versions. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 (https://github.com/ansible-collections/community.general/pull/9762).
- cloudflare_dns - fix crash when deleting a DNS record or when updating a record with ``solo=true`` (https://github.com/ansible-collections/community.general/issues/9652, https://github.com/ansible-collections/community.general/pull/9649).
- cloudlare_dns - handle exhausted response stream in case of HTTP errors to show nice error message to the user (https://github.com/ansible-collections/community.general/issues/9782, https://github.com/ansible-collections/community.general/pull/9818).
- cobbler_system - fix bug with Cobbler >= 3.4.0 caused by giving more than 2 positional arguments to ``CobblerXMLRPCInterface.get_system_handle()`` (https://github.com/ansible-collections/community.general/issues/8506, https://github.com/ansible-collections/community.general/pull/10145).
- cobbler_system - update minimum version number to avoid wrong comparisons that happen in some cases using LooseVersion class which results in TypeError (https://github.com/ansible-collections/community.general/issues/8506, https://github.com/ansible-collections/community.general/pull/10145, https://github.com/ansible-collections/community.general/pull/10178).
- dependent look plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- dig lookup plugin - correctly handle ``NoNameserver`` exception (https://github.com/ansible-collections/community.general/pull/9363, https://github.com/ansible-collections/community.general/issues/9362).
- diy callback plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- dnf_config_manager - fix hanging when prompting to import GPG keys (https://github.com/ansible-collections/community.general/pull/9124, https://github.com/ansible-collections/community.general/issues/8830).
- dnf_config_manager - forces locale to ``C`` before module starts. If the locale was set to non-English, the output of the ``dnf config-manager`` could not be parsed (https://github.com/ansible-collections/community.general/pull/9157, https://github.com/ansible-collections/community.general/issues/9046).
- dnf_versionlock - add support for dnf5 (https://github.com/ansible-collections/community.general/issues/9556).
- elasticsearch_plugin - fix ``ERROR: D is not a recognized option`` issue when configuring proxy settings (https://github.com/ansible-collections/community.general/pull/9774, https://github.com/ansible-collections/community.general/issues/9773).
- flatpak - force the locale language to ``C`` when running the flatpak command (https://github.com/ansible-collections/community.general/pull/9187, https://github.com/ansible-collections/community.general/issues/8883).
- gio_mime - fix command line when determining version of ``gio`` (https://github.com/ansible-collections/community.general/pull/9171, https://github.com/ansible-collections/community.general/issues/9158).
- github_deploy_key - check that key really exists on 422 to avoid masking other errors (https://github.com/ansible-collections/community.general/issues/6718, https://github.com/ansible-collections/community.general/pull/10011).
- github_key - in check mode, a faulty call to ```datetime.strftime(...)``` was being made which generated an exception (https://github.com/ansible-collections/community.general/issues/9185).
- gitlab_group_access_token, gitlab_project_access_token - fix handling of group and project access tokens for changes in GitLab 17.10 (https://github.com/ansible-collections/community.general/pull/10196).
- hashids and unicode_normalize filter plugins - avoid deprecated ``AnsibleFilterTypeError`` on ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/9992).
- homebrew - emit a useful error message if ``brew info`` reports a package tap is ``null`` (https://github.com/ansible-collections/community.general/pull/10013, https://github.com/ansible-collections/community.general/issues/10012).
- homebrew - fix crash when package names include tap (https://github.com/ansible-collections/community.general/issues/9777, https://github.com/ansible-collections/community.general/pull/9803).
- homebrew - fix incorrect handling of aliased homebrew modules when the alias is requested (https://github.com/ansible-collections/community.general/pull/9255, https://github.com/ansible-collections/community.general/issues/9240).
- homebrew - fix incorrect handling of homebrew modules when a tap is requested (https://github.com/ansible-collections/community.general/pull/9546, https://github.com/ansible-collections/community.general/issues/9533).
- homebrew - make package name parsing more resilient (https://github.com/ansible-collections/community.general/pull/9665, https://github.com/ansible-collections/community.general/issues/9641).
- homebrew_cask - allow ``+`` symbol in Homebrew cask name validation regex (https://github.com/ansible-collections/community.general/pull/9128).
- homebrew_cask - handle unusual brew version strings (https://github.com/ansible-collections/community.general/issues/8432, https://github.com/ansible-collections/community.general/pull/9881).
- htpasswd - report changes when file permissions are adjusted (https://github.com/ansible-collections/community.general/issues/9485, https://github.com/ansible-collections/community.general/pull/9490).
- iocage inventory plugin - the plugin parses the IP4 tab of the jails list and put the elements into the new variable ``iocage_ip4_dict``. In multiple interface format the variable ``iocage_ip4`` keeps the comma-separated list of IP4 (https://github.com/ansible-collections/community.general/issues/9538).
- ipa_host - module revoked existing host certificates even if ``user_certificate`` was not given (https://github.com/ansible-collections/community.general/pull/9694).
- java_cert - the module no longer fails if the optional parameters ``pkcs12_alias`` and ``cert_alias`` are not provided (https://github.com/ansible-collections/community.general/pull/9970).
- kdeconfig - allow option values beginning with a dash (https://github.com/ansible-collections/community.general/issues/10127, https://github.com/ansible-collections/community.general/pull/10128).
- keycloak - update more than 10 sub-groups (https://github.com/ansible-collections/community.general/issues/9690, https://github.com/ansible-collections/community.general/pull/9692).
- keycloak module utils - replaces missing return in get_role_composites method which caused it to return None instead of composite roles (https://github.com/ansible-collections/community.general/issues/9678, https://github.com/ansible-collections/community.general/pull/9691).
- keycloak_authentication - fix authentification config duplication for Keycloak < 26.2.0 (https://github.com/ansible-collections/community.general/pull/9987).
- keycloak_client - fix and improve existing tests. The module showed a diff without actual changes, solved by improving the ``normalise_cr()`` function (https://github.com/ansible-collections/community.general/pull/9644).
- keycloak_client - fix diff by removing code that turns the attributes dict which contains additional settings into a list (https://github.com/ansible-collections/community.general/pull/9077).
- keycloak_client - fix the idempotency regression by normalizing the Keycloak response for ``after_client`` (https://github.com/ansible-collections/community.general/issues/9905, https://github.com/ansible-collections/community.general/pull/9976).
- keycloak_client - in check mode, detect whether the lists in before client (for example redirect URI list) contain items that the lists in the desired client do not contain (https://github.com/ansible-collections/community.general/pull/9739).
- keycloak_clientscope - fix diff and ``end_state`` by removing the code that turns the attributes dict, which contains additional config items, into a list (https://github.com/ansible-collections/community.general/pull/9082).
- keycloak_clientscope_type - sort the default and optional clientscope lists to improve the diff (https://github.com/ansible-collections/community.general/pull/9202).
- keycloak_user_rolemapping - fix ``--diff`` mode (https://github.com/ansible-collections/community.general/issues/10067, https://github.com/ansible-collections/community.general/pull/10075).
- lldp - fix crash caused by certain lldpctl output where an attribute is defined as branch and leaf (https://github.com/ansible-collections/community.general/pull/9657).
- nmcli - enable changing only the order of DNS servers or search suffixes (https://github.com/ansible-collections/community.general/issues/8724, https://github.com/ansible-collections/community.general/pull/9880).
- onepassword_doc lookup plugin - ensure that 1Password Connect support also works for this plugin (https://github.com/ansible-collections/community.general/pull/9625).
- passwordstore lookup plugin - fix subkey creation even when ``create=false`` (https://github.com/ansible-collections/community.general/issues/9105, https://github.com/ansible-collections/community.general/pull/9106).
- pickle cache plugin - avoid extra JSON serialization with ansible-core >= 2.19 (https://github.com/ansible-collections/community.general/pull/10136).
- pipx - honor option ``global`` when ``state=latest`` (https://github.com/ansible-collections/community.general/pull/9623).
- qubes connection plugin - fix the printing of debug information (https://github.com/ansible-collections/community.general/pull/9334).
- redfish_utils module utils - Fix ``VerifyBiosAttributes`` command on multi system resource nodes (https://github.com/ansible-collections/community.general/pull/9234).
- redfish_utils module utils - remove undocumented default applytime (https://github.com/ansible-collections/community.general/pull/9114).
- redhat_subscription - do not try to unsubscribe (i.e. remove subscriptions)
  when unregistering a system: newer versions of subscription-manager, as
  available in EL 10 and Fedora 41+, do not support entitlements anymore, and
  thus unsubscribing will fail
  (https://github.com/ansible-collections/community.general/pull/9578).
- redhat_subscription - use the "enable_content" option (when available) when
  registering using D-Bus, to ensure that subscription-manager enables the
  content on registration; this is particular important on EL 10+ and Fedora
  41+
  (https://github.com/ansible-collections/community.general/pull/9778).
- reveal_ansible_type filter plugin and ansible_type test plugin - make compatible with ansible-core's Data Tagging feature (https://github.com/ansible-collections/community.general/pull/9833).
- rundeck_acl_policy - ensure that project ACLs are sent to the correct endpoint (https://github.com/ansible-collections/community.general/pull/10097).
- slack - fail if Slack API response is not OK with error message (https://github.com/ansible-collections/community.general/pull/9198).
- sudoers - display stdout and stderr raised while failed validation (https://github.com/ansible-collections/community.general/issues/9674, https://github.com/ansible-collections/community.general/pull/9871).
- sysrc - no longer always reporting ``changed=true`` when ``state=absent``. This fixes the method ``exists()`` (https://github.com/ansible-collections/community.general/issues/10004, https://github.com/ansible-collections/community.general/pull/10005).
- sysrc - split the output of ``sysrc -e -a`` on the first ``=`` only (https://github.com/ansible-collections/community.general/issues/10120, https://github.com/ansible-collections/community.general/pull/10121).
- xml - ensure file descriptor is closed (https://github.com/ansible-collections/community.general/pull/9695).
- yaml callback plugin - adjust to latest changes in ansible-core devel (https://github.com/ansible-collections/community.general/pull/10212).
- yaml callback plugin - use ansible-core internals to avoid breakage with Data Tagging (https://github.com/ansible-collections/community.general/pull/9833).
- yaml callback plugin - when using ansible-core 2.19.0b2 or newer, uses a new utility provided by ansible-core. This allows us to remove all hacks and vendored code that was part of the plugin for ansible-core versions with Data Tagging so far (https://github.com/ansible-collections/community.general/pull/10242).
- zfs - fix handling of multi-line values of user-defined ZFS properties (https://github.com/ansible-collections/community.general/pull/6264).
- zfs_facts - parameter ``type`` now accepts multple values as documented (https://github.com/ansible-collections/community.general/issues/5909, https://github.com/ansible-collections/community.general/pull/9697).
- zypper_repository - make compatible with Python 3.12+ (https://github.com/ansible-collections/community.general/issues/10222, https://github.com/ansible-collections/community.general/pull/10223).
- zypper_repository - use ``metalink`` attribute to identify repositories without ``<url/>`` element (https://github.com/ansible-collections/community.general/issues/10224, https://github.com/ansible-collections/community.general/pull/10225).

Known Issues
------------

- reveal_ansible_type filter plugin and ansible_type test plugin - note that ansible-core's Data Tagging feature implements new aliases, such as ``_AnsibleTaggedStr`` for ``str``, ``_AnsibleTaggedInt`` for ``int``, and ``_AnsibleTaggedFloat`` for ``float`` (https://github.com/ansible-collections/community.general/pull/9833).

New Plugins
-----------

Callback
~~~~~~~~

- community.general.print_task - Prints playbook task snippet to job output.

Connection
~~~~~~~~~~

- community.general.wsl - Run tasks in WSL distribution using wsl.exe CLI via SSH.

Filter
~~~~~~

- community.general.accumulate - Produce a list of accumulated sums of the input list contents.
- community.general.json_diff - Create a JSON patch by comparing two JSON files.
- community.general.json_patch - Apply a JSON-Patch (RFC 6902) operation to an object.
- community.general.json_patch_recipe - Apply JSON-Patch (RFC 6902) operations to an object.
- community.general.to_prettytable - Format a list of dictionaries as an ASCII table.

Inventory
~~~~~~~~~

- community.general.iocage - iocage inventory source.

Lookup
~~~~~~

- community.general.onepassword_ssh_key - Fetch SSH keys stored in 1Password.

New Modules
-----------

- community.general.android_sdk - Manages Android SDK packages.
- community.general.decompress - Decompresses compressed files.
- community.general.ldap_inc - Use the Modify-Increment LDAP V3 feature to increment an attribute value.
- community.general.lvm_pv - Manage LVM Physical Volumes.
- community.general.pacemaker_resource - Manage pacemaker resources.
- community.general.systemd_creds_decrypt - C(systemd)'s C(systemd-creds decrypt) plugin.
- community.general.systemd_creds_encrypt - C(systemd)'s C(systemd-creds encrypt) plugin.
- community.general.systemd_info - Gather C(systemd) unit info.
- community.general.xdg_mime - Set default handler for MIME types, for applications using XDG tools.
- community.general.zpool - Manage ZFS zpools.
