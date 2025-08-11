# Community General Release Notes

**Topics**

- <a href="#v10-7-3">v10\.7\.3</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v10-7-2">v10\.7\.2</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v10-7-1">v10\.7\.1</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v10-7-0">v10\.7\.0</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-3">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#callback">Callback</a>
        - <a href="#filter">Filter</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v10-6-0">v10\.6\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#deprecated-features-2">Deprecated Features</a>
    - <a href="#bugfixes-4">Bugfixes</a>
    - <a href="#known-issues">Known Issues</a>
    - <a href="#new-plugins-1">New Plugins</a>
        - <a href="#connection">Connection</a>
- <a href="#v10-5-0">v10\.5\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#bugfixes-5">Bugfixes</a>
    - <a href="#new-modules-1">New Modules</a>
- <a href="#v10-4-0">v10\.4\.0</a>
    - <a href="#release-summary-6">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#deprecated-features-3">Deprecated Features</a>
    - <a href="#bugfixes-6">Bugfixes</a>
    - <a href="#new-modules-2">New Modules</a>
- <a href="#v10-3-1">v10\.3\.1</a>
    - <a href="#release-summary-7">Release Summary</a>
    - <a href="#minor-changes-5">Minor Changes</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v10-3-0">v10\.3\.0</a>
    - <a href="#release-summary-8">Release Summary</a>
    - <a href="#minor-changes-6">Minor Changes</a>
    - <a href="#deprecated-features-4">Deprecated Features</a>
    - <a href="#security-fixes">Security Fixes</a>
    - <a href="#bugfixes-8">Bugfixes</a>
    - <a href="#new-plugins-2">New Plugins</a>
        - <a href="#connection-1">Connection</a>
        - <a href="#filter-1">Filter</a>
        - <a href="#lookup">Lookup</a>
    - <a href="#new-modules-3">New Modules</a>
- <a href="#v10-2-0">v10\.2\.0</a>
    - <a href="#release-summary-9">Release Summary</a>
    - <a href="#minor-changes-7">Minor Changes</a>
    - <a href="#deprecated-features-5">Deprecated Features</a>
    - <a href="#security-fixes-1">Security Fixes</a>
    - <a href="#bugfixes-9">Bugfixes</a>
    - <a href="#new-plugins-3">New Plugins</a>
        - <a href="#inventory">Inventory</a>
    - <a href="#new-modules-4">New Modules</a>
- <a href="#v10-1-0">v10\.1\.0</a>
    - <a href="#release-summary-10">Release Summary</a>
    - <a href="#minor-changes-8">Minor Changes</a>
    - <a href="#deprecated-features-6">Deprecated Features</a>
    - <a href="#bugfixes-10">Bugfixes</a>
    - <a href="#new-plugins-4">New Plugins</a>
        - <a href="#filter-2">Filter</a>
    - <a href="#new-modules-5">New Modules</a>
- <a href="#v10-0-1">v10\.0\.1</a>
    - <a href="#release-summary-11">Release Summary</a>
    - <a href="#bugfixes-11">Bugfixes</a>
- <a href="#v10-0-0">v10\.0\.0</a>
    - <a href="#release-summary-12">Release Summary</a>
    - <a href="#minor-changes-9">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#deprecated-features-7">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#bugfixes-12">Bugfixes</a>
    - <a href="#known-issues-1">Known Issues</a>
    - <a href="#new-plugins-5">New Plugins</a>
        - <a href="#filter-3">Filter</a>
        - <a href="#test">Test</a>
    - <a href="#new-modules-6">New Modules</a>
This changelog describes changes after version 9\.0\.0\.

<a id="v10-7-3"></a>
## v10\.7\.3

<a id="release-summary"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes"></a>
### Bugfixes

* apache2\_module \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* apk \- fix check for empty/whitespace\-only package names \([https\://github\.com/ansible\-collections/community\.general/pull/10532](https\://github\.com/ansible\-collections/community\.general/pull/10532)\)\.
* apk \- handle empty name strings properly \([https\://github\.com/ansible\-collections/community\.general/issues/10441](https\://github\.com/ansible\-collections/community\.general/issues/10441)\, [https\://github\.com/ansible\-collections/community\.general/pull/10442](https\://github\.com/ansible\-collections/community\.general/pull/10442)\)\.
* capabilities \- using invalid path \(symlink/directory/\.\.\.\) returned unrelated and incoherent error messages \([https\://github\.com/ansible\-collections/community\.general/issues/5649](https\://github\.com/ansible\-collections/community\.general/issues/5649)\, [https\://github\.com/ansible\-collections/community\.general/pull/10455](https\://github\.com/ansible\-collections/community\.general/pull/10455)\)\.
* cronvar \- fix crash on missing <code>cron\_file</code> parent directories \([https\://github\.com/ansible\-collections/community\.general/issues/10460](https\://github\.com/ansible\-collections/community\.general/issues/10460)\, [https\://github\.com/ansible\-collections/community\.general/pull/10461](https\://github\.com/ansible\-collections/community\.general/pull/10461)\)\.
* cronvar \- handle empty strings on <code>value</code> properly  \([https\://github\.com/ansible\-collections/community\.general/issues/10439](https\://github\.com/ansible\-collections/community\.general/issues/10439)\, [https\://github\.com/ansible\-collections/community\.general/pull/10445](https\://github\.com/ansible\-collections/community\.general/pull/10445)\)\.
* doas become plugin \- disable pipelining on ansible\-core 2\.19\+\. The plugin does not work with pipelining\, and since ansible\-core 2\.19 become plugins can indicate that they do not work with pipelining \([https\://github\.com/ansible\-collections/community\.general/issues/9977](https\://github\.com/ansible\-collections/community\.general/issues/9977)\, [https\://github\.com/ansible\-collections/community\.general/pull/10537](https\://github\.com/ansible\-collections/community\.general/pull/10537)\)\.
* htpasswd \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* irc \- pass hostname to <code>wrap\_socket\(\)</code> if <code>use\_tls\=true</code> and <code>validate\_certs\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10472](https\://github\.com/ansible\-collections/community\.general/issues/10472)\, [https\://github\.com/ansible\-collections/community\.general/pull/10491](https\://github\.com/ansible\-collections/community\.general/pull/10491)\)\.
* json\_query filter plugin \- make compatible with lazy evaluation list and dictionary types of ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10539](https\://github\.com/ansible\-collections/community\.general/pull/10539)\)\.
* listen\_port\_facts \- avoid crash when required commands are missing \([https\://github\.com/ansible\-collections/community\.general/issues/10457](https\://github\.com/ansible\-collections/community\.general/issues/10457)\, [https\://github\.com/ansible\-collections/community\.general/pull/10458](https\://github\.com/ansible\-collections/community\.general/pull/10458)\)\.
* machinectl become plugin \- disable pipelining on ansible\-core 2\.19\+\. The plugin does not work with pipelining\, and since ansible\-core 2\.19 become plugins can indicate that they do not work with pipelining \([https\://github\.com/ansible\-collections/community\.general/pull/10537](https\://github\.com/ansible\-collections/community\.general/pull/10537)\)\.
* merge\_variables lookup plugin \- avoid deprecated functionality from ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10566](https\://github\.com/ansible\-collections/community\.general/pull/10566)\)\.
* proxmox inventory plugin \- avoid using deprecated option when templating options \([https\://github\.com/ansible\-collections/community\.proxmox/pull/108](https\://github\.com/ansible\-collections/community\.proxmox/pull/108)\, [https\://github\.com/ansible\-collections/community\.general/pull/10553](https\://github\.com/ansible\-collections/community\.general/pull/10553)\)\.
* proxmox\_pct\_remote connection plugin \- avoid deprecated ansible\-core paramiko import helper\, import paramiko directly instead \([https\://github\.com/ansible\-collections/community\.proxmox/issues/146](https\://github\.com/ansible\-collections/community\.proxmox/issues/146)\, [https\://github\.com/ansible\-collections/community\.proxmox/pull/151](https\://github\.com/ansible\-collections/community\.proxmox/pull/151)\, [https\://github\.com/ansible\-collections/community\.general/pull/10553](https\://github\.com/ansible\-collections/community\.general/pull/10553)\)\.
* syspatch \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* sysrc \- use <code>shlex</code> to improve parsing of <code>sysrc \-e \-a</code> output \([https\://github\.com/ansible\-collections/community\.general/issues/10394](https\://github\.com/ansible\-collections/community\.general/issues/10394)\, [https\://github\.com/ansible\-collections/community\.general/pull/10400](https\://github\.com/ansible\-collections/community\.general/pull/10400)\)\.
* sysupgrade \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* wsl connection plugin \- avoid deprecated ansible\-core paramiko import helper\, import paramiko directly instead \([https\://github\.com/ansible\-collections/community\.general/issues/10515](https\://github\.com/ansible\-collections/community\.general/issues/10515)\, [https\://github\.com/ansible\-collections/community\.general/pull/10531](https\://github\.com/ansible\-collections/community\.general/pull/10531)\)\.
* zypper\_repository \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.

<a id="v10-7-2"></a>
## v10\.7\.2

<a id="release-summary-1"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-1"></a>
### Bugfixes

* dependent lookup plugin \- avoid deprecated ansible\-core 2\.19 functionality \([https\://github\.com/ansible\-collections/community\.general/pull/10359](https\://github\.com/ansible\-collections/community\.general/pull/10359)\)\.
* github\_release \- support multiple types of GitHub tokens\; no longer failing when <code>ghs\_</code> token type is provided \([https\://github\.com/ansible\-collections/community\.general/issues/10338](https\://github\.com/ansible\-collections/community\.general/issues/10338)\, [https\://github\.com/ansible\-collections/community\.general/pull/10339](https\://github\.com/ansible\-collections/community\.general/pull/10339)\)\.
* icinga2 inventory plugin \- avoid using deprecated option when templating options \([https\://github\.com/ansible\-collections/community\.general/pull/10271](https\://github\.com/ansible\-collections/community\.general/pull/10271)\)\.
* incus connection plugin \- fix error handling to return more useful Ansible errors to the user \([https\://github\.com/ansible\-collections/community\.general/issues/10344](https\://github\.com/ansible\-collections/community\.general/issues/10344)\, [https\://github\.com/ansible\-collections/community\.general/pull/10349](https\://github\.com/ansible\-collections/community\.general/pull/10349)\)\.
* linode inventory plugin \- avoid using deprecated option when templating options \([https\://github\.com/ansible\-collections/community\.general/pull/10271](https\://github\.com/ansible\-collections/community\.general/pull/10271)\)\.
* logstash callback plugin \- remove reference to Python 2 library \([https\://github\.com/ansible\-collections/community\.general/pull/10345](https\://github\.com/ansible\-collections/community\.general/pull/10345)\)\.

<a id="v10-7-1"></a>
## v10\.7\.1

<a id="release-summary-2"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes"></a>
### Minor Changes

* git\_config \- remove redundant <code>required\=False</code> from <code>argument\_spec</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10177](https\://github\.com/ansible\-collections/community\.general/pull/10177)\)\.
* proxmox\_snap \- correctly handle proxmox\_snap timeout parameter \([https\://github\.com/ansible\-collections/community\.proxmox/issues/73](https\://github\.com/ansible\-collections/community\.proxmox/issues/73)\, [https\://github\.com/ansible\-collections/community\.proxmox/issues/95](https\://github\.com/ansible\-collections/community\.proxmox/issues/95)\, [https\://github\.com/ansible\-collections/community\.general/pull/10176](https\://github\.com/ansible\-collections/community\.general/pull/10176)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* yaml callback plugin \- the YAML callback plugin was deprecated for removal in community\.general 13\.0\.0\. Since it needs to use ansible\-core internals since ansible\-core 2\.19 that are changing a lot\, we will remove this plugin already from community\.general 12\.0\.0 to ease the maintenance burden \([https\://github\.com/ansible\-collections/community\.general/pull/10213](https\://github\.com/ansible\-collections/community\.general/pull/10213)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* cobbler\_system \- update minimum version number to avoid wrong comparisons that happen in some cases using LooseVersion class which results in TypeError \([https\://github\.com/ansible\-collections/community\.general/issues/8506](https\://github\.com/ansible\-collections/community\.general/issues/8506)\, [https\://github\.com/ansible\-collections/community\.general/pull/10145](https\://github\.com/ansible\-collections/community\.general/pull/10145)\, [https\://github\.com/ansible\-collections/community\.general/pull/10178](https\://github\.com/ansible\-collections/community\.general/pull/10178)\)\.
* gitlab\_group\_access\_token\, gitlab\_project\_access\_token \- fix handling of group and project access tokens for changes in GitLab 17\.10 \([https\://github\.com/ansible\-collections/community\.general/pull/10196](https\://github\.com/ansible\-collections/community\.general/pull/10196)\)\.
* keycloak \- update more than 10 sub\-groups \([https\://github\.com/ansible\-collections/community\.general/issues/9690](https\://github\.com/ansible\-collections/community\.general/issues/9690)\, [https\://github\.com/ansible\-collections/community\.general/pull/9692](https\://github\.com/ansible\-collections/community\.general/pull/9692)\)\.
* yaml callback plugin \- adjust to latest changes in ansible\-core devel \([https\://github\.com/ansible\-collections/community\.general/pull/10212](https\://github\.com/ansible\-collections/community\.general/pull/10212)\)\.
* yaml callback plugin \- when using ansible\-core 2\.19\.0b2 or newer\, uses a new utility provided by ansible\-core\. This allows us to remove all hacks and vendored code that was part of the plugin for ansible\-core versions with Data Tagging so far \([https\://github\.com/ansible\-collections/community\.general/pull/10242](https\://github\.com/ansible\-collections/community\.general/pull/10242)\)\.
* zypper\_repository \- make compatible with Python 3\.12\+ \([https\://github\.com/ansible\-collections/community\.general/issues/10222](https\://github\.com/ansible\-collections/community\.general/issues/10222)\, [https\://github\.com/ansible\-collections/community\.general/pull/10223](https\://github\.com/ansible\-collections/community\.general/pull/10223)\)\.
* zypper\_repository \- use <code>metalink</code> attribute to identify repositories without <code>\<url/\></code> element \([https\://github\.com/ansible\-collections/community\.general/issues/10224](https\://github\.com/ansible\-collections/community\.general/issues/10224)\, [https\://github\.com/ansible\-collections/community\.general/pull/10225](https\://github\.com/ansible\-collections/community\.general/pull/10225)\)\.

<a id="v10-7-0"></a>
## v10\.7\.0

<a id="release-summary-3"></a>
### Release Summary

Bugfix and feature release\.
Note that this is the final minor 10\.x\.0 release\.
The next release with new features will be 11\.0\.0\.
From now on\, there will only be bugfix 10\.7\.x releases for the community\.general 10 release train\.

<a id="minor-changes-1"></a>
### Minor Changes

* cobbler inventory plugin \- add <code>connection\_timeout</code> option to specify the connection timeout to the cobbler server \([https\://github\.com/ansible\-collections/community\.general/pull/11063](https\://github\.com/ansible\-collections/community\.general/pull/11063)\)\.
* cobbler inventory plugin \- add <code>facts\_level</code> option to allow requesting fully rendered variables for Cobbler systems \([https\://github\.com/ansible\-collections/community\.general/issues/9419](https\://github\.com/ansible\-collections/community\.general/issues/9419)\, [https\://github\.com/ansible\-collections/community\.general/pull/9975](https\://github\.com/ansible\-collections/community\.general/pull/9975)\)\.
* ini\_file \- modify an inactive option also when there are spaces in front of the comment symbol \([https\://github\.com/ansible\-collections/community\.general/pull/10102](https\://github\.com/ansible\-collections/community\.general/pull/10102)\, [https\://github\.com/ansible\-collections/community\.general/issues/8539](https\://github\.com/ansible\-collections/community\.general/issues/8539)\)\.
* pipx \- parameter <code>name</code> now accepts Python package specifiers \([https\://github\.com/ansible\-collections/community\.general/issues/7815](https\://github\.com/ansible\-collections/community\.general/issues/7815)\, [https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* pipx module\_utils \- filtering application list by name now happens in the modules \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* pipx\_info \- filtering application list by name now happens in the module  \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* The proxmox content \(modules and plugins\) is being moved to the [new collection community\.proxmox](https\://github\.com/ansible\-collections/community\.proxmox)\. In community\.general 11\.0\.0\, these modules and plugins will be replaced by deprecated redirections to community\.proxmox\. You need to explicitly install community\.proxmox\, for example with <code>ansible\-galaxy collection install community\.proxmox</code>\. We suggest to update your roles and playbooks to use the new FQCNs as soon as possible to avoid getting deprecation messages \([https\://github\.com/ansible\-collections/community\.general/pull/10109](https\://github\.com/ansible\-collections/community\.general/pull/10109)\)\.
* pipx module\_utils \- function <code>make\_process\_list\(\)</code> is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* cobbler\_system \- fix bug with Cobbler \>\= 3\.4\.0 caused by giving more than 2 positional arguments to <code>CobblerXMLRPCInterface\.get\_system\_handle\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8506](https\://github\.com/ansible\-collections/community\.general/issues/8506)\, [https\://github\.com/ansible\-collections/community\.general/pull/10145](https\://github\.com/ansible\-collections/community\.general/pull/10145)\)\.
* kdeconfig \- allow option values beginning with a dash \([https\://github\.com/ansible\-collections/community\.general/issues/10127](https\://github\.com/ansible\-collections/community\.general/issues/10127)\, [https\://github\.com/ansible\-collections/community\.general/pull/10128](https\://github\.com/ansible\-collections/community\.general/pull/10128)\)\.
* keycloak\_user\_rolemapping \- fix <code>\-\-diff</code> mode \([https\://github\.com/ansible\-collections/community\.general/issues/10067](https\://github\.com/ansible\-collections/community\.general/issues/10067)\, [https\://github\.com/ansible\-collections/community\.general/pull/10075](https\://github\.com/ansible\-collections/community\.general/pull/10075)\)\.
* pickle cache plugin \- avoid extra JSON serialization with ansible\-core \>\= 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10136](https\://github\.com/ansible\-collections/community\.general/pull/10136)\)\.
* proxmox \- fix crash in module when the used on an existing LXC container with <code>state\=present</code> and <code>force\=true</code> \([https\://github\.com/ansible\-collections/community\.proxmox/pull/91](https\://github\.com/ansible\-collections/community\.proxmox/pull/91)\, [https\://github\.com/ansible\-collections/community\.general/pull/10155](https\://github\.com/ansible\-collections/community\.general/pull/10155)\)\.
* rundeck\_acl\_policy \- ensure that project ACLs are sent to the correct endpoint \([https\://github\.com/ansible\-collections/community\.general/pull/10097](https\://github\.com/ansible\-collections/community\.general/pull/10097)\)\.
* sysrc \- split the output of <code>sysrc \-e \-a</code> on the first <code>\=</code> only \([https\://github\.com/ansible\-collections/community\.general/issues/10120](https\://github\.com/ansible\-collections/community\.general/issues/10120)\, [https\://github\.com/ansible\-collections/community\.general/pull/10121](https\://github\.com/ansible\-collections/community\.general/pull/10121)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="callback"></a>
#### Callback

* community\.general\.print\_task \- Prints playbook task snippet to job output\.

<a id="filter"></a>
#### Filter

* community\.general\.to\_prettytable \- Format a list of dictionaries as an ASCII table\.

<a id="new-modules"></a>
### New Modules

* community\.general\.xdg\_mime \- Set default handler for MIME types\, for applications using XDG tools\.

<a id="v10-6-0"></a>
## v10\.6\.0

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-2"></a>
### Minor Changes

* apache2\_module \- added workaround for new PHP module name\, from <code>php7\_module</code> to <code>php\_module</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9951](https\://github\.com/ansible\-collections/community\.general/pull/9951)\)\.
* gitlab\_project \- add option <code>build\_timeout</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9960](https\://github\.com/ansible\-collections/community\.general/pull/9960)\)\.
* gitlab\_project\_members \- extend choices parameter <code>access\_level</code> by missing upstream valid value <code>owner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9953](https\://github\.com/ansible\-collections/community\.general/pull/9953)\)\.
* hpilo\_boot \- add option to get an idempotent behavior while powering on server\, resulting in success instead of failure when using <code>state\: boot\_once</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9646](https\://github\.com/ansible\-collections/community\.general/pull/9646)\)\.
* idrac\_redfish\_command\, idrac\_redfish\_config\, idrac\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* ilo\_redfish\_command\, ilo\_redfish\_config\, ilo\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* keycloak module\_utils \- user groups can now be referenced by their name\, like <code>staff</code>\, or their path\, like <code>/staff/engineering</code>\. The path syntax allows users to reference subgroups\, which is not possible otherwise \([https\://github\.com/ansible\-collections/community\.general/pull/9898](https\://github\.com/ansible\-collections/community\.general/pull/9898)\)\.
* keycloak\_user module \- user groups can now be referenced by their name\, like <code>staff</code>\, or their path\, like <code>/staff/engineering</code>\. The path syntax allows users to reference subgroups\, which is not possible otherwise \([https\://github\.com/ansible\-collections/community\.general/pull/9898](https\://github\.com/ansible\-collections/community\.general/pull/9898)\)\.
* nmcli \- add support for Infiniband MAC setting when <code>type</code> is <code>infiniband</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9962](https\://github\.com/ansible\-collections/community\.general/pull/9962)\)\.
* one\_vm \- update allowed values for <code>updateconf</code> to include new parameters as per the latest OpenNebula API documentation\.
  Added parameters\:

  - <code>OS</code>\: <code>FIRMWARE</code>\;
  - <code>CPU\_MODEL</code>\: <code>MODEL</code>\, <code>FEATURES</code>\;
  - <code>FEATURES</code>\: <code>VIRTIO\_BLK\_QUEUES</code>\, <code>VIRTIO\_SCSI\_QUEUES</code>\, <code>IOTHREADS</code>\;
  - <code>GRAPHICS</code>\: <code>PORT</code>\, <code>COMMAND</code>\;
  - <code>VIDEO</code>\: <code>ATS</code>\, <code>IOMMU</code>\, <code>RESOLUTION</code>\, <code>TYPE</code>\, <code>VRAM</code>\;
  - <code>RAW</code>\: <code>VALIDATE</code>\;
  - <code>BACKUP\_CONFIG</code>\: <code>FS\_FREEZE</code>\, <code>KEEP\_LAST</code>\, <code>BACKUP\_VOLATILE</code>\, <code>MODE</code>\, <code>INCREMENT\_MODE</code>\.

  \([https\://github\.com/ansible\-collections/community\.general/pull/9959](https\://github\.com/ansible\-collections/community\.general/pull/9959)\)\.
* proxmox and proxmox\_kvm modules \- allow uppercase characters in VM/container tags \([https\://github\.com/ansible\-collections/community\.general/issues/9895](https\://github\.com/ansible\-collections/community\.general/issues/9895)\, [https\://github\.com/ansible\-collections/community\.general/pull/10024](https\://github\.com/ansible\-collections/community\.general/pull/10024)\)\.
* puppet \- improve parameter formatting\, no impact to user \([https\://github\.com/ansible\-collections/community\.general/pull/10014](https\://github\.com/ansible\-collections/community\.general/pull/10014)\)\.
* redfish module utils \- add <code>REDFISH\_COMMON\_ARGUMENT\_SPEC</code>\, a corresponding <code>redfish</code> docs fragment\, and support for its <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* redfish\_command\, redfish\_config\, redfish\_info \- add <code>validate\_certs</code> and <code>ca\_path</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* rocketchat \- fix duplicate JSON conversion for Rocket\.Chat \< 7\.4\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9965](https\://github\.com/ansible\-collections/community\.general/pull/9965)\)\.
* wdc\_redfish\_command\, wdc\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* xcc\_redfish\_command \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* zypper \- adds <code>skip\_post\_errors</code> that allows to skip RPM post\-install errors \(Zypper return code 107\) \([https\://github\.com/ansible\-collections/community\.general/issues/9972](https\://github\.com/ansible\-collections/community\.general/issues/9972)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* manifold lookup plugin \- plugin is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10028](https\://github\.com/ansible\-collections/community\.general/pull/10028)\)\.
* stackpath\_compute inventory plugin \- plugin is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10026](https\://github\.com/ansible\-collections/community\.general/pull/10026)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* dependent look plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* diy callback plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* github\_deploy\_key \- check that key really exists on 422 to avoid masking other errors \([https\://github\.com/ansible\-collections/community\.general/issues/6718](https\://github\.com/ansible\-collections/community\.general/issues/6718)\, [https\://github\.com/ansible\-collections/community\.general/pull/10011](https\://github\.com/ansible\-collections/community\.general/pull/10011)\)\.
* hashids and unicode\_normalize filter plugins \- avoid deprecated <code>AnsibleFilterTypeError</code> on ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/9992](https\://github\.com/ansible\-collections/community\.general/pull/9992)\)\.
* homebrew \- emit a useful error message if <code>brew info</code> reports a package tap is <code>null</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10013](https\://github\.com/ansible\-collections/community\.general/pull/10013)\, [https\://github\.com/ansible\-collections/community\.general/issues/10012](https\://github\.com/ansible\-collections/community\.general/issues/10012)\)\.
* java\_cert \- the module no longer fails if the optional parameters <code>pkcs12\_alias</code> and <code>cert\_alias</code> are not provided \([https\://github\.com/ansible\-collections/community\.general/pull/9970](https\://github\.com/ansible\-collections/community\.general/pull/9970)\)\.
* keycloak\_authentication \- fix authentification config duplication for Keycloak \< 26\.2\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9987](https\://github\.com/ansible\-collections/community\.general/pull/9987)\)\.
* keycloak\_client \- fix the idempotency regression by normalizing the Keycloak response for <code>after\_client</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9905](https\://github\.com/ansible\-collections/community\.general/issues/9905)\, [https\://github\.com/ansible\-collections/community\.general/pull/9976](https\://github\.com/ansible\-collections/community\.general/pull/9976)\)\.
* proxmox inventory plugin \- fix <code>ansible\_host</code> staying empty for certain Proxmox nodes \([https\://github\.com/ansible\-collections/community\.general/issues/5906](https\://github\.com/ansible\-collections/community\.general/issues/5906)\, [https\://github\.com/ansible\-collections/community\.general/pull/9952](https\://github\.com/ansible\-collections/community\.general/pull/9952)\)\.
* proxmox\_disk \- fail gracefully if <code>storage</code> is required but not provided by the user \([https\://github\.com/ansible\-collections/community\.general/issues/9941](https\://github\.com/ansible\-collections/community\.general/issues/9941)\, [https\://github\.com/ansible\-collections/community\.general/pull/9963](https\://github\.com/ansible\-collections/community\.general/pull/9963)\)\.
* reveal\_ansible\_type filter plugin and ansible\_type test plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* sysrc \- no longer always reporting <code>changed\=true</code> when <code>state\=absent</code>\. This fixes the method <code>exists\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10004](https\://github\.com/ansible\-collections/community\.general/issues/10004)\, [https\://github\.com/ansible\-collections/community\.general/pull/10005](https\://github\.com/ansible\-collections/community\.general/pull/10005)\)\.
* yaml callback plugin \- use ansible\-core internals to avoid breakage with Data Tagging \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.

<a id="known-issues"></a>
### Known Issues

* reveal\_ansible\_type filter plugin and ansible\_type test plugin \- note that ansible\-core\'s Data Tagging feature implements new aliases\, such as <code>\_AnsibleTaggedStr</code> for <code>str</code>\, <code>\_AnsibleTaggedInt</code> for <code>int</code>\, and <code>\_AnsibleTaggedFloat</code> for <code>float</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="connection"></a>
#### Connection

* community\.general\.wsl \- Run tasks in WSL distribution using wsl\.exe CLI via SSH\.

<a id="v10-5-0"></a>
## v10\.5\.0

<a id="release-summary-5"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-3"></a>
### Minor Changes

* CmdRunner module utils \- the convenience method <code>cmd\_runner\_fmt\.as\_fixed\(\)</code> now accepts multiple arguments as a list \([https\://github\.com/ansible\-collections/community\.general/pull/9893](https\://github\.com/ansible\-collections/community\.general/pull/9893)\)\.
* apache2\_mod\_proxy \- code simplification\, no change in functionality \([https\://github\.com/ansible\-collections/community\.general/pull/9457](https\://github\.com/ansible\-collections/community\.general/pull/9457)\)\.
* consul\_token \- fix idempotency when <code>policies</code> or <code>roles</code> are supplied by name \([https\://github\.com/ansible\-collections/community\.general/issues/9841](https\://github\.com/ansible\-collections/community\.general/issues/9841)\, [https\://github\.com/ansible\-collections/community\.general/pull/9845](https\://github\.com/ansible\-collections/community\.general/pull/9845)\)\.
* keycloak\_realm \- remove ID requirement when creating a realm to allow Keycloak generating its own realm ID \([https\://github\.com/ansible\-collections/community\.general/pull/9768](https\://github\.com/ansible\-collections/community\.general/pull/9768)\)\.
* nmap inventory plugin \- adds <code>dns\_servers</code> option for specifying DNS servers for name resolution\. Accepts hostnames or IP addresses in the same format as the <code>exclude</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9849](https\://github\.com/ansible\-collections/community\.general/pull/9849)\)\.
* proxmox\_kvm \- add missing audio hardware device handling \([https\://github\.com/ansible\-collections/community\.general/issues/5192](https\://github\.com/ansible\-collections/community\.general/issues/5192)\, [https\://github\.com/ansible\-collections/community\.general/pull/9847](https\://github\.com/ansible\-collections/community\.general/pull/9847)\)\.
* redfish\_config \- add command <code>SetPowerRestorePolicy</code> to set the desired power state of the system when power is restored \([https\://github\.com/ansible\-collections/community\.general/pull/9837](https\://github\.com/ansible\-collections/community\.general/pull/9837)\)\.
* redfish\_info \- add command <code>GetPowerRestorePolicy</code> to get the desired power state of the system when power is restored \([https\://github\.com/ansible\-collections/community\.general/pull/9824](https\://github\.com/ansible\-collections/community\.general/pull/9824)\)\.
* rocketchat \- option <code>is\_pre740</code> has been added to control the format of the payload\. For Rocket\.Chat 7\.4\.0 or newer\, it must be set to <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9882](https\://github\.com/ansible\-collections/community\.general/pull/9882)\)\.
* slack callback plugin \- add <code>http\_agent</code> option to enable the user to set a custom user agent for slack callback plugin \([https\://github\.com/ansible\-collections/community\.general/issues/9813](https\://github\.com/ansible\-collections/community\.general/issues/9813)\, [https\://github\.com/ansible\-collections/community\.general/pull/9836](https\://github\.com/ansible\-collections/community\.general/pull/9836)\)\.
* systemd\_info \- add wildcard expression support in <code>unitname</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9821](https\://github\.com/ansible\-collections/community\.general/pull/9821)\)\.
* systemd\_info \- extend support to timer units \([https\://github\.com/ansible\-collections/community\.general/pull/9891](https\://github\.com/ansible\-collections/community\.general/pull/9891)\)\.
* vmadm \- add new options <code>flexible\_disk\_size</code> and <code>owner\_uuid</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9892](https\://github\.com/ansible\-collections/community\.general/pull/9892)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* cloudlare\_dns \- handle exhausted response stream in case of HTTP errors to show nice error message to the user \([https\://github\.com/ansible\-collections/community\.general/issues/9782](https\://github\.com/ansible\-collections/community\.general/issues/9782)\, [https\://github\.com/ansible\-collections/community\.general/pull/9818](https\://github\.com/ansible\-collections/community\.general/pull/9818)\)\.
* dnf\_versionlock \- add support for dnf5 \([https\://github\.com/ansible\-collections/community\.general/issues/9556](https\://github\.com/ansible\-collections/community\.general/issues/9556)\)\.
* homebrew \- fix crash when package names include tap \([https\://github\.com/ansible\-collections/community\.general/issues/9777](https\://github\.com/ansible\-collections/community\.general/issues/9777)\, [https\://github\.com/ansible\-collections/community\.general/pull/9803](https\://github\.com/ansible\-collections/community\.general/pull/9803)\)\.
* homebrew\_cask \- handle unusual brew version strings \([https\://github\.com/ansible\-collections/community\.general/issues/8432](https\://github\.com/ansible\-collections/community\.general/issues/8432)\, [https\://github\.com/ansible\-collections/community\.general/pull/9881](https\://github\.com/ansible\-collections/community\.general/pull/9881)\)\.
* nmcli \- enable changing only the order of DNS servers or search suffixes \([https\://github\.com/ansible\-collections/community\.general/issues/8724](https\://github\.com/ansible\-collections/community\.general/issues/8724)\, [https\://github\.com/ansible\-collections/community\.general/pull/9880](https\://github\.com/ansible\-collections/community\.general/pull/9880)\)\.
* proxmox \- add missing key selection of <code>\'status\'</code> key to <code>get\_lxc\_status</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9696](https\://github\.com/ansible\-collections/community\.general/issues/9696)\, [https\://github\.com/ansible\-collections/community\.general/pull/9809](https\://github\.com/ansible\-collections/community\.general/pull/9809)\)\.
* proxmox\_vm\_info \- the module no longer expects that the key <code>template</code> exists in a dictionary returned by Proxmox \([https\://github\.com/ansible\-collections/community\.general/issues/9875](https\://github\.com/ansible\-collections/community\.general/issues/9875)\, [https\://github\.com/ansible\-collections/community\.general/pull/9910](https\://github\.com/ansible\-collections/community\.general/pull/9910)\)\.
* sudoers \- display stdout and stderr raised while failed validation \([https\://github\.com/ansible\-collections/community\.general/issues/9674](https\://github\.com/ansible\-collections/community\.general/issues/9674)\, [https\://github\.com/ansible\-collections/community\.general/pull/9871](https\://github\.com/ansible\-collections/community\.general/pull/9871)\)\.

<a id="new-modules-1"></a>
### New Modules

* community\.general\.pacemaker\_resource \- Manage pacemaker resources\.

<a id="v10-4-0"></a>
## v10\.4\.0

<a id="release-summary-6"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* bitwarden lookup plugin \- add new option <code>collection\_name</code> to filter results by collection name\, and new option <code>result\_count</code> to validate number of results \([https\://github\.com/ansible\-collections/community\.general/pull/9728](https\://github\.com/ansible\-collections/community\.general/pull/9728)\)\.
* incus connection plugin \- adds <code>remote\_user</code> and <code>incus\_become\_method</code> parameters for allowing a non\-root user to connect to an Incus instance \([https\://github\.com/ansible\-collections/community\.general/pull/9743](https\://github\.com/ansible\-collections/community\.general/pull/9743)\)\.
* iocage inventory plugin \- the new parameter <code>hooks\_results</code> of the plugin is a list of files inside a jail that provide configuration parameters for the inventory\. The inventory plugin reads the files from the jails and put the contents into the items of created variable <code>iocage\_hooks</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9650](https\://github\.com/ansible\-collections/community\.general/issues/9650)\, [https\://github\.com/ansible\-collections/community\.general/pull/9651](https\://github\.com/ansible\-collections/community\.general/pull/9651)\)\.
* jira \- adds <code>client\_cert</code> and <code>client\_key</code> parameters for supporting client certificate authentification when connecting to Jira \([https\://github\.com/ansible\-collections/community\.general/pull/9753](https\://github\.com/ansible\-collections/community\.general/pull/9753)\)\.
* lldp \- adds <code>multivalues</code> parameter to control behavior when lldpctl outputs an attribute multiple times \([https\://github\.com/ansible\-collections/community\.general/pull/9657](https\://github\.com/ansible\-collections/community\.general/pull/9657)\)\.
* lvg \- add <code>remove\_extra\_pvs</code> parameter to control if ansible should remove physical volumes which are not in the <code>pvs</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/9698](https\://github\.com/ansible\-collections/community\.general/pull/9698)\)\.
* lxd connection plugin \- adds <code>remote\_user</code> and <code>lxd\_become\_method</code> parameters for allowing a non\-root user to connect to an LXD instance \([https\://github\.com/ansible\-collections/community\.general/pull/9659](https\://github\.com/ansible\-collections/community\.general/pull/9659)\)\.
* nmcli \- adds VRF support with new <code>type</code> value <code>vrf</code> and new <code>slave\_type</code> value <code>vrf</code> as well as new <code>table</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/9658](https\://github\.com/ansible\-collections/community\.general/pull/9658)\, [https\://github\.com/ansible\-collections/community\.general/issues/8014](https\://github\.com/ansible\-collections/community\.general/issues/8014)\)\.
* proxmox\_kvm \- allow hibernation and suspending of VMs \([https\://github\.com/ansible\-collections/community\.general/issues/9620](https\://github\.com/ansible\-collections/community\.general/issues/9620)\, [https\://github\.com/ansible\-collections/community\.general/pull/9653](https\://github\.com/ansible\-collections/community\.general/pull/9653)\)\.
* redfish\_command \- add <code>PowerFullPowerCycle</code> to power command options \([https\://github\.com/ansible\-collections/community\.general/pull/9729](https\://github\.com/ansible\-collections/community\.general/pull/9729)\)\.
* ssh\_config \- add <code>other\_options</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/8053](https\://github\.com/ansible\-collections/community\.general/issues/8053)\, [https\://github\.com/ansible\-collections/community\.general/pull/9684](https\://github\.com/ansible\-collections/community\.general/pull/9684)\)\.
* xen\_orchestra inventory plugin \- add <code>use\_vm\_uuid</code> and <code>use\_host\_uuid</code> boolean options to allow switching over to using VM/Xen name labels instead of UUIDs as item names \([https\://github\.com/ansible\-collections/community\.general/pull/9787](https\://github\.com/ansible\-collections/community\.general/pull/9787)\)\.

<a id="deprecated-features-3"></a>
### Deprecated Features

* profitbricks \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_datacenter \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_nic \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_volume \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_volume\_attachments \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.

<a id="bugfixes-6"></a>
### Bugfixes

* apache2\_mod\_proxy \- make compatible with Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* apache2\_mod\_proxy \- passing the cluster\'s page as referer for the member\'s pages\. This makes the module actually work again for halfway modern Apache versions\. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* elasticsearch\_plugin \- fix <code>ERROR\: D is not a recognized option</code> issue when configuring proxy settings \([https\://github\.com/ansible\-collections/community\.general/pull/9774](https\://github\.com/ansible\-collections/community\.general/pull/9774)\, [https\://github\.com/ansible\-collections/community\.general/issues/9773](https\://github\.com/ansible\-collections/community\.general/issues/9773)\)\.
* ipa\_host \- module revoked existing host certificates even if <code>user\_certificate</code> was not given \([https\://github\.com/ansible\-collections/community\.general/pull/9694](https\://github\.com/ansible\-collections/community\.general/pull/9694)\)\.
* keycloak\_client \- in check mode\, detect whether the lists in before client \(for example redirect URI list\) contain items that the lists in the desired client do not contain \([https\://github\.com/ansible\-collections/community\.general/pull/9739](https\://github\.com/ansible\-collections/community\.general/pull/9739)\)\.
* lldp \- fix crash caused by certain lldpctl output where an attribute is defined as branch and leaf \([https\://github\.com/ansible\-collections/community\.general/pull/9657](https\://github\.com/ansible\-collections/community\.general/pull/9657)\)\.
* onepassword\_doc lookup plugin \- ensure that 1Password Connect support also works for this plugin \([https\://github\.com/ansible\-collections/community\.general/pull/9625](https\://github\.com/ansible\-collections/community\.general/pull/9625)\)\.
* passwordstore lookup plugin \- fix subkey creation even when <code>create\=false</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9105](https\://github\.com/ansible\-collections/community\.general/issues/9105)\, [https\://github\.com/ansible\-collections/community\.general/pull/9106](https\://github\.com/ansible\-collections/community\.general/pull/9106)\)\.
* proxmox inventory plugin \- plugin did not update cache correctly after <code>meta\: refresh\_inventory</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9710](https\://github\.com/ansible\-collections/community\.general/issues/9710)\, [https\://github\.com/ansible\-collections/community\.general/pull/9760](https\://github\.com/ansible\-collections/community\.general/pull/9760)\)\.
* redhat\_subscription \- use the \"enable\_content\" option \(when available\) when
  registering using D\-Bus\, to ensure that subscription\-manager enables the
  content on registration\; this is particular important on EL 10\+ and Fedora
  41\+
  \([https\://github\.com/ansible\-collections/community\.general/pull/9778](https\://github\.com/ansible\-collections/community\.general/pull/9778)\)\.
* zfs \- fix handling of multi\-line values of user\-defined ZFS properties \([https\://github\.com/ansible\-collections/community\.general/pull/6264](https\://github\.com/ansible\-collections/community\.general/pull/6264)\)\.
* zfs\_facts \- parameter <code>type</code> now accepts multple values as documented \([https\://github\.com/ansible\-collections/community\.general/issues/5909](https\://github\.com/ansible\-collections/community\.general/issues/5909)\, [https\://github\.com/ansible\-collections/community\.general/pull/9697](https\://github\.com/ansible\-collections/community\.general/pull/9697)\)\.

<a id="new-modules-2"></a>
### New Modules

* community\.general\.systemd\_info \- Gather C\(systemd\) unit info\.

<a id="v10-3-1"></a>
## v10\.3\.1

<a id="release-summary-7"></a>
### Release Summary

Bugfix release\.

<a id="minor-changes-5"></a>
### Minor Changes

* onepassword\_ssh\_key \- refactor to move code to lookup class \([https\://github\.com/ansible\-collections/community\.general/pull/9633](https\://github\.com/ansible\-collections/community\.general/pull/9633)\)\.

<a id="bugfixes-7"></a>
### Bugfixes

* cloudflare\_dns \- fix crash when deleting a DNS record or when updating a record with <code>solo\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9652](https\://github\.com/ansible\-collections/community\.general/issues/9652)\, [https\://github\.com/ansible\-collections/community\.general/pull/9649](https\://github\.com/ansible\-collections/community\.general/pull/9649)\)\.
* homebrew \- make package name parsing more resilient \([https\://github\.com/ansible\-collections/community\.general/pull/9665](https\://github\.com/ansible\-collections/community\.general/pull/9665)\, [https\://github\.com/ansible\-collections/community\.general/issues/9641](https\://github\.com/ansible\-collections/community\.general/issues/9641)\)\.
* keycloak module utils \- replaces missing return in get\_role\_composites method which caused it to return None instead of composite roles \([https\://github\.com/ansible\-collections/community\.general/issues/9678](https\://github\.com/ansible\-collections/community\.general/issues/9678)\, [https\://github\.com/ansible\-collections/community\.general/pull/9691](https\://github\.com/ansible\-collections/community\.general/pull/9691)\)\.
* keycloak\_client \- fix and improve existing tests\. The module showed a diff without actual changes\, solved by improving the <code>normalise\_cr\(\)</code> function \([https\://github\.com/ansible\-collections/community\.general/pull/9644](https\://github\.com/ansible\-collections/community\.general/pull/9644)\)\.
* proxmox \- adds the <code>pubkey</code> parameter \(back to\) the <code>update</code> state \([https\://github\.com/ansible\-collections/community\.general/issues/9642](https\://github\.com/ansible\-collections/community\.general/issues/9642)\, [https\://github\.com/ansible\-collections/community\.general/pull/9645](https\://github\.com/ansible\-collections/community\.general/pull/9645)\)\.
* proxmox \- fixes a typo in the translation of the <code>pubkey</code> parameter to proxmox\' <code>ssh\-public\-keys</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9642](https\://github\.com/ansible\-collections/community\.general/issues/9642)\, [https\://github\.com/ansible\-collections/community\.general/pull/9645](https\://github\.com/ansible\-collections/community\.general/pull/9645)\)\.
* xml \- ensure file descriptor is closed \([https\://github\.com/ansible\-collections/community\.general/pull/9695](https\://github\.com/ansible\-collections/community\.general/pull/9695)\)\.

<a id="v10-3-0"></a>
## v10\.3\.0

<a id="release-summary-8"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-6"></a>
### Minor Changes

* MH module utils \- delegate <code>debug</code> to the underlying <code>AnsibleModule</code> instance or issues a warning if an attribute already exists with that name \([https\://github\.com/ansible\-collections/community\.general/pull/9577](https\://github\.com/ansible\-collections/community\.general/pull/9577)\)\.
* apache2\_mod\_proxy \- better handling regexp extraction \([https\://github\.com/ansible\-collections/community\.general/pull/9609](https\://github\.com/ansible\-collections/community\.general/pull/9609)\)\.
* apache2\_mod\_proxy \- change type of <code>state</code> to a list of strings\. No change for the users \([https\://github\.com/ansible\-collections/community\.general/pull/9600](https\://github\.com/ansible\-collections/community\.general/pull/9600)\)\.
* apache2\_mod\_proxy \- improve readability when using results from <code>fecth\_url\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9608](https\://github\.com/ansible\-collections/community\.general/pull/9608)\)\.
* apache2\_mod\_proxy \- refactor repeated code into method \([https\://github\.com/ansible\-collections/community\.general/pull/9599](https\://github\.com/ansible\-collections/community\.general/pull/9599)\)\.
* apache2\_mod\_proxy \- remove unused parameter and code from <code>Balancer</code> constructor \([https\://github\.com/ansible\-collections/community\.general/pull/9614](https\://github\.com/ansible\-collections/community\.general/pull/9614)\)\.
* apache2\_mod\_proxy \- simplified and improved string manipulation \([https\://github\.com/ansible\-collections/community\.general/pull/9614](https\://github\.com/ansible\-collections/community\.general/pull/9614)\)\.
* apache2\_mod\_proxy \- use <code>deps</code> to handle dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/9612](https\://github\.com/ansible\-collections/community\.general/pull/9612)\)\.
* cgroup\_memory\_recap callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* chroot connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* cloud\_init\_data\_facts \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* cobbler inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* context\_demo callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* counter filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* counter\_enabled callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* cpanm \- enable usage of option <code>\-\-with\-recommends</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9554](https\://github\.com/ansible\-collections/community\.general/issues/9554)\, [https\://github\.com/ansible\-collections/community\.general/pull/9555](https\://github\.com/ansible\-collections/community\.general/pull/9555)\)\.
* cpanm \- enable usage of option <code>\-\-with\-suggests</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9555](https\://github\.com/ansible\-collections/community\.general/pull/9555)\)\.
* crc32 filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* cronvar \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* crypttab \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* default\_without\_diff callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dense callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dict filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* dict\_kv filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* diy callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* doas become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dzdo become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* elastic callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* from\_csv filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* from\_ini filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* funcd connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* gitlab\_runners inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* groupby\_as\_dict filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* hashids filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* icinga2 inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* incus connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* iocage connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* iocage inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* iocage inventory plugin \- the new parameter <code>sudo</code> of the plugin lets the command <code>iocage list \-l</code> to run as root on the iocage host\. This is needed to get the IPv4 of a running DHCP jail \([https\://github\.com/ansible\-collections/community\.general/issues/9572](https\://github\.com/ansible\-collections/community\.general/issues/9572)\, [https\://github\.com/ansible\-collections/community\.general/pull/9573](https\://github\.com/ansible\-collections/community\.general/pull/9573)\)\.
* iptables\_state action plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* jabber callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* jail connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* jc filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* jira \- transition operation now has <code>status\_id</code> to directly reference wanted transition \([https\://github\.com/ansible\-collections/community\.general/pull/9602](https\://github\.com/ansible\-collections/community\.general/pull/9602)\)\.
* json\_query filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* keep\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* keycloak\_\* modules \- <code>refresh\_token</code> parameter added\. When multiple authentication parameters are provided \(<code>token</code>\, <code>refresh\_token</code>\, and <code>auth\_username</code>/<code>auth\_password</code>\)\, modules will now automatically retry requests upon authentication errors \(401\)\, using in order the token\, refresh token\, and username/password \([https\://github\.com/ansible\-collections/community\.general/pull/9494](https\://github\.com/ansible\-collections/community\.general/pull/9494)\)\.
* known\_hosts \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* ksu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* linode inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lists filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* lists\_mergeby filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* log\_plays callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* loganalytics callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* logdna callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* logentries callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* logstash callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* lxc connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lxd connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lxd inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* machinectl become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* mail callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* memcached cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* nmap inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* nmcli \- add a option <code>fail\_over\_mac</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9570](https\://github\.com/ansible\-collections/community\.general/issues/9570)\, [https\://github\.com/ansible\-collections/community\.general/pull/9571](https\://github\.com/ansible\-collections/community\.general/pull/9571)\)\.
* nrdp callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* null callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* one\_template \- adds <code>filter</code> option for retrieving templates which are not owned by the user \([https\://github\.com/ansible\-collections/community\.general/pull/9547](https\://github\.com/ansible\-collections/community\.general/pull/9547)\, [https\://github\.com/ansible\-collections/community\.general/issues/9278](https\://github\.com/ansible\-collections/community\.general/issues/9278)\)\.
* online inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* opennebula inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* opentelemetry callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* parted \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* pbrun become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pfexec become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pickle cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pmrun become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* proxmox \- refactors the proxmox module \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\)\.
* proxmox inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* proxmox\_pct\_remote connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* proxmox\_template \- add support for checksum validation with new options <code>checksum\_algorithm</code> and <code>checksum</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9553](https\://github\.com/ansible\-collections/community\.general/issues/9553)\, [https\://github\.com/ansible\-collections/community\.general/pull/9601](https\://github\.com/ansible\-collections/community\.general/pull/9601)\)\.
* pulp\_repo \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* qubes connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* random\_mac filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* redfish\_info \- add command <code>GetAccountServiceConfig</code> to get full information about AccountService configuration \([https\://github\.com/ansible\-collections/community\.general/pull/9403](https\://github\.com/ansible\-collections/community\.general/pull/9403)\)\.
* redhat\_subscription \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* redis cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* remove\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* replace\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* reveal\_ansible\_type filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* run0 become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* saltstack connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* say callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* scaleway inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* selective callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* sesu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* shutdown action plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* slack callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* snap \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9598](https\://github\.com/ansible\-collections/community\.general/pull/9598)\)\.
* snap\_alias \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9598](https\://github\.com/ansible\-collections/community\.general/pull/9598)\)\.
* solaris\_zone \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* sorcery \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* splunk callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* stackpath\_compute inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* sudosu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* sumologic callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* syslog\_json callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* time filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* timestamp callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* timezone \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* to\_ini filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* ufw \- add support for <code>vrrp</code> protocol \([https\://github\.com/ansible\-collections/community\.general/issues/9562](https\://github\.com/ansible\-collections/community\.general/issues/9562)\, [https\://github\.com/ansible\-collections/community\.general/pull/9582](https\://github\.com/ansible\-collections/community\.general/pull/9582)\)\.
* unicode\_normalize filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* unixy callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* version\_sort filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* virtualbox inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* xen\_orchestra inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* yaml cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* yaml callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* zone connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.

<a id="deprecated-features-4"></a>
### Deprecated Features

* MH module utils \- attribute <code>debug</code> definition in subclasses of MH is now deprecated\, as that name will become a delegation to <code>AnsibleModule</code> in community\.general 12\.0\.0\, and any such attribute will be overridden by that delegation in that version \([https\://github\.com/ansible\-collections/community\.general/pull/9577](https\://github\.com/ansible\-collections/community\.general/pull/9577)\)\.
* proxmox \- removes default value <code>false</code> of <code>update</code> parameter\. This will be changed to a default of <code>true</code> in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\)\.

<a id="security-fixes"></a>
### Security Fixes

* keycloak\_client \- Sanitize <code>saml\.encryption\.private\.key</code> so it does not show in the logs \([https\://github\.com/ansible\-collections/community\.general/pull/9621](https\://github\.com/ansible\-collections/community\.general/pull/9621)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* homebrew \- fix incorrect handling of homebrew modules when a tap is requested \([https\://github\.com/ansible\-collections/community\.general/pull/9546](https\://github\.com/ansible\-collections/community\.general/pull/9546)\, [https\://github\.com/ansible\-collections/community\.general/issues/9533](https\://github\.com/ansible\-collections/community\.general/issues/9533)\)\.
* iocage inventory plugin \- the plugin parses the IP4 tab of the jails list and put the elements into the new variable <code>iocage\_ip4\_dict</code>\. In multiple interface format the variable <code>iocage\_ip4</code> keeps the comma\-separated list of IP4 \([https\://github\.com/ansible\-collections/community\.general/issues/9538](https\://github\.com/ansible\-collections/community\.general/issues/9538)\)\.
* pipx \- honor option <code>global</code> when <code>state\=latest</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9623](https\://github\.com/ansible\-collections/community\.general/pull/9623)\)\.
* proxmox \- fixes idempotency of template conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\, [https\://github\.com/ansible\-collections/community\.general/issues/8811](https\://github\.com/ansible\-collections/community\.general/issues/8811)\)\.
* proxmox \- fixes incorrect parsing for bind\-only mounts \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\, [https\://github\.com/ansible\-collections/community\.general/issues/8982](https\://github\.com/ansible\-collections/community\.general/issues/8982)\)\.
* proxmox \- fixes issues with disk\_volume variable \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\, [https\://github\.com/ansible\-collections/community\.general/issues/9065](https\://github\.com/ansible\-collections/community\.general/issues/9065)\)\.
* proxmox module utils \- fixes ignoring of <code>choose\_first\_if\_multiple</code> argument in <code>get\_vmid</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9225](https\://github\.com/ansible\-collections/community\.general/pull/9225)\)\.
* redhat\_subscription \- do not try to unsubscribe \(i\.e\. remove subscriptions\)
  when unregistering a system\: newer versions of subscription\-manager\, as
  available in EL 10 and Fedora 41\+\, do not support entitlements anymore\, and
  thus unsubscribing will fail
  \([https\://github\.com/ansible\-collections/community\.general/pull/9578](https\://github\.com/ansible\-collections/community\.general/pull/9578)\)\.

<a id="new-plugins-2"></a>
### New Plugins

<a id="connection-1"></a>
#### Connection

* community\.general\.proxmox\_pct\_remote \- Run tasks in Proxmox LXC container instances using pct CLI via SSH\.

<a id="filter-1"></a>
#### Filter

* community\.general\.json\_diff \- Create a JSON patch by comparing two JSON files\.
* community\.general\.json\_patch \- Apply a JSON\-Patch \(RFC 6902\) operation to an object\.
* community\.general\.json\_patch\_recipe \- Apply JSON\-Patch \(RFC 6902\) operations to an object\.

<a id="lookup"></a>
#### Lookup

* community\.general\.onepassword\_ssh\_key \- Fetch SSH keys stored in 1Password\.

<a id="new-modules-3"></a>
### New Modules

* community\.general\.proxmox\_backup\_info \- Retrieve information on Proxmox scheduled backups\.

<a id="v10-2-0"></a>
## v10\.2\.0

<a id="release-summary-9"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-7"></a>
### Minor Changes

* bitwarden lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* cgroup\_memory\_recap callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* chef\_databag lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* chroot connection plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* chroot connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* cobbler inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* cobbler inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* collection\_version lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* consul\_kv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* context\_demo callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* counter\_enabled callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* credstash lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* cyberarkpassword lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* cyberarkpassword lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* dense callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* dependent lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* dig lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* dig lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* diy callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* dnstxt lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* dnstxt lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* doas become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* dsv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* dzdo become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* elastic callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* etcd lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* etcd3 lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* etcd3 lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* filetree lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* from\_csv filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* from\_ini filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* funcd connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* github\_app\_access\_token lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* gitlab\_instance\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/9425](https\://github\.com/ansible\-collections/community\.general/pull/9425)\)\.
* gitlab\_runners inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* gitlab\_runners inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* hiera lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* icinga2 inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* incus connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* iocage connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* iocage inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* iptables\_state action plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9318](https\://github\.com/ansible\-collections/community\.general/pull/9318)\)\.
* jabber callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* jail connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* keycloak \- add an action group for Keycloak modules to allow <code>module\_defaults</code> to be set for Keycloak tasks \([https\://github\.com/ansible\-collections/community\.general/pull/9284](https\://github\.com/ansible\-collections/community\.general/pull/9284)\)\.
* keyring lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* ksu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* lastpass lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* linode inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* lmdb\_kv lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* lmdb\_kv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* locale\_gen \- invert the logic to determine <code>ubuntu\_mode</code>\, making it look first for <code>/etc/locale\.gen</code> \(set <code>ubuntu\_mode</code> to <code>False</code>\) and only then looking for <code>/var/lib/locales/supported\.d/</code> \(set <code>ubuntu\_mode</code> to <code>True</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\, [https\://github\.com/ansible\-collections/community\.general/issues/9131](https\://github\.com/ansible\-collections/community\.general/issues/9131)\, [https\://github\.com/ansible\-collections/community\.general/issues/8487](https\://github\.com/ansible\-collections/community\.general/issues/8487)\)\.
* locale\_gen \- new return value <code>mechanism</code> to better express the semantics of the <code>ubuntu\_mode</code>\, with the possible values being either <code>glibc</code> \(<code>ubuntu\_mode\=False</code>\) or <code>ubuntu\_legacy</code> \(<code>ubuntu\_mode\=True</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\)\.
* log\_plays callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* loganalytics callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* logdna callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* logentries callback plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* logentries callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* lxc connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* lxd connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* lxd inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* lxd inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* machinectl become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* mail callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* manageiq\_alert\_profiles \- improve handling of parameter requirements \([https\://github\.com/ansible\-collections/community\.general/pull/9449](https\://github\.com/ansible\-collections/community\.general/pull/9449)\)\.
* manifold lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* manifold lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* memcached cache plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9320](https\://github\.com/ansible\-collections/community\.general/pull/9320)\)\.
* merge\_variables lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* nmap inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* nmap inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* nrdp callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* onepassword lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* onepassword lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* onepassword\_doc lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* online inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* opennebula inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* opennebula inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* opentelemetry callback plugin \- remove code handling Python versions prior to 3\.7 \([https\://github\.com/ansible\-collections/community\.general/pull/9482](https\://github\.com/ansible\-collections/community\.general/pull/9482)\)\.
* opentelemetry callback plugin \- remove code handling Python versions prior to 3\.7 \([https\://github\.com/ansible\-collections/community\.general/pull/9503](https\://github\.com/ansible\-collections/community\.general/pull/9503)\)\.
* opentelemetry callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* pacemaker\_cluster \- remove unused code \([https\://github\.com/ansible\-collections/community\.general/pull/9471](https\://github\.com/ansible\-collections/community\.general/pull/9471)\)\.
* pacemaker\_cluster \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/9471](https\://github\.com/ansible\-collections/community\.general/pull/9471)\)\.
* passwordstore lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* pbrun become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* pfexec become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* pmrun become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* proxmox inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* proxmox inventory plugin \- strip whitespace from <code>user</code>\, <code>token\_id</code>\, and <code>token\_secret</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9227](https\://github\.com/ansible\-collections/community\.general/issues/9227)\, [https\://github\.com/ansible\-collections/community\.general/pull/9228/](https\://github\.com/ansible\-collections/community\.general/pull/9228/)\)\.
* proxmox inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* proxmox module utils \- add method <code>api\_task\_complete</code> that can wait for task completion and return error message \([https\://github\.com/ansible\-collections/community\.general/pull/9256](https\://github\.com/ansible\-collections/community\.general/pull/9256)\)\.
* proxmox\_backup \- refactor permission checking to improve code readability and maintainability \([https\://github\.com/ansible\-collections/community\.general/pull/9239](https\://github\.com/ansible\-collections/community\.general/pull/9239)\)\.
* qubes connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* random\_pet lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* redis cache plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* redis cache plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9320](https\://github\.com/ansible\-collections/community\.general/pull/9320)\)\.
* redis lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* revbitspss lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* saltstack connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* say callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* scaleway inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* scaleway inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* selective callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* sesu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* shelvefile lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* shutdown action plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* shutdown action plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9318](https\://github\.com/ansible\-collections/community\.general/pull/9318)\)\.
* slack callback plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* slack callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* splunk callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* stackpath\_compute inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* sudosu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* timestamp callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* to\_ini filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* tss lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* tss lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* unixy callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* virtualbox inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* virtualbox inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* xbps \- add <code>root</code> and <code>repository</code> options to enable bootstrapping new void installations \([https\://github\.com/ansible\-collections/community\.general/pull/9174](https\://github\.com/ansible\-collections/community\.general/pull/9174)\)\.
* xen\_orchestra inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* xfconf \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9226](https\://github\.com/ansible\-collections/community\.general/pull/9226)\)\.
* xfconf\_info \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9226](https\://github\.com/ansible\-collections/community\.general/pull/9226)\)\.
* yaml callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* zone connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* zypper \- add <code>quiet</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9270](https\://github\.com/ansible\-collections/community\.general/pull/9270)\)\.
* zypper \- add <code>simple\_errors</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9270](https\://github\.com/ansible\-collections/community\.general/pull/9270)\)\.

<a id="deprecated-features-5"></a>
### Deprecated Features

* atomic\_container \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* atomic\_host \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* atomic\_image \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* facter \- module is deprecated and will be removed in community\.general 12\.0\.0\, use <code>community\.general\.facter\_facts</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9451](https\://github\.com/ansible\-collections/community\.general/pull/9451)\)\.
* locale\_gen \- <code>ubuntu\_mode\=True</code>\, or <code>mechanism\=ubuntu\_legacy</code> is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\)\.
* pure module utils \- the module utils is deprecated and will be removed from community\.general 12\.0\.0\. The modules using this were removed in community\.general 3\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9432](https\://github\.com/ansible\-collections/community\.general/pull/9432)\)\.
* purestorage doc fragments \- the doc fragment is deprecated and will be removed from community\.general 12\.0\.0\. The modules using this were removed in community\.general 3\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9432](https\://github\.com/ansible\-collections/community\.general/pull/9432)\)\.
* sensu\_check \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_client \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_handler \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_silence \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_subscription \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* slack \- the default value <code>auto</code> of the <code>prepend\_hash</code> option is deprecated and will change to <code>never</code> in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9443](https\://github\.com/ansible\-collections/community\.general/pull/9443)\)\.
* yaml callback plugin \- deprecate plugin in favor of <code>result\_format\=yaml</code> in plugin <code>ansible\.bulitin\.default</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9456](https\://github\.com/ansible\-collections/community\.general/pull/9456)\)\.

<a id="security-fixes-1"></a>
### Security Fixes

* keycloak\_authentication \- API calls did not properly set the <code>priority</code> during update resulting in incorrectly sorted authentication flows\. This apparently only affects Keycloak 25 or newer \([https\://github\.com/ansible\-collections/community\.general/pull/9263](https\://github\.com/ansible\-collections/community\.general/pull/9263)\)\.

<a id="bugfixes-9"></a>
### Bugfixes

* dig lookup plugin \- correctly handle <code>NoNameserver</code> exception \([https\://github\.com/ansible\-collections/community\.general/pull/9363](https\://github\.com/ansible\-collections/community\.general/pull/9363)\, [https\://github\.com/ansible\-collections/community\.general/issues/9362](https\://github\.com/ansible\-collections/community\.general/issues/9362)\)\.
* homebrew \- fix incorrect handling of aliased homebrew modules when the alias is requested \([https\://github\.com/ansible\-collections/community\.general/pull/9255](https\://github\.com/ansible\-collections/community\.general/pull/9255)\, [https\://github\.com/ansible\-collections/community\.general/issues/9240](https\://github\.com/ansible\-collections/community\.general/issues/9240)\)\.
* htpasswd \- report changes when file permissions are adjusted \([https\://github\.com/ansible\-collections/community\.general/issues/9485](https\://github\.com/ansible\-collections/community\.general/issues/9485)\, [https\://github\.com/ansible\-collections/community\.general/pull/9490](https\://github\.com/ansible\-collections/community\.general/pull/9490)\)\.
* proxmox\_backup \- fix incorrect key lookup in vmid permission check \([https\://github\.com/ansible\-collections/community\.general/pull/9223](https\://github\.com/ansible\-collections/community\.general/pull/9223)\)\.
* proxmox\_disk \- fix async method and make <code>resize\_disk</code> method handle errors correctly \([https\://github\.com/ansible\-collections/community\.general/pull/9256](https\://github\.com/ansible\-collections/community\.general/pull/9256)\)\.
* proxmox\_template \- fix the wrong path called on <code>proxmox\_template\.task\_status</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9276](https\://github\.com/ansible\-collections/community\.general/issues/9276)\, [https\://github\.com/ansible\-collections/community\.general/pull/9277](https\://github\.com/ansible\-collections/community\.general/pull/9277)\)\.
* qubes connection plugin \- fix the printing of debug information \([https\://github\.com/ansible\-collections/community\.general/pull/9334](https\://github\.com/ansible\-collections/community\.general/pull/9334)\)\.
* redfish\_utils module utils \- Fix <code>VerifyBiosAttributes</code> command on multi system resource nodes \([https\://github\.com/ansible\-collections/community\.general/pull/9234](https\://github\.com/ansible\-collections/community\.general/pull/9234)\)\.

<a id="new-plugins-3"></a>
### New Plugins

<a id="inventory"></a>
#### Inventory

* community\.general\.iocage \- iocage inventory source\.

<a id="new-modules-4"></a>
### New Modules

* community\.general\.android\_sdk \- Manages Android SDK packages\.
* community\.general\.ldap\_inc \- Use the Modify\-Increment LDAP V3 feature to increment an attribute value\.
* community\.general\.systemd\_creds\_decrypt \- C\(systemd\)\'s C\(systemd\-creds decrypt\) plugin\.
* community\.general\.systemd\_creds\_encrypt \- C\(systemd\)\'s C\(systemd\-creds encrypt\) plugin\.

<a id="v10-1-0"></a>
## v10\.1\.0

<a id="release-summary-10"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-8"></a>
### Minor Changes

* alternatives \- add <code>family</code> parameter that allows to utilize the <code>\-\-family</code> option available in RedHat version of update\-alternatives \([https\://github\.com/ansible\-collections/community\.general/issues/5060](https\://github\.com/ansible\-collections/community\.general/issues/5060)\, [https\://github\.com/ansible\-collections/community\.general/pull/9096](https\://github\.com/ansible\-collections/community\.general/pull/9096)\)\.
* cloudflare\_dns \- add support for <code>comment</code> and <code>tags</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9132](https\://github\.com/ansible\-collections/community\.general/pull/9132)\)\.
* deps module utils \- add <code>deps\.clear\(\)</code> to clear out previously declared dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/9179](https\://github\.com/ansible\-collections/community\.general/pull/9179)\)\.
* homebrew \- greatly speed up module when multiple packages are passed in the <code>name</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9181](https\://github\.com/ansible\-collections/community\.general/pull/9181)\)\.
* homebrew \- remove duplicated package name validation \([https\://github\.com/ansible\-collections/community\.general/pull/9076](https\://github\.com/ansible\-collections/community\.general/pull/9076)\)\.
* iso\_extract \- adds <code>password</code> parameter that is passed to 7z \([https\://github\.com/ansible\-collections/community\.general/pull/9159](https\://github\.com/ansible\-collections/community\.general/pull/9159)\)\.
* launchd \- add <code>plist</code> option for services such as sshd\, where the plist filename doesn\'t match the service name \([https\://github\.com/ansible\-collections/community\.general/pull/9102](https\://github\.com/ansible\-collections/community\.general/pull/9102)\)\.
* nmcli \- add <code>sriov</code> parameter that enables support for SR\-IOV settings \([https\://github\.com/ansible\-collections/community\.general/pull/9168](https\://github\.com/ansible\-collections/community\.general/pull/9168)\)\.
* pipx \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9180](https\://github\.com/ansible\-collections/community\.general/pull/9180)\)\.
* pipx\_info \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9180](https\://github\.com/ansible\-collections/community\.general/pull/9180)\)\.
* proxmox\_template \- add server side artifact fetching support \([https\://github\.com/ansible\-collections/community\.general/pull/9113](https\://github\.com/ansible\-collections/community\.general/pull/9113)\)\.
* redfish\_command \- add <code>update\_custom\_oem\_header</code>\, <code>update\_custom\_oem\_params</code>\, and <code>update\_custom\_oem\_mime\_type</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/9123](https\://github\.com/ansible\-collections/community\.general/pull/9123)\)\.
* redfish\_utils module utils \- remove redundant code \([https\://github\.com/ansible\-collections/community\.general/pull/9190](https\://github\.com/ansible\-collections/community\.general/pull/9190)\)\.
* rpm\_ostree\_pkg \- added the options <code>apply\_live</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9167](https\://github\.com/ansible\-collections/community\.general/pull/9167)\)\.
* rpm\_ostree\_pkg \- added the return value <code>needs\_reboot</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9167](https\://github\.com/ansible\-collections/community\.general/pull/9167)\)\.
* scaleway\_lb \- minor simplification in the code \([https\://github\.com/ansible\-collections/community\.general/pull/9189](https\://github\.com/ansible\-collections/community\.general/pull/9189)\)\.
* ssh\_config \- add <code>dynamicforward</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9192](https\://github\.com/ansible\-collections/community\.general/pull/9192)\)\.

<a id="deprecated-features-6"></a>
### Deprecated Features

* opkg \- deprecate value <code>\"\"</code> for parameter <code>force</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9172](https\://github\.com/ansible\-collections/community\.general/pull/9172)\)\.
* redfish\_utils module utils \- deprecate method <code>RedfishUtils\.\_init\_session\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9190](https\://github\.com/ansible\-collections/community\.general/pull/9190)\)\.

<a id="bugfixes-10"></a>
### Bugfixes

* dnf\_config\_manager \- fix hanging when prompting to import GPG keys \([https\://github\.com/ansible\-collections/community\.general/pull/9124](https\://github\.com/ansible\-collections/community\.general/pull/9124)\, [https\://github\.com/ansible\-collections/community\.general/issues/8830](https\://github\.com/ansible\-collections/community\.general/issues/8830)\)\.
* dnf\_config\_manager \- forces locale to <code>C</code> before module starts\. If the locale was set to non\-English\, the output of the <code>dnf config\-manager</code> could not be parsed \([https\://github\.com/ansible\-collections/community\.general/pull/9157](https\://github\.com/ansible\-collections/community\.general/pull/9157)\, [https\://github\.com/ansible\-collections/community\.general/issues/9046](https\://github\.com/ansible\-collections/community\.general/issues/9046)\)\.
* flatpak \- force the locale language to <code>C</code> when running the flatpak command \([https\://github\.com/ansible\-collections/community\.general/pull/9187](https\://github\.com/ansible\-collections/community\.general/pull/9187)\, [https\://github\.com/ansible\-collections/community\.general/issues/8883](https\://github\.com/ansible\-collections/community\.general/issues/8883)\)\.
* gio\_mime \- fix command line when determining version of <code>gio</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9171](https\://github\.com/ansible\-collections/community\.general/pull/9171)\, [https\://github\.com/ansible\-collections/community\.general/issues/9158](https\://github\.com/ansible\-collections/community\.general/issues/9158)\)\.
* github\_key \- in check mode\, a faulty call to <code>\`datetime\.strftime\(\.\.\.\)\`</code> was being made which generated an exception \([https\://github\.com/ansible\-collections/community\.general/issues/9185](https\://github\.com/ansible\-collections/community\.general/issues/9185)\)\.
* homebrew\_cask \- allow <code>\+</code> symbol in Homebrew cask name validation regex \([https\://github\.com/ansible\-collections/community\.general/pull/9128](https\://github\.com/ansible\-collections/community\.general/pull/9128)\)\.
* keycloak\_clientscope\_type \- sort the default and optional clientscope lists to improve the diff \([https\://github\.com/ansible\-collections/community\.general/pull/9202](https\://github\.com/ansible\-collections/community\.general/pull/9202)\)\.
* slack \- fail if Slack API response is not OK with error message \([https\://github\.com/ansible\-collections/community\.general/pull/9198](https\://github\.com/ansible\-collections/community\.general/pull/9198)\)\.

<a id="new-plugins-4"></a>
### New Plugins

<a id="filter-2"></a>
#### Filter

* community\.general\.accumulate \- Produce a list of accumulated sums of the input list contents\.

<a id="new-modules-5"></a>
### New Modules

* community\.general\.decompress \- Decompresses compressed files\.
* community\.general\.proxmox\_backup \- Start a VM backup in Proxmox VE cluster\.

<a id="v10-0-1"></a>
## v10\.0\.1

<a id="release-summary-11"></a>
### Release Summary

Bugfix release for inclusion in Ansible 11\.0\.0rc1\.

<a id="bugfixes-11"></a>
### Bugfixes

* keycloak\_client \- fix diff by removing code that turns the attributes dict which contains additional settings into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9077](https\://github\.com/ansible\-collections/community\.general/pull/9077)\)\.
* keycloak\_clientscope \- fix diff and <code>end\_state</code> by removing the code that turns the attributes dict\, which contains additional config items\, into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9082](https\://github\.com/ansible\-collections/community\.general/pull/9082)\)\.
* redfish\_utils module utils \- remove undocumented default applytime \([https\://github\.com/ansible\-collections/community\.general/pull/9114](https\://github\.com/ansible\-collections/community\.general/pull/9114)\)\.

<a id="v10-0-0"></a>
## v10\.0\.0

<a id="release-summary-12"></a>
### Release Summary

This is release 10\.0\.0 of <code>community\.general</code>\, released on 2024\-11\-04\.

<a id="minor-changes-9"></a>
### Minor Changes

* CmdRunner module util \- argument formats can be specified as plain functions without calling <code>cmd\_runner\_fmt\.as\_func\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8479](https\://github\.com/ansible\-collections/community\.general/pull/8479)\)\.
* CmdRunner module utils \- the parameter <code>force\_lang</code> now supports the special value <code>auto</code> which will automatically try and determine the best parsable locale in the system \([https\://github\.com/ansible\-collections/community\.general/pull/8517](https\://github\.com/ansible\-collections/community\.general/pull/8517)\)\.
* MH module utils \- add parameter <code>when</code> to <code>cause\_changes</code> decorator \([https\://github\.com/ansible\-collections/community\.general/pull/8766](https\://github\.com/ansible\-collections/community\.general/pull/8766)\)\.
* MH module utils \- minor refactor in decorators \([https\://github\.com/ansible\-collections/community\.general/pull/8766](https\://github\.com/ansible\-collections/community\.general/pull/8766)\)\.
* alternatives \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* ansible\_galaxy\_install \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9060](https\://github\.com/ansible\-collections/community\.general/pull/9060)\)\.
* ansible\_galaxy\_install \- add upgrade feature \([https\://github\.com/ansible\-collections/community\.general/pull/8431](https\://github\.com/ansible\-collections/community\.general/pull/8431)\, [https\://github\.com/ansible\-collections/community\.general/issues/8351](https\://github\.com/ansible\-collections/community\.general/issues/8351)\)\.
* ansible\_galaxy\_install \- minor refactor in the module \([https\://github\.com/ansible\-collections/community\.general/pull/8413](https\://github\.com/ansible\-collections/community\.general/pull/8413)\)\.
* apache2\_mod\_proxy \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* apache2\_mod\_proxy \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* cargo \- add option <code>directory</code>\, which allows source directory to be specified \([https\://github\.com/ansible\-collections/community\.general/pull/8480](https\://github\.com/ansible\-collections/community\.general/pull/8480)\)\.
* cgroup\_memory\_recap\, hipchat\, jabber\, log\_plays\, loganalytics\, logentries\, logstash\, slack\, splunk\, sumologic\, syslog\_json callback plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8628](https\://github\.com/ansible\-collections/community\.general/pull/8628)\)\.
* chef\_databag\, consul\_kv\, cyberarkpassword\, dsv\, etcd\, filetree\, hiera\, onepassword\, onepassword\_doc\, onepassword\_raw\, passwordstore\, redis\, shelvefile\, tss lookup plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8626](https\://github\.com/ansible\-collections/community\.general/pull/8626)\)\.
* chroot\, funcd\, incus\, iocage\, jail\, lxc\, lxd\, qubes\, zone connection plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8627](https\://github\.com/ansible\-collections/community\.general/pull/8627)\)\.
* cmd\_runner module utils \- add decorator <code>cmd\_runner\_fmt\.stack</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8415](https\://github\.com/ansible\-collections/community\.general/pull/8415)\)\.
* cmd\_runner module utils \- refactor argument formatting code to its own Python module \([https\://github\.com/ansible\-collections/community\.general/pull/8964](https\://github\.com/ansible\-collections/community\.general/pull/8964)\)\.
* cmd\_runner\_fmt module utils \- simplify implementation of <code>cmd\_runner\_fmt\.as\_bool\_not\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8512](https\://github\.com/ansible\-collections/community\.general/pull/8512)\)\.
* cobbler\, linode\, lxd\, nmap\, online\, scaleway\, stackpath\_compute\, virtualbox inventory plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8625](https\://github\.com/ansible\-collections/community\.general/pull/8625)\)\.
* consul\_acl \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* consul\_kv \- add argument for the datacenter option on Consul API \([https\://github\.com/ansible\-collections/community\.general/pull/9026](https\://github\.com/ansible\-collections/community\.general/pull/9026)\)\.
* copr \- Added <code>includepkgs</code> and <code>excludepkgs</code> parameters to limit the list of packages fetched or excluded from the repository\([https\://github\.com/ansible\-collections/community\.general/pull/8779](https\://github\.com/ansible\-collections/community\.general/pull/8779)\)\.
* cpanm \- add return value <code>cpanm\_version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9061](https\://github\.com/ansible\-collections/community\.general/pull/9061)\)\.
* credstash lookup plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* csv module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* deco MH module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* dig lookup plugin \- add <code>port</code> option to specify DNS server port \([https\://github\.com/ansible\-collections/community\.general/pull/8966](https\://github\.com/ansible\-collections/community\.general/pull/8966)\)\.
* django module utils \- always retrieve version \([https\://github\.com/ansible\-collections/community\.general/pull/9063](https\://github\.com/ansible\-collections/community\.general/pull/9063)\)\.
* django\_check \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9063](https\://github\.com/ansible\-collections/community\.general/pull/9063)\)\.
* django\_command \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9063](https\://github\.com/ansible\-collections/community\.general/pull/9063)\)\.
* django\_createcachetable \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9063](https\://github\.com/ansible\-collections/community\.general/pull/9063)\)\.
* doas\, dzdo\, ksu\, machinectl\, pbrun\, pfexec\, pmrun\, sesu\, sudosu become plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8623](https\://github\.com/ansible\-collections/community\.general/pull/8623)\)\.
* etcd3 \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* flatpak \- improve the parsing of Flatpak application IDs based on official guidelines \([https\://github\.com/ansible\-collections/community\.general/pull/8909](https\://github\.com/ansible\-collections/community\.general/pull/8909)\)\.
* gconftool2 \- make use of <code>ModuleHelper</code> features to simplify code \([https\://github\.com/ansible\-collections/community\.general/pull/8711](https\://github\.com/ansible\-collections/community\.general/pull/8711)\)\.
* gcontool2 \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9064](https\://github\.com/ansible\-collections/community\.general/pull/9064)\)\.
* gcontool2 module utils \- add argument formatter <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9064](https\://github\.com/ansible\-collections/community\.general/pull/9064)\)\.
* gcontool2\_info \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9064](https\://github\.com/ansible\-collections/community\.general/pull/9064)\)\.
* gio\_mime \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9067](https\://github\.com/ansible\-collections/community\.general/pull/9067)\)\.
* gio\_mime \- adjust code ahead of the old <code>VardDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8855](https\://github\.com/ansible\-collections/community\.general/pull/8855)\)\.
* gio\_mime \- mute the  old <code>VarDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8776](https\://github\.com/ansible\-collections/community\.general/pull/8776)\)\.
* gio\_mime module utils \- add argument formatter <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9067](https\://github\.com/ansible\-collections/community\.general/pull/9067)\)\.
* github\_app\_access\_token lookup plugin \- adds new <code>private\_key</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/8989](https\://github\.com/ansible\-collections/community\.general/pull/8989)\)\.
* gitlab\_deploy\_key \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_group \- add many new parameters \([https\://github\.com/ansible\-collections/community\.general/pull/8908](https\://github\.com/ansible\-collections/community\.general/pull/8908)\)\.
* gitlab\_group \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* gitlab\_issue \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_merge\_request \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* gitlab\_project \- add option <code>container\_expiration\_policy</code> to schedule container registry cleanup \([https\://github\.com/ansible\-collections/community\.general/pull/8674](https\://github\.com/ansible\-collections/community\.general/pull/8674)\)\.
* gitlab\_project \- add option <code>issues\_access\_level</code> to enable/disable project issues \([https\://github\.com/ansible\-collections/community\.general/pull/8760](https\://github\.com/ansible\-collections/community\.general/pull/8760)\)\.
* gitlab\_project \- add option <code>model\_registry\_access\_level</code> to disable model registry \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* gitlab\_project \- add option <code>pages\_access\_level</code> to disable project pages \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* gitlab\_project \- add option <code>repository\_access\_level</code> to disable project repository \([https\://github\.com/ansible\-collections/community\.general/pull/8674](https\://github\.com/ansible\-collections/community\.general/pull/8674)\)\.
* gitlab\_project \- add option <code>service\_desk\_enabled</code> to disable service desk \([https\://github\.com/ansible\-collections/community\.general/pull/8688](https\://github\.com/ansible\-collections/community\.general/pull/8688)\)\.
* gitlab\_project \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* gitlab\_project \- sorted parameters in order to avoid future merge conflicts \([https\://github\.com/ansible\-collections/community\.general/pull/8759](https\://github\.com/ansible\-collections/community\.general/pull/8759)\)\.
* gitlab\_runner \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* hashids filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* homebrew \- speed up brew install and upgrade \([https\://github\.com/ansible\-collections/community\.general/pull/9022](https\://github\.com/ansible\-collections/community\.general/pull/9022)\)\.
* hwc\_ecs\_instance \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_evs\_disk \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_eip \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_peering\_connect \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_port \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* hwc\_vpc\_subnet \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* icinga2\_host \- replace loop with dict comprehension \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* imc\_rest \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* ipa\_dnsrecord \- adds <code>SSHFP</code> record type for managing SSH fingerprints in FreeIPA DNS \([https\://github\.com/ansible\-collections/community\.general/pull/8404](https\://github\.com/ansible\-collections/community\.general/pull/8404)\)\.
* ipa\_otptoken \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* jenkins\_node \- add <code>offline\_message</code> parameter for updating a Jenkins node offline cause reason when the state is \"disabled\" \(offline\) \([https\://github\.com/ansible\-collections/community\.general/pull/9084](https\://github\.com/ansible\-collections/community\.general/pull/9084)\)\.\"
* jira \- adjust code ahead of the old <code>VardDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8856](https\://github\.com/ansible\-collections/community\.general/pull/8856)\)\.
* jira \- mute the  old <code>VarDict</code> deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/8776](https\://github\.com/ansible\-collections/community\.general/pull/8776)\)\.
* jira \- replace deprecated params when using decorator <code>cause\_changes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8791](https\://github\.com/ansible\-collections/community\.general/pull/8791)\)\.
* keep\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* keycloak\_client \- add <code>client\-x509</code> choice to <code>client\_authenticator\_type</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8973](https\://github\.com/ansible\-collections/community\.general/pull/8973)\)\.
* keycloak\_client \- assign auth flow by name \([https\://github\.com/ansible\-collections/community\.general/pull/8428](https\://github\.com/ansible\-collections/community\.general/pull/8428)\)\.
* keycloak\_client \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_clientscope \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_identity\_provider \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_realm \- add boolean toggle to configure organization support for a given keycloak realm \([https\://github\.com/ansible\-collections/community\.general/issues/9027](https\://github\.com/ansible\-collections/community\.general/issues/9027)\, [https\://github\.com/ansible\-collections/community\.general/pull/8927/](https\://github\.com/ansible\-collections/community\.general/pull/8927/)\)\.
* keycloak\_user\_federation \- add module argument allowing users to optout of the removal of unspecified mappers\, for example to keep the keycloak default mappers \([https\://github\.com/ansible\-collections/community\.general/pull/8764](https\://github\.com/ansible\-collections/community\.general/pull/8764)\)\.
* keycloak\_user\_federation \- add the user federation config parameter <code>referral</code> to the module arguments \([https\://github\.com/ansible\-collections/community\.general/pull/8954](https\://github\.com/ansible\-collections/community\.general/pull/8954)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* keycloak\_user\_federation \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* linode \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* locale\_gen \- add support for multiple locales \([https\://github\.com/ansible\-collections/community\.general/issues/8677](https\://github\.com/ansible\-collections/community\.general/issues/8677)\, [https\://github\.com/ansible\-collections/community\.general/pull/8682](https\://github\.com/ansible\-collections/community\.general/pull/8682)\)\.
* lxc\_container \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* lxd\_container \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* manageiq\_provider \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* mattermost \- adds support for message priority \([https\://github\.com/ansible\-collections/community\.general/issues/9068](https\://github\.com/ansible\-collections/community\.general/issues/9068)\, [https\://github\.com/ansible\-collections/community\.general/pull/9087](https\://github\.com/ansible\-collections/community\.general/pull/9087)\)\.
* memcached\, pickle\, redis\, yaml cache plugins \- make sure that all options are typed \([https\://github\.com/ansible\-collections/community\.general/pull/8624](https\://github\.com/ansible\-collections/community\.general/pull/8624)\)\.
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
* ocapi\_utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* one\_image \- add <code>create</code>\, <code>template</code> and <code>datastore\_id</code> arguments for image creation \([https\://github\.com/ansible\-collections/community\.general/pull/9075](https\://github\.com/ansible\-collections/community\.general/pull/9075)\)\.
* one\_image \- add <code>wait\_timeout</code> argument for adjustable timeouts \([https\://github\.com/ansible\-collections/community\.general/pull/9075](https\://github\.com/ansible\-collections/community\.general/pull/9075)\)\.
* one\_image \- add option <code>persistent</code> to manage image persistence \([https\://github\.com/ansible\-collections/community\.general/issues/3578](https\://github\.com/ansible\-collections/community\.general/issues/3578)\, [https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image \- extend xsd scheme to make it return a lot more info about image \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image \- refactor code to make it more similar to <code>one\_template</code> and <code>one\_vnet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image\_info \- extend xsd scheme to make it return a lot more info about image \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_image\_info \- refactor code to make it more similar to <code>one\_template</code> and <code>one\_vnet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8889](https\://github\.com/ansible\-collections/community\.general/pull/8889)\)\.
* one\_service \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* one\_vm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* onepassword lookup plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* open\_iscsi \- allow login to a portal with multiple targets without specifying any of them \([https\://github\.com/ansible\-collections/community\.general/pull/8719](https\://github\.com/ansible\-collections/community\.general/pull/8719)\)\.
* openbsd\_pkg \- adds diff support to show changes in installed package list\. This does not yet work for check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8402](https\://github\.com/ansible\-collections/community\.general/pull/8402)\)\.
* opennebula\.py \- add VM <code>id</code> and VM <code>host</code> to inventory host data \([https\://github\.com/ansible\-collections/community\.general/pull/8532](https\://github\.com/ansible\-collections/community\.general/pull/8532)\)\.
* opentelemetry callback plugin \- fix default value for <code>store\_spans\_in\_file</code> causing traces to be produced to a file named <code>None</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8566](https\://github\.com/ansible\-collections/community\.general/issues/8566)\, [https\://github\.com/ansible\-collections/community\.general/pull/8741](https\://github\.com/ansible\-collections/community\.general/pull/8741)\)\.
* opkg \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9086](https\://github\.com/ansible\-collections/community\.general/pull/9086)\)\.
* passwordstore lookup plugin \- add subkey creation/update support \([https\://github\.com/ansible\-collections/community\.general/pull/8952](https\://github\.com/ansible\-collections/community\.general/pull/8952)\)\.
* passwordstore lookup plugin \- add the current user to the lockfile file name to address issues on multi\-user systems \([https\://github\.com/ansible\-collections/community\.general/pull/8689](https\://github\.com/ansible\-collections/community\.general/pull/8689)\)\.
* pids \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pipx \- add parameter <code>suffix</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8675](https\://github\.com/ansible\-collections/community\.general/pull/8675)\, [https\://github\.com/ansible\-collections/community\.general/issues/8656](https\://github\.com/ansible\-collections/community\.general/issues/8656)\)\.
* pipx \- added new states <code>install\_all</code>\, <code>uninject</code>\, <code>upgrade\_shared</code>\, <code>pin</code>\, and <code>unpin</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8809](https\://github\.com/ansible\-collections/community\.general/pull/8809)\)\.
* pipx \- added parameter <code>global</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx \- refactor out parsing of <code>pipx list</code> output to module utils \([https\://github\.com/ansible\-collections/community\.general/pull/9044](https\://github\.com/ansible\-collections/community\.general/pull/9044)\)\.
* pipx \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pipx\_info \- add new return value <code>pinned</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9044](https\://github\.com/ansible\-collections/community\.general/pull/9044)\)\.
* pipx\_info \- added parameter <code>global</code> to module \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx\_info \- refactor out parsing of <code>pipx list</code> output to module utils \([https\://github\.com/ansible\-collections/community\.general/pull/9044](https\://github\.com/ansible\-collections/community\.general/pull/9044)\)\.
* pipx\_info \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pkg5\_publisher \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* pkgng \- add option <code>use\_globs</code> \(default <code>true</code>\) to optionally disable glob patterns \([https\://github\.com/ansible\-collections/community\.general/issues/8632](https\://github\.com/ansible\-collections/community\.general/issues/8632)\, [https\://github\.com/ansible\-collections/community\.general/pull/8633](https\://github\.com/ansible\-collections/community\.general/pull/8633)\)\.
* proxmox \- add <code>disk\_volume</code> and <code>mount\_volumes</code> keys for better readability \([https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* proxmox \- allow specification of the API port when using proxmox\_\* \([https\://github\.com/ansible\-collections/community\.general/issues/8440](https\://github\.com/ansible\-collections/community\.general/issues/8440)\, [https\://github\.com/ansible\-collections/community\.general/pull/8441](https\://github\.com/ansible\-collections/community\.general/pull/8441)\)\.
* proxmox \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox \- translate the old <code>disk</code> and <code>mounts</code> keys to the new handling internally \([https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* proxmox inventory plugin \- add new fact for LXC interface details \([https\://github\.com/ansible\-collections/community\.general/pull/8713](https\://github\.com/ansible\-collections/community\.general/pull/8713)\)\.
* proxmox inventory plugin \- clean up authentication code \([https\://github\.com/ansible\-collections/community\.general/pull/8917](https\://github\.com/ansible\-collections/community\.general/pull/8917)\)\.
* proxmox inventory plugin \- fix urllib3 <code>InsecureRequestWarnings</code> not being suppressed when a token is used \([https\://github\.com/ansible\-collections/community\.general/pull/9099](https\://github\.com/ansible\-collections/community\.general/pull/9099)\)\.
* proxmox\_disk \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox\_kvm \- adds the <code>ciupgrade</code> parameter to specify whether cloud\-init should upgrade system packages at first boot \([https\://github\.com/ansible\-collections/community\.general/pull/9066](https\://github\.com/ansible\-collections/community\.general/pull/9066)\)\.
* proxmox\_kvm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* proxmox\_kvm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* proxmox\_template \- small refactor in logic for determining whether a template exists or not \([https\://github\.com/ansible\-collections/community\.general/pull/8516](https\://github\.com/ansible\-collections/community\.general/pull/8516)\)\.
* proxmox\_vm\_info \- add <code>network</code> option to retrieve current network information \([https\://github\.com/ansible\-collections/community\.general/pull/8471](https\://github\.com/ansible\-collections/community\.general/pull/8471)\)\.
* redfish\_\* modules \- adds <code>ciphers</code> option for custom cipher selection \([https\://github\.com/ansible\-collections/community\.general/pull/8533](https\://github\.com/ansible\-collections/community\.general/pull/8533)\)\.
* redfish\_command \- add <code>UpdateUserAccountTypes</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/9058](https\://github\.com/ansible\-collections/community\.general/issues/9058)\, [https\://github\.com/ansible\-collections/community\.general/pull/9059](https\://github\.com/ansible\-collections/community\.general/pull/9059)\)\.
* redfish\_command \- add <code>wait</code> and <code>wait\_timeout</code> options to allow a user to block a command until a service is accessible after performing the requested command \([https\://github\.com/ansible\-collections/community\.general/issues/8051](https\://github\.com/ansible\-collections/community\.general/issues/8051)\, [https\://github\.com/ansible\-collections/community\.general/pull/8434](https\://github\.com/ansible\-collections/community\.general/pull/8434)\)\.
* redfish\_command \- add handling of the <code>PasswordChangeRequired</code> message from services in the <code>UpdateUserPassword</code> command to directly modify the user\'s password if the requested user is the one invoking the operation \([https\://github\.com/ansible\-collections/community\.general/issues/8652](https\://github\.com/ansible\-collections/community\.general/issues/8652)\, [https\://github\.com/ansible\-collections/community\.general/pull/8653](https\://github\.com/ansible\-collections/community\.general/pull/8653)\)\.
* redfish\_confg \- remove <code>CapacityBytes</code> from required paramaters of the <code>CreateVolume</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/8956](https\://github\.com/ansible\-collections/community\.general/pull/8956)\)\.
* redfish\_config \- add parameter <code>storage\_none\_volume\_deletion</code> to <code>CreateVolume</code> command in order to control the automatic deletion of non\-RAID volumes \([https\://github\.com/ansible\-collections/community\.general/pull/8990](https\://github\.com/ansible\-collections/community\.general/pull/8990)\)\.
* redfish\_info \- add command <code>CheckAvailability</code> to check if a service is accessible \([https\://github\.com/ansible\-collections/community\.general/issues/8051](https\://github\.com/ansible\-collections/community\.general/issues/8051)\, [https\://github\.com/ansible\-collections/community\.general/pull/8434](https\://github\.com/ansible\-collections/community\.general/pull/8434)\)\.
* redfish\_info \- adds <code>RedfishURI</code> and <code>StorageId</code> to Disk inventory \([https\://github\.com/ansible\-collections/community\.general/pull/8937](https\://github\.com/ansible\-collections/community\.general/pull/8937)\)\.
* redfish\_utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* redfish\_utils module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* redfish\_utils module utils \- schedule a BIOS configuration job at next reboot when the BIOS config is changed \([https\://github\.com/ansible\-collections/community\.general/pull/9012](https\://github\.com/ansible\-collections/community\.general/pull/9012)\)\.
* redis cache plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* redis\, redis\_info \- add <code>client\_cert</code> and <code>client\_key</code> options to specify path to certificate for Redis authentication  \([https\://github\.com/ansible\-collections/community\.general/pull/8654](https\://github\.com/ansible\-collections/community\.general/pull/8654)\)\.
* redis\_info \- adds support for getting cluster info \([https\://github\.com/ansible\-collections/community\.general/pull/8464](https\://github\.com/ansible\-collections/community\.general/pull/8464)\)\.
* remove\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* replace\_keys filter plugin \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* scaleway \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* scaleway\_compute \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
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
* scaleway\_ip \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_lb \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_security\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* scaleway\_security\_group \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* scaleway\_user\_data \- better construct when using <code>dict\.items\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* scaleway\_user\_data \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* sensu\_silence \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* snmp\_facts \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* sorcery \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8833](https\://github\.com/ansible\-collections/community\.general/pull/8833)\)\.
* sudosu become plugin \- added an option \(<code>alt\_method</code>\) to enhance compatibility with more versions of <code>su</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8214](https\://github\.com/ansible\-collections/community\.general/pull/8214)\)\.
* udm\_dns\_record \- replace loop with <code>dict\.update\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8876](https\://github\.com/ansible\-collections/community\.general/pull/8876)\)\.
* ufw \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* unsafe plugin utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* vardict module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* vars MH module utils \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8814](https\://github\.com/ansible\-collections/community\.general/pull/8814)\)\.
* virtualbox inventory plugin \- expose a new parameter <code>enable\_advanced\_group\_parsing</code> to change how the VirtualBox dynamic inventory parses VM groups \([https\://github\.com/ansible\-collections/community\.general/issues/8508](https\://github\.com/ansible\-collections/community\.general/issues/8508)\, [https\://github\.com/ansible\-collections/community\.general/pull/8510](https\://github\.com/ansible\-collections/community\.general/pull/8510)\)\.
* vmadm \- replace Python 2\.6 construct with dict comprehensions \([https\://github\.com/ansible\-collections/community\.general/pull/8822](https\://github\.com/ansible\-collections/community\.general/pull/8822)\)\.
* wdc\_redfish\_command \- minor change to handle upgrade file for Redfish WD platforms \([https\://github\.com/ansible\-collections/community\.general/pull/8444](https\://github\.com/ansible\-collections/community\.general/pull/8444)\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* The collection no longer supports ansible\-core 2\.13 and ansible\-core 2\.14\. While most \(or even all\) modules and plugins might still work with these versions\, they are no longer tested in CI and breakages regarding them will not be fixed \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* cmd\_runner module utils \- CLI arguments created directly from module parameters are no longer assigned a default formatter \([https\://github\.com/ansible\-collections/community\.general/pull/8928](https\://github\.com/ansible\-collections/community\.general/pull/8928)\)\.
* irc \- the defaults of <code>use\_tls</code> and <code>validate\_certs</code> changed from <code>false</code> to <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.
* rhsm\_repository \- the states <code>present</code> and <code>absent</code> have been removed\. Use <code>enabled</code> and <code>disabled</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.

<a id="deprecated-features-7"></a>
### Deprecated Features

* CmdRunner module util \- setting the value of the <code>ignore\_none</code> parameter within a <code>CmdRunner</code> context is deprecated and that feature should be removed in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8479](https\://github\.com/ansible\-collections/community\.general/pull/8479)\)\.
* MH decorator cause\_changes module utils \- deprecate parameters <code>on\_success</code> and <code>on\_failure</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8791](https\://github\.com/ansible\-collections/community\.general/pull/8791)\)\.
* git\_config \- the <code>list\_all</code> option has been deprecated and will be removed in community\.general 11\.0\.0\. Use the <code>community\.general\.git\_config\_info</code> module instead \([https\://github\.com/ansible\-collections/community\.general/pull/8453](https\://github\.com/ansible\-collections/community\.general/pull/8453)\)\.
* git\_config \- using <code>state\=present</code> without providing <code>value</code> is deprecated and will be disallowed in community\.general 11\.0\.0\. Use the <code>community\.general\.git\_config\_info</code> module instead to read a value \([https\://github\.com/ansible\-collections/community\.general/pull/8453](https\://github\.com/ansible\-collections/community\.general/pull/8453)\)\.
* hipchat \- the hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020\. The module is therefore deprecated and will be removed from community\.general 11\.0\.0 if nobody provides compelling reasons to still keep it \([https\://github\.com/ansible\-collections/community\.general/pull/8919](https\://github\.com/ansible\-collections/community\.general/pull/8919)\)\.
* pipx \- support for versions of the command line tool <code>pipx</code> older than <code>1\.7\.0</code> is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.
* pipx\_info \- support for versions of the command line tool <code>pipx</code> older than <code>1\.7\.0</code> is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/8793](https\://github\.com/ansible\-collections/community\.general/pull/8793)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* The consul\_acl module has been removed\. Use community\.general\.consul\_token and/or community\.general\.consul\_policy instead \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* The hipchat callback plugin has been removed\. The hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020 \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* The redhat module utils has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* The rhn\_channel module has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* The rhn\_register module has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/8921](https\://github\.com/ansible\-collections/community\.general/pull/8921)\)\.
* consul \- removed the <code>ack\_params\_state\_absent</code> option\. It had no effect anymore \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.
* ejabberd\_user \- removed the <code>logging</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.
* gitlab modules \- remove basic auth feature \([https\://github\.com/ansible\-collections/community\.general/pull/8405](https\://github\.com/ansible\-collections/community\.general/pull/8405)\)\.
* proxmox\_kvm \- removed the <code>proxmox\_default\_behavior</code> option\. Explicitly specify the old default values if you were using <code>proxmox\_default\_behavior\=compatibility</code>\, otherwise simply remove it \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.
* redhat\_subscriptions \- removed the <code>pool</code> option\. Use <code>pool\_ids</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/8918](https\://github\.com/ansible\-collections/community\.general/pull/8918)\)\.

<a id="bugfixes-12"></a>
### Bugfixes

* bitwarden lookup plugin \- fix <code>KeyError</code> in <code>search\_field</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8549](https\://github\.com/ansible\-collections/community\.general/issues/8549)\, [https\://github\.com/ansible\-collections/community\.general/pull/8557](https\://github\.com/ansible\-collections/community\.general/pull/8557)\)\.
* bitwarden lookup plugin \- support BWS v0\.3\.0 syntax breaking change \([https\://github\.com/ansible\-collections/community\.general/pull/9028](https\://github\.com/ansible\-collections/community\.general/pull/9028)\)\.
* cloudflare\_dns \- fix changing Cloudflare SRV records \([https\://github\.com/ansible\-collections/community\.general/issues/8679](https\://github\.com/ansible\-collections/community\.general/issues/8679)\, [https\://github\.com/ansible\-collections/community\.general/pull/8948](https\://github\.com/ansible\-collections/community\.general/pull/8948)\)\.
* cmd\_runner module utils \- call to <code>get\_best\_parsable\_locales\(\)</code> was missing parameter \([https\://github\.com/ansible\-collections/community\.general/pull/8929](https\://github\.com/ansible\-collections/community\.general/pull/8929)\)\.
* collection\_version lookup plugin \- use <code>importlib</code> directly instead of the deprecated and in ansible\-core 2\.19 removed <code>ansible\.module\_utils\.compat\.importlib</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9084](https\://github\.com/ansible\-collections/community\.general/pull/9084)\)\.
* cpanm \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* dig lookup plugin \- fix using only the last nameserver specified \([https\://github\.com/ansible\-collections/community\.general/pull/8970](https\://github\.com/ansible\-collections/community\.general/pull/8970)\)\.
* django module utils \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* django\_command \- option <code>command</code> is now split lexically before passed to underlying PythonRunner \([https\://github\.com/ansible\-collections/community\.general/pull/8944](https\://github\.com/ansible\-collections/community\.general/pull/8944)\)\.
* gconftool2\_info \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* git\_config \- fix behavior of <code>state\=absent</code> if <code>value</code> is present \([https\://github\.com/ansible\-collections/community\.general/issues/8436](https\://github\.com/ansible\-collections/community\.general/issues/8436)\, [https\://github\.com/ansible\-collections/community\.general/pull/8452](https\://github\.com/ansible\-collections/community\.general/pull/8452)\)\.
* gitlab\_group\_access\_token \- fix crash in check mode caused by attempted access to a newly created access token \([https\://github\.com/ansible\-collections/community\.general/pull/8796](https\://github\.com/ansible\-collections/community\.general/pull/8796)\)\.
* gitlab\_label \- update label\'s color \([https\://github\.com/ansible\-collections/community\.general/pull/9010](https\://github\.com/ansible\-collections/community\.general/pull/9010)\)\.
* gitlab\_project \- fix <code>container\_expiration\_policy</code> not being applied when creating a new project \([https\://github\.com/ansible\-collections/community\.general/pull/8790](https\://github\.com/ansible\-collections/community\.general/pull/8790)\)\.
* gitlab\_project \- fix crash caused by old Gitlab projects not having a <code>container\_expiration\_policy</code> attribute \([https\://github\.com/ansible\-collections/community\.general/pull/8790](https\://github\.com/ansible\-collections/community\.general/pull/8790)\)\.
* gitlab\_project\_access\_token \- fix crash in check mode caused by attempted access to a newly created access token \([https\://github\.com/ansible\-collections/community\.general/pull/8796](https\://github\.com/ansible\-collections/community\.general/pull/8796)\)\.
* gitlab\_runner \- fix <code>paused</code> parameter being ignored \([https\://github\.com/ansible\-collections/community\.general/pull/8648](https\://github\.com/ansible\-collections/community\.general/pull/8648)\)\.
* homebrew \- do not fail when brew prints warnings \([https\://github\.com/ansible\-collections/community\.general/pull/8406](https\://github\.com/ansible\-collections/community\.general/pull/8406)\, [https\://github\.com/ansible\-collections/community\.general/issues/7044](https\://github\.com/ansible\-collections/community\.general/issues/7044)\)\.
* homebrew\_cask \- fix <code>upgrade\_all</code> returns <code>changed</code> when nothing upgraded \([https\://github\.com/ansible\-collections/community\.general/issues/8707](https\://github\.com/ansible\-collections/community\.general/issues/8707)\, [https\://github\.com/ansible\-collections/community\.general/pull/8708](https\://github\.com/ansible\-collections/community\.general/pull/8708)\)\.
* homectl \- the module now tries to use <code>legacycrypt</code> on Python 3\.13\+ \([https\://github\.com/ansible\-collections/community\.general/issues/4691](https\://github\.com/ansible\-collections/community\.general/issues/4691)\, [https\://github\.com/ansible\-collections/community\.general/pull/8987](https\://github\.com/ansible\-collections/community\.general/pull/8987)\)\.
* hponcfg \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* ini\_file \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* ipa\_host \- add <code>force\_create</code>\, fix <code>enabled</code> and <code>disabled</code> states \([https\://github\.com/ansible\-collections/community\.general/issues/1094](https\://github\.com/ansible\-collections/community\.general/issues/1094)\, [https\://github\.com/ansible\-collections/community\.general/pull/8920](https\://github\.com/ansible\-collections/community\.general/pull/8920)\)\.
* ipa\_hostgroup \- fix <code>enabled \`\` and \`\`disabled</code> states \([https\://github\.com/ansible\-collections/community\.general/issues/8408](https\://github\.com/ansible\-collections/community\.general/issues/8408)\, [https\://github\.com/ansible\-collections/community\.general/pull/8900](https\://github\.com/ansible\-collections/community\.general/pull/8900)\)\.
* java\_keystore \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* jenkins\_node \- fixed <code>enabled</code>\, <code>disable</code> and <code>absent</code> node state redirect authorization issues\, same as was present for <code>present</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9084](https\://github\.com/ansible\-collections/community\.general/pull/9084)\)\.
* jenkins\_plugin \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* kdeconfig \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* kernel\_blacklist \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* keycloak\_client \- fix TypeError when sanitizing the <code>saml\.signing\.private\.key</code> attribute in the module\'s diff or state output\. The <code>sanitize\_cr</code> function expected a dict where in some cases a list might occur \([https\://github\.com/ansible\-collections/community\.general/pull/8403](https\://github\.com/ansible\-collections/community\.general/pull/8403)\)\.
* keycloak\_clientscope \- remove IDs from clientscope and its protocol mappers on comparison for changed check \([https\://github\.com/ansible\-collections/community\.general/pull/8545](https\://github\.com/ansible\-collections/community\.general/pull/8545)\)\.
* keycloak\_clientscope\_type \- fix detect changes in check mode \([https\://github\.com/ansible\-collections/community\.general/issues/9092](https\://github\.com/ansible\-collections/community\.general/issues/9092)\, [https\://github\.com/ansible\-collections/community\.general/pull/9093](https\://github\.com/ansible\-collections/community\.general/pull/9093)\)\.
* keycloak\_group \- fix crash caused in subgroup creation\. The crash was caused by a missing or empty <code>subGroups</code> property in Keycloak ≥23 \([https\://github\.com/ansible\-collections/community\.general/issues/8788](https\://github\.com/ansible\-collections/community\.general/issues/8788)\, [https\://github\.com/ansible\-collections/community\.general/pull/8979](https\://github\.com/ansible\-collections/community\.general/pull/8979)\)\.
* keycloak\_realm \- add normalizations for <code>attributes</code> and <code>protocol\_mappers</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8496](https\://github\.com/ansible\-collections/community\.general/pull/8496)\)\.
* keycloak\_realm \- fix change detection in check mode by sorting the lists in the realms beforehand \([https\://github\.com/ansible\-collections/community\.general/pull/8877](https\://github\.com/ansible\-collections/community\.general/pull/8877)\)\.
* keycloak\_realm\_key \- fix invalid usage of <code>parent\_id</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7850](https\://github\.com/ansible\-collections/community\.general/issues/7850)\, [https\://github\.com/ansible\-collections/community\.general/pull/8823](https\://github\.com/ansible\-collections/community\.general/pull/8823)\)\.
* keycloak\_user\_federation \- add module argument allowing users to configure the update mode for the parameter <code>bindCredential</code> \([https\://github\.com/ansible\-collections/community\.general/pull/8898](https\://github\.com/ansible\-collections/community\.general/pull/8898)\)\.
* keycloak\_user\_federation \- fix key error when removing mappers during an update and new mappers are specified in the module args \([https\://github\.com/ansible\-collections/community\.general/pull/8762](https\://github\.com/ansible\-collections/community\.general/pull/8762)\)\.
* keycloak\_user\_federation \- fix the <code>UnboundLocalError</code> that occurs when an ID is provided for a user federation mapper \([https\://github\.com/ansible\-collections/community\.general/pull/8831](https\://github\.com/ansible\-collections/community\.general/pull/8831)\)\.
* keycloak\_user\_federation \- get cleartext IDP <code>clientSecret</code> from full realm info to detect changes to it \([https\://github\.com/ansible\-collections/community\.general/issues/8294](https\://github\.com/ansible\-collections/community\.general/issues/8294)\, [https\://github\.com/ansible\-collections/community\.general/pull/8735](https\://github\.com/ansible\-collections/community\.general/pull/8735)\)\.
* keycloak\_user\_federation \- minimize change detection by setting <code>krbPrincipalAttribute</code> to <code>\'\'</code> in Keycloak responses if missing \([https\://github\.com/ansible\-collections/community\.general/pull/8785](https\://github\.com/ansible\-collections/community\.general/pull/8785)\)\.
* keycloak\_user\_federation \- remove <code>lastSync</code> parameter from Keycloak responses to minimize diff/changes \([https\://github\.com/ansible\-collections/community\.general/pull/8812](https\://github\.com/ansible\-collections/community\.general/pull/8812)\)\.
* keycloak\_user\_federation \- remove existing user federation mappers if they are not present in the federation configuration and will not be updated \([https\://github\.com/ansible\-collections/community\.general/issues/7169](https\://github\.com/ansible\-collections/community\.general/issues/7169)\, [https\://github\.com/ansible\-collections/community\.general/pull/8695](https\://github\.com/ansible\-collections/community\.general/pull/8695)\)\.
* keycloak\_user\_federation \- sort desired and after mapper list by name \(analog to before mapper list\) to minimize diff and make change detection more accurate \([https\://github\.com/ansible\-collections/community\.general/pull/8761](https\://github\.com/ansible\-collections/community\.general/pull/8761)\)\.
* keycloak\_userprofile \- fix empty response when fetching userprofile component by removing <code>parent\=parent\_id</code> filter \([https\://github\.com/ansible\-collections/community\.general/pull/8923](https\://github\.com/ansible\-collections/community\.general/pull/8923)\)\.
* keycloak\_userprofile \- improve diff by deserializing the fetched <code>kc\.user\.profile\.config</code> and serialize it only when sending back \([https\://github\.com/ansible\-collections/community\.general/pull/8940](https\://github\.com/ansible\-collections/community\.general/pull/8940)\)\.
* launched \- correctly report changed status in check mode \([https\://github\.com/ansible\-collections/community\.general/pull/8406](https\://github\.com/ansible\-collections/community\.general/pull/8406)\)\.
* locale\_gen \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* lxd\_container \- fix bug introduced in previous commit \([https\://github\.com/ansible\-collections/community\.general/pull/8895](https\://github\.com/ansible\-collections/community\.general/pull/8895)\, [https\://github\.com/ansible\-collections/community\.general/issues/8888](https\://github\.com/ansible\-collections/community\.general/issues/8888)\)\.
* mksysb \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* modprobe \- fix check mode not being honored for <code>persistent</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/9051](https\://github\.com/ansible\-collections/community\.general/issues/9051)\, [https\://github\.com/ansible\-collections/community\.general/pull/9052](https\://github\.com/ansible\-collections/community\.general/pull/9052)\)\.
* nsupdate \- fix \'index out of range\' error when changing NS records by falling back to authority section of the response \([https\://github\.com/ansible\-collections/community\.general/issues/8612](https\://github\.com/ansible\-collections/community\.general/issues/8612)\, [https\://github\.com/ansible\-collections/community\.general/pull/8614](https\://github\.com/ansible\-collections/community\.general/pull/8614)\)\.
* one\_host \- fix if statements for cases when <code>ID\=0</code> \([https\://github\.com/ansible\-collections/community\.general/issues/1199](https\://github\.com/ansible\-collections/community\.general/issues/1199)\, [https\://github\.com/ansible\-collections/community\.general/pull/8907](https\://github\.com/ansible\-collections/community\.general/pull/8907)\)\.
* one\_image \- fix module failing due to a class method typo \([https\://github\.com/ansible\-collections/community\.general/pull/9056](https\://github\.com/ansible\-collections/community\.general/pull/9056)\)\.
* one\_image\_info \- fix module failing due to a class method typo \([https\://github\.com/ansible\-collections/community\.general/pull/9056](https\://github\.com/ansible\-collections/community\.general/pull/9056)\)\.
* one\_service \- fix service creation after it was deleted with <code>unique</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/3137](https\://github\.com/ansible\-collections/community\.general/issues/3137)\, [https\://github\.com/ansible\-collections/community\.general/pull/8887](https\://github\.com/ansible\-collections/community\.general/pull/8887)\)\.
* one\_vnet \- fix module failing due to a variable typo \([https\://github\.com/ansible\-collections/community\.general/pull/9019](https\://github\.com/ansible\-collections/community\.general/pull/9019)\)\.
* opennebula inventory plugin \- fix invalid reference to IP when inventory runs against NICs with no IPv4 address \([https\://github\.com/ansible\-collections/community\.general/pull/8489](https\://github\.com/ansible\-collections/community\.general/pull/8489)\)\.
* opentelemetry callback \- do not save the JSON response when using the <code>ansible\.builtin\.uri</code> module \([https\://github\.com/ansible\-collections/community\.general/pull/8430](https\://github\.com/ansible\-collections/community\.general/pull/8430)\)\.
* opentelemetry callback \- do not save the content response when using the <code>ansible\.builtin\.slurp</code> module \([https\://github\.com/ansible\-collections/community\.general/pull/8430](https\://github\.com/ansible\-collections/community\.general/pull/8430)\)\.
* pam\_limits \- pass absolute paths to <code>module\.atomic\_move\(\)</code> \([https\://github\.com/ansible/ansible/issues/83950](https\://github\.com/ansible/ansible/issues/83950)\, [https\://github\.com/ansible\-collections/community\.general/pull/8925](https\://github\.com/ansible\-collections/community\.general/pull/8925)\)\.
* paman \- do not fail if an empty list of packages has been provided and there is nothing to do \([https\://github\.com/ansible\-collections/community\.general/pull/8514](https\://github\.com/ansible\-collections/community\.general/pull/8514)\)\.
* pipx \- it was ignoring <code>global</code> when listing existing applications \([https\://github\.com/ansible\-collections/community\.general/pull/9044](https\://github\.com/ansible\-collections/community\.general/pull/9044)\)\.
* pipx module utils \- add missing command line formatter for argument <code>spec\_metadata</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9044](https\://github\.com/ansible\-collections/community\.general/pull/9044)\)\.
* pipx\_info \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* proxmox \- fix idempotency on creation of mount volumes using Proxmox\' special <code>\<storage\>\:\<size\></code> syntax \([https\://github\.com/ansible\-collections/community\.general/issues/8407](https\://github\.com/ansible\-collections/community\.general/issues/8407)\, [https\://github\.com/ansible\-collections/community\.general/pull/8542](https\://github\.com/ansible\-collections/community\.general/pull/8542)\)\.
* proxmox \- fixed an issue where the new volume handling incorrectly converted <code>null</code> values into <code>\"None\"</code> strings \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.
* proxmox \- fixed an issue where volume strings where overwritten instead of appended to in the new <code>build\_volume\(\)</code> method \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.
* proxmox \- removed the forced conversion of non\-string values to strings to be consistent with the module documentation \([https\://github\.com/ansible\-collections/community\.general/pull/8646](https\://github\.com/ansible\-collections/community\.general/pull/8646)\)\.
* proxmox inventory plugin \- fixed a possible error on concatenating responses from proxmox\. In case an API call unexpectedly returned an empty result\, the inventory failed with a fatal error\. Added check for empty response \([https\://github\.com/ansible\-collections/community\.general/issues/8798](https\://github\.com/ansible\-collections/community\.general/issues/8798)\, [https\://github\.com/ansible\-collections/community\.general/pull/8794](https\://github\.com/ansible\-collections/community\.general/pull/8794)\)\.
* python\_runner module utils \- parameter <code>path\_prefix</code> was being handled as string when it should be a list \([https\://github\.com/ansible\-collections/community\.general/pull/8944](https\://github\.com/ansible\-collections/community\.general/pull/8944)\)\.
* redfish\_utils module utils \- do not fail when language is not exactly \"en\" \([https\://github\.com/ansible\-collections/community\.general/pull/8613](https\://github\.com/ansible\-collections/community\.general/pull/8613)\)\.
* redfish\_utils module utils \- fix issue with URI parsing to gracefully handling trailing slashes when extracting member identifiers \([https\://github\.com/ansible\-collections/community\.general/issues/9047](https\://github\.com/ansible\-collections/community\.general/issues/9047)\, [https\://github\.com/ansible\-collections/community\.general/pull/9057](https\://github\.com/ansible\-collections/community\.general/pull/9057)\)\.
* snap \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* snap\_alias \- use new <code>VarDict</code> to prevent deprecation warning \([https\://github\.com/ansible\-collections/community\.general/issues/8410](https\://github\.com/ansible\-collections/community\.general/issues/8410)\, [https\://github\.com/ansible\-collections/community\.general/pull/8411](https\://github\.com/ansible\-collections/community\.general/pull/8411)\)\.
* udm\_user \- the module now tries to use <code>legacycrypt</code> on Python 3\.13\+ \([https\://github\.com/ansible\-collections/community\.general/issues/4690](https\://github\.com/ansible\-collections/community\.general/issues/4690)\, [https\://github\.com/ansible\-collections/community\.general/pull/8987](https\://github\.com/ansible\-collections/community\.general/pull/8987)\)\.

<a id="known-issues-1"></a>
### Known Issues

* jenkins\_node \- the module is not able to update offline message when node is already offline due to internally using toggleOffline API \([https\://github\.com/ansible\-collections/community\.general/pull/9084](https\://github\.com/ansible\-collections/community\.general/pull/9084)\)\.

<a id="new-plugins-5"></a>
### New Plugins

<a id="filter-3"></a>
#### Filter

* community\.general\.keep\_keys \- Keep specific keys from dictionaries in a list\.
* community\.general\.remove\_keys \- Remove specific keys from dictionaries in a list\.
* community\.general\.replace\_keys \- Replace specific keys in a list of dictionaries\.
* community\.general\.reveal\_ansible\_type \- Return input type\.

<a id="test"></a>
#### Test

* community\.general\.ansible\_type \- Validate input type\.

<a id="new-modules-6"></a>
### New Modules

* community\.general\.bootc\_manage \- Bootc Switch and Upgrade\.
* community\.general\.consul\_agent\_check \- Add\, modify\, and delete checks within a consul cluster\.
* community\.general\.consul\_agent\_service \- Add\, modify and delete services within a consul cluster\.
* community\.general\.django\_check \- Wrapper for C\(django\-admin check\)\.
* community\.general\.django\_createcachetable \- Wrapper for C\(django\-admin createcachetable\)\.
* community\.general\.homebrew\_services \- Services manager for Homebrew\.
* community\.general\.ipa\_getkeytab \- Manage keytab file in FreeIPA\.
* community\.general\.jenkins\_node \- Manage Jenkins nodes\.
* community\.general\.keycloak\_component \- Allows administration of Keycloak components via Keycloak API\.
* community\.general\.keycloak\_realm\_keys\_metadata\_info \- Allows obtaining Keycloak realm keys metadata via Keycloak API\.
* community\.general\.keycloak\_userprofile \- Allows managing Keycloak User Profiles\.
* community\.general\.krb\_ticket \- Kerberos utils for managing tickets\.
* community\.general\.one\_vnet \- Manages OpenNebula virtual networks\.
* community\.general\.zypper\_repository\_info \- List Zypper repositories\.
