===============================
Community General Release Notes
===============================

.. contents:: Topics

This changelog describes changes after version 6.0.0.

v7.3.0
======

Release Summary
---------------

Feature and bugfix release.

Minor Changes
-------------

- chroot connection plugin - add ``disable_root_check`` option (https://github.com/ansible-collections/community.general/pull/7099).
- ejabberd_user - module now using ``CmdRunner`` to execute external command (https://github.com/ansible-collections/community.general/pull/7075).
- ipa_config - add module parameters to manage FreeIPA user and group objectclasses (https://github.com/ansible-collections/community.general/pull/7019).
- ipa_config - adds ``idp`` choice to ``ipauserauthtype`` parameter's choices (https://github.com/ansible-collections/community.general/pull/7051).
- npm - module now using ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6989).
- proxmox_kvm - enabled force restart of VM, bringing the ``force`` parameter functionality in line with what is described in the docs (https://github.com/ansible-collections/community.general/pull/6914).
- proxmox_vm_info - ``node`` parameter is no longer required. Information can be obtained for the whole cluster (https://github.com/ansible-collections/community.general/pull/6976).
- proxmox_vm_info - non-existing provided by name/vmid VM would return empty results instead of failing (https://github.com/ansible-collections/community.general/pull/7049).
- redfish_config - add ``DeleteAllVolumes`` command to allow deletion of all volumes on servers (https://github.com/ansible-collections/community.general/pull/6814).
- redfish_utils - use ``Controllers`` key in redfish data to obtain Storage controllers properties (https://github.com/ansible-collections/community.general/pull/7081).
- redfish_utils module utils - add support for ``PowerCycle`` reset type for ``redfish_command`` responses feature (https://github.com/ansible-collections/community.general/issues/7083).
- redfish_utils module utils - add support for following ``@odata.nextLink`` pagination in ``software_inventory`` responses feature (https://github.com/ansible-collections/community.general/pull/7020).
- shutdown - use ``shutdown -p ...`` with FreeBSD to halt and power off machine (https://github.com/ansible-collections/community.general/pull/7102).
- sorcery - add grimoire (repository) management support (https://github.com/ansible-collections/community.general/pull/7012).

Deprecated Features
-------------------

- ejabberd_user - deprecate the parameter ``logging`` in favour of producing more detailed information in the module output (https://github.com/ansible-collections/community.general/pull/7043).

Bugfixes
--------

- bitwarden lookup plugin - the plugin made assumptions about the structure of a Bitwarden JSON object which may have been broken by an update in the Bitwarden API. Remove assumptions, and allow queries for general fields such as ``notes`` (https://github.com/ansible-collections/community.general/pull/7061).
- ejabberd_user - module was failing to detect whether user was already created and/or password was changed (https://github.com/ansible-collections/community.general/pull/7033).
- keycloak module util - fix missing ``http_agent``, ``timeout``, and ``validate_certs`` ``open_url()`` parameters (https://github.com/ansible-collections/community.general/pull/7067).
- keycloak_client inventory plugin - fix missing client secret (https://github.com/ansible-collections/community.general/pull/6931).
- lvol - add support for percentage of origin size specification when creating snapshot volumes (https://github.com/ansible-collections/community.general/issues/1630, https://github.com/ansible-collections/community.general/pull/7053).
- lxc connection plugin - now handles ``remote_addr`` defaulting to ``inventory_hostname`` correctly (https://github.com/ansible-collections/community.general/pull/7104).
- oci_utils module utils - avoid direct type comparisons (https://github.com/ansible-collections/community.general/pull/7085).
- proxmox_user_info - avoid direct type comparisons (https://github.com/ansible-collections/community.general/pull/7085).
- snap - fix crash when multiple snaps are specified and one has ``---`` in its description (https://github.com/ansible-collections/community.general/pull/7046).
- sorcery - fix interruption of the multi-stage process (https://github.com/ansible-collections/community.general/pull/7012).
- sorcery - fix queue generation before the whole system rebuild (https://github.com/ansible-collections/community.general/pull/7012).
- sorcery - latest state no longer triggers update_cache (https://github.com/ansible-collections/community.general/pull/7012).

v7.2.1
======

Release Summary
---------------

Bugfix release.

Bugfixes
--------

- cmd_runner module utils - when a parameter in ``argument_spec`` has no type, meaning it is implicitly a ``str``, ``CmdRunner`` would fail trying to find the ``type`` key in that dictionary (https://github.com/ansible-collections/community.general/pull/6968).
- ejabberd_user - provide meaningful error message when the ``ejabberdctl`` command is not found (https://github.com/ansible-collections/community.general/pull/7028, https://github.com/ansible-collections/community.general/issues/6949).
- proxmox module utils - fix proxmoxer library version check (https://github.com/ansible-collections/community.general/issues/6974, https://github.com/ansible-collections/community.general/issues/6975, https://github.com/ansible-collections/community.general/pull/6980).
- proxmox_kvm - when ``name`` option is provided without ``vmid`` and VM with that name already exists then no new VM will be created (https://github.com/ansible-collections/community.general/issues/6911, https://github.com/ansible-collections/community.general/pull/6981).
- rundeck - fix ``TypeError`` on 404 API response (https://github.com/ansible-collections/community.general/pull/6983).

v7.2.0
======

Release Summary
---------------

Regular bugfix and feature release.

Minor Changes
-------------

- cobbler inventory plugin - convert Ansible unicode strings to native Python unicode strings before passing user/password to XMLRPC client (https://github.com/ansible-collections/community.general/pull/6923).
- consul_session - drops requirement for the ``python-consul`` library to communicate with the Consul API, instead relying on the existing ``requests`` library requirement (https://github.com/ansible-collections/community.general/pull/6755).
- gitlab_project_variable - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- gitlab_runner - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6927).
- htpasswd - the parameter ``crypt_scheme`` is being renamed as ``hash_scheme`` and added as an alias to it (https://github.com/ansible-collections/community.general/pull/6841).
- keycloak_authentication - added provider ID choices, since Keycloak supports only those two specific ones (https://github.com/ansible-collections/community.general/pull/6763).
- keyring - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6927).
- locale_gen - module has been refactored to use ``ModuleHelper`` and ``CmdRunner`` (https://github.com/ansible-collections/community.general/pull/6903).
- locale_gen - module now using ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6820).
- make - add new ``targets`` parameter allowing multiple targets to be used with ``make`` (https://github.com/ansible-collections/community.general/pull/6882, https://github.com/ansible-collections/community.general/issues/4919).
- nmcli - add support for ``ipv4.dns-options`` and ``ipv6.dns-options`` (https://github.com/ansible-collections/community.general/pull/6902).
- npm - minor improvement on parameter validation (https://github.com/ansible-collections/community.general/pull/6848).
- opkg - add ``executable`` parameter allowing to specify the path of the ``opkg`` command (https://github.com/ansible-collections/community.general/pull/6862).
- pubnub_blocks - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- redfish_command - add ``account_types`` and ``oem_account_types`` as optional inputs to ``AddUser`` (https://github.com/ansible-collections/community.general/issues/6823, https://github.com/ansible-collections/community.general/pull/6871).
- redfish_info - add ``AccountTypes`` and ``OEMAccountTypes`` to the output of ``ListUsers`` (https://github.com/ansible-collections/community.general/issues/6823, https://github.com/ansible-collections/community.general/pull/6871).
- redfish_info - adds ``ProcessorArchitecture`` to CPU inventory (https://github.com/ansible-collections/community.general/pull/6864).
- redfish_info - fix for ``GetVolumeInventory``, Controller name was getting populated incorrectly and duplicates were seen in the volumes retrieved (https://github.com/ansible-collections/community.general/pull/6719).
- rhsm_repository - the interaction with ``subscription-manager`` was
  refactored by grouping things together, removing unused bits, and hardening
  the way it is run; also, the parsing of ``subscription-manager repos --list``
  was improved and made slightly faster; no behaviour change is expected
  (https://github.com/ansible-collections/community.general/pull/6783,
  https://github.com/ansible-collections/community.general/pull/6837).
- scaleway_security_group_rule - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- snap - add option ``dangerous`` to the module, that will map into the command line argument ``--dangerous``, allowing unsigned snap files to be installed (https://github.com/ansible-collections/community.general/pull/6908, https://github.com/ansible-collections/community.general/issues/5715).
- tss lookup plugin - allow to fetch secret by path. Previously, we could not fetch secret by path but now use ``secret_path`` option to indicate to fetch secret by secret path (https://github.com/ansible-collections/community.general/pull/6881).
- xenserver_guest_info - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- xenserver_guest_powerstate - minor refactor removing unnecessary code statements (https://github.com/ansible-collections/community.general/pull/6928).
- yum_versionlock - add support to pin specific package versions instead of only the package itself (https://github.com/ansible-collections/community.general/pull/6861, https://github.com/ansible-collections/community.general/issues/4470).

Deprecated Features
-------------------

- flowdock - module relies entirely on no longer responsive API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6930).
- proxmox - old feature flag ``proxmox_default_behavior`` will be removed in community.general 10.0.0 (https://github.com/ansible-collections/community.general/pull/6836).
- stackdriver - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6887).
- webfaction_app - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_db - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_domain - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_mailbox - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).
- webfaction_site - module relies entirely on no longer existent API endpoints, and it will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/6909).

Bugfixes
--------

- cobbler inventory plugin - fix calculation of cobbler_ipv4/6_address (https://github.com/ansible-collections/community.general/pull/6925).
- datadog_downtime - presence of ``rrule`` param lead to the Datadog API returning Bad Request due to a missing recurrence type (https://github.com/ansible-collections/community.general/pull/6811).
- ipa_dnszone - fix 'idnsallowsyncptr' key error for reverse zone (https://github.com/ansible-collections/community.general/pull/6906, https://github.com/ansible-collections/community.general/issues/6905).
- keycloak_authentication - fix Keycloak authentication flow (step or sub-flow) indexing during update, if not specified by the user (https://github.com/ansible-collections/community.general/pull/6734).
- locale_gen - now works for locales without the underscore character such as ``C.UTF-8`` (https://github.com/ansible-collections/community.general/pull/6774, https://github.com/ansible-collections/community.general/issues/5142, https://github.com/ansible-collections/community.general/issues/4305).
- machinectl become plugin - mark plugin as ``require_tty`` to automatically disable pipelining, with which this plugin is not compatible (https://github.com/ansible-collections/community.general/issues/6932, https://github.com/ansible-collections/community.general/pull/6935).
- nmcli - fix support for empty list (in compare and scrape) (https://github.com/ansible-collections/community.general/pull/6769).
- openbsd_pkg - the pkg_info(1) behavior has changed in OpenBSD >7.3. The error message ``Can't find`` should not lead to an error case (https://github.com/ansible-collections/community.general/pull/6785).
- pacman - module recognizes the output of ``yay`` running as ``root`` (https://github.com/ansible-collections/community.general/pull/6713).
- proxmox - fix error when a configuration had no ``template`` field (https://github.com/ansible-collections/community.general/pull/6838, https://github.com/ansible-collections/community.general/issues/5372).
- proxmox module utils - add logic to detect whether an old Promoxer complains about the ``token_name`` and ``token_value`` parameters and provide a better error message when that happens (https://github.com/ansible-collections/community.general/pull/6839, https://github.com/ansible-collections/community.general/issues/5371).
- proxmox_disk - fix unable to create ``cdrom`` media due to ``size`` always being appended (https://github.com/ansible-collections/community.general/pull/6770).
- proxmox_kvm - ``absent`` state with ``force`` specified failed to stop the VM due to the ``timeout`` value not being passed to ``stop_vm`` (https://github.com/ansible-collections/community.general/pull/6827).
- proxmox_kvm - ``restarted`` state did not actually restart a VM in some VM configurations. The state now uses the Proxmox reboot endpoint instead of calling the ``stop_vm`` and ``start_vm`` functions (https://github.com/ansible-collections/community.general/pull/6773).
- proxmox_template - require ``requests_toolbelt`` module to fix issue with uploading large templates (https://github.com/ansible-collections/community.general/issues/5579, https://github.com/ansible-collections/community.general/pull/6757).
- redfish_info - fix ``ListUsers`` to not show empty account slots (https://github.com/ansible-collections/community.general/issues/6771, https://github.com/ansible-collections/community.general/pull/6772).
- refish_utils module utils - changing variable names to avoid issues occuring when fetching Volumes data (https://github.com/ansible-collections/community.general/pull/6883).
- snap - assume default track ``latest`` in parameter ``channel`` when not specified (https://github.com/ansible-collections/community.general/pull/6835, https://github.com/ansible-collections/community.general/issues/6821).
- snap - fix the processing of the commands' output, stripping spaces and newlines from it (https://github.com/ansible-collections/community.general/pull/6826, https://github.com/ansible-collections/community.general/issues/6803).

New Plugins
-----------

Lookup
~~~~~~

- bitwarden_secrets_manager - Retrieve secrets from Bitwarden Secrets Manager

New Modules
-----------

- consul_policy - Manipulate Consul policies
- keycloak_authz_permission - Allows administration of Keycloak client authorization permissions via Keycloak API
- keycloak_authz_permission_info - Query Keycloak client authorization permissions information
- proxmox_vm_info - Retrieve information about one or more Proxmox VE virtual machines

v7.1.0
======

Release Summary
---------------

Regular bugfix and feature release.

From this version on, community.general is using the new `Ansible semantic markup
<https://docs.ansible.com/ansible/devel/dev_guide/developing_modules_documenting.html#semantic-markup-within-module-documentation>`__
in its documentation. If you look at documentation with the ansible-doc CLI tool
from ansible-core before 2.15, please note that it does not render the markup
correctly. You should be still able to read it in most cases, but you need
ansible-core 2.15 or later to see it as it is intended. Alternatively you can
look at `the devel docsite <https://docs.ansible.com/ansible/devel/collections/community/general/>`__
for the rendered HTML version of the documentation of the latest release.


Minor Changes
-------------

- The collection will start using semantic markup (https://github.com/ansible-collections/community.general/pull/6539).
- VarDict module utils - add method ``VarDict.as_dict()`` to convert to a plain ``dict`` object (https://github.com/ansible-collections/community.general/pull/6602).
- cobbler inventory plugin - add ``inventory_hostname`` option to allow using the system name for the inventory hostname (https://github.com/ansible-collections/community.general/pull/6502).
- cobbler inventory plugin - add ``want_ip_addresses`` option to collect all interface DNS name to IP address mapping (https://github.com/ansible-collections/community.general/pull/6711).
- cobbler inventory plugin - add primary IP addess to ``cobbler_ipv4_address`` and IPv6 address to ``cobbler_ipv6_address`` host variable (https://github.com/ansible-collections/community.general/pull/6711).
- cobbler inventory plugin - add warning for systems with empty profiles (https://github.com/ansible-collections/community.general/pull/6502).
- copr - respawn module to use the system python interpreter when the ``dnf`` python module is not available in ``ansible_python_interpreter`` (https://github.com/ansible-collections/community.general/pull/6522).
- datadog_monitor - adds ``notification_preset_name``, ``renotify_occurrences`` and ``renotify_statuses`` parameters (https://github.com/ansible-collections/community.general/issues/6521,https://github.com/ansible-collections/community.general/issues/5823).
- filesystem - add ``uuid`` parameter for UUID change feature (https://github.com/ansible-collections/community.general/pull/6680).
- keycloak_client_rolemapping - adds support for subgroups with additional parameter ``parents`` (https://github.com/ansible-collections/community.general/pull/6687).
- keycloak_role - add composite roles support for realm and client roles (https://github.com/ansible-collections/community.general/pull/6469).
- ldap_* - add new arguments ``client_cert`` and ``client_key`` to the LDAP modules in order to allow certificate authentication (https://github.com/ansible-collections/community.general/pull/6668).
- ldap_search - add a new ``page_size`` option to enable paged searches (https://github.com/ansible-collections/community.general/pull/6648).
- lvg - add ``active`` and ``inactive`` values to the ``state`` option for active state management feature (https://github.com/ansible-collections/community.general/pull/6682).
- lvg - add ``reset_vg_uuid``, ``reset_pv_uuid`` options for UUID reset feature (https://github.com/ansible-collections/community.general/pull/6682).
- mas - disable sign-in check for macOS 12+ as ``mas account`` is non-functional (https://github.com/ansible-collections/community.general/pull/6520).
- onepassword lookup plugin - add service account support (https://github.com/ansible-collections/community.general/issues/6635, https://github.com/ansible-collections/community.general/pull/6660).
- onepassword_raw lookup plugin - add service account support (https://github.com/ansible-collections/community.general/issues/6635, https://github.com/ansible-collections/community.general/pull/6660).
- opentelemetry callback plugin - add span attributes in the span event (https://github.com/ansible-collections/community.general/pull/6531).
- opkg - remove default value ``""`` for parameter ``force`` as it causes the same behaviour of not having that parameter (https://github.com/ansible-collections/community.general/pull/6513).
- proxmox - support ``timezone`` parameter at container creation (https://github.com/ansible-collections/community.general/pull/6510).
- proxmox inventory plugin - add composite variables support for Proxmox nodes (https://github.com/ansible-collections/community.general/issues/6640).
- proxmox_kvm - added support for ``tpmstate0`` parameter to configure TPM (Trusted Platform Module) disk. TPM is required for Windows 11 installations (https://github.com/ansible-collections/community.general/pull/6533).
- proxmox_kvm - re-use ``timeout`` module param to forcefully shutdown a virtual machine when ``state`` is ``stopped`` (https://github.com/ansible-collections/community.general/issues/6257).
- proxmox_snap - add ``retention`` parameter to delete old snapshots (https://github.com/ansible-collections/community.general/pull/6576).
- redfish_command - add ``MultipartHTTPPushUpdate`` command (https://github.com/ansible-collections/community.general/issues/6471, https://github.com/ansible-collections/community.general/pull/6612).
- redhat_subscription - the internal ``RegistrationBase`` class was folded
  into the other internal ``Rhsm`` class, as the separation had no purpose
  anymore
  (https://github.com/ansible-collections/community.general/pull/6658).
- rhsm_release - improve/harden the way ``subscription-manager`` is run;
  no behaviour change is expected
  (https://github.com/ansible-collections/community.general/pull/6669).
- snap - module is now aware of channel when deciding whether to install or refresh the snap (https://github.com/ansible-collections/community.general/pull/6435, https://github.com/ansible-collections/community.general/issues/1606).
- sorcery - minor refactor (https://github.com/ansible-collections/community.general/pull/6525).
- tss lookup plugin - allow to fetch secret IDs which are in a folder based on folder ID. Previously, we could not fetch secrets based on folder ID but now use ``fetch_secret_ids_from_folder`` option to indicate to fetch secret IDs based on folder ID (https://github.com/ansible-collections/community.general/issues/6223).

Deprecated Features
-------------------

- CmdRunner module utils - deprecate ``cmd_runner_fmt.as_default_type()`` formatter (https://github.com/ansible-collections/community.general/pull/6601).
- MH VarsMixin module utils - deprecates ``VarsMixin`` and supporting classes in favor of plain ``vardict`` module util (https://github.com/ansible-collections/community.general/pull/6649).
- cpanm - value ``compatibility`` is deprecated as default for parameter ``mode`` (https://github.com/ansible-collections/community.general/pull/6512).
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

Bugfixes
--------

- MH DependencyMixin module utils - deprecation notice was popping up for modules not using dependencies (https://github.com/ansible-collections/community.general/pull/6644, https://github.com/ansible-collections/community.general/issues/6639).
- csv module utils - detects and remove unicode BOM markers from incoming CSV content (https://github.com/ansible-collections/community.general/pull/6662).
- gitlab_group - the module passed parameters to the API call even when not set. The module is now filtering out ``None`` values to remediate this (https://github.com/ansible-collections/community.general/pull/6712).
- icinga2_host - fix a key error when updating an existing host (https://github.com/ansible-collections/community.general/pull/6748).
- ini_file - add the ``follow`` paramter to follow the symlinks instead of replacing them (https://github.com/ansible-collections/community.general/pull/6546).
- ini_file - fix a bug where the inactive options were not used when possible (https://github.com/ansible-collections/community.general/pull/6575).
- keycloak module utils - fix ``is_struct_included`` handling of lists of lists/dictionaries (https://github.com/ansible-collections/community.general/pull/6688).
- keycloak module utils - the function ``get_user_by_username`` now return the user representation or ``None`` as stated in the documentation (https://github.com/ansible-collections/community.general/pull/6758).
- proxmox_kvm - allow creation of VM with existing name but new vmid (https://github.com/ansible-collections/community.general/issues/6155, https://github.com/ansible-collections/community.general/pull/6709).
- rhsm_repository - when using the ``purge`` option, the ``repositories``
  dictionary element in the returned JSON is now properly updated according
  to the pruning operation
  (https://github.com/ansible-collections/community.general/pull/6676).
- tss lookup plugin - fix multiple issues when using ``fetch_attachments=true`` (https://github.com/ansible-collections/community.general/pull/6720).

Known Issues
------------

- Ansible markup will show up in raw form on ansible-doc text output for ansible-core before 2.15. If you have trouble deciphering the documentation markup, please upgrade to ansible-core 2.15 (or newer), or read the HTML documentation on https://docs.ansible.com/ansible/devel/collections/community/general/ (https://github.com/ansible-collections/community.general/pull/6539).

New Modules
-----------

- gitlab_instance_variable - Creates, updates, or deletes GitLab instance variables
- gitlab_merge_request - Create, update, or delete GitLab merge requests
- keycloak_authentication_required_actions - Allows administration of Keycloak authentication required actions
- keycloak_user - Create and configure a user in Keycloak
- lvg_rename - Renames LVM volume groups
- proxmox_pool - Pool management for Proxmox VE cluster
- proxmox_pool_member - Add or delete members from Proxmox VE cluster pools

v7.0.1
======

Release Summary
---------------

Bugfix release for Ansible 8.0.0rc1.

Bugfixes
--------

- nmcli - fix bond option ``xmit_hash_policy`` (https://github.com/ansible-collections/community.general/pull/6527).
- portage - fix ``changed_use`` and ``newuse`` not triggering rebuilds (https://github.com/ansible-collections/community.general/issues/6008, https://github.com/ansible-collections/community.general/pull/6548).
- proxmox_tasks_info - remove ``api_user`` + ``api_password`` constraint from ``required_together`` as it causes to require ``api_password`` even when API token param is used (https://github.com/ansible-collections/community.general/issues/6201).
- zypper - added handling of zypper exitcode 102. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook (https://github.com/ansible-collections/community.general/pull/6534).

v7.0.0
======

Release Summary
---------------

This is release 7.0.0 of ``community.general``, released on 2023-05-09.

Minor Changes
-------------

- apache2_module - add module argument ``warn_mpm_absent`` to control whether warning are raised in some edge cases (https://github.com/ansible-collections/community.general/pull/5793).
- apt_rpm - adds ``clean``, ``dist_upgrade`` and ``update_kernel``  parameters for clear caches, complete upgrade system, and upgrade kernel packages (https://github.com/ansible-collections/community.general/pull/5867).
- bitwarden lookup plugin - can now retrieve secrets from custom fields (https://github.com/ansible-collections/community.general/pull/5694).
- bitwarden lookup plugin - implement filtering results by ``collection_id`` parameter (https://github.com/ansible-collections/community.general/issues/5849).
- cmd_runner module utils - ``cmd_runner_fmt.as_bool()`` can now take an extra parameter to format when value is false (https://github.com/ansible-collections/community.general/pull/5647).
- cpanm - minor change, use feature from ``ModuleHelper`` (https://github.com/ansible-collections/community.general/pull/6385).
- dconf - be forgiving about boolean values: convert them to GVariant booleans automatically (https://github.com/ansible-collections/community.general/pull/6206).
- dconf - if ``gi.repository.GLib`` is missing, try to respawn in a Python interpreter that has it (https://github.com/ansible-collections/community.general/pull/6491).
- dconf - minor refactoring improving parameters and dependencies validation (https://github.com/ansible-collections/community.general/pull/6336).
- dconf - parse GVariants for equality comparison when the Python module ``gi.repository`` is available (https://github.com/ansible-collections/community.general/pull/6049).
- deps module utils - add function ``failed()`` providing the ability to check the dependency check result without triggering an exception (https://github.com/ansible-collections/community.general/pull/6383).
- dig lookup plugin - Support multiple domains to be queried as indicated in docs (https://github.com/ansible-collections/community.general/pull/6334).
- dig lookup plugin - support CAA record type (https://github.com/ansible-collections/community.general/pull/5913).
- dnsimple - set custom User-Agent for API requests to DNSimple (https://github.com/ansible-collections/community.general/pull/5927).
- dnsimple_info - minor refactor in the code (https://github.com/ansible-collections/community.general/pull/6440).
- flatpak_remote - add new boolean option ``enabled``. It controls, whether the remote is enabled or not (https://github.com/ansible-collections/community.general/pull/5926).
- gconftool2 - refactor using ``ModuleHelper`` and ``CmdRunner`` (https://github.com/ansible-collections/community.general/pull/5545).
- gitlab_group_variable, gitlab_project_variable - refactor function out to module utils (https://github.com/ansible-collections/community.general/pull/6384).
- gitlab_project - add ``builds_access_level``, ``container_registry_access_level`` and ``forking_access_level`` options (https://github.com/ansible-collections/community.general/pull/5706).
- gitlab_project - add ``releases_access_level``, ``environments_access_level``, ``feature_flags_access_level``, ``infrastructure_access_level``, ``monitor_access_level``, and ``security_and_compliance_access_level`` options (https://github.com/ansible-collections/community.general/pull/5986).
- gitlab_project - add new option ``topics`` for adding topics to GitLab projects (https://github.com/ansible-collections/community.general/pull/6278).
- gitlab_runner - add new boolean option ``access_level_on_creation``. It controls, whether the value of ``access_level`` is used for runner registration or not. The option ``access_level`` has been ignored on registration so far and was only used on updates (https://github.com/ansible-collections/community.general/issues/5907, https://github.com/ansible-collections/community.general/pull/5908).
- gitlab_runner - allow to register group runner (https://github.com/ansible-collections/community.general/pull/3935).
- homebrew_cask - allows passing ``--greedy`` option to ``upgrade_all`` (https://github.com/ansible-collections/community.general/pull/6267).
- idrac_redfish_command - add ``job_id`` to ``CreateBiosConfigJob`` response (https://github.com/ansible-collections/community.general/issues/5603).
- ilo_redfish_utils module utils - change implementation of DNS Server IP and NTP Server IP update (https://github.com/ansible-collections/community.general/pull/5804).
- ipa_group - allow to add and remove external users with the ``external_user`` option (https://github.com/ansible-collections/community.general/pull/5897).
- ipa_hostgroup - add ``append`` parameter for adding a new hosts to existing hostgroups without changing existing hostgroup members (https://github.com/ansible-collections/community.general/pull/6203).
- iptables_state - minor refactoring within the module (https://github.com/ansible-collections/community.general/pull/5844).
- java_certs - add more detailed error output when extracting certificate from PKCS12 fails (https://github.com/ansible-collections/community.general/pull/5550).
- jc filter plugin - added the ability to use parser plugins (https://github.com/ansible-collections/community.general/pull/6043).
- jenkins_plugin - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5565).
- jira - add worklog functionality (https://github.com/ansible-collections/community.general/issues/6209, https://github.com/ansible-collections/community.general/pull/6210).
- keycloak_authentication - add flow type option to sub flows to allow the creation of 'form-flow' sub flows like in Keycloak's built-in registration flow (https://github.com/ansible-collections/community.general/pull/6318).
- keycloak_group - add new optional module parameter ``parents`` to properly handle keycloak subgroups (https://github.com/ansible-collections/community.general/pull/5814).
- keycloak_user_federation - make ``org.keycloak.storage.ldap.mappers.LDAPStorageMapper`` the default value for mappers ``providerType`` (https://github.com/ansible-collections/community.general/pull/5863).
- ldap modules - add ``ca_path`` option (https://github.com/ansible-collections/community.general/pull/6185).
- ldap modules - add ``xorder_discovery`` option (https://github.com/ansible-collections/community.general/issues/6045, https://github.com/ansible-collections/community.general/pull/6109).
- ldap_search - the new ``base64_attributes`` allows to specify which attribute values should be Base64 encoded (https://github.com/ansible-collections/community.general/pull/6473).
- lxd_container - add diff and check mode (https://github.com/ansible-collections/community.general/pull/5866).
- lxd_project - refactored code out to module utils to clear sanity check (https://github.com/ansible-collections/community.general/pull/5549).
- make - add ``command`` return value to the module output (https://github.com/ansible-collections/community.general/pull/6160).
- mattermost, rocketchat, slack - replace missing default favicon with docs.ansible.com favicon (https://github.com/ansible-collections/community.general/pull/5928).
- mksysb - improved the output of the module in case of errors (https://github.com/ansible-collections/community.general/issues/6263).
- modprobe - add ``persistent`` option (https://github.com/ansible-collections/community.general/issues/4028, https://github.com/ansible-collections/community.general/pull/542).
- module_helper module utils - updated the imports to make more MH features available at ``plugins/module_utils/module_helper.py`` (https://github.com/ansible-collections/community.general/pull/6464).
- mssql_script - allow for ``GO`` statement to be mixed-case for scripts not using strict syntax (https://github.com/ansible-collections/community.general/pull/6457).
- mssql_script - handle error condition for empty resultsets to allow for non-returning SQL statements (for example ``UPDATE`` and ``INSERT``) (https://github.com/ansible-collections/community.general/pull/6457).
- mssql_script - improve batching logic to allow a wider variety of input scripts. For example, SQL scripts slurped from Windows machines which may contain carriage return (''\r'') characters (https://github.com/ansible-collections/community.general/pull/6457).
- nmap inventory plugin - add new option ``open`` for only returning open ports (https://github.com/ansible-collections/community.general/pull/6200).
- nmap inventory plugin - add new option ``port`` for port specific scan (https://github.com/ansible-collections/community.general/pull/6165).
- nmap inventory plugin - add new options ``udp_scan``, ``icmp_timestamp``, and ``dns_resolve`` for different types of scans (https://github.com/ansible-collections/community.general/pull/5566).
- nmap inventory plugin - added environment variables for configure ``address`` and ``exclude`` (https://github.com/ansible-collections/community.general/issues/6351).
- nmcli - add ``default`` and ``default-or-eui64`` to the list of valid choices for ``addr_gen_mode6`` parameter (https://github.com/ansible-collections/community.general/pull/5974).
- nmcli - add ``macvlan`` connection type (https://github.com/ansible-collections/community.general/pull/6312).
- nmcli - add support for ``team.runner-fast-rate`` parameter for ``team`` connections (https://github.com/ansible-collections/community.general/issues/6065).
- nmcli - new module option ``slave_type`` added to allow creation of various types of slave devices (https://github.com/ansible-collections/community.general/issues/473, https://github.com/ansible-collections/community.general/pull/6108).
- one_vm - add a new ``updateconf`` option which implements the ``one.vm.updateconf`` API call (https://github.com/ansible-collections/community.general/pull/5812).
- openbsd_pkg - set ``TERM`` to ``'dumb'`` in ``execute_command()`` to make module less dependant on the ``TERM`` environment variable set on the Ansible controller (https://github.com/ansible-collections/community.general/pull/6149).
- opkg - allow installing a package in a certain version (https://github.com/ansible-collections/community.general/pull/5688).
- opkg - refactored module to use ``CmdRunner`` for executing ``opkg`` (https://github.com/ansible-collections/community.general/pull/5718).
- osx_defaults - include stderr in error messages (https://github.com/ansible-collections/community.general/pull/6011).
- pipx - add ``system_site_packages`` parameter to give application access to system-wide packages (https://github.com/ansible-collections/community.general/pull/6308).
- pipx - ensure ``include_injected`` parameter works with ``state=upgrade`` and ``state=latest`` (https://github.com/ansible-collections/community.general/pull/6212).
- pipx - optional ``install_apps`` parameter added to install applications from injected packages (https://github.com/ansible-collections/community.general/pull/6198).
- proxmox - added new module parameter ``tags`` for use with PVE 7+ (https://github.com/ansible-collections/community.general/pull/5714).
- proxmox - suppress urllib3 ``InsecureRequestWarnings`` when ``validate_certs`` option is ``false`` (https://github.com/ansible-collections/community.general/pull/5931).
- proxmox_kvm - add new ``archive`` parameter. This is needed to create a VM from an archive (backup) (https://github.com/ansible-collections/community.general/pull/6159).
- proxmox_kvm - adds ``migrate`` parameter to manage online migrations between hosts (https://github.com/ansible-collections/community.general/pull/6448)
- puppet - add new options ``skip_tags`` to exclude certain tagged resources during a puppet agent or apply (https://github.com/ansible-collections/community.general/pull/6293).
- puppet - refactored module to use ``CmdRunner`` for executing ``puppet`` (https://github.com/ansible-collections/community.general/pull/5612).
- rax_scaling_group - refactored out code to the ``rax`` module utils to clear the sanity check (https://github.com/ansible-collections/community.general/pull/5563).
- redfish_command - add ``PerformRequestedOperations`` command to perform any operations necessary to continue the update flow (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_command - add ``update_apply_time`` to ``SimpleUpdate`` command (https://github.com/ansible-collections/community.general/issues/3910).
- redfish_command - add ``update_status`` to output of ``SimpleUpdate`` command to allow a user monitor the update in progress (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_command - adding ``EnableSecureBoot`` functionality (https://github.com/ansible-collections/community.general/pull/5899).
- redfish_command - adding ``VerifyBiosAttributes`` functionality (https://github.com/ansible-collections/community.general/pull/5900).
- redfish_info - add ``GetUpdateStatus`` command to check the progress of a previous update request (https://github.com/ansible-collections/community.general/issues/4276).
- redfish_info - adds commands to retrieve the HPE ThermalConfiguration and FanPercentMinimum settings from iLO (https://github.com/ansible-collections/community.general/pull/6208).
- redfish_utils module utils - added PUT (``put_request()``) functionality (https://github.com/ansible-collections/community.general/pull/5490).
- redhat_subscription - add a ``server_proxy_scheme`` parameter to configure the scheme for the proxy server (https://github.com/ansible-collections/community.general/pull/5662).
- redhat_subscription - adds ``token`` parameter for subscription-manager authentication using Red Hat API token (https://github.com/ansible-collections/community.general/pull/5725).
- redhat_subscription - credentials (``username``, ``activationkey``, and so on) are required now only if a system needs to be registered, or ``force_register`` is specified (https://github.com/ansible-collections/community.general/pull/5664).
- redhat_subscription - the registration is done using the D-Bus ``rhsm`` service instead of spawning a ``subscription-manager register`` command, if possible; this avoids passing plain-text credentials as arguments to ``subscription-manager register``, which can be seen while that command runs (https://github.com/ansible-collections/community.general/pull/6122).
- sefcontext - add support for path substitutions (https://github.com/ansible-collections/community.general/issues/1193).
- shutdown - if no shutdown commands are found in the ``search_paths`` then the module will attempt to shutdown the system using ``systemctl shutdown`` (https://github.com/ansible-collections/community.general/issues/4269, https://github.com/ansible-collections/community.general/pull/6171).
- slack - add option ``prepend_hash`` which allows to control whether a ``#`` is prepended to ``channel_id``. The current behavior (value ``auto``) is to prepend ``#`` unless some specific prefixes are found. That list of prefixes is incomplete, and there does not seem to exist a documented condition on when exactly ``#`` must not be prepended. We recommend to explicitly set ``prepend_hash=always`` or ``prepend_hash=never`` to avoid any ambiguity (https://github.com/ansible-collections/community.general/pull/5629).
- snap - minor refactor when executing module (https://github.com/ansible-collections/community.general/pull/5773).
- snap - refactor module to use ``CmdRunner`` to execute external commands (https://github.com/ansible-collections/community.general/pull/6468).
- snap_alias - refactor code to module utils (https://github.com/ansible-collections/community.general/pull/6441).
- snap_alias - refactored module to use ``CmdRunner`` to execute ``snap`` (https://github.com/ansible-collections/community.general/pull/5486).
- spotinst_aws_elastigroup - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5553).
- ssh_config - add ``host_key_algorithms`` option (https://github.com/ansible-collections/community.general/pull/5605).
- ssh_config - add ``proxyjump`` option (https://github.com/ansible-collections/community.general/pull/5970).
- ssh_config - refactor code to module util to fix sanity check (https://github.com/ansible-collections/community.general/pull/5720).
- ssh_config - vendored StormSSH's config parser to avoid having to install StormSSH to use the module (https://github.com/ansible-collections/community.general/pull/6117).
- sudoers - add ``setenv`` parameters to support passing environment variables via sudo. (https://github.com/ansible-collections/community.general/pull/5883)
- sudoers - adds ``host`` parameter for setting hostname restrictions in sudoers rules (https://github.com/ansible-collections/community.general/issues/5702).
- terraform - remove state file check condition and error block, because in the native implementation of terraform will not cause errors due to the non-existent file (https://github.com/ansible-collections/community.general/pull/6296).
- udm_dns_record - minor refactor to the code (https://github.com/ansible-collections/community.general/pull/6382).
- udm_share - added ``elements`` attribute to ``list`` type parameters (https://github.com/ansible-collections/community.general/pull/5557).
- udm_user - add ``elements`` attribute when missing in ``list`` parameters (https://github.com/ansible-collections/community.general/pull/5559).
- znode module - optional ``use_tls`` parameter added for encrypted communication (https://github.com/ansible-collections/community.general/issues/6154).

Breaking Changes / Porting Guide
--------------------------------

- If you are not using this collection as part of Ansible, but installed (and/or upgraded) community.general manually, you need to make sure to also install ``community.sap_libs`` if you are using any of the ``sapcar_extract``, ``sap_task_list_execute``, and ``hana_query`` modules.
  Without that collection installed, the redirects for these modules do not work.
- ModuleHelper module utils - when the module sets output variables named ``msg``, ``exception``, ``output``, ``vars``, or ``changed``, the actual output will prefix those names with ``_`` (underscore symbol) only when they clash with output variables generated by ModuleHelper itself, which only occurs when handling exceptions. Please note that this breaking change does not require a new major release since before this release, it was not possible to add such variables to the output `due to a bug <https://github.com/ansible-collections/community.general/pull/5755>`__ (https://github.com/ansible-collections/community.general/pull/5765).
- gconftool2 - fix processing of ``gconftool-2`` when ``key`` does not exist, returning ``null`` instead of empty string for both ``value`` and ``previous_value`` return values (https://github.com/ansible-collections/community.general/issues/6028).
- gitlab_runner - the default of ``access_level_on_creation`` changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/6428).
- ldap_search - convert all string-like values to UTF-8 (https://github.com/ansible-collections/community.general/issues/5704, https://github.com/ansible-collections/community.general/pull/6473).
- nmcli - the default of the ``hairpin`` option changed from ``true`` to ``false`` (https://github.com/ansible-collections/community.general/pull/6428).
- proxmox - the default of the ``unprivileged`` option changed from ``false`` to ``true`` (https://github.com/ansible-collections/community.general/pull/6428).

Deprecated Features
-------------------

- ModuleHelper module_utils - ``deps`` mixin for MH classes deprecated in favour of using the ``deps`` module_utils (https://github.com/ansible-collections/community.general/pull/6465).
- consul - deprecate using parameters unused for ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5772).
- gitlab_runner - the default of the new option ``access_level_on_creation`` will change from ``false`` to ``true`` in community.general 7.0.0. This will cause ``access_level`` to be used during runner registration as well, and not only during updates (https://github.com/ansible-collections/community.general/pull/5908).
- gitlab_runner - the option ``access_level`` will lose its default value in community.general 8.0.0. From that version on, you have set this option to ``ref_protected`` explicitly, if you want to have a protected runner (https://github.com/ansible-collections/community.general/issues/5925).
- manageiq_policies - deprecate ``state=list`` in favour of using ``community.general.manageiq_policies_info`` (https://github.com/ansible-collections/community.general/pull/5721).
- manageiq_tags - deprecate ``state=list`` in favour of using ``community.general.manageiq_tags_info`` (https://github.com/ansible-collections/community.general/pull/5727).
- rax - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax module utils - module utils code relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cbs - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cbs_attachments - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb_database - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_cdb_user - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb_nodes - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_clb_ssl - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_dns - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_dns_record - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_facts - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_files - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_files_objects - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_identity - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_keypair - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_meta - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_alarm - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_check - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_entity - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_notification - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_mon_notification_plan - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_network - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_queue - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_scaling_group - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rax_scaling_policy - module relies on deprecated library ``pyrax`` and will be removed in community.general 9.0.0 (https://github.com/ansible-collections/community.general/pull/5752).
- rhn_channel, rhn_register - RHN hosted at redhat.com was discontinued years
  ago, and Spacewalk 5 (which uses RHN) is EOL since 2020, May 31st;
  while these modules could work on Uyuni / SUSE Manager (fork of Spacewalk 5),
  we have not heard about anyone using them in those setups. Hence, these
  modules are deprecated, and will be removed in community.general 10.0.0
  in case there are no reports about being still useful, and potentially
  noone that steps up to maintain them
  (https://github.com/ansible-collections/community.general/pull/6493).

Removed Features (previously deprecated)
----------------------------------------

- All ``sap`` modules have been removed from this collection.
  They have been migrated to the `community.sap_libs <https://galaxy.ansible.com/community/sap_libs>`_ collection.
  Redirections have been provided.
  Following modules are affected:
  - sapcar_extract
  - sap_task_list_execute
  - hana_query
- cmd_runner module utils - the ``fmt`` alias of ``cmd_runner_fmt`` has been removed. Use ``cmd_runner_fmt`` instead (https://github.com/ansible-collections/community.general/pull/6428).
- newrelic_deployment - the ``appname`` and ``environment`` options have been removed. They did not do anything (https://github.com/ansible-collections/community.general/pull/6428).
- puppet - the alias ``show-diff`` of the ``show_diff`` option has been removed. Use ``show_diff`` instead (https://github.com/ansible-collections/community.general/pull/6428).
- xfconf - generating facts was deprecated in community.general 3.0.0, however three factoids, ``property``, ``channel`` and ``value`` continued to be generated by mistake. This behaviour has been removed and ``xfconf`` generate no facts whatsoever (https://github.com/ansible-collections/community.general/pull/5502).
- xfconf - generating facts was deprecated in community.general 3.0.0, however two factoids, ``previous_value`` and ``type`` continued to be generated by mistake. This behaviour has been removed and ``xfconf`` generate no facts whatsoever (https://github.com/ansible-collections/community.general/pull/5502).

Bugfixes
--------

- ModuleHelper - fix bug when adjusting the name of reserved output variables (https://github.com/ansible-collections/community.general/pull/5755).
- alternatives - support subcommands on Fedora 37, which uses ``follower`` instead of ``slave`` (https://github.com/ansible-collections/community.general/pull/5794).
- ansible_galaxy_install - set default to raise exception if command's return code is different from zero (https://github.com/ansible-collections/community.general/pull/5680).
- ansible_galaxy_install - try ``C.UTF-8`` and then fall back to ``en_US.UTF-8`` before failing (https://github.com/ansible-collections/community.general/pull/5680).
- archive - avoid deprecated exception class on Python 3 (https://github.com/ansible-collections/community.general/pull/6180).
- archive - reduce RAM usage by generating CRC32 checksum over chunks (https://github.com/ansible-collections/community.general/pull/6274).
- bitwarden lookup plugin - clarify what to do, if the bitwarden vault is not unlocked (https://github.com/ansible-collections/community.general/pull/5811).
- cartesian and flattened lookup plugins - adjust to parameter deprecation in ansible-core 2.14's ``listify_lookup_plugin_terms`` helper function (https://github.com/ansible-collections/community.general/pull/6074).
- chroot connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/5570).
- cloudflare_dns - fixed the idempotency for SRV DNS records (https://github.com/ansible-collections/community.general/pull/5972).
- cloudflare_dns - fixed the possiblity of setting a root-level SRV DNS record (https://github.com/ansible-collections/community.general/pull/5972).
- cmd_runner module utils - fixed bug when handling default cases in ``cmd_runner_fmt.as_map()`` (https://github.com/ansible-collections/community.general/pull/5538).
- cmd_runner module utils - formatting arguments ``cmd_runner_fmt.as_fixed()`` was expecting an non-existing argument (https://github.com/ansible-collections/community.general/pull/5538).
- dependent lookup plugin - avoid warning on deprecated parameter for ``Templar.template()`` (https://github.com/ansible-collections/community.general/pull/5543).
- deps module utils - do not fail when dependency cannot be found (https://github.com/ansible-collections/community.general/pull/6479).
- dig lookup plugin - correctly handle DNSKEY record type's ``algorithm`` field (https://github.com/ansible-collections/community.general/pull/5914).
- flatpak - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing Flatpaks because of a parameter witch only checks the installed apps (https://github.com/ansible-collections/community.general/pull/6289).
- gconftool2 - fix ``changed`` result always being ``true`` (https://github.com/ansible-collections/community.general/issues/6028).
- gconftool2 - remove requirement of parameter ``value`` when ``state=absent`` (https://github.com/ansible-collections/community.general/issues/6028).
- gem - fix force parameter not being passed to gem command when uninstalling (https://github.com/ansible-collections/community.general/pull/5822).
- gem - fix hang due to interactive prompt for confirmation on specific version uninstall (https://github.com/ansible-collections/community.general/pull/5751).
- github_webhook - fix always changed state when no secret is provided (https://github.com/ansible-collections/community.general/pull/5994).
- gitlab_deploy_key - also update ``title`` and not just ``can_push`` (https://github.com/ansible-collections/community.general/pull/5888).
- gitlab_group_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- gitlab_project_variables - fix dropping variables accidentally when GitLab introduced new properties (https://github.com/ansible-collections/community.general/pull/5667).
- gitlab_runner - fix ``KeyError`` on runner creation and update (https://github.com/ansible-collections/community.general/issues/6112).
- icinga2_host - fix the data structure sent to Icinga to make use of host templates and template vars (https://github.com/ansible-collections/community.general/pull/6286).
- idrac_redfish_command - allow user to specify ``resource_id`` for ``CreateBiosConfigJob`` to specify an exact manager (https://github.com/ansible-collections/community.general/issues/2090).
- influxdb_user - fix running in check mode when the user does not exist yet (https://github.com/ansible-collections/community.general/pull/6111).
- ini_file - make ``section`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6404).
- interfaces_file - fix reading options in lines not starting with a space (https://github.com/ansible-collections/community.general/issues/6120).
- jail connection plugin - add ``inventory_hostname`` to vars under ``remote_addr``. This is needed for compatibility with ansible-core 2.13 (https://github.com/ansible-collections/community.general/pull/6118).
- jenkins_build - fix the logical flaw when deleting a Jenkins build (https://github.com/ansible-collections/community.general/pull/5514).
- jenkins_plugin - fix error due to undefined variable when updates file is not downloaded (https://github.com/ansible-collections/community.general/pull/6100).
- keycloak - improve error messages (https://github.com/ansible-collections/community.general/pull/6318).
- keycloak_client - fix accidental replacement of value for attribute ``saml.signing.private.key`` with ``no_log`` in wrong contexts (https://github.com/ansible-collections/community.general/pull/5934).
- keycloak_client_rolemapping - calculate ``proposed`` and ``after`` return values properly (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_client_rolemapping - remove only listed mappings with ``state=absent`` (https://github.com/ansible-collections/community.general/pull/5619).
- keycloak_user_federation - fixes federation creation issue. When a new federation was created and at the same time a default / standard mapper was also changed / updated the creation process failed as a bad None set variable led to a bad malformed url request (https://github.com/ansible-collections/community.general/pull/5750).
- keycloak_user_federation - fixes idempotency detection issues. In some cases the module could fail to properly detect already existing user federations because of a buggy seemingly superflous extra query parameter (https://github.com/ansible-collections/community.general/pull/5732).
- loganalytics callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logdna callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- logstash callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- lxc_container - fix the arguments of the lxc command which broke the creation and cloning of containers (https://github.com/ansible-collections/community.general/issues/5578).
- lxd_* modules, lxd inventory plugin - fix TLS/SSL certificate validation problems by using the correct purpose when creating the TLS context (https://github.com/ansible-collections/community.general/issues/5616, https://github.com/ansible-collections/community.general/pull/6034).
- memset - fix memset urlerror handling (https://github.com/ansible-collections/community.general/pull/6114).
- nmcli - fix change handling of values specified as an integer 0 (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix failure to handle WIFI settings when connection type not specified (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fix improper detection of changes to ``wifi.wake-on-wlan`` (https://github.com/ansible-collections/community.general/pull/5431).
- nmcli - fixed idempotency issue for bridge connections. Module forced default value of ``bridge.priority`` to nmcli if not set; if ``bridge.stp`` is disabled nmcli ignores it and keep default (https://github.com/ansible-collections/community.general/issues/3216, https://github.com/ansible-collections/community.general/issues/4683).
- nmcli - fixed idempotency issue when module params is set to ``may_fail4=false`` and ``method4=disabled``; in this case nmcli ignores change and keeps their own default value ``yes`` (https://github.com/ansible-collections/community.general/pull/6106).
- nmcli - implemented changing mtu value on vlan interfaces (https://github.com/ansible-collections/community.general/issues/4387).
- nmcli - order is significant for lists of addresses (https://github.com/ansible-collections/community.general/pull/6048).
- nsupdate - fix zone lookup. The SOA record for an existing zone is returned as an answer RR and not as an authority RR (https://github.com/ansible-collections/community.general/issues/5817, https://github.com/ansible-collections/community.general/pull/5818).
- one_vm - avoid splitting labels that are ``None`` (https://github.com/ansible-collections/community.general/pull/5489).
- one_vm - fix syntax error when creating VMs with a more complex template (https://github.com/ansible-collections/community.general/issues/6225).
- onepassword lookup plugin - Changed to ignore errors from "op account get" calls. Previously, errors would prevent auto-signin code from executing (https://github.com/ansible-collections/community.general/pull/5942).
- onepassword_raw - add missing parameter to plugin documentation (https://github.com/ansible-collections/community.general/issues/5506).
- opkg - fix issue that ``force=reinstall`` would not reinstall an existing package (https://github.com/ansible-collections/community.general/pull/5705).
- opkg - fixes bug when using ``update_cache=true`` (https://github.com/ansible-collections/community.general/issues/6004).
- passwordstore lookup plugin - make compatible with ansible-core 2.16 (https://github.com/ansible-collections/community.general/pull/6447).
- pipx - fixed handling of ``install_deps=true`` with ``state=latest`` and ``state=upgrade`` (https://github.com/ansible-collections/community.general/pull/6303).
- portage - update the logic for generating the emerge command arguments to ensure that ``withbdeps: false`` results in a passing an ``n`` argument with the ``--with-bdeps`` emerge flag (https://github.com/ansible-collections/community.general/issues/6451, https://github.com/ansible-collections/community.general/pull/6456).
- proxmox inventory plugin - fix bug while templating when using templates for the ``url``, ``user``, ``password``, ``token_id``, or ``token_secret`` options (https://github.com/ansible-collections/community.general/pull/5640).
- proxmox inventory plugin - handle tags delimited by semicolon instead of comma, which happens from Proxmox 7.3 on (https://github.com/ansible-collections/community.general/pull/5602).
- proxmox_disk - avoid duplicate ``vmid`` reference (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5493).
- proxmox_disk - fixed issue with read timeout on import action (https://github.com/ansible-collections/community.general/pull/5803).
- proxmox_disk - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- proxmox_nic - fixed possible issues with redundant ``vmid`` parameter (https://github.com/ansible-collections/community.general/issues/5492, https://github.com/ansible-collections/community.general/pull/5672).
- puppet - handling ``noop`` parameter was not working at all, now it is has been fixed (https://github.com/ansible-collections/community.general/issues/6452, https://github.com/ansible-collections/community.general/issues/6458).
- redfish_utils - removed basic auth HTTP header when performing a GET on the service root resource and when performing a POST to the session collection (https://github.com/ansible-collections/community.general/issues/5886).
- redhat_subscription - do not ignore ``consumer_name`` and other variables if ``activationkey`` is specified (https://github.com/ansible-collections/community.general/issues/3486, https://github.com/ansible-collections/community.general/pull/5627).
- redhat_subscription - do not pass arguments to ``subscription-manager register`` for things already configured; now a specified ``rhsm_baseurl`` is properly set for subscription-manager (https://github.com/ansible-collections/community.general/pull/5583).
- redhat_subscription - do not use D-Bus for registering when ``environment`` is specified, so it possible to specify again the environment names for registering, as the D-Bus APIs work only with IDs (https://github.com/ansible-collections/community.general/pull/6319).
- redhat_subscription - try to unregister only when already registered when ``force_register`` is specified (https://github.com/ansible-collections/community.general/issues/6258, https://github.com/ansible-collections/community.general/pull/6259).
- redhat_subscription - use the right D-Bus options for environments when registering a CentOS Stream 8 system and using ``environment`` (https://github.com/ansible-collections/community.general/pull/6275).
- redhat_subscription, rhsm_release, rhsm_repository - cleanly fail when not running as root, rather than hanging on an interactive ``console-helper`` prompt; they all interact with ``subscription-manager``, which already requires to be run as root (https://github.com/ansible-collections/community.general/issues/734, https://github.com/ansible-collections/community.general/pull/6211).
- rhsm_release - make ``release`` parameter not required so it is possible to pass ``null`` as a value. This only was possible in the past due to a bug in ansible-core that now has been fixed (https://github.com/ansible-collections/community.general/pull/6401).
- rundeck module utils - fix errors caused by the API empty responses (https://github.com/ansible-collections/community.general/pull/6300)
- rundeck_acl_policy - fix ``TypeError - byte indices must be integers or slices, not str`` error caused by empty API response. Update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/pull/5887, https://github.com/ansible-collections/community.general/pull/6300).
- rundeck_project - update the module to use ``module_utils.rundeck`` functions (https://github.com/ansible-collections/community.general/issues/5742) (https://github.com/ansible-collections/community.general/pull/6300)
- snap_alias - module would only recognize snap names containing letter, numbers or the underscore character, failing to identify valid snap names such as ``lxd.lxc`` (https://github.com/ansible-collections/community.general/pull/6361).
- splunk callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- sumologic callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- syslog_json callback plugin - adjust type of callback to ``notification``, it was incorrectly classified as ``aggregate`` before (https://github.com/ansible-collections/community.general/pull/5761).
- terraform - fix ``current`` workspace never getting appended to the ``all`` key in the ``workspace_ctf`` object (https://github.com/ansible-collections/community.general/pull/5735).
- terraform - fix ``terraform init`` failure when there are multiple workspaces on the remote backend and when ``default`` workspace is missing by setting ``TF_WORKSPACE`` environmental variable to the value of ``workspace`` when used (https://github.com/ansible-collections/community.general/pull/5735).
- terraform - fix broken ``warn()`` call (https://github.com/ansible-collections/community.general/pull/6497).
- terraform and timezone - slight refactoring to avoid linter reporting potentially undefined variables (https://github.com/ansible-collections/community.general/pull/5933).
- terraform module - disable ANSI escape sequences during validation phase (https://github.com/ansible-collections/community.general/pull/5843).
- tss lookup plugin - allow to download secret attachments. Previously, we could not download secret attachments but now use ``fetch_attachments`` and ``file_download_path`` variables to download attachments (https://github.com/ansible-collections/community.general/issues/6224).
- unixy callback plugin - fix plugin to work with ansible-core 2.14 by using Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).
- unixy callback plugin - fix typo introduced when updating to use Ansible's configuration manager for handling options (https://github.com/ansible-collections/community.general/issues/5600).
- various plugins and modules - remove unnecessary imports (https://github.com/ansible-collections/community.general/pull/5940).
- vdo - now uses ``yaml.safe_load()`` to parse command output instead of the deprecated ``yaml.load()`` which is potentially unsafe. Using ``yaml.load()`` without explicitely setting a ``Loader=`` is also an error in pyYAML 6.0 (https://github.com/ansible-collections/community.general/pull/5632).
- vmadm - fix for index out of range error in ``get_vm_uuid`` (https://github.com/ansible-collections/community.general/pull/5628).
- xenorchestra inventory plugin - fix failure to receive objects from server due to not checking the id of the response (https://github.com/ansible-collections/community.general/pull/6227).
- xfs_quota - in case of a project quota, the call to ``xfs_quota`` did not initialize/reset the project (https://github.com/ansible-collections/community.general/issues/5143).
- xml - fixed a bug where empty ``children`` list would not be set (https://github.com/ansible-collections/community.general/pull/5808).
- yarn - fix ``global=true`` to check for the configured global folder instead of assuming the default (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``global=true`` to not fail when `executable` wasn't specified (https://github.com/ansible-collections/community.general/pull/6132)
- yarn - fix ``state=absent`` not working with ``global=true`` when the package does not include a binary (https://github.com/ansible-collections/community.general/pull/5829)
- yarn - fix ``state=latest`` not working with ``global=true`` (https://github.com/ansible-collections/community.general/issues/5712).
- yarn - fixes bug where yarn module tasks would fail when warnings were emitted from Yarn. The ``yarn.list`` method was not filtering out warnings (https://github.com/ansible-collections/community.general/issues/6127).
- zfs_delegate_admin - zfs allow output can now be parsed when uids/gids are not known to the host system (https://github.com/ansible-collections/community.general/pull/5943).
- zypper - make package managing work on readonly filesystem of openSUSE MicroOS (https://github.com/ansible-collections/community.general/pull/5615).

New Plugins
-----------

Lookup
~~~~~~

- merge_variables - merge variables with a certain suffix

New Modules
-----------

- btrfs_info - Query btrfs filesystem info
- btrfs_subvolume - Manage btrfs subvolumes
- gitlab_project_badge - Manage project badges on GitLab Server
- ilo_redfish_command - Manages Out-Of-Band controllers using Redfish APIs
- ipbase_info - Retrieve IP geolocation and other facts of a host's IP address using the ipbase.com API
- kdeconfig - Manage KDE configuration files
- keycloak_authz_authorization_scope - Allows administration of Keycloak client authorization scopes via Keycloak API
- keycloak_clientscope_type - Set the type of aclientscope in realm or client via Keycloak API
- keycloak_clientsecret_info - Retrieve client secret via Keycloak API
- keycloak_clientsecret_regenerate - Regenerate Keycloak client secret via Keycloak API
- ocapi_command - Manages Out-Of-Band controllers using Open Composable API (OCAPI)
- ocapi_info - Manages Out-Of-Band controllers using Open Composable API (OCAPI)
