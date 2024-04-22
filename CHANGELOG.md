# Community General Release Notes

**Topics**

- <a href="#v8-6-0">v8\.6\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes">Bugfixes</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v8-5-0">v8\.5\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#security-fixes">Security Fixes</a>
    - <a href="#bugfixes-1">Bugfixes</a>
    - <a href="#new-modules-1">New Modules</a>
- <a href="#v8-4-0">v8\.4\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#bugfixes-2">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#callback">Callback</a>
        - <a href="#filter">Filter</a>
    - <a href="#new-modules-2">New Modules</a>
- <a href="#v8-3-0">v8\.3\.0</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-3">Bugfixes</a>
    - <a href="#new-modules-3">New Modules</a>
- <a href="#v8-2-0">v8\.2\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#bugfixes-4">Bugfixes</a>
    - <a href="#new-plugins-1">New Plugins</a>
        - <a href="#connection">Connection</a>
        - <a href="#filter-1">Filter</a>
        - <a href="#lookup">Lookup</a>
    - <a href="#new-modules-4">New Modules</a>
- <a href="#v8-1-0">v8\.1\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#bugfixes-5">Bugfixes</a>
    - <a href="#new-plugins-2">New Plugins</a>
        - <a href="#lookup-1">Lookup</a>
        - <a href="#test">Test</a>
    - <a href="#new-modules-5">New Modules</a>
- <a href="#v8-0-2">v8\.0\.2</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v8-0-1">v8\.0\.1</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v8-0-0">v8\.0\.0</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features-2">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#bugfixes-8">Bugfixes</a>
    - <a href="#known-issues">Known Issues</a>
    - <a href="#new-plugins-3">New Plugins</a>
        - <a href="#lookup-2">Lookup</a>
    - <a href="#new-modules-6">New Modules</a>
This changelog describes changes after version 7\.0\.0\.

<a id="v8-6-0"></a>
## v8\.6\.0

<a id="release-summary"></a>
### Release Summary

Regular bugfix and features release\.

<a id="minor-changes"></a>
### Minor Changes

* Use offset\-aware <code>datetime\.datetime</code> objects \(with timezone UTC\) instead of offset\-naive UTC timestamps\, which are deprecated in Python 3\.12 \([https\://github\.com/ansible\-collections/community\.general/pull/8222](https\://github\.com/ansible\-collections/community\.general/pull/8222)\)\.
* apt\_rpm \- add new states <code>latest</code> and <code>present\_not\_latest</code>\. The value <code>latest</code> is equivalent to the current behavior of <code>present</code>\, which will upgrade a package if a newer version exists\. <code>present\_not\_latest</code> does what most users would expect <code>present</code> to do\: it does not upgrade if the package is already installed\. The current behavior of <code>present</code> will be deprecated in a later version\, and eventually changed to that of <code>present\_not\_latest</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8217](https\://github\.com/ansible\-collections/community\.general/issues/8217)\, [https\://github\.com/ansible\-collections/community\.general/pull/8247](https\://github\.com/ansible\-collections/community\.general/pull/8247)\)\.
* bitwarden lookup plugin \- add support to filter by organization ID \([https\://github\.com/ansible\-collections/community\.general/pull/8188](https\://github\.com/ansible\-collections/community\.general/pull/8188)\)\.
* filesystem \- add bcachefs support \([https\://github\.com/ansible\-collections/community\.general/pull/8126](https\://github\.com/ansible\-collections/community\.general/pull/8126)\)\.
* ini\_file \- add an optional parameter <code>section\_has\_values</code>\. If the target ini file contains more than one <code>section</code>\, use <code>section\_has\_values</code> to specify which one should be updated \([https\://github\.com/ansible\-collections/community\.general/pull/7505](https\://github\.com/ansible\-collections/community\.general/pull/7505)\)\.
* java\_cert \- add <code>cert\_content</code> argument \([https\://github\.com/ansible\-collections/community\.general/pull/8153](https\://github\.com/ansible\-collections/community\.general/pull/8153)\)\.
* keycloak\_client\, keycloak\_clientscope\, keycloak\_clienttemplate \- added <code>docker\-v2</code> protocol support\, enhancing alignment with Keycloak\'s protocol options \([https\://github\.com/ansible\-collections/community\.general/issues/8215](https\://github\.com/ansible\-collections/community\.general/issues/8215)\, [https\://github\.com/ansible\-collections/community\.general/pull/8216](https\://github\.com/ansible\-collections/community\.general/pull/8216)\)\.
* nmcli \- adds OpenvSwitch support with new <code>type</code> values <code>ovs\-port</code>\, <code>ovs\-interface</code>\, and <code>ovs\-bridge</code>\, and new <code>slave\_type</code> value <code>ovs\-port</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8154](https\://github\.com/ansible\-collections/community\.general/pull/8154)\)\.
* osx\_defaults \- add option <code>check\_types</code> to enable changing the type of existing defaults on the fly \([https\://github\.com/ansible\-collections/community\.general/pull/8173](https\://github\.com/ansible\-collections/community\.general/pull/8173)\)\.
* passwordstore lookup \- add <code>missing\_subkey</code> parameter defining the behavior of the lookup when a passwordstore subkey is missing \([https\://github\.com/ansible\-collections/community\.general/pull/8166](https\://github\.com/ansible\-collections/community\.general/pull/8166)\)\.
* portage \- adds the possibility to explicitely tell portage to write packages to world file \([https\://github\.com/ansible\-collections/community\.general/issues/6226](https\://github\.com/ansible\-collections/community\.general/issues/6226)\, [https\://github\.com/ansible\-collections/community\.general/pull/8236](https\://github\.com/ansible\-collections/community\.general/pull/8236)\)\.
* redfish\_command \- add command <code>ResetToDefaults</code> to reset manager to default state \([https\://github\.com/ansible\-collections/community\.general/issues/8163](https\://github\.com/ansible\-collections/community\.general/issues/8163)\)\.
* redfish\_info \- add boolean return value <code>MultipartHttpPush</code> to <code>GetFirmwareUpdateCapabilities</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8194](https\://github\.com/ansible\-collections/community\.general/issues/8194)\, [https\://github\.com/ansible\-collections/community\.general/pull/8195](https\://github\.com/ansible\-collections/community\.general/pull/8195)\)\.
* ssh\_config \- allow <code>accept\-new</code> as valid value for <code>strict\_host\_key\_checking</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8257](https\://github\.com/ansible\-collections/community\.general/pull/8257)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* hipchat callback plugin \- the hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020\. The callback plugin is therefore deprecated and will be removed from community\.general 10\.0\.0 if nobody provides compelling reasons to still keep it \([https\://github\.com/ansible\-collections/community\.general/issues/8184](https\://github\.com/ansible\-collections/community\.general/issues/8184)\, [https\://github\.com/ansible\-collections/community\.general/pull/8189](https\://github\.com/ansible\-collections/community\.general/pull/8189)\)\.

<a id="bugfixes"></a>
### Bugfixes

* aix\_filesystem \- fix <code>\_validate\_vg</code> not passing VG name to <code>lsvg\_cmd</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8151](https\://github\.com/ansible\-collections/community\.general/issues/8151)\)\.
* apt\_rpm \- when checking whether packages were installed after running <code>apt\-get \-y install \<packages\></code>\, only the last package name was checked \([https\://github\.com/ansible\-collections/community\.general/pull/8263](https\://github\.com/ansible\-collections/community\.general/pull/8263)\)\.
* bitwarden\_secrets\_manager lookup plugin \- implements retry with exponential backoff to avoid lookup errors when Bitwardn\'s API rate limiting is encountered \([https\://github\.com/ansible\-collections/community\.general/issues/8230](https\://github\.com/ansible\-collections/community\.general/issues/8230)\, [https\://github\.com/ansible\-collections/community\.general/pull/8238](https\://github\.com/ansible\-collections/community\.general/pull/8238)\)\.
* from\_ini filter plugin \- disabling interpolation of <code>ConfigParser</code> to allow converting values with a <code>\%</code> sign \([https\://github\.com/ansible\-collections/community\.general/issues/8183](https\://github\.com/ansible\-collections/community\.general/issues/8183)\, [https\://github\.com/ansible\-collections/community\.general/pull/8185](https\://github\.com/ansible\-collections/community\.general/pull/8185)\)\.
* gitlab\_issue\, gitlab\_label\, gitlab\_milestone \- avoid crash during version comparison when the python\-gitlab Python module is not installed \([https\://github\.com/ansible\-collections/community\.general/pull/8158](https\://github\.com/ansible\-collections/community\.general/pull/8158)\)\.
* haproxy \- fix an issue where HAProxy could get stuck in DRAIN mode when the backend was unreachable \([https\://github\.com/ansible\-collections/community\.general/issues/8092](https\://github\.com/ansible\-collections/community\.general/issues/8092)\)\.
* inventory plugins \- add unsafe wrapper to avoid marking strings that do not contain <code>\{</code> or <code>\}</code> as unsafe\, to work around a bug in AWX \(\([https\://github\.com/ansible\-collections/community\.general/issues/8212](https\://github\.com/ansible\-collections/community\.general/issues/8212)\, [https\://github\.com/ansible\-collections/community\.general/pull/8225](https\://github\.com/ansible\-collections/community\.general/pull/8225)\)\.
* ipa \- fix get version regex in IPA module\_utils \([https\://github\.com/ansible\-collections/community\.general/pull/8175](https\://github\.com/ansible\-collections/community\.general/pull/8175)\)\.
* keycloak\_client \- add sorted <code>defaultClientScopes</code> and <code>optionalClientScopes</code> to normalizations \([https\://github\.com/ansible\-collections/community\.general/pull/8223](https\://github\.com/ansible\-collections/community\.general/pull/8223)\)\.
* keycloak\_realm \- add normalizations for <code>enabledEventTypes</code> and <code>supportedLocales</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8224](https\://github\.com/ansible\-collections/community\.general/pull/8224)\)\.
* puppet \- add option <code>environment\_lang</code> to set the environment language encoding\. Defaults to lang <code>C</code>\. It is recommended to set it to <code>C\.UTF\-8</code> or <code>en\_US\.UTF\-8</code> depending on what is available on your system\. \([https\://github\.com/ansible\-collections/community\.general/issues/8000](https\://github\.com/ansible\-collections/community\.general/issues/8000)\)
* riak \- support <code>riak admin</code> sub\-command in newer Riak KV versions beside the legacy <code>riak\-admin</code> main command \([https\://github\.com/ansible\-collections/community\.general/pull/8211](https\://github\.com/ansible\-collections/community\.general/pull/8211)\)\.
* to\_ini filter plugin \- disabling interpolation of <code>ConfigParser</code> to allow converting values with a <code>\%</code> sign \([https\://github\.com/ansible\-collections/community\.general/issues/8183](https\://github\.com/ansible\-collections/community\.general/issues/8183)\, [https\://github\.com/ansible\-collections/community\.general/pull/8185](https\://github\.com/ansible\-collections/community\.general/pull/8185)\)\.
* xml \- make module work with lxml 5\.1\.1\, which removed some internals that the module was relying on \([https\://github\.com/ansible\-collections/community\.general/pull/8169](https\://github\.com/ansible\-collections/community\.general/pull/8169)\)\.

<a id="new-modules"></a>
### New Modules

* keycloak\_client\_rolescope \- Allows administration of Keycloak client roles scope to restrict the usage of certain roles to a other specific client applications\.

<a id="v8-5-0"></a>
## v8\.5\.0

<a id="release-summary-1"></a>
### Release Summary

Regular feature and bugfix release with security fixes\.

<a id="minor-changes-1"></a>
### Minor Changes

* bitwarden lookup plugin \- allows to fetch all records of a given collection ID\, by allowing to pass an empty value for <code>search\_value</code> when <code>collection\_id</code> is provided \([https\://github\.com/ansible\-collections/community\.general/pull/8013](https\://github\.com/ansible\-collections/community\.general/pull/8013)\)\.
* icinga2 inventory plugin \- adds new parameter <code>group\_by\_hostgroups</code> in order to make grouping by Icinga2 hostgroups optional \([https\://github\.com/ansible\-collections/community\.general/pull/7998](https\://github\.com/ansible\-collections/community\.general/pull/7998)\)\.
* ini\_file \- support optional spaces between section names and their surrounding brackets \([https\://github\.com/ansible\-collections/community\.general/pull/8075](https\://github\.com/ansible\-collections/community\.general/pull/8075)\)\.
* java\_cert \- enable <code>owner</code>\, <code>group</code>\, <code>mode</code>\, and other generic file arguments \([https\://github\.com/ansible\-collections/community\.general/pull/8116](https\://github\.com/ansible\-collections/community\.general/pull/8116)\)\.
* ldap\_attrs \- module now supports diff mode\, showing which attributes are changed within an operation \([https\://github\.com/ansible\-collections/community\.general/pull/8073](https\://github\.com/ansible\-collections/community\.general/pull/8073)\)\.
* lxd\_container \- uses <code>/1\.0/instances</code> API endpoint\, if available\. Falls back to <code>/1\.0/containers</code> or <code>/1\.0/virtual\-machines</code>\. Fixes issue when using Incus or LXD 5\.19 due to migrating to <code>/1\.0/instances</code> endpoint \([https\://github\.com/ansible\-collections/community\.general/pull/7980](https\://github\.com/ansible\-collections/community\.general/pull/7980)\)\.
* nmcli \- allow setting <code>MTU</code> for <code>bond\-slave</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/8118](https\://github\.com/ansible\-collections/community\.general/pull/8118)\)\.
* proxmox \- adds <code>startup</code> parameters to configure startup order\, startup delay and shutdown delay \([https\://github\.com/ansible\-collections/community\.general/pull/8038](https\://github\.com/ansible\-collections/community\.general/pull/8038)\)\.
* revbitspss lookup plugin \- removed a redundant unicode prefix\. The prefix was not necessary for Python 3 and has been cleaned up to streamline the code \([https\://github\.com/ansible\-collections/community\.general/pull/8087](https\://github\.com/ansible\-collections/community\.general/pull/8087)\)\.

<a id="security-fixes"></a>
### Security Fixes

* cobbler\, gitlab\_runners\, icinga2\, linode\, lxd\, nmap\, online\, opennebula\, proxmox\, scaleway\, stackpath\_compute\, virtualbox\, and xen\_orchestra inventory plugin \- make sure all data received from the remote servers is marked as unsafe\, so remote code execution by obtaining texts that can be evaluated as templates is not possible \([https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/](https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/)\, [https\://github\.com/ansible\-collections/community\.general/pull/8098](https\://github\.com/ansible\-collections/community\.general/pull/8098)\)\.

<a id="bugfixes-1"></a>
### Bugfixes

* aix\_filesystem \- fix issue with empty list items in crfs logic and option order \([https\://github\.com/ansible\-collections/community\.general/pull/8052](https\://github\.com/ansible\-collections/community\.general/pull/8052)\)\.
* consul\_token \- fix token creation without <code>accessor\_id</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8091](https\://github\.com/ansible\-collections/community\.general/pull/8091)\)\.
* homebrew \- error returned from brew command was ignored and tried to parse empty JSON\. Fix now checks for an error and raises it to give accurate error message to users \([https\://github\.com/ansible\-collections/community\.general/issues/8047](https\://github\.com/ansible\-collections/community\.general/issues/8047)\)\.
* ipa\_hbacrule \- the module uses a string for <code>ipaenabledflag</code> for new FreeIPA versions while the returned value is a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7880](https\://github\.com/ansible\-collections/community\.general/pull/7880)\)\.
* ipa\_sudorule \- the module uses a string for <code>ipaenabledflag</code> for new FreeIPA versions while the returned value is a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7880](https\://github\.com/ansible\-collections/community\.general/pull/7880)\)\.
* iptables\_state \- fix idempotency issues when restoring incomplete iptables dumps \([https\://github\.com/ansible\-collections/community\.general/issues/8029](https\://github\.com/ansible\-collections/community\.general/issues/8029)\)\.
* linode inventory plugin \- add descriptive error message for linode inventory plugin \([https\://github\.com/ansible\-collections/community\.general/pull/8133](https\://github\.com/ansible\-collections/community\.general/pull/8133)\)\.
* pacemaker\_cluster \- actually implement check mode\, which the module claims to support\. This means that until now the module also did changes in check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8081](https\://github\.com/ansible\-collections/community\.general/pull/8081)\)\.
* pam\_limits \- when the file does not exist\, do not create it in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/8050](https\://github\.com/ansible\-collections/community\.general/issues/8050)\, [https\://github\.com/ansible\-collections/community\.general/pull/8057](https\://github\.com/ansible\-collections/community\.general/pull/8057)\)\.
* proxmox\_kvm \- fixed status check getting from node\-specific API endpoint \([https\://github\.com/ansible\-collections/community\.general/issues/7817](https\://github\.com/ansible\-collections/community\.general/issues/7817)\)\.

<a id="new-modules-1"></a>
### New Modules

* usb\_facts \- Allows listing information about USB devices

<a id="v8-4-0"></a>
## v8\.4\.0

<a id="release-summary-2"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-2"></a>
### Minor Changes

* bitwarden lookup plugin \- add <code>bw\_session</code> option\, to pass session key instead of reading from env \([https\://github\.com/ansible\-collections/community\.general/pull/7994](https\://github\.com/ansible\-collections/community\.general/pull/7994)\)\.
* gitlab\_deploy\_key\, gitlab\_group\_members\, gitlab\_group\_variable\, gitlab\_hook\, gitlab\_instance\_variable\, gitlab\_project\_badge\, gitlab\_project\_variable\, gitlab\_user \- improve API pagination and compatibility with different versions of <code>python\-gitlab</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7790](https\://github\.com/ansible\-collections/community\.general/pull/7790)\)\.
* gitlab\_hook \- adds <code>releases\_events</code> parameter for supporting Releases events triggers on GitLab hooks \([https\://github\.com/ansible\-collections/community\.general/pull/7956](https\://github\.com/ansible\-collections/community\.general/pull/7956)\)\.
* icinga2 inventory plugin \- add Jinja2 templating support to <code>url</code>\, <code>user</code>\, and <code>password</code> paramenters \([https\://github\.com/ansible\-collections/community\.general/issues/7074](https\://github\.com/ansible\-collections/community\.general/issues/7074)\, [https\://github\.com/ansible\-collections/community\.general/pull/7996](https\://github\.com/ansible\-collections/community\.general/pull/7996)\)\.
* mssql\_script \- adds transactional \(rollback/commit\) support via optional boolean param <code>transaction</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7976](https\://github\.com/ansible\-collections/community\.general/pull/7976)\)\.
* proxmox\_kvm \- add parameter <code>update\_unsafe</code> to avoid limitations when updating dangerous values \([https\://github\.com/ansible\-collections/community\.general/pull/7843](https\://github\.com/ansible\-collections/community\.general/pull/7843)\)\.
* redfish\_config \- add command <code>SetServiceIdentification</code> to set service identification \([https\://github\.com/ansible\-collections/community\.general/issues/7916](https\://github\.com/ansible\-collections/community\.general/issues/7916)\)\.
* sudoers \- add support for the <code>NOEXEC</code> tag in sudoers rules \([https\://github\.com/ansible\-collections/community\.general/pull/7983](https\://github\.com/ansible\-collections/community\.general/pull/7983)\)\.
* terraform \- fix <code>diff\_mode</code> in state <code>absent</code> and when terraform <code>resource\_changes</code> does not exist \([https\://github\.com/ansible\-collections/community\.general/pull/7963](https\://github\.com/ansible\-collections/community\.general/pull/7963)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* cargo \- fix idempotency issues when using a custom installation path for packages \(using the <code>\-\-path</code> parameter\)\. The initial installation runs fine\, but subsequent runs use the <code>get\_installed\(\)</code> function which did not check the given installation location\, before running <code>cargo install</code>\. This resulted in a false <code>changed</code> state\. Also the removal of packeges using <code>state\: absent</code> failed\, as the installation check did not use the given parameter \([https\://github\.com/ansible\-collections/community\.general/pull/7970](https\://github\.com/ansible\-collections/community\.general/pull/7970)\)\.
* gitlab\_issue \- fix behavior to search GitLab issue\, using <code>search</code> keyword instead of <code>title</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7846](https\://github\.com/ansible\-collections/community\.general/issues/7846)\)\.
* gitlab\_runner \- fix pagination when checking for existing runners \([https\://github\.com/ansible\-collections/community\.general/pull/7790](https\://github\.com/ansible\-collections/community\.general/pull/7790)\)\.
* keycloak\_client \- fixes issue when metadata is provided in desired state when task is in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/1226](https\://github\.com/ansible\-collections/community\.general/issues/1226)\, [https\://github\.com/ansible\-collections/community\.general/pull/7881](https\://github\.com/ansible\-collections/community\.general/pull/7881)\)\.
* modprobe \- listing modules files or modprobe files could trigger a FileNotFoundError if <code>/etc/modprobe\.d</code> or <code>/etc/modules\-load\.d</code> did not exist\. Relevant functions now return empty lists if the directories do not exist to avoid crashing the module \([https\://github\.com/ansible\-collections/community\.general/issues/7717](https\://github\.com/ansible\-collections/community\.general/issues/7717)\)\.
* onepassword lookup plugin \- failed for fields that were in sections and had uppercase letters in the label/ID\. Field lookups are now case insensitive in all cases \([https\://github\.com/ansible\-collections/community\.general/pull/7919](https\://github\.com/ansible\-collections/community\.general/pull/7919)\)\.
* pkgin \- pkgin \(pkgsrc package manager used by SmartOS\) raises erratic exceptions and spurious <code>changed\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7971](https\://github\.com/ansible\-collections/community\.general/pull/7971)\)\.
* redfish\_info \- allow for a GET operation invoked by <code>GetUpdateStatus</code> to allow for an empty response body for cases where a service returns 204 No Content \([https\://github\.com/ansible\-collections/community\.general/issues/8003](https\://github\.com/ansible\-collections/community\.general/issues/8003)\)\.
* redfish\_info \- correct uncaught exception when attempting to retrieve <code>Chassis</code> information \([https\://github\.com/ansible\-collections/community\.general/pull/7952](https\://github\.com/ansible\-collections/community\.general/pull/7952)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="callback"></a>
#### Callback

* default\_without\_diff \- The default ansible callback without diff output

<a id="filter"></a>
#### Filter

* lists\_difference \- Difference of lists with a predictive order
* lists\_intersect \- Intersection of lists with a predictive order
* lists\_symmetric\_difference \- Symmetric Difference of lists with a predictive order
* lists\_union \- Union of lists with a predictive order

<a id="new-modules-2"></a>
### New Modules

* gitlab\_group\_access\_token \- Manages GitLab group access tokens
* gitlab\_project\_access\_token \- Manages GitLab project access tokens

<a id="v8-3-0"></a>
## v8\.3\.0

<a id="release-summary-3"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-3"></a>
### Minor Changes

* consul\_auth\_method\, consul\_binding\_rule\, consul\_policy\, consul\_role\, consul\_session\, consul\_token \- added action group <code>community\.general\.consul</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7897](https\://github\.com/ansible\-collections/community\.general/pull/7897)\)\.
* consul\_policy \- added support for diff and check mode \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_policy\, consul\_role\, consul\_session \- removed dependency on <code>requests</code> and factored out common parts \([https\://github\.com/ansible\-collections/community\.general/pull/7826](https\://github\.com/ansible\-collections/community\.general/pull/7826)\, [https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- <code>node\_identities</code> now expects a <code>node\_name</code> option to match the Consul API\, the old <code>name</code> is still supported as alias \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- <code>service\_identities</code> now expects a <code>service\_name</code> option to match the Consul API\, the old <code>name</code> is still supported as alias \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- added support for diff mode \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- added support for templated policies \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* redfish\_info \- add command <code>GetServiceIdentification</code> to get service identification \([https\://github\.com/ansible\-collections/community\.general/issues/7882](https\://github\.com/ansible\-collections/community\.general/issues/7882)\)\.
* terraform \- add support for <code>diff\_mode</code> for terraform resource\_changes \([https\://github\.com/ansible\-collections/community\.general/pull/7896](https\://github\.com/ansible\-collections/community\.general/pull/7896)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* consul\_acl \- the module has been deprecated and will be removed in community\.general 10\.0\.0\. <code>consul\_token</code> and <code>consul\_policy</code> can be used instead \([https\://github\.com/ansible\-collections/community\.general/pull/7901](https\://github\.com/ansible\-collections/community\.general/pull/7901)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* homebrew \- detect already installed formulae and casks using JSON output from <code>brew info</code> \([https\://github\.com/ansible\-collections/community\.general/issues/864](https\://github\.com/ansible\-collections/community\.general/issues/864)\)\.
* incus connection plugin \- treats <code>inventory\_hostname</code> as a variable instead of a literal in remote connections \([https\://github\.com/ansible\-collections/community\.general/issues/7874](https\://github\.com/ansible\-collections/community\.general/issues/7874)\)\.
* ipa\_otptoken \- the module expect <code>ipatokendisabled</code> as string but the <code>ipatokendisabled</code> value is returned as a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7795](https\://github\.com/ansible\-collections/community\.general/pull/7795)\)\.
* ldap \- previously the order number \(if present\) was expected to follow an equals sign in the DN\. This makes it so the order number string is identified correctly anywhere within the DN \([https\://github\.com/ansible\-collections/community\.general/issues/7646](https\://github\.com/ansible\-collections/community\.general/issues/7646)\)\.
* mssql\_script \- make the module work with Python 2 \([https\://github\.com/ansible\-collections/community\.general/issues/7818](https\://github\.com/ansible\-collections/community\.general/issues/7818)\, [https\://github\.com/ansible\-collections/community\.general/pull/7821](https\://github\.com/ansible\-collections/community\.general/pull/7821)\)\.
* nmcli \- fix <code>connection\.slave\-type</code> wired to <code>bond</code> and not with parameter <code>slave\_type</code> in case of connection type <code>wifi</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7389](https\://github\.com/ansible\-collections/community\.general/issues/7389)\)\.
* proxmox \- fix updating a container config if the setting does not already exist \([https\://github\.com/ansible\-collections/community\.general/pull/7872](https\://github\.com/ansible\-collections/community\.general/pull/7872)\)\.

<a id="new-modules-3"></a>
### New Modules

* consul\_acl\_bootstrap \- Bootstrap ACLs in Consul
* consul\_auth\_method \- Manipulate Consul auth methods
* consul\_binding\_rule \- Manipulate Consul binding rules
* consul\_token \- Manipulate Consul tokens
* gitlab\_label \- Creates/updates/deletes GitLab Labels belonging to project or group\.
* gitlab\_milestone \- Creates/updates/deletes GitLab Milestones belonging to project or group

<a id="v8-2-0"></a>
## v8\.2\.0

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* ipa\_dnsrecord \- adds ability to manage NS record types \([https\://github\.com/ansible\-collections/community\.general/pull/7737](https\://github\.com/ansible\-collections/community\.general/pull/7737)\)\.
* ipa\_pwpolicy \- refactor module and exchange a sequence <code>if</code> statements with a <code>for</code> loop \([https\://github\.com/ansible\-collections/community\.general/pull/7723](https\://github\.com/ansible\-collections/community\.general/pull/7723)\)\.
* ipa\_pwpolicy \- update module to support <code>maxrepeat</code>\, <code>maxsequence</code>\, <code>dictcheck</code>\, <code>usercheck</code>\, <code>gracelimit</code> parameters in FreeIPA password policies \([https\://github\.com/ansible\-collections/community\.general/pull/7723](https\://github\.com/ansible\-collections/community\.general/pull/7723)\)\.
* keycloak\_realm\_key \- the <code>config\.algorithm</code> option now supports 8 additional key algorithms \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_realm\_key \- the <code>config\.certificate</code> option value is no longer defined with <code>no\_log\=True</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_realm\_key \- the <code>provider\_id</code> option now supports RSA encryption key usage \(value <code>rsa\-enc</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_user\_federation \- allow custom user storage providers to be set through <code>provider\_id</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7789](https\://github\.com/ansible\-collections/community\.general/pull/7789)\)\.
* mail \- add <code>Message\-ID</code> header\; which is required by some mail servers \([https\://github\.com/ansible\-collections/community\.general/pull/7740](https\://github\.com/ansible\-collections/community\.general/pull/7740)\)\.
* mail module\, mail callback plugin \- allow to configure the domain name of the Message\-ID header with a new <code>message\_id\_domain</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7765](https\://github\.com/ansible\-collections/community\.general/pull/7765)\)\.
* ssh\_config \- new feature to set <code>AddKeysToAgent</code> option to <code>yes</code> or <code>no</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7703](https\://github\.com/ansible\-collections/community\.general/pull/7703)\)\.
* ssh\_config \- new feature to set <code>IdentitiesOnly</code> option to <code>yes</code> or <code>no</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7704](https\://github\.com/ansible\-collections/community\.general/pull/7704)\)\.
* xcc\_redfish\_command \- added support for raw POSTs \(<code>command\=PostResource</code> in <code>category\=Raw</code>\) without a specific action info \([https\://github\.com/ansible\-collections/community\.general/pull/7746](https\://github\.com/ansible\-collections/community\.general/pull/7746)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* keycloak\_identity\_provider \- <code>mappers</code> processing was not idempotent if the mappers configuration list had not been sorted by name \(in ascending order\)\. Fix resolves the issue by sorting mappers in the desired state using the same key which is used for obtaining existing state \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_identity\_provider \- it was not possible to reconfigure \(add\, remove\) <code>mappers</code> once they were created initially\. Removal was ignored\, adding new ones resulted in dropping the pre\-existing unmodified mappers\. Fix resolves the issue by supplying correct input to the internal update call \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_user \- when <code>force</code> is set\, but user does not exist\, do not try to delete it \([https\://github\.com/ansible\-collections/community\.general/pull/7696](https\://github\.com/ansible\-collections/community\.general/pull/7696)\)\.
* proxmox\_kvm \- running <code>state\=template</code> will first check whether VM is already a template \([https\://github\.com/ansible\-collections/community\.general/pull/7792](https\://github\.com/ansible\-collections/community\.general/pull/7792)\)\.
* statusio\_maintenance \- fix error caused by incorrectly formed API data payload\. Was raising \"Failed to create maintenance HTTP Error 400 Bad Request\" caused by bad data type for date/time and deprecated dict keys \([https\://github\.com/ansible\-collections/community\.general/pull/7754](https\://github\.com/ansible\-collections/community\.general/pull/7754)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="connection"></a>
#### Connection

* incus \- Run tasks in Incus instances via the Incus CLI\.

<a id="filter-1"></a>
#### Filter

* from\_ini \- Converts INI text input into a dictionary
* to\_ini \- Converts a dictionary to the INI file format

<a id="lookup"></a>
#### Lookup

* github\_app\_access\_token \- Obtain short\-lived Github App Access tokens

<a id="new-modules-4"></a>
### New Modules

* dnf\_config\_manager \- Enable or disable dnf repositories using config\-manager
* keycloak\_component\_info \- Retrive component info in Keycloak
* keycloak\_realm\_rolemapping \- Allows administration of Keycloak realm role mappings into groups with the Keycloak API
* proxmox\_node\_info \- Retrieve information about one or more Proxmox VE nodes
* proxmox\_storage\_contents\_info \- List content from a Proxmox VE storage

<a id="v8-1-0"></a>
## v8\.1\.0

<a id="release-summary-5"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-5"></a>
### Minor Changes

* bitwarden lookup plugin \- when looking for items using an item ID\, the item is now accessed directly with <code>bw get item</code> instead of searching through all items\. This doubles the lookup speed \([https\://github\.com/ansible\-collections/community\.general/pull/7468](https\://github\.com/ansible\-collections/community\.general/pull/7468)\)\.
* elastic callback plugin \- close elastic client to not leak resources \([https\://github\.com/ansible\-collections/community\.general/pull/7517](https\://github\.com/ansible\-collections/community\.general/pull/7517)\)\.
* git\_config \- allow multiple git configs for the same name with the new <code>add\_mode</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* git\_config \- the <code>after</code> and <code>before</code> fields in the <code>diff</code> of the return value can be a list instead of a string in case more configs with the same key are affected \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* git\_config \- when a value is unset\, all configs with the same key are unset \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* gitlab modules \- add <code>ca\_path</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7472](https\://github\.com/ansible\-collections/community\.general/pull/7472)\)\.
* gitlab modules \- remove duplicate <code>gitlab</code> package check \([https\://github\.com/ansible\-collections/community\.general/pull/7486](https\://github\.com/ansible\-collections/community\.general/pull/7486)\)\.
* gitlab\_runner \- add support for new runner creation workflow \([https\://github\.com/ansible\-collections/community\.general/pull/7199](https\://github\.com/ansible\-collections/community\.general/pull/7199)\)\.
* ipa\_config \- adds <code>passkey</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7588](https\://github\.com/ansible\-collections/community\.general/pull/7588)\)\.
* ipa\_sudorule \- adds options to include denied commands or command groups \([https\://github\.com/ansible\-collections/community\.general/pull/7415](https\://github\.com/ansible\-collections/community\.general/pull/7415)\)\.
* ipa\_user \- adds <code>idp</code> and <code>passkey</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7589](https\://github\.com/ansible\-collections/community\.general/pull/7589)\)\.
* irc \- add <code>validate\_certs</code> option\, and rename <code>use\_ssl</code> to <code>use\_tls</code>\, while keeping <code>use\_ssl</code> as an alias\. The default value for <code>validate\_certs</code> is <code>false</code> for backwards compatibility\. We recommend to every user of this module to explicitly set <code>use\_tls\=true</code> and <em class="title-reference">validate\_certs\=true\`</em> whenever possible\, especially when communicating to IRC servers over the internet \([https\://github\.com/ansible\-collections/community\.general/pull/7550](https\://github\.com/ansible\-collections/community\.general/pull/7550)\)\.
* keycloak module utils \- expose error message from Keycloak server for HTTP errors in some specific situations \([https\://github\.com/ansible\-collections/community\.general/pull/7645](https\://github\.com/ansible\-collections/community\.general/pull/7645)\)\.
* keycloak\_user\_federation \- add option for <code>krbPrincipalAttribute</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7538](https\://github\.com/ansible\-collections/community\.general/pull/7538)\)\.
* lvol \- change <code>pvs</code> argument type to list of strings \([https\://github\.com/ansible\-collections/community\.general/pull/7676](https\://github\.com/ansible\-collections/community\.general/pull/7676)\, [https\://github\.com/ansible\-collections/community\.general/issues/7504](https\://github\.com/ansible\-collections/community\.general/issues/7504)\)\.
* lxd connection plugin \- tighten the detection logic for lxd <code>Instance not found</code> errors\, to avoid false detection on unrelated errors such as <code>/usr/bin/python3\: not found</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7521](https\://github\.com/ansible\-collections/community\.general/pull/7521)\)\.
* netcup\_dns \- adds support for record types <code>OPENPGPKEY</code>\, <code>SMIMEA</code>\, and <code>SSHFP</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7489](https\://github\.com/ansible\-collections/community\.general/pull/7489)\)\.
* nmcli \- add support for new connection type <code>loopback</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6572](https\://github\.com/ansible\-collections/community\.general/issues/6572)\)\.
* nmcli \- allow for <code>infiniband</code> slaves of <code>bond</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/7569](https\://github\.com/ansible\-collections/community\.general/pull/7569)\)\.
* nmcli \- allow for the setting of <code>MTU</code> for <code>infiniband</code> and <code>bond</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/7499](https\://github\.com/ansible\-collections/community\.general/pull/7499)\)\.
* onepassword lookup plugin \- support 1Password Connect with the opv2 client by setting the connect\_host and connect\_token parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7116](https\://github\.com/ansible\-collections/community\.general/pull/7116)\)\.
* onepassword\_raw lookup plugin \- support 1Password Connect with the opv2 client by setting the connect\_host and connect\_token parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7116](https\://github\.com/ansible\-collections/community\.general/pull/7116)\)
* passwordstore \- adds <code>timestamp</code> and <code>preserve</code> parameters to modify the stored password format \([https\://github\.com/ansible\-collections/community\.general/pull/7426](https\://github\.com/ansible\-collections/community\.general/pull/7426)\)\.
* proxmox \- adds <code>template</code> value to the <code>state</code> parameter\, allowing conversion of container to a template \([https\://github\.com/ansible\-collections/community\.general/pull/7143](https\://github\.com/ansible\-collections/community\.general/pull/7143)\)\.
* proxmox \- adds <code>update</code> parameter\, allowing update of an already existing containers configuration \([https\://github\.com/ansible\-collections/community\.general/pull/7540](https\://github\.com/ansible\-collections/community\.general/pull/7540)\)\.
* proxmox inventory plugin \- adds an option to exclude nodes from the dynamic inventory generation\. The new setting is optional\, not using this option will behave as usual \([https\://github\.com/ansible\-collections/community\.general/issues/6714](https\://github\.com/ansible\-collections/community\.general/issues/6714)\, [https\://github\.com/ansible\-collections/community\.general/pull/7461](https\://github\.com/ansible\-collections/community\.general/pull/7461)\)\.
* proxmox\_disk \- add ability to manipulate CD\-ROM drive \([https\://github\.com/ansible\-collections/community\.general/pull/7495](https\://github\.com/ansible\-collections/community\.general/pull/7495)\)\.
* proxmox\_kvm \- adds <code>template</code> value to the <code>state</code> parameter\, allowing conversion of a VM to a template \([https\://github\.com/ansible\-collections/community\.general/pull/7143](https\://github\.com/ansible\-collections/community\.general/pull/7143)\)\.
* proxmox\_kvm \- support the <code>hookscript</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/7600](https\://github\.com/ansible\-collections/community\.general/issues/7600)\)\.
* proxmox\_ostype \- it is now possible to specify the <code>ostype</code> when creating an LXC container \([https\://github\.com/ansible\-collections/community\.general/pull/7462](https\://github\.com/ansible\-collections/community\.general/pull/7462)\)\.
* proxmox\_vm\_info \- add ability to retrieve configuration info \([https\://github\.com/ansible\-collections/community\.general/pull/7485](https\://github\.com/ansible\-collections/community\.general/pull/7485)\)\.
* redfish\_info \- adding the <code>BootProgress</code> property when getting <code>Systems</code> info \([https\://github\.com/ansible\-collections/community\.general/pull/7626](https\://github\.com/ansible\-collections/community\.general/pull/7626)\)\.
* ssh\_config \- adds <code>controlmaster</code>\, <code>controlpath</code> and <code>controlpersist</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7456](https\://github\.com/ansible\-collections/community\.general/pull/7456)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* apt\-rpm \- the module did not upgrade packages if a newer version exists\. Now the package will be reinstalled if the candidate is newer than the installed version \([https\://github\.com/ansible\-collections/community\.general/issues/7414](https\://github\.com/ansible\-collections/community\.general/issues/7414)\)\.
* cloudflare\_dns \- fix Cloudflare lookup of SHFP records \([https\://github\.com/ansible\-collections/community\.general/issues/7652](https\://github\.com/ansible\-collections/community\.general/issues/7652)\)\.
* interface\_files \- also consider <code>address\_family</code> when changing <code>option\=method</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7610](https\://github\.com/ansible\-collections/community\.general/issues/7610)\, [https\://github\.com/ansible\-collections/community\.general/pull/7612](https\://github\.com/ansible\-collections/community\.general/pull/7612)\)\.
* irc \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* keycloak\_\* \- fix Keycloak API client to quote <code>/</code> properly \([https\://github\.com/ansible\-collections/community\.general/pull/7641](https\://github\.com/ansible\-collections/community\.general/pull/7641)\)\.
* keycloak\_authz\_permission \- resource payload variable for scope\-based permission was constructed as a string\, when it needs to be a list\, even for a single item \([https\://github\.com/ansible\-collections/community\.general/issues/7151](https\://github\.com/ansible\-collections/community\.general/issues/7151)\)\.
* log\_entries callback plugin \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* lvol \- test for output messages in both <code>stdout</code> and <code>stderr</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7601](https\://github\.com/ansible\-collections/community\.general/pull/7601)\, [https\://github\.com/ansible\-collections/community\.general/issues/7182](https\://github\.com/ansible\-collections/community\.general/issues/7182)\)\.
* onepassword lookup plugin \- field and section titles are now case insensitive when using op CLI version two or later\. This matches the behavior of version one \([https\://github\.com/ansible\-collections/community\.general/pull/7564](https\://github\.com/ansible\-collections/community\.general/pull/7564)\)\.
* redhat\_subscription \- use the D\-Bus registration on RHEL 7 only on 7\.4 and
  greater\; older versions of RHEL 7 do not have it
  \([https\://github\.com/ansible\-collections/community\.general/issues/7622](https\://github\.com/ansible\-collections/community\.general/issues/7622)\,
  [https\://github\.com/ansible\-collections/community\.general/pull/7624](https\://github\.com/ansible\-collections/community\.general/pull/7624)\)\.
* terraform \- fix multiline string handling in complex variables \([https\://github\.com/ansible\-collections/community\.general/pull/7535](https\://github\.com/ansible\-collections/community\.general/pull/7535)\)\.

<a id="new-plugins-2"></a>
### New Plugins

<a id="lookup-1"></a>
#### Lookup

* onepassword\_doc \- Fetch documents stored in 1Password

<a id="test"></a>
#### Test

* fqdn\_valid \- Validates fully\-qualified domain names against RFC 1123

<a id="new-modules-5"></a>
### New Modules

* git\_config\_info \- Read git configuration
* gitlab\_issue \- Create\, update\, or delete GitLab issues
* nomad\_token \- Manage Nomad ACL tokens

<a id="v8-0-2"></a>
## v8\.0\.2

<a id="release-summary-6"></a>
### Release Summary

Bugfix release for inclusion in Ansible 9\.0\.0rc1\.

<a id="bugfixes-6"></a>
### Bugfixes

* ocapi\_utils\, oci\_utils\, redfish\_utils module utils \- replace <code>type\(\)</code> calls with <code>isinstance\(\)</code> calls \([https\://github\.com/ansible\-collections/community\.general/pull/7501](https\://github\.com/ansible\-collections/community\.general/pull/7501)\)\.
* pipx module utils \- change the CLI argument formatter for the <code>pip\_args</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/7497](https\://github\.com/ansible\-collections/community\.general/issues/7497)\, [https\://github\.com/ansible\-collections/community\.general/pull/7506](https\://github\.com/ansible\-collections/community\.general/pull/7506)\)\.

<a id="v8-0-1"></a>
## v8\.0\.1

<a id="release-summary-7"></a>
### Release Summary

Bugfix release for inclusion in Ansible 9\.0\.0b1\.

<a id="bugfixes-7"></a>
### Bugfixes

* gitlab\_group\_members \- fix gitlab constants call in <code>gitlab\_group\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_project\_members \- fix gitlab constants call in <code>gitlab\_project\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_protected\_branches \- fix gitlab constants call in <code>gitlab\_protected\_branches</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_user \- fix gitlab constants call in <code>gitlab\_user</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* proxmox\_pool\_member \- absent state for type VM did not delete VMs from the pools \([https\://github\.com/ansible\-collections/community\.general/pull/7464](https\://github\.com/ansible\-collections/community\.general/pull/7464)\)\.
* redfish\_command \- fix usage of message parsing in <code>SimpleUpdate</code> and <code>MultipartHTTPPushUpdate</code> commands to treat the lack of a <code>MessageId</code> as no message \([https\://github\.com/ansible\-collections/community\.general/issues/7465](https\://github\.com/ansible\-collections/community\.general/issues/7465)\, [https\://github\.com/ansible\-collections/community\.general/pull/7471](https\://github\.com/ansible\-collections/community\.general/pull/7471)\)\.

<a id="v8-0-0"></a>
## v8\.0\.0

<a id="release-summary-8"></a>
### Release Summary

This is release 8\.0\.0 of <code>community\.general</code>\, released on 2023\-11\-01\.

<a id="minor-changes-6"></a>
### Minor Changes

* The collection will start using semantic markup \([https\://github\.com/ansible\-collections/community\.general/pull/6539](https\://github\.com/ansible\-collections/community\.general/pull/6539)\)\.
* VarDict module utils \- add method <code>VarDict\.as\_dict\(\)</code> to convert to a plain <code>dict</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/6602](https\://github\.com/ansible\-collections/community\.general/pull/6602)\)\.
* apt\_rpm \- extract package name from local <code>\.rpm</code> path when verifying
  installation success\. Allows installing packages from local <code>\.rpm</code> files
  \([https\://github\.com/ansible\-collections/community\.general/pull/7396](https\://github\.com/ansible\-collections/community\.general/pull/7396)\)\.
* cargo \- add option <code>executable</code>\, which allows user to specify path to the cargo binary \([https\://github\.com/ansible\-collections/community\.general/pull/7352](https\://github\.com/ansible\-collections/community\.general/pull/7352)\)\.
* cargo \- add option <code>locked</code> which allows user to specify install the locked version of dependency instead of latest compatible version \([https\://github\.com/ansible\-collections/community\.general/pull/6134](https\://github\.com/ansible\-collections/community\.general/pull/6134)\)\.
* chroot connection plugin \- add <code>disable\_root\_check</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7099](https\://github\.com/ansible\-collections/community\.general/pull/7099)\)\.
* cloudflare\_dns \- add CAA record support \([https\://github\.com/ansible\-collections/community\.general/pull/7399](https\://github\.com/ansible\-collections/community\.general/pull/7399)\)\.
* cobbler inventory plugin \- add <code>exclude\_mgmt\_classes</code> and <code>include\_mgmt\_classes</code> options to exclude or include hosts based on management classes \([https\://github\.com/ansible\-collections/community\.general/pull/7184](https\://github\.com/ansible\-collections/community\.general/pull/7184)\)\.
* cobbler inventory plugin \- add <code>inventory\_hostname</code> option to allow using the system name for the inventory hostname \([https\://github\.com/ansible\-collections/community\.general/pull/6502](https\://github\.com/ansible\-collections/community\.general/pull/6502)\)\.
* cobbler inventory plugin \- add <code>want\_ip\_addresses</code> option to collect all interface DNS name to IP address mapping \([https\://github\.com/ansible\-collections/community\.general/pull/6711](https\://github\.com/ansible\-collections/community\.general/pull/6711)\)\.
* cobbler inventory plugin \- add primary IP addess to <code>cobbler\_ipv4\_address</code> and IPv6 address to <code>cobbler\_ipv6\_address</code> host variable \([https\://github\.com/ansible\-collections/community\.general/pull/6711](https\://github\.com/ansible\-collections/community\.general/pull/6711)\)\.
* cobbler inventory plugin \- add warning for systems with empty profiles \([https\://github\.com/ansible\-collections/community\.general/pull/6502](https\://github\.com/ansible\-collections/community\.general/pull/6502)\)\.
* cobbler inventory plugin \- convert Ansible unicode strings to native Python unicode strings before passing user/password to XMLRPC client \([https\://github\.com/ansible\-collections/community\.general/pull/6923](https\://github\.com/ansible\-collections/community\.general/pull/6923)\)\.
* consul\_session \- drops requirement for the <code>python\-consul</code> library to communicate with the Consul API\, instead relying on the existing <code>requests</code> library requirement \([https\://github\.com/ansible\-collections/community\.general/pull/6755](https\://github\.com/ansible\-collections/community\.general/pull/6755)\)\.
* copr \- respawn module to use the system python interpreter when the <code>dnf</code> python module is not available in <code>ansible\_python\_interpreter</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6522](https\://github\.com/ansible\-collections/community\.general/pull/6522)\)\.
* cpanm \- minor refactor when creating the <code>CmdRunner</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/7231](https\://github\.com/ansible\-collections/community\.general/pull/7231)\)\.
* datadog\_monitor \- adds <code>notification\_preset\_name</code>\, <code>renotify\_occurrences</code> and <code>renotify\_statuses</code> parameters \([https\://github\.com/ansible\-collections/community\.general/issues/6521\,https\://github\.com/ansible\-collections/community\.general/issues/5823](https\://github\.com/ansible\-collections/community\.general/issues/6521\,https\://github\.com/ansible\-collections/community\.general/issues/5823)\)\.
* dig lookup plugin \- add TCP option to enable the use of TCP connection during DNS lookup \([https\://github\.com/ansible\-collections/community\.general/pull/7343](https\://github\.com/ansible\-collections/community\.general/pull/7343)\)\.
* ejabberd\_user \- module now using <code>CmdRunner</code> to execute external command \([https\://github\.com/ansible\-collections/community\.general/pull/7075](https\://github\.com/ansible\-collections/community\.general/pull/7075)\)\.
* filesystem \- add <code>uuid</code> parameter for UUID change feature \([https\://github\.com/ansible\-collections/community\.general/pull/6680](https\://github\.com/ansible\-collections/community\.general/pull/6680)\)\.
* gitlab\_group \- add option <code>force\_delete</code> \(default\: false\) which allows delete group even if projects exists in it \([https\://github\.com/ansible\-collections/community\.general/pull/7364](https\://github\.com/ansible\-collections/community\.general/pull/7364)\)\.
* gitlab\_group\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/7132](https\://github\.com/ansible\-collections/community\.general/pull/7132)\)\.
* gitlab\_project\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/7132](https\://github\.com/ansible\-collections/community\.general/pull/7132)\)\.
* gitlab\_project\_variable \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* gitlab\_runner \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6927](https\://github\.com/ansible\-collections/community\.general/pull/6927)\)\.
* htpasswd \- minor code improvements in the module \([https\://github\.com/ansible\-collections/community\.general/pull/6901](https\://github\.com/ansible\-collections/community\.general/pull/6901)\)\.
* htpasswd \- the parameter <code>crypt\_scheme</code> is being renamed as <code>hash\_scheme</code> and added as an alias to it \([https\://github\.com/ansible\-collections/community\.general/pull/6841](https\://github\.com/ansible\-collections/community\.general/pull/6841)\)\.
* icinga2\_host \- the <code>ip</code> option is no longer required\, since Icinga 2 allows for an empty address attribute \([https\://github\.com/ansible\-collections/community\.general/pull/7452](https\://github\.com/ansible\-collections/community\.general/pull/7452)\)\.
* ini\_file \- add <code>ignore\_spaces</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7273](https\://github\.com/ansible\-collections/community\.general/pull/7273)\)\.
* ini\_file \- add <code>modify\_inactive\_option</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7401](https\://github\.com/ansible\-collections/community\.general/pull/7401)\)\.
* ipa\_config \- add module parameters to manage FreeIPA user and group objectclasses \([https\://github\.com/ansible\-collections/community\.general/pull/7019](https\://github\.com/ansible\-collections/community\.general/pull/7019)\)\.
* ipa\_config \- adds <code>idp</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7051](https\://github\.com/ansible\-collections/community\.general/pull/7051)\)\.
* jenkins\_build \- add new <code>detach</code> option\, which allows the module to exit successfully as long as the build is created \(default functionality is still waiting for the build to end before exiting\) \([https\://github\.com/ansible\-collections/community\.general/pull/7204](https\://github\.com/ansible\-collections/community\.general/pull/7204)\)\.
* jenkins\_build \- add new <code>time\_between\_checks</code> option\, which allows to configure the wait time between requests to the Jenkins server \([https\://github\.com/ansible\-collections/community\.general/pull/7204](https\://github\.com/ansible\-collections/community\.general/pull/7204)\)\.
* keycloak\_authentication \- added provider ID choices\, since Keycloak supports only those two specific ones \([https\://github\.com/ansible\-collections/community\.general/pull/6763](https\://github\.com/ansible\-collections/community\.general/pull/6763)\)\.
* keycloak\_client\_rolemapping \- adds support for subgroups with additional parameter <code>parents</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6687](https\://github\.com/ansible\-collections/community\.general/pull/6687)\)\.
* keycloak\_role \- add composite roles support for realm and client roles \([https\://github\.com/ansible\-collections/community\.general/pull/6469](https\://github\.com/ansible\-collections/community\.general/pull/6469)\)\.
* keyring \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6927](https\://github\.com/ansible\-collections/community\.general/pull/6927)\)\.
* ldap\_\* \- add new arguments <code>client\_cert</code> and <code>client\_key</code> to the LDAP modules in order to allow certificate authentication \([https\://github\.com/ansible\-collections/community\.general/pull/6668](https\://github\.com/ansible\-collections/community\.general/pull/6668)\)\.
* ldap\_search \- add a new <code>page\_size</code> option to enable paged searches \([https\://github\.com/ansible\-collections/community\.general/pull/6648](https\://github\.com/ansible\-collections/community\.general/pull/6648)\)\.
* locale\_gen \- module has been refactored to use <code>ModuleHelper</code> and <code>CmdRunner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6903](https\://github\.com/ansible\-collections/community\.general/pull/6903)\)\.
* locale\_gen \- module now using <code>CmdRunner</code> to execute external commands \([https\://github\.com/ansible\-collections/community\.general/pull/6820](https\://github\.com/ansible\-collections/community\.general/pull/6820)\)\.
* lvg \- add <code>active</code> and <code>inactive</code> values to the <code>state</code> option for active state management feature \([https\://github\.com/ansible\-collections/community\.general/pull/6682](https\://github\.com/ansible\-collections/community\.general/pull/6682)\)\.
* lvg \- add <code>reset\_vg\_uuid</code>\, <code>reset\_pv\_uuid</code> options for UUID reset feature \([https\://github\.com/ansible\-collections/community\.general/pull/6682](https\://github\.com/ansible\-collections/community\.general/pull/6682)\)\.
* lxc connection plugin \- properly handle a change of the <code>remote\_addr</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7373](https\://github\.com/ansible\-collections/community\.general/pull/7373)\)\.
* lxd connection plugin \- automatically translate <code>remote\_addr</code> from FQDN to \(short\) hostname \([https\://github\.com/ansible\-collections/community\.general/pull/7360](https\://github\.com/ansible\-collections/community\.general/pull/7360)\)\.
* lxd connection plugin \- update error parsing to work with newer messages mentioning instances \([https\://github\.com/ansible\-collections/community\.general/pull/7360](https\://github\.com/ansible\-collections/community\.general/pull/7360)\)\.
* lxd inventory plugin \- add <code>server\_cert</code> option for trust anchor to use for TLS verification of server certificates \([https\://github\.com/ansible\-collections/community\.general/pull/7392](https\://github\.com/ansible\-collections/community\.general/pull/7392)\)\.
* lxd inventory plugin \- add <code>server\_check\_hostname</code> option to disable hostname verification of server certificates \([https\://github\.com/ansible\-collections/community\.general/pull/7392](https\://github\.com/ansible\-collections/community\.general/pull/7392)\)\.
* make \- add new <code>targets</code> parameter allowing multiple targets to be used with <code>make</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6882](https\://github\.com/ansible\-collections/community\.general/pull/6882)\, [https\://github\.com/ansible\-collections/community\.general/issues/4919](https\://github\.com/ansible\-collections/community\.general/issues/4919)\)\.
* make \- allows <code>params</code> to be used without value \([https\://github\.com/ansible\-collections/community\.general/pull/7180](https\://github\.com/ansible\-collections/community\.general/pull/7180)\)\.
* mas \- disable sign\-in check for macOS 12\+ as <code>mas account</code> is non\-functional \([https\://github\.com/ansible\-collections/community\.general/pull/6520](https\://github\.com/ansible\-collections/community\.general/pull/6520)\)\.
* newrelic\_deployment \- add option <code>app\_name\_exact\_match</code>\, which filters results for the exact app\_name provided \([https\://github\.com/ansible\-collections/community\.general/pull/7355](https\://github\.com/ansible\-collections/community\.general/pull/7355)\)\.
* nmap inventory plugin \- now has a <code>use\_arp\_ping</code> option to allow the user to disable the default ARP ping query for a more reliable form \([https\://github\.com/ansible\-collections/community\.general/pull/7119](https\://github\.com/ansible\-collections/community\.general/pull/7119)\)\.
* nmcli \- add support for <code>ipv4\.dns\-options</code> and <code>ipv6\.dns\-options</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6902](https\://github\.com/ansible\-collections/community\.general/pull/6902)\)\.
* nomad\_job\, nomad\_job\_info \- add <code>port</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/7412](https\://github\.com/ansible\-collections/community\.general/pull/7412)\)\.
* npm \- minor improvement on parameter validation \([https\://github\.com/ansible\-collections/community\.general/pull/6848](https\://github\.com/ansible\-collections/community\.general/pull/6848)\)\.
* npm \- module now using <code>CmdRunner</code> to execute external commands \([https\://github\.com/ansible\-collections/community\.general/pull/6989](https\://github\.com/ansible\-collections/community\.general/pull/6989)\)\.
* onepassword lookup plugin \- add service account support \([https\://github\.com/ansible\-collections/community\.general/issues/6635](https\://github\.com/ansible\-collections/community\.general/issues/6635)\, [https\://github\.com/ansible\-collections/community\.general/pull/6660](https\://github\.com/ansible\-collections/community\.general/pull/6660)\)\.
* onepassword lookup plugin \- introduce <code>account\_id</code> option which allows specifying which account to use \([https\://github\.com/ansible\-collections/community\.general/pull/7308](https\://github\.com/ansible\-collections/community\.general/pull/7308)\)\.
* onepassword\_raw lookup plugin \- add service account support \([https\://github\.com/ansible\-collections/community\.general/issues/6635](https\://github\.com/ansible\-collections/community\.general/issues/6635)\, [https\://github\.com/ansible\-collections/community\.general/pull/6660](https\://github\.com/ansible\-collections/community\.general/pull/6660)\)\.
* onepassword\_raw lookup plugin \- introduce <code>account\_id</code> option which allows specifying which account to use \([https\://github\.com/ansible\-collections/community\.general/pull/7308](https\://github\.com/ansible\-collections/community\.general/pull/7308)\)\.
* opentelemetry callback plugin \- add span attributes in the span event \([https\://github\.com/ansible\-collections/community\.general/pull/6531](https\://github\.com/ansible\-collections/community\.general/pull/6531)\)\.
* opkg \- add <code>executable</code> parameter allowing to specify the path of the <code>opkg</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/6862](https\://github\.com/ansible\-collections/community\.general/pull/6862)\)\.
* opkg \- remove default value <code>\"\"</code> for parameter <code>force</code> as it causes the same behaviour of not having that parameter \([https\://github\.com/ansible\-collections/community\.general/pull/6513](https\://github\.com/ansible\-collections/community\.general/pull/6513)\)\.
* pagerduty \- adds in option to use v2 API for creating pagerduty incidents \([https\://github\.com/ansible\-collections/community\.general/issues/6151](https\://github\.com/ansible\-collections/community\.general/issues/6151)\)
* parted \- on resize\, use <code>\-\-fix</code> option if available \([https\://github\.com/ansible\-collections/community\.general/pull/7304](https\://github\.com/ansible\-collections/community\.general/pull/7304)\)\.
* pnpm \- set correct version when state is latest or version is not mentioned\. Resolves previous idempotency problem \([https\://github\.com/ansible\-collections/community\.general/pull/7339](https\://github\.com/ansible\-collections/community\.general/pull/7339)\)\.
* pritunl module utils \- ensure <code>validate\_certs</code> parameter is honoured in all methods \([https\://github\.com/ansible\-collections/community\.general/pull/7156](https\://github\.com/ansible\-collections/community\.general/pull/7156)\)\.
* proxmox \- add <code>vmid</code> \(and <code>taskid</code> when possible\) to return values \([https\://github\.com/ansible\-collections/community\.general/pull/7263](https\://github\.com/ansible\-collections/community\.general/pull/7263)\)\.
* proxmox \- support <code>timezone</code> parameter at container creation \([https\://github\.com/ansible\-collections/community\.general/pull/6510](https\://github\.com/ansible\-collections/community\.general/pull/6510)\)\.
* proxmox inventory plugin \- add composite variables support for Proxmox nodes \([https\://github\.com/ansible\-collections/community\.general/issues/6640](https\://github\.com/ansible\-collections/community\.general/issues/6640)\)\.
* proxmox\_kvm \- added support for <code>tpmstate0</code> parameter to configure TPM \(Trusted Platform Module\) disk\. TPM is required for Windows 11 installations \([https\://github\.com/ansible\-collections/community\.general/pull/6533](https\://github\.com/ansible\-collections/community\.general/pull/6533)\)\.
* proxmox\_kvm \- enabled force restart of VM\, bringing the <code>force</code> parameter functionality in line with what is described in the docs \([https\://github\.com/ansible\-collections/community\.general/pull/6914](https\://github\.com/ansible\-collections/community\.general/pull/6914)\)\.
* proxmox\_kvm \- re\-use <code>timeout</code> module param to forcefully shutdown a virtual machine when <code>state</code> is <code>stopped</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6257](https\://github\.com/ansible\-collections/community\.general/issues/6257)\)\.
* proxmox\_snap \- add <code>retention</code> parameter to delete old snapshots \([https\://github\.com/ansible\-collections/community\.general/pull/6576](https\://github\.com/ansible\-collections/community\.general/pull/6576)\)\.
* proxmox\_vm\_info \- <code>node</code> parameter is no longer required\. Information can be obtained for the whole cluster \([https\://github\.com/ansible\-collections/community\.general/pull/6976](https\://github\.com/ansible\-collections/community\.general/pull/6976)\)\.
* proxmox\_vm\_info \- non\-existing provided by name/vmid VM would return empty results instead of failing \([https\://github\.com/ansible\-collections/community\.general/pull/7049](https\://github\.com/ansible\-collections/community\.general/pull/7049)\)\.
* pubnub\_blocks \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* random\_string \- added new <code>ignore\_similar\_chars</code> and <code>similar\_chars</code> option to ignore certain chars \([https\://github\.com/ansible\-collections/community\.general/pull/7242](https\://github\.com/ansible\-collections/community\.general/pull/7242)\)\.
* redfish\_command \- add <code>MultipartHTTPPushUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/6471](https\://github\.com/ansible\-collections/community\.general/issues/6471)\, [https\://github\.com/ansible\-collections/community\.general/pull/6612](https\://github\.com/ansible\-collections/community\.general/pull/6612)\)\.
* redfish\_command \- add <code>account\_types</code> and <code>oem\_account\_types</code> as optional inputs to <code>AddUser</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6823](https\://github\.com/ansible\-collections/community\.general/issues/6823)\, [https\://github\.com/ansible\-collections/community\.general/pull/6871](https\://github\.com/ansible\-collections/community\.general/pull/6871)\)\.
* redfish\_command \- add new option <code>update\_oem\_params</code> for the <code>MultipartHTTPPushUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/7331](https\://github\.com/ansible\-collections/community\.general/issues/7331)\)\.
* redfish\_config \- add <code>CreateVolume</code> command to allow creation of volumes on servers \([https\://github\.com/ansible\-collections/community\.general/pull/6813](https\://github\.com/ansible\-collections/community\.general/pull/6813)\)\.
* redfish\_config \- add <code>DeleteAllVolumes</code> command to allow deletion of all volumes on servers \([https\://github\.com/ansible\-collections/community\.general/pull/6814](https\://github\.com/ansible\-collections/community\.general/pull/6814)\)\.
* redfish\_config \- adding <code>SetSecureBoot</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/7129](https\://github\.com/ansible\-collections/community\.general/pull/7129)\)\.
* redfish\_info \- add <code>AccountTypes</code> and <code>OEMAccountTypes</code> to the output of <code>ListUsers</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6823](https\://github\.com/ansible\-collections/community\.general/issues/6823)\, [https\://github\.com/ansible\-collections/community\.general/pull/6871](https\://github\.com/ansible\-collections/community\.general/pull/6871)\)\.
* redfish\_info \- add support for <code>GetBiosRegistries</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/7144](https\://github\.com/ansible\-collections/community\.general/pull/7144)\)\.
* redfish\_info \- adds <code>LinkStatus</code> to NIC inventory \([https\://github\.com/ansible\-collections/community\.general/pull/7318](https\://github\.com/ansible\-collections/community\.general/pull/7318)\)\.
* redfish\_info \- adds <code>ProcessorArchitecture</code> to CPU inventory \([https\://github\.com/ansible\-collections/community\.general/pull/6864](https\://github\.com/ansible\-collections/community\.general/pull/6864)\)\.
* redfish\_info \- fix for <code>GetVolumeInventory</code>\, Controller name was getting populated incorrectly and duplicates were seen in the volumes retrieved \([https\://github\.com/ansible\-collections/community\.general/pull/6719](https\://github\.com/ansible\-collections/community\.general/pull/6719)\)\.
* redfish\_info \- report <code>Id</code> in the output of <code>GetManagerInventory</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7140](https\://github\.com/ansible\-collections/community\.general/pull/7140)\)\.
* redfish\_utils \- use <code>Controllers</code> key in redfish data to obtain Storage controllers properties \([https\://github\.com/ansible\-collections/community\.general/pull/7081](https\://github\.com/ansible\-collections/community\.general/pull/7081)\)\.
* redfish\_utils module utils \- add support for <code>PowerCycle</code> reset type for <code>redfish\_command</code> responses feature \([https\://github\.com/ansible\-collections/community\.general/issues/7083](https\://github\.com/ansible\-collections/community\.general/issues/7083)\)\.
* redfish\_utils module utils \- add support for following <code>\@odata\.nextLink</code> pagination in <code>software\_inventory</code> responses feature \([https\://github\.com/ansible\-collections/community\.general/pull/7020](https\://github\.com/ansible\-collections/community\.general/pull/7020)\)\.
* redfish\_utils module utils \- support <code>Volumes</code> in response for <code>GetDiskInventory</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6819](https\://github\.com/ansible\-collections/community\.general/pull/6819)\)\.
* redhat\_subscription \- the internal <code>RegistrationBase</code> class was folded
  into the other internal <code>Rhsm</code> class\, as the separation had no purpose
  anymore
  \([https\://github\.com/ansible\-collections/community\.general/pull/6658](https\://github\.com/ansible\-collections/community\.general/pull/6658)\)\.
* redis\_info \- refactor the redis\_info module to use the redis module\_utils enabling to pass TLS parameters to the Redis client \([https\://github\.com/ansible\-collections/community\.general/pull/7267](https\://github\.com/ansible\-collections/community\.general/pull/7267)\)\.
* rhsm\_release \- improve/harden the way <code>subscription\-manager</code> is run\;
  no behaviour change is expected
  \([https\://github\.com/ansible\-collections/community\.general/pull/6669](https\://github\.com/ansible\-collections/community\.general/pull/6669)\)\.
* rhsm\_repository \- the interaction with <code>subscription\-manager</code> was
  refactored by grouping things together\, removing unused bits\, and hardening
  the way it is run\; also\, the parsing of <code>subscription\-manager repos \-\-list</code>
  was improved and made slightly faster\; no behaviour change is expected
  \([https\://github\.com/ansible\-collections/community\.general/pull/6783](https\://github\.com/ansible\-collections/community\.general/pull/6783)\,
  [https\://github\.com/ansible\-collections/community\.general/pull/6837](https\://github\.com/ansible\-collections/community\.general/pull/6837)\)\.
* scaleway\_security\_group\_rule \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* shutdown \- use <code>shutdown \-p \.\.\.</code> with FreeBSD to halt and power off machine \([https\://github\.com/ansible\-collections/community\.general/pull/7102](https\://github\.com/ansible\-collections/community\.general/pull/7102)\)\.
* snap \- add option <code>dangerous</code> to the module\, that will map into the command line argument <code>\-\-dangerous</code>\, allowing unsigned snap files to be installed \([https\://github\.com/ansible\-collections/community\.general/pull/6908](https\://github\.com/ansible\-collections/community\.general/pull/6908)\, [https\://github\.com/ansible\-collections/community\.general/issues/5715](https\://github\.com/ansible\-collections/community\.general/issues/5715)\)\.
* snap \- module is now aware of channel when deciding whether to install or refresh the snap \([https\://github\.com/ansible\-collections/community\.general/pull/6435](https\://github\.com/ansible\-collections/community\.general/pull/6435)\, [https\://github\.com/ansible\-collections/community\.general/issues/1606](https\://github\.com/ansible\-collections/community\.general/issues/1606)\)\.
* sorcery \- add grimoire \(repository\) management support \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* sorcery \- minor refactor \([https\://github\.com/ansible\-collections/community\.general/pull/6525](https\://github\.com/ansible\-collections/community\.general/pull/6525)\)\.
* supervisorctl \- allow to stop matching running processes before removing them with <code>stop\_before\_removing\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7284](https\://github\.com/ansible\-collections/community\.general/pull/7284)\)\.
* tss lookup plugin \- allow to fetch secret IDs which are in a folder based on folder ID\. Previously\, we could not fetch secrets based on folder ID but now use <code>fetch\_secret\_ids\_from\_folder</code> option to indicate to fetch secret IDs based on folder ID \([https\://github\.com/ansible\-collections/community\.general/issues/6223](https\://github\.com/ansible\-collections/community\.general/issues/6223)\)\.
* tss lookup plugin \- allow to fetch secret by path\. Previously\, we could not fetch secret by path but now use <code>secret\_path</code> option to indicate to fetch secret by secret path \([https\://github\.com/ansible\-collections/community\.general/pull/6881](https\://github\.com/ansible\-collections/community\.general/pull/6881)\)\.
* unixy callback plugin \- add support for <code>check\_mode\_markers</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7179](https\://github\.com/ansible\-collections/community\.general/pull/7179)\)\.
* vardict module utils \- added convenience methods to <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6647](https\://github\.com/ansible\-collections/community\.general/pull/6647)\)\.
* xenserver\_guest\_info \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* xenserver\_guest\_powerstate \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* yum\_versionlock \- add support to pin specific package versions instead of only the package itself \([https\://github\.com/ansible\-collections/community\.general/pull/6861](https\://github\.com/ansible\-collections/community\.general/pull/6861)\, [https\://github\.com/ansible\-collections/community\.general/issues/4470](https\://github\.com/ansible\-collections/community\.general/issues/4470)\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* collection\_version lookup plugin \- remove compatibility code for ansible\-base 2\.10 and ansible\-core 2\.11 \([https\://github\.com/ansible\-collections/community\.general/pull/7269](https\://github\.com/ansible\-collections/community\.general/pull/7269)\)\.
* gitlab\_project \- add <code>default\_branch</code> support for project update\. If you used the module so far with <code>default\_branch</code> to update a project\, the value of <code>default\_branch</code> was ignored\. Make sure that you either do not pass a value if you are not sure whether it is the one you want to have to avoid unexpected breaking changes \([https\://github\.com/ansible\-collections/community\.general/pull/7158](https\://github\.com/ansible\-collections/community\.general/pull/7158)\)\.
* selective callback plugin \- remove compatibility code for Ansible 2\.9 and ansible\-core 2\.10 \([https\://github\.com/ansible\-collections/community\.general/pull/7269](https\://github\.com/ansible\-collections/community\.general/pull/7269)\)\.
* vardict module utils \- <code>VarDict</code> will no longer accept variables named <code>\_var</code>\, <code>get\_meta</code>\, and <code>as\_dict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6647](https\://github\.com/ansible\-collections/community\.general/pull/6647)\)\.
* version module util \- remove fallback for ansible\-core 2\.11\. All modules and plugins that do version collections no longer work with ansible\-core 2\.11 \([https\://github\.com/ansible\-collections/community\.general/pull/7269](https\://github\.com/ansible\-collections/community\.general/pull/7269)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* CmdRunner module utils \- deprecate <code>cmd\_runner\_fmt\.as\_default\_type\(\)</code> formatter \([https\://github\.com/ansible\-collections/community\.general/pull/6601](https\://github\.com/ansible\-collections/community\.general/pull/6601)\)\.
* MH VarsMixin module utils \- deprecates <code>VarsMixin</code> and supporting classes in favor of plain <code>vardict</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/6649](https\://github\.com/ansible\-collections/community\.general/pull/6649)\)\.
* ansible\_galaxy\_install \- the <code>ack\_ansible29</code> and <code>ack\_min\_ansiblecore211</code> options have been deprecated and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* consul \- the <code>ack\_params\_state\_absent</code> option has been deprecated and will be removed in community\.general 10\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* cpanm \- value <code>compatibility</code> is deprecated as default for parameter <code>mode</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6512](https\://github\.com/ansible\-collections/community\.general/pull/6512)\)\.
* ejabberd\_user \- deprecate the parameter <code>logging</code> in favour of producing more detailed information in the module output \([https\://github\.com/ansible\-collections/community\.general/pull/7043](https\://github\.com/ansible\-collections/community\.general/pull/7043)\)\.
* flowdock \- module relies entirely on no longer responsive API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6930](https\://github\.com/ansible\-collections/community\.general/pull/6930)\)\.
* proxmox \- old feature flag <code>proxmox\_default\_behavior</code> will be removed in community\.general 10\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6836](https\://github\.com/ansible\-collections/community\.general/pull/6836)\)\.
* proxmox\_kvm \- deprecate the option <code>proxmox\_default\_behavior</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7377](https\://github\.com/ansible\-collections/community\.general/pull/7377)\)\.
* redfish\_info\, redfish\_config\, redfish\_command \- the default value <code>10</code> for the <code>timeout</code> option is deprecated and will change to <code>60</code> in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/7295](https\://github\.com/ansible\-collections/community\.general/pull/7295)\)\.
* redhat module utils \- the <code>module\_utils\.redhat</code> module is deprecated\, as
  effectively unused\: the <code>Rhsm</code>\, <code>RhsmPool</code>\, and <code>RhsmPools</code> classes
  will be removed in community\.general 9\.0\.0\; the <code>RegistrationBase</code> class
  will be removed in community\.general 10\.0\.0 together with the
  <code>rhn\_register</code> module\, as it is the only user of this class\; this means
  that the whole <code>module\_utils\.redhat</code> module will be dropped in
  community\.general 10\.0\.0\, so importing it without even using anything of it
  will fail
  \([https\://github\.com/ansible\-collections/community\.general/pull/6663](https\://github\.com/ansible\-collections/community\.general/pull/6663)\)\.
* redhat\_subscription \- the <code>autosubscribe</code> alias for the <code>auto\_attach</code> option has been
  deprecated for many years\, although only in the documentation\. Officially mark this alias
  as deprecated\, and it will be removed in community\.general 9\.0\.0
  \([https\://github\.com/ansible\-collections/community\.general/pull/6646](https\://github\.com/ansible\-collections/community\.general/pull/6646)\)\.
* redhat\_subscription \- the <code>pool</code> option is deprecated in favour of the
  more precise and flexible <code>pool\_ids</code> option
  \([https\://github\.com/ansible\-collections/community\.general/pull/6650](https\://github\.com/ansible\-collections/community\.general/pull/6650)\)\.
* rhsm\_repository \- <code>state\=present</code> has not been working as expected for many years\,
  and it seems it was not noticed so far\; also\, \"presence\" is not really a valid concept
  for subscription repositories\, which can only be enabled or disabled\. Hence\, mark the
  <code>present</code> and <code>absent</code> values of the <code>state</code> option as deprecated\, slating them
  for removal in community\.general 10\.0\.0
  \([https\://github\.com/ansible\-collections/community\.general/pull/6673](https\://github\.com/ansible\-collections/community\.general/pull/6673)\)\.
* stackdriver \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6887](https\://github\.com/ansible\-collections/community\.general/pull/6887)\)\.
* webfaction\_app \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_db \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_domain \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_mailbox \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_site \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* The collection no longer supports ansible\-core 2\.11 and ansible\-core 2\.12\. Parts of the collection might still work on these ansible\-core versions\, but others might not \([https\://github\.com/ansible\-collections/community\.general/pull/7269](https\://github\.com/ansible\-collections/community\.general/pull/7269)\)\.
* ansible\_galaxy\_install \- support for Ansible 2\.9 and ansible\-base 2\.10 has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* consul \- when <code>state\=absent</code>\, the options <code>script</code>\, <code>ttl</code>\, <code>tcp</code>\, <code>http</code>\, and <code>interval</code> can no longer be specified \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* gconftool2 \- <code>state\=get</code> has been removed\. Use the module <code>community\.general\.gconftool2\_info</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* gitlab\_runner \- remove the default value for the <code>access\_level</code> option\. To restore the previous behavior\, explicitly set it to <code>ref\_protected</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* htpasswd \- removed code for passlib \<1\.6 \([https\://github\.com/ansible\-collections/community\.general/pull/6901](https\://github\.com/ansible\-collections/community\.general/pull/6901)\)\.
* manageiq\_polices \- <code>state\=list</code> has been removed\. Use the module <code>community\.general\.manageiq\_policies\_info</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* manageiq\_tags \- <code>state\=list</code> has been removed\. Use the module <code>community\.general\.manageiq\_tags\_info</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* mh\.mixins\.cmd module utils \- the <code>ArgFormat</code> class has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* mh\.mixins\.cmd module utils \- the <code>CmdMixin</code> mixin has been removed\. Use <code>community\.general\.plugins\.module\_utils\.cmd\_runner\.CmdRunner</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* mh\.mixins\.cmd module utils \- the mh\.mixins\.cmd module utils has been removed after all its contents were removed \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* mh\.module\_helper module utils \- the <code>CmdModuleHelper</code> and <code>CmdStateModuleHelper</code> classes have been removed\. Use <code>community\.general\.plugins\.module\_utils\.cmd\_runner\.CmdRunner</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.
* proxmox module utils \- removed unused imports \([https\://github\.com/ansible\-collections/community\.general/pull/6873](https\://github\.com/ansible\-collections/community\.general/pull/6873)\)\.
* xfconf \- the deprecated <code>disable\_facts</code> option was removed \([https\://github\.com/ansible\-collections/community\.general/pull/7358](https\://github\.com/ansible\-collections/community\.general/pull/7358)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* CmdRunner module utils \- does not attempt to resolve path if executable is a relative or absolute path \([https\://github\.com/ansible\-collections/community\.general/pull/7200](https\://github\.com/ansible\-collections/community\.general/pull/7200)\)\.
* MH DependencyMixin module utils \- deprecation notice was popping up for modules not using dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/6644](https\://github\.com/ansible\-collections/community\.general/pull/6644)\, [https\://github\.com/ansible\-collections/community\.general/issues/6639](https\://github\.com/ansible\-collections/community\.general/issues/6639)\)\.
* bitwarden lookup plugin \- the plugin made assumptions about the structure of a Bitwarden JSON object which may have been broken by an update in the Bitwarden API\. Remove assumptions\, and allow queries for general fields such as <code>notes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7061](https\://github\.com/ansible\-collections/community\.general/pull/7061)\)\.
* cmd\_runner module utils \- when a parameter in <code>argument\_spec</code> has no type\, meaning it is implicitly a <code>str</code>\, <code>CmdRunner</code> would fail trying to find the <code>type</code> key in that dictionary \([https\://github\.com/ansible\-collections/community\.general/pull/6968](https\://github\.com/ansible\-collections/community\.general/pull/6968)\)\.
* cobbler inventory plugin \- fix calculation of cobbler\_ipv4/6\_address \([https\://github\.com/ansible\-collections/community\.general/pull/6925](https\://github\.com/ansible\-collections/community\.general/pull/6925)\)\.
* composer \- fix impossible to run <code>working\_dir</code> dependent commands\. The module was throwing an error when trying to run a <code>working\_dir</code> dependent command\, because it tried to get the command help without passing the <code>working\_dir</code> \([https\://github\.com/ansible\-collections/community\.general/issues/3787](https\://github\.com/ansible\-collections/community\.general/issues/3787)\)\.
* csv module utils \- detects and remove unicode BOM markers from incoming CSV content \([https\://github\.com/ansible\-collections/community\.general/pull/6662](https\://github\.com/ansible\-collections/community\.general/pull/6662)\)\.
* datadog\_downtime \- presence of <code>rrule</code> param lead to the Datadog API returning Bad Request due to a missing recurrence type \([https\://github\.com/ansible\-collections/community\.general/pull/6811](https\://github\.com/ansible\-collections/community\.general/pull/6811)\)\.
* ejabberd\_user \- module was failing to detect whether user was already created and/or password was changed \([https\://github\.com/ansible\-collections/community\.general/pull/7033](https\://github\.com/ansible\-collections/community\.general/pull/7033)\)\.
* ejabberd\_user \- provide meaningful error message when the <code>ejabberdctl</code> command is not found \([https\://github\.com/ansible\-collections/community\.general/pull/7028](https\://github\.com/ansible\-collections/community\.general/pull/7028)\, [https\://github\.com/ansible\-collections/community\.general/issues/6949](https\://github\.com/ansible\-collections/community\.general/issues/6949)\)\.
* github\_deploy\_key \- fix pagination behaviour causing a crash when only a single page of deploy keys exist \([https\://github\.com/ansible\-collections/community\.general/pull/7375](https\://github\.com/ansible\-collections/community\.general/pull/7375)\)\.
* gitlab\_group \- the module passed parameters to the API call even when not set\. The module is now filtering out <code>None</code> values to remediate this \([https\://github\.com/ansible\-collections/community\.general/pull/6712](https\://github\.com/ansible\-collections/community\.general/pull/6712)\)\.
* gitlab\_group\_variable \- deleted all variables when used with <code>purge\=true</code> due to missing <code>raw</code> property in KNOWN attributes \([https\://github\.com/ansible\-collections/community\.general/issues/7250](https\://github\.com/ansible\-collections/community\.general/issues/7250)\)\.
* gitlab\_project\_variable \- deleted all variables when used with <code>purge\=true</code> due to missing <code>raw</code> property in KNOWN attributes \([https\://github\.com/ansible\-collections/community\.general/issues/7250](https\://github\.com/ansible\-collections/community\.general/issues/7250)\)\.
* icinga2\_host \- fix a key error when updating an existing host \([https\://github\.com/ansible\-collections/community\.general/pull/6748](https\://github\.com/ansible\-collections/community\.general/pull/6748)\)\.
* ini\_file \- add the <code>follow</code> paramter to follow the symlinks instead of replacing them \([https\://github\.com/ansible\-collections/community\.general/pull/6546](https\://github\.com/ansible\-collections/community\.general/pull/6546)\)\.
* ini\_file \- fix a bug where the inactive options were not used when possible \([https\://github\.com/ansible\-collections/community\.general/pull/6575](https\://github\.com/ansible\-collections/community\.general/pull/6575)\)\.
* ipa\_dnszone \- fix \'idnsallowsyncptr\' key error for reverse zone \([https\://github\.com/ansible\-collections/community\.general/pull/6906](https\://github\.com/ansible\-collections/community\.general/pull/6906)\, [https\://github\.com/ansible\-collections/community\.general/issues/6905](https\://github\.com/ansible\-collections/community\.general/issues/6905)\)\.
* kernel\_blacklist \- simplified the mechanism to update the file\, fixing the error \([https\://github\.com/ansible\-collections/community\.general/pull/7382](https\://github\.com/ansible\-collections/community\.general/pull/7382)\, [https\://github\.com/ansible\-collections/community\.general/issues/7362](https\://github\.com/ansible\-collections/community\.general/issues/7362)\)\.
* keycloak module util \- fix missing <code>http\_agent</code>\, <code>timeout</code>\, and <code>validate\_certs</code> <code>open\_url\(\)</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7067](https\://github\.com/ansible\-collections/community\.general/pull/7067)\)\.
* keycloak module utils \- fix <code>is\_struct\_included</code> handling of lists of lists/dictionaries \([https\://github\.com/ansible\-collections/community\.general/pull/6688](https\://github\.com/ansible\-collections/community\.general/pull/6688)\)\.
* keycloak module utils \- the function <code>get\_user\_by\_username</code> now return the user representation or <code>None</code> as stated in the documentation \([https\://github\.com/ansible\-collections/community\.general/pull/6758](https\://github\.com/ansible\-collections/community\.general/pull/6758)\)\.
* keycloak\_authentication \- fix Keycloak authentication flow \(step or sub\-flow\) indexing during update\, if not specified by the user \([https\://github\.com/ansible\-collections/community\.general/pull/6734](https\://github\.com/ansible\-collections/community\.general/pull/6734)\)\.
* keycloak\_client inventory plugin \- fix missing client secret \([https\://github\.com/ansible\-collections/community\.general/pull/6931](https\://github\.com/ansible\-collections/community\.general/pull/6931)\)\.
* ldap\_search \- fix string normalization and the <code>base64\_attributes</code> option on Python 3 \([https\://github\.com/ansible\-collections/community\.general/issues/5704](https\://github\.com/ansible\-collections/community\.general/issues/5704)\, [https\://github\.com/ansible\-collections/community\.general/pull/7264](https\://github\.com/ansible\-collections/community\.general/pull/7264)\)\.
* locale\_gen \- now works for locales without the underscore character such as <code>C\.UTF\-8</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6774](https\://github\.com/ansible\-collections/community\.general/pull/6774)\, [https\://github\.com/ansible\-collections/community\.general/issues/5142](https\://github\.com/ansible\-collections/community\.general/issues/5142)\, [https\://github\.com/ansible\-collections/community\.general/issues/4305](https\://github\.com/ansible\-collections/community\.general/issues/4305)\)\.
* lvol \- add support for percentage of origin size specification when creating snapshot volumes \([https\://github\.com/ansible\-collections/community\.general/issues/1630](https\://github\.com/ansible\-collections/community\.general/issues/1630)\, [https\://github\.com/ansible\-collections/community\.general/pull/7053](https\://github\.com/ansible\-collections/community\.general/pull/7053)\)\.
* lxc connection plugin \- now handles <code>remote\_addr</code> defaulting to <code>inventory\_hostname</code> correctly \([https\://github\.com/ansible\-collections/community\.general/pull/7104](https\://github\.com/ansible\-collections/community\.general/pull/7104)\)\.
* lxc connection plugin \- properly evaluate options \([https\://github\.com/ansible\-collections/community\.general/pull/7369](https\://github\.com/ansible\-collections/community\.general/pull/7369)\)\.
* machinectl become plugin \- mark plugin as <code>require\_tty</code> to automatically disable pipelining\, with which this plugin is not compatible \([https\://github\.com/ansible\-collections/community\.general/issues/6932](https\://github\.com/ansible\-collections/community\.general/issues/6932)\, [https\://github\.com/ansible\-collections/community\.general/pull/6935](https\://github\.com/ansible\-collections/community\.general/pull/6935)\)\.
* mail \- skip headers containing equals characters due to missing <code>maxsplit</code> on header key/value parsing \([https\://github\.com/ansible\-collections/community\.general/pull/7303](https\://github\.com/ansible\-collections/community\.general/pull/7303)\)\.
* memset module utils \- make compatible with ansible\-core 2\.17 \([https\://github\.com/ansible\-collections/community\.general/pull/7379](https\://github\.com/ansible\-collections/community\.general/pull/7379)\)\.
* nmap inventory plugin \- fix <code>get\_option</code> calls \([https\://github\.com/ansible\-collections/community\.general/pull/7323](https\://github\.com/ansible\-collections/community\.general/pull/7323)\)\.
* nmap inventory plugin \- now uses <code>get\_option</code> in all cases to get its configuration information \([https\://github\.com/ansible\-collections/community\.general/pull/7119](https\://github\.com/ansible\-collections/community\.general/pull/7119)\)\.
* nmcli \- fix bond option <code>xmit\_hash\_policy</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6527](https\://github\.com/ansible\-collections/community\.general/pull/6527)\)\.
* nmcli \- fix support for empty list \(in compare and scrape\) \([https\://github\.com/ansible\-collections/community\.general/pull/6769](https\://github\.com/ansible\-collections/community\.general/pull/6769)\)\.
* nsupdate \- fix a possible <code>list index out of range</code> exception \([https\://github\.com/ansible\-collections/community\.general/issues/836](https\://github\.com/ansible\-collections/community\.general/issues/836)\)\.
* oci\_utils module util \- fix inappropriate logical comparison expressions and makes them simpler\. The previous checks had logical short circuits \([https\://github\.com/ansible\-collections/community\.general/pull/7125](https\://github\.com/ansible\-collections/community\.general/pull/7125)\)\.
* oci\_utils module utils \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* onepassword \- fix KeyError exception when trying to access value of a field that is not filled out in OnePassword item \([https\://github\.com/ansible\-collections/community\.general/pull/7241](https\://github\.com/ansible\-collections/community\.general/pull/7241)\)\.
* openbsd\_pkg \- the pkg\_info\(1\) behavior has changed in OpenBSD \>7\.3\. The error message <code>Can\'t find</code> should not lead to an error case \([https\://github\.com/ansible\-collections/community\.general/pull/6785](https\://github\.com/ansible\-collections/community\.general/pull/6785)\)\.
* pacman \- module recognizes the output of <code>yay</code> running as <code>root</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6713](https\://github\.com/ansible\-collections/community\.general/pull/6713)\)\.
* portage \- fix <code>changed\_use</code> and <code>newuse</code> not triggering rebuilds \([https\://github\.com/ansible\-collections/community\.general/issues/6008](https\://github\.com/ansible\-collections/community\.general/issues/6008)\, [https\://github\.com/ansible\-collections/community\.general/pull/6548](https\://github\.com/ansible\-collections/community\.general/pull/6548)\)\.
* pritunl module utils \- fix incorrect URL parameter for orgnization add method \([https\://github\.com/ansible\-collections/community\.general/pull/7161](https\://github\.com/ansible\-collections/community\.general/pull/7161)\)\.
* proxmox \- fix error when a configuration had no <code>template</code> field \([https\://github\.com/ansible\-collections/community\.general/pull/6838](https\://github\.com/ansible\-collections/community\.general/pull/6838)\, [https\://github\.com/ansible\-collections/community\.general/issues/5372](https\://github\.com/ansible\-collections/community\.general/issues/5372)\)\.
* proxmox module utils \- add logic to detect whether an old Promoxer complains about the <code>token\_name</code> and <code>token\_value</code> parameters and provide a better error message when that happens \([https\://github\.com/ansible\-collections/community\.general/pull/6839](https\://github\.com/ansible\-collections/community\.general/pull/6839)\, [https\://github\.com/ansible\-collections/community\.general/issues/5371](https\://github\.com/ansible\-collections/community\.general/issues/5371)\)\.
* proxmox module utils \- fix proxmoxer library version check \([https\://github\.com/ansible\-collections/community\.general/issues/6974](https\://github\.com/ansible\-collections/community\.general/issues/6974)\, [https\://github\.com/ansible\-collections/community\.general/issues/6975](https\://github\.com/ansible\-collections/community\.general/issues/6975)\, [https\://github\.com/ansible\-collections/community\.general/pull/6980](https\://github\.com/ansible\-collections/community\.general/pull/6980)\)\.
* proxmox\_disk \- fix unable to create <code>cdrom</code> media due to <code>size</code> always being appended \([https\://github\.com/ansible\-collections/community\.general/pull/6770](https\://github\.com/ansible\-collections/community\.general/pull/6770)\)\.
* proxmox\_kvm \- <code>absent</code> state with <code>force</code> specified failed to stop the VM due to the <code>timeout</code> value not being passed to <code>stop\_vm</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6827](https\://github\.com/ansible\-collections/community\.general/pull/6827)\)\.
* proxmox\_kvm \- <code>restarted</code> state did not actually restart a VM in some VM configurations\. The state now uses the Proxmox reboot endpoint instead of calling the <code>stop\_vm</code> and <code>start\_vm</code> functions \([https\://github\.com/ansible\-collections/community\.general/pull/6773](https\://github\.com/ansible\-collections/community\.general/pull/6773)\)\.
* proxmox\_kvm \- allow creation of VM with existing name but new vmid \([https\://github\.com/ansible\-collections/community\.general/issues/6155](https\://github\.com/ansible\-collections/community\.general/issues/6155)\, [https\://github\.com/ansible\-collections/community\.general/pull/6709](https\://github\.com/ansible\-collections/community\.general/pull/6709)\)\.
* proxmox\_kvm \- when <code>name</code> option is provided without <code>vmid</code> and VM with that name already exists then no new VM will be created \([https\://github\.com/ansible\-collections/community\.general/issues/6911](https\://github\.com/ansible\-collections/community\.general/issues/6911)\, [https\://github\.com/ansible\-collections/community\.general/pull/6981](https\://github\.com/ansible\-collections/community\.general/pull/6981)\)\.
* proxmox\_tasks\_info \- remove <code>api\_user</code> \+ <code>api\_password</code> constraint from <code>required\_together</code> as it causes to require <code>api\_password</code> even when API token param is used \([https\://github\.com/ansible\-collections/community\.general/issues/6201](https\://github\.com/ansible\-collections/community\.general/issues/6201)\)\.
* proxmox\_template \- require <code>requests\_toolbelt</code> module to fix issue with uploading large templates \([https\://github\.com/ansible\-collections/community\.general/issues/5579](https\://github\.com/ansible\-collections/community\.general/issues/5579)\, [https\://github\.com/ansible\-collections/community\.general/pull/6757](https\://github\.com/ansible\-collections/community\.general/pull/6757)\)\.
* proxmox\_user\_info \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* redfish\_info \- fix <code>ListUsers</code> to not show empty account slots \([https\://github\.com/ansible\-collections/community\.general/issues/6771](https\://github\.com/ansible\-collections/community\.general/issues/6771)\, [https\://github\.com/ansible\-collections/community\.general/pull/6772](https\://github\.com/ansible\-collections/community\.general/pull/6772)\)\.
* redhat\_subscription \- use the right D\-Bus options for the consumer type when
  registering a RHEL system older than 9 or a RHEL 9 system older than 9\.2
  and using <code>consumer\_type</code>
  \([https\://github\.com/ansible\-collections/community\.general/pull/7378](https\://github\.com/ansible\-collections/community\.general/pull/7378)\)\.
* refish\_utils module utils \- changing variable names to avoid issues occuring when fetching Volumes data \([https\://github\.com/ansible\-collections/community\.general/pull/6883](https\://github\.com/ansible\-collections/community\.general/pull/6883)\)\.
* rhsm\_repository \- when using the <code>purge</code> option\, the <code>repositories</code>
  dictionary element in the returned JSON is now properly updated according
  to the pruning operation
  \([https\://github\.com/ansible\-collections/community\.general/pull/6676](https\://github\.com/ansible\-collections/community\.general/pull/6676)\)\.
* rundeck \- fix <code>TypeError</code> on 404 API response \([https\://github\.com/ansible\-collections/community\.general/pull/6983](https\://github\.com/ansible\-collections/community\.general/pull/6983)\)\.
* selective callback plugin \- fix length of task name lines in output always being 3 characters longer than desired \([https\://github\.com/ansible\-collections/community\.general/pull/7374](https\://github\.com/ansible\-collections/community\.general/pull/7374)\)\.
* snap \- an exception was being raised when snap list was empty \([https\://github\.com/ansible\-collections/community\.general/pull/7124](https\://github\.com/ansible\-collections/community\.general/pull/7124)\, [https\://github\.com/ansible\-collections/community\.general/issues/7120](https\://github\.com/ansible\-collections/community\.general/issues/7120)\)\.
* snap \- assume default track <code>latest</code> in parameter <code>channel</code> when not specified \([https\://github\.com/ansible\-collections/community\.general/pull/6835](https\://github\.com/ansible\-collections/community\.general/pull/6835)\, [https\://github\.com/ansible\-collections/community\.general/issues/6821](https\://github\.com/ansible\-collections/community\.general/issues/6821)\)\.
* snap \- change the change detection mechanism from \"parsing installation\" to \"comparing end state with initial state\" \([https\://github\.com/ansible\-collections/community\.general/pull/7340](https\://github\.com/ansible\-collections/community\.general/pull/7340)\, [https\://github\.com/ansible\-collections/community\.general/issues/7265](https\://github\.com/ansible\-collections/community\.general/issues/7265)\)\.
* snap \- fix crash when multiple snaps are specified and one has <code>\-\-\-</code> in its description \([https\://github\.com/ansible\-collections/community\.general/pull/7046](https\://github\.com/ansible\-collections/community\.general/pull/7046)\)\.
* snap \- fix the processing of the commands\' output\, stripping spaces and newlines from it \([https\://github\.com/ansible\-collections/community\.general/pull/6826](https\://github\.com/ansible\-collections/community\.general/pull/6826)\, [https\://github\.com/ansible\-collections/community\.general/issues/6803](https\://github\.com/ansible\-collections/community\.general/issues/6803)\)\.
* sorcery \- fix interruption of the multi\-stage process \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* sorcery \- fix queue generation before the whole system rebuild \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* sorcery \- latest state no longer triggers update\_cache \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* terraform \- prevents <code>\-backend\-config</code> option double encapsulating with <code>shlex\_quote</code> function\. \([https\://github\.com/ansible\-collections/community\.general/pull/7301](https\://github\.com/ansible\-collections/community\.general/pull/7301)\)\.
* tss lookup plugin \- fix multiple issues when using <code>fetch\_attachments\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6720](https\://github\.com/ansible\-collections/community\.general/pull/6720)\)\.
* zypper \- added handling of zypper exitcode 102\. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook \([https\://github\.com/ansible\-collections/community\.general/pull/6534](https\://github\.com/ansible\-collections/community\.general/pull/6534)\)\.

<a id="known-issues"></a>
### Known Issues

* Ansible markup will show up in raw form on ansible\-doc text output for ansible\-core before 2\.15\. If you have trouble deciphering the documentation markup\, please upgrade to ansible\-core 2\.15 \(or newer\)\, or read the HTML documentation on [https\://docs\.ansible\.com/ansible/devel/collections/community/general/](https\://docs\.ansible\.com/ansible/devel/collections/community/general/) \([https\://github\.com/ansible\-collections/community\.general/pull/6539](https\://github\.com/ansible\-collections/community\.general/pull/6539)\)\.

<a id="new-plugins-3"></a>
### New Plugins

<a id="lookup-2"></a>
#### Lookup

* bitwarden\_secrets\_manager \- Retrieve secrets from Bitwarden Secrets Manager

<a id="new-modules-6"></a>
### New Modules

* consul\_policy \- Manipulate Consul policies
* consul\_role \- Manipulate Consul roles
* facter\_facts \- Runs the discovery program C\(facter\) on the remote system and return Ansible facts
* gio\_mime \- Set default handler for MIME type\, for applications using Gnome GIO
* gitlab\_instance\_variable \- Creates\, updates\, or deletes GitLab instance variables
* gitlab\_merge\_request \- Create\, update\, or delete GitLab merge requests
* jenkins\_build\_info \- Get information about Jenkins builds
* keycloak\_authentication\_required\_actions \- Allows administration of Keycloak authentication required actions
* keycloak\_authz\_custom\_policy \- Allows administration of Keycloak client custom Javascript policies via Keycloak API
* keycloak\_authz\_permission \- Allows administration of Keycloak client authorization permissions via Keycloak API
* keycloak\_authz\_permission\_info \- Query Keycloak client authorization permissions information
* keycloak\_realm\_key \- Allows administration of Keycloak realm keys via Keycloak API
* keycloak\_user \- Create and configure a user in Keycloak
* lvg\_rename \- Renames LVM volume groups
* pnpm \- Manage node\.js packages with pnpm
* proxmox\_pool \- Pool management for Proxmox VE cluster
* proxmox\_pool\_member \- Add or delete members from Proxmox VE cluster pools
* proxmox\_vm\_info \- Retrieve information about one or more Proxmox VE virtual machines
* simpleinit\_msb \- Manage services on Source Mage GNU/Linux
