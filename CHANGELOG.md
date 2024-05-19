# Community General Release Notes

**Topics**

- <a href="#v6-6-9">v6\.6\.9</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#security-fixes">Security Fixes</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v6-6-8">v6\.6\.8</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#security-fixes-1">Security Fixes</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v6-6-7">v6\.6\.7</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v6-6-6">v6\.6\.6</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v6-6-5">v6\.6\.5</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v6-6-4">v6\.6\.4</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes-5">Bugfixes</a>
- <a href="#v6-6-3">v6\.6\.3</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v6-6-2">v6\.6\.2</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v6-6-1">v6\.6\.1</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#bugfixes-8">Bugfixes</a>
- <a href="#v6-6-0">v6\.6\.0</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#bugfixes-9">Bugfixes</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v6-5-0">v6\.5\.0</a>
    - <a href="#release-summary-10">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#bugfixes-10">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#lookup">Lookup</a>
    - <a href="#new-modules-1">New Modules</a>
- <a href="#v6-4-0">v6\.4\.0</a>
    - <a href="#release-summary-11">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes-11">Bugfixes</a>
- <a href="#v6-3-0">v6\.3\.0</a>
    - <a href="#release-summary-12">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-12">Bugfixes</a>
    - <a href="#new-modules-2">New Modules</a>
- <a href="#v6-2-0">v6\.2\.0</a>
    - <a href="#release-summary-13">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#deprecated-features-2">Deprecated Features</a>
    - <a href="#bugfixes-13">Bugfixes</a>
- <a href="#v6-1-0">v6\.1\.0</a>
    - <a href="#release-summary-14">Release Summary</a>
    - <a href="#minor-changes-9">Minor Changes</a>
    - <a href="#deprecated-features-3">Deprecated Features</a>
    - <a href="#bugfixes-14">Bugfixes</a>
    - <a href="#new-modules-3">New Modules</a>
- <a href="#v6-0-1">v6\.0\.1</a>
    - <a href="#release-summary-15">Release Summary</a>
    - <a href="#bugfixes-15">Bugfixes</a>
- <a href="#v6-0-0">v6\.0\.0</a>
    - <a href="#release-summary-16">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes-10">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-1">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features-4">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#bugfixes-16">Bugfixes</a>
    - <a href="#new-plugins-1">New Plugins</a>
        - <a href="#filter">Filter</a>
        - <a href="#lookup-1">Lookup</a>
    - <a href="#new-modules-4">New Modules</a>
This changelog describes changes after version 5\.0\.0\.

<a id="v6-6-9"></a>
## v6\.6\.9

<a id="release-summary"></a>
### Release Summary

Maintenance release\.

This is the last 6\.x\.y release\. The 6\.x\.y release train is now effectively End of Life\.
Thanks to everyone who contributed to the community\.general 6\.x\.y releases\!

<a id="security-fixes"></a>
### Security Fixes

* keycloak\_identity\_provider \- the client secret was not correctly sanitized by the module\. The return values <code>proposed</code>\, <code>existing</code>\, and <code>end\_state</code>\, as well as the diff\, did contain the client secret unmasked \([https\://github\.com/ansible\-collections/community\.general/pull/8355](https\://github\.com/ansible\-collections/community\.general/pull/8355)\)\.

<a id="bugfixes"></a>
### Bugfixes

* inventory plugins \- add unsafe wrapper to avoid marking strings that do not contain <code>\{</code> or <code>\}</code> as unsafe\, to work around a bug in AWX \(\([https\://github\.com/ansible\-collections/community\.general/issues/8212](https\://github\.com/ansible\-collections/community\.general/issues/8212)\, [https\://github\.com/ansible\-collections/community\.general/pull/8225](https\://github\.com/ansible\-collections/community\.general/pull/8225)\)\.
* xml \- make module work with lxml 5\.1\.1\, which removed some internals that the module was relying on \([https\://github\.com/ansible\-collections/community\.general/pull/8169](https\://github\.com/ansible\-collections/community\.general/pull/8169)\)\.

<a id="v6-6-8"></a>
## v6\.6\.8

<a id="release-summary-1"></a>
### Release Summary

Security and bugfix release\.

<a id="security-fixes-1"></a>
### Security Fixes

* cobbler\, gitlab\_runners\, icinga2\, linode\, lxd\, nmap\, online\, opennebula\, proxmox\, scaleway\, stackpath\_compute\, virtualbox\, and xen\_orchestra inventory plugin \- make sure all data received from the remote servers is marked as unsafe\, so remote code execution by obtaining texts that can be evaluated as templates is not possible \([https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/](https\://www\.die\-welt\.net/2024/03/remote\-code\-execution\-in\-ansible\-dynamic\-inventory\-plugins/)\, [https\://github\.com/ansible\-collections/community\.general/pull/8098](https\://github\.com/ansible\-collections/community\.general/pull/8098)\)\.

<a id="bugfixes-1"></a>
### Bugfixes

* aix\_filesystem \- fix issue with empty list items in crfs logic and option order \([https\://github\.com/ansible\-collections/community\.general/pull/8052](https\://github\.com/ansible\-collections/community\.general/pull/8052)\)\.
* pacemaker\_cluster \- actually implement check mode\, which the module claims to support\. This means that until now the module also did changes in check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8081](https\://github\.com/ansible\-collections/community\.general/pull/8081)\)\.
* pam\_limits \- when the file does not exist\, do not create it in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/8050](https\://github\.com/ansible\-collections/community\.general/issues/8050)\, [https\://github\.com/ansible\-collections/community\.general/pull/8057](https\://github\.com/ansible\-collections/community\.general/pull/8057)\)\.

<a id="v6-6-7"></a>
## v6\.6\.7

<a id="release-summary-2"></a>
### Release Summary

Bugfix release\.

From now on\, community\.general 6\.x\.y will only receive major bugfixes and security fixes anymore\.

<a id="bugfixes-2"></a>
### Bugfixes

* composer \- fix impossible to run <code>working\_dir</code> dependent commands\. The module was throwing an error when trying to run a <code>working\_dir</code> dependent command\, because it tried to get the command help without passing the <code>working\_dir</code> \([https\://github\.com/ansible\-collections/community\.general/issues/3787](https\://github\.com/ansible\-collections/community\.general/issues/3787)\)\.
* github\_deploy\_key \- fix pagination behaviour causing a crash when only a single page of deploy keys exist \([https\://github\.com/ansible\-collections/community\.general/pull/7375](https\://github\.com/ansible\-collections/community\.general/pull/7375)\)\.
* gitlab\_group\_members \- fix gitlab constants call in <code>gitlab\_group\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_project\_members \- fix gitlab constants call in <code>gitlab\_project\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_protected\_branches \- fix gitlab constants call in <code>gitlab\_protected\_branches</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_user \- fix gitlab constants call in <code>gitlab\_user</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* lxc connection plugin \- properly evaluate options \([https\://github\.com/ansible\-collections/community\.general/pull/7369](https\://github\.com/ansible\-collections/community\.general/pull/7369)\)\.
* memset module utils \- make compatible with ansible\-core 2\.17 \([https\://github\.com/ansible\-collections/community\.general/pull/7379](https\://github\.com/ansible\-collections/community\.general/pull/7379)\)\.
* redhat\_subscription \- use the right D\-Bus options for the consumer type when
  registering a RHEL system older than 9 or a RHEL 9 system older than 9\.2
  and using <code>consumer\_type</code>
  \([https\://github\.com/ansible\-collections/community\.general/pull/7378](https\://github\.com/ansible\-collections/community\.general/pull/7378)\)\.
* selective callback plugin \- fix length of task name lines in output always being 3 characters longer than desired \([https\://github\.com/ansible\-collections/community\.general/pull/7374](https\://github\.com/ansible\-collections/community\.general/pull/7374)\)\.

<a id="v6-6-6"></a>
## v6\.6\.6

<a id="release-summary-3"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-3"></a>
### Bugfixes

* mail \- skip headers containing equals characters due to missing <code>maxsplit</code> on header key/value parsing \([https\://github\.com/ansible\-collections/community\.general/pull/7303](https\://github\.com/ansible\-collections/community\.general/pull/7303)\)\.
* onepassword \- fix KeyError exception when trying to access value of a field that is not filled out in OnePassword item \([https\://github\.com/ansible\-collections/community\.general/pull/7241](https\://github\.com/ansible\-collections/community\.general/pull/7241)\)\.
* terraform \- prevents <code>\-backend\-config</code> option double encapsulating with <code>shlex\_quote</code> function\. \([https\://github\.com/ansible\-collections/community\.general/pull/7301](https\://github\.com/ansible\-collections/community\.general/pull/7301)\)\.

<a id="v6-6-5"></a>
## v6\.6\.5

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes"></a>
### Minor Changes

* make \- allows <code>params</code> to be used without value \([https\://github\.com/ansible\-collections/community\.general/pull/7180](https\://github\.com/ansible\-collections/community\.general/pull/7180)\)\.
* pritunl module utils \- ensure <code>validate\_certs</code> parameter is honoured in all methods \([https\://github\.com/ansible\-collections/community\.general/pull/7156](https\://github\.com/ansible\-collections/community\.general/pull/7156)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* CmdRunner module utils \- does not attempt to resolve path if executable is a relative or absolute path \([https\://github\.com/ansible\-collections/community\.general/pull/7200](https\://github\.com/ansible\-collections/community\.general/pull/7200)\)\.
* lxc connection plugin \- now handles <code>remote\_addr</code> defaulting to <code>inventory\_hostname</code> correctly \([https\://github\.com/ansible\-collections/community\.general/pull/7104](https\://github\.com/ansible\-collections/community\.general/pull/7104)\)\.
* nsupdate \- fix a possible <code>list index out of range</code> exception \([https\://github\.com/ansible\-collections/community\.general/issues/836](https\://github\.com/ansible\-collections/community\.general/issues/836)\)\.
* oci\_utils module util \- fix inappropriate logical comparison expressions and makes them simpler\. The previous checks had logical short circuits \([https\://github\.com/ansible\-collections/community\.general/pull/7125](https\://github\.com/ansible\-collections/community\.general/pull/7125)\)\.
* pritunl module utils \- fix incorrect URL parameter for orgnization add method \([https\://github\.com/ansible\-collections/community\.general/pull/7161](https\://github\.com/ansible\-collections/community\.general/pull/7161)\)\.

<a id="v6-6-4"></a>
## v6\.6\.4

<a id="release-summary-5"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes-1"></a>
### Minor Changes

* redfish\_utils \- use <code>Controllers</code> key in redfish data to obtain Storage controllers properties \([https\://github\.com/ansible\-collections/community\.general/pull/7081](https\://github\.com/ansible\-collections/community\.general/pull/7081)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* bitwarden lookup plugin \- the plugin made assumptions about the structure of a Bitwarden JSON object which may have been broken by an update in the Bitwarden API\. Remove assumptions\, and allow queries for general fields such as <code>notes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7061](https\://github\.com/ansible\-collections/community\.general/pull/7061)\)\.
* cmd\_runner module utils \- when a parameter in <code>argument\_spec</code> has no type\, meaning it is implicitly a <code>str</code>\, <code>CmdRunner</code> would fail trying to find the <code>type</code> key in that dictionary \([https\://github\.com/ansible\-collections/community\.general/pull/6968](https\://github\.com/ansible\-collections/community\.general/pull/6968)\)\.
* ejabberd\_user \- module was failing to detect whether user was already created and/or password was changed \([https\://github\.com/ansible\-collections/community\.general/pull/7033](https\://github\.com/ansible\-collections/community\.general/pull/7033)\)\.
* ejabberd\_user \- provide meaningful error message when the <code>ejabberdctl</code> command is not found \([https\://github\.com/ansible\-collections/community\.general/pull/7028](https\://github\.com/ansible\-collections/community\.general/pull/7028)\, [https\://github\.com/ansible\-collections/community\.general/issues/6949](https\://github\.com/ansible\-collections/community\.general/issues/6949)\)\.
* oci\_utils module utils \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* proxmox module utils \- fix proxmoxer library version check \([https\://github\.com/ansible\-collections/community\.general/issues/6974](https\://github\.com/ansible\-collections/community\.general/issues/6974)\, [https\://github\.com/ansible\-collections/community\.general/issues/6975](https\://github\.com/ansible\-collections/community\.general/issues/6975)\, [https\://github\.com/ansible\-collections/community\.general/pull/6980](https\://github\.com/ansible\-collections/community\.general/pull/6980)\)\.
* proxmox\_kvm \- when <code>name</code> option is provided without <code>vmid</code> and VM with that name already exists then no new VM will be created \([https\://github\.com/ansible\-collections/community\.general/issues/6911](https\://github\.com/ansible\-collections/community\.general/issues/6911)\, [https\://github\.com/ansible\-collections/community\.general/pull/6981](https\://github\.com/ansible\-collections/community\.general/pull/6981)\)\.
* proxmox\_user\_info \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* rundeck \- fix <code>TypeError</code> on 404 API response \([https\://github\.com/ansible\-collections/community\.general/pull/6983](https\://github\.com/ansible\-collections/community\.general/pull/6983)\)\.

<a id="v6-6-3"></a>
## v6\.6\.3

<a id="release-summary-6"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes-2"></a>
### Minor Changes

* cobbler inventory plugin \- convert Ansible unicode strings to native Python unicode strings before passing user/password to XMLRPC client \([https\://github\.com/ansible\-collections/community\.general/pull/6923](https\://github\.com/ansible\-collections/community\.general/pull/6923)\)\.
* redfish\_info \- fix for <code>GetVolumeInventory</code>\, Controller name was getting populated incorrectly and duplicates were seen in the volumes retrieved \([https\://github\.com/ansible\-collections/community\.general/pull/6719](https\://github\.com/ansible\-collections/community\.general/pull/6719)\)\.

<a id="bugfixes-6"></a>
### Bugfixes

* datadog\_downtime \- presence of <code>rrule</code> param lead to the Datadog API returning Bad Request due to a missing recurrence type \([https\://github\.com/ansible\-collections/community\.general/pull/6811](https\://github\.com/ansible\-collections/community\.general/pull/6811)\)\.
* icinga2\_host \- fix a key error when updating an existing host \([https\://github\.com/ansible\-collections/community\.general/pull/6748](https\://github\.com/ansible\-collections/community\.general/pull/6748)\)\.
* ipa\_dnszone \- fix \'idnsallowsyncptr\' key error for reverse zone \([https\://github\.com/ansible\-collections/community\.general/pull/6906](https\://github\.com/ansible\-collections/community\.general/pull/6906)\, [https\://github\.com/ansible\-collections/community\.general/issues/6905](https\://github\.com/ansible\-collections/community\.general/issues/6905)\)\.
* locale\_gen \- now works for locales without the underscore character such as <code>C\.UTF\-8</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6774](https\://github\.com/ansible\-collections/community\.general/pull/6774)\, [https\://github\.com/ansible\-collections/community\.general/issues/5142](https\://github\.com/ansible\-collections/community\.general/issues/5142)\, [https\://github\.com/ansible\-collections/community\.general/issues/4305](https\://github\.com/ansible\-collections/community\.general/issues/4305)\)\.
* machinectl become plugin \- mark plugin as <code>require\_tty</code> to automatically disable pipelining\, with which this plugin is not compatible \([https\://github\.com/ansible\-collections/community\.general/issues/6932](https\://github\.com/ansible\-collections/community\.general/issues/6932)\, [https\://github\.com/ansible\-collections/community\.general/pull/6935](https\://github\.com/ansible\-collections/community\.general/pull/6935)\)\.
* nmcli \- fix support for empty list \(in compare and scrape\) \([https\://github\.com/ansible\-collections/community\.general/pull/6769](https\://github\.com/ansible\-collections/community\.general/pull/6769)\)\.
* openbsd\_pkg \- the pkg\_info\(1\) behavior has changed in OpenBSD \>7\.3\. The error message <code>Can\'t find</code> should not lead to an error case \([https\://github\.com/ansible\-collections/community\.general/pull/6785](https\://github\.com/ansible\-collections/community\.general/pull/6785)\)\.
* pacman \- module recognizes the output of <code>yay</code> running as <code>root</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6713](https\://github\.com/ansible\-collections/community\.general/pull/6713)\)\.
* proxmox \- fix error when a configuration had no <code>template</code> field \([https\://github\.com/ansible\-collections/community\.general/pull/6838](https\://github\.com/ansible\-collections/community\.general/pull/6838)\, [https\://github\.com/ansible\-collections/community\.general/issues/5372](https\://github\.com/ansible\-collections/community\.general/issues/5372)\)\.
* proxmox module utils \- add logic to detect whether an old Promoxer complains about the <code>token\_name</code> and <code>token\_value</code> parameters and provide a better error message when that happens \([https\://github\.com/ansible\-collections/community\.general/pull/6839](https\://github\.com/ansible\-collections/community\.general/pull/6839)\, [https\://github\.com/ansible\-collections/community\.general/issues/5371](https\://github\.com/ansible\-collections/community\.general/issues/5371)\)\.
* proxmox\_disk \- fix unable to create <code>cdrom</code> media due to <code>size</code> always being appended \([https\://github\.com/ansible\-collections/community\.general/pull/6770](https\://github\.com/ansible\-collections/community\.general/pull/6770)\)\.
* proxmox\_kvm \- <code>absent</code> state with <code>force</code> specified failed to stop the VM due to the <code>timeout</code> value not being passed to <code>stop\_vm</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6827](https\://github\.com/ansible\-collections/community\.general/pull/6827)\)\.
* redfish\_info \- fix <code>ListUsers</code> to not show empty account slots \([https\://github\.com/ansible\-collections/community\.general/issues/6771](https\://github\.com/ansible\-collections/community\.general/issues/6771)\, [https\://github\.com/ansible\-collections/community\.general/pull/6772](https\://github\.com/ansible\-collections/community\.general/pull/6772)\)\.
* refish\_utils module utils \- changing variable names to avoid issues occuring when fetching Volumes data \([https\://github\.com/ansible\-collections/community\.general/pull/6883](https\://github\.com/ansible\-collections/community\.general/pull/6883)\)\.
* rhsm\_repository \- when using the <code>purge</code> option\, the <code>repositories</code>
  dictionary element in the returned JSON is now properly updated according
  to the pruning operation
  \([https\://github\.com/ansible\-collections/community\.general/pull/6676](https\://github\.com/ansible\-collections/community\.general/pull/6676)\)\.

<a id="v6-6-2"></a>
## v6\.6\.2

<a id="release-summary-7"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-7"></a>
### Bugfixes

* csv module utils \- detects and remove unicode BOM markers from incoming CSV content \([https\://github\.com/ansible\-collections/community\.general/pull/6662](https\://github\.com/ansible\-collections/community\.general/pull/6662)\)\.
* gitlab\_group \- the module passed parameters to the API call even when not set\. The module is now filtering out <code>None</code> values to remediate this \([https\://github\.com/ansible\-collections/community\.general/pull/6712](https\://github\.com/ansible\-collections/community\.general/pull/6712)\)\.
* ini\_file \- fix a bug where the inactive options were not used when possible \([https\://github\.com/ansible\-collections/community\.general/pull/6575](https\://github\.com/ansible\-collections/community\.general/pull/6575)\)\.
* keycloak module utils \- fix <code>is\_struct\_included</code> handling of lists of lists/dictionaries \([https\://github\.com/ansible\-collections/community\.general/pull/6688](https\://github\.com/ansible\-collections/community\.general/pull/6688)\)\.
* keycloak module utils \- the function <code>get\_user\_by\_username</code> now return the user representation or <code>None</code> as stated in the documentation \([https\://github\.com/ansible\-collections/community\.general/pull/6758](https\://github\.com/ansible\-collections/community\.general/pull/6758)\)\.

<a id="v6-6-1"></a>
## v6\.6\.1

<a id="release-summary-8"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes-3"></a>
### Minor Changes

* dconf \- if <code>gi\.repository\.GLib</code> is missing\, try to respawn in a Python interpreter that has it \([https\://github\.com/ansible\-collections/community\.general/pull/6491](https\://github\.com/ansible\-collections/community\.general/pull/6491)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* deps module utils \- do not fail when dependency cannot be found \([https\://github\.com/ansible\-collections/community\.general/pull/6479](https\://github\.com/ansible\-collections/community\.general/pull/6479)\)\.
* nmcli \- fix bond option <code>xmit\_hash\_policy</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6527](https\://github\.com/ansible\-collections/community\.general/pull/6527)\)\.
* passwordstore lookup plugin \- make compatible with ansible\-core 2\.16 \([https\://github\.com/ansible\-collections/community\.general/pull/6447](https\://github\.com/ansible\-collections/community\.general/pull/6447)\)\.
* portage \- fix <code>changed\_use</code> and <code>newuse</code> not triggering rebuilds \([https\://github\.com/ansible\-collections/community\.general/issues/6008](https\://github\.com/ansible\-collections/community\.general/issues/6008)\, [https\://github\.com/ansible\-collections/community\.general/pull/6548](https\://github\.com/ansible\-collections/community\.general/pull/6548)\)\.
* portage \- update the logic for generating the emerge command arguments to ensure that <code>withbdeps\: false</code> results in a passing an <code>n</code> argument with the <code>\-\-with\-bdeps</code> emerge flag \([https\://github\.com/ansible\-collections/community\.general/issues/6451](https\://github\.com/ansible\-collections/community\.general/issues/6451)\, [https\://github\.com/ansible\-collections/community\.general/pull/6456](https\://github\.com/ansible\-collections/community\.general/pull/6456)\)\.
* proxmox\_tasks\_info \- remove <code>api\_user</code> \+ <code>api\_password</code> constraint from <code>required\_together</code> as it causes to require <code>api\_password</code> even when API token param is used \([https\://github\.com/ansible\-collections/community\.general/issues/6201](https\://github\.com/ansible\-collections/community\.general/issues/6201)\)\.
* puppet \- handling <code>noop</code> parameter was not working at all\, now it is has been fixed \([https\://github\.com/ansible\-collections/community\.general/issues/6452](https\://github\.com/ansible\-collections/community\.general/issues/6452)\, [https\://github\.com/ansible\-collections/community\.general/issues/6458](https\://github\.com/ansible\-collections/community\.general/issues/6458)\)\.
* terraform \- fix broken <code>warn\(\)</code> call \([https\://github\.com/ansible\-collections/community\.general/pull/6497](https\://github\.com/ansible\-collections/community\.general/pull/6497)\)\.
* xfs\_quota \- in case of a project quota\, the call to <code>xfs\_quota</code> did not initialize/reset the project \([https\://github\.com/ansible\-collections/community\.general/issues/5143](https\://github\.com/ansible\-collections/community\.general/issues/5143)\)\.
* zypper \- added handling of zypper exitcode 102\. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook \([https\://github\.com/ansible\-collections/community\.general/pull/6534](https\://github\.com/ansible\-collections/community\.general/pull/6534)\)\.

<a id="v6-6-0"></a>
## v6\.6\.0

<a id="release-summary-9"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* cpanm \- minor change\, use feature from <code>ModuleHelper</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6385](https\://github\.com/ansible\-collections/community\.general/pull/6385)\)\.
* dconf \- be forgiving about boolean values\: convert them to GVariant booleans automatically \([https\://github\.com/ansible\-collections/community\.general/pull/6206](https\://github\.com/ansible\-collections/community\.general/pull/6206)\)\.
* dconf \- minor refactoring improving parameters and dependencies validation \([https\://github\.com/ansible\-collections/community\.general/pull/6336](https\://github\.com/ansible\-collections/community\.general/pull/6336)\)\.
* deps module utils \- add function <code>failed\(\)</code> providing the ability to check the dependency check result without triggering an exception \([https\://github\.com/ansible\-collections/community\.general/pull/6383](https\://github\.com/ansible\-collections/community\.general/pull/6383)\)\.
* dig lookup plugin \- Support multiple domains to be queried as indicated in docs \([https\://github\.com/ansible\-collections/community\.general/pull/6334](https\://github\.com/ansible\-collections/community\.general/pull/6334)\)\.
* gitlab\_project \- add new option <code>topics</code> for adding topics to GitLab projects \([https\://github\.com/ansible\-collections/community\.general/pull/6278](https\://github\.com/ansible\-collections/community\.general/pull/6278)\)\.
* homebrew\_cask \- allows passing <code>\-\-greedy</code> option to <code>upgrade\_all</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6267](https\://github\.com/ansible\-collections/community\.general/pull/6267)\)\.
* idrac\_redfish\_command \- add <code>job\_id</code> to <code>CreateBiosConfigJob</code> response \([https\://github\.com/ansible\-collections/community\.general/issues/5603](https\://github\.com/ansible\-collections/community\.general/issues/5603)\)\.
* ipa\_hostgroup \- add <code>append</code> parameter for adding a new hosts to existing hostgroups without changing existing hostgroup members \([https\://github\.com/ansible\-collections/community\.general/pull/6203](https\://github\.com/ansible\-collections/community\.general/pull/6203)\)\.
* keycloak\_authentication \- add flow type option to sub flows to allow the creation of \'form\-flow\' sub flows like in Keycloak\'s built\-in registration flow \([https\://github\.com/ansible\-collections/community\.general/pull/6318](https\://github\.com/ansible\-collections/community\.general/pull/6318)\)\.
* mksysb \- improved the output of the module in case of errors \([https\://github\.com/ansible\-collections/community\.general/issues/6263](https\://github\.com/ansible\-collections/community\.general/issues/6263)\)\.
* nmap inventory plugin \- added environment variables for configure <code>address</code> and <code>exclude</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6351](https\://github\.com/ansible\-collections/community\.general/issues/6351)\)\.
* nmcli \- add <code>macvlan</code> connection type \([https\://github\.com/ansible\-collections/community\.general/pull/6312](https\://github\.com/ansible\-collections/community\.general/pull/6312)\)\.
* pipx \- add <code>system\_site\_packages</code> parameter to give application access to system\-wide packages \([https\://github\.com/ansible\-collections/community\.general/pull/6308](https\://github\.com/ansible\-collections/community\.general/pull/6308)\)\.
* pipx \- ensure <code>include\_injected</code> parameter works with <code>state\=upgrade</code> and <code>state\=latest</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6212](https\://github\.com/ansible\-collections/community\.general/pull/6212)\)\.
* puppet \- add new options <code>skip\_tags</code> to exclude certain tagged resources during a puppet agent or apply \([https\://github\.com/ansible\-collections/community\.general/pull/6293](https\://github\.com/ansible\-collections/community\.general/pull/6293)\)\.
* terraform \- remove state file check condition and error block\, because in the native implementation of terraform will not cause errors due to the non\-existent file \([https\://github\.com/ansible\-collections/community\.general/pull/6296](https\://github\.com/ansible\-collections/community\.general/pull/6296)\)\.
* udm\_dns\_record \- minor refactor to the code \([https\://github\.com/ansible\-collections/community\.general/pull/6382](https\://github\.com/ansible\-collections/community\.general/pull/6382)\)\.

<a id="bugfixes-9"></a>
### Bugfixes

* archive \- reduce RAM usage by generating CRC32 checksum over chunks \([https\://github\.com/ansible\-collections/community\.general/pull/6274](https\://github\.com/ansible\-collections/community\.general/pull/6274)\)\.
* flatpak \- fixes idempotency detection issues\. In some cases the module could fail to properly detect already existing Flatpaks because of a parameter witch only checks the installed apps \([https\://github\.com/ansible\-collections/community\.general/pull/6289](https\://github\.com/ansible\-collections/community\.general/pull/6289)\)\.
* icinga2\_host \- fix the data structure sent to Icinga to make use of host templates and template vars \([https\://github\.com/ansible\-collections/community\.general/pull/6286](https\://github\.com/ansible\-collections/community\.general/pull/6286)\)\.
* idrac\_redfish\_command \- allow user to specify <code>resource\_id</code> for <code>CreateBiosConfigJob</code> to specify an exact manager \([https\://github\.com/ansible\-collections/community\.general/issues/2090](https\://github\.com/ansible\-collections/community\.general/issues/2090)\)\.
* ini\_file \- make <code>section</code> parameter not required so it is possible to pass <code>null</code> as a value\. This only was possible in the past due to a bug in ansible\-core that now has been fixed \([https\://github\.com/ansible\-collections/community\.general/pull/6404](https\://github\.com/ansible\-collections/community\.general/pull/6404)\)\.
* keycloak \- improve error messages \([https\://github\.com/ansible\-collections/community\.general/pull/6318](https\://github\.com/ansible\-collections/community\.general/pull/6318)\)\.
* one\_vm \- fix syntax error when creating VMs with a more complex template \([https\://github\.com/ansible\-collections/community\.general/issues/6225](https\://github\.com/ansible\-collections/community\.general/issues/6225)\)\.
* pipx \- fixed handling of <code>install\_deps\=true</code> with <code>state\=latest</code> and <code>state\=upgrade</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6303](https\://github\.com/ansible\-collections/community\.general/pull/6303)\)\.
* redhat\_subscription \- do not use D\-Bus for registering when <code>environment</code> is specified\, so it possible to specify again the environment names for registering\, as the D\-Bus APIs work only with IDs \([https\://github\.com/ansible\-collections/community\.general/pull/6319](https\://github\.com/ansible\-collections/community\.general/pull/6319)\)\.
* redhat\_subscription \- try to unregister only when already registered when <code>force\_register</code> is specified \([https\://github\.com/ansible\-collections/community\.general/issues/6258](https\://github\.com/ansible\-collections/community\.general/issues/6258)\, [https\://github\.com/ansible\-collections/community\.general/pull/6259](https\://github\.com/ansible\-collections/community\.general/pull/6259)\)\.
* redhat\_subscription \- use the right D\-Bus options for environments when registering a CentOS Stream 8 system and using <code>environment</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6275](https\://github\.com/ansible\-collections/community\.general/pull/6275)\)\.
* rhsm\_release \- make <code>release</code> parameter not required so it is possible to pass <code>null</code> as a value\. This only was possible in the past due to a bug in ansible\-core that now has been fixed \([https\://github\.com/ansible\-collections/community\.general/pull/6401](https\://github\.com/ansible\-collections/community\.general/pull/6401)\)\.
* rundeck module utils \- fix errors caused by the API empty responses \([https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)
* rundeck\_acl\_policy \- fix <code>TypeError \- byte indices must be integers or slices\, not str</code> error caused by empty API response\. Update the module to use <code>module\_utils\.rundeck</code> functions \([https\://github\.com/ansible\-collections/community\.general/pull/5887](https\://github\.com/ansible\-collections/community\.general/pull/5887)\, [https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)\.
* rundeck\_project \- update the module to use <code>module\_utils\.rundeck</code> functions \([https\://github\.com/ansible\-collections/community\.general/issues/5742](https\://github\.com/ansible\-collections/community\.general/issues/5742)\) \([https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)
* snap\_alias \- module would only recognize snap names containing letter\, numbers or the underscore character\, failing to identify valid snap names such as <code>lxd\.lxc</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6361](https\://github\.com/ansible\-collections/community\.general/pull/6361)\)\.

<a id="new-modules"></a>
### New Modules

* btrfs\_info \- Query btrfs filesystem info
* btrfs\_subvolume \- Manage btrfs subvolumes
* ilo\_redfish\_command \- Manages Out\-Of\-Band controllers using Redfish APIs
* keycloak\_authz\_authorization\_scope \- Allows administration of Keycloak client authorization scopes via Keycloak API
* keycloak\_clientscope\_type \- Set the type of aclientscope in realm or client via Keycloak API

<a id="v6-5-0"></a>
## v6\.5\.0

<a id="release-summary-10"></a>
### Release Summary

Feature and bugfix release\.

<a id="minor-changes-5"></a>
### Minor Changes

* apt\_rpm \- adds <code>clean</code>\, <code>dist\_upgrade</code> and <code>update\_kernel</code>  parameters for clear caches\, complete upgrade system\, and upgrade kernel packages \([https\://github\.com/ansible\-collections/community\.general/pull/5867](https\://github\.com/ansible\-collections/community\.general/pull/5867)\)\.
* dconf \- parse GVariants for equality comparison when the Python module <code>gi\.repository</code> is available \([https\://github\.com/ansible\-collections/community\.general/pull/6049](https\://github\.com/ansible\-collections/community\.general/pull/6049)\)\.
* gitlab\_runner \- allow to register group runner \([https\://github\.com/ansible\-collections/community\.general/pull/3935](https\://github\.com/ansible\-collections/community\.general/pull/3935)\)\.
* jira \- add worklog functionality \([https\://github\.com/ansible\-collections/community\.general/issues/6209](https\://github\.com/ansible\-collections/community\.general/issues/6209)\, [https\://github\.com/ansible\-collections/community\.general/pull/6210](https\://github\.com/ansible\-collections/community\.general/pull/6210)\)\.
* ldap modules \- add <code>ca\_path</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/6185](https\://github\.com/ansible\-collections/community\.general/pull/6185)\)\.
* make \- add <code>command</code> return value to the module output \([https\://github\.com/ansible\-collections/community\.general/pull/6160](https\://github\.com/ansible\-collections/community\.general/pull/6160)\)\.
* nmap inventory plugin \- add new option <code>open</code> for only returning open ports \([https\://github\.com/ansible\-collections/community\.general/pull/6200](https\://github\.com/ansible\-collections/community\.general/pull/6200)\)\.
* nmap inventory plugin \- add new option <code>port</code> for port specific scan \([https\://github\.com/ansible\-collections/community\.general/pull/6165](https\://github\.com/ansible\-collections/community\.general/pull/6165)\)\.
* nmcli \- add <code>default</code> and <code>default\-or\-eui64</code> to the list of valid choices for <code>addr\_gen\_mode6</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/5974](https\://github\.com/ansible\-collections/community\.general/pull/5974)\)\.
* nmcli \- add support for <code>team\.runner\-fast\-rate</code> parameter for <code>team</code> connections \([https\://github\.com/ansible\-collections/community\.general/issues/6065](https\://github\.com/ansible\-collections/community\.general/issues/6065)\)\.
* openbsd\_pkg \- set <code>TERM</code> to <code>\'dumb\'</code> in <code>execute\_command\(\)</code> to make module less dependant on the <code>TERM</code> environment variable set on the Ansible controller \([https\://github\.com/ansible\-collections/community\.general/pull/6149](https\://github\.com/ansible\-collections/community\.general/pull/6149)\)\.
* pipx \- optional <code>install\_apps</code> parameter added to install applications from injected packages \([https\://github\.com/ansible\-collections/community\.general/pull/6198](https\://github\.com/ansible\-collections/community\.general/pull/6198)\)\.
* proxmox\_kvm \- add new <code>archive</code> parameter\. This is needed to create a VM from an archive \(backup\) \([https\://github\.com/ansible\-collections/community\.general/pull/6159](https\://github\.com/ansible\-collections/community\.general/pull/6159)\)\.
* redfish\_info \- adds commands to retrieve the HPE ThermalConfiguration and FanPercentMinimum settings from iLO \([https\://github\.com/ansible\-collections/community\.general/pull/6208](https\://github\.com/ansible\-collections/community\.general/pull/6208)\)\.
* redhat\_subscription \- credentials \(<code>username</code>\, <code>activationkey</code>\, and so on\) are required now only if a system needs to be registered\, or <code>force\_register</code> is specified \([https\://github\.com/ansible\-collections/community\.general/pull/5664](https\://github\.com/ansible\-collections/community\.general/pull/5664)\)\.
* redhat\_subscription \- the registration is done using the D\-Bus <code>rhsm</code> service instead of spawning a <code>subscription\-manager register</code> command\, if possible\; this avoids passing plain\-text credentials as arguments to <code>subscription\-manager register</code>\, which can be seen while that command runs \([https\://github\.com/ansible\-collections/community\.general/pull/6122](https\://github\.com/ansible\-collections/community\.general/pull/6122)\)\.
* ssh\_config \- add <code>proxyjump</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5970](https\://github\.com/ansible\-collections/community\.general/pull/5970)\)\.
* ssh\_config \- vendored StormSSH\'s config parser to avoid having to install StormSSH to use the module \([https\://github\.com/ansible\-collections/community\.general/pull/6117](https\://github\.com/ansible\-collections/community\.general/pull/6117)\)\.
* znode module \- optional <code>use\_tls</code> parameter added for encrypted communication \([https\://github\.com/ansible\-collections/community\.general/issues/6154](https\://github\.com/ansible\-collections/community\.general/issues/6154)\)\.

<a id="bugfixes-10"></a>
### Bugfixes

* archive \- avoid deprecated exception class on Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/6180](https\://github\.com/ansible\-collections/community\.general/pull/6180)\)\.
* gitlab\_runner \- fix <code>KeyError</code> on runner creation and update \([https\://github\.com/ansible\-collections/community\.general/issues/6112](https\://github\.com/ansible\-collections/community\.general/issues/6112)\)\.
* influxdb\_user \- fix running in check mode when the user does not exist yet \([https\://github\.com/ansible\-collections/community\.general/pull/6111](https\://github\.com/ansible\-collections/community\.general/pull/6111)\)\.
* interfaces\_file \- fix reading options in lines not starting with a space \([https\://github\.com/ansible\-collections/community\.general/issues/6120](https\://github\.com/ansible\-collections/community\.general/issues/6120)\)\.
* jail connection plugin \- add <code>inventory\_hostname</code> to vars under <code>remote\_addr</code>\. This is needed for compatibility with ansible\-core 2\.13 \([https\://github\.com/ansible\-collections/community\.general/pull/6118](https\://github\.com/ansible\-collections/community\.general/pull/6118)\)\.
* memset \- fix memset urlerror handling \([https\://github\.com/ansible\-collections/community\.general/pull/6114](https\://github\.com/ansible\-collections/community\.general/pull/6114)\)\.
* nmcli \- fixed idempotency issue for bridge connections\. Module forced default value of <code>bridge\.priority</code> to nmcli if not set\; if <code>bridge\.stp</code> is disabled nmcli ignores it and keep default \([https\://github\.com/ansible\-collections/community\.general/issues/3216](https\://github\.com/ansible\-collections/community\.general/issues/3216)\, [https\://github\.com/ansible\-collections/community\.general/issues/4683](https\://github\.com/ansible\-collections/community\.general/issues/4683)\)\.
* nmcli \- fixed idempotency issue when module params is set to <code>may\_fail4\=false</code> and <code>method4\=disabled</code>\; in this case nmcli ignores change and keeps their own default value <code>yes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6106](https\://github\.com/ansible\-collections/community\.general/pull/6106)\)\.
* nmcli \- implemented changing mtu value on vlan interfaces \([https\://github\.com/ansible\-collections/community\.general/issues/4387](https\://github\.com/ansible\-collections/community\.general/issues/4387)\)\.
* opkg \- fixes bug when using <code>update\_cache\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6004](https\://github\.com/ansible\-collections/community\.general/issues/6004)\)\.
* redhat\_subscription\, rhsm\_release\, rhsm\_repository \- cleanly fail when not running as root\, rather than hanging on an interactive <code>console\-helper</code> prompt\; they all interact with <code>subscription\-manager</code>\, which already requires to be run as root \([https\://github\.com/ansible\-collections/community\.general/issues/734](https\://github\.com/ansible\-collections/community\.general/issues/734)\, [https\://github\.com/ansible\-collections/community\.general/pull/6211](https\://github\.com/ansible\-collections/community\.general/pull/6211)\)\.
* xenorchestra inventory plugin \- fix failure to receive objects from server due to not checking the id of the response \([https\://github\.com/ansible\-collections/community\.general/pull/6227](https\://github\.com/ansible\-collections/community\.general/pull/6227)\)\.
* yarn \- fix <code>global\=true</code> to not fail when <em class="title-reference">executable</em> wasn\'t specified \([https\://github\.com/ansible\-collections/community\.general/pull/6132](https\://github\.com/ansible\-collections/community\.general/pull/6132)\)
* yarn \- fixes bug where yarn module tasks would fail when warnings were emitted from Yarn\. The <code>yarn\.list</code> method was not filtering out warnings \([https\://github\.com/ansible\-collections/community\.general/issues/6127](https\://github\.com/ansible\-collections/community\.general/issues/6127)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="lookup"></a>
#### Lookup

* merge\_variables \- merge variables with a certain suffix

<a id="new-modules-1"></a>
### New Modules

* kdeconfig \- Manage KDE configuration files

<a id="v6-4-0"></a>
## v6\.4\.0

<a id="release-summary-11"></a>
### Release Summary

Regular feature and bugfix release\.

<a id="minor-changes-6"></a>
### Minor Changes

* dnsimple \- set custom User\-Agent for API requests to DNSimple \([https\://github\.com/ansible\-collections/community\.general/pull/5927](https\://github\.com/ansible\-collections/community\.general/pull/5927)\)\.
* flatpak\_remote \- add new boolean option <code>enabled</code>\. It controls\, whether the remote is enabled or not \([https\://github\.com/ansible\-collections/community\.general/pull/5926](https\://github\.com/ansible\-collections/community\.general/pull/5926)\)\.
* gitlab\_project \- add <code>releases\_access\_level</code>\, <code>environments\_access\_level</code>\, <code>feature\_flags\_access\_level</code>\, <code>infrastructure\_access\_level</code>\, <code>monitor\_access\_level</code>\, and <code>security\_and\_compliance\_access\_level</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5986](https\://github\.com/ansible\-collections/community\.general/pull/5986)\)\.
* jc filter plugin \- added the ability to use parser plugins \([https\://github\.com/ansible\-collections/community\.general/pull/6043](https\://github\.com/ansible\-collections/community\.general/pull/6043)\)\.
* keycloak\_group \- add new optional module parameter <code>parents</code> to properly handle keycloak subgroups \([https\://github\.com/ansible\-collections/community\.general/pull/5814](https\://github\.com/ansible\-collections/community\.general/pull/5814)\)\.
* keycloak\_user\_federation \- make <code>org\.keycloak\.storage\.ldap\.mappers\.LDAPStorageMapper</code> the default value for mappers <code>providerType</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5863](https\://github\.com/ansible\-collections/community\.general/pull/5863)\)\.
* ldap modules \- add <code>xorder\_discovery</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/6045](https\://github\.com/ansible\-collections/community\.general/issues/6045)\, [https\://github\.com/ansible\-collections/community\.general/pull/6109](https\://github\.com/ansible\-collections/community\.general/pull/6109)\)\.
* lxd\_container \- add diff and check mode \([https\://github\.com/ansible\-collections/community\.general/pull/5866](https\://github\.com/ansible\-collections/community\.general/pull/5866)\)\.
* mattermost\, rocketchat\, slack \- replace missing default favicon with docs\.ansible\.com favicon \([https\://github\.com/ansible\-collections/community\.general/pull/5928](https\://github\.com/ansible\-collections/community\.general/pull/5928)\)\.
* modprobe \- add <code>persistent</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/4028](https\://github\.com/ansible\-collections/community\.general/issues/4028)\, [https\://github\.com/ansible\-collections/community\.general/pull/542](https\://github\.com/ansible\-collections/community\.general/pull/542)\)\.
* osx\_defaults \- include stderr in error messages \([https\://github\.com/ansible\-collections/community\.general/pull/6011](https\://github\.com/ansible\-collections/community\.general/pull/6011)\)\.
* proxmox \- suppress urllib3 <code>InsecureRequestWarnings</code> when <code>validate\_certs</code> option is <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5931](https\://github\.com/ansible\-collections/community\.general/pull/5931)\)\.
* redfish\_command \- adding <code>EnableSecureBoot</code> functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5899](https\://github\.com/ansible\-collections/community\.general/pull/5899)\)\.
* redfish\_command \- adding <code>VerifyBiosAttributes</code> functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5900](https\://github\.com/ansible\-collections/community\.general/pull/5900)\)\.
* sefcontext \- add support for path substitutions \([https\://github\.com/ansible\-collections/community\.general/issues/1193](https\://github\.com/ansible\-collections/community\.general/issues/1193)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* gitlab\_runner \- the option <code>access\_level</code> will lose its default value in community\.general 8\.0\.0\. From that version on\, you have set this option to <code>ref\_protected</code> explicitly\, if you want to have a protected runner \([https\://github\.com/ansible\-collections/community\.general/issues/5925](https\://github\.com/ansible\-collections/community\.general/issues/5925)\)\.

<a id="bugfixes-11"></a>
### Bugfixes

* cartesian and flattened lookup plugins \- adjust to parameter deprecation in ansible\-core 2\.14\'s <code>listify\_lookup\_plugin\_terms</code> helper function \([https\://github\.com/ansible\-collections/community\.general/pull/6074](https\://github\.com/ansible\-collections/community\.general/pull/6074)\)\.
* cloudflare\_dns \- fixed the idempotency for SRV DNS records \([https\://github\.com/ansible\-collections/community\.general/pull/5972](https\://github\.com/ansible\-collections/community\.general/pull/5972)\)\.
* cloudflare\_dns \- fixed the possiblity of setting a root\-level SRV DNS record \([https\://github\.com/ansible\-collections/community\.general/pull/5972](https\://github\.com/ansible\-collections/community\.general/pull/5972)\)\.
* github\_webhook \- fix always changed state when no secret is provided \([https\://github\.com/ansible\-collections/community\.general/pull/5994](https\://github\.com/ansible\-collections/community\.general/pull/5994)\)\.
* jenkins\_plugin \- fix error due to undefined variable when updates file is not downloaded \([https\://github\.com/ansible\-collections/community\.general/pull/6100](https\://github\.com/ansible\-collections/community\.general/pull/6100)\)\.
* keycloak\_client \- fix accidental replacement of value for attribute <code>saml\.signing\.private\.key</code> with <code>no\_log</code> in wrong contexts \([https\://github\.com/ansible\-collections/community\.general/pull/5934](https\://github\.com/ansible\-collections/community\.general/pull/5934)\)\.
* lxd\_\* modules\, lxd inventory plugin \- fix TLS/SSL certificate validation problems by using the correct purpose when creating the TLS context \([https\://github\.com/ansible\-collections/community\.general/issues/5616](https\://github\.com/ansible\-collections/community\.general/issues/5616)\, [https\://github\.com/ansible\-collections/community\.general/pull/6034](https\://github\.com/ansible\-collections/community\.general/pull/6034)\)\.
* nmcli \- fix change handling of values specified as an integer 0 \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- fix failure to handle WIFI settings when connection type not specified \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- fix improper detection of changes to <code>wifi\.wake\-on\-wlan</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- order is significant for lists of addresses \([https\://github\.com/ansible\-collections/community\.general/pull/6048](https\://github\.com/ansible\-collections/community\.general/pull/6048)\)\.
* onepassword lookup plugin \- Changed to ignore errors from \"op account get\" calls\. Previously\, errors would prevent auto\-signin code from executing \([https\://github\.com/ansible\-collections/community\.general/pull/5942](https\://github\.com/ansible\-collections/community\.general/pull/5942)\)\.
* terraform and timezone \- slight refactoring to avoid linter reporting potentially undefined variables \([https\://github\.com/ansible\-collections/community\.general/pull/5933](https\://github\.com/ansible\-collections/community\.general/pull/5933)\)\.
* various plugins and modules \- remove unnecessary imports \([https\://github\.com/ansible\-collections/community\.general/pull/5940](https\://github\.com/ansible\-collections/community\.general/pull/5940)\)\.
* yarn \- fix <code>global\=true</code> to check for the configured global folder instead of assuming the default \([https\://github\.com/ansible\-collections/community\.general/pull/5829](https\://github\.com/ansible\-collections/community\.general/pull/5829)\)
* yarn \- fix <code>state\=absent</code> not working with <code>global\=true</code> when the package does not include a binary \([https\://github\.com/ansible\-collections/community\.general/pull/5829](https\://github\.com/ansible\-collections/community\.general/pull/5829)\)
* yarn \- fix <code>state\=latest</code> not working with <code>global\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/5712](https\://github\.com/ansible\-collections/community\.general/issues/5712)\)\.
* zfs\_delegate\_admin \- zfs allow output can now be parsed when uids/gids are not known to the host system \([https\://github\.com/ansible\-collections/community\.general/pull/5943](https\://github\.com/ansible\-collections/community\.general/pull/5943)\)\.
* zypper \- make package managing work on readonly filesystem of openSUSE MicroOS \([https\://github\.com/ansible\-collections/community\.general/pull/5615](https\://github\.com/ansible\-collections/community\.general/pull/5615)\)\.

<a id="v6-3-0"></a>
## v6\.3\.0

<a id="release-summary-12"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-7"></a>
### Minor Changes

* apache2\_module \- add module argument <code>warn\_mpm\_absent</code> to control whether warning are raised in some edge cases \([https\://github\.com/ansible\-collections/community\.general/pull/5793](https\://github\.com/ansible\-collections/community\.general/pull/5793)\)\.
* bitwarden lookup plugin \- can now retrieve secrets from custom fields \([https\://github\.com/ansible\-collections/community\.general/pull/5694](https\://github\.com/ansible\-collections/community\.general/pull/5694)\)\.
* bitwarden lookup plugin \- implement filtering results by <code>collection\_id</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5849](https\://github\.com/ansible\-collections/community\.general/issues/5849)\)\.
* dig lookup plugin \- support CAA record type \([https\://github\.com/ansible\-collections/community\.general/pull/5913](https\://github\.com/ansible\-collections/community\.general/pull/5913)\)\.
* gitlab\_project \- add <code>builds\_access\_level</code>\, <code>container\_registry\_access\_level</code> and <code>forking\_access\_level</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5706](https\://github\.com/ansible\-collections/community\.general/pull/5706)\)\.
* gitlab\_runner \- add new boolean option <code>access\_level\_on\_creation</code>\. It controls\, whether the value of <code>access\_level</code> is used for runner registration or not\. The option <code>access\_level</code> has been ignored on registration so far and was only used on updates \([https\://github\.com/ansible\-collections/community\.general/issues/5907](https\://github\.com/ansible\-collections/community\.general/issues/5907)\, [https\://github\.com/ansible\-collections/community\.general/pull/5908](https\://github\.com/ansible\-collections/community\.general/pull/5908)\)\.
* ilo\_redfish\_utils module utils \- change implementation of DNS Server IP and NTP Server IP update \([https\://github\.com/ansible\-collections/community\.general/pull/5804](https\://github\.com/ansible\-collections/community\.general/pull/5804)\)\.
* ipa\_group \- allow to add and remove external users with the <code>external\_user</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5897](https\://github\.com/ansible\-collections/community\.general/pull/5897)\)\.
* iptables\_state \- minor refactoring within the module \([https\://github\.com/ansible\-collections/community\.general/pull/5844](https\://github\.com/ansible\-collections/community\.general/pull/5844)\)\.
* one\_vm \- add a new <code>updateconf</code> option which implements the <code>one\.vm\.updateconf</code> API call \([https\://github\.com/ansible\-collections/community\.general/pull/5812](https\://github\.com/ansible\-collections/community\.general/pull/5812)\)\.
* opkg \- refactored module to use <code>CmdRunner</code> for executing <code>opkg</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5718](https\://github\.com/ansible\-collections/community\.general/pull/5718)\)\.
* redhat\_subscription \- adds <code>token</code> parameter for subscription\-manager authentication using Red Hat API token \([https\://github\.com/ansible\-collections/community\.general/pull/5725](https\://github\.com/ansible\-collections/community\.general/pull/5725)\)\.
* snap \- minor refactor when executing module \([https\://github\.com/ansible\-collections/community\.general/pull/5773](https\://github\.com/ansible\-collections/community\.general/pull/5773)\)\.
* snap\_alias \- refactored module to use <code>CmdRunner</code> to execute <code>snap</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5486](https\://github\.com/ansible\-collections/community\.general/pull/5486)\)\.
* sudoers \- add <code>setenv</code> parameters to support passing environment variables via sudo\. \([https\://github\.com/ansible\-collections/community\.general/pull/5883](https\://github\.com/ansible\-collections/community\.general/pull/5883)\)

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* ModuleHelper module utils \- when the module sets output variables named <code>msg</code>\, <code>exception</code>\, <code>output</code>\, <code>vars</code>\, or <code>changed</code>\, the actual output will prefix those names with <code>\_</code> \(underscore symbol\) only when they clash with output variables generated by ModuleHelper itself\, which only occurs when handling exceptions\. Please note that this breaking change does not require a new major release since before this release\, it was not possible to add such variables to the output [due to a bug](https\://github\.com/ansible\-collections/community\.general/pull/5755) \([https\://github\.com/ansible\-collections/community\.general/pull/5765](https\://github\.com/ansible\-collections/community\.general/pull/5765)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* consul \- deprecate using parameters unused for <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5772](https\://github\.com/ansible\-collections/community\.general/pull/5772)\)\.
* gitlab\_runner \- the default of the new option <code>access\_level\_on\_creation</code> will change from <code>false</code> to <code>true</code> in community\.general 7\.0\.0\. This will cause <code>access\_level</code> to be used during runner registration as well\, and not only during updates \([https\://github\.com/ansible\-collections/community\.general/pull/5908](https\://github\.com/ansible\-collections/community\.general/pull/5908)\)\.

<a id="bugfixes-12"></a>
### Bugfixes

* ModuleHelper \- fix bug when adjusting the name of reserved output variables \([https\://github\.com/ansible\-collections/community\.general/pull/5755](https\://github\.com/ansible\-collections/community\.general/pull/5755)\)\.
* alternatives \- support subcommands on Fedora 37\, which uses <code>follower</code> instead of <code>slave</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5794](https\://github\.com/ansible\-collections/community\.general/pull/5794)\)\.
* bitwarden lookup plugin \- clarify what to do\, if the bitwarden vault is not unlocked \([https\://github\.com/ansible\-collections/community\.general/pull/5811](https\://github\.com/ansible\-collections/community\.general/pull/5811)\)\.
* dig lookup plugin \- correctly handle DNSKEY record type\'s <code>algorithm</code> field \([https\://github\.com/ansible\-collections/community\.general/pull/5914](https\://github\.com/ansible\-collections/community\.general/pull/5914)\)\.
* gem \- fix force parameter not being passed to gem command when uninstalling \([https\://github\.com/ansible\-collections/community\.general/pull/5822](https\://github\.com/ansible\-collections/community\.general/pull/5822)\)\.
* gem \- fix hang due to interactive prompt for confirmation on specific version uninstall \([https\://github\.com/ansible\-collections/community\.general/pull/5751](https\://github\.com/ansible\-collections/community\.general/pull/5751)\)\.
* gitlab\_deploy\_key \- also update <code>title</code> and not just <code>can\_push</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5888](https\://github\.com/ansible\-collections/community\.general/pull/5888)\)\.
* keycloak\_user\_federation \- fixes federation creation issue\. When a new federation was created and at the same time a default / standard mapper was also changed / updated the creation process failed as a bad None set variable led to a bad malformed url request \([https\://github\.com/ansible\-collections/community\.general/pull/5750](https\://github\.com/ansible\-collections/community\.general/pull/5750)\)\.
* keycloak\_user\_federation \- fixes idempotency detection issues\. In some cases the module could fail to properly detect already existing user federations because of a buggy seemingly superflous extra query parameter \([https\://github\.com/ansible\-collections/community\.general/pull/5732](https\://github\.com/ansible\-collections/community\.general/pull/5732)\)\.
* loganalytics callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* logdna callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* logstash callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* nsupdate \- fix zone lookup\. The SOA record for an existing zone is returned as an answer RR and not as an authority RR \([https\://github\.com/ansible\-collections/community\.general/issues/5817](https\://github\.com/ansible\-collections/community\.general/issues/5817)\, [https\://github\.com/ansible\-collections/community\.general/pull/5818](https\://github\.com/ansible\-collections/community\.general/pull/5818)\)\.
* proxmox\_disk \- fixed issue with read timeout on import action \([https\://github\.com/ansible\-collections/community\.general/pull/5803](https\://github\.com/ansible\-collections/community\.general/pull/5803)\)\.
* redfish\_utils \- removed basic auth HTTP header when performing a GET on the service root resource and when performing a POST to the session collection \([https\://github\.com/ansible\-collections/community\.general/issues/5886](https\://github\.com/ansible\-collections/community\.general/issues/5886)\)\.
* splunk callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* sumologic callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* syslog\_json callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* terraform \- fix <code>current</code> workspace never getting appended to the <code>all</code> key in the <code>workspace\_ctf</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/5735](https\://github\.com/ansible\-collections/community\.general/pull/5735)\)\.
* terraform \- fix <code>terraform init</code> failure when there are multiple workspaces on the remote backend and when <code>default</code> workspace is missing by setting <code>TF\_WORKSPACE</code> environmental variable to the value of <code>workspace</code> when used \([https\://github\.com/ansible\-collections/community\.general/pull/5735](https\://github\.com/ansible\-collections/community\.general/pull/5735)\)\.
* terraform module \- disable ANSI escape sequences during validation phase \([https\://github\.com/ansible\-collections/community\.general/pull/5843](https\://github\.com/ansible\-collections/community\.general/pull/5843)\)\.
* xml \- fixed a bug where empty <code>children</code> list would not be set \([https\://github\.com/ansible\-collections/community\.general/pull/5808](https\://github\.com/ansible\-collections/community\.general/pull/5808)\)\.

<a id="new-modules-2"></a>
### New Modules

* ocapi\_command \- Manages Out\-Of\-Band controllers using Open Composable API \(OCAPI\)
* ocapi\_info \- Manages Out\-Of\-Band controllers using Open Composable API \(OCAPI\)

<a id="v6-2-0"></a>
## v6\.2\.0

<a id="release-summary-13"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-8"></a>
### Minor Changes

* opkg \- allow installing a package in a certain version \([https\://github\.com/ansible\-collections/community\.general/pull/5688](https\://github\.com/ansible\-collections/community\.general/pull/5688)\)\.
* proxmox \- added new module parameter <code>tags</code> for use with PVE 7\+ \([https\://github\.com/ansible\-collections/community\.general/pull/5714](https\://github\.com/ansible\-collections/community\.general/pull/5714)\)\.
* puppet \- refactored module to use <code>CmdRunner</code> for executing <code>puppet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5612](https\://github\.com/ansible\-collections/community\.general/pull/5612)\)\.
* redhat\_subscription \- add a <code>server\_proxy\_scheme</code> parameter to configure the scheme for the proxy server \([https\://github\.com/ansible\-collections/community\.general/pull/5662](https\://github\.com/ansible\-collections/community\.general/pull/5662)\)\.
* ssh\_config \- refactor code to module util to fix sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5720](https\://github\.com/ansible\-collections/community\.general/pull/5720)\)\.
* sudoers \- adds <code>host</code> parameter for setting hostname restrictions in sudoers rules \([https\://github\.com/ansible\-collections/community\.general/issues/5702](https\://github\.com/ansible\-collections/community\.general/issues/5702)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* manageiq\_policies \- deprecate <code>state\=list</code> in favour of using <code>community\.general\.manageiq\_policies\_info</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5721](https\://github\.com/ansible\-collections/community\.general/pull/5721)\)\.
* rax \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_cbs \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_cbs\_attachments \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_cdb \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_cdb\_database \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_cdb\_user \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_clb \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_clb\_nodes \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_clb\_ssl \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_dns \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_dns\_record \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_facts \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_files \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_files\_objects \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_identity \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_keypair \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_meta \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_mon\_alarm \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_mon\_check \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_mon\_entity \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_mon\_notification \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_mon\_notification\_plan \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_network \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_queue \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_scaling\_group \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.
* rax\_scaling\_policy \- module relies on deprecates library <code>pyrax</code>\. Unless maintainers step up to work on the module\, it will be marked as deprecated in community\.general 7\.0\.0 and removed in version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5733](https\://github\.com/ansible\-collections/community\.general/pull/5733)\)\.

<a id="bugfixes-13"></a>
### Bugfixes

* ansible\_galaxy\_install \- set default to raise exception if command\'s return code is different from zero \([https\://github\.com/ansible\-collections/community\.general/pull/5680](https\://github\.com/ansible\-collections/community\.general/pull/5680)\)\.
* ansible\_galaxy\_install \- try <code>C\.UTF\-8</code> and then fall back to <code>en\_US\.UTF\-8</code> before failing \([https\://github\.com/ansible\-collections/community\.general/pull/5680](https\://github\.com/ansible\-collections/community\.general/pull/5680)\)\.
* gitlab\_group\_variables \- fix dropping variables accidentally when GitLab introduced new properties \([https\://github\.com/ansible\-collections/community\.general/pull/5667](https\://github\.com/ansible\-collections/community\.general/pull/5667)\)\.
* gitlab\_project\_variables \- fix dropping variables accidentally when GitLab introduced new properties \([https\://github\.com/ansible\-collections/community\.general/pull/5667](https\://github\.com/ansible\-collections/community\.general/pull/5667)\)\.
* lxc\_container \- fix the arguments of the lxc command which broke the creation and cloning of containers \([https\://github\.com/ansible\-collections/community\.general/issues/5578](https\://github\.com/ansible\-collections/community\.general/issues/5578)\)\.
* opkg \- fix issue that <code>force\=reinstall</code> would not reinstall an existing package \([https\://github\.com/ansible\-collections/community\.general/pull/5705](https\://github\.com/ansible\-collections/community\.general/pull/5705)\)\.
* proxmox\_disk \- fixed possible issues with redundant <code>vmid</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5672](https\://github\.com/ansible\-collections/community\.general/pull/5672)\)\.
* proxmox\_nic \- fixed possible issues with redundant <code>vmid</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5672](https\://github\.com/ansible\-collections/community\.general/pull/5672)\)\.
* unixy callback plugin \- fix typo introduced when updating to use Ansible\'s configuration manager for handling options \([https\://github\.com/ansible\-collections/community\.general/issues/5600](https\://github\.com/ansible\-collections/community\.general/issues/5600)\)\.

<a id="v6-1-0"></a>
## v6\.1\.0

<a id="release-summary-14"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-9"></a>
### Minor Changes

* cmd\_runner module utils \- <code>cmd\_runner\_fmt\.as\_bool\(\)</code> can now take an extra parameter to format when value is false \([https\://github\.com/ansible\-collections/community\.general/pull/5647](https\://github\.com/ansible\-collections/community\.general/pull/5647)\)\.
* gconftool2 \- refactor using <code>ModuleHelper</code> and <code>CmdRunner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5545](https\://github\.com/ansible\-collections/community\.general/pull/5545)\)\.
* java\_certs \- add more detailed error output when extracting certificate from PKCS12 fails \([https\://github\.com/ansible\-collections/community\.general/pull/5550](https\://github\.com/ansible\-collections/community\.general/pull/5550)\)\.
* jenkins\_plugin \- refactor code to module util to fix sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5565](https\://github\.com/ansible\-collections/community\.general/pull/5565)\)\.
* lxd\_project \- refactored code out to module utils to clear sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5549](https\://github\.com/ansible\-collections/community\.general/pull/5549)\)\.
* nmap inventory plugin \- add new options <code>udp\_scan</code>\, <code>icmp\_timestamp</code>\, and <code>dns\_resolve</code> for different types of scans \([https\://github\.com/ansible\-collections/community\.general/pull/5566](https\://github\.com/ansible\-collections/community\.general/pull/5566)\)\.
* rax\_scaling\_group \- refactored out code to the <code>rax</code> module utils to clear the sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5563](https\://github\.com/ansible\-collections/community\.general/pull/5563)\)\.
* redfish\_command \- add <code>PerformRequestedOperations</code> command to perform any operations necessary to continue the update flow \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_command \- add <code>update\_apply\_time</code> to <code>SimpleUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/3910](https\://github\.com/ansible\-collections/community\.general/issues/3910)\)\.
* redfish\_command \- add <code>update\_status</code> to output of <code>SimpleUpdate</code> command to allow a user monitor the update in progress \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_info \- add <code>GetUpdateStatus</code> command to check the progress of a previous update request \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_utils module utils \- added PUT \(<code>put\_request\(\)</code>\) functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5490](https\://github\.com/ansible\-collections/community\.general/pull/5490)\)\.
* slack \- add option <code>prepend\_hash</code> which allows to control whether a <code>\#</code> is prepended to <code>channel\_id</code>\. The current behavior \(value <code>auto</code>\) is to prepend <code>\#</code> unless some specific prefixes are found\. That list of prefixes is incomplete\, and there does not seem to exist a documented condition on when exactly <code>\#</code> must not be prepended\. We recommend to explicitly set <code>prepend\_hash\=always</code> or <code>prepend\_hash\=never</code> to avoid any ambiguity \([https\://github\.com/ansible\-collections/community\.general/pull/5629](https\://github\.com/ansible\-collections/community\.general/pull/5629)\)\.
* spotinst\_aws\_elastigroup \- add <code>elements</code> attribute when missing in <code>list</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5553](https\://github\.com/ansible\-collections/community\.general/pull/5553)\)\.
* ssh\_config \- add <code>host\_key\_algorithms</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5605](https\://github\.com/ansible\-collections/community\.general/pull/5605)\)\.
* udm\_share \- added <code>elements</code> attribute to <code>list</code> type parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5557](https\://github\.com/ansible\-collections/community\.general/pull/5557)\)\.
* udm\_user \- add <code>elements</code> attribute when missing in <code>list</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5559](https\://github\.com/ansible\-collections/community\.general/pull/5559)\)\.

<a id="deprecated-features-3"></a>
### Deprecated Features

* The <code>sap</code> modules <code>sapcar\_extract</code>\, <code>sap\_task\_list\_execute</code>\, and <code>hana\_query</code>\, will be removed from this collection in community\.general 7\.0\.0 and replaced with redirects to <code>community\.sap\_libs</code>\. If you want to continue using these modules\, make sure to also install <code>community\.sap\_libs</code> \(it is part of the Ansible package\) \([https\://github\.com/ansible\-collections/community\.general/pull/5614](https\://github\.com/ansible\-collections/community\.general/pull/5614)\)\.

<a id="bugfixes-14"></a>
### Bugfixes

* chroot connection plugin \- add <code>inventory\_hostname</code> to vars under <code>remote\_addr</code>\. This is needed for compatibility with ansible\-core 2\.13 \([https\://github\.com/ansible\-collections/community\.general/pull/5570](https\://github\.com/ansible\-collections/community\.general/pull/5570)\)\.
* cmd\_runner module utils \- fixed bug when handling default cases in <code>cmd\_runner\_fmt\.as\_map\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5538](https\://github\.com/ansible\-collections/community\.general/pull/5538)\)\.
* cmd\_runner module utils \- formatting arguments <code>cmd\_runner\_fmt\.as\_fixed\(\)</code> was expecting an non\-existing argument \([https\://github\.com/ansible\-collections/community\.general/pull/5538](https\://github\.com/ansible\-collections/community\.general/pull/5538)\)\.
* keycloak\_client\_rolemapping \- calculate <code>proposed</code> and <code>after</code> return values properly \([https\://github\.com/ansible\-collections/community\.general/pull/5619](https\://github\.com/ansible\-collections/community\.general/pull/5619)\)\.
* keycloak\_client\_rolemapping \- remove only listed mappings with <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5619](https\://github\.com/ansible\-collections/community\.general/pull/5619)\)\.
* proxmox inventory plugin \- fix bug while templating when using templates for the <code>url</code>\, <code>user</code>\, <code>password</code>\, <code>token\_id</code>\, or <code>token\_secret</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5640](https\://github\.com/ansible\-collections/community\.general/pull/5640)\)\.
* proxmox inventory plugin \- handle tags delimited by semicolon instead of comma\, which happens from Proxmox 7\.3 on \([https\://github\.com/ansible\-collections/community\.general/pull/5602](https\://github\.com/ansible\-collections/community\.general/pull/5602)\)\.
* redhat\_subscription \- do not ignore <code>consumer\_name</code> and other variables if <code>activationkey</code> is specified \([https\://github\.com/ansible\-collections/community\.general/issues/3486](https\://github\.com/ansible\-collections/community\.general/issues/3486)\, [https\://github\.com/ansible\-collections/community\.general/pull/5627](https\://github\.com/ansible\-collections/community\.general/pull/5627)\)\.
* redhat\_subscription \- do not pass arguments to <code>subscription\-manager register</code> for things already configured\; now a specified <code>rhsm\_baseurl</code> is properly set for subscription\-manager \([https\://github\.com/ansible\-collections/community\.general/pull/5583](https\://github\.com/ansible\-collections/community\.general/pull/5583)\)\.
* unixy callback plugin \- fix plugin to work with ansible\-core 2\.14 by using Ansible\'s configuration manager for handling options \([https\://github\.com/ansible\-collections/community\.general/issues/5600](https\://github\.com/ansible\-collections/community\.general/issues/5600)\)\.
* vdo \- now uses <code>yaml\.safe\_load\(\)</code> to parse command output instead of the deprecated <code>yaml\.load\(\)</code> which is potentially unsafe\. Using <code>yaml\.load\(\)</code> without explicitely setting a <code>Loader\=</code> is also an error in pyYAML 6\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5632](https\://github\.com/ansible\-collections/community\.general/pull/5632)\)\.
* vmadm \- fix for index out of range error in <code>get\_vm\_uuid</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5628](https\://github\.com/ansible\-collections/community\.general/pull/5628)\)\.

<a id="new-modules-3"></a>
### New Modules

* gitlab\_project\_badge \- Manage project badges on GitLab Server
* keycloak\_clientsecret\_info \- Retrieve client secret via Keycloak API
* keycloak\_clientsecret\_regenerate \- Regenerate Keycloak client secret via Keycloak API

<a id="v6-0-1"></a>
## v6\.0\.1

<a id="release-summary-15"></a>
### Release Summary

Bugfix release for Ansible 7\.0\.0\.

<a id="bugfixes-15"></a>
### Bugfixes

* dependent lookup plugin \- avoid warning on deprecated parameter for <code>Templar\.template\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5543](https\://github\.com/ansible\-collections/community\.general/pull/5543)\)\.
* jenkins\_build \- fix the logical flaw when deleting a Jenkins build \([https\://github\.com/ansible\-collections/community\.general/pull/5514](https\://github\.com/ansible\-collections/community\.general/pull/5514)\)\.
* one\_vm \- avoid splitting labels that are <code>None</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5489](https\://github\.com/ansible\-collections/community\.general/pull/5489)\)\.
* onepassword\_raw \- add missing parameter to plugin documentation \([https\://github\.com/ansible\-collections/community\.general/issues/5506](https\://github\.com/ansible\-collections/community\.general/issues/5506)\)\.
* proxmox\_disk \- avoid duplicate <code>vmid</code> reference \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5493](https\://github\.com/ansible\-collections/community\.general/pull/5493)\)\.

<a id="v6-0-0"></a>
## v6\.0\.0

<a id="release-summary-16"></a>
### Release Summary

New major release of community\.general with lots of bugfixes\, new features\, some removed deprecated features\, and some other breaking changes\. Please check the coresponding sections of the changelog for more details\.

<a id="major-changes"></a>
### Major Changes

* The internal structure of the collection was changed for modules and action plugins\. These no longer live in a directory hierarchy ordered by topic\, but instead are now all in a single \(flat\) directory\. This has no impact on users <em>assuming they did not use internal FQCNs</em>\. These will still work\, but result in deprecation warnings\. They were never officially supported and thus the redirects are kept as a courtsey\, and this is not labelled as a breaking change\. Note that for example the Ansible VScode plugin started recommending these internal names\. If you followed its recommendation\, you will now have to change back to the short names to avoid deprecation warnings\, and potential errors in the future as these redirects will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5461](https\://github\.com/ansible\-collections/community\.general/pull/5461)\)\.
* newrelic\_deployment \- removed New Relic v1 API\, added support for v2 API \([https\://github\.com/ansible\-collections/community\.general/pull/5341](https\://github\.com/ansible\-collections/community\.general/pull/5341)\)\.

<a id="minor-changes-10"></a>
### Minor Changes

* Added MIT license as <code>LICENSES/MIT\.txt</code> for tests/unit/plugins/modules/packaging/language/test\_gem\.py \([https\://github\.com/ansible\-collections/community\.general/pull/5065](https\://github\.com/ansible\-collections/community\.general/pull/5065)\)\.
* All software licenses are now in the <code>LICENSES/</code> directory of the collection root \([https\://github\.com/ansible\-collections/community\.general/pull/5065](https\://github\.com/ansible\-collections/community\.general/pull/5065)\, [https\://github\.com/ansible\-collections/community\.general/pull/5079](https\://github\.com/ansible\-collections/community\.general/pull/5079)\, [https\://github\.com/ansible\-collections/community\.general/pull/5080](https\://github\.com/ansible\-collections/community\.general/pull/5080)\, [https\://github\.com/ansible\-collections/community\.general/pull/5083](https\://github\.com/ansible\-collections/community\.general/pull/5083)\, [https\://github\.com/ansible\-collections/community\.general/pull/5087](https\://github\.com/ansible\-collections/community\.general/pull/5087)\, [https\://github\.com/ansible\-collections/community\.general/pull/5095](https\://github\.com/ansible\-collections/community\.general/pull/5095)\, [https\://github\.com/ansible\-collections/community\.general/pull/5098](https\://github\.com/ansible\-collections/community\.general/pull/5098)\, [https\://github\.com/ansible\-collections/community\.general/pull/5106](https\://github\.com/ansible\-collections/community\.general/pull/5106)\)\.
* ModuleHelper module utils \- added property <code>verbosity</code> to base class \([https\://github\.com/ansible\-collections/community\.general/pull/5035](https\://github\.com/ansible\-collections/community\.general/pull/5035)\)\.
* ModuleHelper module utils \- improved <code>ModuleHelperException</code>\, using <code>to\_native\(\)</code> for the exception message \([https\://github\.com/ansible\-collections/community\.general/pull/4755](https\://github\.com/ansible\-collections/community\.general/pull/4755)\)\.
* The collection repository conforms to the [REUSE specification](https\://reuse\.software/spec/) except for the changelog fragments \([https\://github\.com/ansible\-collections/community\.general/pull/5138](https\://github\.com/ansible\-collections/community\.general/pull/5138)\)\.
* ali\_instance \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5240](https\://github\.com/ansible\-collections/community\.general/pull/5240)\)\.
* ali\_instance\_info \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5240](https\://github\.com/ansible\-collections/community\.general/pull/5240)\)\.
* alternatives \- add <code>state\=absent</code> to be able to remove an alternative \([https\://github\.com/ansible\-collections/community\.general/pull/4654](https\://github\.com/ansible\-collections/community\.general/pull/4654)\)\.
* alternatives \- add <code>subcommands</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/4654](https\://github\.com/ansible\-collections/community\.general/pull/4654)\)\.
* ansible\_galaxy\_install \- minor refactoring using latest <code>ModuleHelper</code> updates \([https\://github\.com/ansible\-collections/community\.general/pull/4752](https\://github\.com/ansible\-collections/community\.general/pull/4752)\)\.
* ansible\_galaxy\_install \- refactored module to use <code>CmdRunner</code> to execute <code>ansible\-galaxy</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5477](https\://github\.com/ansible\-collections/community\.general/pull/5477)\)\.
* apk \- add <code>world</code> parameter for supporting a custom world file \([https\://github\.com/ansible\-collections/community\.general/pull/4976](https\://github\.com/ansible\-collections/community\.general/pull/4976)\)\.
* bitwarden lookup plugin \- add option <code>search</code> to search for other attributes than name \([https\://github\.com/ansible\-collections/community\.general/pull/5297](https\://github\.com/ansible\-collections/community\.general/pull/5297)\)\.
* cartesian lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* cmd\_runner module util \- added parameters <code>check\_mode\_skip</code> and <code>check\_mode\_return</code> to <code>CmdRunner\.context\(\)</code>\, so that the command is not executed when <code>check\_mode\=True</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4736](https\://github\.com/ansible\-collections/community\.general/pull/4736)\)\.
* cmd\_runner module utils \- add <code>\_\_call\_\_</code> method to invoke context \([https\://github\.com/ansible\-collections/community\.general/pull/4791](https\://github\.com/ansible\-collections/community\.general/pull/4791)\)\.
* consul \- adds <code>ttl</code> parameter for session  \([https\://github\.com/ansible\-collections/community\.general/pull/4996](https\://github\.com/ansible\-collections/community\.general/pull/4996)\)\.
* consul \- minor refactoring \([https\://github\.com/ansible\-collections/community\.general/pull/5367](https\://github\.com/ansible\-collections/community\.general/pull/5367)\)\.
* consul\_session \- adds <code>token</code> parameter for session \([https\://github\.com/ansible\-collections/community\.general/pull/5193](https\://github\.com/ansible\-collections/community\.general/pull/5193)\)\.
* cpanm \- refactored module to use <code>CmdRunner</code> to execute <code>cpanm</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5485](https\://github\.com/ansible\-collections/community\.general/pull/5485)\)\.
* cpanm \- using <code>do\_raise\(\)</code> to raise exceptions in <code>ModuleHelper</code> derived modules \([https\://github\.com/ansible\-collections/community\.general/pull/4674](https\://github\.com/ansible\-collections/community\.general/pull/4674)\)\.
* credstash lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* dependent lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* dig lookup plugin \- add option <code>fail\_on\_error</code> to allow stopping execution on lookup failures \([https\://github\.com/ansible\-collections/community\.general/pull/4973](https\://github\.com/ansible\-collections/community\.general/pull/4973)\)\.
* dig lookup plugin \- start using Ansible\'s configuration manager to parse options\. All documented options can now also be passed as lookup parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* dnstxt lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* filetree lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* flattened lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* gitlab module util \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_branch \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_deploy\_key \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_group \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_group\_members \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_group\_variable \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_hook \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_hook \- minor refactoring \([https\://github\.com/ansible\-collections/community\.general/pull/5271](https\://github\.com/ansible\-collections/community\.general/pull/5271)\)\.
* gitlab\_project \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_project\_members \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_project\_variable \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_protected\_branch \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_runner \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* gitlab\_user \- minor refactor when checking for installed dependency \([https\://github\.com/ansible\-collections/community\.general/pull/5259](https\://github\.com/ansible\-collections/community\.general/pull/5259)\)\.
* hiera lookup plugin \- start using Ansible\'s configuration manager to parse options\. The Hiera executable and config file can now also be passed as lookup parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* homebrew\, homebrew\_tap \- added Homebrew on Linux path to defaults \([https\://github\.com/ansible\-collections/community\.general/pull/5241](https\://github\.com/ansible\-collections/community\.general/pull/5241)\)\.
* hponcfg \- refactored module to use <code>CmdRunner</code> to execute <code>hponcfg</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5483](https\://github\.com/ansible\-collections/community\.general/pull/5483)\)\.
* keycloak\_\* modules \- add <code>http\_agent</code> parameter with default value <code>Ansible</code> \([https\://github\.com/ansible\-collections/community\.general/issues/5023](https\://github\.com/ansible\-collections/community\.general/issues/5023)\)\.
* keyring lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* lastpass \- use config manager for handling plugin options \([https\://github\.com/ansible\-collections/community\.general/pull/5022](https\://github\.com/ansible\-collections/community\.general/pull/5022)\)\.
* ldap\_attrs \- allow for DNs to have <code>\{x\}</code> prefix on first RDN \([https\://github\.com/ansible\-collections/community\.general/issues/977](https\://github\.com/ansible\-collections/community\.general/issues/977)\, [https\://github\.com/ansible\-collections/community\.general/pull/5450](https\://github\.com/ansible\-collections/community\.general/pull/5450)\)\.
* linode inventory plugin \- simplify option handling \([https\://github\.com/ansible\-collections/community\.general/pull/5438](https\://github\.com/ansible\-collections/community\.general/pull/5438)\)\.
* listen\_ports\_facts \- add new <code>include\_non\_listening</code> option which adds <code>\-a</code> option to <code>netstat</code> and <code>ss</code>\. This shows both listening and non\-listening \(for TCP this means established connections\) sockets\, and returns <code>state</code> and <code>foreign\_address</code> \([https\://github\.com/ansible\-collections/community\.general/issues/4762](https\://github\.com/ansible\-collections/community\.general/issues/4762)\, [https\://github\.com/ansible\-collections/community\.general/pull/4953](https\://github\.com/ansible\-collections/community\.general/pull/4953)\)\.
* lmdb\_kv lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* lxc\_container \- minor refactoring \([https\://github\.com/ansible\-collections/community\.general/pull/5358](https\://github\.com/ansible\-collections/community\.general/pull/5358)\)\.
* machinectl become plugin \- can now be used with a password from another user than root\, if a polkit rule is present \([https\://github\.com/ansible\-collections/community\.general/pull/4849](https\://github\.com/ansible\-collections/community\.general/pull/4849)\)\.
* machinectl become plugin \- combine the success command when building the become command to be consistent with other become plugins \([https\://github\.com/ansible\-collections/community\.general/pull/5287](https\://github\.com/ansible\-collections/community\.general/pull/5287)\)\.
* manifold lookup plugin \- start using Ansible\'s configuration manager to parse options \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* maven\_artifact \- add a new <code>unredirected\_headers</code> option that can be used with ansible\-core 2\.12 and above\. The default value is to not use <code>Authorization</code> and <code>Cookie</code> headers on redirects for security reasons\. With ansible\-core 2\.11\, all headers are still passed on for redirects \([https\://github\.com/ansible\-collections/community\.general/pull/4812](https\://github\.com/ansible\-collections/community\.general/pull/4812)\)\.
* mksysb \- refactored module to use <code>CmdRunner</code> to execute <code>mksysb</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5484](https\://github\.com/ansible\-collections/community\.general/pull/5484)\)\.
* mksysb \- using <code>do\_raise\(\)</code> to raise exceptions in <code>ModuleHelper</code> derived modules \([https\://github\.com/ansible\-collections/community\.general/pull/4674](https\://github\.com/ansible\-collections/community\.general/pull/4674)\)\.
* nagios \- minor refactoring on parameter validation for different actions \([https\://github\.com/ansible\-collections/community\.general/pull/5239](https\://github\.com/ansible\-collections/community\.general/pull/5239)\)\.
* netcup\_dnsapi \- add <code>timeout</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/5301](https\://github\.com/ansible\-collections/community\.general/pull/5301)\)\.
* nmcli \- add <code>transport\_mode</code> configuration for Infiniband devices \([https\://github\.com/ansible\-collections/community\.general/pull/5361](https\://github\.com/ansible\-collections/community\.general/pull/5361)\)\.
* nmcli \- add bond option <code>xmit\_hash\_policy</code> to bond options \([https\://github\.com/ansible\-collections/community\.general/issues/5148](https\://github\.com/ansible\-collections/community\.general/issues/5148)\)\.
* nmcli \- adds <code>vpn</code> type and parameter for supporting VPN with service type L2TP and PPTP \([https\://github\.com/ansible\-collections/community\.general/pull/4746](https\://github\.com/ansible\-collections/community\.general/pull/4746)\)\.
* nmcli \- honor IP options for VPNs \([https\://github\.com/ansible\-collections/community\.general/pull/5228](https\://github\.com/ansible\-collections/community\.general/pull/5228)\)\.
* onepassword \- support version 2 of the OnePassword CLI \([https\://github\.com/ansible\-collections/community\.general/pull/4728](https\://github\.com/ansible\-collections/community\.general/pull/4728)\)
* opentelemetry callback plugin \- allow configuring opentelementry callback via config file \([https\://github\.com/ansible\-collections/community\.general/pull/4916](https\://github\.com/ansible\-collections/community\.general/pull/4916)\)\.
* opentelemetry callback plugin \- send logs\. This can be disabled by setting <code>disable\_logs\=false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4175](https\://github\.com/ansible\-collections/community\.general/pull/4175)\)\.
* pacman \- added parameters <code>reason</code> and <code>reason\_for</code> to set/change the install reason of packages \([https\://github\.com/ansible\-collections/community\.general/pull/4956](https\://github\.com/ansible\-collections/community\.general/pull/4956)\)\.
* passwordstore lookup plugin \- allow options to be passed lookup options instead of being part of the term strings \([https\://github\.com/ansible\-collections/community\.general/pull/5444](https\://github\.com/ansible\-collections/community\.general/pull/5444)\)\.
* passwordstore lookup plugin \- allow using alternative password managers by detecting wrapper scripts\, allow explicit configuration of pass and gopass backends \([https\://github\.com/ansible\-collections/community\.general/issues/4766](https\://github\.com/ansible\-collections/community\.general/issues/4766)\)\.
* passwordstore lookup plugin \- improve error messages to include stderr \([https\://github\.com/ansible\-collections/community\.general/pull/5436](https\://github\.com/ansible\-collections/community\.general/pull/5436)\)
* pipx \- added state <code>latest</code> to the module \([https\://github\.com/ansible\-collections/community\.general/pull/5105](https\://github\.com/ansible\-collections/community\.general/pull/5105)\)\.
* pipx \- changed implementation to use <code>cmd\_runner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5085](https\://github\.com/ansible\-collections/community\.general/pull/5085)\)\.
* pipx \- module fails faster when <code>name</code> is missing for states <code>upgrade</code> and <code>reinstall</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5100](https\://github\.com/ansible\-collections/community\.general/pull/5100)\)\.
* pipx \- using <code>do\_raise\(\)</code> to raise exceptions in <code>ModuleHelper</code> derived modules \([https\://github\.com/ansible\-collections/community\.general/pull/4674](https\://github\.com/ansible\-collections/community\.general/pull/4674)\)\.
* pipx module utils \- created new module util <code>pipx</code> providing a <code>cmd\_runner</code> specific for the <code>pipx</code> module \([https\://github\.com/ansible\-collections/community\.general/pull/5085](https\://github\.com/ansible\-collections/community\.general/pull/5085)\)\.
* portage \- add knobs for Portage\'s <code>\-\-backtrack</code> and <code>\-\-with\-bdeps</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5349](https\://github\.com/ansible\-collections/community\.general/pull/5349)\)\.
* portage \- use Portage\'s python module instead of calling gentoolkit\-provided program in shell \([https\://github\.com/ansible\-collections/community\.general/pull/5349](https\://github\.com/ansible\-collections/community\.general/pull/5349)\)\.
* proxmox inventory plugin \- added new flag <code>qemu\_extended\_statuses</code> and new groups <code>\<group\_prefix\>prelaunch</code>\, <code>\<group\_prefix\>paused</code>\. They will be populated only when <code>want\_facts\=true</code>\, <code>qemu\_extended\_statuses\=true</code> and only for <code>QEMU</code> machines \([https\://github\.com/ansible\-collections/community\.general/pull/4723](https\://github\.com/ansible\-collections/community\.general/pull/4723)\)\.
* proxmox inventory plugin \- simplify option handling code \([https\://github\.com/ansible\-collections/community\.general/pull/5437](https\://github\.com/ansible\-collections/community\.general/pull/5437)\)\.
* proxmox module utils\, the proxmox\* modules \- add <code>api\_task\_ok</code> helper to standardize API task status checks across all proxmox modules \([https\://github\.com/ansible\-collections/community\.general/pull/5274](https\://github\.com/ansible\-collections/community\.general/pull/5274)\)\.
* proxmox\_kvm \- allow <code>agent</code> argument to be a string \([https\://github\.com/ansible\-collections/community\.general/pull/5107](https\://github\.com/ansible\-collections/community\.general/pull/5107)\)\.
* proxmox\_snap \- add <code>unbind</code> param to support snapshotting containers with configured mountpoints \([https\://github\.com/ansible\-collections/community\.general/pull/5274](https\://github\.com/ansible\-collections/community\.general/pull/5274)\)\.
* puppet \- adds <code>confdir</code> parameter to configure a custom confir location \([https\://github\.com/ansible\-collections/community\.general/pull/4740](https\://github\.com/ansible\-collections/community\.general/pull/4740)\)\.
* redfish \- added new command GetVirtualMedia\, VirtualMediaInsert and VirtualMediaEject to Systems category due to Redfish spec changes the virtualMedia resource location from Manager to System \([https\://github\.com/ansible\-collections/community\.general/pull/5124](https\://github\.com/ansible\-collections/community\.general/pull/5124)\)\.
* redfish\_config \- add <code>SetSessionService</code> to set default session timeout policy \([https\://github\.com/ansible\-collections/community\.general/issues/5008](https\://github\.com/ansible\-collections/community\.general/issues/5008)\)\.
* redfish\_info \- add <code>GetManagerInventory</code> to report list of Manager inventory information \([https\://github\.com/ansible\-collections/community\.general/issues/4899](https\://github\.com/ansible\-collections/community\.general/issues/4899)\)\.
* seport \- added new argument <code>local</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5203](https\://github\.com/ansible\-collections/community\.general/pull/5203)\)
* snap \- using <code>do\_raise\(\)</code> to raise exceptions in <code>ModuleHelper</code> derived modules \([https\://github\.com/ansible\-collections/community\.general/pull/4674](https\://github\.com/ansible\-collections/community\.general/pull/4674)\)\.
* sudoers \- will attempt to validate the proposed sudoers rule using visudo if available\, optionally skipped\, or required \([https\://github\.com/ansible\-collections/community\.general/pull/4794](https\://github\.com/ansible\-collections/community\.general/pull/4794)\, [https\://github\.com/ansible\-collections/community\.general/issues/4745](https\://github\.com/ansible\-collections/community\.general/issues/4745)\)\.
* terraform \- adds capability to handle complex variable structures for <code>variables</code> parameter in the module\. This must be enabled with the new <code>complex\_vars</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/4797](https\://github\.com/ansible\-collections/community\.general/pull/4797)\)\.
* terraform \- run <code>terraform init</code> with <code>\-no\-color</code> not to mess up the stdout of the task \([https\://github\.com/ansible\-collections/community\.general/pull/5147](https\://github\.com/ansible\-collections/community\.general/pull/5147)\)\.
* wdc\_redfish\_command \- add <code>IndicatorLedOn</code> and <code>IndicatorLedOff</code> commands for <code>Chassis</code> category \([https\://github\.com/ansible\-collections/community\.general/pull/5059](https\://github\.com/ansible\-collections/community\.general/pull/5059)\)\.
* wdc\_redfish\_command \- add <code>PowerModeLow</code> and <code>PowerModeNormal</code> commands for <code>Chassis</code> category \([https\://github\.com/ansible\-collections/community\.general/pull/5145](https\://github\.com/ansible\-collections/community\.general/pull/5145)\)\.
* xfconf \- add <code>stdout</code>\, <code>stderr</code> and <code>cmd</code> to the module results \([https\://github\.com/ansible\-collections/community\.general/pull/5037](https\://github\.com/ansible\-collections/community\.general/pull/5037)\)\.
* xfconf \- changed implementation to use <code>cmd\_runner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4776](https\://github\.com/ansible\-collections/community\.general/pull/4776)\)\.
* xfconf \- use <code>do\_raise\(\)</code> instead of defining custom exception class \([https\://github\.com/ansible\-collections/community\.general/pull/4975](https\://github\.com/ansible\-collections/community\.general/pull/4975)\)\.
* xfconf \- using <code>do\_raise\(\)</code> to raise exceptions in <code>ModuleHelper</code> derived modules \([https\://github\.com/ansible\-collections/community\.general/pull/4674](https\://github\.com/ansible\-collections/community\.general/pull/4674)\)\.
* xfconf module utils \- created new module util <code>xfconf</code> providing a <code>cmd\_runner</code> specific for <code>xfconf</code> modules \([https\://github\.com/ansible\-collections/community\.general/pull/4776](https\://github\.com/ansible\-collections/community\.general/pull/4776)\)\.
* xfconf\_info \- changed implementation to use <code>cmd\_runner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4776](https\://github\.com/ansible\-collections/community\.general/pull/4776)\)\.
* xfconf\_info \- use <code>do\_raise\(\)</code> instead of defining custom exception class \([https\://github\.com/ansible\-collections/community\.general/pull/4975](https\://github\.com/ansible\-collections/community\.general/pull/4975)\)\.
* znode \- possibility to use ZooKeeper ACL authentication \([https\://github\.com/ansible\-collections/community\.general/pull/5306](https\://github\.com/ansible\-collections/community\.general/pull/5306)\)\.

<a id="breaking-changes--porting-guide-1"></a>
### Breaking Changes / Porting Guide

* newrelic\_deployment \- <code>revision</code> is required for v2 API \([https\://github\.com/ansible\-collections/community\.general/pull/5341](https\://github\.com/ansible\-collections/community\.general/pull/5341)\)\.
* scaleway\_container\_registry\_info \- no longer replace <code>secret\_environment\_variables</code> in the output by <code>SENSITIVE\_VALUE</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5497](https\://github\.com/ansible\-collections/community\.general/pull/5497)\)\.

<a id="deprecated-features-4"></a>
### Deprecated Features

* ArgFormat module utils \- deprecated along <code>CmdMixin</code>\, in favor of the <code>cmd\_runner\_fmt</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/5370](https\://github\.com/ansible\-collections/community\.general/pull/5370)\)\.
* CmdMixin module utils \- deprecated in favor of the <code>CmdRunner</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/5370](https\://github\.com/ansible\-collections/community\.general/pull/5370)\)\.
* CmdModuleHelper module utils \- deprecated in favor of the <code>CmdRunner</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/5370](https\://github\.com/ansible\-collections/community\.general/pull/5370)\)\.
* CmdStateModuleHelper module utils \- deprecated in favor of the <code>CmdRunner</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/5370](https\://github\.com/ansible\-collections/community\.general/pull/5370)\)\.
* cmd\_runner module utils \- deprecated <code>fmt</code> in favour of <code>cmd\_runner\_fmt</code> as the parameter format object \([https\://github\.com/ansible\-collections/community\.general/pull/4777](https\://github\.com/ansible\-collections/community\.general/pull/4777)\)\.
* django\_manage \- support for Django releases older than 4\.1 has been deprecated and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5400](https\://github\.com/ansible\-collections/community\.general/pull/5400)\)\.
* django\_manage \- support for the commands <code>cleanup</code>\, <code>syncdb</code> and <code>validate</code> that have been deprecated in Django long time ago will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5400](https\://github\.com/ansible\-collections/community\.general/pull/5400)\)\.
* django\_manage \- the behavior of \"creating the virtual environment when missing\" is being deprecated and will be removed in community\.general version 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5405](https\://github\.com/ansible\-collections/community\.general/pull/5405)\)\.
* gconftool2 \- deprecates <code>state\=get</code> in favor of using the module <code>gconftool2\_info</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4778](https\://github\.com/ansible\-collections/community\.general/pull/4778)\)\.
* lxc\_container \- the module will no longer make any effort to support Python 2 \([https\://github\.com/ansible\-collections/community\.general/pull/5304](https\://github\.com/ansible\-collections/community\.general/pull/5304)\)\.
* newrelic\_deployment \- <code>appname</code> and <code>environment</code> are no longer valid options in the v2 API\. They will be removed in community\.general 7\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5341](https\://github\.com/ansible\-collections/community\.general/pull/5341)\)\.
* proxmox \- deprecated the current <code>unprivileged</code> default value\, will be changed to <code>true</code> in community\.general 7\.0\.0 \([https\://github\.com/pull/5224](https\://github\.com/pull/5224)\)\.
* xfconf \- deprecated parameter <code>disable\_facts</code>\, as since version 4\.0\.0 it only allows value <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4520](https\://github\.com/ansible\-collections/community\.general/pull/4520)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* bitbucket\* modules \- <code>username</code> is no longer an alias of <code>workspace</code>\, but of <code>user</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* gem \- the default of the <code>norc</code> option changed from <code>false</code> to <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* gitlab\_group\_members \- <code>gitlab\_group</code> must now always contain the full path\, and no longer just the name or path \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* keycloak\_authentication \- the return value <code>flow</code> has been removed\. Use <code>end\_state</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* keycloak\_group \- the return value <code>group</code> has been removed\. Use <code>end\_state</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* lxd\_container \- the default of the <code>ignore\_volatile\_options</code> option changed from <code>true</code> to <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* mail callback plugin \- the <code>sender</code> option is now required \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* module\_helper module utils \- remove the <code>VarDict</code> attribute from <code>ModuleHelper</code>\. Import <code>VarDict</code> from <code>ansible\_collections\.community\.general\.plugins\.module\_utils\.mh\.mixins\.vars</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* proxmox inventory plugin \- the default of the <code>want\_proxmox\_nodes\_ansible\_host</code> option changed from <code>true</code> to <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.
* vmadm \- the <code>debug</code> option has been removed\. It was not used anyway \([https\://github\.com/ansible\-collections/community\.general/pull/5326](https\://github\.com/ansible\-collections/community\.general/pull/5326)\)\.

<a id="bugfixes-16"></a>
### Bugfixes

* Include <code>PSF\-license\.txt</code> file for <code>plugins/module\_utils/\_mount\.py</code>\.
* Include <code>simplified\_bsd\.txt</code> license file for various module utils\, the <code>lxca\_common</code> docs fragment\, and the <code>utm\_utils</code> unit tests\.
* alternatives \- do not set the priority if the priority was not set by the user \([https\://github\.com/ansible\-collections/community\.general/pull/4810](https\://github\.com/ansible\-collections/community\.general/pull/4810)\)\.
* alternatives \- only pass subcommands when they are specified as module arguments \([https\://github\.com/ansible\-collections/community\.general/issues/4803](https\://github\.com/ansible\-collections/community\.general/issues/4803)\, [https\://github\.com/ansible\-collections/community\.general/issues/4804](https\://github\.com/ansible\-collections/community\.general/issues/4804)\, [https\://github\.com/ansible\-collections/community\.general/pull/4836](https\://github\.com/ansible\-collections/community\.general/pull/4836)\)\.
* alternatives \- when <code>subcommands</code> is specified\, <code>link</code> must be given for every subcommand\. This was already mentioned in the documentation\, but not enforced by the code \([https\://github\.com/ansible\-collections/community\.general/pull/4836](https\://github\.com/ansible\-collections/community\.general/pull/4836)\)\.
* apache2\_mod\_proxy \- avoid crash when reporting inability to parse balancer\_member\_page HTML caused by using an undefined variable in the error message \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* archive \- avoid crash when <code>lzma</code> is not present and <code>format</code> is not <code>xz</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5393](https\://github\.com/ansible\-collections/community\.general/pull/5393)\)\.
* cmd\_runner module utils \- fix bug caused by using the <code>command</code> variable instead of <code>self\.command</code> when looking for binary path \([https\://github\.com/ansible\-collections/community\.general/pull/4903](https\://github\.com/ansible\-collections/community\.general/pull/4903)\)\.
* consul \- fixed bug introduced in PR 4590 \([https\://github\.com/ansible\-collections/community\.general/issues/4680](https\://github\.com/ansible\-collections/community\.general/issues/4680)\)\.
* credstash lookup plugin \- pass plugin options to credstash for all terms\, not just for the first \([https\://github\.com/ansible\-collections/community\.general/pull/5440](https\://github\.com/ansible\-collections/community\.general/pull/5440)\)\.
* dig lookup plugin \- add option to return empty result without empty strings\, and return empty list instead of <code>NXDOMAIN</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5439](https\://github\.com/ansible\-collections/community\.general/pull/5439)\, [https\://github\.com/ansible\-collections/community\.general/issues/5428](https\://github\.com/ansible\-collections/community\.general/issues/5428)\)\.
* dig lookup plugin \- fix evaluation of falsy values for boolean parameters <code>fail\_on\_error</code> and <code>retry\_servfail</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5129](https\://github\.com/ansible\-collections/community\.general/pull/5129)\)\.
* dnsimple\_info \- correctly report missing library as <code>requests</code> and not <code>another\_library</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* dnstxt lookup plugin \- add option to return empty result without empty strings\, and return empty list instead of <code>NXDOMAIN</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5457](https\://github\.com/ansible\-collections/community\.general/pull/5457)\, [https\://github\.com/ansible\-collections/community\.general/issues/5428](https\://github\.com/ansible\-collections/community\.general/issues/5428)\)\.
* dsv lookup plugin \- do not ignore the <code>tld</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/4911](https\://github\.com/ansible\-collections/community\.general/pull/4911)\)\.
* filesystem \- handle <code>fatresize \-\-info</code> output lines without <code>\:</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4700](https\://github\.com/ansible\-collections/community\.general/pull/4700)\)\.
* filesystem \- improve error messages when output cannot be parsed by including newlines in escaped form \([https\://github\.com/ansible\-collections/community\.general/pull/4700](https\://github\.com/ansible\-collections/community\.general/pull/4700)\)\.
* funcd connection plugin \- fix signature of <code>exec\_command</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* ini\_file \- minor refactor fixing a python lint error \([https\://github\.com/ansible\-collections/community\.general/pull/5307](https\://github\.com/ansible\-collections/community\.general/pull/5307)\)\.
* iso\_create \- the module somtimes failed to add folders for Joliet and UDF formats \([https\://github\.com/ansible\-collections/community\.general/issues/5275](https\://github\.com/ansible\-collections/community\.general/issues/5275)\)\.
* keycloak\_realm \- fix default groups and roles \([https\://github\.com/ansible\-collections/community\.general/issues/4241](https\://github\.com/ansible\-collections/community\.general/issues/4241)\)\.
* keyring\_info \- fix the result from the keyring library never getting returned \([https\://github\.com/ansible\-collections/community\.general/pull/4964](https\://github\.com/ansible\-collections/community\.general/pull/4964)\)\.
* ldap\_attrs \- fix bug which caused a <code>Bad search filter</code> error\. The error was occuring when the ldap attribute value contained special characters such as <code>\(</code> or <code>\*</code> \([https\://github\.com/ansible\-collections/community\.general/issues/5434](https\://github\.com/ansible\-collections/community\.general/issues/5434)\, [https\://github\.com/ansible\-collections/community\.general/pull/5435](https\://github\.com/ansible\-collections/community\.general/pull/5435)\)\.
* ldap\_attrs \- fix ordering issue by ignoring the <code>\{x\}</code> prefix on attribute values \([https\://github\.com/ansible\-collections/community\.general/issues/977](https\://github\.com/ansible\-collections/community\.general/issues/977)\, [https\://github\.com/ansible\-collections/community\.general/pull/5385](https\://github\.com/ansible\-collections/community\.general/pull/5385)\)\.
* listen\_ports\_facts \- removed leftover <code>EnvironmentError</code> \. The <code>else</code> clause had a wrong indentation\. The check is now handled in the <code>split\_pid\_name</code> function \([https\://github\.com/ansible\-collections/community\.general/pull/5202](https\://github\.com/ansible\-collections/community\.general/pull/5202)\)\.
* locale\_gen \- fix support for Ubuntu \([https\://github\.com/ansible\-collections/community\.general/issues/5281](https\://github\.com/ansible\-collections/community\.general/issues/5281)\)\.
* lxc\_container \- the module has been updated to support Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/5304](https\://github\.com/ansible\-collections/community\.general/pull/5304)\)\.
* lxd connection plugin \- fix incorrect <code>inventory\_hostname</code> in <code>remote\_addr</code>\. This is needed for compatibility with ansible\-core 2\.13 \([https\://github\.com/ansible\-collections/community\.general/issues/4886](https\://github\.com/ansible\-collections/community\.general/issues/4886)\)\.
* manageiq\_alert\_profiles \- avoid crash when reporting unknown profile caused by trying to return an undefined variable \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* nmcli \- avoid changed status for most cases with VPN connections \([https\://github\.com/ansible\-collections/community\.general/pull/5126](https\://github\.com/ansible\-collections/community\.general/pull/5126)\)\.
* nmcli \- fix error caused by adding undefined module arguments for list options \([https\://github\.com/ansible\-collections/community\.general/issues/4373](https\://github\.com/ansible\-collections/community\.general/issues/4373)\, [https\://github\.com/ansible\-collections/community\.general/pull/4813](https\://github\.com/ansible\-collections/community\.general/pull/4813)\)\.
* nmcli \- fix error when setting previously unset MAC address\, <code>gsm\.apn</code> or <code>vpn\.data</code>\: current values were being normalized without checking if they might be <code>None</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5291](https\://github\.com/ansible\-collections/community\.general/pull/5291)\)\.
* nmcli \- fix int options idempotence \([https\://github\.com/ansible\-collections/community\.general/issues/4998](https\://github\.com/ansible\-collections/community\.general/issues/4998)\)\.
* nsupdate \- compatibility with NS records \([https\://github\.com/ansible\-collections/community\.general/pull/5112](https\://github\.com/ansible\-collections/community\.general/pull/5112)\)\.
* nsupdate \- fix silent failures when updating <code>NS</code> entries from Bind9 managed DNS zones \([https\://github\.com/ansible\-collections/community\.general/issues/4657](https\://github\.com/ansible\-collections/community\.general/issues/4657)\)\.
* opentelemetry callback plugin \- support opentelemetry\-api 1\.13\.0 that removed support for <code>\_time\_ns</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5342](https\://github\.com/ansible\-collections/community\.general/pull/5342)\)\.
* osx\_defaults \- no longer expand <code>\~</code> in <code>value</code> to the user\'s home directory\, or expand environment variables \([https\://github\.com/ansible\-collections/community\.general/issues/5234](https\://github\.com/ansible\-collections/community\.general/issues/5234)\, [https\://github\.com/ansible\-collections/community\.general/pull/5243](https\://github\.com/ansible\-collections/community\.general/pull/5243)\)\.
* packet\_ip\_subnet \- fix error reporting in case of invalid CIDR prefix lengths \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* pacman \- fixed name resolution of URL packages \([https\://github\.com/ansible\-collections/community\.general/pull/4959](https\://github\.com/ansible\-collections/community\.general/pull/4959)\)\.
* passwordstore lookup plugin \- fix <code>returnall</code> for gopass \([https\://github\.com/ansible\-collections/community\.general/pull/5027](https\://github\.com/ansible\-collections/community\.general/pull/5027)\)\.
* passwordstore lookup plugin \- fix password store path detection for gopass \([https\://github\.com/ansible\-collections/community\.general/pull/4955](https\://github\.com/ansible\-collections/community\.general/pull/4955)\)\.
* pfexec become plugin \- remove superflous quotes preventing exe wrap from working as expected \([https\://github\.com/ansible\-collections/community\.general/issues/3671](https\://github\.com/ansible\-collections/community\.general/issues/3671)\, [https\://github\.com/ansible\-collections/community\.general/pull/3889](https\://github\.com/ansible\-collections/community\.general/pull/3889)\)\.
* pip\_package\_info \- remove usage of global variable \([https\://github\.com/ansible\-collections/community\.general/pull/5111](https\://github\.com/ansible\-collections/community\.general/pull/5111)\)\.
* pkgng \- fix case when <code>pkg</code> fails when trying to upgrade all packages \([https\://github\.com/ansible\-collections/community\.general/issues/5363](https\://github\.com/ansible\-collections/community\.general/issues/5363)\)\.
* proxmox \- fix error handling when getting VM by name when <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4945](https\://github\.com/ansible\-collections/community\.general/pull/4945)\)\.
* proxmox inventory plugin \- fix crash when <code>enabled\=1</code> is used in agent config string \([https\://github\.com/ansible\-collections/community\.general/pull/4910](https\://github\.com/ansible\-collections/community\.general/pull/4910)\)\.
* proxmox inventory plugin \- fixed extended status detection for qemu \([https\://github\.com/ansible\-collections/community\.general/pull/4816](https\://github\.com/ansible\-collections/community\.general/pull/4816)\)\.
* proxmox\_kvm \- fix <code>agent</code> parameter when boolean value is specified \([https\://github\.com/ansible\-collections/community\.general/pull/5198](https\://github\.com/ansible\-collections/community\.general/pull/5198)\)\.
* proxmox\_kvm \- fix error handling when getting VM by name when <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4945](https\://github\.com/ansible\-collections/community\.general/pull/4945)\)\.
* proxmox\_kvm \- fix exception when no <code>agent</code> argument is specified \([https\://github\.com/ansible\-collections/community\.general/pull/5194](https\://github\.com/ansible\-collections/community\.general/pull/5194)\)\.
* proxmox\_kvm \- fix wrong condition \([https\://github\.com/ansible\-collections/community\.general/pull/5108](https\://github\.com/ansible\-collections/community\.general/pull/5108)\)\.
* proxmox\_kvm \- replace new condition with proper condition to allow for using <code>vmid</code> on update \([https\://github\.com/ansible\-collections/community\.general/pull/5206](https\://github\.com/ansible\-collections/community\.general/pull/5206)\)\.
* rax\_clb\_nodes \- fix code to be compatible with Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/4933](https\://github\.com/ansible\-collections/community\.general/pull/4933)\)\.
* redfish\_command \- fix the check if a virtual media is unmounted to just check for <code>instered\= false</code> caused by Supermicro hardware that does not clear the <code>ImageName</code> \([https\://github\.com/ansible\-collections/community\.general/pull/4839](https\://github\.com/ansible\-collections/community\.general/pull/4839)\)\.
* redfish\_command \- the Supermicro Redfish implementation only supports the <code>image\_url</code> parameter in the underlying API calls to <code>VirtualMediaInsert</code> and <code>VirtualMediaEject</code>\. Any values set \(or the defaults\) for <code>write\_protected</code> or <code>inserted</code> will be ignored \([https\://github\.com/ansible\-collections/community\.general/pull/4839](https\://github\.com/ansible\-collections/community\.general/pull/4839)\)\.
* redfish\_info \- fix to <code>GetChassisPower</code> to correctly report power information when multiple chassis exist\, but not all chassis report power information \([https\://github\.com/ansible\-collections/community\.general/issues/4901](https\://github\.com/ansible\-collections/community\.general/issues/4901)\)\.
* redfish\_utils module utils \- centralize payload checking when performing modification requests to a Redfish service \([https\://github\.com/ansible\-collections/community\.general/issues/5210/](https\://github\.com/ansible\-collections/community\.general/issues/5210/)\)\.
* redhat\_subscription \- fix unsubscribing on RHEL 9 \([https\://github\.com/ansible\-collections/community\.general/issues/4741](https\://github\.com/ansible\-collections/community\.general/issues/4741)\)\.
* redhat\_subscription \- make module idempotent when <code>pool\_ids</code> are used \([https\://github\.com/ansible\-collections/community\.general/issues/5313](https\://github\.com/ansible\-collections/community\.general/issues/5313)\)\.
* redis\* modules \- fix call to <code>module\.fail\_json</code> when failing because of missing Python libraries \([https\://github\.com/ansible\-collections/community\.general/pull/4733](https\://github\.com/ansible\-collections/community\.general/pull/4733)\)\.
* slack \- fix incorrect channel prefix <code>\#</code> caused by incomplete pattern detection by adding <code>G0</code> and <code>GF</code> as channel ID patterns \([https\://github\.com/ansible\-collections/community\.general/pull/5019](https\://github\.com/ansible\-collections/community\.general/pull/5019)\)\.
* slack \- fix message update for channels which start with <code>CP</code>\. When <code>message\-id</code> was passed it failed for channels which started with <code>CP</code> because the <code>\#</code> symbol was added before the <code>channel\_id</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5249](https\://github\.com/ansible\-collections/community\.general/pull/5249)\)\.
* snap \- allow values in the <code>options</code> parameter to contain whitespaces \([https\://github\.com/ansible\-collections/community\.general/pull/5475](https\://github\.com/ansible\-collections/community\.general/pull/5475)\)\.
* sudoers \- ensure sudoers config files are created with the permissions requested by sudoers \(0440\) \([https\://github\.com/ansible\-collections/community\.general/pull/4814](https\://github\.com/ansible\-collections/community\.general/pull/4814)\)\.
* sudoers \- fix incorrect handling of <code>state\: absent</code> \([https\://github\.com/ansible\-collections/community\.general/issues/4852](https\://github\.com/ansible\-collections/community\.general/issues/4852)\)\.
* tss lookup plugin \- adding support for updated Delinea library \([https\://github\.com/DelineaXPM/python\-tss\-sdk/issues/9](https\://github\.com/DelineaXPM/python\-tss\-sdk/issues/9)\, [https\://github\.com/ansible\-collections/community\.general/pull/5151](https\://github\.com/ansible\-collections/community\.general/pull/5151)\)\.
* virtualbox inventory plugin \- skip parsing values with keys that have both a value and nested data\. Skip parsing values that are nested more than two keys deep \([https\://github\.com/ansible\-collections/community\.general/issues/5332](https\://github\.com/ansible\-collections/community\.general/issues/5332)\, [https\://github\.com/ansible\-collections/community\.general/pull/5348](https\://github\.com/ansible\-collections/community\.general/pull/5348)\)\.
* xcc\_redfish\_command \- for compatibility due to Redfish spec changes the virtualMedia resource location changed from Manager to System \([https\://github\.com/ansible\-collections/community\.general/pull/4682](https\://github\.com/ansible\-collections/community\.general/pull/4682)\)\.
* xenserver\_facts \- fix broken <code>AnsibleModule</code> call that prevented the module from working at all \([https\://github\.com/ansible\-collections/community\.general/pull/5383](https\://github\.com/ansible\-collections/community\.general/pull/5383)\)\.
* xfconf \- fix setting of boolean values \([https\://github\.com/ansible\-collections/community\.general/issues/4999](https\://github\.com/ansible\-collections/community\.general/issues/4999)\, [https\://github\.com/ansible\-collections/community\.general/pull/5007](https\://github\.com/ansible\-collections/community\.general/pull/5007)\)\.
* zfs \- fix wrong quoting of properties \([https\://github\.com/ansible\-collections/community\.general/issues/4707](https\://github\.com/ansible\-collections/community\.general/issues/4707)\, [https\://github\.com/ansible\-collections/community\.general/pull/4726](https\://github\.com/ansible\-collections/community\.general/pull/4726)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="filter"></a>
#### Filter

* counter \- Counts hashable elements in a sequence

<a id="lookup-1"></a>
#### Lookup

* bitwarden \- Retrieve secrets from Bitwarden

<a id="new-modules-4"></a>
### New Modules

* gconftool2\_info \- Retrieve GConf configurations
* iso\_customize \- Add/remove/change files in ISO file
* keycloak\_user\_rolemapping \- Allows administration of Keycloak user\_rolemapping with the Keycloak API
* keyring \- Set or delete a passphrase using the Operating System\'s native keyring
* keyring\_info \- Get a passphrase using the Operating System\'s native keyring
* manageiq\_policies\_info \- Listing of resource policy\_profiles in ManageIQ
* manageiq\_tags\_info \- Retrieve resource tags in ManageIQ
* pipx\_info \- Rretrieves information about applications installed with pipx
* proxmox\_disk \- Management of a disk of a Qemu\(KVM\) VM in a Proxmox VE cluster\.
* scaleway\_compute\_private\_network \- Scaleway compute \- private network management
* scaleway\_container \- Scaleway Container management
* scaleway\_container\_info \- Retrieve information on Scaleway Container
* scaleway\_container\_namespace \- Scaleway Container namespace management
* scaleway\_container\_namespace\_info \- Retrieve information on Scaleway Container namespace
* scaleway\_container\_registry \- Scaleway Container registry management module
* scaleway\_container\_registry\_info \- Scaleway Container registry info module
* scaleway\_function \- Scaleway Function management
* scaleway\_function\_info \- Retrieve information on Scaleway Function
* scaleway\_function\_namespace \- Scaleway Function namespace management
* scaleway\_function\_namespace\_info \- Retrieve information on Scaleway Function namespace
* wdc\_redfish\_command \- Manages WDC UltraStar Data102 Out\-Of\-Band controllers using Redfish APIs
* wdc\_redfish\_info \- Manages WDC UltraStar Data102 Out\-Of\-Band controllers using Redfish APIs
