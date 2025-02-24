# Community General Release Notes

**Topics**

- <a href="#v9-5-5">v9\.5\.5</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v9-5-4">v9\.5\.4</a>
    - <a href="#security-fixes">Security Fixes</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v9-5-3">v9\.5\.3</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#security-fixes-1">Security Fixes</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v9-5-2">v9\.5\.2</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v9-5-1">v9\.5\.1</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v9-5-0">v9\.5\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes-5">Bugfixes</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v9-4-0">v9\.4\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-6">Bugfixes</a>
    - <a href="#new-modules-1">New Modules</a>
- <a href="#v9-3-0">v9\.3\.0</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#bugfixes-7">Bugfixes</a>
    - <a href="#new-modules-2">New Modules</a>
- <a href="#v9-2-0">v9\.2\.0</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#bugfixes-8">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#filter">Filter</a>
        - <a href="#test">Test</a>
- <a href="#v9-1-0">v9\.1\.0</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
    - <a href="#deprecated-features-2">Deprecated Features</a>
    - <a href="#bugfixes-9">Bugfixes</a>
    - <a href="#known-issues">Known Issues</a>
    - <a href="#new-plugins-1">New Plugins</a>
        - <a href="#filter-1">Filter</a>
    - <a href="#new-modules-3">New Modules</a>
- <a href="#v9-0-1">v9\.0\.1</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#bugfixes-10">Bugfixes</a>
- <a href="#v9-0-0">v9\.0\.0</a>
    - <a href="#release-summary-10">Release Summary</a>
    - <a href="#minor-changes-9">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features-3">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#security-fixes-2">Security Fixes</a>
    - <a href="#bugfixes-11">Bugfixes</a>
    - <a href="#new-plugins-2">New Plugins</a>
        - <a href="#become">Become</a>
        - <a href="#callback">Callback</a>
        - <a href="#connection">Connection</a>
        - <a href="#filter-2">Filter</a>
        - <a href="#lookup">Lookup</a>
        - <a href="#test-1">Test</a>
    - <a href="#new-modules-4">New Modules</a>
This changelog describes changes after version 8\.0\.0\.

<a id="v9-5-5"></a>
## v9\.5\.5

<a id="release-summary"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes"></a>
### Bugfixes

* apache2\_mod\_proxy \- make compatible with Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* apache2\_mod\_proxy \- passing the cluster\'s page as referer for the member\'s pages\. This makes the module actually work again for halfway modern Apache versions\. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* cloudflare\_dns \- fix crash when deleting a DNS record or when updating a record with <code>solo\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9652](https\://github\.com/ansible\-collections/community\.general/issues/9652)\, [https\://github\.com/ansible\-collections/community\.general/pull/9649](https\://github\.com/ansible\-collections/community\.general/pull/9649)\)\.
* elasticsearch\_plugin \- fix <code>ERROR\: D is not a recognized option</code> issue when configuring proxy settings \([https\://github\.com/ansible\-collections/community\.general/pull/9774](https\://github\.com/ansible\-collections/community\.general/pull/9774)\, [https\://github\.com/ansible\-collections/community\.general/issues/9773](https\://github\.com/ansible\-collections/community\.general/issues/9773)\)\.
* keycloak\_client \- fix and improve existing tests\. The module showed a diff without actual changes\, solved by improving the <code>normalise\_cr\(\)</code> function \([https\://github\.com/ansible\-collections/community\.general/pull/9644](https\://github\.com/ansible\-collections/community\.general/pull/9644)\)\.
* keycloak\_client \- in check mode\, detect whether the lists in before client \(for example redirect URI list\) contain items that the lists in the desired client do not contain \([https\://github\.com/ansible\-collections/community\.general/pull/9739](https\://github\.com/ansible\-collections/community\.general/pull/9739)\)\.
* passwordstore lookup plugin \- fix subkey creation even when <code>create\=false</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9105](https\://github\.com/ansible\-collections/community\.general/issues/9105)\, [https\://github\.com/ansible\-collections/community\.general/pull/9106](https\://github\.com/ansible\-collections/community\.general/pull/9106)\)\.
* proxmox inventory plugin \- plugin did not update cache correctly after <code>meta\: refresh\_inventory</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9710](https\://github\.com/ansible\-collections/community\.general/issues/9710)\, [https\://github\.com/ansible\-collections/community\.general/pull/9760](https\://github\.com/ansible\-collections/community\.general/pull/9760)\)\.
* redhat\_subscription \- use the \"enable\_content\" option \(when available\) when
  registering using D\-Bus\, to ensure that subscription\-manager enables the
  content on registration\; this is particular important on EL 10\+ and Fedora
  41\+
  \([https\://github\.com/ansible\-collections/community\.general/pull/9778](https\://github\.com/ansible\-collections/community\.general/pull/9778)\)\.
* xml \- ensure file descriptor is closed \([https\://github\.com/ansible\-collections/community\.general/pull/9695](https\://github\.com/ansible\-collections/community\.general/pull/9695)\)\.

<a id="v9-5-4"></a>
## v9\.5\.4

<a id="security-fixes"></a>
### Security Fixes

* keycloak\_client \- Sanitize <code>saml\.encryption\.private\.key</code> so it does not show in the logs \([https\://github\.com/ansible\-collections/community\.general/pull/9621](https\://github\.com/ansible\-collections/community\.general/pull/9621)\)\.

<a id="bugfixes-1"></a>
### Bugfixes

* redhat\_subscription \- do not try to unsubscribe \(i\.e\. remove subscriptions\)
  when unregistering a system\: newer versions of subscription\-manager\, as
  available in EL 10 and Fedora 41\+\, do not support entitlements anymore\, and
  thus unsubscribing will fail
  \([https\://github\.com/ansible\-collections/community\.general/pull/9578](https\://github\.com/ansible\-collections/community\.general/pull/9578)\)\.

<a id="v9-5-3"></a>
## v9\.5\.3

<a id="release-summary-1"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes"></a>
### Minor Changes

* proxmox module utils \- add method <code>api\_task\_complete</code> that can wait for task completion and return error message \([https\://github\.com/ansible\-collections/community\.general/pull/9256](https\://github\.com/ansible\-collections/community\.general/pull/9256)\)\.

<a id="security-fixes-1"></a>
### Security Fixes

* keycloak\_authentication \- API calls did not properly set the <code>priority</code> during update resulting in incorrectly sorted authentication flows\. This apparently only affects Keycloak 25 or newer \([https\://github\.com/ansible\-collections/community\.general/pull/9263](https\://github\.com/ansible\-collections/community\.general/pull/9263)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* dig lookup plugin \- correctly handle <code>NoNameserver</code> exception \([https\://github\.com/ansible\-collections/community\.general/pull/9363](https\://github\.com/ansible\-collections/community\.general/pull/9363)\, [https\://github\.com/ansible\-collections/community\.general/issues/9362](https\://github\.com/ansible\-collections/community\.general/issues/9362)\)\.
* htpasswd \- report changes when file permissions are adjusted \([https\://github\.com/ansible\-collections/community\.general/issues/9485](https\://github\.com/ansible\-collections/community\.general/issues/9485)\, [https\://github\.com/ansible\-collections/community\.general/pull/9490](https\://github\.com/ansible\-collections/community\.general/pull/9490)\)\.
* proxmox\_disk \- fix async method and make <code>resize\_disk</code> method handle errors correctly \([https\://github\.com/ansible\-collections/community\.general/pull/9256](https\://github\.com/ansible\-collections/community\.general/pull/9256)\)\.
* proxmox\_template \- fix the wrong path called on <code>proxmox\_template\.task\_status</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9276](https\://github\.com/ansible\-collections/community\.general/issues/9276)\, [https\://github\.com/ansible\-collections/community\.general/pull/9277](https\://github\.com/ansible\-collections/community\.general/pull/9277)\)\.
* qubes connection plugin \- fix the printing of debug information \([https\://github\.com/ansible\-collections/community\.general/pull/9334](https\://github\.com/ansible\-collections/community\.general/pull/9334)\)\.
* redfish\_utils module utils \- Fix <code>VerifyBiosAttributes</code> command on multi system resource nodes \([https\://github\.com/ansible\-collections/community\.general/pull/9234](https\://github\.com/ansible\-collections/community\.general/pull/9234)\)\.

<a id="v9-5-2"></a>
## v9\.5\.2

<a id="release-summary-2"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes-1"></a>
### Minor Changes

* proxmox inventory plugin \- fix urllib3 <code>InsecureRequestWarnings</code> not being suppressed when a token is used \([https\://github\.com/ansible\-collections/community\.general/pull/9099](https\://github\.com/ansible\-collections/community\.general/pull/9099)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* dnf\_config\_manager \- fix hanging when prompting to import GPG keys \([https\://github\.com/ansible\-collections/community\.general/pull/9124](https\://github\.com/ansible\-collections/community\.general/pull/9124)\, [https\://github\.com/ansible\-collections/community\.general/issues/8830](https\://github\.com/ansible\-collections/community\.general/issues/8830)\)\.
* dnf\_config\_manager \- forces locale to <code>C</code> before module starts\. If the locale was set to non\-English\, the output of the <code>dnf config\-manager</code> could not be parsed \([https\://github\.com/ansible\-collections/community\.general/pull/9157](https\://github\.com/ansible\-collections/community\.general/pull/9157)\, [https\://github\.com/ansible\-collections/community\.general/issues/9046](https\://github\.com/ansible\-collections/community\.general/issues/9046)\)\.
* flatpak \- force the locale language to <code>C</code> when running the flatpak command \([https\://github\.com/ansible\-collections/community\.general/pull/9187](https\://github\.com/ansible\-collections/community\.general/pull/9187)\, [https\://github\.com/ansible\-collections/community\.general/issues/8883](https\://github\.com/ansible\-collections/community\.general/issues/8883)\)\.
* github\_key \- in check mode\, a faulty call to <code>\`datetime\.strftime\(\.\.\.\)\`</code> was being made which generated an exception \([https\://github\.com/ansible\-collections/community\.general/issues/9185](https\://github\.com/ansible\-collections/community\.general/issues/9185)\)\.
* homebrew\_cask \- allow <code>\+</code> symbol in Homebrew cask name validation regex \([https\://github\.com/ansible\-collections/community\.general/pull/9128](https\://github\.com/ansible\-collections/community\.general/pull/9128)\)\.
* keycloak\_client \- fix diff by removing code that turns the attributes dict which contains additional settings into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9077](https\://github\.com/ansible\-collections/community\.general/pull/9077)\)\.
* keycloak\_clientscope \- fix diff and <code>end\_state</code> by removing the code that turns the attributes dict\, which contains additional config items\, into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9082](https\://github\.com/ansible\-collections/community\.general/pull/9082)\)\.
* keycloak\_clientscope\_type \- sort the default and optional clientscope lists to improve the diff \([https\://github\.com/ansible\-collections/community\.general/pull/9202](https\://github\.com/ansible\-collections/community\.general/pull/9202)\)\.
* redfish\_utils module utils \- remove undocumented default applytime \([https\://github\.com/ansible\-collections/community\.general/pull/9114](https\://github\.com/ansible\-collections/community\.general/pull/9114)\)\.
* slack \- fail if Slack API response is not OK with error message \([https\://github\.com/ansible\-collections/community\.general/pull/9198](https\://github\.com/ansible\-collections/community\.general/pull/9198)\)\.

<a id="v9-5-1"></a>
## v9\.5\.1

<a id="release-summary-3"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes-2"></a>
### Minor Changes

* redfish\_utils module utils \- schedule a BIOS configuration job at next reboot when the BIOS config is changed \([https\://github\.com/ansible\-collections/community\.general/pull/9012](https\://github\.com/ansible\-collections/community\.general/pull/9012)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* bitwarden lookup plugin \- support BWS v0\.3\.0 syntax breaking change \([https\://github\.com/ansible\-collections/community\.general/pull/9028](https\://github\.com/ansible\-collections/community\.general/pull/9028)\)\.
* collection\_version lookup plugin \- use <code>importlib</code> directly instead of the deprecated and in ansible\-core 2\.19 removed <code>ansible\.module\_utils\.compat\.importlib</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9084](https\://github\.com/ansible\-collections/community\.general/pull/9084)\)\.
* gitlab\_label \- update label\'s color \([https\://github\.com/ansible\-collections/community\.general/pull/9010](https\://github\.com/ansible\-collections/community\.general/pull/9010)\)\.
* keycloak\_clientscope\_type \- fix detect changes in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/9092](https\://github\.com/ansible\-collections/community\.general/issues/9092)\, [https\://github\.com/ansible\-collections/community\.general/pull/9093](https\://github\.com/ansible\-collections/community\.general/pull/9093)\)\.
* keycloak\_group \- fix crash caused in subgroup creation\. The crash was caused by a missing or empty <code>subGroups</code> property in Keycloak ≥23 \([https\://github\.com/ansible\-collections/community\.general/issues/8788](https\://github\.com/ansible\-collections/community\.general/issues/8788)\, [https\://github\.com/ansible\-collections/community\.general/pull/8979](https\://github\.com/ansible\-collections/community\.general/pull/8979)\)\.
* modprobe \- fix check mode not being honored for <code>persistent</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/9051](https\://github\.com/ansible\-collections/community\.general/issues/9051)\, [https\://github\.com/ansible\-collections/community\.general/pull/9052](https\://github\.com/ansible\-collections/community\.general/pull/9052)\)\.
* one\_host \- fix if statements for cases when <code>ID\=0</code> \([https\://github\.com/ansible\-collections/community\.general/issues/1199](https\://github\.com/ansible\-collections/community\.general/issues/1199)\, [https\://github\.com/ansible\-collections/community\.general/pull/8907](https\://github\.com/ansible\-collections/community\.general/pull/8907)\)\.
* one\_image \- fix module failing due to a class method typo \([https\://github\.com/ansible\-collections/community\.general/pull/9056](https\://github\.com/ansible\-collections/community\.general/pull/9056)\)\.
* one\_image\_info \- fix module failing due to a class method typo \([https\://github\.com/ansible\-collections/community\.general/pull/9056](https\://github\.com/ansible\-collections/community\.general/pull/9056)\)\.
* one\_vnet \- fix module failing due to a variable typo \([https\://github\.com/ansible\-collections/community\.general/pull/9019](https\://github\.com/ansible\-collections/community\.general/pull/9019)\)\.
* redfish\_utils module utils \- fix issue with URI parsing to gracefully handling trailing slashes when extracting member identifiers \([https\://github\.com/ansible\-collections/community\.general/issues/9047](https\://github\.com/ansible\-collections/community\.general/issues/9047)\, [https\://github\.com/ansible\-collections/community\.general/pull/9057](https\://github\.com/ansible\-collections/community\.general/pull/9057)\)\.

<a id="v9-5-0"></a>
## v9\.5\.0

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix and feature release\.

Please note that this is the last feature release for community\.general 9\.x\.y\.
From now on\, new features will only go into community\.general 10\.x\.y\.

<a id="minor-changes-3"></a>
### Minor Changes

* dig lookup plugin \- add <code>port</code> option to specify DNS server port \([https\://github\.com/ansible\-collections/community\.general/pull/8966](https\://github\.com/ansible\-collections/community\.general/pull/8966)\)\.
* flatpak \- improve the parsing of Flatpak application IDs based on official guidelines \([https\://github\.com/ansible\-collections/community\.general/pull/8909](https\://github\.com/ansible\-collections/community\.general/pull/8909)\)\.
* gio\_mime \- adjust code ahead of the old <code>VardDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8855](https\://github\.com/ansible\-collections/community\.general/pull/8855)\)\.
* gitlab\_deploy\_key \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_group \- add many new parameters \([https\://github\.com/ansible\-collections/community\.general/pull/8908](https\://github\.com/ansible\-collections/community\.general/pull/8908)\)\.
* gitlab\_group \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_issue \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_merge\_request \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_runner \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* icinga2\_host \- replace loop with dict comprehension \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* jira \- adjust code ahead of the old <code>VardDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8856](https\://github\.com/ansible\-collections/community\.general/pull/8856)\)\.
* keycloak\_client \- add <code>client\-x509</code> choice to <code>client\_authenticator\_type</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8973](https\://github\.com/ansible\-collections/community\.general/pull/8973)\)\.
* keycloak\_user\_federation \- add the user federation config parameter <code>referral</code> to the module arguments \([https\://github\.com/ansible\-collections/community\.general/pull/8954](https\://github\.com/ansible\-collections/community\.general/pull/8954)\)\.
* memset\_dns\_reload \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* memset\_memstore\_info \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* memset\_server\_info \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* memset\_zone \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* memset\_zone\_domain \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* memset\_zone\_record \- replace loop with <code>dict\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* nmcli \- add <code>conn\_enable</code> param to reload connection \([https\://github\.com/ansible\-collections/community\.general/issues/3752](https\://github\.com/ansible\-collections/community\.general/issues/3752)\, [https\://github\.com/ansible\-collections/community\.general/issues/8704](https\://github\.com/ansible\-collections/community\.general/issues/8704)\, [https\://github\.com/ansible\-collections/community\.general/pull/8897](https\://github\.com/ansible\-collections/community\.general/pull/8897)\)\.
* nmcli \- add <code>state\=up</code> and <code>state\=down</code> to enable/disable connections \([https\://github\.com/ansible\-collections/community\.general/issues/3752](https\://github\.com/ansible\-collections/community\.general/issues/3752)\, [https\://github\.com/ansible\-collections/community\.general/issues/8704](https\://github\.com/ansible\-collections/community\.general/issues/8704)\, [https\://github\.com/ansible\-collections/community\.general/issues/7152](https\://github\.com/ansible\-collections/community\.general/issues/7152)\, [https\://github\.com/ansible\-collections/community\.general/pull/8897](https\://github\.com/ansible\-collections/community\.general/pull/8897)\)\.
* nmcli \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* npm \- add <code>force</code> parameter to allow <code>\-\-force</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8885](https\://github\.com/ansible\-collections/community\.general/pull/8885)\)\.
* one\_image \- add option <code>persistent</code> to manage image persistence \([https\://github\.com/ansible\-collections/community\.general/issues/3578](https\://github\.com/ansible\-collections/community\.general/issues/3578)\, [https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image \- extend xsd scheme to make it return a lot more info about image \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image \- refactor code to make it more similar to <code>one\_template</code> and <code>one\_vnet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image\_info \- extend xsd scheme to make it return a lot more info about image \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image\_info \- refactor code to make it more similar to <code>one\_template</code> and <code>one\_vnet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* open\_iscsi \- allow login to a portal with multiple targets without specifying any of them \([https\://github\.com/ansible\-collections/community\.general/pull/8719](https\://github\.com/ansible\-collections/community\.general/pull/8719)\)\.
* opennebula\.py \- add VM <code>id</code> and VM <code>host</code> to inventory host data \([https\://github\.com/ansible\-collections/community\.general/pull/8532](https\://github\.com/ansible\-collections/community\.general/pull/8532)\)\.
* passwordstore lookup plugin \- add subkey creation/update support \([https\://github\.com/ansible\-collections/community\.general/pull/8952](https\://github\.com/ansible\-collections/community\.general/pull/8952)\)\.
* proxmox inventory plugin \- clean up authentication code \([https\://github\.com/ansible\-collections/community\.general/pull/8917](https\://github\.com/ansible\-collections/community\.general/pull/8917)\)\.
* redfish\_command \- add handling of the <code>PasswordChangeRequired</code> message from services in the <code>UpdateUserPassword</code> command to directly modify the user\'s password if the requested user is the one invoking the operation \([https\://github\.com/ansible\-collections/community\.general/issues/8652](https\://github\.com/ansible\-collections/community\.general/issues/8652)\, [https\://github\.com/ansible\-collections/community\.general/pull/8653](https\://github\.com/ansible\-collections/community\.general/pull/8653)\)\.
* redfish\_confg \- remove <code>CapacityBytes</code> from required paramaters of the <code>CreateVolume</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/8956](https\://github\.com/ansible\-collections/community\.general/pull/8956)\)\.
* redfish\_config \- add parameter <code>storage\_none\_volume\_deletion</code> to <code>CreateVolume</code> command in order to control the automatic deletion of non\-RAID volumes \([https\://github\.com/ansible\-collections/community\.general/pull/8990](https\://github\.com/ansible\-collections/community\.general/pull/8990)\)\.
* redfish\_info \- adds <code>RedfishURI</code> and <code>StorageId</code> to Disk inventory \([https\://github\.com/ansible\-collections/community\.general/pull/8937](https\://github\.com/ansible\-collections/community\.general/pull/8937)\)\.
* scaleway\_container \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_container\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_container\_namespace \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_container\_namespace\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_container\_registry \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_container\_registry\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_function \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_function\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_function\_namespace \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_function\_namespace\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8858](https\://github\.com/ansible\-collections/community\.general/pull/8858)\)\.
* scaleway\_user\_data \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* udm\_dns\_record \- replace loop with <code>dict\.update\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* hipchat \- the hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020\. The module is therefore deprecated and will be removed from community\.general 11\.0\.0 if nobody provides compelling reasons to still keep it \([https\://github\.com/ansible\-collections/community\.general/pull/8919](https\://github\.com/ansible\-collections/community\.general/pull/8919)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* cloudflare\_dns \- fix changing Cloudflare SRV records \([https\://github\.com/ansible\-collections/community\.general/issues/8679](https\://github\.com/ansible\-collections/community\.general/issues/8679)\, [https\://github\.com/ansible\-collections/community\.general/pull/8948](https\://github\.com/ansible\-collections/community\.general/pull/8948)\)\.
* cmd\_runner module utils \- call to <code>get\_best\_parsable\_locales\(\)</code> was missing parameter \([https\://github\.com/ansible\-collections/community\.general/pull/8929](https\://github\.com/ansible\-collections/community\.general/pull/8929)\)\.
* dig lookup plugin \- fix using only the last nameserver specified \([https\://github\.com/ansible\-collections/community\.general/pull/8970](https\://github\.com/ansible\-collections/community\.general/pull/8970)\)\.
* django\_command \- option <code>command</code> is now split lexically before passed to underlying PythonRunner \([https\://github\.com/ansible\-collections/community\.general/pull/8944](https\://github\.com/ansible\-collections/community\.general/pull/8944)\)\.
* homectl \- the module now tries to use <code>legacycrypt</code> on Python 3\.13\+ \([https\://github\.com/ansible\-collections/community\.general/issues/4691](https\://github\.com/ansible\-collections/community\.general/issues/4691)\, [https\://github\.com/ansible\-collections/community\.general/pull/8987](https\://github\.com/ansible\-collections/community\.general/pull/8987)\)\.
* ini\_file \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* ipa\_host \- add <code>force\_create</code>\, fix <code>enabled</code> and <code>disabled</code> states \([https\://github\.com/ansible\-collections/community\.general/issues/1094](https\://github\.com/ansible\-collections/community\.general/issues/1094)\, [https\://github\.com/ansible\-collections/community\.general/pull/8920](https\://github\.com/ansible\-collections/community\.general/pull/8920)\)\.
* ipa\_hostgroup \- fix <code>enabled \`\` and \`\`disabled</code> states \([https\://github\.com/ansible\-collections/community\.general/issues/8408](https\://github\.com/ansible\-collections/community\.general/issues/8408)\, [https\://github\.com/ansible\-collections/community\.general/pull/8900](https\://github\.com/ansible\-collections/community\.general/pull/8900)\)\.
* java\_keystore \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* jenkins\_plugin \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* kdeconfig \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* keycloak\_realm \- fix change detection in check mode by sorting the lists in the realms beforehand \([https\://github\.com/ansible\-collections/community\.general/pull/8877](https\://github\.com/ansible\-collections/community\.general/pull/8877)\)\.
* keycloak\_user\_federation \- add module argument allowing users to configure the update mode for the parameter <code>bindCredential</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8898](https\://github\.com/ansible\-collections/community\.general/pull/8898)\)\.
* keycloak\_user\_federation \- minimize change detection by setting <code>krbPrincipalAttribute</code> to <code>\'\'</code> in Keycloak responses if missing \([https\://github\.com/ansible\-collections/community\.general/pull/8785](https\://github\.com/ansible\-collections/community\.general/pull/8785)\)\.
* keycloak\_user\_federation \- remove <code>lastSync</code> parameter from Keycloak responses to minimize diff/changes \([https\://github\.com/ansible\-collections/community\.general/pull/8812](https\://github\.com/ansible\-collections/community\.general/pull/8812)\)\.
* keycloak\_userprofile \- fix empty response when fetching userprofile component by removing <code>parent\=parent\_id</code> filter \([https\://github\.com/ansible\-collections/community\.general/pull/8923](https\://github\.com/ansible\-collections/community\.general/pull/8923)\)\.
* keycloak\_userprofile \- improve diff by deserializing the fetched <code>kc\.user\.profile\.config</code> and serialize it only when sending back \([https\://github\.com/ansible\-collections/community\.general/pull/8940](https\://github\.com/ansible\-collections/community\.general/pull/8940)\)\.
* lxd\_container \- fix bug introduced in previous commit \([https\://github\.com/ansible\-collections/community\.general/pull/8895](https\://github\.com/ansible\-collections/community\.general/pull/8895)\, [https\://github\.com/ansible\-collections/community\.general/issues/8888](https\://github\.com/ansible\-collections/community\.general/issues/8888)\)\.
* one\_service \- fix service creation after it was deleted with <code>unique</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/3137](https\://github\.com/ansible\-collections/community\.general/issues/3137)\, [https\://github\.com/ansible\-collections/community\.general/pull/8887](https\://github\.com/ansible\-collections/community\.general/pull/8887)\)\.
* pam\_limits \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* python\_runner module utils \- parameter <code>path\_prefix</code> was being handled as string when it should be a list \([https\://github\.com/ansible\-collections/community\.general/pull/8944](https\://github\.com/ansible\-collections/community\.general/pull/8944)\)\.
* udm\_user \- the module now tries to use <code>legacycrypt</code> on Python 3\.13\+ \([https\://github\.com/ansible\-collections/community\.general/issues/4690](https\://github\.com/ansible\-collections/community\.general/issues/4690)\, [https\://github\.com/ansible\-collections/community\.general/pull/8987](https\://github\.com/ansible\-collections/community\.general/pull/8987)\)\.

<a id="new-modules"></a>
### New Modules

* community\.general\.ipa\_getkeytab \- Manage keytab file in FreeIPA\.

<a id="v9-4-0"></a>
## v9\.4\.0

<a id="release-summary-5"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* MH module utils \- add parameter <code>when</code> to <code>cause\_changes</code> decorator \([https\://github\.com/ansible\-collections/community\.general/pull/8766](https\://github\.com/ansible\-collections/community\.general/pull/8766)\)\.
* MH module utils \- minor refactor in decorators \([https\://github\.com/ansible\-collections/community\.general/pull/8766](https\://github\.com/ansible\-collections/community\.general/pull/8766)\)\.
* alternatives \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* apache2\_mod\_proxy \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* apache2\_mod\_proxy \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* consul\_acl \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* copr \- Added <code>includepkgs</code> and <code>excludepkgs</code> parameters to limit the list of packages fetched or excluded from the repository\([https\://github\.com/ansible\-collections/community\.general/pull/8779](https\://github\.com/ansible\-collections/community\.general/pull/8779)\)\.
* credstash lookup plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* csv module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* deco MH module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* etcd3 \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* gio\_mime \- mute the  old <code>VarDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8776](https\://github\.com/ansible\-collections/community\.general/pull/8776)\)\.
* gitlab\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* gitlab\_project \- add option <code>issues\_access\_level</code> to enable/disable project issues \([https\://github\.com/ansible\-collections/community\.general/pull/8760](https\://github\.com/ansible\-collections/community\.general/pull/8760)\)\.
* gitlab\_project \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* gitlab\_project \- sorted parameters in order to avoid future merge conflicts \([https\://github\.com/ansible\-collections/community\.general/pull/8759](https\://github\.com/ansible\-collections/community\.general/pull/8759)\)\.
* hashids filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* hwc\_ecs\_instance \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_evs\_disk \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_eip \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_peering\_connect \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_port \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_subnet \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* imc\_rest \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* ipa\_otptoken \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* jira \- mute the  old <code>VarDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8776](https\://github\.com/ansible\-collections/community\.general/pull/8776)\)\.
* jira \- replace deprecated params when using decorator <code>cause\_changes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8791](https\://github\.com/ansible\-collections/community\.general/pull/8791)\)\.
* keep\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* keycloak\_client \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_clientscope \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_identity\_provider \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_user\_federation \- add module argument allowing users to optout of the removal of unspecified mappers\, for example to keep the keycloak default mappers \([https\://github\.com/ansible\-collections/community\.general/pull/8764](https\://github\.com/ansible\-collections/community\.general/pull/8764)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* linode \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* lxc\_container \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* lxd\_container \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* manageiq\_provider \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* ocapi\_utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* one\_service \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* one\_vm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* onepassword lookup plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pids \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pipx \- added new states <code>install\_all</code>\, <code>uninject</code>\, <code>upgrade\_shared</code>\, <code>pin</code>\, and <code>unpin</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8809](https\://github\.com/ansible\-collections/community\.general/pull/8809)\)\.
* pipx \- added parameter <code>global</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pipx\_info \- added parameter <code>global</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pkg5\_publisher \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* proxmox \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox\_disk \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox\_kvm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox\_kvm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* redfish\_utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* redfish\_utils module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* redis cache plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* remove\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* replace\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* scaleway \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* scaleway\_compute \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_ip \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_lb \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_security\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* scaleway\_security\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_user\_data \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* sensu\_silence \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* snmp\_facts \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* sorcery \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* ufw \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* unsafe plugin utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* vardict module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* vars MH module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* vmadm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* MH decorator cause\_changes module utils \- deprecate parameters <code>on\_success</code> and <code>on\_failure</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8791](https\://github\.com/ansible\-collections/community\.general/pull/8791)\)\.
* pipx \- support for versions of the command line tool <code>pipx</code> older than <code>1\.7\.0</code> is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx\_info \- support for versions of the command line tool <code>pipx</code> older than <code>1\.7\.0</code> is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.

<a id="bugfixes-6"></a>
### Bugfixes

* gitlab\_group\_access\_token \- fix crash in check mode caused by attempted access to a newly created access token \([https\://github\.com/ansible\-collections/community\.general/pull/8796](https\://github\.com/ansible\-collections/community\.general/pull/8796)\)\.
* gitlab\_project \- fix <code>container\_expiration\_policy</code> not being applied when creating a new project \([https\://github\.com/ansible\-collections/community\.general/pull/8790](https\://github\.com/ansible\-collections/community\.general/pull/8790)\)\.
* gitlab\_project \- fix crash caused by old Gitlab projects not having a <code>container\_expiration\_policy</code> attribute \([https\://github\.com/ansible\-collections/community\.general/pull/8790](https\://github\.com/ansible\-collections/community\.general/pull/8790)\)\.
* gitlab\_project\_access\_token \- fix crash in check mode caused by attempted access to a newly created access token \([https\://github\.com/ansible\-collections/community\.general/pull/8796](https\://github\.com/ansible\-collections/community\.general/pull/8796)\)\.
* keycloak\_realm\_key \- fix invalid usage of <code>parent\_id</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7850](https\://github\.com/ansible\-collections/community\.general/issues/7850)\, [https\://github\.com/ansible\-collections/community\.general/pull/8823](https\://github\.com/ansible\-collections/community\.general/pull/8823)\)\.
* keycloak\_user\_federation \- fix key error when removing mappers during an update and new mappers are specified in the module args \([https\://github\.com/ansible\-collections/community\.general/pull/8762](https\://github\.com/ansible\-collections/community\.general/pull/8762)\)\.
* keycloak\_user\_federation \- fix the <code>UnboundLocalError</code> that occurs when an ID is provided for a user federation mapper \([https\://github\.com/ansible\-collections/community\.general/pull/8831](https\://github\.com/ansible\-collections/community\.general/pull/8831)\)\.
* keycloak\_user\_federation \- sort desired and after mapper list by name \(analog to before mapper list\) to minimize diff and make change detection more accurate \([https\://github\.com/ansible\-collections/community\.general/pull/8761](https\://github\.com/ansible\-collections/community\.general/pull/8761)\)\.
* proxmox inventory plugin \- fixed a possible error on concatenating responses from proxmox\. In case an API call unexpectedly returned an empty result\, the inventory failed with a fatal error\. Added check for empty response \([https\://github\.com/ansible\-collections/community\.general/issues/8798](https\://github\.com/ansible\-collections/community\.general/issues/8798)\, [https\://github\.com/ansible\-collections/community\.general/pull/8794](https\://github\.com/ansible\-collections/community\.general/pull/8794)\)\.

<a id="new-modules-1"></a>
### New Modules

* community\.general\.keycloak\_userprofile \- Allows managing Keycloak User Profiles\.
* community\.general\.one\_vnet \- Manages OpenNebula virtual networks\.

<a id="v9-3-0"></a>
## v9\.3\.0

<a id="release-summary-6"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-5"></a>
### Minor Changes

* cgroup\_memory\_recap\, hipchat\, jabber\, log\_plays\, loganalytics\, logentries\, logstash\, slack\, splunk\, sumologic\, syslog\_json callback plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8628](https\://github\.com/ansible\-collections/community\.general/pull/8628)\)\.
* chef\_databag\, consul\_kv\, cyberarkpassword\, dsv\, etcd\, filetree\, hiera\, onepassword\, onepassword\_doc\, onepassword\_raw\, passwordstore\, redis\, shelvefile\, tss lookup plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8626](https\://github\.com/ansible\-collections/community\.general/pull/8626)\)\.
* chroot\, funcd\, incus\, iocage\, jail\, lxc\, lxd\, qubes\, zone connection plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8627](https\://github\.com/ansible\-collections/community\.general/pull/8627)\)\.
* cobbler\, linode\, lxd\, nmap\, online\, scaleway\, stackpath\_compute\, virtualbox inventory plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8625](https\://github\.com/ansible\-collections/community\.general/pull/8625)\)\.
* doas\, dzdo\, ksu\, machinectl\, pbrun\, pfexec\, pmrun\, sesu\, sudosu become plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8623](https\://github\.com/ansible\-collections/community\.general/pull/8623)\)\.
* gconftool2 \- make use of <code>ModuleHelper</code> features to simplify code \([https\://github\.com/ansible\-collections/community\.general/pull/8711](https\://github\.com/ansible\-collections/community\.general/pull/8711)\)\.
* gitlab\_project \- add option <code>container\_expiration\_policy</code> to schedule container registry cleanup \([https\://github\.com/ansible\-collections/community\.general/pull/8674](https\://github\.com/ansible\-collections/community\.general/pull/8674)\)\.
* gitlab\_project \- add option <code>model\_registry\_access\_level</code> to disable model registry \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* gitlab\_project \- add option <code>pages\_access\_level</code> to disable project pages \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* gitlab\_project \- add option <code>repository\_access\_level</code> to disable project repository \([https\://github\.com/ansible\-collections/community\.general/pull/8674](https\://github\.com/ansible\-collections/community\.general/pull/8674)\)\.
* gitlab\_project \- add option <code>service\_desk\_enabled</code> to disable service desk \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* locale\_gen \- add support for multiple locales \([https\://github\.com/ansible\-collections/community\.general/issues/8677](https\://github\.com/ansible\-collections/community\.general/issues/8677)\, [https\://github\.com/ansible\-collections/community\.general/pull/8682](https\://github\.com/ansible\-collections/community\.general/pull/8682)\)\.
* memcached\, pickle\, redis\, yaml cache plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8624](https\://github\.com/ansible\-collections/community\.general/pull/8624)\)\.
* opentelemetry callback plugin \- fix default value for <code>store\_spans\_in\_file</code> causing traces to be produced to a file named <code>None</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8566](https\://github\.com/ansible\-collections/community\.general/issues/8566)\, [https\://github\.com/ansible\-collections/community\.general/pull/8741](https\://github\.com/ansible\-collections/community\.general/pull/8741)\)\.
* passwordstore lookup plugin \- add the current user to the lockfile file name to address issues on multi\-user systems \([https\://github\.com/ansible\-collections/community\.general/pull/8689](https\://github\.com/ansible\-collections/community\.general/pull/8689)\)\.
* pipx \- add parameter <code>suffix</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8675](https\://github\.com/ansible\-collections/community\.general/pull/8675)\, [https\://github\.com/ansible\-collections/community\.general/issues/8656](https\://github\.com/ansible\-collections/community\.general/issues/8656)\)\.
* pkgng \- add option <code>use\_globs</code> \(default <code>true</code>\) to optionally disable glob patterns \([https\://github\.com/ansible\-collections/community\.general/issues/8632](https\://github\.com/ansible\-collections/community\.general/issues/8632)\, [https\://github\.com/ansible\-collections/community\.general/pull/8633](https\://github\.com/ansible\-collections/community\.general/pull/8633)\)\.
* proxmox inventory plugin \- add new fact for LXC interface details \([https\://github\.com/ansible\-collections/community\.general/pull/8713](https\://github\.com/ansible\-collections/community\.general/pull/8713)\)\.
* redis\, redis\_info \- add <code>client\_cert</code> and <code>client\_key</code> options to specify path to certificate for Redis authentication  \([https\://github\.com/ansible\-collections/community\.general/pull/8654](https\://github\.com/ansible\-collections/community\.general/pull/8654)\)\.

<a id="bugfixes-7"></a>
### Bugfixes

* gitlab\_runner \- fix <code>paused</code> parameter being ignored \([https\://github\.com/ansible\-collections/community\.general/pull/8648](https\://github\.com/ansible\-collections/community\.general/pull/8648)\)\.
* homebrew\_cask \- fix <code>upgrade\_all</code> returns <code>changed</code> when nothing upgraded \([https\://github\.com/ansible\-collections/community\.general/issues/8707](https\://github\.com/ansible\-collections/community\.general/issues/8707)\, [https\://github\.com/ansible\-collections/community\.general/pull/8708](https\://github\.com/ansible\-collections/community\.general/pull/8708)\)\.
* keycloak\_user\_federation \- get cleartext IDP <code>clientSecret</code> from full realm info to detect changes to it \([https\://github\.com/ansible\-collections/community\.general/issues/8294](https\://github\.com/ansible\-collections/community\.general/issues/8294)\, [https\://github\.com/ansible\-collections/community\.general/pull/8735](https\://github\.com/ansible\-collections/community\.general/pull/8735)\)\.
* keycloak\_user\_federation \- remove existing user federation mappers if they are not present in the federation configuration and will not be updated \([https\://github\.com/ansible\-collections/community\.general/issues/7169](https\://github\.com/ansible\-collections/community\.general/issues/7169)\, [https\://github\.com/ansible\-collections/community\.general/pull/8695](https\://github\.com/ansible\-collections/community\.general/pull/8695)\)\.
* proxmox \- fixed an issue where the new volume handling incorrectly converted <code>null</code> values into <code>\"None\"</code> strings \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.
* proxmox \- fixed an issue where volume strings where overwritten instead of appended to in the new <code>build\_volume\(\)</code> method \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.
* proxmox \- removed the forced conversion of non\-string values to strings to be consistent with the module documentation \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.

<a id="new-modules-2"></a>
### New Modules

* community\.general\.bootc\_manage \- Bootc Switch and Upgrade\.
* community\.general\.homebrew\_services \- Services manager for Homebrew\.
* community\.general\.keycloak\_realm\_keys\_metadata\_info \- Allows obtaining Keycloak realm keys metadata via Keycloak API\.

<a id="v9-2-0"></a>
## v9\.2\.0

<a id="release-summary-7"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-6"></a>
### Minor Changes

* CmdRunner module utils \- the parameter <code>force\_lang</code> now supports the special value <code>auto</code> which will automatically try and determine the best parsable locale in the system \([https\://github\.com/ansible\-collections/community\.general/pull/8517](https\://github\.com/ansible\-collections/community\.general/pull/8517)\)\.
* proxmox \- add <code>disk\_volume</code> and <code>mount\_volumes</code> keys for better readability \([https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* proxmox \- translate the old <code>disk</code> and <code>mounts</code> keys to the new handling internally \([https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* proxmox\_template \- small refactor in logic for determining whether a template exists or not \([https\://github\.com/ansible\-collections/community\.general/pull/8516](https\://github\.com/ansible\-collections/community\.general/pull/8516)\)\.
* redfish\_\* modules \- adds <code>ciphers</code> option for custom cipher selection \([https\://github\.com/ansible\-collections/community\.general/pull/8533](https\://github\.com/ansible\-collections/community\.general/pull/8533)\)\.
* sudosu become plugin \- added an option \(<code>alt\_method</code>\) to enhance compatibility with more versions of <code>su</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8214](https\://github\.com/ansible\-collections/community\.general/pull/8214)\)\.
* virtualbox inventory plugin \- expose a new parameter <code>enable\_advanced\_group\_parsing</code> to change how the VirtualBox dynamic inventory parses VM groups \([https\://github\.com/ansible\-collections/community\.general/issues/8508](https\://github\.com/ansible\-collections/community\.general/issues/8508)\, [https\://github\.com/ansible\-collections/community\.general/pull/8510](https\://github\.com/ansible\-collections/community\.general/pull/8510)\)\.
* wdc\_redfish\_command \- minor change to handle upgrade file for Redfish WD platforms \([https\://github\.com/ansible\-collections/community\.general/pull/8444](https\://github\.com/ansible\-collections/community\.general/pull/8444)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* bitwarden lookup plugin \- fix <code>KeyError</code> in <code>search\_field</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8549](https\://github\.com/ansible\-collections/community\.general/issues/8549)\, [https\://github\.com/ansible\-collections/community\.general/pull/8557](https\://github\.com/ansible\-collections/community\.general/pull/8557)\)\.
* keycloak\_clientscope \- remove IDs from clientscope and its protocol mappers on comparison for changed check \([https\://github\.com/ansible\-collections/community\.general/pull/8545](https\://github\.com/ansible\-collections/community\.general/pull/8545)\)\.
* nsupdate \- fix \'index out of range\' error when changing NS records by falling back to authority section of the response \([https\://github\.com/ansible\-collections/community\.general/issues/8612](https\://github\.com/ansible\-collections/community\.general/issues/8612)\, [https\://github\.com/ansible\-collections/community\.general/pull/8614](https\://github\.com/ansible\-collections/community\.general/pull/8614)\)\.
* proxmox \- fix idempotency on creation of mount volumes using Proxmox\' special <code>\<storage\>\:\<size\></code> syntax \([https\://github\.com/ansible\-collections/community\.general/issues/8407](https\://github\.com/ansible\-collections/community\.general/issues/8407)\, [https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* redfish\_utils module utils \- do not fail when language is not exactly \"en\" \([https\://github\.com/ansible\-collections/community\.general/pull/8613](https\://github\.com/ansible\-collections/community\.general/pull/8613)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="filter"></a>
#### Filter

* community\.general\.reveal\_ansible\_type \- Return input type\.

<a id="test"></a>
#### Test

* community\.general\.ansible\_type \- Validate input type\.

<a id="v9-1-0"></a>
## v9\.1\.0

<a id="release-summary-8"></a>
### Release Summary

Regular feature and bugfix release\.

<a id="minor-changes-7"></a>
### Minor Changes

* CmdRunner module util \- argument formats can be specified as plain functions without calling <code>cmd\_runner\_fmt\.as\_func\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8479](https\://github\.com/ansible\-collections/community\.general/pull/8479)\)\.
* ansible\_galaxy\_install \- add upgrade feature \([https\://github\.com/ansible\-collections/community\.general/pull/8431](https\://github\.com/ansible\-collections/community\.general/pull/8431)\, [https\://github\.com/ansible\-collections/community\.general/issues/8351](https\://github\.com/ansible\-collections/community\.general/issues/8351)\)\.
* cargo \- add option <code>directory</code>\, which allows source directory to be specified \([https\://github\.com/ansible\-collections/community\.general/pull/8480](https\://github\.com/ansible\-collections/community\.general/pull/8480)\)\.
* cmd\_runner module utils \- add decorator <code>cmd\_runner\_fmt\.stack</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8415](https\://github\.com/ansible\-collections/community\.general/pull/8415)\)\.
* cmd\_runner\_fmt module utils \- simplify implementation of <code>cmd\_runner\_fmt\.as\_bool\_not\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8512](https\://github\.com/ansible\-collections/community\.general/pull/8512)\)\.
* ipa\_dnsrecord \- adds <code>SSHFP</code> record type for managing SSH fingerprints in FreeIPA DNS \([https\://github\.com/ansible\-collections/community\.general/pull/8404](https\://github\.com/ansible\-collections/community\.general/pull/8404)\)\.
* keycloak\_client \- assign auth flow by name \([https\://github\.com/ansible\-collections/community\.general/pull/8428](https\://github\.com/ansible\-collections/community\.general/pull/8428)\)\.
* openbsd\_pkg \- adds diff support to show changes in installed package list\. This does not yet work for check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8402](https\://github\.com/ansible\-collections/community\.general/pull/8402)\)\.
* proxmox \- allow specification of the API port when using proxmox\_\* \([https\://github\.com/ansible\-collections/community\.general/issues/8440](https\://github\.com/ansible\-collections/community\.general/issues/8440)\, [https\://github\.com/ansible\-collections/community\.general/pull/8441](https\://github\.com/ansible\-collections/community\.general/pull/8441)\)\.
* proxmox\_vm\_info \- add <code>network</code> option to retrieve current network information \([https\://github\.com/ansible\-collections/community\.general/pull/8471](https\://github\.com/ansible\-collections/community\.general/pull/8471)\)\.
* redfish\_command \- add <code>wait</code> and <code>wait\_timeout</code> options to allow a user to block a command until a service is accessible after performing the requested command \([https\://github\.com/ansible\-collections/community\.general/issues/8051](https\://github\.com/ansible\-collections/community\.general/issues/8051)\, [https\://github\.com/ansible\-collections/community\.general/pull/8434](https\://github\.com/ansible\-collections/community\.general/pull/8434)\)\.
* redfish\_info \- add command <code>CheckAvailability</code> to check if a service is accessible \([https\://github\.com/ansible\-collections/community\.general/issues/8051](https\://github\.com/ansible\-collections/community\.general/issues/8051)\, [https\://github\.com/ansible\-collections/community\.general/pull/8434](https\://github\.com/ansible\-collections/community\.general/pull/8434)\)\.
* redis\_info \- adds support for getting cluster info \([https\://github\.com/ansible\-collections/community\.general/pull/8464](https\://github\.com/ansible\-collections/community\.general/pull/8464)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* CmdRunner module util \- setting the value of the <code>ignore\_none</code> parameter within a <code>CmdRunner</code> context is deprecated and that feature should be removed in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8479](https\://github\.com/ansible\-collections/community\.general/pull/8479)\)\.
* git\_config \- the <code>list\_all</code> option has been deprecated and will be removed in community\.general 11\.0\.0\. Use the <code>community\.general\.git\_config\_info</code> module instead \([https\://github\.com/ansible\-collections/community\.general/pull/8453](https\://github\.com/ansible\-collections/community\.general/pull/8453)\)\.
* git\_config \- using <code>state\=present</code> without providing <code>value</code> is deprecated and will be disallowed in community\.general 11\.0\.0\. Use the <code>community\.general\.git\_config\_info</code> module instead to read a value \([https\://github\.com/ansible\-collections/community\.general/pull/8453](https\://github\.com/ansible\-collections/community\.general/pull/8453)\)\.

<a id="bugfixes-9"></a>
### Bugfixes

* git\_config \- fix behavior of <code>state\=absent</code> if <code>value</code> is present \([https\://github\.com/ansible\-collections/community\.general/issues/8436](https\://github\.com/ansible\-collections/community\.general/issues/8436)\, [https\://github\.com/ansible\-collections/community\.general/pull/8452](https\://github\.com/ansible\-collections/community\.general/pull/8452)\)\.
* keycloak\_realm \- add normalizations for <code>attributes</code> and <code>protocol\_mappers</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8496](https\://github\.com/ansible\-collections/community\.general/pull/8496)\)\.
* launched \- correctly report changed status in check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8406](https\://github\.com/ansible\-collections/community\.general/pull/8406)\)\.
* opennebula inventory plugin \- fix invalid reference to IP when inventory runs against NICs with no IPv4 address \([https\://github\.com/ansible\-collections/community\.general/pull/8489](https\://github\.com/ansible\-collections/community\.general/pull/8489)\)\.
* opentelemetry callback \- do not save the JSON response when using the <code>ansible\.builtin\.uri</code> module \([https\://github\.com/ansible\-collections/community\.general/pull/8430](https\://github\.com/ansible\-collections/community\.general/pull/8430)\)\.
* opentelemetry callback \- do not save the content response when using the <code>ansible\.builtin\.slurp</code> module \([https\://github\.com/ansible\-collections/community\.general/pull/8430](https\://github\.com/ansible\-collections/community\.general/pull/8430)\)\.
* paman \- do not fail if an empty list of packages has been provided and there is nothing to do \([https\://github\.com/ansible\-collections/community\.general/pull/8514](https\://github\.com/ansible\-collections/community\.general/pull/8514)\)\.

<a id="known-issues"></a>
### Known Issues

* homectl \- the module does not work under Python 3\.13 or newer\, since it relies on the removed <code>crypt</code> standard library module \([https\://github\.com/ansible\-collections/community\.general/issues/4691](https\://github\.com/ansible\-collections/community\.general/issues/4691)\, [https\://github\.com/ansible\-collections/community\.general/pull/8497](https\://github\.com/ansible\-collections/community\.general/pull/8497)\)\.
* udm\_user \- the module does not work under Python 3\.13 or newer\, since it relies on the removed <code>crypt</code> standard library module \([https\://github\.com/ansible\-collections/community\.general/issues/4690](https\://github\.com/ansible\-collections/community\.general/issues/4690)\, [https\://github\.com/ansible\-collections/community\.general/pull/8497](https\://github\.com/ansible\-collections/community\.general/pull/8497)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="filter-1"></a>
#### Filter

* community\.general\.keep\_keys \- Keep specific keys from dictionaries in a list\.
* community\.general\.remove\_keys \- Remove specific keys from dictionaries in a list\.
* community\.general\.replace\_keys \- Replace specific keys in a list of dictionaries\.

<a id="new-modules-3"></a>
### New Modules

* community\.general\.consul\_agent\_check \- Add\, modify\, and delete checks within a consul cluster\.
* community\.general\.consul\_agent\_service \- Add\, modify and delete services within a consul cluster\.
* community\.general\.django\_check \- Wrapper for C\(django\-admin check\)\.
* community\.general\.django\_createcachetable \- Wrapper for C\(django\-admin createcachetable\)\.

<a id="v9-0-1"></a>
## v9\.0\.1

<a id="release-summary-9"></a>
### Release Summary

Bugfix release for inclusion in Ansible 10\.0\.0rc1\.

<a id="minor-changes-8"></a>
### Minor Changes

* ansible\_galaxy\_install \- minor refactor in the module \([https\://github\.com/ansible\-collections/community\.general/pull/8413](https\://github\.com/ansible\-collections/community\.general/pull/8413)\)\.

<a id="bugfixes-10"></a>
### Bugfixes

* cpanm \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* django module utils \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* gconftool2\_info \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* homebrew \- do not fail when brew prints warnings \([https\://github\.com/ansible\-collections/community\.general/pull/8406](https\://github\.com/ansible\-collections/community\.general/pull/8406)\, [https\://github\.com/ansible\-collections/community\.general/issues/7044](https\://github\.com/ansible\-collections/community\.general/issues/7044)\)\.
* hponcfg \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* kernel\_blacklist \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* keycloak\_client \- fix TypeError when sanitizing the <code>saml\.signing\.private\.key</code> attribute in the module\'s diff or state output\. The <code>sanitize\_cr</code> function expected a dict where in some cases a list might occur \([https\://github\.com/ansible\-collections/community\.general/pull/8403](https\://github\.com/ansible\-collections/community\.general/pull/8403)\)\.
* locale\_gen \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* mksysb \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* pipx\_info \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* snap \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* snap\_alias \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.

<a id="v9-0-0"></a>
## v9\.0\.0

<a id="release-summary-10"></a>
### Release Summary

This is release 9\.0\.0 of <code>community\.general</code>\, released on 2024\-05\-20\.

<a id="minor-changes-9"></a>
### Minor Changes

* PythonRunner module utils \- specialisation of <code>CmdRunner</code> to execute Python scripts \([https\://github\.com/ansible\-collections/community\.general/pull/8289](https\://github\.com/ansible\-collections/community\.general/pull/8289)\)\.
* Use offset\-aware <code>datetime\.datetime</code> objects \(with timezone UTC\) instead of offset\-naive UTC timestamps\, which are deprecated in Python 3\.12 \([https\://github\.com/ansible\-collections/community\.general/pull/8222](https\://github\.com/ansible\-collections/community\.general/pull/8222)\)\.
* aix\_lvol \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* apt\_rpm \- add new states <code>latest</code> and <code>present\_not\_latest</code>\. The value <code>latest</code> is equivalent to the current behavior of <code>present</code>\, which will upgrade a package if a newer version exists\. <code>present\_not\_latest</code> does what most users would expect <code>present</code> to do\: it does not upgrade if the package is already installed\. The current behavior of <code>present</code> will be deprecated in a later version\, and eventually changed to that of <code>present\_not\_latest</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8217](https\://github\.com/ansible\-collections/community\.general/issues/8217)\, [https\://github\.com/ansible\-collections/community\.general/pull/8247](https\://github\.com/ansible\-collections/community\.general/pull/8247)\)\.
* apt\_rpm \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* bitwarden lookup plugin \- add <code>bw\_session</code> option\, to pass session key instead of reading from env \([https\://github\.com/ansible\-collections/community\.general/pull/7994](https\://github\.com/ansible\-collections/community\.general/pull/7994)\)\.
* bitwarden lookup plugin \- add support to filter by organization ID \([https\://github\.com/ansible\-collections/community\.general/pull/8188](https\://github\.com/ansible\-collections/community\.general/pull/8188)\)\.
* bitwarden lookup plugin \- allows to fetch all records of a given collection ID\, by allowing to pass an empty value for <code>search\_value</code> when <code>collection\_id</code> is provided \([https\://github\.com/ansible\-collections/community\.general/pull/8013](https\://github\.com/ansible\-collections/community\.general/pull/8013)\)\.
* bitwarden lookup plugin \- when looking for items using an item ID\, the item is now accessed directly with <code>bw get item</code> instead of searching through all items\. This doubles the lookup speed \([https\://github\.com/ansible\-collections/community\.general/pull/7468](https\://github\.com/ansible\-collections/community\.general/pull/7468)\)\.
* btrfs\_subvolume \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* cmd\_runner module\_utils \- add validation for minimum and maximum length in the value passed to <code>cmd\_runner\_fmt\.as\_list\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8288](https\://github\.com/ansible\-collections/community\.general/pull/8288)\)\.
* consul\_auth\_method\, consul\_binding\_rule\, consul\_policy\, consul\_role\, consul\_session\, consul\_token \- added action group <code>community\.general\.consul</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7897](https\://github\.com/ansible\-collections/community\.general/pull/7897)\)\.
* consul\_policy \- added support for diff and check mode \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_policy\, consul\_role\, consul\_session \- removed dependency on <code>requests</code> and factored out common parts \([https\://github\.com/ansible\-collections/community\.general/pull/7826](https\://github\.com/ansible\-collections/community\.general/pull/7826)\, [https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- <code>node\_identities</code> now expects a <code>node\_name</code> option to match the Consul API\, the old <code>name</code> is still supported as alias \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- <code>service\_identities</code> now expects a <code>service\_name</code> option to match the Consul API\, the old <code>name</code> is still supported as alias \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- added support for diff mode \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* consul\_role \- added support for templated policies \([https\://github\.com/ansible\-collections/community\.general/pull/7878](https\://github\.com/ansible\-collections/community\.general/pull/7878)\)\.
* elastic callback plugin \- close elastic client to not leak resources \([https\://github\.com/ansible\-collections/community\.general/pull/7517](https\://github\.com/ansible\-collections/community\.general/pull/7517)\)\.
* filesystem \- add bcachefs support \([https\://github\.com/ansible\-collections/community\.general/pull/8126](https\://github\.com/ansible\-collections/community\.general/pull/8126)\)\.
* gandi\_livedns \- adds support for personal access tokens \([https\://github\.com/ansible\-collections/community\.general/issues/7639](https\://github\.com/ansible\-collections/community\.general/issues/7639)\, [https\://github\.com/ansible\-collections/community\.general/pull/8337](https\://github\.com/ansible\-collections/community\.general/pull/8337)\)\.
* gconftool2 \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* git\_config \- allow multiple git configs for the same name with the new <code>add\_mode</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* git\_config \- the <code>after</code> and <code>before</code> fields in the <code>diff</code> of the return value can be a list instead of a string in case more configs with the same key are affected \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* git\_config \- when a value is unset\, all configs with the same key are unset \([https\://github\.com/ansible\-collections/community\.general/pull/7260](https\://github\.com/ansible\-collections/community\.general/pull/7260)\)\.
* gitlab modules \- add <code>ca\_path</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7472](https\://github\.com/ansible\-collections/community\.general/pull/7472)\)\.
* gitlab modules \- remove duplicate <code>gitlab</code> package check \([https\://github\.com/ansible\-collections/community\.general/pull/7486](https\://github\.com/ansible\-collections/community\.general/pull/7486)\)\.
* gitlab\_deploy\_key\, gitlab\_group\_members\, gitlab\_group\_variable\, gitlab\_hook\, gitlab\_instance\_variable\, gitlab\_project\_badge\, gitlab\_project\_variable\, gitlab\_user \- improve API pagination and compatibility with different versions of <code>python\-gitlab</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7790](https\://github\.com/ansible\-collections/community\.general/pull/7790)\)\.
* gitlab\_hook \- adds <code>releases\_events</code> parameter for supporting Releases events triggers on GitLab hooks \([https\://github\.com/ansible\-collections/community\.general/pull/7956](https\://github\.com/ansible\-collections/community\.general/pull/7956)\)\.
* gitlab\_runner \- add support for new runner creation workflow \([https\://github\.com/ansible\-collections/community\.general/pull/7199](https\://github\.com/ansible\-collections/community\.general/pull/7199)\)\.
* homebrew \- adds <code>force\_formula</code> parameter to disambiguate a formula from a cask of the same name \([https\://github\.com/ansible\-collections/community\.general/issues/8274](https\://github\.com/ansible\-collections/community\.general/issues/8274)\)\.
* homebrew\, homebrew\_cask \- refactor common argument validation logic into a dedicated <code>homebrew</code> module utils \([https\://github\.com/ansible\-collections/community\.general/issues/8323](https\://github\.com/ansible\-collections/community\.general/issues/8323)\, [https\://github\.com/ansible\-collections/community\.general/pull/8324](https\://github\.com/ansible\-collections/community\.general/pull/8324)\)\.
* icinga2 inventory plugin \- add Jinja2 templating support to <code>url</code>\, <code>user</code>\, and <code>password</code> paramenters \([https\://github\.com/ansible\-collections/community\.general/issues/7074](https\://github\.com/ansible\-collections/community\.general/issues/7074)\, [https\://github\.com/ansible\-collections/community\.general/pull/7996](https\://github\.com/ansible\-collections/community\.general/pull/7996)\)\.
* icinga2 inventory plugin \- adds new parameter <code>group\_by\_hostgroups</code> in order to make grouping by Icinga2 hostgroups optional \([https\://github\.com/ansible\-collections/community\.general/pull/7998](https\://github\.com/ansible\-collections/community\.general/pull/7998)\)\.
* ini\_file \- add an optional parameter <code>section\_has\_values</code>\. If the target ini file contains more than one <code>section</code>\, use <code>section\_has\_values</code> to specify which one should be updated \([https\://github\.com/ansible\-collections/community\.general/pull/7505](https\://github\.com/ansible\-collections/community\.general/pull/7505)\)\.
* ini\_file \- support optional spaces between section names and their surrounding brackets \([https\://github\.com/ansible\-collections/community\.general/pull/8075](https\://github\.com/ansible\-collections/community\.general/pull/8075)\)\.
* installp \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* ipa\_config \- adds <code>passkey</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7588](https\://github\.com/ansible\-collections/community\.general/pull/7588)\)\.
* ipa\_dnsrecord \- adds ability to manage NS record types \([https\://github\.com/ansible\-collections/community\.general/pull/7737](https\://github\.com/ansible\-collections/community\.general/pull/7737)\)\.
* ipa\_pwpolicy \- refactor module and exchange a sequence <code>if</code> statements with a <code>for</code> loop \([https\://github\.com/ansible\-collections/community\.general/pull/7723](https\://github\.com/ansible\-collections/community\.general/pull/7723)\)\.
* ipa\_pwpolicy \- update module to support <code>maxrepeat</code>\, <code>maxsequence</code>\, <code>dictcheck</code>\, <code>usercheck</code>\, <code>gracelimit</code> parameters in FreeIPA password policies \([https\://github\.com/ansible\-collections/community\.general/pull/7723](https\://github\.com/ansible\-collections/community\.general/pull/7723)\)\.
* ipa\_sudorule \- adds options to include denied commands or command groups \([https\://github\.com/ansible\-collections/community\.general/pull/7415](https\://github\.com/ansible\-collections/community\.general/pull/7415)\)\.
* ipa\_user \- adds <code>idp</code> and <code>passkey</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7589](https\://github\.com/ansible\-collections/community\.general/pull/7589)\)\.
* irc \- add <code>validate\_certs</code> option\, and rename <code>use\_ssl</code> to <code>use\_tls</code>\, while keeping <code>use\_ssl</code> as an alias\. The default value for <code>validate\_certs</code> is <code>false</code> for backwards compatibility\. We recommend to every user of this module to explicitly set <code>use\_tls\=true</code> and <em class="title-reference">validate\_certs\=true\`</em> whenever possible\, especially when communicating to IRC servers over the internet \([https\://github\.com/ansible\-collections/community\.general/pull/7550](https\://github\.com/ansible\-collections/community\.general/pull/7550)\)\.
* java\_cert \- add <code>cert\_content</code> argument \([https\://github\.com/ansible\-collections/community\.general/pull/8153](https\://github\.com/ansible\-collections/community\.general/pull/8153)\)\.
* java\_cert \- enable <code>owner</code>\, <code>group</code>\, <code>mode</code>\, and other generic file arguments \([https\://github\.com/ansible\-collections/community\.general/pull/8116](https\://github\.com/ansible\-collections/community\.general/pull/8116)\)\.
* kernel\_blacklist \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* keycloak module utils \- expose error message from Keycloak server for HTTP errors in some specific situations \([https\://github\.com/ansible\-collections/community\.general/pull/7645](https\://github\.com/ansible\-collections/community\.general/pull/7645)\)\.
* keycloak\_client\, keycloak\_clientscope\, keycloak\_clienttemplate \- added <code>docker\-v2</code> protocol support\, enhancing alignment with Keycloak\'s protocol options \([https\://github\.com/ansible\-collections/community\.general/issues/8215](https\://github\.com/ansible\-collections/community\.general/issues/8215)\, [https\://github\.com/ansible\-collections/community\.general/pull/8216](https\://github\.com/ansible\-collections/community\.general/pull/8216)\)\.
* keycloak\_realm\_key \- the <code>config\.algorithm</code> option now supports 8 additional key algorithms \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_realm\_key \- the <code>config\.certificate</code> option value is no longer defined with <code>no\_log\=True</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_realm\_key \- the <code>provider\_id</code> option now supports RSA encryption key usage \(value <code>rsa\-enc</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/7698](https\://github\.com/ansible\-collections/community\.general/pull/7698)\)\.
* keycloak\_user\_federation \- add option for <code>krbPrincipalAttribute</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7538](https\://github\.com/ansible\-collections/community\.general/pull/7538)\)\.
* keycloak\_user\_federation \- allow custom user storage providers to be set through <code>provider\_id</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7789](https\://github\.com/ansible\-collections/community\.general/pull/7789)\)\.
* ldap\_attrs \- module now supports diff mode\, showing which attributes are changed within an operation \([https\://github\.com/ansible\-collections/community\.general/pull/8073](https\://github\.com/ansible\-collections/community\.general/pull/8073)\)\.
* lvg \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* lvol \- change <code>pvs</code> argument type to list of strings \([https\://github\.com/ansible\-collections/community\.general/pull/7676](https\://github\.com/ansible\-collections/community\.general/pull/7676)\, [https\://github\.com/ansible\-collections/community\.general/issues/7504](https\://github\.com/ansible\-collections/community\.general/issues/7504)\)\.
* lvol \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* lxd connection plugin \- tighten the detection logic for lxd <code>Instance not found</code> errors\, to avoid false detection on unrelated errors such as <code>/usr/bin/python3\: not found</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7521](https\://github\.com/ansible\-collections/community\.general/pull/7521)\)\.
* lxd\_container \- uses <code>/1\.0/instances</code> API endpoint\, if available\. Falls back to <code>/1\.0/containers</code> or <code>/1\.0/virtual\-machines</code>\. Fixes issue when using Incus or LXD 5\.19 due to migrating to <code>/1\.0/instances</code> endpoint \([https\://github\.com/ansible\-collections/community\.general/pull/7980](https\://github\.com/ansible\-collections/community\.general/pull/7980)\)\.
* macports \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* mail \- add <code>Message\-ID</code> header\; which is required by some mail servers \([https\://github\.com/ansible\-collections/community\.general/pull/7740](https\://github\.com/ansible\-collections/community\.general/pull/7740)\)\.
* mail module\, mail callback plugin \- allow to configure the domain name of the Message\-ID header with a new <code>message\_id\_domain</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7765](https\://github\.com/ansible\-collections/community\.general/pull/7765)\)\.
* mssql\_script \- adds transactional \(rollback/commit\) support via optional boolean param <code>transaction</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7976](https\://github\.com/ansible\-collections/community\.general/pull/7976)\)\.
* netcup\_dns \- adds support for record types <code>OPENPGPKEY</code>\, <code>SMIMEA</code>\, and <code>SSHFP</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7489](https\://github\.com/ansible\-collections/community\.general/pull/7489)\)\.
* nmcli \- add support for new connection type <code>loopback</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6572](https\://github\.com/ansible\-collections/community\.general/issues/6572)\)\.
* nmcli \- adds OpenvSwitch support with new <code>type</code> values <code>ovs\-port</code>\, <code>ovs\-interface</code>\, and <code>ovs\-bridge</code>\, and new <code>slave\_type</code> value <code>ovs\-port</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8154](https\://github\.com/ansible\-collections/community\.general/pull/8154)\)\.
* nmcli \- allow for <code>infiniband</code> slaves of <code>bond</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/7569](https\://github\.com/ansible\-collections/community\.general/pull/7569)\)\.
* nmcli \- allow for the setting of <code>MTU</code> for <code>infiniband</code> and <code>bond</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/7499](https\://github\.com/ansible\-collections/community\.general/pull/7499)\)\.
* nmcli \- allow setting <code>MTU</code> for <code>bond\-slave</code> interface types \([https\://github\.com/ansible\-collections/community\.general/pull/8118](https\://github\.com/ansible\-collections/community\.general/pull/8118)\)\.
* onepassword lookup plugin \- support 1Password Connect with the opv2 client by setting the connect\_host and connect\_token parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7116](https\://github\.com/ansible\-collections/community\.general/pull/7116)\)\.
* onepassword\_raw lookup plugin \- support 1Password Connect with the opv2 client by setting the connect\_host and connect\_token parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7116](https\://github\.com/ansible\-collections/community\.general/pull/7116)\)
* opentelemetry \- add support for HTTP trace\_exporter and configures the behavior via <code>OTEL\_EXPORTER\_OTLP\_TRACES\_PROTOCOL</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7888](https\://github\.com/ansible\-collections/community\.general/issues/7888)\, [https\://github\.com/ansible\-collections/community\.general/pull/8321](https\://github\.com/ansible\-collections/community\.general/pull/8321)\)\.
* opentelemetry \- add support for exporting spans in a file via <code>ANSIBLE\_OPENTELEMETRY\_STORE\_SPANS\_IN\_FILE</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7888](https\://github\.com/ansible\-collections/community\.general/issues/7888)\, [https\://github\.com/ansible\-collections/community\.general/pull/8363](https\://github\.com/ansible\-collections/community\.general/pull/8363)\)\.
* opkg \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* osx\_defaults \- add option <code>check\_types</code> to enable changing the type of existing defaults on the fly \([https\://github\.com/ansible\-collections/community\.general/pull/8173](https\://github\.com/ansible\-collections/community\.general/pull/8173)\)\.
* parted \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* passwordstore \- adds <code>timestamp</code> and <code>preserve</code> parameters to modify the stored password format \([https\://github\.com/ansible\-collections/community\.general/pull/7426](https\://github\.com/ansible\-collections/community\.general/pull/7426)\)\.
* passwordstore lookup \- add <code>missing\_subkey</code> parameter defining the behavior of the lookup when a passwordstore subkey is missing \([https\://github\.com/ansible\-collections/community\.general/pull/8166](https\://github\.com/ansible\-collections/community\.general/pull/8166)\)\.
* pipx \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* pkg5 \- add support for non\-silent execution \([https\://github\.com/ansible\-collections/community\.general/issues/8379](https\://github\.com/ansible\-collections/community\.general/issues/8379)\, [https\://github\.com/ansible\-collections/community\.general/pull/8382](https\://github\.com/ansible\-collections/community\.general/pull/8382)\)\.
* pkgin \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* portage \- adds the possibility to explicitely tell portage to write packages to world file \([https\://github\.com/ansible\-collections/community\.general/issues/6226](https\://github\.com/ansible\-collections/community\.general/issues/6226)\, [https\://github\.com/ansible\-collections/community\.general/pull/8236](https\://github\.com/ansible\-collections/community\.general/pull/8236)\)\.
* portinstall \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* proxmox \- adds <code>startup</code> parameters to configure startup order\, startup delay and shutdown delay \([https\://github\.com/ansible\-collections/community\.general/pull/8038](https\://github\.com/ansible\-collections/community\.general/pull/8038)\)\.
* proxmox \- adds <code>template</code> value to the <code>state</code> parameter\, allowing conversion of container to a template \([https\://github\.com/ansible\-collections/community\.general/pull/7143](https\://github\.com/ansible\-collections/community\.general/pull/7143)\)\.
* proxmox \- adds <code>update</code> parameter\, allowing update of an already existing containers configuration \([https\://github\.com/ansible\-collections/community\.general/pull/7540](https\://github\.com/ansible\-collections/community\.general/pull/7540)\)\.
* proxmox inventory plugin \- adds an option to exclude nodes from the dynamic inventory generation\. The new setting is optional\, not using this option will behave as usual \([https\://github\.com/ansible\-collections/community\.general/issues/6714](https\://github\.com/ansible\-collections/community\.general/issues/6714)\, [https\://github\.com/ansible\-collections/community\.general/pull/7461](https\://github\.com/ansible\-collections/community\.general/pull/7461)\)\.
* proxmox\* modules \- there is now a <code>community\.general\.proxmox</code> module defaults group that can be used to set default options for all Proxmox modules \([https\://github\.com/ansible\-collections/community\.general/pull/8334](https\://github\.com/ansible\-collections/community\.general/pull/8334)\)\.
* proxmox\_disk \- add ability to manipulate CD\-ROM drive \([https\://github\.com/ansible\-collections/community\.general/pull/7495](https\://github\.com/ansible\-collections/community\.general/pull/7495)\)\.
* proxmox\_kvm \- add parameter <code>update\_unsafe</code> to avoid limitations when updating dangerous values \([https\://github\.com/ansible\-collections/community\.general/pull/7843](https\://github\.com/ansible\-collections/community\.general/pull/7843)\)\.
* proxmox\_kvm \- adds <code>template</code> value to the <code>state</code> parameter\, allowing conversion of a VM to a template \([https\://github\.com/ansible\-collections/community\.general/pull/7143](https\://github\.com/ansible\-collections/community\.general/pull/7143)\)\.
* proxmox\_kvm \- adds\`\`usb\`\` parameter for setting USB devices on proxmox KVM VMs \([https\://github\.com/ansible\-collections/community\.general/pull/8199](https\://github\.com/ansible\-collections/community\.general/pull/8199)\)\.
* proxmox\_kvm \- support the <code>hookscript</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/7600](https\://github\.com/ansible\-collections/community\.general/issues/7600)\)\.
* proxmox\_ostype \- it is now possible to specify the <code>ostype</code> when creating an LXC container \([https\://github\.com/ansible\-collections/community\.general/pull/7462](https\://github\.com/ansible\-collections/community\.general/pull/7462)\)\.
* proxmox\_vm\_info \- add ability to retrieve configuration info \([https\://github\.com/ansible\-collections/community\.general/pull/7485](https\://github\.com/ansible\-collections/community\.general/pull/7485)\)\.
* puppet \- new feature to set <code>\-\-waitforlock</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/8282](https\://github\.com/ansible\-collections/community\.general/pull/8282)\)\.
* redfish\_command \- add command <code>ResetToDefaults</code> to reset manager to default state \([https\://github\.com/ansible\-collections/community\.general/issues/8163](https\://github\.com/ansible\-collections/community\.general/issues/8163)\)\.
* redfish\_config \- add command <code>SetServiceIdentification</code> to set service identification \([https\://github\.com/ansible\-collections/community\.general/issues/7916](https\://github\.com/ansible\-collections/community\.general/issues/7916)\)\.
* redfish\_info \- add boolean return value <code>MultipartHttpPush</code> to <code>GetFirmwareUpdateCapabilities</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8194](https\://github\.com/ansible\-collections/community\.general/issues/8194)\, [https\://github\.com/ansible\-collections/community\.general/pull/8195](https\://github\.com/ansible\-collections/community\.general/pull/8195)\)\.
* redfish\_info \- add command <code>GetServiceIdentification</code> to get service identification \([https\://github\.com/ansible\-collections/community\.general/issues/7882](https\://github\.com/ansible\-collections/community\.general/issues/7882)\)\.
* redfish\_info \- adding the <code>BootProgress</code> property when getting <code>Systems</code> info \([https\://github\.com/ansible\-collections/community\.general/pull/7626](https\://github\.com/ansible\-collections/community\.general/pull/7626)\)\.
* revbitspss lookup plugin \- removed a redundant unicode prefix\. The prefix was not necessary for Python 3 and has been cleaned up to streamline the code \([https\://github\.com/ansible\-collections/community\.general/pull/8087](https\://github\.com/ansible\-collections/community\.general/pull/8087)\)\.
* rundeck module utils \- allow to pass <code>Content\-Type</code> to API requests \([https\://github\.com/ansible\-collections/community\.general/pull/7684](https\://github\.com/ansible\-collections/community\.general/pull/7684)\)\.
* slackpkg \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* ssh\_config \- adds <code>controlmaster</code>\, <code>controlpath</code> and <code>controlpersist</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7456](https\://github\.com/ansible\-collections/community\.general/pull/7456)\)\.
* ssh\_config \- allow <code>accept\-new</code> as valid value for <code>strict\_host\_key\_checking</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8257](https\://github\.com/ansible\-collections/community\.general/pull/8257)\)\.
* ssh\_config \- new feature to set <code>AddKeysToAgent</code> option to <code>yes</code> or <code>no</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7703](https\://github\.com/ansible\-collections/community\.general/pull/7703)\)\.
* ssh\_config \- new feature to set <code>IdentitiesOnly</code> option to <code>yes</code> or <code>no</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7704](https\://github\.com/ansible\-collections/community\.general/pull/7704)\)\.
* sudoers \- add support for the <code>NOEXEC</code> tag in sudoers rules \([https\://github\.com/ansible\-collections/community\.general/pull/7983](https\://github\.com/ansible\-collections/community\.general/pull/7983)\)\.
* svr4pkg \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* swdepot \- refactor module to pass list of arguments to <code>module\.run\_command\(\)</code> instead of relying on interpretation by a shell \([https\://github\.com/ansible\-collections/community\.general/pull/8264](https\://github\.com/ansible\-collections/community\.general/pull/8264)\)\.
* terraform \- add support for <code>diff\_mode</code> for terraform resource\_changes \([https\://github\.com/ansible\-collections/community\.general/pull/7896](https\://github\.com/ansible\-collections/community\.general/pull/7896)\)\.
* terraform \- fix <code>diff\_mode</code> in state <code>absent</code> and when terraform <code>resource\_changes</code> does not exist \([https\://github\.com/ansible\-collections/community\.general/pull/7963](https\://github\.com/ansible\-collections/community\.general/pull/7963)\)\.
* xcc\_redfish\_command \- added support for raw POSTs \(<code>command\=PostResource</code> in <code>category\=Raw</code>\) without a specific action info \([https\://github\.com/ansible\-collections/community\.general/pull/7746](https\://github\.com/ansible\-collections/community\.general/pull/7746)\)\.
* xfconf \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* xfconf\_info \- use <code>ModuleHelper</code> with <code>VarDict</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* cpanm \- the default of the <code>mode</code> option changed from <code>compatibility</code> to <code>new</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* django\_manage \- the module now requires Django \>\= 4\.1 \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* django\_manage \- the module will now fail if <code>virtualenv</code> is specified but no virtual environment exists at that location \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* redfish\_command\, redfish\_config\, redfish\_info \- change the default for <code>timeout</code> from 10 to 60 \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.

<a id="deprecated-features-3"></a>
### Deprecated Features

* MH DependencyCtxMgr module\_utils \- deprecate <code>module\_utils\.mh\.mixin\.deps\.DependencyCtxMgr</code> in favour of <code>module\_utils\.deps</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.AnsibleModule</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.DependencyCtxMgr</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.StateMixin</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.VarDict\,</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.VarMeta</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate <code>plugins\.module\_utils\.module\_helper\.VarsMixin</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8280](https\://github\.com/ansible\-collections/community\.general/pull/8280)\)\.
* ModuleHelper module\_utils \- deprecate use of <code>VarsMixin</code> in favor of using the <code>VardDict</code> module\_utils \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* ModuleHelper vars module\_utils \- bump deprecation of <code>VarMeta</code>\, <code>VarDict</code> and <code>VarsMixin</code> to version 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8226](https\://github\.com/ansible\-collections/community\.general/pull/8226)\)\.
* apt\_rpm \- the behavior of <code>state\=present</code> and <code>state\=installed</code> is deprecated and will change in community\.general 11\.0\.0\. Right now the module will upgrade a package to the latest version if one of these two states is used\. You should explicitly use <code>state\=latest</code> if you want this behavior\, and switch to <code>state\=present\_not\_latest</code> if you do not want to upgrade the package if it is already installed\. In community\.general 11\.0\.0 the behavior of <code>state\=present</code> and <code>state\=installed</code> will change to that of <code>state\=present\_not\_latest</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8217](https\://github\.com/ansible\-collections/community\.general/issues/8217)\, [https\://github\.com/ansible\-collections/community\.general/pull/8285](https\://github\.com/ansible\-collections/community\.general/pull/8285)\)\.
* consul\_acl \- the module has been deprecated and will be removed in community\.general 10\.0\.0\. <code>consul\_token</code> and <code>consul\_policy</code> can be used instead \([https\://github\.com/ansible\-collections/community\.general/pull/7901](https\://github\.com/ansible\-collections/community\.general/pull/7901)\)\.
* django\_manage \- the <code>ack\_venv\_creation\_deprecation</code> option has no more effect and will be removed from community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* gitlab modules \- the basic auth method on GitLab API have been deprecated and will be removed in community\.general 10\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8383](https\://github\.com/ansible\-collections/community\.general/pull/8383)\)\.
* hipchat callback plugin \- the hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020\. The callback plugin is therefore deprecated and will be removed from community\.general 10\.0\.0 if nobody provides compelling reasons to still keep it \([https\://github\.com/ansible\-collections/community\.general/issues/8184](https\://github\.com/ansible\-collections/community\.general/issues/8184)\, [https\://github\.com/ansible\-collections/community\.general/pull/8189](https\://github\.com/ansible\-collections/community\.general/pull/8189)\)\.
* irc \- the defaults <code>false</code> for <code>use\_tls</code> and <code>validate\_certs</code> have been deprecated and will change to <code>true</code> in community\.general 10\.0\.0 to improve security\. You can already improve security now by explicitly setting them to <code>true</code>\. Specifying values now disables the deprecation warning \([https\://github\.com/ansible\-collections/community\.general/pull/7578](https\://github\.com/ansible\-collections/community\.general/pull/7578)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* The deprecated redirects for internal module names have been removed\. These internal redirects were extra\-long FQCNs like <code>community\.general\.packaging\.os\.apt\_rpm</code> that redirect to the short FQCN <code>community\.general\.apt\_rpm</code>\. They were originally needed to implement flatmapping\; as various tooling started to recommend users to use the long names flatmapping was removed from the collection and redirects were added for users who already followed these incorrect recommendations \([https\://github\.com/ansible\-collections/community\.general/pull/7835](https\://github\.com/ansible\-collections/community\.general/pull/7835)\)\.
* ansible\_galaxy\_install \- the <code>ack\_ansible29</code> and <code>ack\_min\_ansiblecore211</code> options have been removed\. They no longer had any effect \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* cloudflare\_dns \- remove support for SPF records\. These are no longer supported by CloudFlare \([https\://github\.com/ansible\-collections/community\.general/pull/7782](https\://github\.com/ansible\-collections/community\.general/pull/7782)\)\.
* django\_manage \- support for the <code>command</code> values <code>cleanup</code>\, <code>syncdb</code>\, and <code>validate</code> were removed\. Use <code>clearsessions</code>\, <code>migrate</code>\, and <code>check</code> instead\, respectively \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* flowdock \- this module relied on HTTPS APIs that do not exist anymore and was thus removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* mh\.mixins\.deps module utils \- the <code>DependencyMixin</code> has been removed\. Use the <code>deps</code> module utils instead \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* proxmox \- the <code>proxmox\_default\_behavior</code> option has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* rax\* modules\, rax module utils\, rax docs fragment \- the Rackspace modules relied on the deprecated package <code>pyrax</code> and were thus removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* redhat module utils \- the classes <code>Rhsm</code>\, <code>RhsmPool</code>\, and <code>RhsmPools</code> have been removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* redhat\_subscription \- the alias <code>autosubscribe</code> of the <code>auto\_attach</code> option was removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* stackdriver \- this module relied on HTTPS APIs that do not exist anymore and was thus removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.
* webfaction\_\* modules \- these modules relied on HTTPS APIs that do not exist anymore and were thus removed \([https\://github\.com/ansible\-collections/community\.general/pull/8198](https\://github\.com/ansible\-collections/community\.general/pull/8198)\)\.

<a id="security-fixes-2"></a>
### Security Fixes

* cobbler\, gitlab\_runners\, icinga2\, linode\, lxd\, nmap\, online\, opennebula\, proxmox\, scaleway\, stackpath\_compute\, virtualbox\, and xen\_orchestra inventory plugin \- make sure all data received from the remote servers is marked as unsafe\, so remote code execution by obtaining texts that can be evaluated as templates is not possible \([https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/](https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/)\, [https\://github\.com/ansible\-collections/community\.general/pull/8098](https\://github\.com/ansible\-collections/community\.general/pull/8098)\)\.
* keycloak\_identity\_provider \- the client secret was not correctly sanitized by the module\. The return values <code>proposed</code>\, <code>existing</code>\, and <code>end\_state</code>\, as well as the diff\, did contain the client secret unmasked \([https\://github\.com/ansible\-collections/community\.general/pull/8355](https\://github\.com/ansible\-collections/community\.general/pull/8355)\)\.

<a id="bugfixes-11"></a>
### Bugfixes

* aix\_filesystem \- fix <code>\_validate\_vg</code> not passing VG name to <code>lsvg\_cmd</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8151](https\://github\.com/ansible\-collections/community\.general/issues/8151)\)\.
* aix\_filesystem \- fix issue with empty list items in crfs logic and option order \([https\://github\.com/ansible\-collections/community\.general/pull/8052](https\://github\.com/ansible\-collections/community\.general/pull/8052)\)\.
* apt\-rpm \- the module did not upgrade packages if a newer version exists\. Now the package will be reinstalled if the candidate is newer than the installed version \([https\://github\.com/ansible\-collections/community\.general/issues/7414](https\://github\.com/ansible\-collections/community\.general/issues/7414)\)\.
* apt\_rpm \- when checking whether packages were installed after running <code>apt\-get \-y install \<packages\></code>\, only the last package name was checked \([https\://github\.com/ansible\-collections/community\.general/pull/8263](https\://github\.com/ansible\-collections/community\.general/pull/8263)\)\.
* bitwarden\_secrets\_manager lookup plugin \- implements retry with exponential backoff to avoid lookup errors when Bitwardn\'s API rate limiting is encountered \([https\://github\.com/ansible\-collections/community\.general/issues/8230](https\://github\.com/ansible\-collections/community\.general/issues/8230)\, [https\://github\.com/ansible\-collections/community\.general/pull/8238](https\://github\.com/ansible\-collections/community\.general/pull/8238)\)\.
* cargo \- fix idempotency issues when using a custom installation path for packages \(using the <code>\-\-path</code> parameter\)\. The initial installation runs fine\, but subsequent runs use the <code>get\_installed\(\)</code> function which did not check the given installation location\, before running <code>cargo install</code>\. This resulted in a false <code>changed</code> state\. Also the removal of packeges using <code>state\: absent</code> failed\, as the installation check did not use the given parameter \([https\://github\.com/ansible\-collections/community\.general/pull/7970](https\://github\.com/ansible\-collections/community\.general/pull/7970)\)\.
* cloudflare\_dns \- fix Cloudflare lookup of SHFP records \([https\://github\.com/ansible\-collections/community\.general/issues/7652](https\://github\.com/ansible\-collections/community\.general/issues/7652)\)\.
* consul\_token \- fix token creation without <code>accessor\_id</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8091](https\://github\.com/ansible\-collections/community\.general/pull/8091)\)\.
* from\_ini filter plugin \- disabling interpolation of <code>ConfigParser</code> to allow converting values with a <code>\%</code> sign \([https\://github\.com/ansible\-collections/community\.general/issues/8183](https\://github\.com/ansible\-collections/community\.general/issues/8183)\, [https\://github\.com/ansible\-collections/community\.general/pull/8185](https\://github\.com/ansible\-collections/community\.general/pull/8185)\)\.
* gitlab\_group\_members \- fix gitlab constants call in <code>gitlab\_group\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_issue \- fix behavior to search GitLab issue\, using <code>search</code> keyword instead of <code>title</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7846](https\://github\.com/ansible\-collections/community\.general/issues/7846)\)\.
* gitlab\_issue\, gitlab\_label\, gitlab\_milestone \- avoid crash during version comparison when the python\-gitlab Python module is not installed \([https\://github\.com/ansible\-collections/community\.general/pull/8158](https\://github\.com/ansible\-collections/community\.general/pull/8158)\)\.
* gitlab\_project\_members \- fix gitlab constants call in <code>gitlab\_project\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_protected\_branches \- fix gitlab constants call in <code>gitlab\_protected\_branches</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_runner \- fix pagination when checking for existing runners \([https\://github\.com/ansible\-collections/community\.general/pull/7790](https\://github\.com/ansible\-collections/community\.general/pull/7790)\)\.
* gitlab\_user \- fix gitlab constants call in <code>gitlab\_user</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* haproxy \- fix an issue where HAProxy could get stuck in DRAIN mode when the backend was unreachable \([https\://github\.com/ansible\-collections/community\.general/issues/8092](https\://github\.com/ansible\-collections/community\.general/issues/8092)\)\.
* homebrew \- detect already installed formulae and casks using JSON output from <code>brew info</code> \([https\://github\.com/ansible\-collections/community\.general/issues/864](https\://github\.com/ansible\-collections/community\.general/issues/864)\)\.
* homebrew \- error returned from brew command was ignored and tried to parse empty JSON\. Fix now checks for an error and raises it to give accurate error message to users \([https\://github\.com/ansible\-collections/community\.general/issues/8047](https\://github\.com/ansible\-collections/community\.general/issues/8047)\)\.
* incus connection plugin \- treats <code>inventory\_hostname</code> as a variable instead of a literal in remote connections \([https\://github\.com/ansible\-collections/community\.general/issues/7874](https\://github\.com/ansible\-collections/community\.general/issues/7874)\)\.
* interface\_files \- also consider <code>address\_family</code> when changing <code>option\=method</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7610](https\://github\.com/ansible\-collections/community\.general/issues/7610)\, [https\://github\.com/ansible\-collections/community\.general/pull/7612](https\://github\.com/ansible\-collections/community\.general/pull/7612)\)\.
* inventory plugins \- add unsafe wrapper to avoid marking strings that do not contain <code>\{</code> or <code>\}</code> as unsafe\, to work around a bug in AWX \(\([https\://github\.com/ansible\-collections/community\.general/issues/8212](https\://github\.com/ansible\-collections/community\.general/issues/8212)\, [https\://github\.com/ansible\-collections/community\.general/pull/8225](https\://github\.com/ansible\-collections/community\.general/pull/8225)\)\.
* ipa \- fix get version regex in IPA module\_utils \([https\://github\.com/ansible\-collections/community\.general/pull/8175](https\://github\.com/ansible\-collections/community\.general/pull/8175)\)\.
* ipa\_hbacrule \- the module uses a string for <code>ipaenabledflag</code> for new FreeIPA versions while the returned value is a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7880](https\://github\.com/ansible\-collections/community\.general/pull/7880)\)\.
* ipa\_otptoken \- the module expect <code>ipatokendisabled</code> as string but the <code>ipatokendisabled</code> value is returned as a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7795](https\://github\.com/ansible\-collections/community\.general/pull/7795)\)\.
* ipa\_sudorule \- the module uses a string for <code>ipaenabledflag</code> for new FreeIPA versions while the returned value is a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7880](https\://github\.com/ansible\-collections/community\.general/pull/7880)\)\.
* iptables\_state \- fix idempotency issues when restoring incomplete iptables dumps \([https\://github\.com/ansible\-collections/community\.general/issues/8029](https\://github\.com/ansible\-collections/community\.general/issues/8029)\)\.
* irc \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* keycloak\_\* \- fix Keycloak API client to quote <code>/</code> properly \([https\://github\.com/ansible\-collections/community\.general/pull/7641](https\://github\.com/ansible\-collections/community\.general/pull/7641)\)\.
* keycloak\_authz\_permission \- resource payload variable for scope\-based permission was constructed as a string\, when it needs to be a list\, even for a single item \([https\://github\.com/ansible\-collections/community\.general/issues/7151](https\://github\.com/ansible\-collections/community\.general/issues/7151)\)\.
* keycloak\_client \- add sorted <code>defaultClientScopes</code> and <code>optionalClientScopes</code> to normalizations \([https\://github\.com/ansible\-collections/community\.general/pull/8223](https\://github\.com/ansible\-collections/community\.general/pull/8223)\)\.
* keycloak\_client \- fixes issue when metadata is provided in desired state when task is in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/1226](https\://github\.com/ansible\-collections/community\.general/issues/1226)\, [https\://github\.com/ansible\-collections/community\.general/pull/7881](https\://github\.com/ansible\-collections/community\.general/pull/7881)\)\.
* keycloak\_identity\_provider \- <code>mappers</code> processing was not idempotent if the mappers configuration list had not been sorted by name \(in ascending order\)\. Fix resolves the issue by sorting mappers in the desired state using the same key which is used for obtaining existing state \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_identity\_provider \- it was not possible to reconfigure \(add\, remove\) <code>mappers</code> once they were created initially\. Removal was ignored\, adding new ones resulted in dropping the pre\-existing unmodified mappers\. Fix resolves the issue by supplying correct input to the internal update call \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_realm \- add normalizations for <code>enabledEventTypes</code> and <code>supportedLocales</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8224](https\://github\.com/ansible\-collections/community\.general/pull/8224)\)\.
* keycloak\_user \- when <code>force</code> is set\, but user does not exist\, do not try to delete it \([https\://github\.com/ansible\-collections/community\.general/pull/7696](https\://github\.com/ansible\-collections/community\.general/pull/7696)\)\.
* keycloak\_user\_federation \- fix diff of empty <code>krbPrincipalAttribute</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8320](https\://github\.com/ansible\-collections/community\.general/pull/8320)\)\.
* ldap \- previously the order number \(if present\) was expected to follow an equals sign in the DN\. This makes it so the order number string is identified correctly anywhere within the DN \([https\://github\.com/ansible\-collections/community\.general/issues/7646](https\://github\.com/ansible\-collections/community\.general/issues/7646)\)\.
* linode inventory plugin \- add descriptive error message for linode inventory plugin \([https\://github\.com/ansible\-collections/community\.general/pull/8133](https\://github\.com/ansible\-collections/community\.general/pull/8133)\)\.
* log\_entries callback plugin \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* lvol \- test for output messages in both <code>stdout</code> and <code>stderr</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7601](https\://github\.com/ansible\-collections/community\.general/pull/7601)\, [https\://github\.com/ansible\-collections/community\.general/issues/7182](https\://github\.com/ansible\-collections/community\.general/issues/7182)\)\.
* merge\_variables lookup plugin \- fixing cross host merge\: providing access to foreign hosts variables to the perspective of the host that is performing the merge \([https\://github\.com/ansible\-collections/community\.general/pull/8303](https\://github\.com/ansible\-collections/community\.general/pull/8303)\)\.
* modprobe \- listing modules files or modprobe files could trigger a FileNotFoundError if <code>/etc/modprobe\.d</code> or <code>/etc/modules\-load\.d</code> did not exist\. Relevant functions now return empty lists if the directories do not exist to avoid crashing the module \([https\://github\.com/ansible\-collections/community\.general/issues/7717](https\://github\.com/ansible\-collections/community\.general/issues/7717)\)\.
* mssql\_script \- make the module work with Python 2 \([https\://github\.com/ansible\-collections/community\.general/issues/7818](https\://github\.com/ansible\-collections/community\.general/issues/7818)\, [https\://github\.com/ansible\-collections/community\.general/pull/7821](https\://github\.com/ansible\-collections/community\.general/pull/7821)\)\.
* nmcli \- fix <code>connection\.slave\-type</code> wired to <code>bond</code> and not with parameter <code>slave\_type</code> in case of connection type <code>wifi</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7389](https\://github\.com/ansible\-collections/community\.general/issues/7389)\)\.
* ocapi\_utils\, oci\_utils\, redfish\_utils module utils \- replace <code>type\(\)</code> calls with <code>isinstance\(\)</code> calls \([https\://github\.com/ansible\-collections/community\.general/pull/7501](https\://github\.com/ansible\-collections/community\.general/pull/7501)\)\.
* onepassword lookup plugin \- failed for fields that were in sections and had uppercase letters in the label/ID\. Field lookups are now case insensitive in all cases \([https\://github\.com/ansible\-collections/community\.general/pull/7919](https\://github\.com/ansible\-collections/community\.general/pull/7919)\)\.
* onepassword lookup plugin \- field and section titles are now case insensitive when using op CLI version two or later\. This matches the behavior of version one \([https\://github\.com/ansible\-collections/community\.general/pull/7564](https\://github\.com/ansible\-collections/community\.general/pull/7564)\)\.
* opentelemetry callback plugin \- close spans always \([https\://github\.com/ansible\-collections/community\.general/pull/8367](https\://github\.com/ansible\-collections/community\.general/pull/8367)\)\.
* opentelemetry callback plugin \- honour the <code>disable\_logs</code> option to avoid storing task results since they are not used regardless \([https\://github\.com/ansible\-collections/community\.general/pull/8373](https\://github\.com/ansible\-collections/community\.general/pull/8373)\)\.
* pacemaker\_cluster \- actually implement check mode\, which the module claims to support\. This means that until now the module also did changes in check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8081](https\://github\.com/ansible\-collections/community\.general/pull/8081)\)\.
* pam\_limits \- when the file does not exist\, do not create it in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/8050](https\://github\.com/ansible\-collections/community\.general/issues/8050)\, [https\://github\.com/ansible\-collections/community\.general/pull/8057](https\://github\.com/ansible\-collections/community\.general/pull/8057)\)\.
* pipx module utils \- change the CLI argument formatter for the <code>pip\_args</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/7497](https\://github\.com/ansible\-collections/community\.general/issues/7497)\, [https\://github\.com/ansible\-collections/community\.general/pull/7506](https\://github\.com/ansible\-collections/community\.general/pull/7506)\)\.
* pkgin \- pkgin \(pkgsrc package manager used by SmartOS\) raises erratic exceptions and spurious <code>changed\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7971](https\://github\.com/ansible\-collections/community\.general/pull/7971)\)\.
* proxmox \- fix updating a container config if the setting does not already exist \([https\://github\.com/ansible\-collections/community\.general/pull/7872](https\://github\.com/ansible\-collections/community\.general/pull/7872)\)\.
* proxmox\_kvm \- fixed status check getting from node\-specific API endpoint \([https\://github\.com/ansible\-collections/community\.general/issues/7817](https\://github\.com/ansible\-collections/community\.general/issues/7817)\)\.
* proxmox\_kvm \- running <code>state\=template</code> will first check whether VM is already a template \([https\://github\.com/ansible\-collections/community\.general/pull/7792](https\://github\.com/ansible\-collections/community\.general/pull/7792)\)\.
* proxmox\_pool\_member \- absent state for type VM did not delete VMs from the pools \([https\://github\.com/ansible\-collections/community\.general/pull/7464](https\://github\.com/ansible\-collections/community\.general/pull/7464)\)\.
* puppet \- add option <code>environment\_lang</code> to set the environment language encoding\. Defaults to lang <code>C</code>\. It is recommended to set it to <code>C\.UTF\-8</code> or <code>en\_US\.UTF\-8</code> depending on what is available on your system\. \([https\://github\.com/ansible\-collections/community\.general/issues/8000](https\://github\.com/ansible\-collections/community\.general/issues/8000)\)
* redfish\_command \- fix usage of message parsing in <code>SimpleUpdate</code> and <code>MultipartHTTPPushUpdate</code> commands to treat the lack of a <code>MessageId</code> as no message \([https\://github\.com/ansible\-collections/community\.general/issues/7465](https\://github\.com/ansible\-collections/community\.general/issues/7465)\, [https\://github\.com/ansible\-collections/community\.general/pull/7471](https\://github\.com/ansible\-collections/community\.general/pull/7471)\)\.
* redfish\_info \- allow for a GET operation invoked by <code>GetUpdateStatus</code> to allow for an empty response body for cases where a service returns 204 No Content \([https\://github\.com/ansible\-collections/community\.general/issues/8003](https\://github\.com/ansible\-collections/community\.general/issues/8003)\)\.
* redfish\_info \- correct uncaught exception when attempting to retrieve <code>Chassis</code> information \([https\://github\.com/ansible\-collections/community\.general/pull/7952](https\://github\.com/ansible\-collections/community\.general/pull/7952)\)\.
* redhat\_subscription \- use the D\-Bus registration on RHEL 7 only on 7\.4 and
  greater\; older versions of RHEL 7 do not have it
  \([https\://github\.com/ansible\-collections/community\.general/issues/7622](https\://github\.com/ansible\-collections/community\.general/issues/7622)\,
  [https\://github\.com/ansible\-collections/community\.general/pull/7624](https\://github\.com/ansible\-collections/community\.general/pull/7624)\)\.
* riak \- support <code>riak admin</code> sub\-command in newer Riak KV versions beside the legacy <code>riak\-admin</code> main command \([https\://github\.com/ansible\-collections/community\.general/pull/8211](https\://github\.com/ansible\-collections/community\.general/pull/8211)\)\.
* statusio\_maintenance \- fix error caused by incorrectly formed API data payload\. Was raising \"Failed to create maintenance HTTP Error 400 Bad Request\" caused by bad data type for date/time and deprecated dict keys \([https\://github\.com/ansible\-collections/community\.general/pull/7754](https\://github\.com/ansible\-collections/community\.general/pull/7754)\)\.
* terraform \- fix multiline string handling in complex variables \([https\://github\.com/ansible\-collections/community\.general/pull/7535](https\://github\.com/ansible\-collections/community\.general/pull/7535)\)\.
* to\_ini filter plugin \- disabling interpolation of <code>ConfigParser</code> to allow converting values with a <code>\%</code> sign \([https\://github\.com/ansible\-collections/community\.general/issues/8183](https\://github\.com/ansible\-collections/community\.general/issues/8183)\, [https\://github\.com/ansible\-collections/community\.general/pull/8185](https\://github\.com/ansible\-collections/community\.general/pull/8185)\)\.
* xml \- make module work with lxml 5\.1\.1\, which removed some internals that the module was relying on \([https\://github\.com/ansible\-collections/community\.general/pull/8169](https\://github\.com/ansible\-collections/community\.general/pull/8169)\)\.

<a id="new-plugins-2"></a>
### New Plugins

<a id="become"></a>
#### Become

* community\.general\.run0 \- Systemd\'s run0\.

<a id="callback"></a>
#### Callback

* community\.general\.default\_without\_diff \- The default ansible callback without diff output\.
* community\.general\.timestamp \- Adds simple timestamp for each header\.

<a id="connection"></a>
#### Connection

* community\.general\.incus \- Run tasks in Incus instances via the Incus CLI\.

<a id="filter-2"></a>
#### Filter

* community\.general\.from\_ini \- Converts INI text input into a dictionary\.
* community\.general\.lists\_difference \- Difference of lists with a predictive order\.
* community\.general\.lists\_intersect \- Intersection of lists with a predictive order\.
* community\.general\.lists\_symmetric\_difference \- Symmetric Difference of lists with a predictive order\.
* community\.general\.lists\_union \- Union of lists with a predictive order\.
* community\.general\.to\_ini \- Converts a dictionary to the INI file format\.

<a id="lookup"></a>
#### Lookup

* community\.general\.github\_app\_access\_token \- Obtain short\-lived Github App Access tokens\.
* community\.general\.onepassword\_doc \- Fetch documents stored in 1Password\.

<a id="test-1"></a>
#### Test

* community\.general\.fqdn\_valid \- Validates fully\-qualified domain names against RFC 1123\.

<a id="new-modules-4"></a>
### New Modules

* community\.general\.consul\_acl\_bootstrap \- Bootstrap ACLs in Consul\.
* community\.general\.consul\_auth\_method \- Manipulate Consul auth methods\.
* community\.general\.consul\_binding\_rule \- Manipulate Consul binding rules\.
* community\.general\.consul\_token \- Manipulate Consul tokens\.
* community\.general\.django\_command \- Run Django admin commands\.
* community\.general\.dnf\_config\_manager \- Enable or disable dnf repositories using config\-manager\.
* community\.general\.git\_config\_info \- Read git configuration\.
* community\.general\.gitlab\_group\_access\_token \- Manages GitLab group access tokens\.
* community\.general\.gitlab\_issue \- Create\, update\, or delete GitLab issues\.
* community\.general\.gitlab\_label \- Creates/updates/deletes GitLab Labels belonging to project or group\.
* community\.general\.gitlab\_milestone \- Creates/updates/deletes GitLab Milestones belonging to project or group\.
* community\.general\.gitlab\_project\_access\_token \- Manages GitLab project access tokens\.
* community\.general\.keycloak\_client\_rolescope \- Allows administration of Keycloak client roles scope to restrict the usage of certain roles to a other specific client applications\.
* community\.general\.keycloak\_component\_info \- Retrive component info in Keycloak\.
* community\.general\.keycloak\_realm\_rolemapping \- Allows administration of Keycloak realm role mappings into groups with the Keycloak API\.
* community\.general\.nomad\_token \- Manage Nomad ACL tokens\.
* community\.general\.proxmox\_node\_info \- Retrieve information about one or more Proxmox VE nodes\.
* community\.general\.proxmox\_storage\_contents\_info \- List content from a Proxmox VE storage\.
* community\.general\.usb\_facts \- Allows listing information about USB devices\.
