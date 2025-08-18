# Community General Release Notes

**Topics**

- <a href="#v11-2-1">v11\.2\.1</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v11-2-0">v11\.2\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#deprecated-features">Deprecated Features</a>
    - <a href="#bugfixes-1">Bugfixes</a>
    - <a href="#new-plugins">New Plugins</a>
        - <a href="#lookup">Lookup</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v11-1-2">v11\.1\.2</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v11-1-1">v11\.1\.1</a>
    - <a href="#release-summary-3">Release Summary</a>
    - <a href="#minor-changes-2">Minor Changes</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v11-1-0">v11\.1\.0</a>
    - <a href="#release-summary-4">Release Summary</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#deprecated-features-1">Deprecated Features</a>
    - <a href="#bugfixes-4">Bugfixes</a>
    - <a href="#new-plugins-1">New Plugins</a>
        - <a href="#callback">Callback</a>
    - <a href="#new-modules-1">New Modules</a>
- <a href="#v11-0-0">v11\.0\.0</a>
    - <a href="#release-summary-5">Release Summary</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#deprecated-features-2">Deprecated Features</a>
    - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
    - <a href="#security-fixes">Security Fixes</a>
    - <a href="#bugfixes-5">Bugfixes</a>
    - <a href="#known-issues">Known Issues</a>
    - <a href="#new-plugins-2">New Plugins</a>
        - <a href="#callback-1">Callback</a>
        - <a href="#connection">Connection</a>
        - <a href="#filter">Filter</a>
        - <a href="#inventory">Inventory</a>
        - <a href="#lookup-1">Lookup</a>
    - <a href="#new-modules-2">New Modules</a>
This changelog describes changes after version 10\.0\.0\.

<a id="v11-2-1"></a>
## v11\.2\.1

<a id="release-summary"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes"></a>
### Bugfixes

* Avoid deprecated functionality in ansible\-core 2\.20 \([https\://github\.com/ansible\-collections/community\.general/pull/10687](https\://github\.com/ansible\-collections/community\.general/pull/10687)\)\.
* apache2\_module \- check the <code>cgi</code> module restrictions only during activation \([https\://github\.com/ansible\-collections/community\.general/pull/10423](https\://github\.com/ansible\-collections/community\.general/pull/10423)\)\.
* composer \- fix broken command lines \([https\://github\.com/ansible\-collections/community\.general/issues/10662](https\://github\.com/ansible\-collections/community\.general/issues/10662)\, [https\://github\.com/ansible\-collections/community\.general/pull/10669](https\://github\.com/ansible\-collections/community\.general/pull/10669)\)\.
* pacemaker\_resource \- fix <code>resource\_type</code> parameter formatting \([https\://github\.com/ansible\-collections/community\.general/issues/10426](https\://github\.com/ansible\-collections/community\.general/issues/10426)\, [https\://github\.com/ansible\-collections/community\.general/pull/10663](https\://github\.com/ansible\-collections/community\.general/pull/10663)\)\.
* pids \- prevent error when an empty string is provided for <code>name</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10672](https\://github\.com/ansible\-collections/community\.general/issues/10672)\, [https\://github\.com/ansible\-collections/community\.general/pull/10688](https\://github\.com/ansible\-collections/community\.general/pull/10688)\)\.

<a id="v11-2-0"></a>
## v11\.2\.0

<a id="release-summary-1"></a>
### Release Summary

Regular bugfix and features release\.

<a id="minor-changes"></a>
### Minor Changes

* apk \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/issues/10479](https\://github\.com/ansible\-collections/community\.general/issues/10479)\, [https\://github\.com/ansible\-collections/community\.general/pull/10520](https\://github\.com/ansible\-collections/community\.general/pull/10520)\)\.
* bzr \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10523](https\://github\.com/ansible\-collections/community\.general/pull/10523)\)\.
* capabilities \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10524](https\://github\.com/ansible\-collections/community\.general/pull/10524)\)\.
* composer \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10525](https\://github\.com/ansible\-collections/community\.general/pull/10525)\)\.
* django module utils \- remove deprecated parameter <code>\_DjangoRunner</code> call \([https\://github\.com/ansible\-collections/community\.general/pull/10574](https\://github\.com/ansible\-collections/community\.general/pull/10574)\)\.
* easy\_install \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10526](https\://github\.com/ansible\-collections/community\.general/pull/10526)\)\.
* imgadm \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10536](https\://github\.com/ansible\-collections/community\.general/pull/10536)\)\.
* jenkins\_plugin \- install dependencies for specific version \([https\://github\.com/ansible\-collections/community\.general/issue/4995](https\://github\.com/ansible\-collections/community\.general/issue/4995)\, [https\://github\.com/ansible\-collections/community\.general/pull/10346](https\://github\.com/ansible\-collections/community\.general/pull/10346)\)\.
* keycloak\_identity\_provider – add support for <code>fromUrl</code> to automatically fetch OIDC endpoints from the well\-known discovery URL\, simplifying identity provider configuration \([https\://github\.com/ansible\-collections/community\.general/pull/10527](https\://github\.com/ansible\-collections/community\.general/pull/10527)\)\.
* keycloak\_realm \- add support for <code>brute\_force\_strategy</code> and <code>max\_temporary\_lockouts</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10412](https\://github\.com/ansible\-collections/community\.general/issues/10412)\, [https\://github\.com/ansible\-collections/community\.general/pull/10415](https\://github\.com/ansible\-collections/community\.general/pull/10415)\)\.
* keycloak\_realm \- add support for client\-related options and Oauth2 device \([https\://github\.com/ansible\-collections/community\.general/pull/10538](https\://github\.com/ansible\-collections/community\.general/pull/10538)\)\.
* logstash\_plugin \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/issues/10479](https\://github\.com/ansible\-collections/community\.general/issues/10479)\, [https\://github\.com/ansible\-collections/community\.general/pull/10520](https\://github\.com/ansible\-collections/community\.general/pull/10520)\)\.
* nagios \- make parameter <code>services</code> a <code>list</code> instead of a <code>str</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10493](https\://github\.com/ansible\-collections/community\.general/pull/10493)\)\.
* open\_iscsi \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10599](https\://github\.com/ansible\-collections/community\.general/pull/10599)\)\.
* pear \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10601](https\://github\.com/ansible\-collections/community\.general/pull/10601)\)\.
* portage \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10602](https\://github\.com/ansible\-collections/community\.general/pull/10602)\)\.
* riak \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10603](https\://github\.com/ansible\-collections/community\.general/pull/10603)\)\.
* scaleway\_\* modules\, scaleway inventory plugin \- update available zones and API URLs \([https\://github\.com/ansible\-collections/community\.general/issues/10383](https\://github\.com/ansible\-collections/community\.general/issues/10383)\, [https\://github\.com/ansible\-collections/community\.general/pull/10424](https\://github\.com/ansible\-collections/community\.general/pull/10424)\)\.
* sensu\_subscription \- normalize quotes in the module output \([https\://github\.com/ansible\-collections/community\.general/pull/10483](https\://github\.com/ansible\-collections/community\.general/pull/10483)\)\.
* solaris\_zone \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10604](https\://github\.com/ansible\-collections/community\.general/pull/10604)\)\.
* swupd \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10605](https\://github\.com/ansible\-collections/community\.general/pull/10605)\)\.
* tasks\_only callback plugin \- add <code>result\_format</code> and <code>pretty\_results</code> options similarly to the default callback \([https\://github\.com/ansible\-collections/community\.general/pull/10422](https\://github\.com/ansible\-collections/community\.general/pull/10422)\)\.
* timezone \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10612](https\://github\.com/ansible\-collections/community\.general/pull/10612)\)\.
* urpmi \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10606](https\://github\.com/ansible\-collections/community\.general/pull/10606)\)\.
* xbps \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10608](https\://github\.com/ansible\-collections/community\.general/pull/10608)\)\.
* xfs\_quota \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/10609](https\://github\.com/ansible\-collections/community\.general/pull/10609)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* bearychat \- module is deprecated and will be removed in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/issues/10514](https\://github\.com/ansible\-collections/community\.general/issues/10514)\)\.
* cpanm \- deprecate <code>mode\=compatibility</code>\, <code>mode\=new</code> should be used instead \([https\://github\.com/ansible\-collections/community\.general/pull/10434](https\://github\.com/ansible\-collections/community\.general/pull/10434)\)\.
* github\_repo \- deprecate <code>force\_defaults\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10435](https\://github\.com/ansible\-collections/community\.general/pull/10435)\)\.
* rocketchat \- the default value for <code>is\_pre740</code>\, currently <code>true</code>\, is deprecated and will change to <code>false</code> in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10490](https\://github\.com/ansible\-collections/community\.general/pull/10490)\)\.

<a id="bugfixes-1"></a>
### Bugfixes

* jenkins\_plugin \- install latest compatible version instead of latest \([https\://github\.com/ansible\-collections/community\.general/issues/854](https\://github\.com/ansible\-collections/community\.general/issues/854)\, [https\://github\.com/ansible\-collections/community\.general/pull/10346](https\://github\.com/ansible\-collections/community\.general/pull/10346)\)\.
* jenkins\_plugin \- separate Jenkins and external URL credentials \([https\://github\.com/ansible\-collections/community\.general/issues/4419](https\://github\.com/ansible\-collections/community\.general/issues/4419)\, [https\://github\.com/ansible\-collections/community\.general/pull/10346](https\://github\.com/ansible\-collections/community\.general/pull/10346)\)\.
* lvm\_pv \- properly detect SCSI or NVMe devices to rescan \([https\://github\.com/ansible\-collections/community\.general/issues/10444](https\://github\.com/ansible\-collections/community\.general/issues/10444)\, [https\://github\.com/ansible\-collections/community\.general/pull/10596](https\://github\.com/ansible\-collections/community\.general/pull/10596)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="lookup"></a>
#### Lookup

* community\.general\.binary\_file \- Read binary file and return it Base64 encoded\.

<a id="new-modules"></a>
### New Modules

* community\.general\.lvm\_pv\_move\_data \- Move data between LVM Physical Volumes \(PVs\)\.
* community\.general\.pacemaker\_info \- Gather information about Pacemaker cluster\.

<a id="v11-1-2"></a>
## v11\.1\.2

<a id="release-summary-2"></a>
### Release Summary

Bugfix release\.

<a id="minor-changes-1"></a>
### Minor Changes

* gem \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* git\_config\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* github\_deploy\_key \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* github\_repo \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* github\_webhook \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* github\_webhook\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_branch \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_group\_access\_token \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_group\_variable \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_hook \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_instance\_variable \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_issue \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_label \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_merge\_request \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_milestone \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_project \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_project\_access\_token \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* gitlab\_project\_variable \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* grove \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* hg \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* homebrew \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* homebrew\_cask \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* homebrew\_tap \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* honeybadger\_deployment \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* htpasswd \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* icinga2\_host \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* influxdb\_user \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ini\_file \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ipa\_dnsrecord \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ipa\_dnszone \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ipa\_service \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ipbase\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* ipwcli\_dns \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* irc \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* jabber \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* jenkins\_credential \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* jenkins\_job \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* jenkins\_script \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10505](https\://github\.com/ansible\-collections/community\.general/pull/10505)\)\.
* keycloak\_authz\_authorization\_scope \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* keycloak\_authz\_permission \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* keycloak\_role \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* keycloak\_userprofile \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* keyring \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* kibana\_plugin \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* layman \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* ldap\_attrs \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* ldap\_inc \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* librato\_annotation \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* lldp \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* logentries \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* lxca\_cmms \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* lxca\_nodes \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* macports \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* mail \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_alerts \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_group \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_policies \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_policies\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_tags \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* manageiq\_tenant \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* matrix \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* mattermost \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* maven\_artifact \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* memset\_dns\_reload \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* memset\_zone \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* memset\_zone\_record \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* mqtt \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* mssql\_db \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* mssql\_script \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* netcup\_dns \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* newrelic\_deployment \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* nsupdate \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10507](https\://github\.com/ansible\-collections/community\.general/pull/10507)\)\.
* oci\_vcn \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* one\_image\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* one\_template \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* one\_vnet \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* onepassword\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* oneview\_fc\_network\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* opendj\_backendprop \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* ovh\_monthly\_billing \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pagerduty \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pagerduty\_change \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pagerduty\_user \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pam\_limits \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pear \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pkgng \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pnpm \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* portage \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pritunl\_org \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pritunl\_org\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pritunl\_user \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pritunl\_user\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pubnub\_blocks \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pushbullet \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* pushover \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* redis\_data \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* redis\_data\_incr \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* riak \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* rocketchat \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* rollbar\_deployment \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* say \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* scaleway\_database\_backup \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* sendgrid \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* sensu\_silence \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* sorcery \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* ssh\_config \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* statusio\_maintenance \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* svr4pkg \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* swdepot \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* syslogger \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* sysrc \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* systemd\_creds\_decrypt \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* systemd\_creds\_encrypt \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10512](https\://github\.com/ansible\-collections/community\.general/pull/10512)\)\.
* taiga\_issue \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* twilio \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_aaa\_group \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_ca\_host\_key\_cert \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_dns\_host \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_network\_interface\_address \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_proxy\_auth\_profile \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_proxy\_exception \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_proxy\_frontend \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* utm\_proxy\_location \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* vertica\_configuration \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* vertica\_info \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* vertica\_role \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* xbps \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* yarn \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* zypper \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.
* zypper\_repository \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10513](https\://github\.com/ansible\-collections/community\.general/pull/10513)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* apk \- fix check for empty/whitespace\-only package names \([https\://github\.com/ansible\-collections/community\.general/pull/10532](https\://github\.com/ansible\-collections/community\.general/pull/10532)\)\.
* capabilities \- using invalid path \(symlink/directory/\.\.\.\) returned unrelated and incoherent error messages \([https\://github\.com/ansible\-collections/community\.general/issues/5649](https\://github\.com/ansible\-collections/community\.general/issues/5649)\, [https\://github\.com/ansible\-collections/community\.general/pull/10455](https\://github\.com/ansible\-collections/community\.general/pull/10455)\)\.
* doas become plugin \- disable pipelining on ansible\-core 2\.19\+\. The plugin does not work with pipelining\, and since ansible\-core 2\.19 become plugins can indicate that they do not work with pipelining \([https\://github\.com/ansible\-collections/community\.general/issues/9977](https\://github\.com/ansible\-collections/community\.general/issues/9977)\, [https\://github\.com/ansible\-collections/community\.general/pull/10537](https\://github\.com/ansible\-collections/community\.general/pull/10537)\)\.
* json\_query filter plugin \- make compatible with lazy evaluation list and dictionary types of ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10539](https\://github\.com/ansible\-collections/community\.general/pull/10539)\)\.
* machinectl become plugin \- disable pipelining on ansible\-core 2\.19\+\. The plugin does not work with pipelining\, and since ansible\-core 2\.19 become plugins can indicate that they do not work with pipelining \([https\://github\.com/ansible\-collections/community\.general/pull/10537](https\://github\.com/ansible\-collections/community\.general/pull/10537)\)\.
* merge\_variables lookup plugin \- avoid deprecated functionality from ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10566](https\://github\.com/ansible\-collections/community\.general/pull/10566)\)\.
* wsl connection plugin \- avoid deprecated ansible\-core paramiko import helper\, import paramiko directly instead \([https\://github\.com/ansible\-collections/community\.general/issues/10515](https\://github\.com/ansible\-collections/community\.general/issues/10515)\, [https\://github\.com/ansible\-collections/community\.general/pull/10531](https\://github\.com/ansible\-collections/community\.general/pull/10531)\)\.

<a id="v11-1-1"></a>
## v11\.1\.1

<a id="release-summary-3"></a>
### Release Summary

Bugfix release for the next Ansible 12 pre\-release\.

<a id="minor-changes-2"></a>
### Minor Changes

* aerospike\_migrations \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* airbrake\_deployment \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* bigpanda \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* bootc\_manage \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* bower \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* btrfs\_subvolume \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* bundler \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* campfire \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* cargo \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* catapult \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* cisco\_webex \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* consul\_kv \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* consul\_policy \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* copr \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* datadog\_downtime \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* datadog\_monitor \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dconf \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dimensiondata\_network \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dimensiondata\_vlan \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dnf\_config\_manager \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dnsmadeeasy \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* dpkg\_divert \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* easy\_install \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* elasticsearch\_plugin \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* facter \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* filesystem \- remove redundant constructs from argument specs \([https\://github\.com/ansible\-collections/community\.general/pull/10494](https\://github\.com/ansible\-collections/community\.general/pull/10494)\)\.
* sysrc \- adjustments to the code \([https\://github\.com/ansible\-collections/community\.general/pull/10417](https\://github\.com/ansible\-collections/community\.general/pull/10417)\)\.

<a id="bugfixes-3"></a>
### Bugfixes

* apache2\_module \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* apk \- handle empty name strings properly \([https\://github\.com/ansible\-collections/community\.general/issues/10441](https\://github\.com/ansible\-collections/community\.general/issues/10441)\, [https\://github\.com/ansible\-collections/community\.general/pull/10442](https\://github\.com/ansible\-collections/community\.general/pull/10442)\)\.
* cronvar \- fix crash on missing <code>cron\_file</code> parent directories \([https\://github\.com/ansible\-collections/community\.general/issues/10460](https\://github\.com/ansible\-collections/community\.general/issues/10460)\, [https\://github\.com/ansible\-collections/community\.general/pull/10461](https\://github\.com/ansible\-collections/community\.general/pull/10461)\)\.
* cronvar \- handle empty strings on <code>value</code> properly  \([https\://github\.com/ansible\-collections/community\.general/issues/10439](https\://github\.com/ansible\-collections/community\.general/issues/10439)\, [https\://github\.com/ansible\-collections/community\.general/pull/10445](https\://github\.com/ansible\-collections/community\.general/pull/10445)\)\.
* htpasswd \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* irc \- pass hostname to <code>wrap\_socket\(\)</code> if <code>use\_tls\=true</code> and <code>validate\_certs\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10472](https\://github\.com/ansible\-collections/community\.general/issues/10472)\, [https\://github\.com/ansible\-collections/community\.general/pull/10491](https\://github\.com/ansible\-collections/community\.general/pull/10491)\)\.
* listen\_port\_facts \- avoid crash when required commands are missing \([https\://github\.com/ansible\-collections/community\.general/issues/10457](https\://github\.com/ansible\-collections/community\.general/issues/10457)\, [https\://github\.com/ansible\-collections/community\.general/pull/10458](https\://github\.com/ansible\-collections/community\.general/pull/10458)\)\.
* syspatch \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* sysrc \- fixes parsing with multi\-line variables \([https\://github\.com/ansible\-collections/community\.general/issues/10394](https\://github\.com/ansible\-collections/community\.general/issues/10394)\, [https\://github\.com/ansible\-collections/community\.general/pull/10417](https\://github\.com/ansible\-collections/community\.general/pull/10417)\)\.
* sysupgrade \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.
* zypper\_repository \- avoid ansible\-core 2\.19 deprecation \([https\://github\.com/ansible\-collections/community\.general/pull/10459](https\://github\.com/ansible\-collections/community\.general/pull/10459)\)\.

<a id="v11-1-0"></a>
## v11\.1\.0

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-3"></a>
### Minor Changes

* cloudflare\_dns \- adds support for PTR records \([https\://github\.com/ansible\-collections/community\.general/pull/10267](https\://github\.com/ansible\-collections/community\.general/pull/10267)\)\.
* cloudflare\_dns \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* cloudflare\_dns \- simplify validations and refactor some code\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10269](https\://github\.com/ansible\-collections/community\.general/pull/10269)\)\.
* crypttab \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* datadog\_monitor \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* dense callback plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* gitlab\_deploy\_key \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* gitlab\_group\_access\_token \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* gitlab\_hook \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* gitlab\_project\_access\_token \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* gitlab\_runner \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* iocage inventory plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* ipa\_group \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* jc filter plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* jenkins\_build \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* jenkins\_build\_info \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* keycloak \- add support for <code>grant\_type\=client\_credentials</code> to all keycloak modules\, so that specifying <code>auth\_client\_id</code> and <code>auth\_client\_secret</code> is sufficient for authentication \([https\://github\.com/ansible\-collections/community\.general/pull/10231](https\://github\.com/ansible\-collections/community\.general/pull/10231)\)\.
* keycloak module utils \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* logstash callback plugin \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* mail callback plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* nmcli \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* nmcli \- simplify validations and refactor some code\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10323](https\://github\.com/ansible\-collections/community\.general/pull/10323)\)\.
* oneandone\_firewall\_policy \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* oneandone\_load\_balancer \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* oneandone\_monitoring\_policy \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* onepassword\_info \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* osx\_defaults \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* ovh\_ip\_loadbalancing\_backend \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* pacemaker\_cluster \- add <code>state\=maintenance</code> for managing pacemaker maintenance mode \([https\://github\.com/ansible\-collections/community\.general/issues/10200](https\://github\.com/ansible\-collections/community\.general/issues/10200)\, [https\://github\.com/ansible\-collections/community\.general/pull/10227](https\://github\.com/ansible\-collections/community\.general/pull/10227)\)\.
* pacemaker\_cluster \- rename <code>node</code> to <code>name</code> and add <code>node</code> alias \([https\://github\.com/ansible\-collections/community\.general/pull/10227](https\://github\.com/ansible\-collections/community\.general/pull/10227)\)\.
* pacemaker\_resource \- enhance module by removing duplicative code \([https\://github\.com/ansible\-collections/community\.general/pull/10227](https\://github\.com/ansible\-collections/community\.general/pull/10227)\)\.
* packet\_device \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* pagerduty \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* pingdom \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* python\_runner module utils \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* rhevm \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* rocketchat \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* sensu\_silence \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* sl\_vm \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* urpmi \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* wsl connection plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* xattr \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.
* xen\_orchestra inventory plugin \- use f\-strings instead of concatenation \([https\://github\.com/ansible\-collections/community\.general/pull/10285](https\://github\.com/ansible\-collections/community\.general/pull/10285)\)\.
* xfconf \- minor adjustments the the code \([https\://github\.com/ansible\-collections/community\.general/pull/10311](https\://github\.com/ansible\-collections/community\.general/pull/10311)\)\.
* xml \- remove redundant brackets in conditionals\, no functional changes \([https\://github\.com/ansible\-collections/community\.general/pull/10328](https\://github\.com/ansible\-collections/community\.general/pull/10328)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* catapult \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/issues/10318](https\://github\.com/ansible\-collections/community\.general/issues/10318)\, [https\://github\.com/ansible\-collections/community\.general/pull/10329](https\://github\.com/ansible\-collections/community\.general/pull/10329)\)\.
* pacemaker\_cluster \- the parameter <code>state</code> will become a required parameter in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10227](https\://github\.com/ansible\-collections/community\.general/pull/10227)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* dependent lookup plugin \- avoid deprecated ansible\-core 2\.19 functionality \([https\://github\.com/ansible\-collections/community\.general/pull/10359](https\://github\.com/ansible\-collections/community\.general/pull/10359)\)\.
* github\_release \- support multiple types of GitHub tokens\; no longer failing when <code>ghs\_</code> token type is provided \([https\://github\.com/ansible\-collections/community\.general/issues/10338](https\://github\.com/ansible\-collections/community\.general/issues/10338)\, [https\://github\.com/ansible\-collections/community\.general/pull/10339](https\://github\.com/ansible\-collections/community\.general/pull/10339)\)\.
* icinga2 inventory plugin \- avoid using deprecated option when templating options \([https\://github\.com/ansible\-collections/community\.general/pull/10271](https\://github\.com/ansible\-collections/community\.general/pull/10271)\)\.
* incus connection plugin \- fix error handling to return more useful Ansible errors to the user \([https\://github\.com/ansible\-collections/community\.general/issues/10344](https\://github\.com/ansible\-collections/community\.general/issues/10344)\, [https\://github\.com/ansible\-collections/community\.general/pull/10349](https\://github\.com/ansible\-collections/community\.general/pull/10349)\)\.
* linode inventory plugin \- avoid using deprecated option when templating options \([https\://github\.com/ansible\-collections/community\.general/pull/10271](https\://github\.com/ansible\-collections/community\.general/pull/10271)\)\.
* logstash callback plugin \- remove reference to Python 2 library \([https\://github\.com/ansible\-collections/community\.general/pull/10345](https\://github\.com/ansible\-collections/community\.general/pull/10345)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="callback"></a>
#### Callback

* community\.general\.tasks\_only \- Only show tasks\.

<a id="new-modules-1"></a>
### New Modules

* community\.general\.jenkins\_credential \- Manage Jenkins credentials and domains via API\.

<a id="v11-0-0"></a>
## v11\.0\.0

<a id="release-summary-5"></a>
### Release Summary

This is release 11\.0\.0 of <code>community\.general</code>\, released on 2025\-06\-16\.

<a id="minor-changes-4"></a>
### Minor Changes

* CmdRunner module utils \- the convenience method <code>cmd\_runner\_fmt\.as\_fixed\(\)</code> now accepts multiple arguments as a list \([https\://github\.com/ansible\-collections/community\.general/pull/9893](https\://github\.com/ansible\-collections/community\.general/pull/9893)\)\.
* MH module utils \- delegate <code>debug</code> to the underlying <code>AnsibleModule</code> instance or issues a warning if an attribute already exists with that name \([https\://github\.com/ansible\-collections/community\.general/pull/9577](https\://github\.com/ansible\-collections/community\.general/pull/9577)\)\.
* alternatives \- add <code>family</code> parameter that allows to utilize the <code>\-\-family</code> option available in RedHat version of update\-alternatives \([https\://github\.com/ansible\-collections/community\.general/issues/5060](https\://github\.com/ansible\-collections/community\.general/issues/5060)\, [https\://github\.com/ansible\-collections/community\.general/pull/9096](https\://github\.com/ansible\-collections/community\.general/pull/9096)\)\.
* apache2\_mod\_proxy \- better handling regexp extraction \([https\://github\.com/ansible\-collections/community\.general/pull/9609](https\://github\.com/ansible\-collections/community\.general/pull/9609)\)\.
* apache2\_mod\_proxy \- change type of <code>state</code> to a list of strings\. No change for the users \([https\://github\.com/ansible\-collections/community\.general/pull/9600](https\://github\.com/ansible\-collections/community\.general/pull/9600)\)\.
* apache2\_mod\_proxy \- code simplification\, no change in functionality \([https\://github\.com/ansible\-collections/community\.general/pull/9457](https\://github\.com/ansible\-collections/community\.general/pull/9457)\)\.
* apache2\_mod\_proxy \- improve readability when using results from <code>fecth\_url\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9608](https\://github\.com/ansible\-collections/community\.general/pull/9608)\)\.
* apache2\_mod\_proxy \- refactor repeated code into method \([https\://github\.com/ansible\-collections/community\.general/pull/9599](https\://github\.com/ansible\-collections/community\.general/pull/9599)\)\.
* apache2\_mod\_proxy \- remove unused parameter and code from <code>Balancer</code> constructor \([https\://github\.com/ansible\-collections/community\.general/pull/9614](https\://github\.com/ansible\-collections/community\.general/pull/9614)\)\.
* apache2\_mod\_proxy \- simplified and improved string manipulation \([https\://github\.com/ansible\-collections/community\.general/pull/9614](https\://github\.com/ansible\-collections/community\.general/pull/9614)\)\.
* apache2\_mod\_proxy \- use <code>deps</code> to handle dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/9612](https\://github\.com/ansible\-collections/community\.general/pull/9612)\)\.
* apache2\_module \- added workaround for new PHP module name\, from <code>php7\_module</code> to <code>php\_module</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9951](https\://github\.com/ansible\-collections/community\.general/pull/9951)\)\.
* bitwarden lookup plugin \- add new option <code>collection\_name</code> to filter results by collection name\, and new option <code>result\_count</code> to validate number of results \([https\://github\.com/ansible\-collections/community\.general/pull/9728](https\://github\.com/ansible\-collections/community\.general/pull/9728)\)\.
* bitwarden lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* cargo \- add <code>features</code> parameter to allow activating specific features when installing Rust packages \([https\://github\.com/ansible\-collections/community\.general/pull/10198](https\://github\.com/ansible\-collections/community\.general/pull/10198)\)\.
* cartesian lookup plugin \- removed compatibility code for ansible\-core \< 2\.14 \([https\://github\.com/ansible\-collections/community\.general/pull/10160](https\://github\.com/ansible\-collections/community\.general/pull/10160)\)\.
* cgroup\_memory\_recap callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* cgroup\_memory\_recap callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* chef\_databag lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* chroot connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* chroot connection plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* chroot connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* cloud\_init\_data\_facts \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* cloudflare\_dns \- add support for <code>comment</code> and <code>tags</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9132](https\://github\.com/ansible\-collections/community\.general/pull/9132)\)\.
* cobbler inventory plugin \- add <code>connection\_timeout</code> option to specify the connection timeout to the cobbler server \([https\://github\.com/ansible\-collections/community\.general/pull/11063](https\://github\.com/ansible\-collections/community\.general/pull/11063)\)\.
* cobbler inventory plugin \- add <code>facts\_level</code> option to allow requesting fully rendered variables for Cobbler systems \([https\://github\.com/ansible\-collections/community\.general/issues/9419](https\://github\.com/ansible\-collections/community\.general/issues/9419)\, [https\://github\.com/ansible\-collections/community\.general/pull/9975](https\://github\.com/ansible\-collections/community\.general/pull/9975)\)\.
* cobbler inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* cobbler inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* cobbler inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* collection\_version lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* consul\_kv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* consul\_token \- fix idempotency when <code>policies</code> or <code>roles</code> are supplied by name \([https\://github\.com/ansible\-collections/community\.general/issues/9841](https\://github\.com/ansible\-collections/community\.general/issues/9841)\, [https\://github\.com/ansible\-collections/community\.general/pull/9845](https\://github\.com/ansible\-collections/community\.general/pull/9845)\)\.
* context\_demo callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* context\_demo callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* counter filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* counter\_enabled callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* counter\_enabled callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* cpanm \- enable usage of option <code>\-\-with\-recommends</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9554](https\://github\.com/ansible\-collections/community\.general/issues/9554)\, [https\://github\.com/ansible\-collections/community\.general/pull/9555](https\://github\.com/ansible\-collections/community\.general/pull/9555)\)\.
* cpanm \- enable usage of option <code>\-\-with\-suggests</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9555](https\://github\.com/ansible\-collections/community\.general/pull/9555)\)\.
* crc32 filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* credstash lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* cronvar \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* crypttab \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* cyberarkpassword lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* cyberarkpassword lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* default\_without\_diff callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dense callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dense callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* dependent lookup plugin \- removed compatibility code for ansible\-core \< 2\.14 \([https\://github\.com/ansible\-collections/community\.general/pull/10160](https\://github\.com/ansible\-collections/community\.general/pull/10160)\)\.
* dependent lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* deps module utils \- add <code>deps\.clear\(\)</code> to clear out previously declared dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/9179](https\://github\.com/ansible\-collections/community\.general/pull/9179)\)\.
* dict filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* dict\_kv filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* dig lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* dig lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* diy callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* diy callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* dnstxt lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* dnstxt lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* doas become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* doas become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* dsv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* dzdo become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* dzdo become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* elastic callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* elastic callback plugin \- instead of trying to extract the ansible\-core version from task data\, use ansible\-core\'s actual version \([https\://github\.com/ansible\-collections/community\.general/pull/10193](https\://github\.com/ansible\-collections/community\.general/pull/10193)\)\.
* elastic callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* etcd lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* etcd3 lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* etcd3 lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* filetree lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* flattened lookup plugin \- removed compatibility code for ansible\-core \< 2\.14 \([https\://github\.com/ansible\-collections/community\.general/pull/10160](https\://github\.com/ansible\-collections/community\.general/pull/10160)\)\.
* from\_csv filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* from\_csv filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* from\_ini filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* from\_ini filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* funcd connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* funcd connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* git\_config \- remove redundant <code>required\=False</code> from <code>argument\_spec</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10177](https\://github\.com/ansible\-collections/community\.general/pull/10177)\)\.
* github\_app\_access\_token lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* github\_key \- add <code>api\_url</code> parameter to support GitHub Enterprise Server installations \([https\://github\.com/ansible\-collections/community\.general/pull/10191](https\://github\.com/ansible\-collections/community\.general/pull/10191)\)\.
* gitlab\_instance\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/9425](https\://github\.com/ansible\-collections/community\.general/pull/9425)\)\.
* gitlab\_project \- add option <code>build\_timeout</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9960](https\://github\.com/ansible\-collections/community\.general/pull/9960)\)\.
* gitlab\_project\_members \- extend choices parameter <code>access\_level</code> by missing upstream valid value <code>owner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9953](https\://github\.com/ansible\-collections/community\.general/pull/9953)\)\.
* gitlab\_runners inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* gitlab\_runners inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* gitlab\_runners inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* groupby\_as\_dict filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* hashids filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* hiera lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* homebrew \- greatly speed up module when multiple packages are passed in the <code>name</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9181](https\://github\.com/ansible\-collections/community\.general/pull/9181)\)\.
* homebrew \- remove duplicated package name validation \([https\://github\.com/ansible\-collections/community\.general/pull/9076](https\://github\.com/ansible\-collections/community\.general/pull/9076)\)\.
* hpilo\_boot \- add option to get an idempotent behavior while powering on server\, resulting in success instead of failure when using <code>state\: boot\_once</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9646](https\://github\.com/ansible\-collections/community\.general/pull/9646)\)\.
* icinga2 inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* icinga2 inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* idrac\_redfish\_command\, idrac\_redfish\_config\, idrac\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* ilo\_redfish\_command\, ilo\_redfish\_config\, ilo\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* incus connection plugin \- adds <code>remote\_user</code> and <code>incus\_become\_method</code> parameters for allowing a non\-root user to connect to an Incus instance \([https\://github\.com/ansible\-collections/community\.general/pull/9743](https\://github\.com/ansible\-collections/community\.general/pull/9743)\)\.
* incus connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* incus connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* ini\_file \- modify an inactive option also when there are spaces in front of the comment symbol \([https\://github\.com/ansible\-collections/community\.general/pull/10102](https\://github\.com/ansible\-collections/community\.general/pull/10102)\, [https\://github\.com/ansible\-collections/community\.general/issues/8539](https\://github\.com/ansible\-collections/community\.general/issues/8539)\)\.
* iocage connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* iocage connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* iocage inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* iocage inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* iocage inventory plugin \- the new parameter <code>hooks\_results</code> of the plugin is a list of files inside a jail that provide configuration parameters for the inventory\. The inventory plugin reads the files from the jails and put the contents into the items of created variable <code>iocage\_hooks</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9650](https\://github\.com/ansible\-collections/community\.general/issues/9650)\, [https\://github\.com/ansible\-collections/community\.general/pull/9651](https\://github\.com/ansible\-collections/community\.general/pull/9651)\)\.
* iocage inventory plugin \- the new parameter <code>inventory\_hostname\_tag</code> of the plugin provides the name of the tag in the C\(iocage properties notes\) that contains the jails alias\. The new parameter <code>inventory\_hostname\_required</code>\, if enabled\, makes the tag mandatory \([https\://github\.com/ansible\-collections/community\.general/issues/10206](https\://github\.com/ansible\-collections/community\.general/issues/10206)\, [https\://github\.com/ansible\-collections/community\.general/pull/10207](https\://github\.com/ansible\-collections/community\.general/pull/10207)\)\.
* iocage inventory plugin \- the new parameter <code>sudo</code> of the plugin lets the command <code>iocage list \-l</code> to run as root on the iocage host\. This is needed to get the IPv4 of a running DHCP jail \([https\://github\.com/ansible\-collections/community\.general/issues/9572](https\://github\.com/ansible\-collections/community\.general/issues/9572)\, [https\://github\.com/ansible\-collections/community\.general/pull/9573](https\://github\.com/ansible\-collections/community\.general/pull/9573)\)\.
* iptables\_state action plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* iptables\_state action plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9318](https\://github\.com/ansible\-collections/community\.general/pull/9318)\)\.
* iso\_extract \- adds <code>password</code> parameter that is passed to 7z \([https\://github\.com/ansible\-collections/community\.general/pull/9159](https\://github\.com/ansible\-collections/community\.general/pull/9159)\)\.
* jabber callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* jabber callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* jail connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* jail connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* jc filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* jira \- adds <code>client\_cert</code> and <code>client\_key</code> parameters for supporting client certificate authentification when connecting to Jira \([https\://github\.com/ansible\-collections/community\.general/pull/9753](https\://github\.com/ansible\-collections/community\.general/pull/9753)\)\.
* jira \- transition operation now has <code>status\_id</code> to directly reference wanted transition \([https\://github\.com/ansible\-collections/community\.general/pull/9602](https\://github\.com/ansible\-collections/community\.general/pull/9602)\)\.
* json\_query filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* keep\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* keycloak \- add an action group for Keycloak modules to allow <code>module\_defaults</code> to be set for Keycloak tasks \([https\://github\.com/ansible\-collections/community\.general/pull/9284](https\://github\.com/ansible\-collections/community\.general/pull/9284)\)\.
* keycloak module\_utils \- user groups can now be referenced by their name\, like <code>staff</code>\, or their path\, like <code>/staff/engineering</code>\. The path syntax allows users to reference subgroups\, which is not possible otherwise \([https\://github\.com/ansible\-collections/community\.general/pull/9898](https\://github\.com/ansible\-collections/community\.general/pull/9898)\)\.
* keycloak\_\* modules \- <code>refresh\_token</code> parameter added\. When multiple authentication parameters are provided \(<code>token</code>\, <code>refresh\_token</code>\, and <code>auth\_username</code>/<code>auth\_password</code>\)\, modules will now automatically retry requests upon authentication errors \(401\)\, using in order the token\, refresh token\, and username/password \([https\://github\.com/ansible\-collections/community\.general/pull/9494](https\://github\.com/ansible\-collections/community\.general/pull/9494)\)\.
* keycloak\_realm \- remove ID requirement when creating a realm to allow Keycloak generating its own realm ID \([https\://github\.com/ansible\-collections/community\.general/pull/9768](https\://github\.com/ansible\-collections/community\.general/pull/9768)\)\.
* keycloak\_user module \- user groups can now be referenced by their name\, like <code>staff</code>\, or their path\, like <code>/staff/engineering</code>\. The path syntax allows users to reference subgroups\, which is not possible otherwise \([https\://github\.com/ansible\-collections/community\.general/pull/9898](https\://github\.com/ansible\-collections/community\.general/pull/9898)\)\.
* keyring lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* known\_hosts \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* ksu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* ksu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* lastpass lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* launchd \- add <code>plist</code> option for services such as sshd\, where the plist filename doesn\'t match the service name \([https\://github\.com/ansible\-collections/community\.general/pull/9102](https\://github\.com/ansible\-collections/community\.general/pull/9102)\)\.
* linode inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* linode inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* lists filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* lists\_mergeby filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* lldp \- adds <code>multivalues</code> parameter to control behavior when lldpctl outputs an attribute multiple times \([https\://github\.com/ansible\-collections/community\.general/pull/9657](https\://github\.com/ansible\-collections/community\.general/pull/9657)\)\.
* lmdb\_kv lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* lmdb\_kv lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* locale\_gen \- invert the logic to determine <code>ubuntu\_mode</code>\, making it look first for <code>/etc/locale\.gen</code> \(set <code>ubuntu\_mode</code> to <code>False</code>\) and only then looking for <code>/var/lib/locales/supported\.d/</code> \(set <code>ubuntu\_mode</code> to <code>True</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\, [https\://github\.com/ansible\-collections/community\.general/issues/9131](https\://github\.com/ansible\-collections/community\.general/issues/9131)\, [https\://github\.com/ansible\-collections/community\.general/issues/8487](https\://github\.com/ansible\-collections/community\.general/issues/8487)\)\.
* locale\_gen \- new return value <code>mechanism</code> to better express the semantics of the <code>ubuntu\_mode</code>\, with the possible values being either <code>glibc</code> \(<code>ubuntu\_mode\=False</code>\) or <code>ubuntu\_legacy</code> \(<code>ubuntu\_mode\=True</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\)\.
* log\_plays callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* log\_plays callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* loganalytics callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* loganalytics callback plugin \- instead of trying to extract the ansible\-core version from task data\, use ansible\-core\'s actual version \([https\://github\.com/ansible\-collections/community\.general/pull/10193](https\://github\.com/ansible\-collections/community\.general/pull/10193)\)\.
* loganalytics callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* logdna callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* logdna callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* logentries callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* logentries callback plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* logentries callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* logstash callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* lvg \- add <code>remove\_extra\_pvs</code> parameter to control if ansible should remove physical volumes which are not in the <code>pvs</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/9698](https\://github\.com/ansible\-collections/community\.general/pull/9698)\)\.
* lxc connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lxc connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* lxd connection plugin \- adds <code>remote\_user</code> and <code>lxd\_become\_method</code> parameters for allowing a non\-root user to connect to an LXD instance \([https\://github\.com/ansible\-collections/community\.general/pull/9659](https\://github\.com/ansible\-collections/community\.general/pull/9659)\)\.
* lxd connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lxd connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* lxd inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* lxd inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* lxd inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* machinectl become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* machinectl become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* mail callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* mail callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* manageiq\_alert\_profiles \- improve handling of parameter requirements \([https\://github\.com/ansible\-collections/community\.general/pull/9449](https\://github\.com/ansible\-collections/community\.general/pull/9449)\)\.
* manifold lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* manifold lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* maven\_artifact \- removed compatibility code for ansible\-core \< 2\.12 \([https\://github\.com/ansible\-collections/community\.general/pull/10192](https\://github\.com/ansible\-collections/community\.general/pull/10192)\)\.
* memcached cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* memcached cache plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9320](https\://github\.com/ansible\-collections/community\.general/pull/9320)\)\.
* merge\_variables lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* nmap inventory plugin \- adds <code>dns\_servers</code> option for specifying DNS servers for name resolution\. Accepts hostnames or IP addresses in the same format as the <code>exclude</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9849](https\://github\.com/ansible\-collections/community\.general/pull/9849)\)\.
* nmap inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* nmap inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* nmap inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* nmcli \- add <code>sriov</code> parameter that enables support for SR\-IOV settings \([https\://github\.com/ansible\-collections/community\.general/pull/9168](https\://github\.com/ansible\-collections/community\.general/pull/9168)\)\.
* nmcli \- add a option <code>fail\_over\_mac</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9570](https\://github\.com/ansible\-collections/community\.general/issues/9570)\, [https\://github\.com/ansible\-collections/community\.general/pull/9571](https\://github\.com/ansible\-collections/community\.general/pull/9571)\)\.
* nmcli \- add support for Infiniband MAC setting when <code>type</code> is <code>infiniband</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9962](https\://github\.com/ansible\-collections/community\.general/pull/9962)\)\.
* nmcli \- adds VRF support with new <code>type</code> value <code>vrf</code> and new <code>slave\_type</code> value <code>vrf</code> as well as new <code>table</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/9658](https\://github\.com/ansible\-collections/community\.general/pull/9658)\, [https\://github\.com/ansible\-collections/community\.general/issues/8014](https\://github\.com/ansible\-collections/community\.general/issues/8014)\)\.
* nmcli \- adds <code>autoconnect\_priority</code> and <code>autoconnect\_retries</code> options to support autoconnect logic \([https\://github\.com/ansible\-collections/community\.general/pull/10134](https\://github\.com/ansible\-collections/community\.general/pull/10134)\)\.
* nrdp callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* nrdp callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* null callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* one\_template \- adds <code>filter</code> option for retrieving templates which are not owned by the user \([https\://github\.com/ansible\-collections/community\.general/pull/9547](https\://github\.com/ansible\-collections/community\.general/pull/9547)\, [https\://github\.com/ansible\-collections/community\.general/issues/9278](https\://github\.com/ansible\-collections/community\.general/issues/9278)\)\.
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
* onepassword lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* onepassword lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* onepassword\_doc lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* onepassword\_ssh\_key \- refactor to move code to lookup class \([https\://github\.com/ansible\-collections/community\.general/pull/9633](https\://github\.com/ansible\-collections/community\.general/pull/9633)\)\.
* online inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* online inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* opennebula inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* opennebula inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* opennebula inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* opentelemetry callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* opentelemetry callback plugin \- instead of trying to extract the ansible\-core version from task data\, use ansible\-core\'s actual version \([https\://github\.com/ansible\-collections/community\.general/pull/10193](https\://github\.com/ansible\-collections/community\.general/pull/10193)\)\.
* opentelemetry callback plugin \- remove code handling Python versions prior to 3\.7 \([https\://github\.com/ansible\-collections/community\.general/pull/9482](https\://github\.com/ansible\-collections/community\.general/pull/9482)\)\.
* opentelemetry callback plugin \- remove code handling Python versions prior to 3\.7 \([https\://github\.com/ansible\-collections/community\.general/pull/9503](https\://github\.com/ansible\-collections/community\.general/pull/9503)\)\.
* opentelemetry callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* pacemaker\_cluster \- remove unused code \([https\://github\.com/ansible\-collections/community\.general/pull/9471](https\://github\.com/ansible\-collections/community\.general/pull/9471)\)\.
* pacemaker\_cluster \- using safer mechanism to run external command \([https\://github\.com/ansible\-collections/community\.general/pull/9471](https\://github\.com/ansible\-collections/community\.general/pull/9471)\)\.
* pacemaker\_resource \- add maintenance mode support for handling resource creation and deletion \([https\://github\.com/ansible\-collections/community\.general/issues/10180](https\://github\.com/ansible\-collections/community\.general/issues/10180)\, [https\://github\.com/ansible\-collections/community\.general/pull/10194](https\://github\.com/ansible\-collections/community\.general/pull/10194)\)\.
* pacman\_key \- support verifying that keys are trusted and not expired \([https\://github\.com/ansible\-collections/community\.general/issues/9949](https\://github\.com/ansible\-collections/community\.general/issues/9949)\, [https\://github\.com/ansible\-collections/community\.general/pull/9950](https\://github\.com/ansible\-collections/community\.general/pull/9950)\)\.
* parted \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* passwordstore lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* pbrun become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pbrun become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* pfexec become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pfexec become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* pickle cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pipx \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9180](https\://github\.com/ansible\-collections/community\.general/pull/9180)\)\.
* pipx \- parameter <code>name</code> now accepts Python package specifiers \([https\://github\.com/ansible\-collections/community\.general/issues/7815](https\://github\.com/ansible\-collections/community\.general/issues/7815)\, [https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* pipx module\_utils \- filtering application list by name now happens in the modules \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* pipx\_info \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9180](https\://github\.com/ansible\-collections/community\.general/pull/9180)\)\.
* pipx\_info \- filtering application list by name now happens in the module  \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* pmrun become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* pmrun become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* pulp\_repo \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* puppet \- improve parameter formatting\, no impact to user \([https\://github\.com/ansible\-collections/community\.general/pull/10014](https\://github\.com/ansible\-collections/community\.general/pull/10014)\)\.
* qubes connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* qubes connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* random\_mac filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* random\_pet lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* redfish module utils \- add <code>REDFISH\_COMMON\_ARGUMENT\_SPEC</code>\, a corresponding <code>redfish</code> docs fragment\, and support for its <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* redfish module utils \- removed compatibility code for ansible\-core \< 2\.14 \([https\://github\.com/ansible\-collections/community\.general/pull/10160](https\://github\.com/ansible\-collections/community\.general/pull/10160)\)\.
* redfish\_command \- add <code>PowerFullPowerCycle</code> to power command options \([https\://github\.com/ansible\-collections/community\.general/pull/9729](https\://github\.com/ansible\-collections/community\.general/pull/9729)\)\.
* redfish\_command \- add <code>update\_custom\_oem\_header</code>\, <code>update\_custom\_oem\_params</code>\, and <code>update\_custom\_oem\_mime\_type</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/9123](https\://github\.com/ansible\-collections/community\.general/pull/9123)\)\.
* redfish\_command\, redfish\_config\, redfish\_info \- add <code>validate\_certs</code> and <code>ca\_path</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* redfish\_config \- add command <code>SetPowerRestorePolicy</code> to set the desired power state of the system when power is restored \([https\://github\.com/ansible\-collections/community\.general/pull/9837](https\://github\.com/ansible\-collections/community\.general/pull/9837)\)\.
* redfish\_info \- add command <code>GetAccountServiceConfig</code> to get full information about AccountService configuration \([https\://github\.com/ansible\-collections/community\.general/pull/9403](https\://github\.com/ansible\-collections/community\.general/pull/9403)\)\.
* redfish\_info \- add command <code>GetPowerRestorePolicy</code> to get the desired power state of the system when power is restored \([https\://github\.com/ansible\-collections/community\.general/pull/9824](https\://github\.com/ansible\-collections/community\.general/pull/9824)\)\.
* redfish\_utils module utils \- remove redundant code \([https\://github\.com/ansible\-collections/community\.general/pull/9190](https\://github\.com/ansible\-collections/community\.general/pull/9190)\)\.
* redhat\_subscription \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* redis cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* redis cache plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* redis cache plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9320](https\://github\.com/ansible\-collections/community\.general/pull/9320)\)\.
* redis lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* remove\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* replace\_keys filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* revbitspss lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* reveal\_ansible\_type filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* rocketchat \- fix duplicate JSON conversion for Rocket\.Chat \< 7\.4\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9965](https\://github\.com/ansible\-collections/community\.general/pull/9965)\)\.
* rocketchat \- option <code>is\_pre740</code> has been added to control the format of the payload\. For Rocket\.Chat 7\.4\.0 or newer\, it must be set to <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9882](https\://github\.com/ansible\-collections/community\.general/pull/9882)\)\.
* rpm\_ostree\_pkg \- added the options <code>apply\_live</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9167](https\://github\.com/ansible\-collections/community\.general/pull/9167)\)\.
* rpm\_ostree\_pkg \- added the return value <code>needs\_reboot</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9167](https\://github\.com/ansible\-collections/community\.general/pull/9167)\)\.
* run0 become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* saltstack connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* saltstack connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* say callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* say callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* scaleway inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* scaleway inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* scaleway inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* scaleway\_lb \- minor simplification in the code \([https\://github\.com/ansible\-collections/community\.general/pull/9189](https\://github\.com/ansible\-collections/community\.general/pull/9189)\)\.
* selective callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* selective callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* sesu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* sesu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* shelvefile lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* shutdown action plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* shutdown action plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* shutdown action plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9318](https\://github\.com/ansible\-collections/community\.general/pull/9318)\)\.
* slack callback plugin \- add <code>http\_agent</code> option to enable the user to set a custom user agent for slack callback plugin \([https\://github\.com/ansible\-collections/community\.general/issues/9813](https\://github\.com/ansible\-collections/community\.general/issues/9813)\, [https\://github\.com/ansible\-collections/community\.general/pull/9836](https\://github\.com/ansible\-collections/community\.general/pull/9836)\)\.
* slack callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* slack callback plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* slack callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* snap \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9598](https\://github\.com/ansible\-collections/community\.general/pull/9598)\)\.
* snap\_alias \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9598](https\://github\.com/ansible\-collections/community\.general/pull/9598)\)\.
* solaris\_zone \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* sorcery \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* splunk callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* splunk callback plugin \- instead of trying to extract the ansible\-core version from task data\, use ansible\-core\'s actual version \([https\://github\.com/ansible\-collections/community\.general/pull/10193](https\://github\.com/ansible\-collections/community\.general/pull/10193)\)\.
* splunk callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* ssh\_config \- add <code>dynamicforward</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9192](https\://github\.com/ansible\-collections/community\.general/pull/9192)\)\.
* ssh\_config \- add <code>other\_options</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/8053](https\://github\.com/ansible\-collections/community\.general/issues/8053)\, [https\://github\.com/ansible\-collections/community\.general/pull/9684](https\://github\.com/ansible\-collections/community\.general/pull/9684)\)\.
* stackpath\_compute inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* stackpath\_compute inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* sudosu become plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* sudosu become plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9319](https\://github\.com/ansible\-collections/community\.general/pull/9319)\)\.
* sumologic callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* sumologic callback plugin \- instead of trying to extract the ansible\-core version from task data\, use ansible\-core\'s actual version \([https\://github\.com/ansible\-collections/community\.general/pull/10193](https\://github\.com/ansible\-collections/community\.general/pull/10193)\)\.
* syslog\_json callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* systemd\_info \- add wildcard expression support in <code>unitname</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9821](https\://github\.com/ansible\-collections/community\.general/pull/9821)\)\.
* systemd\_info \- extend support to timer units \([https\://github\.com/ansible\-collections/community\.general/pull/9891](https\://github\.com/ansible\-collections/community\.general/pull/9891)\)\.
* terraform \- adds the <code>no\_color</code> parameter\, which suppresses or allows color codes in stdout from Terraform commands \([https\://github\.com/ansible\-collections/community\.general/pull/10154](https\://github\.com/ansible\-collections/community\.general/pull/10154)\)\.
* time filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* timestamp callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* timestamp callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* timezone \- open file using <code>open\(\)</code> as a context manager \([https\://github\.com/ansible\-collections/community\.general/pull/9579](https\://github\.com/ansible\-collections/community\.general/pull/9579)\)\.
* to\_ini filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* to\_ini filter plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* tss lookup plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* tss lookup plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9324](https\://github\.com/ansible\-collections/community\.general/pull/9324)\)\.
* ufw \- add support for <code>vrrp</code> protocol \([https\://github\.com/ansible\-collections/community\.general/issues/9562](https\://github\.com/ansible\-collections/community\.general/issues/9562)\, [https\://github\.com/ansible\-collections/community\.general/pull/9582](https\://github\.com/ansible\-collections/community\.general/pull/9582)\)\.
* unicode\_normalize filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* unixy callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* unixy callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* version\_sort filter plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9585](https\://github\.com/ansible\-collections/community\.general/pull/9585)\)\.
* virtualbox inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* virtualbox inventory plugin \- clean up string conversions \([https\://github\.com/ansible\-collections/community\.general/pull/9379](https\://github\.com/ansible\-collections/community\.general/pull/9379)\)\.
* virtualbox inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* vmadm \- add new options <code>flexible\_disk\_size</code> and <code>owner\_uuid</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9892](https\://github\.com/ansible\-collections/community\.general/pull/9892)\)\.
* wdc\_redfish\_command\, wdc\_redfish\_info \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* xbps \- add <code>root</code> and <code>repository</code> options to enable bootstrapping new void installations \([https\://github\.com/ansible\-collections/community\.general/pull/9174](https\://github\.com/ansible\-collections/community\.general/pull/9174)\)\.
* xcc\_redfish\_command \- add <code>validate\_certs</code>\, <code>ca\_path</code>\, and <code>ciphers</code> options to configure TLS/SSL \([https\://github\.com/ansible\-collections/community\.general/issues/3686](https\://github\.com/ansible\-collections/community\.general/issues/3686)\, [https\://github\.com/ansible\-collections/community\.general/pull/9964](https\://github\.com/ansible\-collections/community\.general/pull/9964)\)\.
* xen\_orchestra inventory plugin \- add <code>use\_vm\_uuid</code> and <code>use\_host\_uuid</code> boolean options to allow switching over to using VM/Xen name labels instead of UUIDs as item names \([https\://github\.com/ansible\-collections/community\.general/pull/9787](https\://github\.com/ansible\-collections/community\.general/pull/9787)\)\.
* xen\_orchestra inventory plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* xen\_orchestra inventory plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9323](https\://github\.com/ansible\-collections/community\.general/pull/9323)\)\.
* xfconf \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9226](https\://github\.com/ansible\-collections/community\.general/pull/9226)\)\.
* xfconf\_info \- add return value <code>version</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9226](https\://github\.com/ansible\-collections/community\.general/pull/9226)\)\.
* xml \- support adding value of children when creating with subnodes \([https\://github\.com/ansible\-collections/community\.general/pull/8437](https\://github\.com/ansible\-collections/community\.general/pull/8437)\)\.
* yaml cache plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* yaml callback plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9583](https\://github\.com/ansible\-collections/community\.general/pull/9583)\)\.
* yaml callback plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9321](https\://github\.com/ansible\-collections/community\.general/pull/9321)\)\.
* zone connection plugin \- adjust standard preamble for Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9584](https\://github\.com/ansible\-collections/community\.general/pull/9584)\)\.
* zone connection plugin \- use f\-strings instead of interpolations or <code>format</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9322](https\://github\.com/ansible\-collections/community\.general/pull/9322)\)\.
* zypper \- add <code>quiet</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9270](https\://github\.com/ansible\-collections/community\.general/pull/9270)\)\.
* zypper \- add <code>simple\_errors</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/9270](https\://github\.com/ansible\-collections/community\.general/pull/9270)\)\.
* zypper \- adds <code>skip\_post\_errors</code> that allows to skip RPM post\-install errors \(Zypper return code 107\) \([https\://github\.com/ansible\-collections/community\.general/issues/9972](https\://github\.com/ansible\-collections/community\.general/issues/9972)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* MH module utils \- attribute <code>debug</code> definition in subclasses of MH is now deprecated\, as that name will become a delegation to <code>AnsibleModule</code> in community\.general 12\.0\.0\, and any such attribute will be overridden by that delegation in that version \([https\://github\.com/ansible\-collections/community\.general/pull/9577](https\://github\.com/ansible\-collections/community\.general/pull/9577)\)\.
* atomic\_container \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* atomic\_host \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* atomic\_image \- module is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9487](https\://github\.com/ansible\-collections/community\.general/pull/9487)\)\.
* facter \- module is deprecated and will be removed in community\.general 12\.0\.0\, use <code>community\.general\.facter\_facts</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9451](https\://github\.com/ansible\-collections/community\.general/pull/9451)\)\.
* locale\_gen \- <code>ubuntu\_mode\=True</code>\, or <code>mechanism\=ubuntu\_legacy</code> is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9238](https\://github\.com/ansible\-collections/community\.general/pull/9238)\)\.
* manifold lookup plugin \- plugin is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10028](https\://github\.com/ansible\-collections/community\.general/pull/10028)\)\.
* opkg \- deprecate value <code>\"\"</code> for parameter <code>force</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9172](https\://github\.com/ansible\-collections/community\.general/pull/9172)\)\.
* pipx module\_utils \- function <code>make\_process\_list\(\)</code> is deprecated and will be removed in community\.general 13\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10031](https\://github\.com/ansible\-collections/community\.general/pull/10031)\)\.
* profitbricks \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_datacenter \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_nic \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_volume \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* profitbricks\_volume\_attachments \- module is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9733](https\://github\.com/ansible\-collections/community\.general/pull/9733)\)\.
* pure module utils \- the module utils is deprecated and will be removed from community\.general 12\.0\.0\. The modules using this were removed in community\.general 3\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9432](https\://github\.com/ansible\-collections/community\.general/pull/9432)\)\.
* purestorage doc fragments \- the doc fragment is deprecated and will be removed from community\.general 12\.0\.0\. The modules using this were removed in community\.general 3\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9432](https\://github\.com/ansible\-collections/community\.general/pull/9432)\)\.
* redfish\_utils module utils \- deprecate method <code>RedfishUtils\.\_init\_session\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9190](https\://github\.com/ansible\-collections/community\.general/pull/9190)\)\.
* sensu\_check \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_client \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_handler \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_silence \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* sensu\_subscription \- module is deprecated and will be removed in community\.general 13\.0\.0\, use collection <code>sensu\.sensu\_go</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/9483](https\://github\.com/ansible\-collections/community\.general/pull/9483)\)\.
* slack \- the default value <code>auto</code> of the <code>prepend\_hash</code> option is deprecated and will change to <code>never</code> in community\.general 12\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9443](https\://github\.com/ansible\-collections/community\.general/pull/9443)\)\.
* stackpath\_compute inventory plugin \- plugin is deprecated and will be removed in community\.general 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10026](https\://github\.com/ansible\-collections/community\.general/pull/10026)\)\.
* yaml callback plugin \- deprecate plugin in favor of <code>result\_format\=yaml</code> in plugin <code>ansible\.bulitin\.default</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9456](https\://github\.com/ansible\-collections/community\.general/pull/9456)\)\.
* yaml callback plugin \- the YAML callback plugin was deprecated for removal in community\.general 13\.0\.0\. Since it needs to use ansible\-core internals since ansible\-core 2\.19 that are changing a lot\, we will remove this plugin already from community\.general 12\.0\.0 to ease the maintenance burden \([https\://github\.com/ansible\-collections/community\.general/pull/10213](https\://github\.com/ansible\-collections/community\.general/pull/10213)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* Dropped support for ansible\-core 2\.15\. The collection now requires ansible\-core 2\.16 or newer\. This means that on the controller\, Python 3\.10\+ is required\. On the target side\, Python 2\.7 and Python 3\.6\+ are supported \([https\://github\.com/ansible\-collections/community\.general/pull/10160](https\://github\.com/ansible\-collections/community\.general/pull/10160)\, [https\://github\.com/ansible\-collections/community\.general/pull/10192](https\://github\.com/ansible\-collections/community\.general/pull/10192)\)\.
* The Proxmox content \(modules and plugins\) has been moved to the [new collection community\.proxmox](https\://github\.com/ansible\-collections/community\.proxmox)\. Since community\.general 11\.0\.0\, these modules and plugins have been replaced by deprecated redirections to community\.proxmox\. You need to explicitly install community\.proxmox\, for example with <code>ansible\-galaxy collection install community\.proxmox</code>\, or by installing a new enough version of the Ansible community package\. We suggest to update your roles and playbooks to use the new FQCNs as soon as possible to avoid getting deprecation messages \([https\://github\.com/ansible\-collections/community\.general/pull/10110](https\://github\.com/ansible\-collections/community\.general/pull/10110)\)\.
* apt\_rpm \- the <code>present</code> and <code>installed</code> states are no longer equivalent to <code>latest</code>\, but to <code>present\_not\_latest</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* clc\_\* modules and doc fragment \- the modules were removed since CenturyLink Cloud services went EOL in September 2023 \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* django\_manage \- the <code>ack\_venv\_creation\_deprecation</code> option has been removed\. It had no effect anymore anyway \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* git\_config \- it is no longer allowed to use <code>state\=present</code> with no value to read the config value\. Use the <code>community\.general\.git\_config\_info</code> module instead \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* git\_config \- the <code>list\_all</code> option has been removed\. Use the <code>community\.general\.git\_config\_info</code> module instead \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* hipchat \- the module was removed since the hipchat service has been discontinued and the self\-hosted variant has been End of Life since 2020 \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* manifold lookup plugin \- the plugin was removed since the company was acquired in 2021 and service was ceased afterwards \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* mh\.mixins\.deps module utils \- this module utils has been removed\. Use the <code>deps</code> module utils instead \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* mh\.mixins\.vars module utils \- this module utils has been removed\. Use <code>VarDict</code> from the <code>vardict</code> module utils instead \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* mh\.module\_helper module utils \- <code>AnsibleModule</code> and <code>VarsMixin</code> are no longer provided \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* mh\.module\_helper module utils \- <code>VarDict</code> is now imported from the <code>vardict</code> module utils and no longer from the removed <code>mh\.mixins\.vars</code> module utils \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* mh\.module\_helper module utils \- the attributes <code>use\_old\_vardict</code> and <code>mute\_vardict\_deprecation</code> from <code>ModuleHelper</code> have been removed\. We suggest to remove them from your modules if you no longer support community\.general \< 11\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* module\_helper module utils \- <code>StateMixin</code>\, <code>DependencyCtxMgr</code>\, <code>VarMeta</code>\, <code>VarDict</code>\, and <code>VarsMixin</code> are no longer provided \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* pipx \- module no longer supports <code>pipx</code> older than 1\.7\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10137](https\://github\.com/ansible\-collections/community\.general/pull/10137)\)\.
* pipx\_info \- module no longer supports <code>pipx</code> older than 1\.7\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/10137](https\://github\.com/ansible\-collections/community\.general/pull/10137)\)\.
* profitbrick\* modules \- the modules were removed since the supporting library is unsupported since 2021 \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* redfish\_utils module utils \- the <code>\_init\_session</code> method has been removed \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.
* stackpath\_compute inventory plugin \- the plugin was removed since the company and the service were sunset in June 2024 \([https\://github\.com/ansible\-collections/community\.general/pull/10126](https\://github\.com/ansible\-collections/community\.general/pull/10126)\)\.

<a id="security-fixes"></a>
### Security Fixes

* keycloak\_authentication \- API calls did not properly set the <code>priority</code> during update resulting in incorrectly sorted authentication flows\. This apparently only affects Keycloak 25 or newer \([https\://github\.com/ansible\-collections/community\.general/pull/9263](https\://github\.com/ansible\-collections/community\.general/pull/9263)\)\.
* keycloak\_client \- Sanitize <code>saml\.encryption\.private\.key</code> so it does not show in the logs \([https\://github\.com/ansible\-collections/community\.general/pull/9621](https\://github\.com/ansible\-collections/community\.general/pull/9621)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* apache2\_mod\_proxy \- make compatible with Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* apache2\_mod\_proxy \- passing the cluster\'s page as referer for the member\'s pages\. This makes the module actually work again for halfway modern Apache versions\. According to some comments founds on the net the referer was required since at least 2019 for some versions of Apache 2 \([https\://github\.com/ansible\-collections/community\.general/pull/9762](https\://github\.com/ansible\-collections/community\.general/pull/9762)\)\.
* cloudflare\_dns \- fix crash when deleting a DNS record or when updating a record with <code>solo\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9652](https\://github\.com/ansible\-collections/community\.general/issues/9652)\, [https\://github\.com/ansible\-collections/community\.general/pull/9649](https\://github\.com/ansible\-collections/community\.general/pull/9649)\)\.
* cloudlare\_dns \- handle exhausted response stream in case of HTTP errors to show nice error message to the user \([https\://github\.com/ansible\-collections/community\.general/issues/9782](https\://github\.com/ansible\-collections/community\.general/issues/9782)\, [https\://github\.com/ansible\-collections/community\.general/pull/9818](https\://github\.com/ansible\-collections/community\.general/pull/9818)\)\.
* cobbler\_system \- fix bug with Cobbler \>\= 3\.4\.0 caused by giving more than 2 positional arguments to <code>CobblerXMLRPCInterface\.get\_system\_handle\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/issues/8506](https\://github\.com/ansible\-collections/community\.general/issues/8506)\, [https\://github\.com/ansible\-collections/community\.general/pull/10145](https\://github\.com/ansible\-collections/community\.general/pull/10145)\)\.
* cobbler\_system \- update minimum version number to avoid wrong comparisons that happen in some cases using LooseVersion class which results in TypeError \([https\://github\.com/ansible\-collections/community\.general/issues/8506](https\://github\.com/ansible\-collections/community\.general/issues/8506)\, [https\://github\.com/ansible\-collections/community\.general/pull/10145](https\://github\.com/ansible\-collections/community\.general/pull/10145)\, [https\://github\.com/ansible\-collections/community\.general/pull/10178](https\://github\.com/ansible\-collections/community\.general/pull/10178)\)\.
* dependent look plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* dig lookup plugin \- correctly handle <code>NoNameserver</code> exception \([https\://github\.com/ansible\-collections/community\.general/pull/9363](https\://github\.com/ansible\-collections/community\.general/pull/9363)\, [https\://github\.com/ansible\-collections/community\.general/issues/9362](https\://github\.com/ansible\-collections/community\.general/issues/9362)\)\.
* diy callback plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* dnf\_config\_manager \- fix hanging when prompting to import GPG keys \([https\://github\.com/ansible\-collections/community\.general/pull/9124](https\://github\.com/ansible\-collections/community\.general/pull/9124)\, [https\://github\.com/ansible\-collections/community\.general/issues/8830](https\://github\.com/ansible\-collections/community\.general/issues/8830)\)\.
* dnf\_config\_manager \- forces locale to <code>C</code> before module starts\. If the locale was set to non\-English\, the output of the <code>dnf config\-manager</code> could not be parsed \([https\://github\.com/ansible\-collections/community\.general/pull/9157](https\://github\.com/ansible\-collections/community\.general/pull/9157)\, [https\://github\.com/ansible\-collections/community\.general/issues/9046](https\://github\.com/ansible\-collections/community\.general/issues/9046)\)\.
* dnf\_versionlock \- add support for dnf5 \([https\://github\.com/ansible\-collections/community\.general/issues/9556](https\://github\.com/ansible\-collections/community\.general/issues/9556)\)\.
* elasticsearch\_plugin \- fix <code>ERROR\: D is not a recognized option</code> issue when configuring proxy settings \([https\://github\.com/ansible\-collections/community\.general/pull/9774](https\://github\.com/ansible\-collections/community\.general/pull/9774)\, [https\://github\.com/ansible\-collections/community\.general/issues/9773](https\://github\.com/ansible\-collections/community\.general/issues/9773)\)\.
* flatpak \- force the locale language to <code>C</code> when running the flatpak command \([https\://github\.com/ansible\-collections/community\.general/pull/9187](https\://github\.com/ansible\-collections/community\.general/pull/9187)\, [https\://github\.com/ansible\-collections/community\.general/issues/8883](https\://github\.com/ansible\-collections/community\.general/issues/8883)\)\.
* gio\_mime \- fix command line when determining version of <code>gio</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9171](https\://github\.com/ansible\-collections/community\.general/pull/9171)\, [https\://github\.com/ansible\-collections/community\.general/issues/9158](https\://github\.com/ansible\-collections/community\.general/issues/9158)\)\.
* github\_deploy\_key \- check that key really exists on 422 to avoid masking other errors \([https\://github\.com/ansible\-collections/community\.general/issues/6718](https\://github\.com/ansible\-collections/community\.general/issues/6718)\, [https\://github\.com/ansible\-collections/community\.general/pull/10011](https\://github\.com/ansible\-collections/community\.general/pull/10011)\)\.
* github\_key \- in check mode\, a faulty call to <code>\`datetime\.strftime\(\.\.\.\)\`</code> was being made which generated an exception \([https\://github\.com/ansible\-collections/community\.general/issues/9185](https\://github\.com/ansible\-collections/community\.general/issues/9185)\)\.
* gitlab\_group\_access\_token\, gitlab\_project\_access\_token \- fix handling of group and project access tokens for changes in GitLab 17\.10 \([https\://github\.com/ansible\-collections/community\.general/pull/10196](https\://github\.com/ansible\-collections/community\.general/pull/10196)\)\.
* hashids and unicode\_normalize filter plugins \- avoid deprecated <code>AnsibleFilterTypeError</code> on ansible\-core 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/9992](https\://github\.com/ansible\-collections/community\.general/pull/9992)\)\.
* homebrew \- emit a useful error message if <code>brew info</code> reports a package tap is <code>null</code> \([https\://github\.com/ansible\-collections/community\.general/pull/10013](https\://github\.com/ansible\-collections/community\.general/pull/10013)\, [https\://github\.com/ansible\-collections/community\.general/issues/10012](https\://github\.com/ansible\-collections/community\.general/issues/10012)\)\.
* homebrew \- fix crash when package names include tap \([https\://github\.com/ansible\-collections/community\.general/issues/9777](https\://github\.com/ansible\-collections/community\.general/issues/9777)\, [https\://github\.com/ansible\-collections/community\.general/pull/9803](https\://github\.com/ansible\-collections/community\.general/pull/9803)\)\.
* homebrew \- fix incorrect handling of aliased homebrew modules when the alias is requested \([https\://github\.com/ansible\-collections/community\.general/pull/9255](https\://github\.com/ansible\-collections/community\.general/pull/9255)\, [https\://github\.com/ansible\-collections/community\.general/issues/9240](https\://github\.com/ansible\-collections/community\.general/issues/9240)\)\.
* homebrew \- fix incorrect handling of homebrew modules when a tap is requested \([https\://github\.com/ansible\-collections/community\.general/pull/9546](https\://github\.com/ansible\-collections/community\.general/pull/9546)\, [https\://github\.com/ansible\-collections/community\.general/issues/9533](https\://github\.com/ansible\-collections/community\.general/issues/9533)\)\.
* homebrew \- make package name parsing more resilient \([https\://github\.com/ansible\-collections/community\.general/pull/9665](https\://github\.com/ansible\-collections/community\.general/pull/9665)\, [https\://github\.com/ansible\-collections/community\.general/issues/9641](https\://github\.com/ansible\-collections/community\.general/issues/9641)\)\.
* homebrew\_cask \- allow <code>\+</code> symbol in Homebrew cask name validation regex \([https\://github\.com/ansible\-collections/community\.general/pull/9128](https\://github\.com/ansible\-collections/community\.general/pull/9128)\)\.
* homebrew\_cask \- handle unusual brew version strings \([https\://github\.com/ansible\-collections/community\.general/issues/8432](https\://github\.com/ansible\-collections/community\.general/issues/8432)\, [https\://github\.com/ansible\-collections/community\.general/pull/9881](https\://github\.com/ansible\-collections/community\.general/pull/9881)\)\.
* htpasswd \- report changes when file permissions are adjusted \([https\://github\.com/ansible\-collections/community\.general/issues/9485](https\://github\.com/ansible\-collections/community\.general/issues/9485)\, [https\://github\.com/ansible\-collections/community\.general/pull/9490](https\://github\.com/ansible\-collections/community\.general/pull/9490)\)\.
* iocage inventory plugin \- the plugin parses the IP4 tab of the jails list and put the elements into the new variable <code>iocage\_ip4\_dict</code>\. In multiple interface format the variable <code>iocage\_ip4</code> keeps the comma\-separated list of IP4 \([https\://github\.com/ansible\-collections/community\.general/issues/9538](https\://github\.com/ansible\-collections/community\.general/issues/9538)\)\.
* ipa\_host \- module revoked existing host certificates even if <code>user\_certificate</code> was not given \([https\://github\.com/ansible\-collections/community\.general/pull/9694](https\://github\.com/ansible\-collections/community\.general/pull/9694)\)\.
* java\_cert \- the module no longer fails if the optional parameters <code>pkcs12\_alias</code> and <code>cert\_alias</code> are not provided \([https\://github\.com/ansible\-collections/community\.general/pull/9970](https\://github\.com/ansible\-collections/community\.general/pull/9970)\)\.
* kdeconfig \- allow option values beginning with a dash \([https\://github\.com/ansible\-collections/community\.general/issues/10127](https\://github\.com/ansible\-collections/community\.general/issues/10127)\, [https\://github\.com/ansible\-collections/community\.general/pull/10128](https\://github\.com/ansible\-collections/community\.general/pull/10128)\)\.
* keycloak \- update more than 10 sub\-groups \([https\://github\.com/ansible\-collections/community\.general/issues/9690](https\://github\.com/ansible\-collections/community\.general/issues/9690)\, [https\://github\.com/ansible\-collections/community\.general/pull/9692](https\://github\.com/ansible\-collections/community\.general/pull/9692)\)\.
* keycloak module utils \- replaces missing return in get\_role\_composites method which caused it to return None instead of composite roles \([https\://github\.com/ansible\-collections/community\.general/issues/9678](https\://github\.com/ansible\-collections/community\.general/issues/9678)\, [https\://github\.com/ansible\-collections/community\.general/pull/9691](https\://github\.com/ansible\-collections/community\.general/pull/9691)\)\.
* keycloak\_authentication \- fix authentification config duplication for Keycloak \< 26\.2\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/9987](https\://github\.com/ansible\-collections/community\.general/pull/9987)\)\.
* keycloak\_client \- fix and improve existing tests\. The module showed a diff without actual changes\, solved by improving the <code>normalise\_cr\(\)</code> function \([https\://github\.com/ansible\-collections/community\.general/pull/9644](https\://github\.com/ansible\-collections/community\.general/pull/9644)\)\.
* keycloak\_client \- fix diff by removing code that turns the attributes dict which contains additional settings into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9077](https\://github\.com/ansible\-collections/community\.general/pull/9077)\)\.
* keycloak\_client \- fix the idempotency regression by normalizing the Keycloak response for <code>after\_client</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9905](https\://github\.com/ansible\-collections/community\.general/issues/9905)\, [https\://github\.com/ansible\-collections/community\.general/pull/9976](https\://github\.com/ansible\-collections/community\.general/pull/9976)\)\.
* keycloak\_client \- in check mode\, detect whether the lists in before client \(for example redirect URI list\) contain items that the lists in the desired client do not contain \([https\://github\.com/ansible\-collections/community\.general/pull/9739](https\://github\.com/ansible\-collections/community\.general/pull/9739)\)\.
* keycloak\_clientscope \- fix diff and <code>end\_state</code> by removing the code that turns the attributes dict\, which contains additional config items\, into a list \([https\://github\.com/ansible\-collections/community\.general/pull/9082](https\://github\.com/ansible\-collections/community\.general/pull/9082)\)\.
* keycloak\_clientscope\_type \- sort the default and optional clientscope lists to improve the diff \([https\://github\.com/ansible\-collections/community\.general/pull/9202](https\://github\.com/ansible\-collections/community\.general/pull/9202)\)\.
* keycloak\_user\_rolemapping \- fix <code>\-\-diff</code> mode \([https\://github\.com/ansible\-collections/community\.general/issues/10067](https\://github\.com/ansible\-collections/community\.general/issues/10067)\, [https\://github\.com/ansible\-collections/community\.general/pull/10075](https\://github\.com/ansible\-collections/community\.general/pull/10075)\)\.
* lldp \- fix crash caused by certain lldpctl output where an attribute is defined as branch and leaf \([https\://github\.com/ansible\-collections/community\.general/pull/9657](https\://github\.com/ansible\-collections/community\.general/pull/9657)\)\.
* nmcli \- enable changing only the order of DNS servers or search suffixes \([https\://github\.com/ansible\-collections/community\.general/issues/8724](https\://github\.com/ansible\-collections/community\.general/issues/8724)\, [https\://github\.com/ansible\-collections/community\.general/pull/9880](https\://github\.com/ansible\-collections/community\.general/pull/9880)\)\.
* onepassword\_doc lookup plugin \- ensure that 1Password Connect support also works for this plugin \([https\://github\.com/ansible\-collections/community\.general/pull/9625](https\://github\.com/ansible\-collections/community\.general/pull/9625)\)\.
* passwordstore lookup plugin \- fix subkey creation even when <code>create\=false</code> \([https\://github\.com/ansible\-collections/community\.general/issues/9105](https\://github\.com/ansible\-collections/community\.general/issues/9105)\, [https\://github\.com/ansible\-collections/community\.general/pull/9106](https\://github\.com/ansible\-collections/community\.general/pull/9106)\)\.
* pickle cache plugin \- avoid extra JSON serialization with ansible\-core \>\= 2\.19 \([https\://github\.com/ansible\-collections/community\.general/pull/10136](https\://github\.com/ansible\-collections/community\.general/pull/10136)\)\.
* pipx \- honor option <code>global</code> when <code>state\=latest</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9623](https\://github\.com/ansible\-collections/community\.general/pull/9623)\)\.
* qubes connection plugin \- fix the printing of debug information \([https\://github\.com/ansible\-collections/community\.general/pull/9334](https\://github\.com/ansible\-collections/community\.general/pull/9334)\)\.
* redfish\_utils module utils \- Fix <code>VerifyBiosAttributes</code> command on multi system resource nodes \([https\://github\.com/ansible\-collections/community\.general/pull/9234](https\://github\.com/ansible\-collections/community\.general/pull/9234)\)\.
* redfish\_utils module utils \- remove undocumented default applytime \([https\://github\.com/ansible\-collections/community\.general/pull/9114](https\://github\.com/ansible\-collections/community\.general/pull/9114)\)\.
* redhat\_subscription \- do not try to unsubscribe \(i\.e\. remove subscriptions\)
  when unregistering a system\: newer versions of subscription\-manager\, as
  available in EL 10 and Fedora 41\+\, do not support entitlements anymore\, and
  thus unsubscribing will fail
  \([https\://github\.com/ansible\-collections/community\.general/pull/9578](https\://github\.com/ansible\-collections/community\.general/pull/9578)\)\.
* redhat\_subscription \- use the \"enable\_content\" option \(when available\) when
  registering using D\-Bus\, to ensure that subscription\-manager enables the
  content on registration\; this is particular important on EL 10\+ and Fedora
  41\+
  \([https\://github\.com/ansible\-collections/community\.general/pull/9778](https\://github\.com/ansible\-collections/community\.general/pull/9778)\)\.
* reveal\_ansible\_type filter plugin and ansible\_type test plugin \- make compatible with ansible\-core\'s Data Tagging feature \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* rundeck\_acl\_policy \- ensure that project ACLs are sent to the correct endpoint \([https\://github\.com/ansible\-collections/community\.general/pull/10097](https\://github\.com/ansible\-collections/community\.general/pull/10097)\)\.
* slack \- fail if Slack API response is not OK with error message \([https\://github\.com/ansible\-collections/community\.general/pull/9198](https\://github\.com/ansible\-collections/community\.general/pull/9198)\)\.
* sudoers \- display stdout and stderr raised while failed validation \([https\://github\.com/ansible\-collections/community\.general/issues/9674](https\://github\.com/ansible\-collections/community\.general/issues/9674)\, [https\://github\.com/ansible\-collections/community\.general/pull/9871](https\://github\.com/ansible\-collections/community\.general/pull/9871)\)\.
* sysrc \- no longer always reporting <code>changed\=true</code> when <code>state\=absent</code>\. This fixes the method <code>exists\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/issues/10004](https\://github\.com/ansible\-collections/community\.general/issues/10004)\, [https\://github\.com/ansible\-collections/community\.general/pull/10005](https\://github\.com/ansible\-collections/community\.general/pull/10005)\)\.
* sysrc \- split the output of <code>sysrc \-e \-a</code> on the first <code>\=</code> only \([https\://github\.com/ansible\-collections/community\.general/issues/10120](https\://github\.com/ansible\-collections/community\.general/issues/10120)\, [https\://github\.com/ansible\-collections/community\.general/pull/10121](https\://github\.com/ansible\-collections/community\.general/pull/10121)\)\.
* xml \- ensure file descriptor is closed \([https\://github\.com/ansible\-collections/community\.general/pull/9695](https\://github\.com/ansible\-collections/community\.general/pull/9695)\)\.
* yaml callback plugin \- adjust to latest changes in ansible\-core devel \([https\://github\.com/ansible\-collections/community\.general/pull/10212](https\://github\.com/ansible\-collections/community\.general/pull/10212)\)\.
* yaml callback plugin \- use ansible\-core internals to avoid breakage with Data Tagging \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.
* yaml callback plugin \- when using ansible\-core 2\.19\.0b2 or newer\, uses a new utility provided by ansible\-core\. This allows us to remove all hacks and vendored code that was part of the plugin for ansible\-core versions with Data Tagging so far \([https\://github\.com/ansible\-collections/community\.general/pull/10242](https\://github\.com/ansible\-collections/community\.general/pull/10242)\)\.
* zfs \- fix handling of multi\-line values of user\-defined ZFS properties \([https\://github\.com/ansible\-collections/community\.general/pull/6264](https\://github\.com/ansible\-collections/community\.general/pull/6264)\)\.
* zfs\_facts \- parameter <code>type</code> now accepts multple values as documented \([https\://github\.com/ansible\-collections/community\.general/issues/5909](https\://github\.com/ansible\-collections/community\.general/issues/5909)\, [https\://github\.com/ansible\-collections/community\.general/pull/9697](https\://github\.com/ansible\-collections/community\.general/pull/9697)\)\.
* zypper\_repository \- make compatible with Python 3\.12\+ \([https\://github\.com/ansible\-collections/community\.general/issues/10222](https\://github\.com/ansible\-collections/community\.general/issues/10222)\, [https\://github\.com/ansible\-collections/community\.general/pull/10223](https\://github\.com/ansible\-collections/community\.general/pull/10223)\)\.
* zypper\_repository \- use <code>metalink</code> attribute to identify repositories without <code>\<url/\></code> element \([https\://github\.com/ansible\-collections/community\.general/issues/10224](https\://github\.com/ansible\-collections/community\.general/issues/10224)\, [https\://github\.com/ansible\-collections/community\.general/pull/10225](https\://github\.com/ansible\-collections/community\.general/pull/10225)\)\.

<a id="known-issues"></a>
### Known Issues

* reveal\_ansible\_type filter plugin and ansible\_type test plugin \- note that ansible\-core\'s Data Tagging feature implements new aliases\, such as <code>\_AnsibleTaggedStr</code> for <code>str</code>\, <code>\_AnsibleTaggedInt</code> for <code>int</code>\, and <code>\_AnsibleTaggedFloat</code> for <code>float</code> \([https\://github\.com/ansible\-collections/community\.general/pull/9833](https\://github\.com/ansible\-collections/community\.general/pull/9833)\)\.

<a id="new-plugins-2"></a>
### New Plugins

<a id="callback-1"></a>
#### Callback

* community\.general\.print\_task \- Prints playbook task snippet to job output\.

<a id="connection"></a>
#### Connection

* community\.general\.wsl \- Run tasks in WSL distribution using wsl\.exe CLI via SSH\.

<a id="filter"></a>
#### Filter

* community\.general\.accumulate \- Produce a list of accumulated sums of the input list contents\.
* community\.general\.json\_diff \- Create a JSON patch by comparing two JSON files\.
* community\.general\.json\_patch \- Apply a JSON\-Patch \(RFC 6902\) operation to an object\.
* community\.general\.json\_patch\_recipe \- Apply JSON\-Patch \(RFC 6902\) operations to an object\.
* community\.general\.to\_prettytable \- Format a list of dictionaries as an ASCII table\.

<a id="inventory"></a>
#### Inventory

* community\.general\.iocage \- iocage inventory source\.

<a id="lookup-1"></a>
#### Lookup

* community\.general\.onepassword\_ssh\_key \- Fetch SSH keys stored in 1Password\.

<a id="new-modules-2"></a>
### New Modules

* community\.general\.android\_sdk \- Manages Android SDK packages\.
* community\.general\.decompress \- Decompresses compressed files\.
* community\.general\.ldap\_inc \- Use the Modify\-Increment LDAP V3 feature to increment an attribute value\.
* community\.general\.lvm\_pv \- Manage LVM Physical Volumes\.
* community\.general\.pacemaker\_resource \- Manage pacemaker resources\.
* community\.general\.systemd\_creds\_decrypt \- C\(systemd\)\'s C\(systemd\-creds decrypt\) plugin\.
* community\.general\.systemd\_creds\_encrypt \- C\(systemd\)\'s C\(systemd\-creds encrypt\) plugin\.
* community\.general\.systemd\_info \- Gather C\(systemd\) unit info\.
* community\.general\.xdg\_mime \- Set default handler for MIME types\, for applications using XDG tools\.
* community\.general\.zpool \- Manage ZFS zpools\.
