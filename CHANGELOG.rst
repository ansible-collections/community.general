===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 11.0.0.

v12.3.0
=======

Release Summary
---------------

Regular feature and bugfix release.

Minor Changes
-------------

- alicloud_ecs module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- android_sdk - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- archive - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- bitbucket_pipeline_known_host - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- chroot connection plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- cobbler inventory plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- copr - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- cronvar - simplify handling unknown exceptions (https://github.com/ansible-collections/community.general/pull/11340).
- cronvar - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- crypttab - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- elasticsearch_plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- gitlab_group - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- gitlab_issue - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- gitlab_merge_request - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- gitlab_project - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- gunicorn - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- htpasswd - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- idrac_redfish_info - add multiple manager support to ``GetManagerAttributes`` command (https://github.com/ansible-collections/community.general/pull/11294).
- imc_rest - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- incus connection plugin - improve code readability (https://github.com/ansible-collections/community.general/pull/11346).
- incus connection plugin - simplify regular expression matching commands (https://github.com/ansible-collections/community.general/pull/11347).
- ini_file - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- interfaces_file - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- iptables_state - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- jail connection plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- jenkins_credential - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- jenkins_plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- jenkins_script - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- kdeconfig - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- known_hosts module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- layman - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- linode - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- linode inventory plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- listen_ports_facts - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- locale_gen - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- logentries callback plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- lvm_pv - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11343).
- lxc connection plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- lxd inventory plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- lxd module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- manageiq module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- manageiq_alert_profiles - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- modprobe - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- mssql_db - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- nagios - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- netcup_dns - support diff mode (https://github.com/ansible-collections/community.general/pull/11376).
- nmcli - add idempotency check (https://github.com/ansible-collections/community.general/pull/11114).
- nmcli - add support for IPv6 routing rules (https://github.com/ansible-collections/community.general/issues/7094, https://github.com/ansible-collections/community.general/pull/11413).
- nosh - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- nsupdate - add support for server FQDN and the GSS-TSIG key algorithm (https://github.com/ansible-collections/community.general/issues/5730, https://github.com/ansible-collections/community.general/pull/11425).
- nsupdate modules plugin - replace aliased errors with proper Python error (https://github.com/ansible-collections/community.general/pull/11391).
- oci_utils module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- omapi_host - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- one_image - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- one_image_info - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- one_service - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- one_vm - move ``import`` statemetns to the top of the file (https://github.com/ansible-collections/community.general/pull/11396).
- one_vm - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- opennebula inventory plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- pam_limits - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- pamd - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- parted - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- pmem - simplify text tests without using regular expression (https://github.com/ansible-collections/community.general/pull/11388).
- pubnub_blocks - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- pulp_repo - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- read_csv - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- redfish_utils module utils - adds support of ``@Redfish.Settings`` in ``ComputerSystem`` attributes for ``set_boot_override`` function (https://github.com/ansible-collections/community.general/issues/11297, https://github.com/ansible-collections/community.general/pull/11322).
- redhat_subscription - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- rhsm_repository - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- runit - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- scaleway_ip - added ``project`` parameter (https://github.com/ansible-collections/community.general/issues/11367, https://github.com/ansible-collections/community.general/pull/11368).
- scaleway_security_group - added ``project`` parameter (https://github.com/ansible-collections/community.general/issues/11364, https://github.com/ansible-collections/community.general/pull/11366).
- sensu_check - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- sensu_client - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- sensu_handler - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- sensu_subscription - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- seport - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- serverless - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- slackpkg - refactor function ``query_packages()`` (https://github.com/ansible-collections/community.general/pull/11390).
- solaris_zone - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- sorcery - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- spotinst_aws_elastigroup - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- sudoers - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- svc - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- timestamp callback plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- timezone - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- univention_umc module utils - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- wakeonlan - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- wsl connection plugin - add option ``wsl_remote_ssh_shell_type``. Support PowerShell in addition to cmd as the Windows shell (https://github.com/ansible-collections/community.general/issues/11307, https://github.com/ansible-collections/community.general/pull/11308).
- wsl connection plugin - replace aliased errors with proper Python error (https://github.com/ansible-collections/community.general/pull/11391).
- wsl connection plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- xfs_quota - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- yaml cache plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- zone connection plugin - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11341).
- zypper - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).
- zypper_repository - update to Python 3.7 idioms (https://github.com/ansible-collections/community.general/pull/11344).

Bugfixes
--------

- cloudflare_dns - also allow ``flag=128`` for CAA records (https://github.com/ansible-collections/community.general/issues/11355, https://github.com/ansible-collections/community.general/pull/11377).
- gem - add compatibility with Ruby 4 rubygems (https://github.com/ansible-collections/community.general/issues/11397, https://github.com/ansible-collections/community.general/pull/11442).
- incus connection plugin - fix parsing of commands for Windows, enforcing a ``\`` after the drive letter and colon symbol (https://github.com/ansible-collections/community.general/pull/11347).
- keycloak_client - fix idempotency bug caused by ``null`` client attribute value differences for non-existing client attributes (https://github.com/ansible-collections/community.general/issues/11443, https://github.com/ansible-collections/community.general/pull/11444).
- logstash_plugin - fix argument order when using ``version`` parameter. The plugin name must come after options like ``--version`` for the ``logstash-plugin`` CLI to work correctly (https://github.com/ansible-collections/community.general/issues/10745, https://github.com/ansible-collections/community.general/pull/11440).
- pmem - fix test for invalid data input (https://github.com/ansible-collections/community.general/pull/11388).

New Plugins
-----------

Filter
~~~~~~

- community.general.to_toml - Convert variable to TOML string.

v12.2.0
=======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- btrfs module utils - make execution of external commands safer by passing arguments as list (https://github.com/ansible-collections/community.general/pull/11240).
- deps module utils - change the internal representaion of dependency state (https://github.com/ansible-collections/community.general/pull/11242).
- keycloak_userprofile - add support for ``selector`` option (https://github.com/ansible-collections/community.general/pull/11309).
- keycloak_userprofile - add support for additional user profile attribute-validations available in Keycloak (https://github.com/ansible-collections/community.general/issues/9048, https://github.com/ansible-collections/community.general/pull/11285).
- lxc_container - refactor function ``create_script``, using ``subprocess.Popen()``, to a new module_utils ``_lxc`` (https://github.com/ansible-collections/community.general/pull/11204).
- lxc_container - use ``tempfile.TemporaryDirectory()`` instead of ``mkdtemp()`` (https://github.com/ansible-collections/community.general/pull/11323).
- monit - add ``monit_version`` return value also when the module has succeeded (https://github.com/ansible-collections/community.general/pull/11255).
- monit - use ``Enum`` to represent the possible states (https://github.com/ansible-collections/community.general/pull/11245).
- nmcli module - add ``vxlan_parent`` option required for multicast ``vxlan_remote`` addresses; add ``vxlan`` to list of bridgeable devices (https://github.com/ansible-collections/community.general/pull/11182).
- scaleway inventory plugin - added support for ``SCW_PROFILE`` environment variable for the ``scw_profile`` option (https://github.com/ansible-collections/community.general/issues/11310, https://github.com/ansible-collections/community.general/pull/11311).
- scaleway module utils - added ``scw_profile`` parameter with ``SCW_PROFILE`` environment variable support (https://github.com/ansible-collections/community.general/issues/11313, https://github.com/ansible-collections/community.general/pull/11314).

Deprecated Features
-------------------

- All module utils, plugin utils, and doc fragments will be made **private** in community.general 13.0.0. This means that they will no longer be part of the public API of the collection, and can have breaking changes even in bugfix releases. If you depend on importing code from the module or plugin utils, or use one of the doc fragments, please `comment in the issue to discuss this <https://github.com/ansible-collections/community.general/issues/11312>`__. Note that this does not affect any use of community.general in task files, roles, or playbooks (https://github.com/ansible-collections/community.general/issues/11312, https://github.com/ansible-collections/community.general/pull/11320).

Bugfixes
--------

- apk - fix ``packages`` return value for apk-tools >= 3 (Alpine 3.23) (https://github.com/ansible-collections/community.general/issues/11264).
- iptables_state - refactor code to avoid writing unnecessary temporary files (https://github.com/ansible-collections/community.general/pull/11258).
- keycloak_realm - fixed crash in ``sanitize_cr()`` when ``realmrep`` was ``None`` (https://github.com/ansible-collections/community.general/pull/11260).
- keycloak_user_rolemapping module - fixed crash when assigning roles to users without an existing role (https://github.com/ansible-collections/community.general/issues/10960, https://github.com/ansible-collections/community.general/pull/11256).
- listen_ports_facts - fix handling of empty PID lists when ``command=ss`` (https://github.com/ansible-collections/community.general/pull/11332).
- monit - add delay of 0.5 seconds after state change and check for status (https://github.com/ansible-collections/community.general/pull/11255).
- monit - internal state was not reflecting when operation is "pending" in ``monit`` (https://github.com/ansible-collections/community.general/pull/11245).

New Modules
-----------

- community.general.ip2location_info - Retrieve IP geolocation information of a host's IP address.
- community.general.sssd_info - Check SSSD domain status using D-Bus.

v12.1.0
=======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- The last code included in the collection that was licensed under the PSF 2.0 license was removed form the collection. This means that now all code is either GPLv3+ licensed, MIT licensed, or BSD-2-clause licensed (https://github.com/ansible-collections/community.general/pull/11232).
- _mount module utils - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- _stormssh module utils - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- a_module test plugin - add proper parameter checking and type hints (https://github.com/ansible-collections/community.general/pull/11167).
- aerospike_migrations - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- aix_filesystem - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- ali_instance - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- ansible_type plugin utils - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- ansible_type test plugin - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- apk - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- apt_rpm - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- apt_rpm - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- atomic_container - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- atomic_container modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- atomic_host - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- atomic_image - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- atomic_image modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- awall - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- beadm - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- bigpanda - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- binary_file lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- bitbucket module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- bitbucket_access_key modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- bitbucket_pipeline_key_pair modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- bitbucket_pipeline_known_host modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- bitbucket_pipeline_variable modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- chef_databag lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- chroot connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- circonus_annotation - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- cloudflare_dns - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- cmd_runner module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- cobbler inventory plugin - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- cobbler_sync - remove conditional code handling SSL for unsupported versions of Python (https://github.com/ansible-collections/community.general/pull/11078).
- cobbler_sync - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11105).
- cobbler_system - remove conditional code handling SSL for unsupported versions of Python (https://github.com/ansible-collections/community.general/pull/11078).
- cobbler_system - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11105).
- collection_version lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- composer - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- consul_kv lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- counter filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- credstash lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- cronvar - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- crypttab - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- csv module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- csv module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- cyberarkpassword lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- database module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- database module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- datadog_event - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- datadog_monitor - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- dconf - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- dependent lookup plugin - improve templating of strings (https://github.com/ansible-collections/community.general/pull/11189).
- dependent lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- deps module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- dig lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- dimensiondata_network - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- dimensiondata_network modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- dnf_config_manager - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- dnstxt lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- dsv lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- elastic callback plugin - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- etcd3 lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- exceptions module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- filesize - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11104).
- filesize - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- flatpak - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- flatpak_remote - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- fqdn_valid test plugin - add proper parameter checking, and add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- from_csv filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- from_ini filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- gandi_livedns_api module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- github_app_access_token lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- gitlab_group_access_token - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- gitlab_group_members - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- gitlab_project_access_token - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- gitlab_project_members - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- gitlab_runner - allow maximum timeout to be disabled by passing ``0`` to ``maximum_timeout``  (https://github.com/ansible-collections/community.general/pull/11174).
- gitlab_runners inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- haproxy - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- hashids filter - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- hashids filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- hg - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- hg - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- hpilo_info - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- hpilo_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- htpasswd - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- hwc_ecs_instance - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- hwc_utils module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- hwc_utils module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- hwc_vpc_port - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- ibm_sa_utils module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- icinga2 inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- icinga2_host - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- identity.keycloak.keycloak module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- idrac_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- idrac_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- idrac_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- idrac_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- idrac_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- idrac_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- idrac_redfish_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- idrac_redfish_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- ilo_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- ilo_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- ilo_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- ilo_redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- imc_rest modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- incus connection plugin - add support for Windows virtual machines (https://github.com/ansible-collections/community.general/pull/11199).
- influxdb_query - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- influxdb_user - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- influxdb_user - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- influxdb_write - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- iocage inventory plugin - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- ip_netns - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11104).
- ip_netns - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11105).
- ip_netns - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- ipa module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- ipa module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- ipa_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_dnsrecord - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_dnszone - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_group - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_hbacrule - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_host - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_hostgroup - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_otpconfig - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_otptoken - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_pwpolicy - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_pwpolicy - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- ipa_role - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_service - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_subca - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11104).
- ipa_sudocmd - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_sudocmdgroup - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_sudorule - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_user - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- ipa_vault - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- iptables_state action plugin - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- iso_customize - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- jail connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- jc filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- jenkins_job - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- jenkins_job_info - remove conditional code handling SSL for unsupported versions of Python (https://github.com/ansible-collections/community.general/pull/11078).
- jenkins_plugin - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- jenkins_plugin - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- jenkins_plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- jenkins_plugin modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- jenkins_script - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- jira - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11104).
- jira - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- jira - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- json_query filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- keycloak module utils - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- keycloak module_utils - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- keycloak_authentication - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_client_rolemapping - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_component - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_realm - add ``webAuthnPolicyPasswordlessPasskeysEnabled`` parameter (https://github.com/ansible-collections/community.general/pull/11197).
- keycloak_realm_key - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_realm_rolemapping - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_user_rolemapping - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keycloak_userprofile - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- keys_filter plugin_utils plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- keys_filter.py plugin utils - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- known_hosts module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- layman - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- ldap module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- ldap_attrs - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- ldap_entry - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- ldap_inc - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- ldap_search - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11104).
- ldap_search - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- linode inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- listen_ports_facts - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- listen_ports_facts - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- lmdb_kv lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- locale_gen - extend the search for available locales to include ``/usr/local/share/i18n/SUPPORTED`` in Debian and Ubuntu systems (https://github.com/ansible-collections/community.general/issues/10964, https://github.com/ansible-collections/community.general/pull/11046).
- logentries - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- lxc connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- lxd connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- lxd inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- lxd module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- lxd module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- lxd_container - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- macports - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- mail - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- maven_artifact - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- merge_variables - extend type detection failure message to allow users for easier failure debugging (https://github.com/ansible-collections/community.general/pull/11107).
- merge_variables lookup plugin - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- modprobe - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- net_tools.pritunl.api module utils - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- nmap inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- nmcli - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- nmcli - fix comparison of type (https://github.com/ansible-collections/community.general/pull/11121).
- nmcli modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- nomad_job - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- nomad_job - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- nomad_job_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- nomad_token - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- nosh - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- ocapi_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- ocapi_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- ocapi_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- ocapi_utils module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- oci_utils module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- oci_utils module utils - improve templating of strings (https://github.com/ansible-collections/community.general/pull/11189).
- oneandone_firewall_policy - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- oneandone_load_balancer - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- oneandone_monitoring_policy - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- oneandone_private_network - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- oneandone_server - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11231).
- oneandone_server modules - mark ``%`` templating as ``noqa`` (https://github.com/ansible-collections/community.general/pull/11223).
- onepassword lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- onepassword_info - execute external commands using Ansible construct (https://github.com/ansible-collections/community.general/pull/11193).
- onepassword_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- onepassword_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- oneview module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- online inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- opennebula inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- opentelemetry callback plugin - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- osx_defaults - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- packet_device - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11231).
- packet_device modules - mark ``%`` templating as ``noqa`` (https://github.com/ansible-collections/community.general/pull/11223).
- packet_ip_subnet - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- packet_project - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- packet_sshkey - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- packet_volume - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- packet_volume - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- pamd - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- parted - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- passwordstore lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- pear - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- pids - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- pids - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- portage - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- pritunl_org - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- pritunl_org_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- pritunl_user - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- pritunl_user_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- pushbullet modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- read_csv - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- redfish_config - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- redfish_utils module utils - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- redfish_utils module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- redhat_subscription - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- redhat_subscription - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- redis cache plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- redis lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- revbitspss lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- rhevm - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- riak - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- rundeck module utils - improve handling the return value ``exception``. It now contains the full stack trace of the exception, while the message is included in ``msg`` (https://github.com/ansible-collections/community.general/pull/11149).
- scaleway inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- scaleway_user_data modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- selinux_permissive - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- sensu_check - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- sensu_silence - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- sensu_silence modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- sensu_subscription - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- sensu_subscription - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- shelvefile lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- shutdown action plugin - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- shutdown action plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- slack - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- slackpkg - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- snap - improve templating of strings (https://github.com/ansible-collections/community.general/pull/11189).
- snmp_facts - simplify and improve code using standard Ansible validations (https://github.com/ansible-collections/community.general/pull/11148).
- solaris_zone - execute external commands using Ansible construct (https://github.com/ansible-collections/community.general/pull/11192).
- solaris_zone - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- spectrum_model_attrs - convert ``%`` templating to f-string (https://github.com/ansible-collections/community.general/pull/11229).
- statusio_maintenance - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- sudoers - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- svc - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- svr4pkg - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- swupd - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- to_ini filter plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- tss lookup plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- univention_umc module utils - update code to Python 3 (https://github.com/ansible-collections/community.general/pull/11122).
- unsafe.py plugin utils - add type hints (https://github.com/ansible-collections/community.general/pull/11167).
- urpmi - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- utm_aaa_group - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_aaa_group_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_ca_host_key_cert - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_ca_host_key_cert_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_dns_host - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_network_interface_address - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_network_interface_address_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_auth_profile - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_exception - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_frontend - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_frontend_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_location - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_proxy_location_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- utm_utils module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- utm_utils module utils - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11112).
- vertica_configuration - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- vertica_configuration - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- vertica_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- vertica_role - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- vertica_role - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- vertica_schema - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- vertica_schema - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- vertica_schema - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- vertica_user - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- vertica_user - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- vertica_user - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11097).
- virtualbox inventory plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- vmadm - in case of failure, the module no longer returns the stderr output as ``exception``, but instead as ``stderr``. Other information (``stdout``, ``rc``) is now also returned (https://github.com/ansible-collections/community.general/pull/11149).
- vmadm - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11102).
- wakeonlan - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11098).
- wdc_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- wdc_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- wdc_redfish_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- wdc_redfish_info - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- wsl connection plugin - adjust variable name for integration tests (https://github.com/ansible-collections/community.general/pull/11190).
- wsl connection plugin - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- wsl connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).
- xbps - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- xbps - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- xcc_redfish_command - fix cases of unused variables in loops (https://github.com/ansible-collections/community.general/pull/11115).
- xcc_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11110).
- xcc_redfish_command - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/1114).
- xenserver module utils - improve code by using native Python construct (https://github.com/ansible-collections/community.general/pull/11215).
- xenserver module utils - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- xenserver_guest modules - replace ``%`` templating with f-strings or ``format()`` (https://github.com/ansible-collections/community.general/pull/11223).
- xml - remove redundant conversions to unicode (https://github.com/ansible-collections/community.general/pull/11106).
- xml - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- yum_versionlock - remove redundant conversion to unicode in command output (https://github.com/ansible-collections/community.general/pull/11093).
- zfs - simplify return of boolean values in functions (https://github.com/ansible-collections/community.general/pull/11119).
- zone connection plugin - use ``raise ... from ...`` when passing on exceptions (https://github.com/ansible-collections/community.general/pull/11095).

Deprecated Features
-------------------

- cloud module utils - this module utils is not used by community.general and will thus be removed from community.general 13.0.0. If you are using it from another collection, please copy it over (https://github.com/ansible-collections/community.general/pull/11205).
- database module utils - this module utils is not used by community.general and will thus be removed from community.general 13.0.0. If you are using it from another collection, please copy it over (https://github.com/ansible-collections/community.general/pull/11205).
- dconf - deprecate fallback mechanism when ``gi.repository`` is not available; fallback will be removed in community.general 15.0.0 (https://github.com/ansible-collections/community.general/pull/11088).
- known_hosts module utils - this module utils is not used by community.general and will thus be removed from community.general 13.0.0. If you are using it from another collection, please copy it over (https://github.com/ansible-collections/community.general/pull/11205).
- layman - ClearLinux was made EOL in July 2025.; the module will be removed from community.general 15.0.0 (https://github.com/ansible-collections/community.general/pull/11087).
- layman - Gentoo deprecated ``layman`` in mid-2023; the module will be removed from community.general 14.0.0 (https://github.com/ansible-collections/community.general/pull/11070).
- pushbullet - module relies on Python package supporting Python 3.2 only; the module will be removed from community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/11224).
- saslprep module utils - this module utils is not used by community.general and will thus be removed from community.general 13.0.0. If you are using it from another collection, please copy it over (https://github.com/ansible-collections/community.general/pull/11205).
- spotinst_aws_elastigroup - module relies on Python package supporting Python 2.7 only; the module will be removed from community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/11069).

Bugfixes
--------

- _filelock module utils - add type hints. Fix bug if ``set_lock()`` is called with ``lock_timeout=None`` (https://github.com/ansible-collections/community.general/pull/11222).
- aix_filesystem - remove compatibility code for ancient Python versions (https://github.com/ansible-collections/community.general/pull/11232).
- ansible_type plugin utils - avoid potential concatenation of non-strings when ``alias`` has non-string values (https://github.com/ansible-collections/community.general/pull/11167).
- ansible_type test plugin - fix parameter checking (https://github.com/ansible-collections/community.general/pull/11167).
- cobbler_system - compare the version as a float which is the type returned by the Cobbler API (https://github.com/ansible-collections/community.general/issues/11044).
- datetime module utils - fix bug in ``fromtimestamp()`` that caused the function to crash. This function is not used in community.general (https://github.com/ansible-collections/community.general/pull/11206).
- gitlab module utils - add type hints. Pass API version to python-gitlab as string and not as integer (https://github.com/ansible-collections/community.general/pull/11222).
- homebrew_service - slightly refactor code (https://github.com/ansible-collections/community.general/pull/11168).
- ipinfoio_facts - fix handling of HTTP errors consulting the service (https://github.com/ansible-collections/community.general/pull/11145).
- keys_filter.py plugin utils - fixed requirements check so that other sequences than lists and strings are checked, and corrected broken formatting during error reporting (https://github.com/ansible-collections/community.general/pull/11167).
- mas - parse CLI output correctly when listing installed apps with mas 3.0.0+ (https://github.com/ansible-collections/community.general/pull/11179).
- pam_limits - remove ``%`` templating no longer used in f-string (https://github.com/ansible-collections/community.general/pull/11229).
- xcc_redfish_command - fix templating of dictionary keys as list (https://github.com/ansible-collections/community.general/pull/11144).
- zfs - mark change correctly when updating properties whose current value differs, even if they already have a non-default value (https://github.com/ansible-collections/community.general/issues/11019, https://github.com/ansible-collections/community.general/pull/11172).

New Modules
-----------

- community.general.file_remove - Remove files matching a pattern from a directory.
- community.general.lxd_storage_pool_info - Retrieve information about LXD storage pools.
- community.general.lxd_storage_volume_info - Retrieve information about LXD storage volumes.

v12.0.1
=======

Release Summary
---------------

Bugfix release for inclusion in Ansible 13.0.0rc1.

Minor Changes
-------------

- datetime module utils - remove code for unsupported Python version (https://github.com/ansible-collections/community.general/pull/11048).
- dnsimple_info - use Ansible construct to validate parameters (https://github.com/ansible-collections/community.general/pull/11052).
- infinity - consolidate double and triple whitespaces (https://github.com/ansible-collections/community.general/pull/11029).
- ipa_otptoken - consolidate double and triple whitespaces (https://github.com/ansible-collections/community.general/pull/11029).
- irc - use proper boolean value in loops (https://github.com/ansible-collections/community.general/pull/11076).
- jenkins_node - remove code for unsupported Python version (https://github.com/ansible-collections/community.general/pull/11048).
- opendj_backendprop - use Ansible construct to perform check for external commands (https://github.com/ansible-collections/community.general/pull/11072).
- rhevm - consolidate double and triple whitespaces (https://github.com/ansible-collections/community.general/pull/11029).
- slack - consolidate double and triple whitespaces (https://github.com/ansible-collections/community.general/pull/11029).
- tss lookup plugin - fixed ``AccessTokenAuthorizer`` initialization to include ``base_url`` parameter for proper token authentication (https://github.com/ansible-collections/community.general/pull/11031).
- zfs_facts - use Ansible construct to check result of external command (https://github.com/ansible-collections/community.general/pull/11054).

Bugfixes
--------

- _filelock module utils - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- aerospike_migrations - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- aix_lvol - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ali_instance - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- ali_instance - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ali_instance_info - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- apt_rpm - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- apt_rpm - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- btrfs module utils - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- btrfs module utils - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- btrfs_subvolume - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- btrfs_subvolume - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- chef_databag lookup plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- consul - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- consul_kv lookup plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- cronvar - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- discord - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- dnf_versionlock - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- dnsmadeeasy - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- dpkg_divert - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- elastic callback plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- filesystem - avoid false positive change detection on XFS resize due to unusable slack space (https://github.com/ansible-collections/community.general/pull/11033).
- gitlab module utils - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- gitlab_branch - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- gitlab_group_members - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- gitlab_issue - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- gitlab_merge_request - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- gitlab_project - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- gitlab_project_members - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- gitlab_protected_branch - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- gitlab_user - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- haproxy - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- homebrew - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- homebrew_services - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- hpilo_boot - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- infinity - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ini_file - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- interfaces_file - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ipa_group - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ipa_otptoken - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- ipa_vault - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ipmi_boot - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- jenkins_build - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- jenkins_build_info - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- jenkins_credential - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- jenkins_plugin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- jenkins_plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- json_patch filter plugin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- kea_command - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- keycloak_authz_permission - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- keycloak_clientscope_type - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- keycloak_component - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- keycloak_realm_key - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- keycloak_user_execute_actions_email - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- keycloak_user_federation - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- keycloak_userprofile - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- launchd - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- linode inventory plugin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- listen_ports_facts - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- listen_ports_facts - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- logentries callback plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- lxc_container - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- lxd_container - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- manageiq_alert_profiles - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- manageiq_provider - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- manageiq_tenant - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- matrix - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- maven_artifact - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- memset_memstore_info - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- memset_server_info - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- memset_zone - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- module_helper module utils - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- monit - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- netcup_dns - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- nmcli - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- nomad_job - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- nosh - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- npm - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- odbc - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- one_host - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- one_image - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- one_service - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- one_template - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- one_vm - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- one_vm - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- one_vnet - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- oneandone module utils - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- onepassword_info - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- online inventory plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- opendj_backendprop - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- opennebula module utils - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- opentelemetry callback plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- ovh_monthly_billing - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- pamd - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- pkgin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- portinstall - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- pulp_repo - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- redfish_utils module utils - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- redhat_subscription - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- redhat_subscription - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- redis_data_incr - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- rhevm - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- scaleway module utils - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- scaleway_sshkey - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- sensu_check - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- simpleinit_msb - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- sorcery - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- spectrum_model_attrs - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- spotinst_aws_elastigroup - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- svc - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- syslog_json callback plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- terraform - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- timestamp callback plugin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- timezone - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- to_* time filter plugins - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- to_prettytable filter plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- vmadm - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- wsl connection plugin - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- wsl connection plugin - rename variable to fix type checking (https://github.com/ansible-collections/community.general/pull/11030).
- xen_orchestra inventory plugin - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- xenserver module utils - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- xenserver_guest - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).
- xenserver_guest - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- xfs_quota - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- xml - improve Python code by removing unnecessary variables (https://github.com/ansible-collections/community.general/pull/11049).
- zypper_repository - improve Python code (https://github.com/ansible-collections/community.general/pull/11043).

v12.0.0
=======

Release Summary
---------------

This is release 12.0.0 of ``community.general``, released on 2025-11-03.

Minor Changes
-------------

- Modernize code for Python 3.7+. This includes code reformatting, and adding new checks to CI, including a type checker (mypy). Most of the code does not have type hints yet, but now it is possible to add typing hints and have these validated (https://github.com/ansible-collections/community.general/pull/10285, https://github.com/ansible-collections/community.general/pull/10886, https://github.com/ansible-collections/community.general/pull/10891, https://github.com/ansible-collections/community.general/pull/10892, https://github.com/ansible-collections/community.general/pull/10897, https://github.com/ansible-collections/community.general/pull/10899, https://github.com/ansible-collections/community.general/pull/10902, https://github.com/ansible-collections/community.general/pull/10903, https://github.com/ansible-collections/community.general/pull/10904, https://github.com/ansible-collections/community.general/pull/10907, https://github.com/ansible-collections/community.general/pull/10908, https://github.com/ansible-collections/community.general/pull/10909, https://github.com/ansible-collections/community.general/pull/10939, https://github.com/ansible-collections/community.general/pull/10940, https://github.com/ansible-collections/community.general/pull/10941, https://github.com/ansible-collections/community.general/pull/10942, https://github.com/ansible-collections/community.general/pull/10945, https://github.com/ansible-collections/community.general/pull/10947, https://github.com/ansible-collections/community.general/pull/10958, https://github.com/ansible-collections/community.general/pull/10959, https://github.com/ansible-collections/community.general/pull/10968, https://github.com/ansible-collections/community.general/pull/10969, https://github.com/ansible-collections/community.general/pull/10970, https://github.com/ansible-collections/community.general/pull/10971, https://github.com/ansible-collections/community.general/pull/10973, https://github.com/ansible-collections/community.general/pull/10974, https://github.com/ansible-collections/community.general/pull/10975, https://github.com/ansible-collections/community.general/pull/10976, https://github.com/ansible-collections/community.general/pull/10977, https://github.com/ansible-collections/community.general/pull/10978, https://github.com/ansible-collections/community.general/pull/10979, https://github.com/ansible-collections/community.general/pull/10980, https://github.com/ansible-collections/community.general/pull/10981, https://github.com/ansible-collections/community.general/pull/10992, https://github.com/ansible-collections/community.general/pull/10993, https://github.com/ansible-collections/community.general/pull/10997, https://github.com/ansible-collections/community.general/pull/10999, https://github.com/ansible-collections/community.general/pull/11015, https://github.com/ansible-collections/community.general/pull/11016, https://github.com/ansible-collections/community.general/pull/11017).
- aerospike_migrations - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- airbrake_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- android_sdk - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- apk - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/issues/10479, https://github.com/ansible-collections/community.general/pull/10520).
- bigpanda - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bootc_manage - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bower - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- btrfs_subvolume - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bundler - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- bzr - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10523).
- campfire - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- capabilities - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10524).
- cargo - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- catapult - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- cisco_webex - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- cloudflare_dns - adds support for PTR records (https://github.com/ansible-collections/community.general/pull/10267).
- cloudflare_dns - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- cloudflare_dns - simplify validations and refactor some code, no functional changes (https://github.com/ansible-collections/community.general/pull/10269).
- composer - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10525).
- consul_kv - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- consul_policy - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- copr - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- crypttab - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- datadog_downtime - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- datadog_monitor - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- datadog_monitor - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dconf - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dimensiondata_network - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dimensiondata_vlan - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- django module utils - remove deprecated parameter ``_DjangoRunner`` call (https://github.com/ansible-collections/community.general/pull/10574).
- django module utils - simplify/consolidate the common settings for the command line (https://github.com/ansible-collections/community.general/pull/10684).
- django_check - rename parameter ``database`` to ``databases``, add alias for compatibility (https://github.com/ansible-collections/community.general/pull/10700).
- django_check - simplify/consolidate the common settings for the command line (https://github.com/ansible-collections/community.general/pull/10684).
- django_createcachetable - simplify/consolidate the common settings for the command line (https://github.com/ansible-collections/community.general/pull/10684).
- dnf_config_manager - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dnsmadeeasy - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- dpkg_divert - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- easy_install - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- easy_install - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10526).
- elasticsearch_plugin - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- elasticsearch_plugin - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- facter - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- filesize - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- filesystem - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10494).
- filetree - add ``exclude`` option (https://github.com/ansible-collections/community.general/issues/10936, https://github.com/ansible-collections/community.general/pull/10936).
- gem - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- git_config_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_app_access_token lookup plugin - add support for GitHub Enterprise Server (https://github.com/ansible-collections/community.general/issues/10879, https://github.com/ansible-collections/community.general/pull/10880).
- github_app_access_token lookup plugin - support both ``jwt`` and ``pyjwt`` to avoid conflict with other modules requirements (https://github.com/ansible-collections/community.general/issues/10299).
- github_deploy_key - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_repo - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_webhook - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- github_webhook_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_branch - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_deploy_key - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_group_access_token - add ``planner`` access level (https://github.com/ansible-collections/community.general/pull/10679).
- gitlab_group_access_token - add missing scopes (https://github.com/ansible-collections/community.general/pull/10785).
- gitlab_group_access_token - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_group_access_token - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_group_variable - add ``description`` option (https://github.com/ansible-collections/community.general/pull/10812).
- gitlab_group_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_group_variable - support masked-and-hidden variables (https://github.com/ansible-collections/community.general/pull/10787).
- gitlab_hook - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_hook - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_instance_variable - add ``description`` option (https://github.com/ansible-collections/community.general/pull/10812).
- gitlab_instance_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_issue - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_label - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10711).
- gitlab_label - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_merge_request - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_milestone - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10711).
- gitlab_milestone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project_access_token - add ``planner`` access level (https://github.com/ansible-collections/community.general/pull/10679).
- gitlab_project_access_token - add missing scopes (https://github.com/ansible-collections/community.general/pull/10785).
- gitlab_project_access_token - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- gitlab_project_access_token - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project_variable - add ``description`` option (https://github.com/ansible-collections/community.general/pull/10812, https://github.com/ansible-collections/community.general/issues/8584, https://github.com/ansible-collections/community.general/issues/10809).
- gitlab_project_variable - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- gitlab_project_variable - support masked-and-hidden variables (https://github.com/ansible-collections/community.general/pull/10787).
- gitlab_protected_branch - add ``allow_force_push``, ``code_owner_approval_required`` (https://github.com/ansible-collections/community.general/pull/10795, https://github.com/ansible-collections/community.general/issues/6432, https://github.com/ansible-collections/community.general/issues/10289, https://github.com/ansible-collections/community.general/issues/10765).
- gitlab_protected_branch - update protected branches if possible instead of recreating them (https://github.com/ansible-collections/community.general/pull/10795).
- gitlab_runner - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- grove - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- hg - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew_cask - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- homebrew_tap - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- honeybadger_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- htpasswd - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- icinga2_host - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- imgadm - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10536).
- influxdb_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ini_file - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- iocage inventory plugin - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- ipa_dnsrecord - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipa_dnszone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipa_group - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- ipa_host - add ``userclass`` and ``locality`` parameters (https://github.com/ansible-collections/community.general/pull/10935).
- ipa_host - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10711).
- ipa_service - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- ipbase_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- iptables_state - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- ipwcli_dns - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- irc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jabber - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- java_keystore - remove redundant function (https://github.com/ansible-collections/community.general/pull/10905).
- jenkins_build - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- jenkins_build_info - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- jenkins_credential - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jenkins_job - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- jenkins_plugin - install dependencies for specific version (https://github.com/ansible-collections/community.general/issue/4995, https://github.com/ansible-collections/community.general/pull/10346).
- jenkins_script - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10505).
- keycloak - add support for ``grant_type=client_credentials`` to all keycloak modules, so that specifying ``auth_client_id`` and ``auth_client_secret`` is sufficient for authentication (https://github.com/ansible-collections/community.general/pull/10231).
- keycloak module utils - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- keycloak_authz_authorization_scope - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_authz_permission - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_client - add idempotent support for ``optional_client_scopes`` and ``optional_client_scopes``, and ensure consistent change detection between check mode and live run (https://github.com/ansible-collections/community.general/issues/5495, https://github.com/ansible-collections/community.general/pull/10842).
- keycloak_identity_provider – add support for ``fromUrl`` to automatically fetch OIDC endpoints from the well-known discovery URL, simplifying identity provider configuration (https://github.com/ansible-collections/community.general/pull/10527).
- keycloak_realm - add support for WebAuthn policy configuration options, including both regular and passwordless WebAuthn policies (https://github.com/ansible-collections/community.general/pull/10791).
- keycloak_realm - add support for ``brute_force_strategy`` and ``max_temporary_lockouts`` (https://github.com/ansible-collections/community.general/issues/10412, https://github.com/ansible-collections/community.general/pull/10415).
- keycloak_realm - add support for client-related options and Oauth2 device (https://github.com/ansible-collections/community.general/pull/10538).
- keycloak_role - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keycloak_user - return user created boolean flag (https://github.com/ansible-collections/community.general/pull/10950).
- keycloak_userprofile - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- keyring - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- kibana_plugin - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- layman - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- ldap_attrs - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- ldap_inc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- librato_annotation - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- linode module utils - remove redundant code for ancient versions of Ansible (https://github.com/ansible-collections/community.general/pull/10906).
- lldp - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- logentries - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- logstash callback plugin - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- logstash_plugin - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/issues/10479, https://github.com/ansible-collections/community.general/pull/10520).
- lvg_rename - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10711).
- lxca_cmms - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- lxca_nodes - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- macports - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mail - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- manageiq_alert_profiles - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- manageiq_alerts - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_group - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- manageiq_group - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_policies - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_policies_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_tags - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- manageiq_tenant - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- manageiq_tenant - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- matrix - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mattermost - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- maven_artifact - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_dns_reload - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_zone - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- memset_zone_record - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mqtt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mssql_db - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- mssql_db - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- mssql_script - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- nagios - make parameter ``services`` a ``list`` instead of a ``str`` (https://github.com/ansible-collections/community.general/pull/10493).
- netcup_dns - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- newrelic_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- nmcli - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- nmcli - simplify validations and refactor some code, no functional changes (https://github.com/ansible-collections/community.general/pull/10323).
- npm - improve parameter validation using Ansible construct (https://github.com/ansible-collections/community.general/pull/10983).
- nsupdate - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10507).
- oci_vcn - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_image_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_template - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- one_vm - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10712).
- one_vnet - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- oneandone_firewall_policy - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- oneandone_load_balancer - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- oneandone_monitoring_policy - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- onepassword_info - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- onepassword_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- oneview_fc_network_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- open_iscsi - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10599).
- openbsd_pkg - add ``autoremove`` parameter to remove unused dependencies (https://github.com/ansible-collections/community.general/pull/10705).
- openbsd_pkg - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- opendj_backendprop - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- osx_defaults - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- ovh_ip_loadbalancing_backend - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- ovh_monthly_billing - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pacemaker_cluster - add ``state=maintenance`` for managing pacemaker maintenance mode (https://github.com/ansible-collections/community.general/issues/10200, https://github.com/ansible-collections/community.general/pull/10227).
- pacemaker_cluster - rename ``node`` to ``name`` and add ``node`` alias (https://github.com/ansible-collections/community.general/pull/10227).
- pacemaker_resource - add ``state=cleanup`` for cleaning up pacemaker resources (https://github.com/ansible-collections/community.general/pull/10413)
- pacemaker_resource - add ``state=cloned`` for cloning pacemaker resources or groups (https://github.com/ansible-collections/community.general/issues/10322, https://github.com/ansible-collections/community.general/pull/10665).
- pacemaker_resource - enhance module by removing duplicative code (https://github.com/ansible-collections/community.general/pull/10227).
- pacemaker_resource - the parameter ``name`` is no longer a required parameter in community.general 11.3.0 (https://github.com/ansible-collections/community.general/pull/10413)
- packet_device - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pagerduty - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pagerduty - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pagerduty_change - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pagerduty_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pam_limits - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- parted - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10642).
- pear - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pear - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10601).
- pingdom - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- pipx module_utils - use ``PIPX_USE_EMOJI`` to disable emojis in the output of ``pipx`` 1.8.0 (https://github.com/ansible-collections/community.general/pull/10874).
- pkgng - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pnpm - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- portage - add a ``changed_deps`` option (https://github.com/ansible-collections/community.general/pull/11023).
- portage - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- portage - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10602).
- pritunl_org - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_org_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_user - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pritunl_user_info - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pubnub_blocks - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pushbullet - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- pushover - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- python_runner module utils - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- random_string lookup plugin - allow to specify seed while generating random string (https://github.com/ansible-collections/community.general/issues/5362, https://github.com/ansible-collections/community.general/pull/10710).
- redis_data - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- redis_data_incr - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- rhevm - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- riak - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- riak - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10603).
- rocketchat - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- rocketchat - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- rollbar_deployment - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- say - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- scaleway modules - add a ``scaleway`` group to use ``module_defaults`` (https://github.com/ansible-collections/community.general/pull/10647).
- scaleway_* modules, scaleway inventory plugin - update available zones and API URLs (https://github.com/ansible-collections/community.general/issues/10383, https://github.com/ansible-collections/community.general/pull/10424).
- scaleway_container - add a ``cpu_limit`` argument (https://github.com/ansible-collections/community.general/pull/10646).
- scaleway_database_backup - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sendgrid - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sensu_silence - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- sensu_silence - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sensu_subscription - normalize quotes in the module output (https://github.com/ansible-collections/community.general/pull/10483).
- sl_vm - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- solaris_zone - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10604).
- sorcery - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- ssh_config - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- statusio_maintenance - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- svr4pkg - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- swdepot - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- swupd - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10605).
- syslogger - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- sysrc - adjustments to the code (https://github.com/ansible-collections/community.general/pull/10417).
- sysrc - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- systemd_creds_decrypt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- systemd_creds_encrypt - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10512).
- taiga_issue - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- tasks_only callback plugin - add ``result_format`` and ``pretty_results`` options similarly to the default callback (https://github.com/ansible-collections/community.general/pull/10422).
- terraform - minor refactor to improve readability (https://github.com/ansible-collections/community.general/pull/10711).
- timezone - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10612).
- twilio - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- ufw - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- urpmi - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- urpmi - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10606).
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
- xattr - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- xbps - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- xbps - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10608).
- xenserver module utils - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10769).
- xenserver_facts - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- xfconf - minor adjustments the the code (https://github.com/ansible-collections/community.general/pull/10311).
- xfs_quota - using safer mechanism to run external command (https://github.com/ansible-collections/community.general/pull/10609).
- xml - remove redundant brackets in conditionals, no functional changes (https://github.com/ansible-collections/community.general/pull/10328).
- yarn - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- zfs_facts - minor refactor to simplify string formatting (https://github.com/ansible-collections/community.general/pull/10727).
- zypper - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).
- zypper - support the ``--gpg-auto-import-keys`` option in zypper (https://github.com/ansible-collections/community.general/issues/10660, https://github.com/ansible-collections/community.general/pull/10661).
- zypper_repository - remove redundant constructs from argument specs (https://github.com/ansible-collections/community.general/pull/10513).

Breaking Changes / Porting Guide
--------------------------------

- mh.base module utils - ``debug`` will now always be delegated to the underlying ``AnsibleModule`` object (https://github.com/ansible-collections/community.general/pull/10883).
- oneview module utils - remove import of standard library ``os`` (https://github.com/ansible-collections/community.general/pull/10644).
- slack - the default of ``prepend_hash`` changed from ``auto`` to ``never`` (https://github.com/ansible-collections/community.general/pull/10883).

Deprecated Features
-------------------

- catapult - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/issues/10318, https://github.com/ansible-collections/community.general/pull/10329).
- cpanm - deprecate ``mode=compatibility``, ``mode=new`` should be used instead (https://github.com/ansible-collections/community.general/pull/10434).
- dimensiondata doc_fragments plugin - fragments is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10986).
- dimensiondata module_utils plugin - utils is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10986).
- dimensiondata_network - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10986).
- dimensiondata_vlan - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10986).
- dimensiondata_wait doc_fragments plugin - fragments is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10986).
- github_repo - deprecate ``force_defaults=true`` (https://github.com/ansible-collections/community.general/pull/10435).
- hiera lookup plugin - retrieving data with Hiera has been deprecated a long time ago; because of that this plugin will be removed from community.general 13.0.0. If you disagree with this deprecation, please create an issue in the community.general repository (https://github.com/ansible-collections/community.general/issues/4462, https://github.com/ansible-collections/community.general/pull/10779).
- oci_utils module utils - utils is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/issues/10318, https://github.com/ansible-collections/community.general/pull/10652).
- oci_vcn - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/issues/10318, https://github.com/ansible-collections/community.general/pull/10652).
- oneandone module utils - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_firewall_policy - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_load_balancer - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_monitoring_policy - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_private_network - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_public_ip - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oneandone_server - DNS fails to resolve the API endpoint used by the module. The module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10994).
- oracle* doc fragments - fragments are deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/issues/10318, https://github.com/ansible-collections/community.general/pull/10652).
- pacemaker_cluster - the state ``cleanup`` will be removed from community.general 14.0.0 (https://github.com/ansible-collections/community.general/pull/10741).
- rocketchat - the default value for ``is_pre740``, currently ``true``, is deprecated and will change to ``false`` in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/10490).
- typetalk - module is deprecated and will be removed in community.general 13.0.0 (https://github.com/ansible-collections/community.general/pull/9499).

Removed Features (previously deprecated)
----------------------------------------

- Ansible-core 2.16 is no longer supported. This also means that the collection now requires Python 3.7+ (https://github.com/ansible-collections/community.general/pull/10884).
- bearychat - the module has been removed as the chat service is no longer available (https://github.com/ansible-collections/community.general/pull/10883).
- cmd_runner module utils - the parameter ``ignore_value_none`` to ``CmdRunner.__call__()`` has been removed (https://github.com/ansible-collections/community.general/pull/10883).
- cmd_runner_fmt module utils - the parameter ``ctx_ignore_none`` to argument formatters has been removed (https://github.com/ansible-collections/community.general/pull/10883).
- facter - the module has been replaced by ``community.general.facter_facts`` (https://github.com/ansible-collections/community.general/pull/10883).
- mh.deco module utils - the parameters ``on_success`` and ``on_failure`` of ``cause()`` have been removed; use ``when="success"`` and ``when="failure"`` instead (https://github.com/ansible-collections/community.general/pull/10883).
- opkg - the value ``""`` for the option ``force`` is no longer allowed. Omit ``force`` instead (https://github.com/ansible-collections/community.general/pull/10883).
- pacemaker_cluster - the option ``state`` is now required (https://github.com/ansible-collections/community.general/pull/10883).
- pure module utils - the modules using this module utils have been removed from community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/10883).
- purestorage doc fragment - the modules using this doc fragment have been removed from community.general 3.0.0 (https://github.com/ansible-collections/community.general/pull/10883).
- yaml callback plugin - the deprecated plugin has been removed. Use the default callback with ``result_format=yaml`` instead (https://github.com/ansible-collections/community.general/pull/10883).

Security Fixes
--------------

- keycloak_user - the parameter ``credentials[].value`` is now marked as ``no_log=true``. Before it was logged by Ansible, unless the task was marked as ``no_log: true``. Since this parameter can be used for passwords, this resulted in credential leaking (https://github.com/ansible-collections/community.general/issues/11000, https://github.com/ansible-collections/community.general/pull/11005).

Bugfixes
--------

- Avoid deprecated functionality in ansible-core 2.20 (https://github.com/ansible-collections/community.general/pull/10687).
- Avoid usage of deprecated ``ansible.module_utils.six`` in all code that does not have to support Python 2 (https://github.com/ansible-collections/community.general/pull/10873).
- Remove all usage of ``ansible.module_utils.six`` (https://github.com/ansible-collections/community.general/pull/10888).
- apache2_module - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- apache2_module - check the ``cgi`` module restrictions only during activation (https://github.com/ansible-collections/community.general/pull/10423).
- apk - fix check for empty/whitespace-only package names (https://github.com/ansible-collections/community.general/pull/10532).
- apk - handle empty name strings properly (https://github.com/ansible-collections/community.general/issues/10441, https://github.com/ansible-collections/community.general/pull/10442).
- capabilities - using invalid path (symlink/directory/...) returned unrelated and incoherent error messages (https://github.com/ansible-collections/community.general/issues/5649, https://github.com/ansible-collections/community.general/pull/10455).
- cloudflare_dns - roll back changes to CAA record validation (https://github.com/ansible-collections/community.general/issues/10934, https://github.com/ansible-collections/community.general/pull/10956).
- cloudflare_dns - roll back changes to SRV record validation (https://github.com/ansible-collections/community.general/issues/10934, https://github.com/ansible-collections/community.general/pull/10937).
- cronvar - fix crash on missing ``cron_file`` parent directories (https://github.com/ansible-collections/community.general/issues/10460, https://github.com/ansible-collections/community.general/pull/10461).
- cronvar - handle empty strings on ``value`` properly  (https://github.com/ansible-collections/community.general/issues/10439, https://github.com/ansible-collections/community.general/pull/10445).
- dependent lookup plugin - avoid deprecated ansible-core 2.19 functionality (https://github.com/ansible-collections/community.general/pull/10359).
- doas become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/issues/9977, https://github.com/ansible-collections/community.general/pull/10537).
- gem - fix soundness issue when uninstalling default gems on Ubuntu  (https://github.com/ansible-collections/community.general/issues/10451, https://github.com/ansible-collections/community.general/pull/10689).
- github_app_access_token lookup plugin - fix compatibility imports for using jwt (https://github.com/ansible-collections/community.general/issues/10807, https://github.com/ansible-collections/community.general/pull/10810).
- github_deploy_key - fix bug during error handling if no body was present in the result (https://github.com/ansible-collections/community.general/issues/10853, https://github.com/ansible-collections/community.general/pull/10857).
- github_release - support multiple types of GitHub tokens; no longer failing when ``ghs_`` token type is provided (https://github.com/ansible-collections/community.general/issues/10338, https://github.com/ansible-collections/community.general/pull/10339).
- gitlab_runner - fix exception in check mode when a new runner is created (https://github.com/ansible-collections/community.general/issues/8854).
- homebrew - do not fail when cask or formula name has changed in homebrew repo (https://github.com/ansible-collections/community.general/issues/10804, https://github.com/ansible-collections/community.general/pull/10805).
- htpasswd - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- icinga2 inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- incus connection plugin - fix error handling to return more useful Ansible errors to the user (https://github.com/ansible-collections/community.general/issues/10344, https://github.com/ansible-collections/community.general/pull/10349).
- irc - pass hostname to ``wrap_socket()`` if ``use_tls=true`` and ``validate_certs=true`` (https://github.com/ansible-collections/community.general/issues/10472, https://github.com/ansible-collections/community.general/pull/10491).
- jenkins_plugin - install latest compatible version instead of latest (https://github.com/ansible-collections/community.general/issues/854, https://github.com/ansible-collections/community.general/pull/10346).
- jenkins_plugin - separate Jenkins and external URL credentials (https://github.com/ansible-collections/community.general/issues/4419, https://github.com/ansible-collections/community.general/pull/10346).
- json_query filter plugin - make compatible with lazy evaluation list and dictionary types of ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10539).
- kdeconfig - ``kwriteconfig`` executable could not be discovered automatically on systems with only ``kwriteconfig6`` installed. ``kwriteconfig6`` can now be discovered by Ansible (https://github.com/ansible-collections/community.general/issues/10746, https://github.com/ansible-collections/community.general/pull/10751).
- keycloak_clientsecret, keycloak_clientsecret_info - make ``client_auth`` work (https://github.com/ansible-collections/community.general/issues/10932, https://github.com/ansible-collections/community.general/pull/10933).
- keycloak_group - fixes an issue where module ignores realm when searching subgroups by name (https://github.com/ansible-collections/community.general/pull/10840).
- keycloak_realm - support setting ``adminPermissionsEnabled`` for a realm (https://github.com/ansible-collections/community.general/issues/10962).
- keycloak_role - fixes an issue where the module incorrectly returns ``changed=true`` when using the alias ``clientId`` in composite roles (https://github.com/ansible-collections/community.general/pull/10829).
- linode inventory plugin - avoid using deprecated option when templating options (https://github.com/ansible-collections/community.general/pull/10271).
- listen_port_facts - avoid crash when required commands are missing (https://github.com/ansible-collections/community.general/issues/10457, https://github.com/ansible-collections/community.general/pull/10458).
- logstash callback plugin - remove reference to Python 2 library (https://github.com/ansible-collections/community.general/pull/10345).
- lvm_pv - properly detect SCSI or NVMe devices to rescan (https://github.com/ansible-collections/community.general/issues/10444, https://github.com/ansible-collections/community.general/pull/10596).
- machinectl become plugin - disable pipelining on ansible-core 2.19+. The plugin does not work with pipelining, and since ansible-core 2.19 become plugins can indicate that they do not work with pipelining (https://github.com/ansible-collections/community.general/pull/10537).
- merge_variables lookup plugin - avoid deprecated functionality from ansible-core 2.19 (https://github.com/ansible-collections/community.general/pull/10566).
- monit - fix crash caused by an unknown status value returned from the monit service (https://github.com/ansible-collections/community.general/issues/10742, https://github.com/ansible-collections/community.general/pull/10743).
- omapi_host - make return values compatible with ansible-core 2.19 and Python 3 (https://github.com/ansible-collections/community.general/pull/11001).
- onepassword_doc and onepassword_ssh_key lookup plugins - ensure that all connection parameters are passed to CLI class (https://github.com/ansible-collections/community.general/pull/10965).
- pacemaker - use regex for matching ``maintenance-mode`` output to determine cluster maintenance status (https://github.com/ansible-collections/community.general/issues/10426, https://github.com/ansible-collections/community.general/pull/10707).
- pacemaker_resource - fix ``resource_type`` parameter formatting (https://github.com/ansible-collections/community.general/issues/10426, https://github.com/ansible-collections/community.general/pull/10663).
- parted - variable is a list, not text (https://github.com/ansible-collections/community.general/pull/10823, https://github.com/ansible-collections/community.general/issues/10817).
- pids - prevent error when an empty string is provided for ``name`` (https://github.com/ansible-collections/community.general/issues/10672, https://github.com/ansible-collections/community.general/pull/10688).
- pritunl_user - improve resilience when comparing user parameters if remote fields are ``null`` or missing. List parameters (``groups``, ``mac_addresses``) now safely default to empty lists for comparison and avoids ``KeyError`` issues (https://github.com/ansible-collections/community.general/issues/10954, https://github.com/ansible-collections/community.general/pull/10955).
- random_string lookup plugin - replace ``random.SystemRandom()`` with ``secrets.SystemRandom()`` when generating strings. This has no practical effect, as both are the same (https://github.com/ansible-collections/community.general/pull/10893).
- rocketchat - fix message delivery in Rocket Chat >= 7.5.3 by forcing ``Content-Type`` header to ``application/json`` instead of the default ``application/x-www-form-urlencoded`` (https://github.com/ansible-collections/community.general/issues/10796, https://github.com/ansible-collections/community.general/pull/10796).
- selective callback plugin - specify ``ansible_loop_var`` instead of the explicit value ``item`` when printing task result (https://github.com/ansible-collections/community.general/pull/10752).
- syspatch - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- sysrc - fixes parsing with multi-line variables (https://github.com/ansible-collections/community.general/issues/10394, https://github.com/ansible-collections/community.general/pull/10417).
- sysupgrade - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).
- terraform - fix bug when ``null`` values inside complex vars are throwing error instead of being passed to terraform. Now terraform can handle ``null``s in ``complex_vars`` itself (https://github.com/ansible-collections/community.general/pull/10961).
- wsl connection plugin - avoid deprecated ansible-core paramiko import helper, import paramiko directly instead (https://github.com/ansible-collections/community.general/issues/10515, https://github.com/ansible-collections/community.general/pull/10531).
- xfconf - fix handling of empty array properties (https://github.com/ansible-collections/community.general/pull/11026).
- xfconf_info - fix handling of empty array properties (https://github.com/ansible-collections/community.general/pull/11026).
- yaml cache plugin - make compatible with ansible-core 2.19 (https://github.com/ansible-collections/community.general/issues/10849, https://github.com/ansible-collections/community.general/issues/10852).
- zypper_repository - avoid ansible-core 2.19 deprecation (https://github.com/ansible-collections/community.general/pull/10459).

New Plugins
-----------

Callback
~~~~~~~~

- community.general.tasks_only - Only show tasks.

Filter
~~~~~~

- community.general.to_nice_yaml - Convert variable to YAML string.
- community.general.to_yaml - Convert variable to YAML string.

Inventory
~~~~~~~~~

- community.general.incus - Incus inventory source.

Lookup
~~~~~~

- community.general.binary_file - Read binary file and return it Base64 encoded.

New Modules
-----------

- community.general.django_dumpdata - Wrapper for ``django-admin dumpdata``.
- community.general.django_loaddata - Wrapper for ``django-admin loaddata``.
- community.general.jenkins_credential - Manage Jenkins credentials and domains through API.
- community.general.kea_command - Submits generic command to ISC KEA server on target.
- community.general.keycloak_user_execute_actions_email - Send a Keycloak execute-actions email to a user.
- community.general.lvm_pv_move_data - Move data between LVM Physical Volumes (PVs).
- community.general.pacemaker_info - Gather information about Pacemaker cluster.
- community.general.pacemaker_stonith - Manage Pacemaker STONITH.
