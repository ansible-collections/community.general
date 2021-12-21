===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 3.0.0.

v4.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- aix_filesystem - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3833).
- aix_lvg - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3834).
- gitlab - add more token authentication support with the new options ``api_oauth_token`` and ``api_job_token`` (https://github.com/ansible-collections/community.general/issues/705).
- gitlab_group, gitlab_project - add new option ``avatar_path`` (https://github.com/ansible-collections/community.general/pull/3792).
- gitlab_project - add new option ``default_branch`` to gitlab_project (if ``readme = true``) (https://github.com/ansible-collections/community.general/pull/3792).
- hponcfg - revamped module using ModuleHelper (https://github.com/ansible-collections/community.general/pull/3840).
- icinga2 inventory plugin - added the ``display_name`` field to variables (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- icinga2 inventory plugin - inventory object names are changable using ``inventory_attr`` in your config file to the host object name, address, or display_name fields (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- ip_netns - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3822).
- iso_extract - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3805).
- java_cert - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3835).
- jira - add support for Bearer token auth (https://github.com/ansible-collections/community.general/pull/3838).
- keycloak_user_federation - add sssd user federation support (https://github.com/ansible-collections/community.general/issues/3767).
- logentries - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3807).
- logstash_plugin - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3808).
- lxc_container - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3851).
- lxd connection plugin - make sure that ``ansible_lxd_host``, ``ansible_executable``, and ``ansible_lxd_executable`` work (https://github.com/ansible-collections/community.general/pull/3798).
- lxd inventory plugin - support virtual machines (https://github.com/ansible-collections/community.general/pull/3519).
- module_helper module utils - added decorators ``check_mode_skip`` and ``check_mode_skip_returns`` for skipping methods when ``check_mode=True`` (https://github.com/ansible-collections/community.general/pull/3849).
- monit - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3821).
- nmcli - add multiple addresses support for ``ip6`` parameter (https://github.com/ansible-collections/community.general/issues/1088).
- nmcli - add support for ``eui64`` and ``ipv6privacy`` parameters (https://github.com/ansible-collections/community.general/issues/3357).
- python_requirements_info - returns python version broken down into its components, and some minor refactoring (https://github.com/ansible-collections/community.general/pull/3797).
- svc - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3829).
- xattr - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3806).
- xfconf - minor refactor on the base class for the module (https://github.com/ansible-collections/community.general/pull/3919).

Deprecated Features
-------------------

- module_helper module utils - deprecated the attribute ``ModuleHelper.VarDict`` (https://github.com/ansible-collections/community.general/pull/3801).

Bugfixes
--------

- icinga2 inventory plugin - handle 404 error when filter produces no results (https://github.com/ansible-collections/community.general/issues/3875, https://github.com/ansible-collections/community.general/pull/3906).
- interfaces_file - fixed the check for existing option in interface (https://github.com/ansible-collections/community.general/issues/3841).
- jira - fixed bug where module returns error related to dictionary key ``body`` (https://github.com/ansible-collections/community.general/issues/3419).
- nmcli - fix returning "changed" when no mask set for IPv4 or IPv6 addresses on task rerun (https://github.com/ansible-collections/community.general/issues/3768).
- nmcli - pass ``flags``, ``ingress``, ``egress`` params to ``nmcli`` (https://github.com/ansible-collections/community.general/issues/1086).
- nrdp callback plugin - fix error ``string arguments without an encoding`` (https://github.com/ansible-collections/community.general/issues/3903).
- opentelemetry_plugin - honour ``ignore_errors`` when a task has failed instead of reporting an error (https://github.com/ansible-collections/community.general/pull/3837).
- pipx - passes the correct command line option ``--include-apps`` (https://github.com/ansible-collections/community.general/issues/3791).
- proxmox - fixed ``onboot`` parameter causing module failures when undefined (https://github.com/ansible-collections/community.general/issues/3844).
- python_requirements_info - fails if version operator used without version (https://github.com/ansible-collections/community.general/pull/3785).

New Modules
-----------

Net Tools
~~~~~~~~~

- dnsimple_info - Pull basic info from DNSimple API

Remote Management
~~~~~~~~~~~~~~~~~

redfish
^^^^^^^

- ilo_redfish_config - Sets or updates configuration attributes on HPE iLO with Redfish OEM extensions
- ilo_redfish_info - Gathers server information through iLO using Redfish APIs

Source Control
~~~~~~~~~~~~~~

gitlab
^^^^^^

- gitlab_branch - Create or delete a branch

v4.1.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- gitlab - clean up modules and utils (https://github.com/ansible-collections/community.general/pull/3694).
- ipmi_boot - add support for user-specified IPMI encryption key (https://github.com/ansible-collections/community.general/issues/3698).
- ipmi_power - add support for user-specified IPMI encryption key (https://github.com/ansible-collections/community.general/issues/3698).
- listen_ports_facts - add support for ``ss`` command besides ``netstat`` (https://github.com/ansible-collections/community.general/pull/3708).
- lxd_container - adds ``type`` option which also allows to operate on virtual machines and not just containers (https://github.com/ansible-collections/community.general/pull/3661).
- nmcli - add multiple addresses support for ``ip4`` parameter (https://github.com/ansible-collections/community.general/issues/1088, https://github.com/ansible-collections/community.general/pull/3738).
- open_iscsi - extended module to allow rescanning of established session for one or all targets (https://github.com/ansible-collections/community.general/issues/3763).
- pacman - add ``stdout`` and ``stderr`` as return values (https://github.com/ansible-collections/community.general/pull/3758).
- redfish_command - add ``GetHostInterfaces`` command to enable reporting Redfish Host Interface information (https://github.com/ansible-collections/community.general/issues/3693).
- redfish_command - add ``SetHostInterface`` command to enable configuring the Redfish Host Interface (https://github.com/ansible-collections/community.general/issues/3632).

Bugfixes
--------

- github_repo - ``private`` and ``description`` attributes should not be set to default values when the repo already exists (https://github.com/ansible-collections/community.general/pull/2386).
- terraform - fix command options being ignored during planned/plan in function ``build_plan`` such as ``lock`` or ``lock_timeout`` (https://github.com/ansible-collections/community.general/issues/3707, https://github.com/ansible-collections/community.general/pull/3726).

New Plugins
-----------

Inventory
~~~~~~~~~

- xen_orchestra - Xen Orchestra inventory source

Lookup
~~~~~~

- revbitspss - Get secrets from RevBits PAM server

v4.0.2
======

Release Summary
---------------

Bugfix release for today's Ansible 5.0.0 beta 2.

Deprecated Features
-------------------

- Support for Ansible 2.9 and ansible-base 2.10 is deprecated, and will be removed in the next major release (community.general 5.0.0) next spring. While most content will probably still work with ansible-base 2.10, we will remove symbolic links for modules and action plugins, which will make it impossible to use them with Ansible 2.9 anymore. Please use community.general 4.x.y with Ansible 2.9 and ansible-base 2.10, as these releases will continue to support Ansible 2.9 and ansible-base 2.10 even after they are End of Life (https://github.com/ansible-community/community-topics/issues/50, https://github.com/ansible-collections/community.general/pull/3723).

Bugfixes
--------

- counter_enabled callback plugin - fix output to correctly display host and task counters in serial mode (https://github.com/ansible-collections/community.general/pull/3709).
- ldap_search - allow it to be used even in check mode (https://github.com/ansible-collections/community.general/issues/3619).
- lvol - allows logical volumes to be created with certain size arguments prefixed with ``+`` to preserve behavior of older versions of this module (https://github.com/ansible-collections/community.general/issues/3665).
- nmcli - fixed falsely reported changed status when ``mtu`` is omitted with ``dummy`` connections (https://github.com/ansible-collections/community.general/issues/3612, https://github.com/ansible-collections/community.general/pull/3625).

v4.0.1
======

Release Summary
---------------

Bugfix release for today's Ansible 5.0.0 beta 1.

Bugfixes
--------

- a_module test plugin - fix crash when testing a module name that was tombstoned (https://github.com/ansible-collections/community.general/pull/3660).
- xattr - fix exception caused by ``_run_xattr()`` raising a ``ValueError`` due to a mishandling of base64-encoded value (https://github.com/ansible-collections/community.general/issues/3673).

v4.0.0
======

Release Summary
---------------

This is release 4.0.0 of ``community.general``, released on 2021-11-02.

Major Changes
-------------

- bitbucket_* modules - ``client_id`` is no longer marked as ``no_log=true``. If you relied on its value not showing up in logs and output, please mark the whole tasks with ``no_log: true`` (https://github.com/ansible-collections/community.general/pull/2045).

Minor Changes
-------------

- Avoid internal ansible-core module_utils in favor of equivalent public API available since at least Ansible 2.9 (https://github.com/ansible-collections/community.general/pull/2877).
- ModuleHelper module utils - improved mechanism for customizing the calculation of ``changed`` (https://github.com/ansible-collections/community.general/pull/2514).
- Remove unnecessary ``__init__.py`` files from ``plugins/`` (https://github.com/ansible-collections/community.general/pull/2632).
- apache2_module - minor refactoring improving code quality, readability and speed (https://github.com/ansible-collections/community.general/pull/3106).
- archive - added ``dest_state`` return value to describe final state of ``dest`` after successful task execution (https://github.com/ansible-collections/community.general/pull/2913).
- archive - added ``exclusion_patterns`` option to exclude files or subdirectories from archives (https://github.com/ansible-collections/community.general/pull/2616).
- archive - refactoring prior to fix for idempotency checks. The fix will be a breaking change and only appear in community.general 4.0.0 (https://github.com/ansible-collections/community.general/pull/2987).
- bitbucket_* modules - add ``user`` and ``password`` options for Basic authentication (https://github.com/ansible-collections/community.general/pull/2045).
- chroot connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- cloud_init_data_facts - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- cmd (Module Helper) module utils - ``CmdMixin`` now pulls the value for ``run_command()`` params from ``self.vars``, as opposed to previously retrieving those from ``self.module.params`` (https://github.com/ansible-collections/community.general/pull/2517).
- composer - add ``composer_executable`` option (https://github.com/ansible-collections/community.general/issues/2649).
- datadog_event - adding parameter ``api_host`` to allow selecting a datadog API endpoint instead of using the default one (https://github.com/ansible-collections/community.general/issues/2774, https://github.com/ansible-collections/community.general/pull/2775).
- datadog_monitor - allow creation of composite datadog monitors (https://github.com/ansible-collections/community.general/issues/2956).
- dig lookup plugin - add ``retry_servfail`` option (https://github.com/ansible-collections/community.general/pull/3247).
- dnsimple - module rewrite to include support for python-dnsimple>=2.0.0; also add ``sandbox`` parameter (https://github.com/ansible-collections/community.general/pull/2946).
- elastic callback plugin - enriched the stacktrace information with the ``message``, ``exception`` and ``stderr`` fields from the failed task (https://github.com/ansible-collections/community.general/pull/3556).
- filesystem - cleanup and revamp module, tests and doc. Pass all commands to ``module.run_command()`` as lists. Move the device-vs-mountpoint logic to ``grow()`` method. Give to all ``get_fs_size()`` the same logic and error handling. (https://github.com/ansible-collections/community.general/pull/2472).
- filesystem - extend support for FreeBSD. Avoid potential data loss by checking existence of a filesystem with ``fstyp`` (native command) if ``blkid`` (foreign command) doesn't find one. Add support for character devices and ``ufs`` filesystem type (https://github.com/ansible-collections/community.general/pull/2902).
- flatpak - add ``no_dependencies`` parameter (https://github.com/ansible/ansible/pull/55452, https://github.com/ansible-collections/community.general/pull/2751).
- flatpak - allows installing or uninstalling a list of packages (https://github.com/ansible-collections/community.general/pull/2521).
- funcd connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- gem - add ``bindir`` option to specify an installation path for executables such as ``/home/user/bin`` or ``/home/user/.local/bin`` (https://github.com/ansible-collections/community.general/pull/2837).
- gem - add ``norc`` option to avoid loading any ``.gemrc`` file (https://github.com/ansible-collections/community.general/pull/2837).
- github_repo - add new option ``api_url``  to allow working with on premises installations (https://github.com/ansible-collections/community.general/pull/3038).
- gitlab_group - add new options ``project_creation_level``, ``auto_devops_enabled``, ``subgroup_creation_level`` (https://github.com/ansible-collections/community.general/pull/3248).
- gitlab_group - add new property ``require_two_factor_authentication`` (https://github.com/ansible-collections/community.general/pull/3367).
- gitlab_group_members - ``gitlab_user`` can now also be a list of users (https://github.com/ansible-collections/community.general/pull/3047).
- gitlab_group_members - added functionality to set all members exactly as given (https://github.com/ansible-collections/community.general/pull/3047).
- gitlab_project - add new options ``allow_merge_on_skipped_pipeline``, ``only_allow_merge_if_all_discussions_are_resolved``, ``only_allow_merge_if_pipeline_succeeds``, ``packages_enabled``, ``remove_source_branch_after_merge``, ``squash_option`` (https://github.com/ansible-collections/community.general/pull/3002).
- gitlab_project - add new properties ``ci_config_path`` and ``shared_runners_enabled`` (https://github.com/ansible-collections/community.general/pull/3379).
- gitlab_project - projects can be created under other user's namespaces with the new ``username`` option (https://github.com/ansible-collections/community.general/pull/2824).
- gitlab_project_members - ``gitlab_user`` can now also be a list of users (https://github.com/ansible-collections/community.general/pull/3319).
- gitlab_project_members - added functionality to set all members exactly as given (https://github.com/ansible-collections/community.general/pull/3319).
- gitlab_runner - support project-scoped gitlab.com runners registration (https://github.com/ansible-collections/community.general/pull/634).
- gitlab_user - add ``expires_at`` option (https://github.com/ansible-collections/community.general/issues/2325).
- gitlab_user - add functionality for adding external identity providers to a GitLab user (https://github.com/ansible-collections/community.general/pull/2691).
- gitlab_user - allow to reset an existing password with the new ``reset_password`` option (https://github.com/ansible-collections/community.general/pull/2691).
- gitlab_user - specifying a password is no longer necessary (https://github.com/ansible-collections/community.general/pull/2691).
- gunicorn - search for ``gunicorn`` binary in more paths (https://github.com/ansible-collections/community.general/pull/3092).
- hana_query - added the abillity to use hdbuserstore (https://github.com/ansible-collections/community.general/pull/3125).
- hpilo_info - added ``host_power_status`` return value to report power state of machine with ``OFF``, ``ON`` or ``UNKNOWN`` (https://github.com/ansible-collections/community.general/pull/3079).
- idrac_redfish_config - modified set_manager_attributes function to skip invalid attribute instead of returning. Added skipped attributes to output. Modified module exit to add warning variable (https://github.com/ansible-collections/community.general/issues/1995).
- influxdb_retention_policy - add ``state`` parameter with allowed values ``present`` and ``absent`` to support deletion of existing retention policies (https://github.com/ansible-collections/community.general/issues/2383).
- influxdb_retention_policy - simplify duration logic parsing (https://github.com/ansible-collections/community.general/pull/2385).
- ini_file - add abbility to define multiple options with the same name but different values (https://github.com/ansible-collections/community.general/issues/273, https://github.com/ansible-collections/community.general/issues/1204).
- ini_file - add module option ``exclusive`` (boolean) for the ability to add/remove single ``option=value`` entries without overwriting existing options with the same name but different values (https://github.com/ansible-collections/community.general/pull/3033).
- ini_file - opening file with encoding ``utf-8-sig`` (https://github.com/ansible-collections/community.general/issues/2189).
- interfaces_file - minor refactor (https://github.com/ansible-collections/community.general/pull/3328).
- iocage connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- ipa_config - add ``ipaselinuxusermaporder`` option to set the SELinux user map order (https://github.com/ansible-collections/community.general/pull/3178).
- ipa_group - add ``append`` option for adding group and users members, instead of replacing the respective lists (https://github.com/ansible-collections/community.general/pull/3545).
- jail connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- java_keystore - added ``ssl_backend`` parameter for using the cryptography library instead of the OpenSSL binary (https://github.com/ansible-collections/community.general/pull/2485).
- java_keystore - replace envvar by stdin to pass secret to ``keytool`` (https://github.com/ansible-collections/community.general/pull/2526).
- jenkins_build - support stopping a running jenkins build (https://github.com/ansible-collections/community.general/pull/2850).
- jenkins_job_info - the ``password`` and ``token`` parameters can also be omitted to retrieve only public information (https://github.com/ansible-collections/community.general/pull/2948).
- jenkins_plugin - add fallback url(s) for failure of plugin installation/download (https://github.com/ansible-collections/community.general/pull/1334).
- jira - add comment visibility parameter for comment operation (https://github.com/ansible-collections/community.general/pull/2556).
- kernel_blacklist - revamped the module using ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/3329).
- keycloak_* modules - refactor many of the ``keycloak_*`` modules to have similar structures, comments, and documentation (https://github.com/ansible-collections/community.general/pull/3280).
- keycloak_authentication - enhanced diff mode to also return before and after state when the authentication flow is updated (https://github.com/ansible-collections/community.general/pull/2963).
- keycloak_client - add ``authentication_flow_binding_overrides`` option (https://github.com/ansible-collections/community.general/pull/2949).
- keycloak_realm - add ``events_enabled`` parameter to allow activation or deactivation of login events (https://github.com/ansible-collections/community.general/pull/3231).
- linode - added proper traceback when failing due to exceptions (https://github.com/ansible-collections/community.general/pull/2410).
- linode - parameter ``additional_disks`` is now validated as a list of dictionaries (https://github.com/ansible-collections/community.general/pull/2410).
- linode inventory plugin - adds the ``ip_style`` configuration key. Set to ``api`` to get more detailed network details back from the remote Linode host (https://github.com/ansible-collections/community.general/pull/3203).
- lxc connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- lxd_container - add ``ignore_volatile_options`` option which allows to disable the behavior that the module ignores options starting with ``volatile.`` (https://github.com/ansible-collections/community.general/pull/3331).
- mail - added the ``ehlohost`` parameter which allows for manual override of the host used in SMTP EHLO (https://github.com/ansible-collections/community.general/pull/3425).
- maven_artifact - added ``checksum_alg`` option to support SHA1 checksums in order to support FIPS systems (https://github.com/ansible-collections/community.general/pull/2662).
- module_helper cmd module utils - added the ``ArgFormat`` style ``BOOLEAN_NOT``, to add CLI parameters when the module argument is false-ish (https://github.com/ansible-collections/community.general/pull/3290).
- module_helper module utils - added feature flag parameter to ``CmdMixin`` to control whether ``cmd_args`` is automatically added to the module output (https://github.com/ansible-collections/community.general/pull/3648).
- module_helper module utils - added feature flag parameters to ``CmdMixin`` to control whether ``rc``, ``out`` and ``err`` are automatically added to the module output (https://github.com/ansible-collections/community.general/pull/2922).
- module_helper module utils - break down of the long file into smaller pieces (https://github.com/ansible-collections/community.general/pull/2393).
- module_helper module utils - method ``CmdMixin.run_command()`` now accepts ``process_output`` specifying a function to process the outcome of the underlying ``module.run_command()`` (https://github.com/ansible-collections/community.general/pull/2564).
- module_helper module_utils - added classmethod to trigger the execution of MH modules (https://github.com/ansible-collections/community.general/pull/3206).
- nmcli - add ``disabled`` value to ``method6`` option (https://github.com/ansible-collections/community.general/issues/2730).
- nmcli - add ``dummy`` interface support (https://github.com/ansible-collections/community.general/issues/724).
- nmcli - add ``gre`` tunnel support (https://github.com/ansible-collections/community.general/issues/3105, https://github.com/ansible-collections/community.general/pull/3262).
- nmcli - add ``gsm`` support (https://github.com/ansible-collections/community.general/pull/3313).
- nmcli - add ``routing_rules4`` and ``may_fail4`` options (https://github.com/ansible-collections/community.general/issues/2730).
- nmcli - add ``runner`` and ``runner_hwaddr_policy`` options (https://github.com/ansible-collections/community.general/issues/2901).
- nmcli - add ``wifi-sec`` option change detection to support managing secure Wi-Fi connections (https://github.com/ansible-collections/community.general/pull/3136).
- nmcli - add ``wifi`` option to support managing Wi-Fi settings such as ``hidden`` or ``mode`` (https://github.com/ansible-collections/community.general/pull/3081).
- nmcli - add new options to ignore automatic DNS servers and gateways (https://github.com/ansible-collections/community.general/issues/1087).
- nmcli - query ``nmcli`` directly to determine available WiFi options (https://github.com/ansible-collections/community.general/pull/3141).
- nmcli - remove dead code, ``options`` never contains keys from ``param_alias`` (https://github.com/ansible-collections/community.general/pull/2417).
- nmcli - the option ``routing_rules4`` can now be specified as a list of strings, instead of as a single string (https://github.com/ansible-collections/community.general/issues/3401).
- nrdp callback plugin - parameters are now converted to strings, except ``validate_certs`` which is converted to boolean (https://github.com/ansible-collections/community.general/pull/2878).
- onepassword lookup plugin - add ``domain`` option (https://github.com/ansible-collections/community.general/issues/2734).
- open-iscsi - adding support for mutual authentication between target and initiator (https://github.com/ansible-collections/community.general/pull/3422).
- open_iscsi - add ``auto_portal_startup`` parameter to allow ``node.startup`` setting per portal (https://github.com/ansible-collections/community.general/issues/2685).
- open_iscsi - also consider ``portal`` and ``port`` to check if already logged in or not (https://github.com/ansible-collections/community.general/issues/2683).
- open_iscsi - minor refactoring (https://github.com/ansible-collections/community.general/pull/3286).
- opentelemetry callback plugin - added option ``enable_from_environment`` to support enabling the plugin only if the given environment variable exists and it is set to true (https://github.com/ansible-collections/community.general/pull/3498).
- opentelemetry callback plugin - enriched the span attributes with HTTP metadata for those Ansible tasks that interact with third party systems (https://github.com/ansible-collections/community.general/pull/3448).
- opentelemetry callback plugin - enriched the stacktrace information for loops with the ``message``, ``exception`` and ``stderr`` fields from the failed item in the tasks in addition to the name of the task and failed item (https://github.com/ansible-collections/community.general/pull/3599).
- opentelemetry callback plugin - enriched the stacktrace information with the ``message``, ``exception`` and ``stderr`` fields from the failed task (https://github.com/ansible-collections/community.general/pull/3496).
- opentelemetry callback plugin - transformed args in a list of span attributes in addition it redacted username and password from any URLs (https://github.com/ansible-collections/community.general/pull/3564).
- openwrt_init - minor refactoring (https://github.com/ansible-collections/community.general/pull/3284).
- opkg - allow ``name`` to be a YAML list of strings (https://github.com/ansible-collections/community.general/issues/572, https://github.com/ansible-collections/community.general/pull/3554).
- pacman - add ``executable`` option to use an alternative pacman binary (https://github.com/ansible-collections/community.general/issues/2524).
- pacman - speed up checking if the package is installed, when the latest version check is not needed (https://github.com/ansible-collections/community.general/pull/3606).
- pamd - minor refactorings (https://github.com/ansible-collections/community.general/pull/3285).
- passwordstore lookup - add option ``missing`` to choose what to do if the password file is missing (https://github.com/ansible-collections/community.general/pull/2500).
- pids - refactor to add support for older ``psutil`` versions to the ``pattern`` option (https://github.com/ansible-collections/community.general/pull/3315).
- pipx - minor refactor on the ``changed`` logic (https://github.com/ansible-collections/community.general/pull/3647).
- pkgin - in case of ``pkgin`` tool failue, display returned standard output ``stdout`` and standard error ``stderr`` to ease debugging (https://github.com/ansible-collections/community.general/issues/3146).
- pkgng - ``annotation`` can now also be a YAML list (https://github.com/ansible-collections/community.general/pull/3526).
- pkgng - packages being installed (or upgraded) are acted on in one command (per action) (https://github.com/ansible-collections/community.general/issues/2265).
- pkgng - status message specifies number of packages installed and/or upgraded separately. Previously, all changes were reported as one count of packages "added" (https://github.com/ansible-collections/community.general/pull/3393).
- proxmox inventory plugin - added snapshots to host facts (https://github.com/ansible-collections/community.general/pull/3044).
- proxmox_group_info - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- proxmox_kvm - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- qubes connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- rax_mon_notification_plan - fixed validation checks by specifying type ``str`` as the ``elements`` of parameters ``ok_state``, ``warning_state`` and ``critical_state`` (https://github.com/ansible-collections/community.general/pull/2955).
- redfish_command - add ``boot_override_mode`` argument to BootSourceOverride commands (https://github.com/ansible-collections/community.general/issues/3134).
- redfish_command and redfish_config and redfish_utils module utils - add parameter to strip etag of quotes before patch, since some vendors do not properly ``If-Match`` etag with quotes (https://github.com/ansible-collections/community.general/pull/3296).
- redfish_config - modified module exit to add warning variable (https://github.com/ansible-collections/community.general/issues/1995).
- redfish_info - include ``Status`` property for Thermal objects when querying Thermal properties via ``GetChassisThermals`` command (https://github.com/ansible-collections/community.general/issues/3232).
- redfish_utils module utils - modified set_bios_attributes function to skip invalid attribute instead of returning. Added skipped attributes to output (https://github.com/ansible-collections/community.general/issues/1995).
- redhat_subscription - add ``server_prefix`` and ``server_port`` parameters (https://github.com/ansible-collections/community.general/pull/2779).
- redis - allow to use the term ``replica`` instead of ``slave``, which has been the official Redis terminology since 2018 (https://github.com/ansible-collections/community.general/pull/2867).
- rhevm - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- saltstack connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- scaleway plugin inventory - parse scw-cli config file for ``oauth_token`` (https://github.com/ansible-collections/community.general/pull/3250).
- serverless - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- slack - minor refactoring (https://github.com/ansible-collections/community.general/pull/3205).
- snap - added ``enabled`` and ``disabled`` states (https://github.com/ansible-collections/community.general/issues/1990).
- snap - improved module error handling, especially for the case when snap server is down (https://github.com/ansible-collections/community.general/issues/2970).
- splunk callback plugin - add ``batch`` option for user-configurable correlation ID's (https://github.com/ansible-collections/community.general/issues/2790).
- spotinst_aws_elastigroup - elements of list parameters are now validated (https://github.com/ansible-collections/community.general/pull/2355).
- ssh_config - new feature to set ``ForwardAgent`` option to ``yes`` or ``no`` (https://github.com/ansible-collections/community.general/issues/2473).
- stacki_host - minor refactoring (https://github.com/ansible-collections/community.general/pull/2681).
- supervisorctl - add the possibility to restart all programs and program groups (https://github.com/ansible-collections/community.general/issues/3551).
- supervisorctl - using standard Ansible mechanism to validate ``signalled`` state required parameter (https://github.com/ansible-collections/community.general/pull/3068).
- terraform - add ``check_destroy`` optional parameter to check for deletion of resources before it is applied (https://github.com/ansible-collections/community.general/pull/2874).
- terraform - add ``parallelism`` parameter (https://github.com/ansible-collections/community.general/pull/3540).
- terraform - add option ``overwrite_init`` to skip init if exists (https://github.com/ansible-collections/community.general/pull/2573).
- terraform - minor refactor (https://github.com/ansible-collections/community.general/pull/2557).
- timezone - print error message to debug instead of warning when timedatectl fails (https://github.com/ansible-collections/community.general/issues/1942).
- tss lookup plugin - added ``token`` parameter for token authorization; ``username`` and ``password`` are optional when ``token`` is provided (https://github.com/ansible-collections/community.general/pull/3327).
- tss lookup plugin - added new parameter for domain authorization (https://github.com/ansible-collections/community.general/pull/3228).
- tss lookup plugin - refactored to decouple the supporting third-party library (``python-tss-sdk``) (https://github.com/ansible-collections/community.general/pull/3252).
- ufw - if ``delete=true`` and ``insert`` option is present, then ``insert`` is now ignored rather than failing with a syntax error (https://github.com/ansible-collections/community.general/pull/3514).
- vdo - minor refactoring of the code (https://github.com/ansible-collections/community.general/pull/3191).
- zfs - added diff mode support (https://github.com/ansible-collections/community.general/pull/502).
- zfs_delegate_admin - drop choices from permissions, allowing any permission supported by the underlying zfs commands (https://github.com/ansible-collections/community.general/pull/2540).
- zone connection - minor refactor to make lints and IDEs happy (https://github.com/ansible-collections/community.general/pull/2520).
- zpool_facts - minor refactoring (https://github.com/ansible-collections/community.general/pull/3332).
- zypper - prefix zypper commands with ``/sbin/transactional-update --continue --drop-if-no-change --quiet run`` if transactional updates are detected (https://github.com/ansible-collections/community.general/issues/3159).

Breaking Changes / Porting Guide
--------------------------------

- archive - adding idempotency checks for changes to file names and content within the ``destination`` file (https://github.com/ansible-collections/community.general/pull/3075).
- lxd inventory plugin - when used with Python 2, the plugin now needs ``ipaddress`` installed `from pypi <https://pypi.org/project/ipaddress/>`_ (https://github.com/ansible-collections/community.general/pull/2441).
- scaleway_security_group_rule - when used with Python 2, the module now needs ``ipaddress`` installed `from pypi <https://pypi.org/project/ipaddress/>`_ (https://github.com/ansible-collections/community.general/pull/2441).

Deprecated Features
-------------------

- ali_instance_info - marked removal version of deprecated parameters ``availability_zone`` and ``instance_names`` (https://github.com/ansible-collections/community.general/issues/2429).
- bitbucket_* modules - ``username`` options have been deprecated in favor of ``workspace`` and will be removed in community.general 6.0.0 (https://github.com/ansible-collections/community.general/pull/2045).
- dnsimple - python-dnsimple < 2.0.0 is deprecated and support for it will be removed in community.general 5.0.0 (https://github.com/ansible-collections/community.general/pull/2946#discussion_r667624693).
- gitlab_group_members - setting ``gitlab_group`` to ``name`` or ``path`` is deprecated. Use ``full_path`` instead (https://github.com/ansible-collections/community.general/pull/3451).
- keycloak_authentication - the return value ``flow`` is now deprecated and will be removed in community.general 6.0.0; use ``end_state`` instead (https://github.com/ansible-collections/community.general/pull/3280).
- keycloak_group - the return value ``group`` is now deprecated and will be removed in community.general 6.0.0; use ``end_state`` instead (https://github.com/ansible-collections/community.general/pull/3280).
- linode - parameter ``backupsenabled`` is deprecated and will be removed in community.general 5.0.0 (https://github.com/ansible-collections/community.general/pull/2410).
- lxd_container - the current default value ``true`` of ``ignore_volatile_options`` is deprecated and will change to ``false`` in community.general 6.0.0 (https://github.com/ansible-collections/community.general/pull/3429).
- serverless - deprecating parameter ``functions`` because it was not used in the code (https://github.com/ansible-collections/community.general/pull/2845).
- xfconf - deprecate the ``get`` state. The new module ``xfconf_info`` should be used instead (https://github.com/ansible-collections/community.general/pull/3049).

Removed Features (previously deprecated)
----------------------------------------

- All inventory and vault scripts contained in community.general were moved to the `contrib-scripts GitHub repository <https://github.com/ansible-community/contrib-scripts>`_ (https://github.com/ansible-collections/community.general/pull/2696).
- ModuleHelper module utils - remove fallback when value could not be determined for a parameter (https://github.com/ansible-collections/community.general/pull/3461).
- Removed deprecated netapp module utils and doc fragments (https://github.com/ansible-collections/community.general/pull/3197).
- The nios, nios_next_ip, nios_next_network lookup plugins, the nios documentation fragment, and the nios_host_record, nios_ptr_record, nios_mx_record, nios_fixed_address, nios_zone, nios_member, nios_a_record, nios_aaaa_record, nios_network, nios_dns_view, nios_txt_record, nios_naptr_record, nios_srv_record, nios_cname_record, nios_nsgroup, and nios_network_view module have been removed from community.general 4.0.0 and were replaced by redirects to the `infoblox.nios_modules <https://galaxy.ansible.com/infoblox/nios_modules>`_ collection. Please install the ``infoblox.nios_modules`` collection to continue using these plugins and modules, and update your FQCNs (https://github.com/ansible-collections/community.general/pull/3592).
- The vendored copy of ``ipaddress`` has been removed. Please use ``ipaddress`` from the Python 3 standard library, or `from pypi <https://pypi.org/project/ipaddress/>`_. (https://github.com/ansible-collections/community.general/pull/2441).
- cpanm - removed the deprecated ``system_lib`` option. Use Ansible's privilege escalation mechanism instead; the option basically used ``sudo`` (https://github.com/ansible-collections/community.general/pull/3461).
- grove - removed the deprecated alias ``message`` of the ``message_content`` option (https://github.com/ansible-collections/community.general/pull/3461).
- proxmox - default value of ``proxmox_default_behavior`` changed to ``no_defaults`` (https://github.com/ansible-collections/community.general/pull/3461).
- proxmox_kvm - default value of ``proxmox_default_behavior`` changed to ``no_defaults`` (https://github.com/ansible-collections/community.general/pull/3461).
- runit - removed the deprecated ``dist`` option which was not used by the module (https://github.com/ansible-collections/community.general/pull/3461).
- telegram - removed the deprecated ``msg``, ``msg_format`` and ``chat_id`` options (https://github.com/ansible-collections/community.general/pull/3461).
- xfconf - the default value of ``disable_facts`` changed to ``true``, and the value ``false`` is no longer allowed. Register the module results instead (https://github.com/ansible-collections/community.general/pull/3461).

Security Fixes
--------------

- nmcli - do not pass WiFi secrets on the ``nmcli`` command line. Use ``nmcli con edit`` instead and pass secrets as ``stdin`` (https://github.com/ansible-collections/community.general/issues/3145).

Bugfixes
--------

- _mount module utils - fixed the sanity checks (https://github.com/ansible-collections/community.general/pull/2883).
- ali_instance_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- ansible_galaxy_install - the output value ``cmd_args`` was bringing the intermediate command used to gather the state, instead of the command that actually performed the state change (https://github.com/ansible-collections/community.general/pull/3655).
- apache2_module - fix ``a2enmod``/``a2dismod`` detection, and error message when not found (https://github.com/ansible-collections/community.general/issues/3253).
- archive - fixed ``exclude_path`` values causing incorrect archive root (https://github.com/ansible-collections/community.general/pull/2816).
- archive - fixed improper file names for single file zip archives (https://github.com/ansible-collections/community.general/issues/2818).
- archive - fixed incorrect ``state`` result value documentation (https://github.com/ansible-collections/community.general/pull/2816).
- archive - fixed task failure when using the ``remove`` option with a ``path`` containing nested files for ``format``s other than ``zip`` (https://github.com/ansible-collections/community.general/issues/2919).
- archive - fixing archive root determination when longest common root is ``/`` (https://github.com/ansible-collections/community.general/pull/3036).
- composer - use ``no-interaction`` option when discovering available options to avoid an issue where composer hangs (https://github.com/ansible-collections/community.general/pull/2348).
- consul_acl - update the hcl allowlist to include all supported options (https://github.com/ansible-collections/community.general/pull/2495).
- consul_kv lookup plugin - allow to set ``recurse``, ``index``, ``datacenter`` and ``token`` as keyword arguments (https://github.com/ansible-collections/community.general/issues/2124).
- copr - fix chroot naming issues, ``centos-stream`` changed naming to ``centos-stream-<number>`` (for exmaple ``centos-stream-8``) (https://github.com/ansible-collections/community.general/issues/2084, https://github.com/ansible-collections/community.general/pull/3237).
- cpanm - also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/pull/2731).
- deploy_helper - improved parameter checking by using standard Ansible construct (https://github.com/ansible-collections/community.general/pull/3104).
- django_manage - argument ``command`` is being splitted again as it should (https://github.com/ansible-collections/community.general/issues/3215).
- django_manage - parameters ``apps`` and ``fixtures`` are now splitted instead of being used as a single argument (https://github.com/ansible-collections/community.general/issues/3333).
- django_manage - refactor to call ``run_command()`` passing command as a list instead of string (https://github.com/ansible-collections/community.general/pull/3098).
- ejabberd_user - replaced in-code check with ``required_if``, using ``get_bin_path()`` for the command, passing args to ``run_command()`` as list instead of string (https://github.com/ansible-collections/community.general/pull/3093).
- filesystem - repair ``reiserfs`` fstype support after adding it to integration tests (https://github.com/ansible-collections/community.general/pull/2472).
- gitlab_deploy_key - fix idempotency on projects with multiple deploy keys (https://github.com/ansible-collections/community.general/pull/3473).
- gitlab_deploy_key - fix the SSH Deploy Key being deleted accidentally while running task in check mode (https://github.com/ansible-collections/community.general/issues/3621, https://github.com/ansible-collections/community.general/pull/3622).
- gitlab_group - avoid passing wrong value for ``require_two_factor_authentication`` on creation when the option has not been specified (https://github.com/ansible-collections/community.general/pull/3453).
- gitlab_group_members - ``get_group_id`` return the group ID by matching ``full_path``, ``path`` or ``name`` (https://github.com/ansible-collections/community.general/pull/3400).
- gitlab_group_members - fixes issue when gitlab group has more then 20 members, pagination problem (https://github.com/ansible-collections/community.general/issues/3041).
- gitlab_project - user projects are created using namespace ID now, instead of user ID (https://github.com/ansible-collections/community.general/pull/2881).
- gitlab_project_members - ``get_project_id`` return the project id by matching ``full_path`` or ``name`` (https://github.com/ansible-collections/community.general/pull/3602).
- gitlab_project_members - fixes issue when gitlab group has more then 20 members, pagination problem (https://github.com/ansible-collections/community.general/issues/3041).
- idrac_redfish_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- influxdb_retention_policy - fix bug where ``INF`` duration values failed parsing (https://github.com/ansible-collections/community.general/pull/2385).
- influxdb_user - allow creation of admin users when InfluxDB authentication is enabled but no other user exists on the database. In this scenario, InfluxDB 1.x allows only ``CREATE USER`` queries and rejects any other query (https://github.com/ansible-collections/community.general/issues/2364).
- influxdb_user - fix bug where an influxdb user has no privileges for 2 or more databases (https://github.com/ansible-collections/community.general/pull/2499).
- influxdb_user - fix bug which removed current privileges instead of appending them to existing ones (https://github.com/ansible-collections/community.general/issues/2609, https://github.com/ansible-collections/community.general/pull/2614).
- ini_file - fix Unicode processing for Python 2 (https://github.com/ansible-collections/community.general/pull/2875).
- ini_file - fix inconsistency between empty value and no value (https://github.com/ansible-collections/community.general/issues/3031).
- interfaces_file - no longer reporting change when none happened (https://github.com/ansible-collections/community.general/pull/3328).
- inventory and vault scripts - change file permissions to make vendored inventory and vault scripts exectuable (https://github.com/ansible-collections/community.general/pull/2337).
- ipa_* modules - fix environment fallback for ``ipa_host`` option (https://github.com/ansible-collections/community.general/issues/3560).
- ipa_sudorule - call ``sudorule_add_allow_command`` method instead of  ``sudorule_add_allow_command_group`` (https://github.com/ansible-collections/community.general/issues/2442).
- iptables_state - call ``async_status`` action plugin rather than its module (https://github.com/ansible-collections/community.general/issues/2700).
- iptables_state - fix a 'FutureWarning' in a regex and do some basic code clean up (https://github.com/ansible-collections/community.general/pull/2525).
- iptables_state - fix a broken query of ``async_status`` result with current ansible-core development version (https://github.com/ansible-collections/community.general/issues/2627, https://github.com/ansible-collections/community.general/pull/2671).
- iptables_state - fix initialization of iptables from null state when adressing more than one table (https://github.com/ansible-collections/community.general/issues/2523).
- java_cert - fix issue with incorrect alias used on PKCS#12 certificate import (https://github.com/ansible-collections/community.general/pull/2560).
- java_cert - import private key as well as public certificate from PKCS#12 (https://github.com/ansible-collections/community.general/issues/2460).
- java_keystore - add parameter ``keystore_type`` to control output file format and override ``keytool``'s default, which depends on Java version (https://github.com/ansible-collections/community.general/issues/2515).
- jboss - fix the deployment file permission issue when Jboss server is running under non-root user. The deployment file is copied with file content only. The file permission is set to ``440`` and belongs to root user. When the JBoss ``WildFly`` server is running under non-root user, it is unable to read the deployment file (https://github.com/ansible-collections/community.general/pull/3426).
- jenkins_build - examine presence of ``build_number`` before deleting a jenkins build (https://github.com/ansible-collections/community.general/pull/2850).
- jenkins_plugin - use POST method for sending request to jenkins API when ``state`` option is one of ``enabled``, ``disabled``, ``pinned``, ``unpinned``, or ``absent`` (https://github.com/ansible-collections/community.general/issues/2510).
- json_query filter plugin - avoid 'unknown type' errors for more Ansible internal types (https://github.com/ansible-collections/community.general/pull/2607).
- keycloak_authentication - fix bug when two identical executions are in the same authentication flow (https://github.com/ansible-collections/community.general/pull/2904).
- keycloak_authentication - fix bug, the requirement was always on ``DISABLED`` when creating a new authentication flow (https://github.com/ansible-collections/community.general/pull/3330).
- keycloak_client - update the check mode to not show differences resulting from sorting and default values relating to the properties, ``redirectUris``, ``attributes``, and ``protocol_mappers`` (https://github.com/ansible-collections/community.general/pull/3610).
- keycloak_identity_provider - fix change detection when updating identity provider mappers (https://github.com/ansible-collections/community.general/pull/3538, https://github.com/ansible-collections/community.general/issues/3537).
- keycloak_realm - ``ssl_required`` changed from a boolean type to accept the strings ``none``, ``external`` or ``all``. This is not a breaking change since the module always failed when a boolean was supplied (https://github.com/ansible-collections/community.general/pull/2693).
- keycloak_realm - element type for ``events_listeners`` parameter should be ``string`` instead of ``dict`` (https://github.com/ansible-collections/community.general/pull/3231).
- keycloak_realm - remove warning that ``reset_password_allowed`` needs to be marked as ``no_log`` (https://github.com/ansible-collections/community.general/pull/2694).
- keycloak_role - quote role name when used in URL path to avoid errors when role names contain special characters (https://github.com/ansible-collections/community.general/issues/3535, https://github.com/ansible-collections/community.general/pull/3536).
- launchd - fixed sanity check in the module's code (https://github.com/ansible-collections/community.general/pull/2960).
- launchd - use private attribute to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- linode inventory plugin - fix default value of new option ``ip_style`` (https://github.com/ansible-collections/community.general/issues/3337).
- linode_v4 - changed the error message to point to the correct bugtracker URL (https://github.com/ansible-collections/community.general/pull/2430).
- logdns callback plugin - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- logstash callback plugin - replace ``_option`` with ``context.CLIARGS`` to fix the plugin on ansible-base and ansible-core (https://github.com/ansible-collections/community.general/issues/2692).
- lvol - fixed rounding errors (https://github.com/ansible-collections/community.general/issues/2370).
- lvol - fixed size unit capitalization to match units used between different tools for comparison (https://github.com/ansible-collections/community.general/issues/2360).
- lvol - honor ``check_mode`` on thinpool (https://github.com/ansible-collections/community.general/issues/2934).
- macports - add ``stdout`` and ``stderr`` to return values (https://github.com/ansible-collections/community.general/issues/3499).
- maven_artifact - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- memcached cache plugin - change function argument names to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- memset_memstore_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- memset_server_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- modprobe - added additional checks to ensure module load/unload is effective (https://github.com/ansible-collections/community.general/issues/1608).
- module_helper module utils - ``CmdMixin`` must also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/pull/2731).
- module_helper module utils - avoid failing when non-zero ``rc`` is present on regular exit (https://github.com/ansible-collections/community.general/pull/2912).
- module_helper module utils - fixed change-tracking for dictionaries and lists (https://github.com/ansible-collections/community.general/pull/2951).
- netapp module utils - remove always-true conditional to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- netcup_dns - use ``str(ex)`` instead of unreliable ``ex.message`` in exception handling to fix ``AttributeError`` in error cases (https://github.com/ansible-collections/community.general/pull/2590).
- nmap inventory plugin - fix local variable error when cache is disabled (https://github.com/ansible-collections/community.general/issues/2512).
- nmcli - added ip4/ip6 configuration arguments for ``sit`` and ``ipip`` tunnels (https://github.com/ansible-collections/community.general/issues/3238, https://github.com/ansible-collections/community.general/pull/3239).
- nmcli - compare MAC addresses case insensitively to fix idempotency issue (https://github.com/ansible-collections/community.general/issues/2409).
- nmcli - fixed ``dns6`` option handling so that it is treated as a list internally (https://github.com/ansible-collections/community.general/pull/3563).
- nmcli - fixed ``ipv4.route-metric`` being in properties of type list (https://github.com/ansible-collections/community.general/pull/3563).
- nmcli - fixes team-slave configuration by adding connection.slave-type (https://github.com/ansible-collections/community.general/issues/766).
- nmcli - if type is ``bridge-slave`` add ``slave-type bridge`` to ``nmcli`` command (https://github.com/ansible-collections/community.general/issues/2408).
- npm - correctly handle cases where a dependency does not have a ``version`` property because it is either missing or invalid (https://github.com/ansible-collections/community.general/issues/2917).
- npm - when the ``version`` option is used the comparison of installed vs missing will use name@version instead of just name, allowing version specific updates (https://github.com/ansible-collections/community.general/issues/2021).
- one_image - fix error message when renaming an image (https://github.com/ansible-collections/community.general/pull/3626).
- one_template - change function argument name to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- one_vm - Allow missing NIC keys (https://github.com/ansible-collections/community.general/pull/2435).
- oneview_datacenter_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_enclosure_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_ethernet_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_fc_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_fcoe_network_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_logical_interconnect_group_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_network_set_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- oneview_san_manager_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- online inventory plugin - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- online module utils - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- open_iscsi - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3286).
- openbsd_pkg - fix crash from ``KeyError`` exception when package installs, but ``pkg_add`` returns with a non-zero exit code (https://github.com/ansible-collections/community.general/pull/3336).
- openbsd_pkg - fix regexp matching crash. This bug could trigger on package names with special characters, for example ``g++`` (https://github.com/ansible-collections/community.general/pull/3161).
- opentelemetry callback plugin - validated the task result exception without crashing. Also simplifying code a bit (https://github.com/ansible-collections/community.general/pull/3450, https://github.com/ansible/ansible/issues/75726).
- openwrt_init - calling ``run_command`` with arguments as ``list`` instead of ``str`` (https://github.com/ansible-collections/community.general/pull/3284).
- ovir4 inventory script - improve configparser creation to avoid crashes for options without values (https://github.com/ansible-collections/community.general/issues/674).
- packet_device - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- packet_sshkey - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- pacman - fix changed status when ignorepkg has been defined (https://github.com/ansible-collections/community.general/issues/1758).
- pamd - code for ``state=updated`` when dealing with the pam module arguments, made no distinction between ``None`` and an empty list (https://github.com/ansible-collections/community.general/issues/3260).
- pamd - fixed problem with files containing only one or two lines (https://github.com/ansible-collections/community.general/issues/2925).
- pids - avoid crashes for older ``psutil`` versions, like on RHEL6 and RHEL7 (https://github.com/ansible-collections/community.general/pull/2808).
- pipx - ``state=inject`` was failing to parse the list of injected packages (https://github.com/ansible-collections/community.general/pull/3611).
- pipx - set environment variable ``USE_EMOJI=0`` to prevent errors in platforms that do not support ``UTF-8`` (https://github.com/ansible-collections/community.general/pull/3611).
- pipx - the output value ``cmd_args`` was bringing the intermediate command used to gather the state, instead of the command that actually performed the state change (https://github.com/ansible-collections/community.general/pull/3655).
- pkgin - Fix exception encountered when all packages are already installed (https://github.com/ansible-collections/community.general/pull/3583).
- pkgng - ``name=* state=latest`` check for upgrades did not count "Number of packages to be reinstalled" as a `changed` action, giving incorrect results in both regular and check mode (https://github.com/ansible-collections/community.general/pull/3526).
- pkgng - an `earlier PR <https://github.com/ansible-collections/community.general/pull/3393>`_ broke check mode so that the module always reports `not changed`. This is now fixed so that the module reports number of upgrade or install actions that would be performed (https://github.com/ansible-collections/community.general/pull/3526).
- pkgng - the ``annotation`` functionality was broken and is now fixed, and now also works with check mode (https://github.com/ansible-collections/community.general/pull/3526).
- proxmox inventory plugin - fixed parsing failures when some cluster nodes are offline (https://github.com/ansible-collections/community.general/issues/2931).
- proxmox inventory plugin - fixed plugin failure when a ``qemu`` guest has no ``template`` key (https://github.com/ansible-collections/community.general/pull/3052).
- proxmox_group_info - fix module crash if a ``group`` parameter is used (https://github.com/ansible-collections/community.general/pull/3649).
- proxmox_kvm - clone operation should return the VMID of the target VM and not that of the source VM. This was failing when the target VM with the chosen name already existed (https://github.com/ansible-collections/community.general/pull/3266).
- proxmox_kvm - fix parsing of Proxmox VM information with device info not containing a comma, like disks backed by ZFS zvols (https://github.com/ansible-collections/community.general/issues/2840).
- proxmox_kvm - fix result of clone, now returns ``newid`` instead of ``vmid`` (https://github.com/ansible-collections/community.general/pull/3034).
- proxmox_kvm - fixed ``vmid`` return value when VM with ``name`` already exists (https://github.com/ansible-collections/community.general/issues/2648).
- puppet - replace ``console` with ``stdout`` in ``logdest`` option when ``all`` has been chosen (https://github.com/ansible-collections/community.general/issues/1190).
- rax_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- redfish_command - fix extraneous error caused by missing ``bootdevice`` argument when using the ``DisableBootOverride`` sub-command (https://github.com/ansible-collections/community.general/issues/3005).
- redfish_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- redfish_utils module utils - do not attempt to change the boot source override mode if not specified by the user (https://github.com/ansible-collections/community.general/issues/3509/).
- redfish_utils module utils - if a manager network property is not specified in the service, attempt to change the requested settings (https://github.com/ansible-collections/community.general/issues/3404/).
- redfish_utils module utils - if given, add account ID of user that should be created to HTTP request (https://github.com/ansible-collections/community.general/pull/3343/).
- redis cache - improved connection string parsing (https://github.com/ansible-collections/community.general/issues/497).
- rhsm_release - fix the issue that module considers 8, 7Client and 7Workstation as invalid releases (https://github.com/ansible-collections/community.general/pull/2571).
- saltstack connection plugin - fix function signature (https://github.com/ansible-collections/community.general/pull/3194).
- scaleway module utils - improve split call to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- scaleway plugin inventory - fix ``JSON object must be str, not 'bytes'`` with Python 3.5 (https://github.com/ansible-collections/community.general/issues/2769).
- smartos_image_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- snap - also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/pull/2731).
- snap - fix formatting of ``--channel`` argument when the ``channel`` option is used (https://github.com/ansible-collections/community.general/pull/3028).
- snap - fix various bugs which prevented the module from working at all, and which resulted in ``state=absent`` fail on absent snaps (https://github.com/ansible-collections/community.general/issues/2835, https://github.com/ansible-collections/community.general/issues/2906, https://github.com/ansible-collections/community.general/pull/2912).
- snap - fixed the order of the ``--classic`` parameter in the command line invocation (https://github.com/ansible-collections/community.general/issues/2916).
- snap_alias - the output value ``cmd_args`` was bringing the intermediate command used to gather the state, instead of the command that actually performed the state change (https://github.com/ansible-collections/community.general/pull/3655).
- snmp_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- ssh_config - reduce stormssh searches based on host (https://github.com/ansible-collections/community.general/pull/2568/).
- stacki_host - when adding a new server, ``rack`` and ``rank`` must be passed, and network parameters are optional (https://github.com/ansible-collections/community.general/pull/2681).
- stackpath_compute inventory script - fix broken validation checks for client ID and client secret (https://github.com/ansible-collections/community.general/pull/2448).
- supervisorctl - state ``signalled`` was not working (https://github.com/ansible-collections/community.general/pull/3068).
- svr4pkg - convert string to a bytes-like object to avoid ``TypeError`` with Python 3 (https://github.com/ansible-collections/community.general/issues/2373).
- taiga - some constructs in the module fixed to work also in Python 3 (https://github.com/ansible-collections/community.general/pull/3067).
- terraform - ensure the workspace is set back to its previous value when the apply fails (https://github.com/ansible-collections/community.general/pull/2634).
- tss lookup plugin - fixed backwards compatibility issue with ``python-tss-sdk`` version <=0.0.5 (https://github.com/ansible-collections/community.general/issues/3192, https://github.com/ansible-collections/community.general/pull/3199).
- tss lookup plugin - fixed incompatibility with ``python-tss-sdk`` version 1.0.0 (https://github.com/ansible-collections/community.general/issues/3057, https://github.com/ansible-collections/community.general/pull/3139).
- udm_dns_record - fixed managing of PTR records, which can never have worked before (https://github.com/ansible-collections/community.general/pull/3256).
- ufw - use generator to fix sanity errors (https://github.com/ansible-collections/community.general/pull/3194).
- utm_aaa_group_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_ca_host_key_cert_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_network_interface_address_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_proxy_frontend_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- utm_proxy_location_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- vdo - boolean arguments now compared with proper ``true`` and ``false`` values instead of string representations like ``"yes"`` or ``"no"`` (https://github.com/ansible-collections/community.general/pull/3191).
- xenserver_facts - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- xfconf - also use ``LC_ALL`` to enforce locale choice (https://github.com/ansible-collections/community.general/issues/2715).
- xfconf_info - added support to check mode (https://github.com/ansible-collections/community.general/pull/3084).
- yaml callback plugin - avoid modifying PyYAML so that other plugins using it on the controller, like the ``to_yaml`` filter, do not produce different output (https://github.com/ansible-collections/community.general/issues/3471, https://github.com/ansible-collections/community.general/pull/3478).
- yum_versionlock - fix idempotency when using wildcard (asterisk) in ``name`` option (https://github.com/ansible-collections/community.general/issues/2761).
- zfs - certain ZFS properties, especially sizes, would lead to a task being falsely marked as "changed" even when no actual change was made (https://github.com/ansible-collections/community.general/issues/975, https://github.com/ansible-collections/community.general/pull/2454).
- zfs - treated received properties as local (https://github.com/ansible-collections/community.general/pull/502).
- zypper_repository - fix idempotency on adding repository with ``$releasever`` and ``$basearch`` variables (https://github.com/ansible-collections/community.general/issues/1985).
- zypper_repository - when an URL to a .repo file was provided in option ``repo=`` and ``state=present`` only the first run was successful, future runs failed due to missing checks prior starting zypper. Usage of ``state=absent`` in combination with a .repo file was not working either (https://github.com/ansible-collections/community.general/issues/1791, https://github.com/ansible-collections/community.general/issues/3466).

New Plugins
-----------

Callback
~~~~~~~~

- elastic - Create distributed traces for each Ansible task in Elastic APM
- opentelemetry - Create distributed traces with OpenTelemetry

Filter
~~~~~~

- groupby_as_dict - Transform a sequence of dictionaries to a dictionary where the dictionaries are indexed by an attribute
- unicode_normalize - Normalizes unicode strings to facilitate comparison of characters with normalized forms

Inventory
~~~~~~~~~

- icinga2 - Icinga2 inventory source
- opennebula - OpenNebula inventory source

Lookup
~~~~~~

- collection_version - Retrieves the version of an installed collection
- dependent - Composes a list with nested elements of other lists or dicts which can depend on previous loop variables
- random_pet - Generates random pet names
- random_string - Generates random string
- random_words - Return a number of random words

Test
~~~~

- a_module - Check whether the given string refers to an available module or action plugin

New Modules
-----------

Cloud
~~~~~

misc
^^^^

- proxmox_nic - Management of a NIC of a Qemu(KVM) VM in a Proxmox VE cluster.
- proxmox_tasks_info - Retrieve information about one or more Proxmox VE tasks

Database
~~~~~~~~

misc
^^^^

- redis_data - Set key value pairs in Redis
- redis_data_incr - Increment keys in Redis
- redis_data_info - Get value of key in Redis database

mssql
^^^^^

- mssql_script - Execute SQL scripts on a MSSQL database

saphana
^^^^^^^

- hana_query - Execute SQL on HANA

Files
~~~~~

- sapcar_extract - Manages SAP SAPCAR archives

Identity
~~~~~~~~

keycloak
^^^^^^^^

- keycloak_authentication - Configure authentication in Keycloak
- keycloak_client_rolemapping - Allows administration of Keycloak client_rolemapping with the Keycloak API
- keycloak_clientscope - Allows administration of Keycloak client_scopes via Keycloak API
- keycloak_identity_provider - Allows administration of Keycloak identity providers via Keycloak API
- keycloak_role - Allows administration of Keycloak roles via Keycloak API
- keycloak_user_federation - Allows administration of Keycloak user federations via Keycloak API

Notification
~~~~~~~~~~~~

- discord - Send Discord messages

Packaging
~~~~~~~~~

language
^^^^^^^^

- ansible_galaxy_install - Install Ansible roles or collections using ansible-galaxy
- pipx - Manages applications installed with pipx

os
^^

- dnf_versionlock - Locks package versions in C(dnf) based systems
- pacman_key - Manage pacman's list of trusted keys
- snap_alias - Manages snap aliases

Source Control
~~~~~~~~~~~~~~

gitlab
^^^^^^

- gitlab_protected_branch - (un)Marking existing branches for protection

System
~~~~~~

- sap_task_list_execute - Perform SAP Task list execution
- xfconf_info - Retrieve XFCE4 configurations

Web Infrastructure
~~~~~~~~~~~~~~~~~~

- rundeck_job_executions_info - Query executions for a Rundeck job
- rundeck_job_run - Run a Rundeck job
