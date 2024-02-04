# Community General Release Notes

**Topics**
- <a href="#v7-5-4">v7\.5\.4</a>
  - <a href="#release-summary">Release Summary</a>
  - <a href="#bugfixes">Bugfixes</a>
- <a href="#v7-5-3">v7\.5\.3</a>
  - <a href="#release-summary-1">Release Summary</a>
  - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v7-5-2">v7\.5\.2</a>
  - <a href="#release-summary-2">Release Summary</a>
  - <a href="#minor-changes">Minor Changes</a>
  - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v7-5-1">v7\.5\.1</a>
  - <a href="#release-summary-3">Release Summary</a>
  - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v7-5-0">v7\.5\.0</a>
  - <a href="#release-summary-4">Release Summary</a>
  - <a href="#minor-changes-1">Minor Changes</a>
  - <a href="#deprecated-features">Deprecated Features</a>
  - <a href="#bugfixes-4">Bugfixes</a>
  - <a href="#new-modules">New Modules</a>
- <a href="#v7-4-0">v7\.4\.0</a>
  - <a href="#release-summary-5">Release Summary</a>
  - <a href="#minor-changes-2">Minor Changes</a>
  - <a href="#bugfixes-5">Bugfixes</a>
  - <a href="#new-modules-1">New Modules</a>
- <a href="#v7-3-0">v7\.3\.0</a>
  - <a href="#release-summary-6">Release Summary</a>
  - <a href="#minor-changes-3">Minor Changes</a>
  - <a href="#deprecated-features-1">Deprecated Features</a>
  - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v7-2-1">v7\.2\.1</a>
  - <a href="#release-summary-7">Release Summary</a>
  - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v7-2-0">v7\.2\.0</a>
  - <a href="#release-summary-8">Release Summary</a>
  - <a href="#minor-changes-4">Minor Changes</a>
  - <a href="#deprecated-features-2">Deprecated Features</a>
  - <a href="#bugfixes-8">Bugfixes</a>
  - <a href="#new-plugins">New Plugins</a>
    - <a href="#lookup">Lookup</a>
  - <a href="#new-modules-2">New Modules</a>
- <a href="#v7-1-0">v7\.1\.0</a>
  - <a href="#release-summary-9">Release Summary</a>
  - <a href="#minor-changes-5">Minor Changes</a>
  - <a href="#deprecated-features-3">Deprecated Features</a>
  - <a href="#bugfixes-9">Bugfixes</a>
  - <a href="#known-issues">Known Issues</a>
  - <a href="#new-modules-3">New Modules</a>
- <a href="#v7-0-1">v7\.0\.1</a>
  - <a href="#release-summary-10">Release Summary</a>
  - <a href="#bugfixes-10">Bugfixes</a>
- <a href="#v7-0-0">v7\.0\.0</a>
  - <a href="#release-summary-11">Release Summary</a>
  - <a href="#minor-changes-6">Minor Changes</a>
  - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
  - <a href="#deprecated-features-4">Deprecated Features</a>
  - <a href="#removed-features-previously-deprecated">Removed Features \(previously deprecated\)</a>
  - <a href="#bugfixes-11">Bugfixes</a>
  - <a href="#new-plugins-1">New Plugins</a>
    - <a href="#lookup-1">Lookup</a>
  - <a href="#new-modules-4">New Modules</a>
This changelog describes changes after version 6\.0\.0\.

<a id="v7-5-4"></a>
## v7\.5\.4

<a id="release-summary"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes"></a>
### Bugfixes

* homebrew \- detect already installed formulae and casks using JSON output from <code>brew info</code> \([https\://github\.com/ansible\-collections/community\.general/issues/864](https\://github\.com/ansible\-collections/community\.general/issues/864)\)\.
* ipa\_otptoken \- the module expect <code>ipatokendisabled</code> as string but the <code>ipatokendisabled</code> value is returned as a boolean \([https\://github\.com/ansible\-collections/community\.general/pull/7795](https\://github\.com/ansible\-collections/community\.general/pull/7795)\)\.
* ldap \- previously the order number \(if present\) was expected to follow an equals sign in the DN\. This makes it so the order number string is identified correctly anywhere within the DN \([https\://github\.com/ansible\-collections/community\.general/issues/7646](https\://github\.com/ansible\-collections/community\.general/issues/7646)\)\.
* mssql\_script \- make the module work with Python 2 \([https\://github\.com/ansible\-collections/community\.general/issues/7818](https\://github\.com/ansible\-collections/community\.general/issues/7818)\, [https\://github\.com/ansible\-collections/community\.general/pull/7821](https\://github\.com/ansible\-collections/community\.general/pull/7821)\)\.
* nmcli \- fix <code>connection\.slave\-type</code> wired to <code>bond</code> and not with parameter <code>slave\_type</code> in case of connection type <code>wifi</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7389](https\://github\.com/ansible\-collections/community\.general/issues/7389)\)\.

<a id="v7-5-3"></a>
## v7\.5\.3

<a id="release-summary-1"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-1"></a>
### Bugfixes

* keycloak\_identity\_provider \- <code>mappers</code> processing was not idempotent if the mappers configuration list had not been sorted by name \(in ascending order\)\. Fix resolves the issue by sorting mappers in the desired state using the same key which is used for obtaining existing state \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_identity\_provider \- it was not possible to reconfigure \(add\, remove\) <code>mappers</code> once they were created initially\. Removal was ignored\, adding new ones resulted in dropping the pre\-existing unmodified mappers\. Fix resolves the issue by supplying correct input to the internal update call \([https\://github\.com/ansible\-collections/community\.general/pull/7418](https\://github\.com/ansible\-collections/community\.general/pull/7418)\)\.
* keycloak\_user \- when <code>force</code> is set\, but user does not exist\, do not try to delete it \([https\://github\.com/ansible\-collections/community\.general/pull/7696](https\://github\.com/ansible\-collections/community\.general/pull/7696)\)\.
* statusio\_maintenance \- fix error caused by incorrectly formed API data payload\. Was raising \"Failed to create maintenance HTTP Error 400 Bad Request\" caused by bad data type for date/time and deprecated dict keys \([https\://github\.com/ansible\-collections/community\.general/pull/7754](https\://github\.com/ansible\-collections/community\.general/pull/7754)\)\.

<a id="v7-5-2"></a>
## v7\.5\.2

<a id="release-summary-2"></a>
### Release Summary

Regular bugfix release\.

<a id="minor-changes"></a>
### Minor Changes

* elastic callback plugin \- close elastic client to not leak resources \([https\://github\.com/ansible\-collections/community\.general/pull/7517](https\://github\.com/ansible\-collections/community\.general/pull/7517)\)\.

<a id="bugfixes-2"></a>
### Bugfixes

* cloudflare\_dns \- fix Cloudflare lookup of SHFP records \([https\://github\.com/ansible\-collections/community\.general/issues/7652](https\://github\.com/ansible\-collections/community\.general/issues/7652)\)\.
* interface\_files \- also consider <code>address\_family</code> when changing <code>option\=method</code> \([https\://github\.com/ansible\-collections/community\.general/issues/7610](https\://github\.com/ansible\-collections/community\.general/issues/7610)\, [https\://github\.com/ansible\-collections/community\.general/pull/7612](https\://github\.com/ansible\-collections/community\.general/pull/7612)\)\.
* irc \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* keycloak\_\* \- fix Keycloak API client to quote <code>/</code> properly \([https\://github\.com/ansible\-collections/community\.general/pull/7641](https\://github\.com/ansible\-collections/community\.general/pull/7641)\)\.
* keycloak\_authz\_permission \- resource payload variable for scope\-based permission was constructed as a string\, when it needs to be a list\, even for a single item \([https\://github\.com/ansible\-collections/community\.general/issues/7151](https\://github\.com/ansible\-collections/community\.general/issues/7151)\)\.
* log\_entries callback plugin \- replace <code>ssl\.wrap\_socket</code> that was removed from Python 3\.12 with code for creating a proper SSL context \([https\://github\.com/ansible\-collections/community\.general/pull/7542](https\://github\.com/ansible\-collections/community\.general/pull/7542)\)\.
* lvol \- test for output messages in both <code>stdout</code> and <code>stderr</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7601](https\://github\.com/ansible\-collections/community\.general/pull/7601)\, [https\://github\.com/ansible\-collections/community\.general/issues/7182](https\://github\.com/ansible\-collections/community\.general/issues/7182)\)\.
* ocapi\_utils\, oci\_utils\, redfish\_utils module utils \- replace <code>type\(\)</code> calls with <code>isinstance\(\)</code> calls \([https\://github\.com/ansible\-collections/community\.general/pull/7501](https\://github\.com/ansible\-collections/community\.general/pull/7501)\)\.
* onepassword lookup plugin \- field and section titles are now case insensitive when using op CLI version two or later\. This matches the behavior of version one \([https\://github\.com/ansible\-collections/community\.general/pull/7564](https\://github\.com/ansible\-collections/community\.general/pull/7564)\)\.
* pipx module utils \- change the CLI argument formatter for the <code>pip\_args</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/7497](https\://github\.com/ansible\-collections/community\.general/issues/7497)\, [https\://github\.com/ansible\-collections/community\.general/pull/7506](https\://github\.com/ansible\-collections/community\.general/pull/7506)\)\.
* redhat\_subscription \- use the D\-Bus registration on RHEL 7 only on 7\.4 and
  greater\; older versions of RHEL 7 do not have it
  \([https\://github\.com/ansible\-collections/community\.general/issues/7622](https\://github\.com/ansible\-collections/community\.general/issues/7622)\,
  [https\://github\.com/ansible\-collections/community\.general/pull/7624](https\://github\.com/ansible\-collections/community\.general/pull/7624)\)\.
* terraform \- fix multiline string handling in complex variables \([https\://github\.com/ansible\-collections/community\.general/pull/7535](https\://github\.com/ansible\-collections/community\.general/pull/7535)\)\.

<a id="v7-5-1"></a>
## v7\.5\.1

<a id="release-summary-3"></a>
### Release Summary

Regular bugfix release\.

<a id="bugfixes-3"></a>
### Bugfixes

* composer \- fix impossible to run <code>working\_dir</code> dependent commands\. The module was throwing an error when trying to run a <code>working\_dir</code> dependent command\, because it tried to get the command help without passing the <code>working\_dir</code> \([https\://github\.com/ansible\-collections/community\.general/issues/3787](https\://github\.com/ansible\-collections/community\.general/issues/3787)\)\.
* github\_deploy\_key \- fix pagination behaviour causing a crash when only a single page of deploy keys exist \([https\://github\.com/ansible\-collections/community\.general/pull/7375](https\://github\.com/ansible\-collections/community\.general/pull/7375)\)\.
* gitlab\_group\_members \- fix gitlab constants call in <code>gitlab\_group\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_project\_members \- fix gitlab constants call in <code>gitlab\_project\_members</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_protected\_branches \- fix gitlab constants call in <code>gitlab\_protected\_branches</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* gitlab\_user \- fix gitlab constants call in <code>gitlab\_user</code> module \([https\://github\.com/ansible\-collections/community\.general/issues/7467](https\://github\.com/ansible\-collections/community\.general/issues/7467)\)\.
* kernel\_blacklist \- simplified the mechanism to update the file\, fixing the error \([https\://github\.com/ansible\-collections/community\.general/pull/7382](https\://github\.com/ansible\-collections/community\.general/pull/7382)\, [https\://github\.com/ansible\-collections/community\.general/issues/7362](https\://github\.com/ansible\-collections/community\.general/issues/7362)\)\.
* memset module utils \- make compatible with ansible\-core 2\.17 \([https\://github\.com/ansible\-collections/community\.general/pull/7379](https\://github\.com/ansible\-collections/community\.general/pull/7379)\)\.
* proxmox\_pool\_member \- absent state for type VM did not delete VMs from the pools \([https\://github\.com/ansible\-collections/community\.general/pull/7464](https\://github\.com/ansible\-collections/community\.general/pull/7464)\)\.
* redfish\_command \- fix usage of message parsing in <code>SimpleUpdate</code> and <code>MultipartHTTPPushUpdate</code> commands to treat the lack of a <code>MessageId</code> as no message \([https\://github\.com/ansible\-collections/community\.general/issues/7465](https\://github\.com/ansible\-collections/community\.general/issues/7465)\, [https\://github\.com/ansible\-collections/community\.general/pull/7471](https\://github\.com/ansible\-collections/community\.general/pull/7471)\)\.
* redhat\_subscription \- use the right D\-Bus options for the consumer type when
  registering a RHEL system older than 9 or a RHEL 9 system older than 9\.2
  and using <code>consumer\_type</code>
  \([https\://github\.com/ansible\-collections/community\.general/pull/7378](https\://github\.com/ansible\-collections/community\.general/pull/7378)\)\.
* selective callback plugin \- fix length of task name lines in output always being 3 characters longer than desired \([https\://github\.com/ansible\-collections/community\.general/pull/7374](https\://github\.com/ansible\-collections/community\.general/pull/7374)\)\.

<a id="v7-5-0"></a>
## v7\.5\.0

<a id="release-summary-4"></a>
### Release Summary

Regular bugfix and feature release\.

Please note that this is the last minor 7\.x\.0 release\. Further releases
with major version 7 will be bugfix releases 7\.5\.y\.

<a id="minor-changes-1"></a>
### Minor Changes

* cargo \- add option <code>executable</code>\, which allows user to specify path to the cargo binary \([https\://github\.com/ansible\-collections/community\.general/pull/7352](https\://github\.com/ansible\-collections/community\.general/pull/7352)\)\.
* cargo \- add option <code>locked</code> which allows user to specify install the locked version of dependency instead of latest compatible version \([https\://github\.com/ansible\-collections/community\.general/pull/6134](https\://github\.com/ansible\-collections/community\.general/pull/6134)\)\.
* dig lookup plugin \- add TCP option to enable the use of TCP connection during DNS lookup \([https\://github\.com/ansible\-collections/community\.general/pull/7343](https\://github\.com/ansible\-collections/community\.general/pull/7343)\)\.
* gitlab\_group \- add option <code>force\_delete</code> \(default\: false\) which allows delete group even if projects exists in it \([https\://github\.com/ansible\-collections/community\.general/pull/7364](https\://github\.com/ansible\-collections/community\.general/pull/7364)\)\.
* ini\_file \- add <code>ignore\_spaces</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7273](https\://github\.com/ansible\-collections/community\.general/pull/7273)\)\.
* newrelic\_deployment \- add option <code>app\_name\_exact\_match</code>\, which filters results for the exact app\_name provided \([https\://github\.com/ansible\-collections/community\.general/pull/7355](https\://github\.com/ansible\-collections/community\.general/pull/7355)\)\.
* onepassword lookup plugin \- introduce <code>account\_id</code> option which allows specifying which account to use \([https\://github\.com/ansible\-collections/community\.general/pull/7308](https\://github\.com/ansible\-collections/community\.general/pull/7308)\)\.
* onepassword\_raw lookup plugin \- introduce <code>account\_id</code> option which allows specifying which account to use \([https\://github\.com/ansible\-collections/community\.general/pull/7308](https\://github\.com/ansible\-collections/community\.general/pull/7308)\)\.
* parted \- on resize\, use <code>\-\-fix</code> option if available \([https\://github\.com/ansible\-collections/community\.general/pull/7304](https\://github\.com/ansible\-collections/community\.general/pull/7304)\)\.
* pnpm \- set correct version when state is latest or version is not mentioned\. Resolves previous idempotency problem \([https\://github\.com/ansible\-collections/community\.general/pull/7339](https\://github\.com/ansible\-collections/community\.general/pull/7339)\)\.
* proxmox \- add <code>vmid</code> \(and <code>taskid</code> when possible\) to return values \([https\://github\.com/ansible\-collections/community\.general/pull/7263](https\://github\.com/ansible\-collections/community\.general/pull/7263)\)\.
* random\_string \- added new <code>ignore\_similar\_chars</code> and <code>similar\_chars</code> option to ignore certain chars \([https\://github\.com/ansible\-collections/community\.general/pull/7242](https\://github\.com/ansible\-collections/community\.general/pull/7242)\)\.
* redfish\_command \- add new option <code>update\_oem\_params</code> for the <code>MultipartHTTPPushUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/7331](https\://github\.com/ansible\-collections/community\.general/issues/7331)\)\.
* redfish\_config \- add <code>CreateVolume</code> command to allow creation of volumes on servers \([https\://github\.com/ansible\-collections/community\.general/pull/6813](https\://github\.com/ansible\-collections/community\.general/pull/6813)\)\.
* redfish\_config \- adding <code>SetSecureBoot</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/7129](https\://github\.com/ansible\-collections/community\.general/pull/7129)\)\.
* redfish\_info \- add support for <code>GetBiosRegistries</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/7144](https\://github\.com/ansible\-collections/community\.general/pull/7144)\)\.
* redfish\_info \- adds <code>LinkStatus</code> to NIC inventory \([https\://github\.com/ansible\-collections/community\.general/pull/7318](https\://github\.com/ansible\-collections/community\.general/pull/7318)\)\.
* redis\_info \- refactor the redis\_info module to use the redis module\_utils enabling to pass TLS parameters to the Redis client \([https\://github\.com/ansible\-collections/community\.general/pull/7267](https\://github\.com/ansible\-collections/community\.general/pull/7267)\)\.
* supervisorctl \- allow to stop matching running processes before removing them with <code>stop\_before\_removing\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7284](https\://github\.com/ansible\-collections/community\.general/pull/7284)\)\.

<a id="deprecated-features"></a>
### Deprecated Features

* The next major release\, community\.general 8\.0\.0\, will drop support for ansible\-core 2\.11 and 2\.12\, which have been End of Life for some time now\. This means that this collection no longer supports Python 2\.6 on the target\. Individual content might still work with unsupported ansible\-core versions\, but that can change at any time\. Also please note that from now on\, for every new major community\.general release\, we will drop support for all ansible\-core versions that have been End of Life for more than a few weeks on the date of the major release \([https\://github\.com/ansible\-community/community\-topics/discussions/271](https\://github\.com/ansible\-community/community\-topics/discussions/271)\, [https\://github\.com/ansible\-collections/community\.general/pull/7259](https\://github\.com/ansible\-collections/community\.general/pull/7259)\)\.
* redfish\_info\, redfish\_config\, redfish\_command \- the default value <code>10</code> for the <code>timeout</code> option is deprecated and will change to <code>60</code> in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/7295](https\://github\.com/ansible\-collections/community\.general/pull/7295)\)\.

<a id="bugfixes-4"></a>
### Bugfixes

* gitlab\_group\_variable \- deleted all variables when used with <code>purge\=true</code> due to missing <code>raw</code> property in KNOWN attributes \([https\://github\.com/ansible\-collections/community\.general/issues/7250](https\://github\.com/ansible\-collections/community\.general/issues/7250)\)\.
* gitlab\_project\_variable \- deleted all variables when used with <code>purge\=true</code> due to missing <code>raw</code> property in KNOWN attributes \([https\://github\.com/ansible\-collections/community\.general/issues/7250](https\://github\.com/ansible\-collections/community\.general/issues/7250)\)\.
* ldap\_search \- fix string normalization and the <code>base64\_attributes</code> option on Python 3 \([https\://github\.com/ansible\-collections/community\.general/issues/5704](https\://github\.com/ansible\-collections/community\.general/issues/5704)\, [https\://github\.com/ansible\-collections/community\.general/pull/7264](https\://github\.com/ansible\-collections/community\.general/pull/7264)\)\.
* lxc connection plugin \- properly evaluate options \([https\://github\.com/ansible\-collections/community\.general/pull/7369](https\://github\.com/ansible\-collections/community\.general/pull/7369)\)\.
* mail \- skip headers containing equals characters due to missing <code>maxsplit</code> on header key/value parsing \([https\://github\.com/ansible\-collections/community\.general/pull/7303](https\://github\.com/ansible\-collections/community\.general/pull/7303)\)\.
* nmap inventory plugin \- fix <code>get\_option</code> calls \([https\://github\.com/ansible\-collections/community\.general/pull/7323](https\://github\.com/ansible\-collections/community\.general/pull/7323)\)\.
* onepassword \- fix KeyError exception when trying to access value of a field that is not filled out in OnePassword item \([https\://github\.com/ansible\-collections/community\.general/pull/7241](https\://github\.com/ansible\-collections/community\.general/pull/7241)\)\.
* snap \- change the change detection mechanism from \"parsing installation\" to \"comparing end state with initial state\" \([https\://github\.com/ansible\-collections/community\.general/pull/7340](https\://github\.com/ansible\-collections/community\.general/pull/7340)\, [https\://github\.com/ansible\-collections/community\.general/issues/7265](https\://github\.com/ansible\-collections/community\.general/issues/7265)\)\.
* terraform \- prevents <code>\-backend\-config</code> option double encapsulating with <code>shlex\_quote</code> function\. \([https\://github\.com/ansible\-collections/community\.general/pull/7301](https\://github\.com/ansible\-collections/community\.general/pull/7301)\)\.

<a id="new-modules"></a>
### New Modules

* consul\_role \- Manipulate Consul roles
* gio\_mime \- Set default handler for MIME type\, for applications using Gnome GIO
* keycloak\_authz\_custom\_policy \- Allows administration of Keycloak client custom Javascript policies via Keycloak API
* keycloak\_realm\_key \- Allows administration of Keycloak realm keys via Keycloak API
* simpleinit\_msb \- Manage services on Source Mage GNU/Linux

<a id="v7-4-0"></a>
## v7\.4\.0

<a id="release-summary-5"></a>
### Release Summary

Bugfix and feature release\.

<a id="minor-changes-2"></a>
### Minor Changes

* cobbler inventory plugin \- add <code>exclude\_mgmt\_classes</code> and <code>include\_mgmt\_classes</code> options to exclude or include hosts based on management classes \([https\://github\.com/ansible\-collections/community\.general/pull/7184](https\://github\.com/ansible\-collections/community\.general/pull/7184)\)\.
* cpanm \- minor refactor when creating the <code>CmdRunner</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/7231](https\://github\.com/ansible\-collections/community\.general/pull/7231)\)\.
* gitlab\_group\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/7132](https\://github\.com/ansible\-collections/community\.general/pull/7132)\)\.
* gitlab\_project\_variable \- add support for <code>raw</code> variables suboption \([https\://github\.com/ansible\-collections/community\.general/pull/7132](https\://github\.com/ansible\-collections/community\.general/pull/7132)\)\.
* jenkins\_build \- add new <code>detach</code> option\, which allows the module to exit successfully as long as the build is created \(default functionality is still waiting for the build to end before exiting\) \([https\://github\.com/ansible\-collections/community\.general/pull/7204](https\://github\.com/ansible\-collections/community\.general/pull/7204)\)\.
* jenkins\_build \- add new <code>time\_between\_checks</code> option\, which allows to configure the wait time between requests to the Jenkins server \([https\://github\.com/ansible\-collections/community\.general/pull/7204](https\://github\.com/ansible\-collections/community\.general/pull/7204)\)\.
* make \- allows <code>params</code> to be used without value \([https\://github\.com/ansible\-collections/community\.general/pull/7180](https\://github\.com/ansible\-collections/community\.general/pull/7180)\)\.
* nmap inventory plugin \- now has a <code>use\_arp\_ping</code> option to allow the user to disable the default ARP ping query for a more reliable form \([https\://github\.com/ansible\-collections/community\.general/pull/7119](https\://github\.com/ansible\-collections/community\.general/pull/7119)\)\.
* pagerduty \- adds in option to use v2 API for creating pagerduty incidents \([https\://github\.com/ansible\-collections/community\.general/issues/6151](https\://github\.com/ansible\-collections/community\.general/issues/6151)\)
* pritunl module utils \- ensure <code>validate\_certs</code> parameter is honoured in all methods \([https\://github\.com/ansible\-collections/community\.general/pull/7156](https\://github\.com/ansible\-collections/community\.general/pull/7156)\)\.
* redfish\_info \- report <code>Id</code> in the output of <code>GetManagerInventory</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7140](https\://github\.com/ansible\-collections/community\.general/pull/7140)\)\.
* redfish\_utils module utils \- support <code>Volumes</code> in response for <code>GetDiskInventory</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6819](https\://github\.com/ansible\-collections/community\.general/pull/6819)\)\.
* unixy callback plugin \- add support for <code>check\_mode\_markers</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7179](https\://github\.com/ansible\-collections/community\.general/pull/7179)\)\.

<a id="bugfixes-5"></a>
### Bugfixes

* CmdRunner module utils \- does not attempt to resolve path if executable is a relative or absolute path \([https\://github\.com/ansible\-collections/community\.general/pull/7200](https\://github\.com/ansible\-collections/community\.general/pull/7200)\)\.
* nmap inventory plugin \- now uses <code>get\_option</code> in all cases to get its configuration information \([https\://github\.com/ansible\-collections/community\.general/pull/7119](https\://github\.com/ansible\-collections/community\.general/pull/7119)\)\.
* nsupdate \- fix a possible <code>list index out of range</code> exception \([https\://github\.com/ansible\-collections/community\.general/issues/836](https\://github\.com/ansible\-collections/community\.general/issues/836)\)\.
* oci\_utils module util \- fix inappropriate logical comparison expressions and makes them simpler\. The previous checks had logical short circuits \([https\://github\.com/ansible\-collections/community\.general/pull/7125](https\://github\.com/ansible\-collections/community\.general/pull/7125)\)\.
* pritunl module utils \- fix incorrect URL parameter for orgnization add method \([https\://github\.com/ansible\-collections/community\.general/pull/7161](https\://github\.com/ansible\-collections/community\.general/pull/7161)\)\.
* snap \- an exception was being raised when snap list was empty \([https\://github\.com/ansible\-collections/community\.general/pull/7124](https\://github\.com/ansible\-collections/community\.general/pull/7124)\, [https\://github\.com/ansible\-collections/community\.general/issues/7120](https\://github\.com/ansible\-collections/community\.general/issues/7120)\)\.

<a id="new-modules-1"></a>
### New Modules

* jenkins\_build\_info \- Get information about Jenkins builds
* pnpm \- Manage node\.js packages with pnpm

<a id="v7-3-0"></a>
## v7\.3\.0

<a id="release-summary-6"></a>
### Release Summary

Feature and bugfix release\.

<a id="minor-changes-3"></a>
### Minor Changes

* chroot connection plugin \- add <code>disable\_root\_check</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/7099](https\://github\.com/ansible\-collections/community\.general/pull/7099)\)\.
* ejabberd\_user \- module now using <code>CmdRunner</code> to execute external command \([https\://github\.com/ansible\-collections/community\.general/pull/7075](https\://github\.com/ansible\-collections/community\.general/pull/7075)\)\.
* ipa\_config \- add module parameters to manage FreeIPA user and group objectclasses \([https\://github\.com/ansible\-collections/community\.general/pull/7019](https\://github\.com/ansible\-collections/community\.general/pull/7019)\)\.
* ipa\_config \- adds <code>idp</code> choice to <code>ipauserauthtype</code> parameter\'s choices \([https\://github\.com/ansible\-collections/community\.general/pull/7051](https\://github\.com/ansible\-collections/community\.general/pull/7051)\)\.
* npm \- module now using <code>CmdRunner</code> to execute external commands \([https\://github\.com/ansible\-collections/community\.general/pull/6989](https\://github\.com/ansible\-collections/community\.general/pull/6989)\)\.
* proxmox\_kvm \- enabled force restart of VM\, bringing the <code>force</code> parameter functionality in line with what is described in the docs \([https\://github\.com/ansible\-collections/community\.general/pull/6914](https\://github\.com/ansible\-collections/community\.general/pull/6914)\)\.
* proxmox\_vm\_info \- <code>node</code> parameter is no longer required\. Information can be obtained for the whole cluster \([https\://github\.com/ansible\-collections/community\.general/pull/6976](https\://github\.com/ansible\-collections/community\.general/pull/6976)\)\.
* proxmox\_vm\_info \- non\-existing provided by name/vmid VM would return empty results instead of failing \([https\://github\.com/ansible\-collections/community\.general/pull/7049](https\://github\.com/ansible\-collections/community\.general/pull/7049)\)\.
* redfish\_config \- add <code>DeleteAllVolumes</code> command to allow deletion of all volumes on servers \([https\://github\.com/ansible\-collections/community\.general/pull/6814](https\://github\.com/ansible\-collections/community\.general/pull/6814)\)\.
* redfish\_utils \- use <code>Controllers</code> key in redfish data to obtain Storage controllers properties \([https\://github\.com/ansible\-collections/community\.general/pull/7081](https\://github\.com/ansible\-collections/community\.general/pull/7081)\)\.
* redfish\_utils module utils \- add support for <code>PowerCycle</code> reset type for <code>redfish\_command</code> responses feature \([https\://github\.com/ansible\-collections/community\.general/issues/7083](https\://github\.com/ansible\-collections/community\.general/issues/7083)\)\.
* redfish\_utils module utils \- add support for following <code>\@odata\.nextLink</code> pagination in <code>software\_inventory</code> responses feature \([https\://github\.com/ansible\-collections/community\.general/pull/7020](https\://github\.com/ansible\-collections/community\.general/pull/7020)\)\.
* shutdown \- use <code>shutdown \-p \.\.\.</code> with FreeBSD to halt and power off machine \([https\://github\.com/ansible\-collections/community\.general/pull/7102](https\://github\.com/ansible\-collections/community\.general/pull/7102)\)\.
* sorcery \- add grimoire \(repository\) management support \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.

<a id="deprecated-features-1"></a>
### Deprecated Features

* ejabberd\_user \- deprecate the parameter <code>logging</code> in favour of producing more detailed information in the module output \([https\://github\.com/ansible\-collections/community\.general/pull/7043](https\://github\.com/ansible\-collections/community\.general/pull/7043)\)\.

<a id="bugfixes-6"></a>
### Bugfixes

* bitwarden lookup plugin \- the plugin made assumptions about the structure of a Bitwarden JSON object which may have been broken by an update in the Bitwarden API\. Remove assumptions\, and allow queries for general fields such as <code>notes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/7061](https\://github\.com/ansible\-collections/community\.general/pull/7061)\)\.
* ejabberd\_user \- module was failing to detect whether user was already created and/or password was changed \([https\://github\.com/ansible\-collections/community\.general/pull/7033](https\://github\.com/ansible\-collections/community\.general/pull/7033)\)\.
* keycloak module util \- fix missing <code>http\_agent</code>\, <code>timeout</code>\, and <code>validate\_certs</code> <code>open\_url\(\)</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/7067](https\://github\.com/ansible\-collections/community\.general/pull/7067)\)\.
* keycloak\_client inventory plugin \- fix missing client secret \([https\://github\.com/ansible\-collections/community\.general/pull/6931](https\://github\.com/ansible\-collections/community\.general/pull/6931)\)\.
* lvol \- add support for percentage of origin size specification when creating snapshot volumes \([https\://github\.com/ansible\-collections/community\.general/issues/1630](https\://github\.com/ansible\-collections/community\.general/issues/1630)\, [https\://github\.com/ansible\-collections/community\.general/pull/7053](https\://github\.com/ansible\-collections/community\.general/pull/7053)\)\.
* lxc connection plugin \- now handles <code>remote\_addr</code> defaulting to <code>inventory\_hostname</code> correctly \([https\://github\.com/ansible\-collections/community\.general/pull/7104](https\://github\.com/ansible\-collections/community\.general/pull/7104)\)\.
* oci\_utils module utils \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* proxmox\_user\_info \- avoid direct type comparisons \([https\://github\.com/ansible\-collections/community\.general/pull/7085](https\://github\.com/ansible\-collections/community\.general/pull/7085)\)\.
* snap \- fix crash when multiple snaps are specified and one has <code>\-\-\-</code> in its description \([https\://github\.com/ansible\-collections/community\.general/pull/7046](https\://github\.com/ansible\-collections/community\.general/pull/7046)\)\.
* sorcery \- fix interruption of the multi\-stage process \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* sorcery \- fix queue generation before the whole system rebuild \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.
* sorcery \- latest state no longer triggers update\_cache \([https\://github\.com/ansible\-collections/community\.general/pull/7012](https\://github\.com/ansible\-collections/community\.general/pull/7012)\)\.

<a id="v7-2-1"></a>
## v7\.2\.1

<a id="release-summary-7"></a>
### Release Summary

Bugfix release\.

<a id="bugfixes-7"></a>
### Bugfixes

* cmd\_runner module utils \- when a parameter in <code>argument\_spec</code> has no type\, meaning it is implicitly a <code>str</code>\, <code>CmdRunner</code> would fail trying to find the <code>type</code> key in that dictionary \([https\://github\.com/ansible\-collections/community\.general/pull/6968](https\://github\.com/ansible\-collections/community\.general/pull/6968)\)\.
* ejabberd\_user \- provide meaningful error message when the <code>ejabberdctl</code> command is not found \([https\://github\.com/ansible\-collections/community\.general/pull/7028](https\://github\.com/ansible\-collections/community\.general/pull/7028)\, [https\://github\.com/ansible\-collections/community\.general/issues/6949](https\://github\.com/ansible\-collections/community\.general/issues/6949)\)\.
* proxmox module utils \- fix proxmoxer library version check \([https\://github\.com/ansible\-collections/community\.general/issues/6974](https\://github\.com/ansible\-collections/community\.general/issues/6974)\, [https\://github\.com/ansible\-collections/community\.general/issues/6975](https\://github\.com/ansible\-collections/community\.general/issues/6975)\, [https\://github\.com/ansible\-collections/community\.general/pull/6980](https\://github\.com/ansible\-collections/community\.general/pull/6980)\)\.
* proxmox\_kvm \- when <code>name</code> option is provided without <code>vmid</code> and VM with that name already exists then no new VM will be created \([https\://github\.com/ansible\-collections/community\.general/issues/6911](https\://github\.com/ansible\-collections/community\.general/issues/6911)\, [https\://github\.com/ansible\-collections/community\.general/pull/6981](https\://github\.com/ansible\-collections/community\.general/pull/6981)\)\.
* rundeck \- fix <code>TypeError</code> on 404 API response \([https\://github\.com/ansible\-collections/community\.general/pull/6983](https\://github\.com/ansible\-collections/community\.general/pull/6983)\)\.

<a id="v7-2-0"></a>
## v7\.2\.0

<a id="release-summary-8"></a>
### Release Summary

Regular bugfix and feature release\.

<a id="minor-changes-4"></a>
### Minor Changes

* cobbler inventory plugin \- convert Ansible unicode strings to native Python unicode strings before passing user/password to XMLRPC client \([https\://github\.com/ansible\-collections/community\.general/pull/6923](https\://github\.com/ansible\-collections/community\.general/pull/6923)\)\.
* consul\_session \- drops requirement for the <code>python\-consul</code> library to communicate with the Consul API\, instead relying on the existing <code>requests</code> library requirement \([https\://github\.com/ansible\-collections/community\.general/pull/6755](https\://github\.com/ansible\-collections/community\.general/pull/6755)\)\.
* gitlab\_project\_variable \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* gitlab\_runner \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6927](https\://github\.com/ansible\-collections/community\.general/pull/6927)\)\.
* htpasswd \- the parameter <code>crypt\_scheme</code> is being renamed as <code>hash\_scheme</code> and added as an alias to it \([https\://github\.com/ansible\-collections/community\.general/pull/6841](https\://github\.com/ansible\-collections/community\.general/pull/6841)\)\.
* keycloak\_authentication \- added provider ID choices\, since Keycloak supports only those two specific ones \([https\://github\.com/ansible\-collections/community\.general/pull/6763](https\://github\.com/ansible\-collections/community\.general/pull/6763)\)\.
* keyring \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6927](https\://github\.com/ansible\-collections/community\.general/pull/6927)\)\.
* locale\_gen \- module has been refactored to use <code>ModuleHelper</code> and <code>CmdRunner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6903](https\://github\.com/ansible\-collections/community\.general/pull/6903)\)\.
* locale\_gen \- module now using <code>CmdRunner</code> to execute external commands \([https\://github\.com/ansible\-collections/community\.general/pull/6820](https\://github\.com/ansible\-collections/community\.general/pull/6820)\)\.
* make \- add new <code>targets</code> parameter allowing multiple targets to be used with <code>make</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6882](https\://github\.com/ansible\-collections/community\.general/pull/6882)\, [https\://github\.com/ansible\-collections/community\.general/issues/4919](https\://github\.com/ansible\-collections/community\.general/issues/4919)\)\.
* nmcli \- add support for <code>ipv4\.dns\-options</code> and <code>ipv6\.dns\-options</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6902](https\://github\.com/ansible\-collections/community\.general/pull/6902)\)\.
* npm \- minor improvement on parameter validation \([https\://github\.com/ansible\-collections/community\.general/pull/6848](https\://github\.com/ansible\-collections/community\.general/pull/6848)\)\.
* opkg \- add <code>executable</code> parameter allowing to specify the path of the <code>opkg</code> command \([https\://github\.com/ansible\-collections/community\.general/pull/6862](https\://github\.com/ansible\-collections/community\.general/pull/6862)\)\.
* pubnub\_blocks \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* redfish\_command \- add <code>account\_types</code> and <code>oem\_account\_types</code> as optional inputs to <code>AddUser</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6823](https\://github\.com/ansible\-collections/community\.general/issues/6823)\, [https\://github\.com/ansible\-collections/community\.general/pull/6871](https\://github\.com/ansible\-collections/community\.general/pull/6871)\)\.
* redfish\_info \- add <code>AccountTypes</code> and <code>OEMAccountTypes</code> to the output of <code>ListUsers</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6823](https\://github\.com/ansible\-collections/community\.general/issues/6823)\, [https\://github\.com/ansible\-collections/community\.general/pull/6871](https\://github\.com/ansible\-collections/community\.general/pull/6871)\)\.
* redfish\_info \- adds <code>ProcessorArchitecture</code> to CPU inventory \([https\://github\.com/ansible\-collections/community\.general/pull/6864](https\://github\.com/ansible\-collections/community\.general/pull/6864)\)\.
* redfish\_info \- fix for <code>GetVolumeInventory</code>\, Controller name was getting populated incorrectly and duplicates were seen in the volumes retrieved \([https\://github\.com/ansible\-collections/community\.general/pull/6719](https\://github\.com/ansible\-collections/community\.general/pull/6719)\)\.
* rhsm\_repository \- the interaction with <code>subscription\-manager</code> was
  refactored by grouping things together\, removing unused bits\, and hardening
  the way it is run\; also\, the parsing of <code>subscription\-manager repos \-\-list</code>
  was improved and made slightly faster\; no behaviour change is expected
  \([https\://github\.com/ansible\-collections/community\.general/pull/6783](https\://github\.com/ansible\-collections/community\.general/pull/6783)\,
  [https\://github\.com/ansible\-collections/community\.general/pull/6837](https\://github\.com/ansible\-collections/community\.general/pull/6837)\)\.
* scaleway\_security\_group\_rule \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* snap \- add option <code>dangerous</code> to the module\, that will map into the command line argument <code>\-\-dangerous</code>\, allowing unsigned snap files to be installed \([https\://github\.com/ansible\-collections/community\.general/pull/6908](https\://github\.com/ansible\-collections/community\.general/pull/6908)\, [https\://github\.com/ansible\-collections/community\.general/issues/5715](https\://github\.com/ansible\-collections/community\.general/issues/5715)\)\.
* tss lookup plugin \- allow to fetch secret by path\. Previously\, we could not fetch secret by path but now use <code>secret\_path</code> option to indicate to fetch secret by secret path \([https\://github\.com/ansible\-collections/community\.general/pull/6881](https\://github\.com/ansible\-collections/community\.general/pull/6881)\)\.
* xenserver\_guest\_info \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* xenserver\_guest\_powerstate \- minor refactor removing unnecessary code statements \([https\://github\.com/ansible\-collections/community\.general/pull/6928](https\://github\.com/ansible\-collections/community\.general/pull/6928)\)\.
* yum\_versionlock \- add support to pin specific package versions instead of only the package itself \([https\://github\.com/ansible\-collections/community\.general/pull/6861](https\://github\.com/ansible\-collections/community\.general/pull/6861)\, [https\://github\.com/ansible\-collections/community\.general/issues/4470](https\://github\.com/ansible\-collections/community\.general/issues/4470)\)\.

<a id="deprecated-features-2"></a>
### Deprecated Features

* flowdock \- module relies entirely on no longer responsive API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6930](https\://github\.com/ansible\-collections/community\.general/pull/6930)\)\.
* proxmox \- old feature flag <code>proxmox\_default\_behavior</code> will be removed in community\.general 10\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6836](https\://github\.com/ansible\-collections/community\.general/pull/6836)\)\.
* stackdriver \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6887](https\://github\.com/ansible\-collections/community\.general/pull/6887)\)\.
* webfaction\_app \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_db \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_domain \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_mailbox \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.
* webfaction\_site \- module relies entirely on no longer existent API endpoints\, and it will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/6909](https\://github\.com/ansible\-collections/community\.general/pull/6909)\)\.

<a id="bugfixes-8"></a>
### Bugfixes

* cobbler inventory plugin \- fix calculation of cobbler\_ipv4/6\_address \([https\://github\.com/ansible\-collections/community\.general/pull/6925](https\://github\.com/ansible\-collections/community\.general/pull/6925)\)\.
* datadog\_downtime \- presence of <code>rrule</code> param lead to the Datadog API returning Bad Request due to a missing recurrence type \([https\://github\.com/ansible\-collections/community\.general/pull/6811](https\://github\.com/ansible\-collections/community\.general/pull/6811)\)\.
* ipa\_dnszone \- fix \'idnsallowsyncptr\' key error for reverse zone \([https\://github\.com/ansible\-collections/community\.general/pull/6906](https\://github\.com/ansible\-collections/community\.general/pull/6906)\, [https\://github\.com/ansible\-collections/community\.general/issues/6905](https\://github\.com/ansible\-collections/community\.general/issues/6905)\)\.
* keycloak\_authentication \- fix Keycloak authentication flow \(step or sub\-flow\) indexing during update\, if not specified by the user \([https\://github\.com/ansible\-collections/community\.general/pull/6734](https\://github\.com/ansible\-collections/community\.general/pull/6734)\)\.
* locale\_gen \- now works for locales without the underscore character such as <code>C\.UTF\-8</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6774](https\://github\.com/ansible\-collections/community\.general/pull/6774)\, [https\://github\.com/ansible\-collections/community\.general/issues/5142](https\://github\.com/ansible\-collections/community\.general/issues/5142)\, [https\://github\.com/ansible\-collections/community\.general/issues/4305](https\://github\.com/ansible\-collections/community\.general/issues/4305)\)\.
* machinectl become plugin \- mark plugin as <code>require\_tty</code> to automatically disable pipelining\, with which this plugin is not compatible \([https\://github\.com/ansible\-collections/community\.general/issues/6932](https\://github\.com/ansible\-collections/community\.general/issues/6932)\, [https\://github\.com/ansible\-collections/community\.general/pull/6935](https\://github\.com/ansible\-collections/community\.general/pull/6935)\)\.
* nmcli \- fix support for empty list \(in compare and scrape\) \([https\://github\.com/ansible\-collections/community\.general/pull/6769](https\://github\.com/ansible\-collections/community\.general/pull/6769)\)\.
* openbsd\_pkg \- the pkg\_info\(1\) behavior has changed in OpenBSD \>7\.3\. The error message <code>Can\'t find</code> should not lead to an error case \([https\://github\.com/ansible\-collections/community\.general/pull/6785](https\://github\.com/ansible\-collections/community\.general/pull/6785)\)\.
* pacman \- module recognizes the output of <code>yay</code> running as <code>root</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6713](https\://github\.com/ansible\-collections/community\.general/pull/6713)\)\.
* proxmox \- fix error when a configuration had no <code>template</code> field \([https\://github\.com/ansible\-collections/community\.general/pull/6838](https\://github\.com/ansible\-collections/community\.general/pull/6838)\, [https\://github\.com/ansible\-collections/community\.general/issues/5372](https\://github\.com/ansible\-collections/community\.general/issues/5372)\)\.
* proxmox module utils \- add logic to detect whether an old Promoxer complains about the <code>token\_name</code> and <code>token\_value</code> parameters and provide a better error message when that happens \([https\://github\.com/ansible\-collections/community\.general/pull/6839](https\://github\.com/ansible\-collections/community\.general/pull/6839)\, [https\://github\.com/ansible\-collections/community\.general/issues/5371](https\://github\.com/ansible\-collections/community\.general/issues/5371)\)\.
* proxmox\_disk \- fix unable to create <code>cdrom</code> media due to <code>size</code> always being appended \([https\://github\.com/ansible\-collections/community\.general/pull/6770](https\://github\.com/ansible\-collections/community\.general/pull/6770)\)\.
* proxmox\_kvm \- <code>absent</code> state with <code>force</code> specified failed to stop the VM due to the <code>timeout</code> value not being passed to <code>stop\_vm</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6827](https\://github\.com/ansible\-collections/community\.general/pull/6827)\)\.
* proxmox\_kvm \- <code>restarted</code> state did not actually restart a VM in some VM configurations\. The state now uses the Proxmox reboot endpoint instead of calling the <code>stop\_vm</code> and <code>start\_vm</code> functions \([https\://github\.com/ansible\-collections/community\.general/pull/6773](https\://github\.com/ansible\-collections/community\.general/pull/6773)\)\.
* proxmox\_template \- require <code>requests\_toolbelt</code> module to fix issue with uploading large templates \([https\://github\.com/ansible\-collections/community\.general/issues/5579](https\://github\.com/ansible\-collections/community\.general/issues/5579)\, [https\://github\.com/ansible\-collections/community\.general/pull/6757](https\://github\.com/ansible\-collections/community\.general/pull/6757)\)\.
* redfish\_info \- fix <code>ListUsers</code> to not show empty account slots \([https\://github\.com/ansible\-collections/community\.general/issues/6771](https\://github\.com/ansible\-collections/community\.general/issues/6771)\, [https\://github\.com/ansible\-collections/community\.general/pull/6772](https\://github\.com/ansible\-collections/community\.general/pull/6772)\)\.
* refish\_utils module utils \- changing variable names to avoid issues occuring when fetching Volumes data \([https\://github\.com/ansible\-collections/community\.general/pull/6883](https\://github\.com/ansible\-collections/community\.general/pull/6883)\)\.
* snap \- assume default track <code>latest</code> in parameter <code>channel</code> when not specified \([https\://github\.com/ansible\-collections/community\.general/pull/6835](https\://github\.com/ansible\-collections/community\.general/pull/6835)\, [https\://github\.com/ansible\-collections/community\.general/issues/6821](https\://github\.com/ansible\-collections/community\.general/issues/6821)\)\.
* snap \- fix the processing of the commands\' output\, stripping spaces and newlines from it \([https\://github\.com/ansible\-collections/community\.general/pull/6826](https\://github\.com/ansible\-collections/community\.general/pull/6826)\, [https\://github\.com/ansible\-collections/community\.general/issues/6803](https\://github\.com/ansible\-collections/community\.general/issues/6803)\)\.

<a id="new-plugins"></a>
### New Plugins

<a id="lookup"></a>
#### Lookup

* bitwarden\_secrets\_manager \- Retrieve secrets from Bitwarden Secrets Manager

<a id="new-modules-2"></a>
### New Modules

* consul\_policy \- Manipulate Consul policies
* keycloak\_authz\_permission \- Allows administration of Keycloak client authorization permissions via Keycloak API
* keycloak\_authz\_permission\_info \- Query Keycloak client authorization permissions information
* proxmox\_vm\_info \- Retrieve information about one or more Proxmox VE virtual machines

<a id="v7-1-0"></a>
## v7\.1\.0

<a id="release-summary-9"></a>
### Release Summary

Regular bugfix and feature release\.

From this version on\, community\.general is using the new [Ansible semantic markup](https\://docs\.ansible\.com/ansible/devel/dev\_guide/developing\_modules\_documenting\.html\#semantic\-markup\-within\-module\-documentation)
in its documentation\. If you look at documentation with the ansible\-doc CLI tool
from ansible\-core before 2\.15\, please note that it does not render the markup
correctly\. You should be still able to read it in most cases\, but you need
ansible\-core 2\.15 or later to see it as it is intended\. Alternatively you can
look at [the devel docsite](https\://docs\.ansible\.com/ansible/devel/collections/community/general/)
for the rendered HTML version of the documentation of the latest release\.

<a id="minor-changes-5"></a>
### Minor Changes

* The collection will start using semantic markup \([https\://github\.com/ansible\-collections/community\.general/pull/6539](https\://github\.com/ansible\-collections/community\.general/pull/6539)\)\.
* VarDict module utils \- add method <code>VarDict\.as\_dict\(\)</code> to convert to a plain <code>dict</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/6602](https\://github\.com/ansible\-collections/community\.general/pull/6602)\)\.
* cobbler inventory plugin \- add <code>inventory\_hostname</code> option to allow using the system name for the inventory hostname \([https\://github\.com/ansible\-collections/community\.general/pull/6502](https\://github\.com/ansible\-collections/community\.general/pull/6502)\)\.
* cobbler inventory plugin \- add <code>want\_ip\_addresses</code> option to collect all interface DNS name to IP address mapping \([https\://github\.com/ansible\-collections/community\.general/pull/6711](https\://github\.com/ansible\-collections/community\.general/pull/6711)\)\.
* cobbler inventory plugin \- add primary IP addess to <code>cobbler\_ipv4\_address</code> and IPv6 address to <code>cobbler\_ipv6\_address</code> host variable \([https\://github\.com/ansible\-collections/community\.general/pull/6711](https\://github\.com/ansible\-collections/community\.general/pull/6711)\)\.
* cobbler inventory plugin \- add warning for systems with empty profiles \([https\://github\.com/ansible\-collections/community\.general/pull/6502](https\://github\.com/ansible\-collections/community\.general/pull/6502)\)\.
* copr \- respawn module to use the system python interpreter when the <code>dnf</code> python module is not available in <code>ansible\_python\_interpreter</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6522](https\://github\.com/ansible\-collections/community\.general/pull/6522)\)\.
* datadog\_monitor \- adds <code>notification\_preset\_name</code>\, <code>renotify\_occurrences</code> and <code>renotify\_statuses</code> parameters \([https\://github\.com/ansible\-collections/community\.general/issues/6521\,https\://github\.com/ansible\-collections/community\.general/issues/5823](https\://github\.com/ansible\-collections/community\.general/issues/6521\,https\://github\.com/ansible\-collections/community\.general/issues/5823)\)\.
* filesystem \- add <code>uuid</code> parameter for UUID change feature \([https\://github\.com/ansible\-collections/community\.general/pull/6680](https\://github\.com/ansible\-collections/community\.general/pull/6680)\)\.
* keycloak\_client\_rolemapping \- adds support for subgroups with additional parameter <code>parents</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6687](https\://github\.com/ansible\-collections/community\.general/pull/6687)\)\.
* keycloak\_role \- add composite roles support for realm and client roles \([https\://github\.com/ansible\-collections/community\.general/pull/6469](https\://github\.com/ansible\-collections/community\.general/pull/6469)\)\.
* ldap\_\* \- add new arguments <code>client\_cert</code> and <code>client\_key</code> to the LDAP modules in order to allow certificate authentication \([https\://github\.com/ansible\-collections/community\.general/pull/6668](https\://github\.com/ansible\-collections/community\.general/pull/6668)\)\.
* ldap\_search \- add a new <code>page\_size</code> option to enable paged searches \([https\://github\.com/ansible\-collections/community\.general/pull/6648](https\://github\.com/ansible\-collections/community\.general/pull/6648)\)\.
* lvg \- add <code>active</code> and <code>inactive</code> values to the <code>state</code> option for active state management feature \([https\://github\.com/ansible\-collections/community\.general/pull/6682](https\://github\.com/ansible\-collections/community\.general/pull/6682)\)\.
* lvg \- add <code>reset\_vg\_uuid</code>\, <code>reset\_pv\_uuid</code> options for UUID reset feature \([https\://github\.com/ansible\-collections/community\.general/pull/6682](https\://github\.com/ansible\-collections/community\.general/pull/6682)\)\.
* mas \- disable sign\-in check for macOS 12\+ as <code>mas account</code> is non\-functional \([https\://github\.com/ansible\-collections/community\.general/pull/6520](https\://github\.com/ansible\-collections/community\.general/pull/6520)\)\.
* onepassword lookup plugin \- add service account support \([https\://github\.com/ansible\-collections/community\.general/issues/6635](https\://github\.com/ansible\-collections/community\.general/issues/6635)\, [https\://github\.com/ansible\-collections/community\.general/pull/6660](https\://github\.com/ansible\-collections/community\.general/pull/6660)\)\.
* onepassword\_raw lookup plugin \- add service account support \([https\://github\.com/ansible\-collections/community\.general/issues/6635](https\://github\.com/ansible\-collections/community\.general/issues/6635)\, [https\://github\.com/ansible\-collections/community\.general/pull/6660](https\://github\.com/ansible\-collections/community\.general/pull/6660)\)\.
* opentelemetry callback plugin \- add span attributes in the span event \([https\://github\.com/ansible\-collections/community\.general/pull/6531](https\://github\.com/ansible\-collections/community\.general/pull/6531)\)\.
* opkg \- remove default value <code>\"\"</code> for parameter <code>force</code> as it causes the same behaviour of not having that parameter \([https\://github\.com/ansible\-collections/community\.general/pull/6513](https\://github\.com/ansible\-collections/community\.general/pull/6513)\)\.
* proxmox \- support <code>timezone</code> parameter at container creation \([https\://github\.com/ansible\-collections/community\.general/pull/6510](https\://github\.com/ansible\-collections/community\.general/pull/6510)\)\.
* proxmox inventory plugin \- add composite variables support for Proxmox nodes \([https\://github\.com/ansible\-collections/community\.general/issues/6640](https\://github\.com/ansible\-collections/community\.general/issues/6640)\)\.
* proxmox\_kvm \- added support for <code>tpmstate0</code> parameter to configure TPM \(Trusted Platform Module\) disk\. TPM is required for Windows 11 installations \([https\://github\.com/ansible\-collections/community\.general/pull/6533](https\://github\.com/ansible\-collections/community\.general/pull/6533)\)\.
* proxmox\_kvm \- re\-use <code>timeout</code> module param to forcefully shutdown a virtual machine when <code>state</code> is <code>stopped</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6257](https\://github\.com/ansible\-collections/community\.general/issues/6257)\)\.
* proxmox\_snap \- add <code>retention</code> parameter to delete old snapshots \([https\://github\.com/ansible\-collections/community\.general/pull/6576](https\://github\.com/ansible\-collections/community\.general/pull/6576)\)\.
* redfish\_command \- add <code>MultipartHTTPPushUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/6471](https\://github\.com/ansible\-collections/community\.general/issues/6471)\, [https\://github\.com/ansible\-collections/community\.general/pull/6612](https\://github\.com/ansible\-collections/community\.general/pull/6612)\)\.
* redhat\_subscription \- the internal <code>RegistrationBase</code> class was folded
  into the other internal <code>Rhsm</code> class\, as the separation had no purpose
  anymore
  \([https\://github\.com/ansible\-collections/community\.general/pull/6658](https\://github\.com/ansible\-collections/community\.general/pull/6658)\)\.
* rhsm\_release \- improve/harden the way <code>subscription\-manager</code> is run\;
  no behaviour change is expected
  \([https\://github\.com/ansible\-collections/community\.general/pull/6669](https\://github\.com/ansible\-collections/community\.general/pull/6669)\)\.
* snap \- module is now aware of channel when deciding whether to install or refresh the snap \([https\://github\.com/ansible\-collections/community\.general/pull/6435](https\://github\.com/ansible\-collections/community\.general/pull/6435)\, [https\://github\.com/ansible\-collections/community\.general/issues/1606](https\://github\.com/ansible\-collections/community\.general/issues/1606)\)\.
* sorcery \- minor refactor \([https\://github\.com/ansible\-collections/community\.general/pull/6525](https\://github\.com/ansible\-collections/community\.general/pull/6525)\)\.
* tss lookup plugin \- allow to fetch secret IDs which are in a folder based on folder ID\. Previously\, we could not fetch secrets based on folder ID but now use <code>fetch\_secret\_ids\_from\_folder</code> option to indicate to fetch secret IDs based on folder ID \([https\://github\.com/ansible\-collections/community\.general/issues/6223](https\://github\.com/ansible\-collections/community\.general/issues/6223)\)\.

<a id="deprecated-features-3"></a>
### Deprecated Features

* CmdRunner module utils \- deprecate <code>cmd\_runner\_fmt\.as\_default\_type\(\)</code> formatter \([https\://github\.com/ansible\-collections/community\.general/pull/6601](https\://github\.com/ansible\-collections/community\.general/pull/6601)\)\.
* MH VarsMixin module utils \- deprecates <code>VarsMixin</code> and supporting classes in favor of plain <code>vardict</code> module util \([https\://github\.com/ansible\-collections/community\.general/pull/6649](https\://github\.com/ansible\-collections/community\.general/pull/6649)\)\.
* cpanm \- value <code>compatibility</code> is deprecated as default for parameter <code>mode</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6512](https\://github\.com/ansible\-collections/community\.general/pull/6512)\)\.
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

<a id="bugfixes-9"></a>
### Bugfixes

* MH DependencyMixin module utils \- deprecation notice was popping up for modules not using dependencies \([https\://github\.com/ansible\-collections/community\.general/pull/6644](https\://github\.com/ansible\-collections/community\.general/pull/6644)\, [https\://github\.com/ansible\-collections/community\.general/issues/6639](https\://github\.com/ansible\-collections/community\.general/issues/6639)\)\.
* csv module utils \- detects and remove unicode BOM markers from incoming CSV content \([https\://github\.com/ansible\-collections/community\.general/pull/6662](https\://github\.com/ansible\-collections/community\.general/pull/6662)\)\.
* gitlab\_group \- the module passed parameters to the API call even when not set\. The module is now filtering out <code>None</code> values to remediate this \([https\://github\.com/ansible\-collections/community\.general/pull/6712](https\://github\.com/ansible\-collections/community\.general/pull/6712)\)\.
* icinga2\_host \- fix a key error when updating an existing host \([https\://github\.com/ansible\-collections/community\.general/pull/6748](https\://github\.com/ansible\-collections/community\.general/pull/6748)\)\.
* ini\_file \- add the <code>follow</code> paramter to follow the symlinks instead of replacing them \([https\://github\.com/ansible\-collections/community\.general/pull/6546](https\://github\.com/ansible\-collections/community\.general/pull/6546)\)\.
* ini\_file \- fix a bug where the inactive options were not used when possible \([https\://github\.com/ansible\-collections/community\.general/pull/6575](https\://github\.com/ansible\-collections/community\.general/pull/6575)\)\.
* keycloak module utils \- fix <code>is\_struct\_included</code> handling of lists of lists/dictionaries \([https\://github\.com/ansible\-collections/community\.general/pull/6688](https\://github\.com/ansible\-collections/community\.general/pull/6688)\)\.
* keycloak module utils \- the function <code>get\_user\_by\_username</code> now return the user representation or <code>None</code> as stated in the documentation \([https\://github\.com/ansible\-collections/community\.general/pull/6758](https\://github\.com/ansible\-collections/community\.general/pull/6758)\)\.
* proxmox\_kvm \- allow creation of VM with existing name but new vmid \([https\://github\.com/ansible\-collections/community\.general/issues/6155](https\://github\.com/ansible\-collections/community\.general/issues/6155)\, [https\://github\.com/ansible\-collections/community\.general/pull/6709](https\://github\.com/ansible\-collections/community\.general/pull/6709)\)\.
* rhsm\_repository \- when using the <code>purge</code> option\, the <code>repositories</code>
  dictionary element in the returned JSON is now properly updated according
  to the pruning operation
  \([https\://github\.com/ansible\-collections/community\.general/pull/6676](https\://github\.com/ansible\-collections/community\.general/pull/6676)\)\.
* tss lookup plugin \- fix multiple issues when using <code>fetch\_attachments\=true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6720](https\://github\.com/ansible\-collections/community\.general/pull/6720)\)\.

<a id="known-issues"></a>
### Known Issues

* Ansible markup will show up in raw form on ansible\-doc text output for ansible\-core before 2\.15\. If you have trouble deciphering the documentation markup\, please upgrade to ansible\-core 2\.15 \(or newer\)\, or read the HTML documentation on [https\://docs\.ansible\.com/ansible/devel/collections/community/general/](https\://docs\.ansible\.com/ansible/devel/collections/community/general/) \([https\://github\.com/ansible\-collections/community\.general/pull/6539](https\://github\.com/ansible\-collections/community\.general/pull/6539)\)\.

<a id="new-modules-3"></a>
### New Modules

* gitlab\_instance\_variable \- Creates\, updates\, or deletes GitLab instance variables
* gitlab\_merge\_request \- Create\, update\, or delete GitLab merge requests
* keycloak\_authentication\_required\_actions \- Allows administration of Keycloak authentication required actions
* keycloak\_user \- Create and configure a user in Keycloak
* lvg\_rename \- Renames LVM volume groups
* proxmox\_pool \- Pool management for Proxmox VE cluster
* proxmox\_pool\_member \- Add or delete members from Proxmox VE cluster pools

<a id="v7-0-1"></a>
## v7\.0\.1

<a id="release-summary-10"></a>
### Release Summary

Bugfix release for Ansible 8\.0\.0rc1\.

<a id="bugfixes-10"></a>
### Bugfixes

* nmcli \- fix bond option <code>xmit\_hash\_policy</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6527](https\://github\.com/ansible\-collections/community\.general/pull/6527)\)\.
* portage \- fix <code>changed\_use</code> and <code>newuse</code> not triggering rebuilds \([https\://github\.com/ansible\-collections/community\.general/issues/6008](https\://github\.com/ansible\-collections/community\.general/issues/6008)\, [https\://github\.com/ansible\-collections/community\.general/pull/6548](https\://github\.com/ansible\-collections/community\.general/pull/6548)\)\.
* proxmox\_tasks\_info \- remove <code>api\_user</code> \+ <code>api\_password</code> constraint from <code>required\_together</code> as it causes to require <code>api\_password</code> even when API token param is used \([https\://github\.com/ansible\-collections/community\.general/issues/6201](https\://github\.com/ansible\-collections/community\.general/issues/6201)\)\.
* zypper \- added handling of zypper exitcode 102\. Changed state is set correctly now and rc 102 is still preserved to be evaluated by the playbook \([https\://github\.com/ansible\-collections/community\.general/pull/6534](https\://github\.com/ansible\-collections/community\.general/pull/6534)\)\.

<a id="v7-0-0"></a>
## v7\.0\.0

<a id="release-summary-11"></a>
### Release Summary

This is release 7\.0\.0 of <code>community\.general</code>\, released on 2023\-05\-09\.

<a id="minor-changes-6"></a>
### Minor Changes

* apache2\_module \- add module argument <code>warn\_mpm\_absent</code> to control whether warning are raised in some edge cases \([https\://github\.com/ansible\-collections/community\.general/pull/5793](https\://github\.com/ansible\-collections/community\.general/pull/5793)\)\.
* apt\_rpm \- adds <code>clean</code>\, <code>dist\_upgrade</code> and <code>update\_kernel</code>  parameters for clear caches\, complete upgrade system\, and upgrade kernel packages \([https\://github\.com/ansible\-collections/community\.general/pull/5867](https\://github\.com/ansible\-collections/community\.general/pull/5867)\)\.
* bitwarden lookup plugin \- can now retrieve secrets from custom fields \([https\://github\.com/ansible\-collections/community\.general/pull/5694](https\://github\.com/ansible\-collections/community\.general/pull/5694)\)\.
* bitwarden lookup plugin \- implement filtering results by <code>collection\_id</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5849](https\://github\.com/ansible\-collections/community\.general/issues/5849)\)\.
* cmd\_runner module utils \- <code>cmd\_runner\_fmt\.as\_bool\(\)</code> can now take an extra parameter to format when value is false \([https\://github\.com/ansible\-collections/community\.general/pull/5647](https\://github\.com/ansible\-collections/community\.general/pull/5647)\)\.
* cpanm \- minor change\, use feature from <code>ModuleHelper</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6385](https\://github\.com/ansible\-collections/community\.general/pull/6385)\)\.
* dconf \- be forgiving about boolean values\: convert them to GVariant booleans automatically \([https\://github\.com/ansible\-collections/community\.general/pull/6206](https\://github\.com/ansible\-collections/community\.general/pull/6206)\)\.
* dconf \- if <code>gi\.repository\.GLib</code> is missing\, try to respawn in a Python interpreter that has it \([https\://github\.com/ansible\-collections/community\.general/pull/6491](https\://github\.com/ansible\-collections/community\.general/pull/6491)\)\.
* dconf \- minor refactoring improving parameters and dependencies validation \([https\://github\.com/ansible\-collections/community\.general/pull/6336](https\://github\.com/ansible\-collections/community\.general/pull/6336)\)\.
* dconf \- parse GVariants for equality comparison when the Python module <code>gi\.repository</code> is available \([https\://github\.com/ansible\-collections/community\.general/pull/6049](https\://github\.com/ansible\-collections/community\.general/pull/6049)\)\.
* deps module utils \- add function <code>failed\(\)</code> providing the ability to check the dependency check result without triggering an exception \([https\://github\.com/ansible\-collections/community\.general/pull/6383](https\://github\.com/ansible\-collections/community\.general/pull/6383)\)\.
* dig lookup plugin \- Support multiple domains to be queried as indicated in docs \([https\://github\.com/ansible\-collections/community\.general/pull/6334](https\://github\.com/ansible\-collections/community\.general/pull/6334)\)\.
* dig lookup plugin \- support CAA record type \([https\://github\.com/ansible\-collections/community\.general/pull/5913](https\://github\.com/ansible\-collections/community\.general/pull/5913)\)\.
* dnsimple \- set custom User\-Agent for API requests to DNSimple \([https\://github\.com/ansible\-collections/community\.general/pull/5927](https\://github\.com/ansible\-collections/community\.general/pull/5927)\)\.
* dnsimple\_info \- minor refactor in the code \([https\://github\.com/ansible\-collections/community\.general/pull/6440](https\://github\.com/ansible\-collections/community\.general/pull/6440)\)\.
* flatpak\_remote \- add new boolean option <code>enabled</code>\. It controls\, whether the remote is enabled or not \([https\://github\.com/ansible\-collections/community\.general/pull/5926](https\://github\.com/ansible\-collections/community\.general/pull/5926)\)\.
* gconftool2 \- refactor using <code>ModuleHelper</code> and <code>CmdRunner</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5545](https\://github\.com/ansible\-collections/community\.general/pull/5545)\)\.
* gitlab\_group\_variable\, gitlab\_project\_variable \- refactor function out to module utils \([https\://github\.com/ansible\-collections/community\.general/pull/6384](https\://github\.com/ansible\-collections/community\.general/pull/6384)\)\.
* gitlab\_project \- add <code>builds\_access\_level</code>\, <code>container\_registry\_access\_level</code> and <code>forking\_access\_level</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5706](https\://github\.com/ansible\-collections/community\.general/pull/5706)\)\.
* gitlab\_project \- add <code>releases\_access\_level</code>\, <code>environments\_access\_level</code>\, <code>feature\_flags\_access\_level</code>\, <code>infrastructure\_access\_level</code>\, <code>monitor\_access\_level</code>\, and <code>security\_and\_compliance\_access\_level</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5986](https\://github\.com/ansible\-collections/community\.general/pull/5986)\)\.
* gitlab\_project \- add new option <code>topics</code> for adding topics to GitLab projects \([https\://github\.com/ansible\-collections/community\.general/pull/6278](https\://github\.com/ansible\-collections/community\.general/pull/6278)\)\.
* gitlab\_runner \- add new boolean option <code>access\_level\_on\_creation</code>\. It controls\, whether the value of <code>access\_level</code> is used for runner registration or not\. The option <code>access\_level</code> has been ignored on registration so far and was only used on updates \([https\://github\.com/ansible\-collections/community\.general/issues/5907](https\://github\.com/ansible\-collections/community\.general/issues/5907)\, [https\://github\.com/ansible\-collections/community\.general/pull/5908](https\://github\.com/ansible\-collections/community\.general/pull/5908)\)\.
* gitlab\_runner \- allow to register group runner \([https\://github\.com/ansible\-collections/community\.general/pull/3935](https\://github\.com/ansible\-collections/community\.general/pull/3935)\)\.
* homebrew\_cask \- allows passing <code>\-\-greedy</code> option to <code>upgrade\_all</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6267](https\://github\.com/ansible\-collections/community\.general/pull/6267)\)\.
* idrac\_redfish\_command \- add <code>job\_id</code> to <code>CreateBiosConfigJob</code> response \([https\://github\.com/ansible\-collections/community\.general/issues/5603](https\://github\.com/ansible\-collections/community\.general/issues/5603)\)\.
* ilo\_redfish\_utils module utils \- change implementation of DNS Server IP and NTP Server IP update \([https\://github\.com/ansible\-collections/community\.general/pull/5804](https\://github\.com/ansible\-collections/community\.general/pull/5804)\)\.
* ipa\_group \- allow to add and remove external users with the <code>external\_user</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5897](https\://github\.com/ansible\-collections/community\.general/pull/5897)\)\.
* ipa\_hostgroup \- add <code>append</code> parameter for adding a new hosts to existing hostgroups without changing existing hostgroup members \([https\://github\.com/ansible\-collections/community\.general/pull/6203](https\://github\.com/ansible\-collections/community\.general/pull/6203)\)\.
* iptables\_state \- minor refactoring within the module \([https\://github\.com/ansible\-collections/community\.general/pull/5844](https\://github\.com/ansible\-collections/community\.general/pull/5844)\)\.
* java\_certs \- add more detailed error output when extracting certificate from PKCS12 fails \([https\://github\.com/ansible\-collections/community\.general/pull/5550](https\://github\.com/ansible\-collections/community\.general/pull/5550)\)\.
* jc filter plugin \- added the ability to use parser plugins \([https\://github\.com/ansible\-collections/community\.general/pull/6043](https\://github\.com/ansible\-collections/community\.general/pull/6043)\)\.
* jenkins\_plugin \- refactor code to module util to fix sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5565](https\://github\.com/ansible\-collections/community\.general/pull/5565)\)\.
* jira \- add worklog functionality \([https\://github\.com/ansible\-collections/community\.general/issues/6209](https\://github\.com/ansible\-collections/community\.general/issues/6209)\, [https\://github\.com/ansible\-collections/community\.general/pull/6210](https\://github\.com/ansible\-collections/community\.general/pull/6210)\)\.
* keycloak\_authentication \- add flow type option to sub flows to allow the creation of \'form\-flow\' sub flows like in Keycloak\'s built\-in registration flow \([https\://github\.com/ansible\-collections/community\.general/pull/6318](https\://github\.com/ansible\-collections/community\.general/pull/6318)\)\.
* keycloak\_group \- add new optional module parameter <code>parents</code> to properly handle keycloak subgroups \([https\://github\.com/ansible\-collections/community\.general/pull/5814](https\://github\.com/ansible\-collections/community\.general/pull/5814)\)\.
* keycloak\_user\_federation \- make <code>org\.keycloak\.storage\.ldap\.mappers\.LDAPStorageMapper</code> the default value for mappers <code>providerType</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5863](https\://github\.com/ansible\-collections/community\.general/pull/5863)\)\.
* ldap modules \- add <code>ca\_path</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/6185](https\://github\.com/ansible\-collections/community\.general/pull/6185)\)\.
* ldap modules \- add <code>xorder\_discovery</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/6045](https\://github\.com/ansible\-collections/community\.general/issues/6045)\, [https\://github\.com/ansible\-collections/community\.general/pull/6109](https\://github\.com/ansible\-collections/community\.general/pull/6109)\)\.
* ldap\_search \- the new <code>base64\_attributes</code> allows to specify which attribute values should be Base64 encoded \([https\://github\.com/ansible\-collections/community\.general/pull/6473](https\://github\.com/ansible\-collections/community\.general/pull/6473)\)\.
* lxd\_container \- add diff and check mode \([https\://github\.com/ansible\-collections/community\.general/pull/5866](https\://github\.com/ansible\-collections/community\.general/pull/5866)\)\.
* lxd\_project \- refactored code out to module utils to clear sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5549](https\://github\.com/ansible\-collections/community\.general/pull/5549)\)\.
* make \- add <code>command</code> return value to the module output \([https\://github\.com/ansible\-collections/community\.general/pull/6160](https\://github\.com/ansible\-collections/community\.general/pull/6160)\)\.
* mattermost\, rocketchat\, slack \- replace missing default favicon with docs\.ansible\.com favicon \([https\://github\.com/ansible\-collections/community\.general/pull/5928](https\://github\.com/ansible\-collections/community\.general/pull/5928)\)\.
* mksysb \- improved the output of the module in case of errors \([https\://github\.com/ansible\-collections/community\.general/issues/6263](https\://github\.com/ansible\-collections/community\.general/issues/6263)\)\.
* modprobe \- add <code>persistent</code> option \([https\://github\.com/ansible\-collections/community\.general/issues/4028](https\://github\.com/ansible\-collections/community\.general/issues/4028)\, [https\://github\.com/ansible\-collections/community\.general/pull/542](https\://github\.com/ansible\-collections/community\.general/pull/542)\)\.
* module\_helper module utils \- updated the imports to make more MH features available at <code>plugins/module\_utils/module\_helper\.py</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6464](https\://github\.com/ansible\-collections/community\.general/pull/6464)\)\.
* mssql\_script \- allow for <code>GO</code> statement to be mixed\-case for scripts not using strict syntax \([https\://github\.com/ansible\-collections/community\.general/pull/6457](https\://github\.com/ansible\-collections/community\.general/pull/6457)\)\.
* mssql\_script \- handle error condition for empty resultsets to allow for non\-returning SQL statements \(for example <code>UPDATE</code> and <code>INSERT</code>\) \([https\://github\.com/ansible\-collections/community\.general/pull/6457](https\://github\.com/ansible\-collections/community\.general/pull/6457)\)\.
* mssql\_script \- improve batching logic to allow a wider variety of input scripts\. For example\, SQL scripts slurped from Windows machines which may contain carriage return \(\'\'r\'\'\) characters \([https\://github\.com/ansible\-collections/community\.general/pull/6457](https\://github\.com/ansible\-collections/community\.general/pull/6457)\)\.
* nmap inventory plugin \- add new option <code>open</code> for only returning open ports \([https\://github\.com/ansible\-collections/community\.general/pull/6200](https\://github\.com/ansible\-collections/community\.general/pull/6200)\)\.
* nmap inventory plugin \- add new option <code>port</code> for port specific scan \([https\://github\.com/ansible\-collections/community\.general/pull/6165](https\://github\.com/ansible\-collections/community\.general/pull/6165)\)\.
* nmap inventory plugin \- add new options <code>udp\_scan</code>\, <code>icmp\_timestamp</code>\, and <code>dns\_resolve</code> for different types of scans \([https\://github\.com/ansible\-collections/community\.general/pull/5566](https\://github\.com/ansible\-collections/community\.general/pull/5566)\)\.
* nmap inventory plugin \- added environment variables for configure <code>address</code> and <code>exclude</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6351](https\://github\.com/ansible\-collections/community\.general/issues/6351)\)\.
* nmcli \- add <code>default</code> and <code>default\-or\-eui64</code> to the list of valid choices for <code>addr\_gen\_mode6</code> parameter \([https\://github\.com/ansible\-collections/community\.general/pull/5974](https\://github\.com/ansible\-collections/community\.general/pull/5974)\)\.
* nmcli \- add <code>macvlan</code> connection type \([https\://github\.com/ansible\-collections/community\.general/pull/6312](https\://github\.com/ansible\-collections/community\.general/pull/6312)\)\.
* nmcli \- add support for <code>team\.runner\-fast\-rate</code> parameter for <code>team</code> connections \([https\://github\.com/ansible\-collections/community\.general/issues/6065](https\://github\.com/ansible\-collections/community\.general/issues/6065)\)\.
* nmcli \- new module option <code>slave\_type</code> added to allow creation of various types of slave devices \([https\://github\.com/ansible\-collections/community\.general/issues/473](https\://github\.com/ansible\-collections/community\.general/issues/473)\, [https\://github\.com/ansible\-collections/community\.general/pull/6108](https\://github\.com/ansible\-collections/community\.general/pull/6108)\)\.
* one\_vm \- add a new <code>updateconf</code> option which implements the <code>one\.vm\.updateconf</code> API call \([https\://github\.com/ansible\-collections/community\.general/pull/5812](https\://github\.com/ansible\-collections/community\.general/pull/5812)\)\.
* openbsd\_pkg \- set <code>TERM</code> to <code>\'dumb\'</code> in <code>execute\_command\(\)</code> to make module less dependant on the <code>TERM</code> environment variable set on the Ansible controller \([https\://github\.com/ansible\-collections/community\.general/pull/6149](https\://github\.com/ansible\-collections/community\.general/pull/6149)\)\.
* opkg \- allow installing a package in a certain version \([https\://github\.com/ansible\-collections/community\.general/pull/5688](https\://github\.com/ansible\-collections/community\.general/pull/5688)\)\.
* opkg \- refactored module to use <code>CmdRunner</code> for executing <code>opkg</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5718](https\://github\.com/ansible\-collections/community\.general/pull/5718)\)\.
* osx\_defaults \- include stderr in error messages \([https\://github\.com/ansible\-collections/community\.general/pull/6011](https\://github\.com/ansible\-collections/community\.general/pull/6011)\)\.
* pipx \- add <code>system\_site\_packages</code> parameter to give application access to system\-wide packages \([https\://github\.com/ansible\-collections/community\.general/pull/6308](https\://github\.com/ansible\-collections/community\.general/pull/6308)\)\.
* pipx \- ensure <code>include\_injected</code> parameter works with <code>state\=upgrade</code> and <code>state\=latest</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6212](https\://github\.com/ansible\-collections/community\.general/pull/6212)\)\.
* pipx \- optional <code>install\_apps</code> parameter added to install applications from injected packages \([https\://github\.com/ansible\-collections/community\.general/pull/6198](https\://github\.com/ansible\-collections/community\.general/pull/6198)\)\.
* proxmox \- added new module parameter <code>tags</code> for use with PVE 7\+ \([https\://github\.com/ansible\-collections/community\.general/pull/5714](https\://github\.com/ansible\-collections/community\.general/pull/5714)\)\.
* proxmox \- suppress urllib3 <code>InsecureRequestWarnings</code> when <code>validate\_certs</code> option is <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5931](https\://github\.com/ansible\-collections/community\.general/pull/5931)\)\.
* proxmox\_kvm \- add new <code>archive</code> parameter\. This is needed to create a VM from an archive \(backup\) \([https\://github\.com/ansible\-collections/community\.general/pull/6159](https\://github\.com/ansible\-collections/community\.general/pull/6159)\)\.
* proxmox\_kvm \- adds <code>migrate</code> parameter to manage online migrations between hosts \([https\://github\.com/ansible\-collections/community\.general/pull/6448](https\://github\.com/ansible\-collections/community\.general/pull/6448)\)
* puppet \- add new options <code>skip\_tags</code> to exclude certain tagged resources during a puppet agent or apply \([https\://github\.com/ansible\-collections/community\.general/pull/6293](https\://github\.com/ansible\-collections/community\.general/pull/6293)\)\.
* puppet \- refactored module to use <code>CmdRunner</code> for executing <code>puppet</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5612](https\://github\.com/ansible\-collections/community\.general/pull/5612)\)\.
* rax\_scaling\_group \- refactored out code to the <code>rax</code> module utils to clear the sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5563](https\://github\.com/ansible\-collections/community\.general/pull/5563)\)\.
* redfish\_command \- add <code>PerformRequestedOperations</code> command to perform any operations necessary to continue the update flow \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_command \- add <code>update\_apply\_time</code> to <code>SimpleUpdate</code> command \([https\://github\.com/ansible\-collections/community\.general/issues/3910](https\://github\.com/ansible\-collections/community\.general/issues/3910)\)\.
* redfish\_command \- add <code>update\_status</code> to output of <code>SimpleUpdate</code> command to allow a user monitor the update in progress \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_command \- adding <code>EnableSecureBoot</code> functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5899](https\://github\.com/ansible\-collections/community\.general/pull/5899)\)\.
* redfish\_command \- adding <code>VerifyBiosAttributes</code> functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5900](https\://github\.com/ansible\-collections/community\.general/pull/5900)\)\.
* redfish\_info \- add <code>GetUpdateStatus</code> command to check the progress of a previous update request \([https\://github\.com/ansible\-collections/community\.general/issues/4276](https\://github\.com/ansible\-collections/community\.general/issues/4276)\)\.
* redfish\_info \- adds commands to retrieve the HPE ThermalConfiguration and FanPercentMinimum settings from iLO \([https\://github\.com/ansible\-collections/community\.general/pull/6208](https\://github\.com/ansible\-collections/community\.general/pull/6208)\)\.
* redfish\_utils module utils \- added PUT \(<code>put\_request\(\)</code>\) functionality \([https\://github\.com/ansible\-collections/community\.general/pull/5490](https\://github\.com/ansible\-collections/community\.general/pull/5490)\)\.
* redhat\_subscription \- add a <code>server\_proxy\_scheme</code> parameter to configure the scheme for the proxy server \([https\://github\.com/ansible\-collections/community\.general/pull/5662](https\://github\.com/ansible\-collections/community\.general/pull/5662)\)\.
* redhat\_subscription \- adds <code>token</code> parameter for subscription\-manager authentication using Red Hat API token \([https\://github\.com/ansible\-collections/community\.general/pull/5725](https\://github\.com/ansible\-collections/community\.general/pull/5725)\)\.
* redhat\_subscription \- credentials \(<code>username</code>\, <code>activationkey</code>\, and so on\) are required now only if a system needs to be registered\, or <code>force\_register</code> is specified \([https\://github\.com/ansible\-collections/community\.general/pull/5664](https\://github\.com/ansible\-collections/community\.general/pull/5664)\)\.
* redhat\_subscription \- the registration is done using the D\-Bus <code>rhsm</code> service instead of spawning a <code>subscription\-manager register</code> command\, if possible\; this avoids passing plain\-text credentials as arguments to <code>subscription\-manager register</code>\, which can be seen while that command runs \([https\://github\.com/ansible\-collections/community\.general/pull/6122](https\://github\.com/ansible\-collections/community\.general/pull/6122)\)\.
* sefcontext \- add support for path substitutions \([https\://github\.com/ansible\-collections/community\.general/issues/1193](https\://github\.com/ansible\-collections/community\.general/issues/1193)\)\.
* shutdown \- if no shutdown commands are found in the <code>search\_paths</code> then the module will attempt to shutdown the system using <code>systemctl shutdown</code> \([https\://github\.com/ansible\-collections/community\.general/issues/4269](https\://github\.com/ansible\-collections/community\.general/issues/4269)\, [https\://github\.com/ansible\-collections/community\.general/pull/6171](https\://github\.com/ansible\-collections/community\.general/pull/6171)\)\.
* slack \- add option <code>prepend\_hash</code> which allows to control whether a <code>\#</code> is prepended to <code>channel\_id</code>\. The current behavior \(value <code>auto</code>\) is to prepend <code>\#</code> unless some specific prefixes are found\. That list of prefixes is incomplete\, and there does not seem to exist a documented condition on when exactly <code>\#</code> must not be prepended\. We recommend to explicitly set <code>prepend\_hash\=always</code> or <code>prepend\_hash\=never</code> to avoid any ambiguity \([https\://github\.com/ansible\-collections/community\.general/pull/5629](https\://github\.com/ansible\-collections/community\.general/pull/5629)\)\.
* snap \- minor refactor when executing module \([https\://github\.com/ansible\-collections/community\.general/pull/5773](https\://github\.com/ansible\-collections/community\.general/pull/5773)\)\.
* snap \- refactor module to use <code>CmdRunner</code> to execute external commands \([https\://github\.com/ansible\-collections/community\.general/pull/6468](https\://github\.com/ansible\-collections/community\.general/pull/6468)\)\.
* snap\_alias \- refactor code to module utils \([https\://github\.com/ansible\-collections/community\.general/pull/6441](https\://github\.com/ansible\-collections/community\.general/pull/6441)\)\.
* snap\_alias \- refactored module to use <code>CmdRunner</code> to execute <code>snap</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5486](https\://github\.com/ansible\-collections/community\.general/pull/5486)\)\.
* spotinst\_aws\_elastigroup \- add <code>elements</code> attribute when missing in <code>list</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5553](https\://github\.com/ansible\-collections/community\.general/pull/5553)\)\.
* ssh\_config \- add <code>host\_key\_algorithms</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5605](https\://github\.com/ansible\-collections/community\.general/pull/5605)\)\.
* ssh\_config \- add <code>proxyjump</code> option \([https\://github\.com/ansible\-collections/community\.general/pull/5970](https\://github\.com/ansible\-collections/community\.general/pull/5970)\)\.
* ssh\_config \- refactor code to module util to fix sanity check \([https\://github\.com/ansible\-collections/community\.general/pull/5720](https\://github\.com/ansible\-collections/community\.general/pull/5720)\)\.
* ssh\_config \- vendored StormSSH\'s config parser to avoid having to install StormSSH to use the module \([https\://github\.com/ansible\-collections/community\.general/pull/6117](https\://github\.com/ansible\-collections/community\.general/pull/6117)\)\.
* sudoers \- add <code>setenv</code> parameters to support passing environment variables via sudo\. \([https\://github\.com/ansible\-collections/community\.general/pull/5883](https\://github\.com/ansible\-collections/community\.general/pull/5883)\)
* sudoers \- adds <code>host</code> parameter for setting hostname restrictions in sudoers rules \([https\://github\.com/ansible\-collections/community\.general/issues/5702](https\://github\.com/ansible\-collections/community\.general/issues/5702)\)\.
* terraform \- remove state file check condition and error block\, because in the native implementation of terraform will not cause errors due to the non\-existent file \([https\://github\.com/ansible\-collections/community\.general/pull/6296](https\://github\.com/ansible\-collections/community\.general/pull/6296)\)\.
* udm\_dns\_record \- minor refactor to the code \([https\://github\.com/ansible\-collections/community\.general/pull/6382](https\://github\.com/ansible\-collections/community\.general/pull/6382)\)\.
* udm\_share \- added <code>elements</code> attribute to <code>list</code> type parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5557](https\://github\.com/ansible\-collections/community\.general/pull/5557)\)\.
* udm\_user \- add <code>elements</code> attribute when missing in <code>list</code> parameters \([https\://github\.com/ansible\-collections/community\.general/pull/5559](https\://github\.com/ansible\-collections/community\.general/pull/5559)\)\.
* znode module \- optional <code>use\_tls</code> parameter added for encrypted communication \([https\://github\.com/ansible\-collections/community\.general/issues/6154](https\://github\.com/ansible\-collections/community\.general/issues/6154)\)\.

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* If you are not using this collection as part of Ansible\, but installed \(and/or upgraded\) community\.general manually\, you need to make sure to also install <code>community\.sap\_libs</code> if you are using any of the <code>sapcar\_extract</code>\, <code>sap\_task\_list\_execute</code>\, and <code>hana\_query</code> modules\.
  Without that collection installed\, the redirects for these modules do not work\.
* ModuleHelper module utils \- when the module sets output variables named <code>msg</code>\, <code>exception</code>\, <code>output</code>\, <code>vars</code>\, or <code>changed</code>\, the actual output will prefix those names with <code>\_</code> \(underscore symbol\) only when they clash with output variables generated by ModuleHelper itself\, which only occurs when handling exceptions\. Please note that this breaking change does not require a new major release since before this release\, it was not possible to add such variables to the output [due to a bug](https\://github\.com/ansible\-collections/community\.general/pull/5755) \([https\://github\.com/ansible\-collections/community\.general/pull/5765](https\://github\.com/ansible\-collections/community\.general/pull/5765)\)\.
* gconftool2 \- fix processing of <code>gconftool\-2</code> when <code>key</code> does not exist\, returning <code>null</code> instead of empty string for both <code>value</code> and <code>previous\_value</code> return values \([https\://github\.com/ansible\-collections/community\.general/issues/6028](https\://github\.com/ansible\-collections/community\.general/issues/6028)\)\.
* gitlab\_runner \- the default of <code>access\_level\_on\_creation</code> changed from <code>false</code> to <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.
* ldap\_search \- convert all string\-like values to UTF\-8 \([https\://github\.com/ansible\-collections/community\.general/issues/5704](https\://github\.com/ansible\-collections/community\.general/issues/5704)\, [https\://github\.com/ansible\-collections/community\.general/pull/6473](https\://github\.com/ansible\-collections/community\.general/pull/6473)\)\.
* nmcli \- the default of the <code>hairpin</code> option changed from <code>true</code> to <code>false</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.
* proxmox \- the default of the <code>unprivileged</code> option changed from <code>false</code> to <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.

<a id="deprecated-features-4"></a>
### Deprecated Features

* ModuleHelper module\_utils \- <code>deps</code> mixin for MH classes deprecated in favour of using the <code>deps</code> module\_utils \([https\://github\.com/ansible\-collections/community\.general/pull/6465](https\://github\.com/ansible\-collections/community\.general/pull/6465)\)\.
* consul \- deprecate using parameters unused for <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5772](https\://github\.com/ansible\-collections/community\.general/pull/5772)\)\.
* gitlab\_runner \- the default of the new option <code>access\_level\_on\_creation</code> will change from <code>false</code> to <code>true</code> in community\.general 7\.0\.0\. This will cause <code>access\_level</code> to be used during runner registration as well\, and not only during updates \([https\://github\.com/ansible\-collections/community\.general/pull/5908](https\://github\.com/ansible\-collections/community\.general/pull/5908)\)\.
* gitlab\_runner \- the option <code>access\_level</code> will lose its default value in community\.general 8\.0\.0\. From that version on\, you have set this option to <code>ref\_protected</code> explicitly\, if you want to have a protected runner \([https\://github\.com/ansible\-collections/community\.general/issues/5925](https\://github\.com/ansible\-collections/community\.general/issues/5925)\)\.
* manageiq\_policies \- deprecate <code>state\=list</code> in favour of using <code>community\.general\.manageiq\_policies\_info</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5721](https\://github\.com/ansible\-collections/community\.general/pull/5721)\)\.
* manageiq\_tags \- deprecate <code>state\=list</code> in favour of using <code>community\.general\.manageiq\_tags\_info</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5727](https\://github\.com/ansible\-collections/community\.general/pull/5727)\)\.
* rax \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax module utils \- module utils code relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_cbs \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_cbs\_attachments \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_cdb \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_cdb\_database \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_cdb\_user \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_clb \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_clb\_nodes \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_clb\_ssl \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_dns \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_dns\_record \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_facts \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_files \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_files\_objects \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_identity \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_keypair \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_meta \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_mon\_alarm \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_mon\_check \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_mon\_entity \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_mon\_notification \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_mon\_notification\_plan \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_network \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_queue \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_scaling\_group \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rax\_scaling\_policy \- module relies on deprecated library <code>pyrax</code> and will be removed in community\.general 9\.0\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5752](https\://github\.com/ansible\-collections/community\.general/pull/5752)\)\.
* rhn\_channel\, rhn\_register \- RHN hosted at redhat\.com was discontinued years
  ago\, and Spacewalk 5 \(which uses RHN\) is EOL since 2020\, May 31st\;
  while these modules could work on Uyuni / SUSE Manager \(fork of Spacewalk 5\)\,
  we have not heard about anyone using them in those setups\. Hence\, these
  modules are deprecated\, and will be removed in community\.general 10\.0\.0
  in case there are no reports about being still useful\, and potentially
  no one that steps up to maintain them
  \([https\://github\.com/ansible\-collections/community\.general/pull/6493](https\://github\.com/ansible\-collections/community\.general/pull/6493)\)\.

<a id="removed-features-previously-deprecated"></a>
### Removed Features \(previously deprecated\)

* All <code>sap</code> modules have been removed from this collection\.
  They have been migrated to the [community\.sap\_libs](https\://galaxy\.ansible\.com/community/sap\_libs) collection\.
  Redirections have been provided\.
  Following modules are affected\:
  \- sapcar\_extract
  \- sap\_task\_list\_execute
  \- hana\_query
* cmd\_runner module utils \- the <code>fmt</code> alias of <code>cmd\_runner\_fmt</code> has been removed\. Use <code>cmd\_runner\_fmt</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.
* newrelic\_deployment \- the <code>appname</code> and <code>environment</code> options have been removed\. They did not do anything \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.
* puppet \- the alias <code>show\-diff</code> of the <code>show\_diff</code> option has been removed\. Use <code>show\_diff</code> instead \([https\://github\.com/ansible\-collections/community\.general/pull/6428](https\://github\.com/ansible\-collections/community\.general/pull/6428)\)\.
* xfconf \- generating facts was deprecated in community\.general 3\.0\.0\, however three factoids\, <code>property</code>\, <code>channel</code> and <code>value</code> continued to be generated by mistake\. This behaviour has been removed and <code>xfconf</code> generate no facts whatsoever \([https\://github\.com/ansible\-collections/community\.general/pull/5502](https\://github\.com/ansible\-collections/community\.general/pull/5502)\)\.
* xfconf \- generating facts was deprecated in community\.general 3\.0\.0\, however two factoids\, <code>previous\_value</code> and <code>type</code> continued to be generated by mistake\. This behaviour has been removed and <code>xfconf</code> generate no facts whatsoever \([https\://github\.com/ansible\-collections/community\.general/pull/5502](https\://github\.com/ansible\-collections/community\.general/pull/5502)\)\.

<a id="bugfixes-11"></a>
### Bugfixes

* ModuleHelper \- fix bug when adjusting the name of reserved output variables \([https\://github\.com/ansible\-collections/community\.general/pull/5755](https\://github\.com/ansible\-collections/community\.general/pull/5755)\)\.
* alternatives \- support subcommands on Fedora 37\, which uses <code>follower</code> instead of <code>slave</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5794](https\://github\.com/ansible\-collections/community\.general/pull/5794)\)\.
* ansible\_galaxy\_install \- set default to raise exception if command\'s return code is different from zero \([https\://github\.com/ansible\-collections/community\.general/pull/5680](https\://github\.com/ansible\-collections/community\.general/pull/5680)\)\.
* ansible\_galaxy\_install \- try <code>C\.UTF\-8</code> and then fall back to <code>en\_US\.UTF\-8</code> before failing \([https\://github\.com/ansible\-collections/community\.general/pull/5680](https\://github\.com/ansible\-collections/community\.general/pull/5680)\)\.
* archive \- avoid deprecated exception class on Python 3 \([https\://github\.com/ansible\-collections/community\.general/pull/6180](https\://github\.com/ansible\-collections/community\.general/pull/6180)\)\.
* archive \- reduce RAM usage by generating CRC32 checksum over chunks \([https\://github\.com/ansible\-collections/community\.general/pull/6274](https\://github\.com/ansible\-collections/community\.general/pull/6274)\)\.
* bitwarden lookup plugin \- clarify what to do\, if the bitwarden vault is not unlocked \([https\://github\.com/ansible\-collections/community\.general/pull/5811](https\://github\.com/ansible\-collections/community\.general/pull/5811)\)\.
* cartesian and flattened lookup plugins \- adjust to parameter deprecation in ansible\-core 2\.14\'s <code>listify\_lookup\_plugin\_terms</code> helper function \([https\://github\.com/ansible\-collections/community\.general/pull/6074](https\://github\.com/ansible\-collections/community\.general/pull/6074)\)\.
* chroot connection plugin \- add <code>inventory\_hostname</code> to vars under <code>remote\_addr</code>\. This is needed for compatibility with ansible\-core 2\.13 \([https\://github\.com/ansible\-collections/community\.general/pull/5570](https\://github\.com/ansible\-collections/community\.general/pull/5570)\)\.
* cloudflare\_dns \- fixed the idempotency for SRV DNS records \([https\://github\.com/ansible\-collections/community\.general/pull/5972](https\://github\.com/ansible\-collections/community\.general/pull/5972)\)\.
* cloudflare\_dns \- fixed the possiblity of setting a root\-level SRV DNS record \([https\://github\.com/ansible\-collections/community\.general/pull/5972](https\://github\.com/ansible\-collections/community\.general/pull/5972)\)\.
* cmd\_runner module utils \- fixed bug when handling default cases in <code>cmd\_runner\_fmt\.as\_map\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5538](https\://github\.com/ansible\-collections/community\.general/pull/5538)\)\.
* cmd\_runner module utils \- formatting arguments <code>cmd\_runner\_fmt\.as\_fixed\(\)</code> was expecting an non\-existing argument \([https\://github\.com/ansible\-collections/community\.general/pull/5538](https\://github\.com/ansible\-collections/community\.general/pull/5538)\)\.
* dependent lookup plugin \- avoid warning on deprecated parameter for <code>Templar\.template\(\)</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5543](https\://github\.com/ansible\-collections/community\.general/pull/5543)\)\.
* deps module utils \- do not fail when dependency cannot be found \([https\://github\.com/ansible\-collections/community\.general/pull/6479](https\://github\.com/ansible\-collections/community\.general/pull/6479)\)\.
* dig lookup plugin \- correctly handle DNSKEY record type\'s <code>algorithm</code> field \([https\://github\.com/ansible\-collections/community\.general/pull/5914](https\://github\.com/ansible\-collections/community\.general/pull/5914)\)\.
* flatpak \- fixes idempotency detection issues\. In some cases the module could fail to properly detect already existing Flatpaks because of a parameter witch only checks the installed apps \([https\://github\.com/ansible\-collections/community\.general/pull/6289](https\://github\.com/ansible\-collections/community\.general/pull/6289)\)\.
* gconftool2 \- fix <code>changed</code> result always being <code>true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6028](https\://github\.com/ansible\-collections/community\.general/issues/6028)\)\.
* gconftool2 \- remove requirement of parameter <code>value</code> when <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6028](https\://github\.com/ansible\-collections/community\.general/issues/6028)\)\.
* gem \- fix force parameter not being passed to gem command when uninstalling \([https\://github\.com/ansible\-collections/community\.general/pull/5822](https\://github\.com/ansible\-collections/community\.general/pull/5822)\)\.
* gem \- fix hang due to interactive prompt for confirmation on specific version uninstall \([https\://github\.com/ansible\-collections/community\.general/pull/5751](https\://github\.com/ansible\-collections/community\.general/pull/5751)\)\.
* github\_webhook \- fix always changed state when no secret is provided \([https\://github\.com/ansible\-collections/community\.general/pull/5994](https\://github\.com/ansible\-collections/community\.general/pull/5994)\)\.
* gitlab\_deploy\_key \- also update <code>title</code> and not just <code>can\_push</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5888](https\://github\.com/ansible\-collections/community\.general/pull/5888)\)\.
* gitlab\_group\_variables \- fix dropping variables accidentally when GitLab introduced new properties \([https\://github\.com/ansible\-collections/community\.general/pull/5667](https\://github\.com/ansible\-collections/community\.general/pull/5667)\)\.
* gitlab\_project\_variables \- fix dropping variables accidentally when GitLab introduced new properties \([https\://github\.com/ansible\-collections/community\.general/pull/5667](https\://github\.com/ansible\-collections/community\.general/pull/5667)\)\.
* gitlab\_runner \- fix <code>KeyError</code> on runner creation and update \([https\://github\.com/ansible\-collections/community\.general/issues/6112](https\://github\.com/ansible\-collections/community\.general/issues/6112)\)\.
* icinga2\_host \- fix the data structure sent to Icinga to make use of host templates and template vars \([https\://github\.com/ansible\-collections/community\.general/pull/6286](https\://github\.com/ansible\-collections/community\.general/pull/6286)\)\.
* idrac\_redfish\_command \- allow user to specify <code>resource\_id</code> for <code>CreateBiosConfigJob</code> to specify an exact manager \([https\://github\.com/ansible\-collections/community\.general/issues/2090](https\://github\.com/ansible\-collections/community\.general/issues/2090)\)\.
* influxdb\_user \- fix running in check mode when the user does not exist yet \([https\://github\.com/ansible\-collections/community\.general/pull/6111](https\://github\.com/ansible\-collections/community\.general/pull/6111)\)\.
* ini\_file \- make <code>section</code> parameter not required so it is possible to pass <code>null</code> as a value\. This only was possible in the past due to a bug in ansible\-core that now has been fixed \([https\://github\.com/ansible\-collections/community\.general/pull/6404](https\://github\.com/ansible\-collections/community\.general/pull/6404)\)\.
* interfaces\_file \- fix reading options in lines not starting with a space \([https\://github\.com/ansible\-collections/community\.general/issues/6120](https\://github\.com/ansible\-collections/community\.general/issues/6120)\)\.
* jail connection plugin \- add <code>inventory\_hostname</code> to vars under <code>remote\_addr</code>\. This is needed for compatibility with ansible\-core 2\.13 \([https\://github\.com/ansible\-collections/community\.general/pull/6118](https\://github\.com/ansible\-collections/community\.general/pull/6118)\)\.
* jenkins\_build \- fix the logical flaw when deleting a Jenkins build \([https\://github\.com/ansible\-collections/community\.general/pull/5514](https\://github\.com/ansible\-collections/community\.general/pull/5514)\)\.
* jenkins\_plugin \- fix error due to undefined variable when updates file is not downloaded \([https\://github\.com/ansible\-collections/community\.general/pull/6100](https\://github\.com/ansible\-collections/community\.general/pull/6100)\)\.
* keycloak \- improve error messages \([https\://github\.com/ansible\-collections/community\.general/pull/6318](https\://github\.com/ansible\-collections/community\.general/pull/6318)\)\.
* keycloak\_client \- fix accidental replacement of value for attribute <code>saml\.signing\.private\.key</code> with <code>no\_log</code> in wrong contexts \([https\://github\.com/ansible\-collections/community\.general/pull/5934](https\://github\.com/ansible\-collections/community\.general/pull/5934)\)\.
* keycloak\_client\_rolemapping \- calculate <code>proposed</code> and <code>after</code> return values properly \([https\://github\.com/ansible\-collections/community\.general/pull/5619](https\://github\.com/ansible\-collections/community\.general/pull/5619)\)\.
* keycloak\_client\_rolemapping \- remove only listed mappings with <code>state\=absent</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5619](https\://github\.com/ansible\-collections/community\.general/pull/5619)\)\.
* keycloak\_user\_federation \- fixes federation creation issue\. When a new federation was created and at the same time a default / standard mapper was also changed / updated the creation process failed as a bad None set variable led to a bad malformed url request \([https\://github\.com/ansible\-collections/community\.general/pull/5750](https\://github\.com/ansible\-collections/community\.general/pull/5750)\)\.
* keycloak\_user\_federation \- fixes idempotency detection issues\. In some cases the module could fail to properly detect already existing user federations because of a buggy seemingly superflous extra query parameter \([https\://github\.com/ansible\-collections/community\.general/pull/5732](https\://github\.com/ansible\-collections/community\.general/pull/5732)\)\.
* loganalytics callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* logdna callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* logstash callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* lxc\_container \- fix the arguments of the lxc command which broke the creation and cloning of containers \([https\://github\.com/ansible\-collections/community\.general/issues/5578](https\://github\.com/ansible\-collections/community\.general/issues/5578)\)\.
* lxd\_\* modules\, lxd inventory plugin \- fix TLS/SSL certificate validation problems by using the correct purpose when creating the TLS context \([https\://github\.com/ansible\-collections/community\.general/issues/5616](https\://github\.com/ansible\-collections/community\.general/issues/5616)\, [https\://github\.com/ansible\-collections/community\.general/pull/6034](https\://github\.com/ansible\-collections/community\.general/pull/6034)\)\.
* memset \- fix memset urlerror handling \([https\://github\.com/ansible\-collections/community\.general/pull/6114](https\://github\.com/ansible\-collections/community\.general/pull/6114)\)\.
* nmcli \- fix change handling of values specified as an integer 0 \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- fix failure to handle WIFI settings when connection type not specified \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- fix improper detection of changes to <code>wifi\.wake\-on\-wlan</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5431](https\://github\.com/ansible\-collections/community\.general/pull/5431)\)\.
* nmcli \- fixed idempotency issue for bridge connections\. Module forced default value of <code>bridge\.priority</code> to nmcli if not set\; if <code>bridge\.stp</code> is disabled nmcli ignores it and keep default \([https\://github\.com/ansible\-collections/community\.general/issues/3216](https\://github\.com/ansible\-collections/community\.general/issues/3216)\, [https\://github\.com/ansible\-collections/community\.general/issues/4683](https\://github\.com/ansible\-collections/community\.general/issues/4683)\)\.
* nmcli \- fixed idempotency issue when module params is set to <code>may\_fail4\=false</code> and <code>method4\=disabled</code>\; in this case nmcli ignores change and keeps their own default value <code>yes</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6106](https\://github\.com/ansible\-collections/community\.general/pull/6106)\)\.
* nmcli \- implemented changing mtu value on vlan interfaces \([https\://github\.com/ansible\-collections/community\.general/issues/4387](https\://github\.com/ansible\-collections/community\.general/issues/4387)\)\.
* nmcli \- order is significant for lists of addresses \([https\://github\.com/ansible\-collections/community\.general/pull/6048](https\://github\.com/ansible\-collections/community\.general/pull/6048)\)\.
* nsupdate \- fix zone lookup\. The SOA record for an existing zone is returned as an answer RR and not as an authority RR \([https\://github\.com/ansible\-collections/community\.general/issues/5817](https\://github\.com/ansible\-collections/community\.general/issues/5817)\, [https\://github\.com/ansible\-collections/community\.general/pull/5818](https\://github\.com/ansible\-collections/community\.general/pull/5818)\)\.
* one\_vm \- avoid splitting labels that are <code>None</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5489](https\://github\.com/ansible\-collections/community\.general/pull/5489)\)\.
* one\_vm \- fix syntax error when creating VMs with a more complex template \([https\://github\.com/ansible\-collections/community\.general/issues/6225](https\://github\.com/ansible\-collections/community\.general/issues/6225)\)\.
* onepassword lookup plugin \- Changed to ignore errors from \"op account get\" calls\. Previously\, errors would prevent auto\-signin code from executing \([https\://github\.com/ansible\-collections/community\.general/pull/5942](https\://github\.com/ansible\-collections/community\.general/pull/5942)\)\.
* onepassword\_raw \- add missing parameter to plugin documentation \([https\://github\.com/ansible\-collections/community\.general/issues/5506](https\://github\.com/ansible\-collections/community\.general/issues/5506)\)\.
* opkg \- fix issue that <code>force\=reinstall</code> would not reinstall an existing package \([https\://github\.com/ansible\-collections/community\.general/pull/5705](https\://github\.com/ansible\-collections/community\.general/pull/5705)\)\.
* opkg \- fixes bug when using <code>update\_cache\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/6004](https\://github\.com/ansible\-collections/community\.general/issues/6004)\)\.
* passwordstore lookup plugin \- make compatible with ansible\-core 2\.16 \([https\://github\.com/ansible\-collections/community\.general/pull/6447](https\://github\.com/ansible\-collections/community\.general/pull/6447)\)\.
* pipx \- fixed handling of <code>install\_deps\=true</code> with <code>state\=latest</code> and <code>state\=upgrade</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6303](https\://github\.com/ansible\-collections/community\.general/pull/6303)\)\.
* portage \- update the logic for generating the emerge command arguments to ensure that <code>withbdeps\: false</code> results in a passing an <code>n</code> argument with the <code>\-\-with\-bdeps</code> emerge flag \([https\://github\.com/ansible\-collections/community\.general/issues/6451](https\://github\.com/ansible\-collections/community\.general/issues/6451)\, [https\://github\.com/ansible\-collections/community\.general/pull/6456](https\://github\.com/ansible\-collections/community\.general/pull/6456)\)\.
* proxmox inventory plugin \- fix bug while templating when using templates for the <code>url</code>\, <code>user</code>\, <code>password</code>\, <code>token\_id</code>\, or <code>token\_secret</code> options \([https\://github\.com/ansible\-collections/community\.general/pull/5640](https\://github\.com/ansible\-collections/community\.general/pull/5640)\)\.
* proxmox inventory plugin \- handle tags delimited by semicolon instead of comma\, which happens from Proxmox 7\.3 on \([https\://github\.com/ansible\-collections/community\.general/pull/5602](https\://github\.com/ansible\-collections/community\.general/pull/5602)\)\.
* proxmox\_disk \- avoid duplicate <code>vmid</code> reference \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5493](https\://github\.com/ansible\-collections/community\.general/pull/5493)\)\.
* proxmox\_disk \- fixed issue with read timeout on import action \([https\://github\.com/ansible\-collections/community\.general/pull/5803](https\://github\.com/ansible\-collections/community\.general/pull/5803)\)\.
* proxmox\_disk \- fixed possible issues with redundant <code>vmid</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5672](https\://github\.com/ansible\-collections/community\.general/pull/5672)\)\.
* proxmox\_nic \- fixed possible issues with redundant <code>vmid</code> parameter \([https\://github\.com/ansible\-collections/community\.general/issues/5492](https\://github\.com/ansible\-collections/community\.general/issues/5492)\, [https\://github\.com/ansible\-collections/community\.general/pull/5672](https\://github\.com/ansible\-collections/community\.general/pull/5672)\)\.
* puppet \- handling <code>noop</code> parameter was not working at all\, now it is has been fixed \([https\://github\.com/ansible\-collections/community\.general/issues/6452](https\://github\.com/ansible\-collections/community\.general/issues/6452)\, [https\://github\.com/ansible\-collections/community\.general/issues/6458](https\://github\.com/ansible\-collections/community\.general/issues/6458)\)\.
* redfish\_utils \- removed basic auth HTTP header when performing a GET on the service root resource and when performing a POST to the session collection \([https\://github\.com/ansible\-collections/community\.general/issues/5886](https\://github\.com/ansible\-collections/community\.general/issues/5886)\)\.
* redhat\_subscription \- do not ignore <code>consumer\_name</code> and other variables if <code>activationkey</code> is specified \([https\://github\.com/ansible\-collections/community\.general/issues/3486](https\://github\.com/ansible\-collections/community\.general/issues/3486)\, [https\://github\.com/ansible\-collections/community\.general/pull/5627](https\://github\.com/ansible\-collections/community\.general/pull/5627)\)\.
* redhat\_subscription \- do not pass arguments to <code>subscription\-manager register</code> for things already configured\; now a specified <code>rhsm\_baseurl</code> is properly set for subscription\-manager \([https\://github\.com/ansible\-collections/community\.general/pull/5583](https\://github\.com/ansible\-collections/community\.general/pull/5583)\)\.
* redhat\_subscription \- do not use D\-Bus for registering when <code>environment</code> is specified\, so it possible to specify again the environment names for registering\, as the D\-Bus APIs work only with IDs \([https\://github\.com/ansible\-collections/community\.general/pull/6319](https\://github\.com/ansible\-collections/community\.general/pull/6319)\)\.
* redhat\_subscription \- try to unregister only when already registered when <code>force\_register</code> is specified \([https\://github\.com/ansible\-collections/community\.general/issues/6258](https\://github\.com/ansible\-collections/community\.general/issues/6258)\, [https\://github\.com/ansible\-collections/community\.general/pull/6259](https\://github\.com/ansible\-collections/community\.general/pull/6259)\)\.
* redhat\_subscription \- use the right D\-Bus options for environments when registering a CentOS Stream 8 system and using <code>environment</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6275](https\://github\.com/ansible\-collections/community\.general/pull/6275)\)\.
* redhat\_subscription\, rhsm\_release\, rhsm\_repository \- cleanly fail when not running as root\, rather than hanging on an interactive <code>console\-helper</code> prompt\; they all interact with <code>subscription\-manager</code>\, which already requires to be run as root \([https\://github\.com/ansible\-collections/community\.general/issues/734](https\://github\.com/ansible\-collections/community\.general/issues/734)\, [https\://github\.com/ansible\-collections/community\.general/pull/6211](https\://github\.com/ansible\-collections/community\.general/pull/6211)\)\.
* rhsm\_release \- make <code>release</code> parameter not required so it is possible to pass <code>null</code> as a value\. This only was possible in the past due to a bug in ansible\-core that now has been fixed \([https\://github\.com/ansible\-collections/community\.general/pull/6401](https\://github\.com/ansible\-collections/community\.general/pull/6401)\)\.
* rundeck module utils \- fix errors caused by the API empty responses \([https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)
* rundeck\_acl\_policy \- fix <code>TypeError \- byte indices must be integers or slices\, not str</code> error caused by empty API response\. Update the module to use <code>module\_utils\.rundeck</code> functions \([https\://github\.com/ansible\-collections/community\.general/pull/5887](https\://github\.com/ansible\-collections/community\.general/pull/5887)\, [https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)\.
* rundeck\_project \- update the module to use <code>module\_utils\.rundeck</code> functions \([https\://github\.com/ansible\-collections/community\.general/issues/5742](https\://github\.com/ansible\-collections/community\.general/issues/5742)\) \([https\://github\.com/ansible\-collections/community\.general/pull/6300](https\://github\.com/ansible\-collections/community\.general/pull/6300)\)
* snap\_alias \- module would only recognize snap names containing letter\, numbers or the underscore character\, failing to identify valid snap names such as <code>lxd\.lxc</code> \([https\://github\.com/ansible\-collections/community\.general/pull/6361](https\://github\.com/ansible\-collections/community\.general/pull/6361)\)\.
* splunk callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* sumologic callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* syslog\_json callback plugin \- adjust type of callback to <code>notification</code>\, it was incorrectly classified as <code>aggregate</code> before \([https\://github\.com/ansible\-collections/community\.general/pull/5761](https\://github\.com/ansible\-collections/community\.general/pull/5761)\)\.
* terraform \- fix <code>current</code> workspace never getting appended to the <code>all</code> key in the <code>workspace\_ctf</code> object \([https\://github\.com/ansible\-collections/community\.general/pull/5735](https\://github\.com/ansible\-collections/community\.general/pull/5735)\)\.
* terraform \- fix <code>terraform init</code> failure when there are multiple workspaces on the remote backend and when <code>default</code> workspace is missing by setting <code>TF\_WORKSPACE</code> environmental variable to the value of <code>workspace</code> when used \([https\://github\.com/ansible\-collections/community\.general/pull/5735](https\://github\.com/ansible\-collections/community\.general/pull/5735)\)\.
* terraform \- fix broken <code>warn\(\)</code> call \([https\://github\.com/ansible\-collections/community\.general/pull/6497](https\://github\.com/ansible\-collections/community\.general/pull/6497)\)\.
* terraform and timezone \- slight refactoring to avoid linter reporting potentially undefined variables \([https\://github\.com/ansible\-collections/community\.general/pull/5933](https\://github\.com/ansible\-collections/community\.general/pull/5933)\)\.
* terraform module \- disable ANSI escape sequences during validation phase \([https\://github\.com/ansible\-collections/community\.general/pull/5843](https\://github\.com/ansible\-collections/community\.general/pull/5843)\)\.
* tss lookup plugin \- allow to download secret attachments\. Previously\, we could not download secret attachments but now use <code>fetch\_attachments</code> and <code>file\_download\_path</code> variables to download attachments \([https\://github\.com/ansible\-collections/community\.general/issues/6224](https\://github\.com/ansible\-collections/community\.general/issues/6224)\)\.
* unixy callback plugin \- fix plugin to work with ansible\-core 2\.14 by using Ansible\'s configuration manager for handling options \([https\://github\.com/ansible\-collections/community\.general/issues/5600](https\://github\.com/ansible\-collections/community\.general/issues/5600)\)\.
* unixy callback plugin \- fix typo introduced when updating to use Ansible\'s configuration manager for handling options \([https\://github\.com/ansible\-collections/community\.general/issues/5600](https\://github\.com/ansible\-collections/community\.general/issues/5600)\)\.
* various plugins and modules \- remove unnecessary imports \([https\://github\.com/ansible\-collections/community\.general/pull/5940](https\://github\.com/ansible\-collections/community\.general/pull/5940)\)\.
* vdo \- now uses <code>yaml\.safe\_load\(\)</code> to parse command output instead of the deprecated <code>yaml\.load\(\)</code> which is potentially unsafe\. Using <code>yaml\.load\(\)</code> without explicitely setting a <code>Loader\=</code> is also an error in pyYAML 6\.0 \([https\://github\.com/ansible\-collections/community\.general/pull/5632](https\://github\.com/ansible\-collections/community\.general/pull/5632)\)\.
* vmadm \- fix for index out of range error in <code>get\_vm\_uuid</code> \([https\://github\.com/ansible\-collections/community\.general/pull/5628](https\://github\.com/ansible\-collections/community\.general/pull/5628)\)\.
* xenorchestra inventory plugin \- fix failure to receive objects from server due to not checking the id of the response \([https\://github\.com/ansible\-collections/community\.general/pull/6227](https\://github\.com/ansible\-collections/community\.general/pull/6227)\)\.
* xfs\_quota \- in case of a project quota\, the call to <code>xfs\_quota</code> did not initialize/reset the project \([https\://github\.com/ansible\-collections/community\.general/issues/5143](https\://github\.com/ansible\-collections/community\.general/issues/5143)\)\.
* xml \- fixed a bug where empty <code>children</code> list would not be set \([https\://github\.com/ansible\-collections/community\.general/pull/5808](https\://github\.com/ansible\-collections/community\.general/pull/5808)\)\.
* yarn \- fix <code>global\=true</code> to check for the configured global folder instead of assuming the default \([https\://github\.com/ansible\-collections/community\.general/pull/5829](https\://github\.com/ansible\-collections/community\.general/pull/5829)\)
* yarn \- fix <code>global\=true</code> to not fail when <em class="title-reference">executable</em> wasn\'t specified \([https\://github\.com/ansible\-collections/community\.general/pull/6132](https\://github\.com/ansible\-collections/community\.general/pull/6132)\)
* yarn \- fix <code>state\=absent</code> not working with <code>global\=true</code> when the package does not include a binary \([https\://github\.com/ansible\-collections/community\.general/pull/5829](https\://github\.com/ansible\-collections/community\.general/pull/5829)\)
* yarn \- fix <code>state\=latest</code> not working with <code>global\=true</code> \([https\://github\.com/ansible\-collections/community\.general/issues/5712](https\://github\.com/ansible\-collections/community\.general/issues/5712)\)\.
* yarn \- fixes bug where yarn module tasks would fail when warnings were emitted from Yarn\. The <code>yarn\.list</code> method was not filtering out warnings \([https\://github\.com/ansible\-collections/community\.general/issues/6127](https\://github\.com/ansible\-collections/community\.general/issues/6127)\)\.
* zfs\_delegate\_admin \- zfs allow output can now be parsed when uids/gids are not known to the host system \([https\://github\.com/ansible\-collections/community\.general/pull/5943](https\://github\.com/ansible\-collections/community\.general/pull/5943)\)\.
* zypper \- make package managing work on readonly filesystem of openSUSE MicroOS \([https\://github\.com/ansible\-collections/community\.general/pull/5615](https\://github\.com/ansible\-collections/community\.general/pull/5615)\)\.

<a id="new-plugins-1"></a>
### New Plugins

<a id="lookup-1"></a>
#### Lookup

* merge\_variables \- merge variables with a certain suffix

<a id="new-modules-4"></a>
### New Modules

* btrfs\_info \- Query btrfs filesystem info
* btrfs\_subvolume \- Manage btrfs subvolumes
* gitlab\_project\_badge \- Manage project badges on GitLab Server
* ilo\_redfish\_command \- Manages Out\-Of\-Band controllers using Redfish APIs
* ipbase\_info \- Retrieve IP geolocation and other facts of a host\'s IP address using the ipbase\.com API
* kdeconfig \- Manage KDE configuration files
* keycloak\_authz\_authorization\_scope \- Allows administration of Keycloak client authorization scopes via Keycloak API
* keycloak\_clientscope\_type \- Set the type of aclientscope in realm or client via Keycloak API
* keycloak\_clientsecret\_info \- Retrieve client secret via Keycloak API
* keycloak\_clientsecret\_regenerate \- Regenerate Keycloak client secret via Keycloak API
* ocapi\_command \- Manages Out\-Of\-Band controllers using Open Composable API \(OCAPI\)
* ocapi\_info \- Manages Out\-Of\-Band controllers using Open Composable API \(OCAPI\)
