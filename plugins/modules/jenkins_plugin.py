#!/usr/bin/python

# Copyright (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations


DOCUMENTATION = r"""
module: jenkins_plugin
author: Jiri Tyr (@jtyr)
short_description: Add or remove Jenkins plugin
description:
  - Ansible module which helps to manage Jenkins plugins.
attributes:
  check_mode:
    support: full
  diff_mode:
    support: none

options:
  group:
    type: str
    description:
      - GID or name of the Jenkins group on the OS.
    default: jenkins
  jenkins_home:
    type: path
    description:
      - Home directory of the Jenkins user.
    default: /var/lib/jenkins
  mode:
    type: raw
    description:
      - File mode applied on versioned plugins.
    default: '0644'
  name:
    type: str
    description:
      - Plugin name.
    required: true
  owner:
    type: str
    description:
      - UID or name of the Jenkins user on the OS.
    default: jenkins
  state:
    type: str
    description:
      - Desired plugin state.
      - If set to V(latest), the check for new version is performed every time. This is suitable to keep the plugin up-to-date.
    choices: [absent, present, pinned, unpinned, enabled, disabled, latest]
    default: present
  timeout:
    type: int
    description:
      - Server connection timeout in secs.
    default: 30
  updates_expiration:
    type: int
    description:
      - Number of seconds after which a new copy of the C(update-center.json) file is downloaded. This is used to avoid the
        need to download the plugin to calculate its checksum when O(state=latest) is specified.
      - Set it to V(0) if no cache file should be used. In that case, the plugin file is always downloaded to calculate its
        checksum when O(state=latest) is specified.
    default: 86400
  updates_url:
    type: list
    elements: str
    description:
      - A list of base URL(s) to retrieve C(update-center.json), and direct plugin files from.
      - This can be a list since community.general 3.3.0.
    default: ['https://updates.jenkins.io', 'http://mirrors.jenkins.io']
  updates_url_username:
    description:
      - If using a custom O(updates_url), set this as the username of the user with access to the URL.
      - If the custom O(updates_url) does not require authentication, this can be left empty.
    type: str
    version_added: 11.2.0
  updates_url_password:
    description:
      - If using a custom O(updates_url), set this as the password of the user with access to the URL.
      - If the custom O(updates_url) does not require authentication, this can be left empty.
    type: str
    version_added: 11.2.0
  update_json_url_segment:
    type: list
    elements: str
    description:
      - A list of URL segment(s) to retrieve the update center JSON file from.
    default: ['update-center.json', 'updates/update-center.json']
    version_added: 3.3.0
  plugin_versions_url_segment:
    type: list
    elements: str
    description:
      - A list of URL segment(s) to retrieve the plugin versions JSON file from.
    default: ['plugin-versions.json', 'current/plugin-versions.json']
    version_added: 11.2.0
  latest_plugins_url_segments:
    type: list
    elements: str
    description:
      - Path inside the O(updates_url) to get latest plugins from.
    default: ['latest']
    version_added: 3.3.0
  versioned_plugins_url_segments:
    type: list
    elements: str
    description:
      - Path inside the O(updates_url) to get specific version of plugins from.
    default: ['download/plugins', 'plugins']
    version_added: 3.3.0
  url:
    type: str
    description:
      - URL of the Jenkins server.
    default: http://localhost:8080
  version:
    type: str
    description:
      - Plugin version number.
      - If this option is specified, all plugin dependencies must be installed manually.
      - It might take longer to verify that the correct version is installed. This is especially true if a specific version
        number is specified.
      - Quote the version to prevent the value to be interpreted as float. For example if V(1.20) would be unquoted, it would
        become V(1.2).
  with_dependencies:
    description:
      - Defines whether to install plugin dependencies.
      - In earlier versions, this option had no effect when a specific O(version) was set.
        Since community.general 11.2.0, dependencies are also installed for versioned plugins.
    type: bool
    default: true

notes:
  - Plugin installation should be run under root or the same user which owns the plugin files on the disk. Only if the plugin
    is not installed yet and no version is specified, the API installation is performed which requires only the Web UI credentials.
  - It is necessary to notify the handler or call the M(ansible.builtin.service) module to restart the Jenkins service after
    a new plugin was installed.
  - Pinning works only if the plugin is installed and Jenkins service was successfully restarted after the plugin installation.
  - It is not possible to run the module remotely by changing the O(url) parameter to point to the Jenkins server. The module
    must be used on the host where Jenkins runs as it needs direct access to the plugin files.
  - If using a custom O(updates_url), ensure that the URL provides a C(plugin-versions.json) file.
    This file must include metadata for all available plugin versions to support version compatibility resolution.
    The file should be in the same format as the one provided by Jenkins update center (https://updates.jenkins.io/current/plugin-versions.json).
extends_documentation_fragment:
  - ansible.builtin.url
  - ansible.builtin.files
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Install plugin
  community.general.jenkins_plugin:
    name: build-pipeline-plugin

- name: Install plugin without its dependencies
  community.general.jenkins_plugin:
    name: build-pipeline-plugin
    with_dependencies: false

- name: Make sure the plugin is always up-to-date
  community.general.jenkins_plugin:
    name: token-macro
    state: latest

- name: Install specific version of the plugin
  community.general.jenkins_plugin:
    name: token-macro
    version: "1.15"

- name: Pin the plugin
  community.general.jenkins_plugin:
    name: token-macro
    state: pinned

- name: Unpin the plugin
  community.general.jenkins_plugin:
    name: token-macro
    state: unpinned

- name: Enable the plugin
  community.general.jenkins_plugin:
    name: token-macro
    state: enabled

- name: Disable the plugin
  community.general.jenkins_plugin:
    name: token-macro
    state: disabled

- name: Uninstall plugin
  community.general.jenkins_plugin:
    name: build-pipeline-plugin
    state: absent

#
# Example of how to authenticate
#
- name: Install plugin
  community.general.jenkins_plugin:
    name: build-pipeline-plugin
    url_username: admin
    url_password: p4ssw0rd
    url: http://localhost:8888

#
# Example of how to authenticate with serverless deployment
#
- name: Update plugins on ECS Fargate Jenkins instance
  community.general.jenkins_plugin:
    # plugin name and version
    name: ws-cleanup
    version: '0.45'
    # Jenkins home path mounted on ec2-helper VM (example)
    jenkins_home: "/mnt/{{ jenkins_instance }}"
    # matching the UID/GID to one in official Jenkins image
    owner: 1000
    group: 1000
    # Jenkins instance URL and admin credentials
    url: "https://{{ jenkins_instance }}.com/"
    url_username: admin
    url_password: p4ssw0rd
  # make module work from EC2 which has local access
  # to EFS mount as well as Jenkins URL
  delegate_to: ec2-helper
  vars:
    jenkins_instance: foobar

#
# Example of a Play which handles Jenkins restarts during the state changes
#
- name: Jenkins Master play
  hosts: jenkins-master
  vars:
    my_jenkins_plugins:
      token-macro:
        enabled: true
      build-pipeline-plugin:
        version: "1.4.9"
        pinned: false
        enabled: true
  tasks:
    - name: Install plugins without a specific version
      community.general.jenkins_plugin:
        name: "{{ item.key }}"
      register: my_jenkins_plugin_unversioned
      when: >
        'version' not in item.value
      with_dict: "{{ my_jenkins_plugins }}"

    - name: Install plugins with a specific version
      community.general.jenkins_plugin:
        name: "{{ item.key }}"
        version: "{{ item.value['version'] }}"
      register: my_jenkins_plugin_versioned
      when: >
        'version' in item.value
      with_dict: "{{ my_jenkins_plugins }}"

    - name: Initiate the fact
      ansible.builtin.set_fact:
        jenkins_restart_required: false

    - name: Check if restart is required by any of the versioned plugins
      ansible.builtin.set_fact:
        jenkins_restart_required: true
      when: item.changed
      with_items: "{{ my_jenkins_plugin_versioned.results }}"

    - name: Check if restart is required by any of the unversioned plugins
      ansible.builtin.set_fact:
        jenkins_restart_required: true
      when: item.changed
      with_items: "{{ my_jenkins_plugin_unversioned.results }}"

    - name: Restart Jenkins if required
      ansible.builtin.service:
        name: jenkins
        state: restarted
      when: jenkins_restart_required

    - name: Wait for Jenkins to start up
      ansible.builtin.uri:
        url: http://localhost:8080
        status_code: 200
        timeout: 5
      register: jenkins_service_status
      # Keep trying for 5 mins in 5 sec intervals
      retries: 60
      delay: 5
      until: >
        'status' in jenkins_service_status and
        jenkins_service_status['status'] == 200
      when: jenkins_restart_required

    - name: Reset the fact
      ansible.builtin.set_fact:
        jenkins_restart_required: false
      when: jenkins_restart_required

    - name: Plugin pinning
      community.general.jenkins_plugin:
        name: "{{ item.key }}"
        state: "{{ 'pinned' if item.value['pinned'] else 'unpinned'}}"
      when: >
        'pinned' in item.value
      with_dict: "{{ my_jenkins_plugins }}"

    - name: Plugin enabling
      community.general.jenkins_plugin:
        name: "{{ item.key }}"
        state: "{{ 'enabled' if item.value['enabled'] else 'disabled'}}"
      when: >
        'enabled' in item.value
      with_dict: "{{ my_jenkins_plugins }}"
"""

RETURN = r"""
plugin:
  description: Plugin name.
  returned: success
  type: str
  sample: build-pipeline-plugin
state:
  description: State of the target, after execution.
  returned: success
  type: str
  sample: "present"
"""

import hashlib
import json
import os
import tempfile
import time
from collections import OrderedDict
from http import cookiejar
from urllib.parse import urlencode

from ansible.module_utils.basic import AnsibleModule, to_bytes
from ansible.module_utils.urls import fetch_url, url_argument_spec, basic_auth_header
from ansible.module_utils.common.text.converters import to_native

from ansible_collections.community.general.plugins.module_utils.jenkins import download_updates_file


class FailedInstallingWithPluginManager(Exception):
    pass


class JenkinsPlugin:
    def __init__(self, module):
        # To be able to call fail_json
        self.module = module

        # Shortcuts for the params
        self.params = self.module.params
        self.url = self.params["url"]
        self.timeout = self.params["timeout"]

        # Authentication for non-Jenkins calls
        self.updates_url_credentials = {}
        if self.params.get("updates_url_username") and self.params.get("updates_url_password"):
            self.updates_url_credentials["Authorization"] = basic_auth_header(
                self.params["updates_url_username"], self.params["updates_url_password"]
            )

        # Crumb
        self.crumb = {}

        # Authentication for Jenkins calls
        if self.params.get("url_username") and self.params.get("url_password"):
            self.crumb["Authorization"] = basic_auth_header(self.params["url_username"], self.params["url_password"])

        # Cookie jar for crumb session
        self.cookies = None

        if self._csrf_enabled():
            self.cookies = cookiejar.LWPCookieJar()
            self._get_crumb()

        # Get list of installed plugins
        self._get_installed_plugins()

    def _csrf_enabled(self):
        csrf_data = self._get_json_data(f"{self.url}/api/json", "CSRF")

        if "useCrumbs" not in csrf_data:
            self.module.fail_json(msg="Required fields not found in the Crumbs response.", details=csrf_data)

        return csrf_data["useCrumbs"]

    def _get_json_data(self, url, what, **kwargs):
        # Get the JSON data
        r = self._get_url_data(url, what, **kwargs)

        # Parse the JSON data
        try:
            json_data = json.loads(to_native(r.read()))
        except Exception as e:
            self.module.fail_json(msg=f"Cannot parse {what} JSON data.", details=to_native(e))

        return json_data

    def _get_urls_data(self, urls, what=None, msg_status=None, msg_exception=None, **kwargs):
        # Compose default messages
        if msg_status is None:
            msg_status = f"Cannot get {what}"

        if msg_exception is None:
            msg_exception = f"Retrieval of {what} failed."

        errors = {}
        for url in urls:
            err_msg = None
            try:
                self.module.debug(f"fetching url: {url}")

                is_jenkins_call = url.startswith(self.url)
                self.module.params["force_basic_auth"] = is_jenkins_call

                response, info = fetch_url(
                    self.module,
                    url,
                    timeout=self.timeout,
                    cookies=self.cookies,
                    headers=self.crumb if is_jenkins_call else self.updates_url_credentials or self.crumb,
                    **kwargs,
                )
                if info["status"] == 200:
                    return response
                else:
                    err_msg = f"{msg_status}. fetching url {url} failed. response code: {info['status']}"
                    if info["status"] > 400:  # extend error message
                        err_msg = f"{err_msg}. response body: {info['body']}"
            except Exception as e:
                err_msg = f"{msg_status}. fetching url {url} failed. error msg: {e}"
            finally:
                if err_msg is not None:
                    self.module.debug(err_msg)
                    errors[url] = err_msg

        # failed on all urls
        self.module.fail_json(msg=msg_exception, details=errors)

    def _get_url_data(self, url, what=None, msg_status=None, msg_exception=None, dont_fail=False, **kwargs):
        # Compose default messages
        if msg_status is None:
            msg_status = f"Cannot get {what}"

        if msg_exception is None:
            msg_exception = f"Retrieval of {what} failed."

        # Get the URL data
        try:
            is_jenkins_call = url.startswith(self.url)
            self.module.params["force_basic_auth"] = is_jenkins_call

            response, info = fetch_url(
                self.module,
                url,
                timeout=self.timeout,
                cookies=self.cookies,
                headers=self.crumb if is_jenkins_call else self.updates_url_credentials or self.crumb,
                **kwargs,
            )

            if info["status"] != 200:
                if dont_fail:
                    raise FailedInstallingWithPluginManager(info["msg"])
                else:
                    self.module.fail_json(msg=msg_status, details=info["msg"])
        except Exception as e:
            if dont_fail:
                raise FailedInstallingWithPluginManager(e)
            else:
                self.module.fail_json(msg=msg_exception, details=to_native(e))

        return response

    def _get_crumb(self):
        crumb_data = self._get_json_data(f"{self.url}/crumbIssuer/api/json", "Crumb")

        if "crumbRequestField" in crumb_data and "crumb" in crumb_data:
            self.crumb[crumb_data["crumbRequestField"]] = crumb_data["crumb"]
        else:
            self.module.fail_json(msg="Required fields not found in the Crum response.", details=crumb_data)

    def _get_installed_plugins(self):
        plugins_data = self._get_json_data(f"{self.url}/pluginManager/api/json?depth=1", "list of plugins")

        # Check if we got valid data
        if "plugins" not in plugins_data:
            self.module.fail_json(msg="No valid plugin data found.")

        # Create final list of installed/pined plugins
        self.is_installed = False
        self.is_pinned = False
        self.is_enabled = False
        self.installed_plugins = plugins_data["plugins"]

        for p in plugins_data["plugins"]:
            if p["shortName"] == self.params["name"]:
                self.is_installed = True

                if p["pinned"]:
                    self.is_pinned = True

                if p["enabled"]:
                    self.is_enabled = True

                break

    def _install_dependencies(self):
        dependencies = self._get_versioned_dependencies()
        self.dependencies_states = []

        for dep_name, dep_version in dependencies.items():
            if not any(p["shortName"] == dep_name and p["version"] == dep_version for p in self.installed_plugins):
                dep_params = self.params.copy()
                dep_params["name"] = dep_name
                dep_params["version"] = dep_version
                dep_module = AnsibleModule(
                    argument_spec=self.module.argument_spec, supports_check_mode=self.module.check_mode
                )
                dep_module.params = dep_params
                dep_plugin = JenkinsPlugin(dep_module)
                if not dep_plugin.install():
                    self.dependencies_states.append({"name": dep_name, "version": dep_version, "state": "absent"})
                else:
                    self.dependencies_states.append({"name": dep_name, "version": dep_version, "state": "present"})
            else:
                self.dependencies_states.append({"name": dep_name, "version": dep_version, "state": "present"})

    def _install_with_plugin_manager(self):
        if not self.module.check_mode:
            # Install the plugin (with dependencies)
            install_script = (
                f"""d = Jenkins.instance.updateCenter.getPlugin("{self.params["name"]}").deploy(); d.get();"""
            )

            if self.params["with_dependencies"]:
                install_script = (
                    'Jenkins.instance.updateCenter.getPlugin("%s")'
                    ".getNeededDependencies().each{it.deploy()}; %s" % (self.params["name"], install_script)
                )

            script_data = {"script": install_script}
            data = urlencode(script_data)

            # Send the installation request
            self._get_url_data(
                f"{self.url}/scriptText",
                msg_status="Cannot install plugin.",
                msg_exception="Plugin installation has failed.",
                data=data,
                dont_fail=True,
            )

            hpi_file = f"{self.params['jenkins_home']}/plugins/{self.params['name']}.hpi"

            if os.path.isfile(hpi_file):
                os.remove(hpi_file)

    def install(self):
        changed = False
        plugin_file = f"{self.params['jenkins_home']}/plugins/{self.params['name']}.jpi"

        if not self.is_installed and self.params["version"] in [None, "latest"]:
            try:
                self._install_with_plugin_manager()
                changed = True
            except FailedInstallingWithPluginManager:  # Fallback to manually downloading the plugin
                pass

        if not changed:
            # Check if the plugin directory exists
            if not os.path.isdir(self.params["jenkins_home"]):
                self.module.fail_json(msg="Jenkins home directory doesn't exist.")

            checksum_old = None
            if os.path.isfile(plugin_file):
                # Make the checksum of the currently installed plugin
                with open(plugin_file, "rb") as plugin_fh:
                    plugin_content = plugin_fh.read()
                checksum_old = hashlib.sha1(plugin_content).hexdigest()

            # Install dependencies
            if self.params["with_dependencies"]:
                self._install_dependencies()

            if self.params["version"] in [None, "latest"]:
                # Take latest version
                plugin_urls = self._get_latest_plugin_urls()
            else:
                # Take specific version
                plugin_urls = self._get_versioned_plugin_urls()
            if (
                self.params["updates_expiration"] == 0
                or self.params["version"] not in [None, "latest"]
                or checksum_old is None
            ):
                # Download the plugin file directly
                r = self._download_plugin(plugin_urls)

                # Write downloaded plugin into file if checksums don't match
                if checksum_old is None:
                    # No previously installed plugin
                    if not self.module.check_mode:
                        self._write_file(plugin_file, r)

                    changed = True
                else:
                    # Get data for the MD5
                    data = r.read()

                    # Make new checksum
                    checksum_new = hashlib.sha1(data).hexdigest()

                    # If the checksum is different from the currently installed
                    # plugin, store the new plugin
                    if checksum_old != checksum_new:
                        if not self.module.check_mode:
                            self._write_file(plugin_file, data)

                        changed = True
            elif self.params["version"] == "latest":
                # Check for update from the updates JSON file
                plugin_data = self._download_updates()

                # If the latest version changed, download it
                if checksum_old != to_bytes(plugin_data["sha1"]):
                    if not self.module.check_mode:
                        r = self._download_plugin(plugin_urls)
                        self._write_file(plugin_file, r)

                    changed = True

        # Change file attributes if needed
        if os.path.isfile(plugin_file):
            params = {"dest": plugin_file}
            params.update(self.params)
            file_args = self.module.load_file_common_arguments(params)

            if not self.module.check_mode:
                # Not sure how to run this in the check mode
                changed = self.module.set_fs_attributes_if_different(file_args, changed)
            else:
                # See the comment above
                changed = True

        return changed

    def _get_latest_plugin_urls(self):
        urls = []
        for base_url in self.params["updates_url"]:
            for update_segment in self.params["latest_plugins_url_segments"]:
                urls.append(f"{base_url}/{update_segment}/{self.params['name']}.hpi")
        return urls

    def _get_latest_compatible_plugin_version(self, plugin_name=None):
        if not hasattr(self, "jenkins_version"):
            self.module.params["force_basic_auth"] = True
            resp, info = fetch_url(self.module, self.url)
            raw_version = info.get("x-jenkins")
            self.jenkins_version = self.parse_version(raw_version)
        name = plugin_name or self.params["name"]
        cache_path = f"{self.params['jenkins_home']}/ansible_jenkins_plugin_cache.json"
        plugin_version_urls = []
        for base_url in self.params["updates_url"]:
            for update_json in self.params["plugin_versions_url_segment"]:
                plugin_version_urls.append(f"{base_url}/{update_json}")

        try:  # Check if file is saved localy
            if os.path.exists(cache_path):
                file_mtime = os.path.getmtime(cache_path)
            else:
                file_mtime = 0

            now = time.time()
            if now - file_mtime >= 86400:
                response = self._get_urls_data(plugin_version_urls, what="plugin-versions.json")
                plugin_data = json.loads(to_native(response.read()), object_pairs_hook=OrderedDict)

                # Save it to file for next time
                with open(cache_path, "w") as f:
                    json.dump(plugin_data, f)

            with open(cache_path, "r") as f:
                plugin_data = json.load(f)

        except Exception as e:
            if os.path.exists(cache_path):
                os.remove(cache_path)
            self.module.fail_json(msg="Failed to parse plugin-versions.json", details=to_native(e))

        plugin_versions = plugin_data.get("plugins", {}).get(name)
        if not plugin_versions:
            self.module.fail_json(msg=f"Plugin '{name}' not found.")

        sorted_versions = list(reversed(plugin_versions.items()))

        for idx, (version_title, version_info) in enumerate(sorted_versions):
            required_core = version_info.get("requiredCore", "0.0")
            if self.parse_version(required_core) <= self.jenkins_version:
                return "latest" if idx == 0 else version_title

        self.module.warn(f"No compatible version found for plugin '{name}'. Installing latest version.")
        return "latest"

    def _get_versioned_plugin_urls(self):
        urls = []
        for base_url in self.params["updates_url"]:
            for versioned_segment in self.params["versioned_plugins_url_segments"]:
                urls.append(
                    f"{base_url}/{versioned_segment}/{self.params['name']}/{self.params['version']}/{self.params['name']}.hpi"
                )
        return urls

    def _get_update_center_urls(self):
        urls = []
        for base_url in self.params["updates_url"]:
            for update_json in self.params["update_json_url_segment"]:
                urls.append(f"{base_url}/{update_json}")
        return urls

    def _get_versioned_dependencies(self):
        # Get dependencies for the specified plugin version
        plugin_data = self._download_updates()["dependencies"]

        dependencies_info = {
            dep["name"]: self._get_latest_compatible_plugin_version(dep["name"])
            for dep in plugin_data
            if not dep.get("optional", False)
        }

        return dependencies_info

    def _download_updates(self):
        try:
            updates_file, download_updates = download_updates_file(self.params["updates_expiration"])
        except OSError as e:
            self.module.fail_json(msg="Cannot create temporal directory.", details=to_native(e))

        # Download the updates file if needed
        if download_updates:
            urls = self._get_update_center_urls()

            # Get the data
            r = self._get_urls_data(
                urls, msg_status="Remote updates not found.", msg_exception="Updates download failed."
            )

            # Write the updates file
            tmp_update_fd, tmp_updates_file = tempfile.mkstemp()
            os.write(tmp_update_fd, r.read())

            try:
                os.close(tmp_update_fd)
            except IOError as e:
                self.module.fail_json(
                    msg=f"Cannot close the tmp updates file {tmp_updates_file}.", details=to_native(e)
                )
        else:
            tmp_updates_file = updates_file

        # Open the updates file
        try:
            f = open(tmp_updates_file, encoding="utf-8")

            # Read only the second line
            dummy = f.readline()
            data = json.loads(f.readline())
        except IOError as e:
            self.module.fail_json(
                msg=f"Cannot open{' temporary' if tmp_updates_file != updates_file else ''} updates file.",
                details=to_native(e),
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Cannot load JSON data from the{' temporary' if tmp_updates_file != updates_file else ''} updates file.",
                details=to_native(e),
            )

        # Move the updates file to the right place if we could read it
        if tmp_updates_file != updates_file:
            self.module.atomic_move(os.path.abspath(tmp_updates_file), os.path.abspath(updates_file))

        # Check if we have the plugin data available
        if not data.get("plugins", {}).get(self.params["name"]):
            self.module.fail_json(msg="Cannot find plugin data in the updates file.")

        return data["plugins"][self.params["name"]]

    def _download_plugin(self, plugin_urls):
        # Download the plugin

        return self._get_urls_data(plugin_urls, msg_status="Plugin not found.", msg_exception="Plugin download failed.")

    def _write_file(self, f, data):
        # Store the plugin into a temp file and then move it
        tmp_f_fd, tmp_f = tempfile.mkstemp()

        if isinstance(data, (str, bytes)):
            os.write(tmp_f_fd, data)
        else:
            os.write(tmp_f_fd, data.read())

        try:
            os.close(tmp_f_fd)
        except IOError as e:
            self.module.fail_json(msg=f"Cannot close the temporal plugin file {tmp_f}.", details=to_native(e))

        # Move the file onto the right place
        self.module.atomic_move(os.path.abspath(tmp_f), os.path.abspath(f))

    def uninstall(self):
        changed = False

        # Perform the action
        if self.is_installed:
            if not self.module.check_mode:
                self._pm_query("doUninstall", "Uninstallation")

            changed = True

        return changed

    def pin(self):
        return self._pinning("pin")

    def unpin(self):
        return self._pinning("unpin")

    def _pinning(self, action):
        changed = False

        # Check if the plugin is pinned/unpinned
        if action == "pin" and not self.is_pinned or action == "unpin" and self.is_pinned:
            # Perform the action
            if not self.module.check_mode:
                self._pm_query(action, f"{action.capitalize()}ning")

            changed = True

        return changed

    def enable(self):
        return self._enabling("enable")

    def disable(self):
        return self._enabling("disable")

    def _enabling(self, action):
        changed = False

        # Check if the plugin is pinned/unpinned
        if action == "enable" and not self.is_enabled or action == "disable" and self.is_enabled:
            # Perform the action
            if not self.module.check_mode:
                self._pm_query(f"make{action.capitalize()}d", f"{action[:-1].capitalize()}ing")

            changed = True

        return changed

    def _pm_query(self, action, msg):
        url = f"{self.params['url']}/pluginManager/plugin/{self.params['name']}/{action}"

        # Send the request
        self._get_url_data(
            url, msg_status=f"Plugin not found. {url}", msg_exception=f"{msg} has failed.", method="POST"
        )

    @staticmethod
    def parse_version(version_str):
        return tuple(int(x) for x in version_str.split("."))


def main():
    # Module arguments
    argument_spec = url_argument_spec()
    argument_spec.update(
        group=dict(type="str", default="jenkins"),
        jenkins_home=dict(type="path", default="/var/lib/jenkins"),
        mode=dict(default="0644", type="raw"),
        name=dict(type="str", required=True),
        owner=dict(type="str", default="jenkins"),
        state=dict(
            choices=["present", "absent", "pinned", "unpinned", "enabled", "disabled", "latest"], default="present"
        ),
        timeout=dict(default=30, type="int"),
        updates_expiration=dict(default=86400, type="int"),
        updates_url=dict(
            type="list", elements="str", default=["https://updates.jenkins.io", "http://mirrors.jenkins.io"]
        ),
        updates_url_username=dict(type="str"),
        updates_url_password=dict(type="str", no_log=True),
        update_json_url_segment=dict(
            type="list", elements="str", default=["update-center.json", "updates/update-center.json"]
        ),
        plugin_versions_url_segment=dict(
            type="list", elements="str", default=["plugin-versions.json", "current/plugin-versions.json"]
        ),
        latest_plugins_url_segments=dict(type="list", elements="str", default=["latest"]),
        versioned_plugins_url_segments=dict(type="list", elements="str", default=["download/plugins", "plugins"]),
        url=dict(default="http://localhost:8080"),
        url_password=dict(no_log=True),
        version=dict(),
        with_dependencies=dict(default=True, type="bool"),
    )
    # Module settings
    module = AnsibleModule(
        argument_spec=argument_spec,
        add_file_common_args=True,
        supports_check_mode=True,
    )

    # Convert timeout to float
    try:
        module.params["timeout"] = float(module.params["timeout"])
    except ValueError as e:
        module.fail_json(msg=f"Cannot convert {module.params['timeout']} to float.", details=to_native(e))
    # Instantiate the JenkinsPlugin object
    jp = JenkinsPlugin(module)

    # Set version to latest if state is latest
    if module.params["state"] == "latest":
        module.params["state"] = "present"
        module.params["version"] = jp._get_latest_compatible_plugin_version()

    # Set version to latest compatible version if version is latest
    if module.params["version"] == "latest":
        module.params["version"] = jp._get_latest_compatible_plugin_version()

    # Create some shortcuts
    name = module.params["name"]
    state = module.params["state"]

    # Initial change state of the task
    changed = False

    # Perform action depending on the requested state
    if state == "present":
        changed = jp.install()
    elif state == "absent":
        changed = jp.uninstall()
    elif state == "pinned":
        changed = jp.pin()
    elif state == "unpinned":
        changed = jp.unpin()
    elif state == "enabled":
        changed = jp.enable()
    elif state == "disabled":
        changed = jp.disable()

    # Print status of the change
    module.exit_json(
        changed=changed,
        plugin=name,
        state=state,
        dependencies=jp.dependencies_states if hasattr(jp, "dependencies_states") else None,
    )


if __name__ == "__main__":
    main()
