<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

Setup Docker
============

This role provides a mechanism to install docker automatically within the context of an integration test.

For the time being (Apr 2023) it has been tested in Fedora 37 and Ubuntu Jammy.

This role was largely based on the `setup_snap` one written by @felixfontein.


Quickstart
----------

Add the file `meta/main.yml` to your integration test target it it does not yet contain one, and add (or update) the `dependencies` block with `setup_docker`, as in:

```yaml
dependencies:
  - setup_docker
```

In your integration test target, add to the beginning of the `tasks/main.yml` something like (example from `mssql_script`):

```yaml
- name: Start container
  community.docker.docker_container:
    name: mssql-test
    image: "mcr.microsoft.com/mssql/server:2019-latest"
    env:
      ACCEPT_EULA: "Y"
      SA_PASSWORD: "{{ mssql_login_password }}"
      MSSQL_PID: Developer
    ports:
      - "{{ mssql_port }}:1433"
    detach: true
    auto_remove: true
    memory: 2200M
```

That's it! Your integration test will be using a docker container to support the test.


What it does
------------

The role will install `docker` on the test target, allowing the test to run a container to support its execution.

The installation of the package sends a notification to an Ansible handler that will remove `docker` from the system after the integration test target is done.

This role assumes that developers will use the collection `community.docker` to manage the containers used in the test. To support that assumption, this role will install the `requests` package in the Python runtime environment used, usually a *virtualenv* used for the test. That package is **not removed** from that environment after the test.

The most common use case is to use `community.docker.docker_container` to start a container, as in the example above. It is likely that `community.docker.docker_compose` can be used as well, although this has **not been tested** yet.


Recommendations
---------------

* Don't forget to publish the service ports when starting the container
* Take into consideration that the services inside the container will take a while to get started. Use both/either `ansible.builtin.wait_for` to check for the availability of the network port and/or `retries` on the first task effectively using those services
* As a precautionary measure, start using the role in a test that is marked either `disabled` or `unsupported`, and move forward from there.


Known Issues & Caveats
----------------------

* Support only Ubuntu and Fedora, having been tested in Ubuntu Jammy and Fedora 37, respectively
* Lack mechanism to choose or constraint the `docker` version to be used
* Lack option to prevent `docker` from being removed at the end of the integration test
