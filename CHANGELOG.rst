===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 7.0.0.

v8.3.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- consul_auth_method, consul_binding_rule, consul_policy, consul_role, consul_session, consul_token - added action group ``community.general.consul`` (https://github.com/ansible-collections/community.general/pull/7897).
- consul_policy - added support for diff and check mode (https://github.com/ansible-collections/community.general/pull/7878).
- consul_policy, consul_role, consul_session - removed dependency on ``requests`` and factored out common parts (https://github.com/ansible-collections/community.general/pull/7826, https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - ``node_identities`` now expects a ``node_name`` option to match the Consul API, the old ``name`` is still supported as alias (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - ``service_identities`` now expects a ``service_name`` option to match the Consul API, the old ``name`` is still supported as alias (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - added support for diff mode (https://github.com/ansible-collections/community.general/pull/7878).
- consul_role - added support for templated policies (https://github.com/ansible-collections/community.general/pull/7878).
- redfish_info - add command ``GetServiceIdentification`` to get service identification (https://github.com/ansible-collections/community.general/issues/7882).
- terraform - add support for ``diff_mode`` for terraform resource_changes (https://github.com/ansible-collections/community.general/pull/7896).

Deprecated Features
-------------------

- consul_acl - the module has been deprecated and will be removed in community.general 10.0.0. ``consul_token`` and ``consul_policy`` can be used instead (https://github.com/ansible-collections/community.general/pull/7901).

Bugfixes
--------

- homebrew - detect already installed formulae and casks using JSON output from ``brew info`` (https://github.com/ansible-collections/community.general/issues/864).
- incus connection plugin - treats ``inventory_hostname`` as a variable instead of a literal in remote connections (https://github.com/ansible-collections/community.general/issues/7874).
- ipa_otptoken - the module expect ``ipatokendisabled`` as string but the ``ipatokendisabled`` value is returned as a boolean (https://github.com/ansible-collections/community.general/pull/7795).
- ldap - previously the order number (if present) was expected to follow an equals sign in the DN. This makes it so the order number string is identified correctly anywhere within the DN (https://github.com/ansible-collections/community.general/issues/7646).
- mssql_script - make the module work with Python 2 (https://github.com/ansible-collections/community.general/issues/7818, https://github.com/ansible-collections/community.general/pull/7821).
- nmcli - fix ``connection.slave-type`` wired to ``bond`` and not with parameter ``slave_type`` in case of connection type ``wifi`` (https://github.com/ansible-collections/community.general/issues/7389).
- proxmox - fix updating a container config if the setting does not already exist (https://github.com/ansible-collections/community.general/pull/7872).

New Modules
-----------

- consul_acl_bootstrap - Bootstrap ACLs in Consul
- consul_auth_method - Manipulate Consul auth methods
- consul_binding_rule - Manipulate Consul binding rules
- consul_token - Manipulate Consul tokens
- gitlab_label - Creates/updates/deletes GitLab Labels belonging to project or group.
- gitlab_milestone - Creates/updates/deletes GitLab Milestones belonging to project or group

v8.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- ipa_dnsrecord - adds ability to manage NS record types (https://github.com/ansible-collections/community.general/pull/7737).
- ipa_pwpolicy - refactor module and exchange a sequence ``if`` statements with a ``for`` loop (https://github.com/ansible-collections/community.general/pull/7723).
- ipa_pwpolicy - update module to support ``maxrepeat``, ``maxsequence``, ``dictcheck``, ``usercheck``, ``gracelimit`` parameters in FreeIPA password policies (https://github.com/ansible-collections/community.general/pull/7723).
- keycloak_realm_key - the ``config.algorithm`` option now supports 8 additional key algorithms (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_realm_key - the ``config.certificate`` option value is no longer defined with ``no_log=True`` (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_realm_key - the ``provider_id`` option now supports RSA encryption key usage (value ``rsa-enc``) (https://github.com/ansible-collections/community.general/pull/7698).
- keycloak_user_federation - allow custom user storage providers to be set through ``provider_id`` (https://github.com/ansible-collections/community.general/pull/7789).
- mail - add ``Message-ID`` header; which is required by some mail servers (https://github.com/ansible-collections/community.general/pull/7740).
- mail module, mail callback plugin - allow to configure the domain name of the Message-ID header with a new ``message_id_domain`` option (https://github.com/ansible-collections/community.general/pull/7765).
- ssh_config - new feature to set ``AddKeysToAgent`` option to ``yes`` or ``no`` (https://github.com/ansible-collections/community.general/pull/7703).
- ssh_config - new feature to set ``IdentitiesOnly`` option to ``yes`` or ``no`` (https://github.com/ansible-collections/community.general/pull/7704).
- xcc_redfish_command - added support for raw POSTs (``command=PostResource`` in ``category=Raw``) without a specific action info (https://github.com/ansible-collections/community.general/pull/7746).

Bugfixes
--------

- keycloak_identity_provider - ``mappers`` processing was not idempotent if the mappers configuration list had not been sorted by name (in ascending order). Fix resolves the issue by sorting mappers in the desired state using the same key which is used for obtaining existing state (https://github.com/ansible-collections/community.general/pull/7418).
- keycloak_identity_provider - it was not possible to reconfigure (add, remove) ``mappers`` once they were created initially. Removal was ignored, adding new ones resulted in dropping the pre-existing unmodified mappers. Fix resolves the issue by supplying correct input to the internal update call (https://github.com/ansible-collections/community.general/pull/7418).
- keycloak_user - when ``force`` is set, but user does not exist, do not try to delete it (https://github.com/ansible-collections/community.general/pull/7696).
- proxmox_kvm - running ``state=template`` will first check whether VM is already a template (https://github.com/ansible-collections/community.general/pull/7792).
- statusio_maintenance - fix error caused by incorrectly formed API data payload. Was raising "Failed to create maintenance HTTP Error 400 Bad Request" caused by bad data type for date/time and deprecated dict keys (https://github.com/ansible-collections/community.general/pull/7754).

New Plugins
-----------

Connection
~~~~~~~~~~

- incus - Run tasks in Incus instances via the Incus CLI.

Filter
~~~~~~

- from_ini - Converts INI text input into a dictionary
- to_ini - Converts a dictionary to the INI file format

Lookup
~~~~~~

- github_app_access_token - Obtain short-lived Github App Access tokens

New Modules
-----------

- dnf_config_manager - Enable or disable dnf repositories using config-manager
- keycloak_component_info - Retrive component info in Keycloak
- keycloak_realm_rolemapping - Allows administration of Keycloak realm role mappings into groups with the Keycloak API
- proxmox_node_info - Retrieve information about one or more Proxmox VE nodes
- proxmox_storage_contents_info - List content from a Proxmox VE storage

v8.1.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- bitwarden lookup plugin - when looking for items using an item ID, the item is now accessed directly with ``bw get item`` instead of searching through all items. This doubles the lookup speed (https://github.com/ansible-collections/community.general/pull/7468).
- elastic callback plugin - close elastic client to not leak resources (https://github.com/ansible-collections/community.general/pull/7517).
- git_config - allow multiple git configs for the same name with the new ``add_mode`` option (https://github.com/ansible-collections/community.general/pull/7260).
- git_config - the ``after`` and ``before`` fields in the ``diff`` of the return value can be a list instead of a string in case more configs with the same key are affected (https://github.com/ansible-collections/community.general/pull/7260).
- git_config - when a value is unset, all configs with the same key are unset (https://github.com/ansible-collections/community.general/pull/7260).
- gitlab modules - add ``ca_path`` option (https://github.com/ansible-collections/community.general/pull/7472).
- gitlab modules - remove duplicate ``gitlab`` package check (https://github.com/ansible-collections/community.general/pull/7486).
- gitlab_runner - add support for new runner creation workflow (https://github.com/ansible-collections/community.general/pull/7199).
- ipa_config - adds ``passkey`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7588).
- ipa_sudorule - adds options to include denied commands or command groups (https://github.com/ansible-collections/community.general/pull/7415).
- ipa_user - adds ``idp`` and ``passkey`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7589).
- irc - add ``validate_certs`` option, and rename ``use_ssl`` to ``use_tls``, while keeping ``use_ssl`` as an alias. The default value for ``validate_certs`` is ``false`` for backwards compatibility. We recommend to every user of this module to explicitly set ``use_tls=true`` and `validate_certs=true`` whenever possible, especially when communicating to IRC servers over the internet (https://github.com/ansible-collections/community.general/pull/7550).
- keycloak module utils - expose error message from Keycloak server for HTTP errors in some specific situations (https://github.com/ansible-collections/community.general/pull/7645).
- keycloak_user_federation - add option for ``krbPrincipalAttribute`` (https://github.com/ansible-collections/community.general/pull/7538).
- lvol - change ``pvs`` argument type to list of strings (https://github.com/ansible-collections/community.general/pull/7676, https://github.com/ansible-collections/community.general/issues/7504).
- lxd connection plugin - tighten the detection logic for lxd ``Instance not found`` errors, to avoid false detection on unrelated errors such as ``/usr/bin/python3: not found`` (https://github.com/ansible-collections/community.general/pull/7521).
- netcup_dns - adds support for record types ``OPENPGPKEY``, ``SMIMEA``, and ``SSHFP`` (https://github.com/ansible-collections/community.general/pull/7489).
- nmcli - add support for new connection type ``loopback`` (https://github.com/ansible-collections/community.general/issues/6572).
- nmcli - allow for ``infiniband`` slaves of ``bond`` interface types (https://github.com/ansible-collections/community.general/pull/7569).
- nmcli - allow for the setting of ``MTU`` for ``infiniband`` and ``bond`` interface types (https://github.com/ansible-collections/community.general/pull/7499).
- onepassword lookup plugin - support 1Password Connect with the opv2 client by setting the connect_host and connect_token parameters (https://github.com/ansible-collections/community.general/pull/7116).
- onepassword_raw lookup plugin - support 1Password Connect with the opv2 client by setting the connect_host and connect_token parameters (https://github.com/ansible-collections/community.general/pull/7116)
- passwordstore - adds ``timestamp`` and ``preserve`` parameters to modify the stored password format (https://github.com/ansible-collections/community.general/pull/7426).
- proxmox - adds ``template`` value to the ``state`` parameter, allowing conversion of container to a template (https://github.com/ansible-collections/community.general/pull/7143).
- proxmox - adds ``update`` parameter, allowing update of an already existing containers configuration (https://github.com/ansible-collections/community.general/pull/7540).
- proxmox inventory plugin - adds an option to exclude nodes from the dynamic inventory generation. The new setting is optional, not using this option will behave as usual (https://github.com/ansible-collections/community.general/issues/6714, https://github.com/ansible-collections/community.general/pull/7461).
- proxmox_disk - add ability to manipulate CD-ROM drive (https://github.com/ansible-collections/community.general/pull/7495).
- proxmox_kvm - adds ``template`` value to the ``state`` parameter, allowing conversion of a VM to a template (https://github.com/ansible-collections/community.general/pull/7143).
- proxmox_kvm - support the ``hookscript`` parameter (https://github.com/ansible-collections/community.general/issues/7600).
- proxmox_ostype - it is now possible to specify the ``ostype`` when creating an LXC container (https://github.com/ansible-collections/community.general/pull/7462).
- proxmox_vm_info - add ability to retrieve configuration info (https://github.com/ansible-collections/community.general/pull/7485).
- redfish_info - adding the ``BootProgress`` property when getting ``Systems`` info (https://github.com/ansible-collections/community.general/pull/7626).
- ssh_config - adds ``controlmaster``, ``controlpath`` and ``controlpersist`` parameters (https://github.com/ansible-collections/community.general/pull/7456).

Bugfixes
--------

- apt-rpm - the module did not upgrade packages if a newer version exists. Now the package will be reinstalled if the candidate is newer than the installed version (https://github.com/ansible-collections/community.general/issues/7414).
- cloudflare_dns - fix Cloudflare lookup of SHFP records (https://github.com/ansible-collections/community.general/issues/7652).
- interface_files - also consider ``address_family`` when changing ``option=method`` (https://github.com/ansible-collections/community.general/issues/7610, https://github.com/ansible-collections/community.general/pull/7612).
- irc - replace ``ssl.wrap_socket`` that was removed from Python 3.12 with code for creating a proper SSL context (https://github.com/ansible-collections/community.general/pull/7542).
- keycloak_* - fix Keycloak API client to quote ``/`` properly (https://github.com/ansible-collections/community.general/pull/7641).
- keycloak_authz_permission - resource payload variable for scope-based permission was constructed as a string, when it needs to be a list, even for a single item (https://github.com/ansible-collections/community.general/issues/7151).
- log_entries callback plugin - replace ``ssl.wrap_socket`` that was removed from Python 3.12 with code for creating a proper SSL context (https://github.com/ansible-collections/community.general/pull/7542).
- lvol - test for output messages in both ``stdout`` and ``stderr`` (https://github.com/ansible-collections/community.general/pull/7601, https://github.com/ansible-collections/community.general/issues/7182).
- onepassword lookup plugin - field and section titles are now case insensitive when using op CLI version two or later. This matches the behavior of version one (https://github.com/ansible-collections/community.general/pull/7564).
- redhat_subscription - use the D-Bus registration on RHEL 7 only on 7.4 and
  greater; older versions of RHEL 7 do not have it
  (https://github.com/ansible-collections/community.general/issues/7622,
  https://github.com/ansible-collections/community.general/pull/7624).
- terraform - fix multiline string handling in complex variables (https://github.com/ansible-collections/community.general/pull/7535).

New Plugins
-----------

Lookup
~~~~~~

- onepassword_doc - Fetch documents stored in 1Password

Test
~~~~

- fqdn_valid - Validates fully-qualified domain names against RFC 1123

New Modules
-----------

- git_config_info - Read git configuration
- gitlab_issue - Create, update, or delete GitLab issues
- nomad_token - Manage Nomad ACL tokens

v8.0.2
======

Release Summary
---------------

Bugfix release for inclusion in Ansible 9.0.0rc1.

Bugfixes
--------

- ocapi_utils, oci_utils, redfish_utils module utils - replace ``type()`` calls with ``isinstance()`` calls (https://github.com/ansible-collections/community.general/pull/7501).
- pipx module utils - change the CLI argument formatter for the ``pip_args`` parameter (https://github.com/ansible-collections/community.general/issues/7497, https://github.com/ansible-collections/community.general/pull/7506).

v8.0.1
======

Release Summary
---------------

Bugfix release for inclusion in Ansible 9.0.0b1.

Bugfixes
--------

- gitlab_group_members - fix gitlab constants call in ``gitlab_group_members`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_project_members - fix gitlab constants call in ``gitlab_project_members`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_protected_branches - fix gitlab constants call in ``gitlab_protected_branches`` module (https://github.com/ansible-collections/community.general/issues/7467).
- gitlab_user - fix gitlab constants call in ``gitlab_user`` module (https://github.com/ansible-collections/community.general/issues/7467).
- proxmox_pool_member - absent state for type VM did not delete VMs from the pools (https://github.com/ansible-collections/community.general/pull/7464).
- redfish_command - fix usage of message parsing in ``SimpleUpdate`` and ``MultipartHTTPPushUpdate`` commands to treat the lack of a ``MessageId`` as no message (https://github.com/ansible-collections/community.general/issues/7465, https://github.com/ansible-collections/community.general/pull/7471).

v8.0.0
======

Release Summary
---------------

This is release 8.0.0 of ``community.general``, released on 2023-11-01.

Minor Changes
-------------

- The collection will start using semantic markup (https://github.com/ansible-collections/community.general/pull/6539).
- VarDict module utils - add method ``VarDict.as_dict()`` to convert to a plain ``dict`` object (https://github.com/ansible-collections/community.general/pull/6602).
- apt_rpm - extract package name from local ``.rpm`` path when verifying
  installation success. Allows installing packages from local ``.rpm`` files
  (https://github.com/ansible-collections/community.general/pull/7396).
- cargo - add option ``executable``, which allows user to specify path to the cargo binary (https://github.com/ansible-collections/community.general/pull/7352).
- cargo - add option ``locked`` which allows user to specify install the locked version of dependency instead of latest compatible version (https://github.com/ansible-collections/community.general/pull/6134).
- chroot connection plugin - add ``disable_root_check`` option (https://github.com/ansible-collections/community.general/pull/7099).
- cloudflare_dns - add CAA record support (https://github.com/ansible-collections/community.general/pull/7399).
- cobbler inventory plugin - add ``exclude_mgmt_classes`` and ``include_mgmt_classes`` options to exclude or include hosts based on management classes (https://github.com/ansible-collections/community.general/pull/7184).
- cobbler inventory plugin - add ``inventory_hostname`` option to allow using the system name for the inventory hostname (https://github.com/ansible-collections/community.general/pull/6502).
- cobbler inventory plugin - add ``want_ip_addresses`` option to collect all interface DNS name to IP address mapping (https://github.com/ansible-collections/community.general/pull/6711).
- cobbler inventory plugin - add primary IP addess to ``cobbler_ipv4_address`` and IPv6 address to ``cobbler_ipv6_address`` host variable (https://github.com/ansible-collections/community.general/pull/6711).
- cobbler inventory plugin - add warning for systems with empty profiles (https://github.com/ansible-collections/community.general/pull/6502).
- cobbler inventory plugin - convert Ansible unicode strings to native Python unicode strings before passing user/password to XMLRPC client (https://github.com/ansible-collections/community.general/pull/6923).
- consul_session - drops requirement for the ``python-consul`` library to communicate with the Consul API, instead relying on the existing ``requests`` library requirement (https://github.com/ansible-collections/community.general/pull/6755).
- copr - respawn module to use the system python interpreter when the ``dnf`` python module is not available in ``ansible_python_interpreter`` (https://github.com/ansible-collections/community.general/pull/6522).
- cpanm - minor refactor when creating the ``CmdRunner`` object (https://github.com/ansible-collections/community.general/pull/7231).
- datadog_monitor - adds ``notification_preset_name``, ``renotify_occurrences`` and ``renotify_statuses`` parameters (https://github.com/ansible-collections/community.general/issues/6521,https://github.com/ansible-collections/community.general/issues/5823).
- dig lookup plugin - add TCP option to enable the use of TCP connection during DNS lookup (https://github.com/ansible-collections/community.general/pull/7343).
- ejabberd_user - module now using ``CmdRunner`` to execute external command (https://github.com/ansible-collections/community.general/pull/7075).
- filesystem - add ``uuid`` parameter for UUID change feature (https://github.com/ansible-collections/community.general/pull/6680).
- gitlab_group - add option ``force_delete`` (default: false) which allows delete group even if projects exists in it (https://github.com/ansible-collections/community.general/pull/7364).
- gitlab_group_variable - add support for ``raw`` variables suboption (https://github.com/ansible-collections/community.general/pull/7132).
- gitlab_project_variable - add support for ``raw`` variables suboption (https://github.com/ansible-collections/community.general/pull/7132).
- gitlab_project_variable - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- gitlab_runner - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6927).
- htpasswd - minor code improvements in the module (https://github.com/ansible-collections/community.general/pull/6901).
- htpasswd - the parameter ``crypt_scheme`` is being renamed as ``hash_scheme`` and added as an alias to it (https://github.com/ansible-collections/community.general/pull/6841).
- icinga2_host - the ``ip`` option is no longer required, since Icinga 2 allows for an empty address attribute (https://github.com/ansible-collections/community.general/pull/7452).
- ini_file - add ``ignore_spaces`` option (https://github.com/ansible-collections/community.general/pull/7273).
- ini_file - add ``modify_inactive_option`` option (https://github.com/ansible-collections/community.general/pull/7401).
- ipa_config - add module parameters to manage FreeIPA user and group objectclasses (https://github.com/ansible-collections/community.general/pull/7019).
- ipa_config - adds ``idp`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7051).
- jenkins_build - add new ``detach`` option, which allows the module to exit successfully as long as the build is created (default functionality is still waiting for the build to end before exiting) (https://github.com/ansible-collections/community.general/pull/7204).
- jenkins_build - add new ``time_between_checks`` option, which allows to configure the wait time between requests to the Jenkins server (https://github.com/ansible-collections/community.general/pull/7204).
- keycloak_authentication - added provider ID choices, since Keycloak supports only those two specific ones (https://github.com/ansible-collections/community.general/pull/6763).
- keycloak_client_rolemapping - adds support for subgroups with additional parameter ``parents`` (https://github.com/ansible-collections/community.general/pull/6687).
- keycloak_role - add composite roles support for realm and client roles (https://github.com/ansible-collections/community.general/pull/6469).
- keyring - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6927).
- ldap_* - add new arguments ``client_cert`` and ``client_key`` to the LDAP modules in order to allow certificate authentication (https://github.com/ansible-collections/community.general/pull/6668).
- ldap_search - add a new ``page_size`` option to enable paged searches (https://github.com/ansible-collections/community.general/pull/6648).
- locale_gen - module has been refactored to use ``ModuleHelper`` and ``CmdRunner`` (https://github.com/ansible-collections/community.general/pull/6903).
- locale_gen - module now using ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6820).
- lvg - add ``active`` and ``inactive`` values to the ``state`` option for active state management feature (https://github.com/ansible-collections/community.general/pull/6682).
- lvg - add ``reset_vg_uuid``, ``reset_pv_uuid`` options for UUID reset feature (https://github.com/ansible-collections/community.general/pull/6682).
- lxc connection plugin - properly handle a change of the ``remote_addr`` option (https://github.com/ansible-collections/community.general/pull/7373).
- lxd connection plugin - automatically translate ``remote_addr`` from FQDN to (short) hostname (https://github.com/ansible-collections/community.general/pull/7360).
- lxd connection plugin - update error parsing to work with newer messages mentioning instances (https://github.com/ansible-collections/community.general/pull/7360).
- lxd inventory plugin - add ``server_cert`` option for trust anchor to use for TLS verification of server certificates (https://github.com/ansible-collections/community.general/pull/7392).
- lxd inventory plugin - add ``server_check_hostname`` option to disable hostname verification of server certificates (https://github.com/ansible-collections/community.general/pull/7392).
- make - add new ``targets`` parameter allowing multiple targets to be used with ``make`` (https://github.com/ansible-collections/community.general/pull/6882, https://github.com/ansible-collections/community.general/issues/4919).
- make - allows ``params`` to be used without value (https://github.com/ansible-collections/community.general/pull/7180).
- mas - disable sign-in check for macOS 12+ as ``mas account`` is non-functional (https://github.com/ansible-collections/community.general/pull/6520).
- newrelic_deployment - add option ``app_name_exact_match``, which filters results for the exact app_name provided (https://github.com/ansible-collections/community.general/pull/7355).
- nmap inventory plugin - now has a ``use_arp_ping`` option to allow the user to disable the default ARP ping query for a more reliable form (https://github.com/ansible-collections/community.general/pull/7119).
- nmcli - add support for ``ipv4.dns-options`` and ``ipv6.dns-options`` (https://github.com/ansible-collections/community.general/pull/6902).
- nomad_job, nomad_job_info - add ``port`` parameter (https://github.com/ansible-collections/community.general/pull/7412).
- npm - minor improvement on parameter validation (https://github.com/ansible-collections/community.general/pull/6848).
- npm - module now using ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6989).
- onepassword lookup plugin - add service account support (https://github.com/ansible-collections/community.general/issues/6635, https://github.com/ansible-collections/community.general/pull/6660).
- onepassword lookup plugin - introduce ``account_id`` option which allows specifying which account to use (https://github.com/ansible-collections/community.general/pull/7308).
- onepassword_raw lookup plugin - add service account support (https://github.com/ansible-collections/community.general/issues/6635, https://github.com/ansible-collections/community.general/pull/6660).
- onepassword_raw lookup plugin - introduce ``account_id`` option which allows specifying which account to use (https://github.com/ansible-collections/community.general/pull/7308).
- opentelemetry callback plugin - add span attributes in the span event (https://github.com/ansible-collections/community.general/pull/6531).
- opkg - add ``executable`` parameter allowing to specify the path of the ``opkg`` command (https://github.com/ansible-collections/community.general/pull/6862).
- opkg - remove default value ``""`` for parameter ``force`` as it causes the same behaviour of not having that parameter (https://github.com/ansible-collections/community.general/pull/6513).
- pagerduty - adds in option to use v2 API for creating pagerduty incidents (https://github.com/ansible-collections/community.general/issues/6151)
- parted - on resize, use ``--fix`` option if available (https://github.com/ansible-collections/community.general/pull/7304).
- pnpm - set correct version when state is latest or version is not mentioned. Resolves previous idempotency problem (https://github.com/ansible-collections/community.general/pull/7339).
- pritunl module utils - ensure ``validate_certs`` parameter is honoured in all methods (https://github.com/ansible-collections/community.general/pull/7156).
- proxmox - add ``vmid`` (and ``taskid`` when possible) to return values (https://github.com/ansible-collections/community.general/pull/7263).
- proxmox - support ``timezone`` parameter at container creation (https://github.com/ansible-collections/community.general/pull/6510).
- proxmox inventory plugin - add composite variables support for Proxmox nodes (https://github.com/ansible-collections/community.general/issues/6640).
- proxmox_kvm - added support for ``tpmstate0`` parameter to configure TPM (Trusted Platform Module) disk. TPM is required for Windows 11 installations (https://github.com/ansible-collections/community.general/pull/6533).
- proxmox_kvm - enabled force restart of VM, bringing the ``force`` parameter functionality in line with what is described in the docs (https://github.com/ansible-collections/community.general/pull/6914).
- proxmox_kvm - re-use ``timeout`` module param to forcefully shutdown a virtual machine when ``state`` is ``stopped`` (https://github.com/ansible-collections/community.general/issues/6257).
- proxmox_snap - add ``retention`` parameter to delete old snapshots (https://github.com/ansible-collections/community.general/pull/6576).
- proxmox_vm_info - ``node`` parameter is no longer required. Information can be obtained for the whole cluster (https://github.com/ansible-collections/community.general/pull/6976).
- proxmox_vm_info - non-existing provided by name/vmid VM would return empty results instead of failing (https://github.com/ansible-collections/community.general/pull/7049).
- pubnub_blocks - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- random_string - added new ``ignore_similar_chars`` and ``similar_chars`` option to ignore certain chars (https://github.com/ansible-collections/community.general/pull/7242).
- redfish_command - add ``MultipartHTTPPushUpdate`` command (https://github.com/ansible-collections/community.general/issues/6471, https://github.com/ansible-collections/community.general/pull/6612).
- redfish_command - add ``account_types`` and ``oem_account_types`` as optional inputs to ``AddUser`` (https://github.com/ansible-collections/community.general/issues/6823, https://github.com/ansible-collections/community.general/pull/6871).
- redfish_command - add new option ``update_oem_params`` for the ``MultipartHTTPPushUpdate`` command (https://github.com/ansible-collections/community.general/issues/7331).
- redfish_config - add ``CreateVolume`` command to allow creation of volumes on servers (https://github.com/ansible-collections/community.general/pull/6813).
- redfish_config - add ``DeleteAllVolumes`` command to allow deletion of all volumes on servers (https://github.com/ansible-collections/community.general/pull/6814).
- redfish_config - adding ``SetSecureBoot`` command (https://github.com/ansible-collections/community.general/pull/7129).
- redfish_info - add ``AccountTypes`` and ``OEMAccountTypes`` to the output of ``ListUsers`` (https://github.com/ansible-collections/community.general/issues/6823, https://github.com/ansible-collections/community.general/pull/6871).
- redfish_info - add support for ``GetBiosRegistries`` command (https://github.com/ansible-collections/community.general/pull/7144).
- redfish_info - adds ``LinkStatus`` to NIC inventory (https://github.com/ansible-collections/community.general/pull/7318).
- redfish_info - adds ``ProcessorArchitecture`` to CPU inventory (https://github.com/ansible-collections/community.general/pull/6864).
- redfish_info - fix for ``GetVolumeInventory``, Controller name was getting populated incorrectly and duplicates were seen in the volumes retrieved (https://github.com/ansible-collections/community.general/pull/6719).
- redfish_info - report ``Id`` in the output of ``GetManagerInventory`` (https://github.com/ansible-collections/community.general/pull/7140).
- redfish_utils - use ``Controllers`` key in redfish data to obtain Storage controllers properties (https://github.com/ansible-collections/community.general/pull/7081).
- redfish_utils module utils - add support for ``PowerCycle`` reset type for ``redfish_command`` responses feature (https://github.com/ansible-collections/community.general/issues/7083).
- redfish_utils module utils - add support for following ``@odata.nextLink`` pagination in ``software_inventory`` responses feature (https://github.com/ansible-collections/community.general/pull/7020).
- redfish_utils module utils - support ``Volumes`` in response for ``GetDiskInventory`` (https://github.com/ansible-collections/community.general/pull/6819).
- redhat_subscription - the internal ``RegistrationBase`` class was folded
  into the other internal ``Rhsm`` class, as the separation had no purpose
  anymore
  (https://github.com/ansible-collections/community.general/pull/6658).
- redis_info - refactor the redis_info module to use the redis module_utils enabling to pass TLS parameters to the Redis client (https://github.com/ansible-collections/community.general/pull/7267).
- rhsm_release - improve/harden the way ``subscription-manager`` is run;
  no behaviour change is expected
  (https://github.com/ansible-collections/community.general/pull/6669).
- rhsm_repository - the interaction with ``subscription-manager`` was
  refactored by grouping things together, removing unused bits, and hardening
  the way it is run; also, the parsing of ``subscription-manager repos --list``
  was improved and made slightly faster; no behaviour change is expected
  (https://github.com/ansible-collections/community.general/pull/6783,
  https://github.com/ansible-collections/community.general/pull/6837).
- scaleway_security_group_rule - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- shutdown - use ``shutdown -p ...`` with FreeBSD to halt and power off machine (https://github.com/ansible-collections/community.general/pull/7102).
- snap - add option ``dangerous`` to the module, that will map into the command line argument ``--dangerous``, allowing unsigned snap files to be installed (https://github.com/ansible-collections/community.general/pull/6908, https://github.com/ansible-collections/community.general/issues/5715).
- snap - module is now aware of channel when deciding whether to install or refresh the snap (https://github.com/ansible-collections/community.general/pull/6435, https://github.com/ansible-collections/community.general/issues/1606).
- sorcery - add grimoire (repository) management support (https://github.com/ansible-collections/community.general/pull/7012).
- sorcery - minor refactor (https://github.com/ansible-collections/community.general/pull/6525).
- supervisorctl - allow to stop matching running processes before removing them with ``stop_before_removing=true`` (https://github.com/ansible-collections/community.general/pull/7284).
- tss lookup plugin - allow to fetch secret IDs which are in a folder based on folder ID. Previously, we could not fetch secrets based on folder ID but now use ``fetch_secret_ids_from_folder`` option to indicate to fetch secret IDs based on folder ID (https://github.com/ansible-collections/community.general/issues/6223).
- tss lookup plugin - allow to fetch secret by path. Previously, we could not fetch secret by path but now use ``secret_path`` option to indicate to fetch secret by secret path (https://github.com/ansible-collections/community.general/pull/6881).
- unixy callback plugin - add support for ``check_mode_markers`` option (https://github.com/ansible-collections/community.general/pull/7179).
- vardict module utils - added convenience methods to ``VarDict`` (https://github.com/ansible-collections/community.general/pull/6647).
- xenserver_guest_info - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- xenserver_guest_powerstate - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- yum_versionlock - add support to pin specific package versions instead of only the package itself (https://github.com/ansible-collections/community.general/pull/6861, https://github.com/ansible-collections/community.general/issues/4470).

Breaking Changes / Porting Guide
--------------------------------

- collection_version lookup plugin - remove compatibility code for ansible-base 2.10 and ansible-core 2.11 (https://github.com/ansible-collections/community.general/pull/7269).
- gitlab_project - add ``default_branch`` support for project update. If you used the module so far with ``default_branch`` to update a project, the value of ``default_branch`` was ignored. Make sure that you either do not pass a value if you are not sure whether it is the one you want to have to avoid unexpected breaking changes (https://github.com/ansible-collections/community.general/pull/7158).
- selective callback plugin - remove compatibility code for Ansible 2.9 and ansible-core 2.10 (https://github.com/ansible-collections/community.general/pull/7269).
- vardict module utils - ``VarDict`` will no longer accept variables named ``_var``, ``get_meta``, and ``as_dict`` (https://github.com/ansible-collections/community.general/pull/6647).
- version module util - remove fallback for ansible-core 2.11. All modules and plugins that do version collections no longer work with ansible-core 2.11 (https://github.com/ansible-collections/community.general/pull/7269).

Deprecated Features
-------------------

- CmdRunner module utils - deprecate ``cmd_runner_fmt.as_default_type()`` formatter (https://github.com/ansible-collections/community.general/pull/6601).
- MH VarsMixin module utils - deprecates ``VarsMixin`` and supporting classes in favor of plain ``vardict`` module util (https://github.com/ansible-collections/community.general/pull/6649).
- ansible_galaxy_install - the ``ack_ansible29`` and ``ack_min_ansiblecore211`` options have been deprecated and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/7358).
- consul - the ``ack_params_state_absent`` option has been deprecated and will be removed in community.general 10.0.0 (https://github.com/ansible-collections/community.general/pull/7358).
- cpanm - value ``compatibility`` is deprecated as default for parameter ``mode`` (https://github.com/ansible-collections/community.general/pull/6512).
- ejabberd_user - deprecate the parameter ``logging`` in favour of producing more detailed information in the module output (https://github.com/ansible-collections/community.general/pull/7043).
- flowdock - module relies entirely on no longer responsive API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6930).
- proxmox - old feature flag ``proxmox_default_behavior`` will be removed in community.general 10.0.0 (https://github.com/ansible-collections/community.general/pull/6836).
- proxmox_kvm - deprecate the option ``proxmox_default_behavior`` (https://github.com/ansible-collections/community.general/pull/7377).
- redfish_info, redfish_config, redfish_command - the default value ``10`` for the ``timeout`` option is deprecated and will change to ``60`` in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/7295).
- redhat module utils - the ``module_utils.redhat`` module is deprecated, as
  effectively unused: the ``Rhsm``, ``RhsmPool``, and ``RhsmPools`` classes
  will be removed in community.general 9.0.0; the ``RegistrationBase`` class
  will be removed in community.general 10.0.0 together with the
  ``rhn_register`` module, as it is the only user of this class; this means
  that the whole ``module_utils.redhat`` module will be dropped in
  community.general 10.0.0, so importing it without even using anything of it
  will fail
  (https://github.com/ansible-collections/community.general/pull/6663).
- redhat_subscription - the ``autosubscribe`` alias for the ``auto_attach`` option has been
  deprecated for many years, although only in the documentation. Officially mark this alias
  as deprecated, and it will be removed in community.general 9.0.0
  (https://github.com/ansible-collections/community.general/pull/6646).
- redhat_subscription - the ``pool`` option is deprecated in favour of the
  more precise and flexible ``pool_ids`` option
  (https://github.com/ansible-collections/community.general/pull/6650).
- rhsm_repository - ``state=present`` has not been working as expected for many years,
  and it seems it was not noticed so far; also, "presence" is not really a valid concept
  for subscription repositories, which can only be enabled or disabled. Hence, mark the
  ``present`` and ``absent`` values of the ``state`` option as deprecated, slating them
  for removal in community.general 10.0.0
  (https://github.com/ansible-collections/community.general/pull/6673).
- stackdriver - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6887).
- webfaction_app - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_db - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_domain - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_mailbox - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_site - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).

Removed Features (previously deprecated)
----------------------------------------

- The collection no longer supports ansible-core 2.11 and ansible-core 2.12. Parts of the collection might still work on these ansible-core versions, but others might not (https://github.com/ansible-collections/community.general/pull/7269).
- ansible_galaxy_install - support for Ansible 2.9 and ansible-base 2.10 has been removed (https://github.com/ansible-collections/community.general/pull/7358).
- consul - when ``state=absent``, the options ``script``, ``ttl``, ``tcp``, ``http``, and ``interval`` can no longer be specified (https://github.com/ansible-collections/community.general/pull/7358).
- gconftool2 - ``state=get`` has been removed. Use the module ``community.general.gconftool2_info`` instead (https://github.com/ansible-collections/community.general/pull/7358).
- gitlab_runner - remove the default value for the ``access_level`` option. To restore the previous behavior, explicitly set it to ``ref_protected`` (https://github.com/ansible-collections/community.general/pull/7358).
- htpasswd - removed code for passlib <1.6 (https://github.com/ansible-collections/community.general/pull/6901).
- manageiq_polices - ``state=list`` has been removed. Use the module ``community.general.manageiq_policies_info`` instead (https://github.com/ansible-collections/community.general/pull/7358).
- manageiq_tags - ``state=list`` has been removed. Use the module ``community.general.manageiq_tags_info`` instead (https://github.com/ansible-collections/community.general/pull/7358).
- mh.mixins.cmd module utils - the ``ArgFormat`` class has been removed (https://github.com/ansible-collections/community.general/pull/7358).
- mh.mixins.cmd module utils - the ``CmdMixin`` mixin has been removed. Use ``community.general.plugins.module_utils.cmd_runner.CmdRunner`` instead (https://github.com/ansible-collections/community.general/pull/7358).
- mh.mixins.cmd module utils - the mh.mixins.cmd module utils has been removed after all its contents were removed (https://github.com/ansible-collections/community.general/pull/7358).
- mh.module_helper module utils - the ``CmdModuleHelper`` and ``CmdStateModuleHelper`` classes have been removed. Use ``community.general.plugins.module_utils.cmd_runner.CmdRunner`` instead (https://github.com/ansible-collections/community.general/pull/7358).
- proxmox module utils - removed unused imports (https://github.com/ansible-collections/community.general/pull/6873).
- xfconf - the deprecated ``disable_facts`` option was removed (https://github.com/ansible-collections/community.general/pull/7358).

Bugfixes
--------

- CmdRunner module utils - does not attempt to resolve path if executable is a relative or absolute path (https://github.com/ansible-collections/community.general/pull/7200).
- MH DependencyMixin module utils - deprecation notice was popping up for modules not using dependencies (https://github.com/ansible-collections/community.general/pull/6644, https://github.com/ansible-collections/community.general/issues/6639).
- bitwarden lookup plugin - the plugin made assumptions about the structure of a Bitwarden JSON object which may have been broken by an update in the Bitwarden API. Remove assumptions, and allow queries for general fields such as ``notes`` (https://github.com/ansible-collections/community.general/pull/7061).
- cmd_runner module utils - when a parameter in ``argument_spec`` has no type, meaning it is implicitly a ``str``, ``CmdRunner`` would fail trying to find the ``type`` key in that dictionary (https://github.com/ansible-collections/community.general/pull/6968).
- cobbler inventory plugin - fix calculation of cobbler_ipv4/6_address (https://github.com/ansible-collections/community.general/pull/6925).
- composer - fix impossible to run ``working_dir`` dependent commands. The module was throwing an error when trying to run a ``working_dir`` dependent command, because it tried to get the command help without passing the ``working_dir`` (https://github.com/ansible-collections/community.general/issues/3787).
- csv module utils - detects and remove unicode BOM markers from incoming CSV content (https://github.com/ansible-collections/community.general/pull/6662).
- datadog_downtime - presence of ``rrule`` param lead to the Datadog API returning Bad Request due to a missing recurrence type (https://github.com/ansible-collections/community.general/pull/6811).
- ejabberd_user - module was failing to detect whether user was already created and/or password was changed (https://github.com/ansible-collections/community.general/pull/7033).
- ejabberd_user - provide meaningful error message when the ``ejabberdctl`` command is not found (https://github.com/ansible-collections/community.general/pull/7028, https://github.com/ansible-collections/community.general/issues/6949).
- github_deploy_key - fix pagination behaviour causing a crash when only a single page of deploy keys exist (https://github.com/ansible-collections/community.general/pull/7375).
- gitlab_group - the module passed parameters to the API call even when not set. The module is now filtering out ``None`` values to remediate this (https://github.com/ansible-collections/community.general/pull/6712).
- gitlab_group_variable - deleted all variables when used with ``purge=true`` due to missing ``raw`` property in KNOWN attributes (https://github.com/ansible-collections/community.general/issues/7250).
- gitlab_project_variable - deleted all variables when used with ``purge=true`` due to missing ``raw`` property in KNOWN attributes (https://github.com/ansible-collections/community.general/issues/7250).
- icinga2_host - fix a key error when updating an existing host (https://github.com/ansible-collections/community.general/pull/6748).
- ini_file - add the ``follow`` paramter to follow the symlinks instead of replacing them (https://github.com/ansible-collections/community.general/pull/6546).
- ini_file - fix a bug where the inactive options were not used when possible (https://github.com/ansible-collections/community.general/pull/6575).
- ipa_dnszone - fix 'idnsallowsyncptr' key error for reverse zone (https://github.com/ansible-collections/community.general/pull/6906, https://github.com/ansible-collections/community.general/issues/6905).
- kernel_blacklist - simplified the mechanism to update the file, fixing the error (https://github.com/ansible-collections/community.general/pull/7382, https://github.com/ansible-collections/community.general/issues/7362).
- keycloak module util - fix missing ``http_agent``, ``timeout``, and ``validate_certs`` ``open_url()`` parameters (https://github.com/ansible-collections/community.general/pull/7067).
- keycloak module utils - fix ``is_struct_included`` handling of lists of lists/dictionaries (https://github.com/ansible-collections/community.general/pull/6688).
- keycloak module utils - the function ``get_user_by_username`` now return the user representation or ``None`` as stated in the documentation (https://github.com/ansible-collections/community.general/pull/6758).
- keycloak_authentication - fix Keycloak authentication flow (step or sub-flow) indexing during update, if not specified by the user (https://github.com/ansible-collections/community.general/pull/6734).
- keycloak_client inventory plugin - fix missing client secret (https://github.com/ansible-collections/community.general/pull/6931).
- ldap_search - fix string normalization and the ``base64_attributes`` option on Python 3 (https://github.com/ansible-collections/community.general/issues/5704, https://github.com/ansible-collections/community.general/pull/7264).
- locale_gen - now works for locales without the underscore character such as ``C.UTF-8`` (https://github.com/ansible-collections/community.general/pull/6774, https://github.com/ansible-collections/community.general/issues/5142, https://github.com/ansible-collections/community.general/issues/4305).
- lvol - add support for percentage of origin size specification when creating snapshot volumes (https://github.com/ansible-collections/community.general/issues/1630, https://github.com/ansible-collections/community.general/pull/7053).
- lxc connection plugin - now handles ``remote_addr`` defaulting to ``inventory_hostname`` correctly (https://github.com/ansible-collections/community.general/pull/7104).
- lxc connection plugin - properly evaluate options (https://github.com/ansible-collections/community.general/pull/7369).
- machinectl become plugin - mark plugin as ``require_tty`` to automatically disable pipelining, with which this plugin is not compatible (https://github.com/ansible-collections/community.general/issues/6932, https://github.com/ansible-collections/community.general/pull/6935).
- mail - skip headers containing equals characters due to missing ``maxsplit`` on header key/value parsing (https://github.com/ansible-collections/community.general/pull/7303).
- memset module utils - make compatible with ansible-core 2.17 (https://github.com/ansible-collections/community.general/pull/7379).
- nmap inventory plugin - fix ``get_option`` calls (https://github.com/ansible-collections/community.general/pull/7323).
- nmap inventory plugin - now uses ``get_option`` in all cases to get its configuration information (https://github.com/ansible-collections/community.general/pull/7119).
- nmcli - fix bond option ``xmit_hash_policy`` (https://github.com/ansible-collections/community.general/pull/6527).
- nmcli - fix support for empty list (in compare and scrape) (https://github.com/ansible-collections/community.general/pull/6769).
- nsupdate - fix a possible ``list index out of range`` exception (https://github.com/ansible-collections/community.general/issues/836).
- oci_utils module util - fix inappropriate logical comparison expressions and makes them simpler. The previous checks had logical short circuits (https://github.com/ansible-collections/community.general/pull/7125).
- oci_utils module utils - avoid direct type comparisons (https://github.com/ansible-collections/community.general/pull/7085).
- onepassword - fix KeyError exception when trying to access value of a field that is not filled out in OnePassword item (https://github.com/ansible-collections/community.general/pull/7241).
- openbsd_pkg - the pkg_info(1) behavior has changed in OpenBSD >7.3. The error message ``Can't find`` should not lead to an error case (https://github.com/ansible-collections/community.general/pull/6785).
- pacman - module recognizes the output of ``yay`` running as ``root`` (https://github.com/ansible-collections/community.general/pull/6713).
- portage - fix ``changed_use`` and ``newuse`` not triggering rebuilds (https://github.com/ansible-collections/community.general/issues/6008, https://github.com/ansible-collections/community.general/pull/6548).
- pritunl module utils - fix incorrect URL parameter for orgnization add method (https://github.com/ansible-collections/community.general/pull/7161).
- proxmox - fix error when a configuration had no ``template`` field (https://github.com/ansible-collections/community.general/pull/6838, https://github.com/ansible-collections/community.general/issues/5372).
- proxmox module utils - add logic to detect whether an old Promoxer complains about the ``token_name`` and ``token_value`` parameters and provide a better error message when that happens (https://github.com/ansible-collections/community.general/pull/6839, https://github.com/ansible-collections/community.general/issues/5371).
- proxmox module utils - fix proxmoxer library version check (https://github.com/ansible-collections/community.general/issues/6974, https://github.com/ansible-collections/community.general/issues/6975, https://github.com/ansible-collections/community.general/pull/6980).
- proxmox_disk - fix unable to create ``cdrom`` media due to ``size`` always being appended (https://github.com/ansible-collections/community.general/pull/6770).
- proxmox_kvm - ``absent`` state with ``force`` specified failed to stop the VM due to the ``timeout`` value not being passed to ``stop_vm`` (https://github.com/ansible-collections/community.general/pull/6827).
- proxmox_kvm - ``restarted`` state did not actually restart a VM in some VM configurations. The state now uses the Proxmox reboot endpoint instead of calling the ``stop_vm`` and ``start_vm`` functions (https://github.com/ansible-collections/community.general/pull/6773).
- proxmox_kvm - allow creation of VM with existing name but new vmid (https://github.com/ansible-collections/community.general/issues/6155, https://github.com/ansible-collections/community.general/pull/6709).
- proxmox_kvm - when ``name`` option is provided without ``vmid`` and VM with that name already exists then no new VM will be created (https://github.com/ansible-collections/community.general/issues/6911, https://github.com/ansible-collections/community.general/pull/6981).
- proxmox_tasks_info - remove ``api_user`` + ``api_password`` constraint from ``required_together`` as it causes to require ``api_password`` even when API token param is used (https://github.com/ansible-collections/community.general/issues/6201).
- proxmox_template - require ``requests_toolbelt`` module to fix issue with uploading large templates (https://github.com/ansible-collections/community.general/issues/5579, https://github.com/ansible-collections/community.general/pull/6757).
- proxmox_user_info - avoid direct type comparisons (https://github.com/ansible-collections/community.general/pull/7085).
- redfish_info - fix ``ListUsers`` to not show empty account slots (https://github.com/ansible-collections/community.general/issues/6771, https://github.com/ansible-collections/community.general/pull/6772).
- redhat_subscription - use the right D-Bus options for the consumer type when
  registering a RHEL system older than 9 or a RHEL 9 system older than 9.2
  and using ``consumer_type``
  (https://github.com/ansible-collections/community.general/pull/7378).
- refish_utils module utils - changing variable names to avoid issues occuring when fetching Volumes data (https://github.com/ansible-collections/community.general/pull/6883).
- rhsm_repository - when using the ``purge`` option, the ``repositories``
  dictionary element in the returned JSON is now properly updated according
  to the pruning operation
  (https://github.com/ansible-collections/community.general/pull/6676).
- rundeck - fix ``TypeError`` on 404 API response (https://github.com/ansible-collections/community.general/pull/6983).
- selective callback plugin - fix length of task name lines in output always being 3 characters longer than desired (https://github.com/ansible-collections/community.general/pull/7374).
- snap - an exception was being raised when snap list was empty (https://github.com/ansible-collections/community.general/pull/7124, https://github.com/ansible-collections/community.general/issues/7120).
- snap - assume default track ``latest`` in parameter ``channel`` when not specified (https://github.com/ansible-collections/community.general/pull/6835, https://github.com/ansible-collections/community.general/issues/6821).
- snap - change the change detection mechanism from "parsing installation" to "comparing end state with initial state" (https://github.com/ansible-collections/community.general/pull/7340, https://github.com/ansible-collections/community.general/issues/7265).
- snap - fix crash when multiple snaps are specified and one has ``---`` in its description (https://github.com/ansible-collections/community.general/pull/7046).
- snap - fix the processing of the commands' output, stripping spaces and newlines from it (https://github.com/ansible-collections/community.general/pull/6826, https://github.com/ansible-collections/community.general/issues/6803).
- sorcery - fix interruption of the multi-stage process (https://github.com/ansible-collections/community.general/pull/7012).
- sorcery - fix queue generation before the whole system rebuild (https://github.com/ansible-collections/community.general/pull/7012).
- sorcery - latest state no longer triggers update_cache (https://github.com/ansible-collections/community.general/pull/7012).
- terraform - prevents ``-backend-config`` option double encapsulating with ``shlex_quote`` function. (https://github.com/ansible-collections/community.general/pull/7301).
- tss lookup plugin - fix multiple issues when using ``fetch_attachments=true`` (https://github.com/ansible-collections/community.general/pull/6720).
- zypper - added handling of zypper exitcode 102. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook (https://github.com/ansible-collections/community.general/pull/6534).

Known Issues
------------

- Ansible markup will show up in raw form on ansible-doc text output for ansible-core before 2.15. If you have trouble deciphering the documentation markup, please upgrade to ansible-core 2.15 (or newer), or read the HTML documentation on https://docs.ansible.com/ansible/devel/collections/community/general/ (https://github.com/ansible-collections/community.general/pull/6539).

New Plugins
-----------

Lookup
~~~~~~

- bitwarden_secrets_manager - Retrieve secrets from Bitwarden Secrets Manager

New Modules
-----------

- consul_policy - Manipulate Consul policies
- consul_role - Manipulate Consul roles
- facter_facts - Runs the discovery program C(facter) on the remote system and return Ansible facts
- gio_mime - Set default handler for MIME type, for applications using Gnome GIO
- gitlab_instance_variable - Creates, updates, or deletes GitLab instance variables
- gitlab_merge_request - Create, update, or delete GitLab merge requests
- jenkins_build_info - Get information about Jenkins builds
- keycloak_authentication_required_actions - Allows administration of Keycloak authentication required actions
- keycloak_authz_custom_policy - Allows administration of Keycloak client custom Javascript policies via Keycloak API
- keycloak_authz_permission - Allows administration of Keycloak client authorization permissions via Keycloak API
- keycloak_authz_permission_info - Query Keycloak client authorization permissions information
- keycloak_realm_key - Allows administration of Keycloak realm keys via Keycloak API
- keycloak_user - Create and configure a user in Keycloak
- lvg_rename - Renames LVM volume groups
- pnpm - Manage node.js packages with pnpm
- proxmox_pool - Pool management for Proxmox VE cluster
- proxmox_pool_member - Add or delete members from Proxmox VE cluster pools
- proxmox_vm_info - Retrieve information about one or more Proxmox VE virtual machines
- simpleinit_msb - Manage services on Source Mage GNU/Linux
