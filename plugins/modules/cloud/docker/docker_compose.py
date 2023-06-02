#!/usr/bin/python
#
# Copyright 2016 Red Hat | Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''

module: docker_compose

short_description: Manage multi-container Docker applications with Docker Compose.


author: "Chris Houseknecht (@chouseknecht)"

description:
  - Uses Docker Compose to start, shutdown and scale services.
  - Works with compose versions 1 and 2.
  - Configuration can be read from a C(docker-compose.yml) or C(docker-compose.yaml) file or inline using the I(definition) option.
  - See the examples for more details.
  - Supports check mode.
  - This module was called C(docker_service) before Ansible 2.8. The usage did not change.

options:
  project_src:
    description:
      - Path to a directory containing a C(docker-compose.yml) or C(docker-compose.yaml) file.
      - Mutually exclusive with I(definition).
      - Required when no I(definition) is provided.
    type: path
  project_name:
    description:
      - Provide a project name. If not provided, the project name is taken from the basename of I(project_src).
      - Required when I(definition) is provided.
    type: str
  files:
    description:
      - List of Compose file names relative to I(project_src). Overrides C(docker-compose.yml) or C(docker-compose.yaml).
      - Files are loaded and merged in the order given.
    type: list
    elements: path
  state:
    description:
      - Desired state of the project.
      - Specifying C(present) is the same as running C(docker-compose up) resp. C(docker-compose stop) (with I(stopped)) resp. C(docker-compose restart)
        (with I(restarted)).
      - Specifying C(absent) is the same as running C(docker-compose down).
    type: str
    default: present
    choices:
      - absent
      - present
  services:
    description:
      - When I(state) is C(present) run C(docker-compose up) resp. C(docker-compose stop) (with I(stopped)) resp. C(docker-compose restart) (with I(restarted))
        on a subset of services.
      - If empty, which is the default, the operation will be performed on all services defined in the Compose file (or inline I(definition)).
    type: list
    elements: str
  scale:
    description:
      - When I(state) is C(present) scale services. Provide a dictionary of key/value pairs where the key
        is the name of the service and the value is an integer count for the number of containers.
    type: dict
  dependencies:
    description:
      - When I(state) is C(present) specify whether or not to include linked services.
    type: bool
    default: yes
  definition:
    description:
      - Compose file describing one or more services, networks and volumes.
      - Mutually exclusive with I(project_src) and I(files).
    type: dict
  hostname_check:
    description:
      - Whether or not to check the Docker daemon's hostname against the name provided in the client certificate.
    type: bool
    default: no
  recreate:
    description:
      - By default containers will be recreated when their configuration differs from the service definition.
      - Setting to C(never) ignores configuration differences and leaves existing containers unchanged.
      - Setting to C(always) forces recreation of all existing containers.
    type: str
    default: smart
    choices:
      - always
      - never
      - smart
  build:
    description:
      - Use with I(state) C(present) to always build images prior to starting the application.
      - Same as running C(docker-compose build) with the pull option.
      - Images will only be rebuilt if Docker detects a change in the Dockerfile or build directory contents.
      - Use the I(nocache) option to ignore the image cache when performing the build.
      - If an existing image is replaced, services using the image will be recreated unless I(recreate) is C(never).
    type: bool
    default: no
  pull:
    description:
      - Use with I(state) C(present) to always pull images prior to starting the application.
      - Same as running C(docker-compose pull).
      - When a new image is pulled, services using the image will be recreated unless I(recreate) is C(never).
    type: bool
    default: no
  nocache:
    description:
      - Use with the I(build) option to ignore the cache during the image build process.
    type: bool
    default: no
  remove_images:
    description:
      - Use with I(state) C(absent) to remove all images or only local images.
    type: str
    choices:
        - 'all'
        - 'local'
  remove_volumes:
    description:
      - Use with I(state) C(absent) to remove data volumes.
    type: bool
    default: no
  stopped:
    description:
      - Use with I(state) C(present) to stop all containers defined in the Compose file.
      - If I(services) is defined, only the containers listed there will be stopped.
    type: bool
    default: no
  restarted:
    description:
      - Use with I(state) C(present) to restart all containers defined in the Compose file.
      - If I(services) is defined, only the containers listed there will be restarted.
    type: bool
    default: no
  remove_orphans:
    description:
      - Remove containers for services not defined in the Compose file.
    type: bool
    default: no
  timeout:
    description:
        - timeout in seconds for container shutdown when attached or when containers are already running.
    type: int
    default: 10

extends_documentation_fragment:
- community.general.docker
- community.general.docker.docker_py_1_documentation


requirements:
  - "L(Docker SDK for Python,https://docker-py.readthedocs.io/en/stable/) >= 1.8.0 (use L(docker-py,https://pypi.org/project/docker-py/) for Python 2.6)"
  - "docker-compose >= 1.7.0"
  - "Docker API >= 1.20"
  - "PyYAML >= 3.11"
'''

EXAMPLES = '''
# Examples use the django example at https://docs.docker.com/compose/django. Follow it to create the
# flask directory

- name: Run using a project directory
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Tear down existing services
      community.general.docker_compose:
        project_src: flask
        state: absent

    - name: Create and start services
      community.general.docker_compose:
        project_src: flask
      register: output

    - ansible.builtin.debug:
        var: output

    - name: Run `docker-compose up` again
      community.general.docker_compose:
        project_src: flask
        build: no
      register: output

    - ansible.builtin.debug:
        var: output

    - ansible.builtin.assert:
        that: "not output.changed "

    - name: Stop all services
      community.general.docker_compose:
        project_src: flask
        build: no
        stopped: yes
      register: output

    - ansible.builtin.debug:
        var: output

    - ansible.builtin.assert:
        that:
          - "not web.flask_web_1.state.running"
          - "not db.flask_db_1.state.running"

    - name: Restart services
      community.general.docker_compose:
        project_src: flask
        build: no
        restarted: yes
      register: output

    - ansible.builtin.debug:
        var: output

    - ansible.builtin.assert:
        that:
          - "web.flask_web_1.state.running"
          - "db.flask_db_1.state.running"

- name: Scale the web service to 2
  hosts: localhost
  gather_facts: no
  tasks:
    - community.general.docker_compose:
        project_src: flask
        scale:
          web: 2
      register: output

    - ansible.builtin.debug:
        var: output

- name: Run with inline v2 compose
  hosts: localhost
  gather_facts: no
  tasks:
    - community.general.docker_compose:
        project_src: flask
        state: absent

    - community.general.docker_compose:
        project_name: flask
        definition:
          version: '2'
          services:
            db:
              image: postgres
            web:
              build: "{{ playbook_dir }}/flask"
              command: "python manage.py runserver 0.0.0.0:8000"
              volumes:
                - "{{ playbook_dir }}/flask:/code"
              ports:
                - "8000:8000"
              depends_on:
                - db
      register: output

    - ansible.builtin.debug:
        var: output

    - ansible.builtin.assert:
        that:
          - "web.flask_web_1.state.running"
          - "db.flask_db_1.state.running"

- name: Run with inline v1 compose
  hosts: localhost
  gather_facts: no
  tasks:
    - community.general.docker_compose:
        project_src: flask
        state: absent

    - community.general.docker_compose:
        project_name: flask
        definition:
            db:
              image: postgres
            web:
              build: "{{ playbook_dir }}/flask"
              command: "python manage.py runserver 0.0.0.0:8000"
              volumes:
                - "{{ playbook_dir }}/flask:/code"
              ports:
                - "8000:8000"
              links:
                - db
      register: output

    - ansible.builtin.debug:
        var: output

    - ansible.builtin.assert:
        that:
          - "web.flask_web_1.state.running"
          - "db.flask_db_1.state.running"
'''

RETURN = '''
services:
  description:
  - A dictionary mapping the service's name to a dictionary of containers.
  - Note that facts are part of the registered vars since Ansible 2.8. For compatibility reasons, the facts
    are also accessible directly. The service's name is the variable with which the container dictionary
    can be accessed. Note that the returned facts will be removed in community.general 2.0.0.
  returned: success
  type: complex
  contains:
      container_name:
          description: Name of the container. Format is C(project_service_#).
          returned: success
          type: complex
          contains:
              cmd:
                  description: One or more commands to be executed in the container.
                  returned: success
                  type: list
                  elements: str
                  example: ["postgres"]
              image:
                  description: Name of the image from which the container was built.
                  returned: success
                  type: str
                  example: postgres
              labels:
                  description: Meta data assigned to the container.
                  returned: success
                  type: dict
                  example: {...}
              networks:
                  description: Contains a dictionary for each network to which the container is a member.
                  returned: success
                  type: list
                  elements: dict
                  contains:
                      IPAddress:
                          description: The IP address assigned to the container.
                          returned: success
                          type: str
                          example: 172.17.0.2
                      IPPrefixLen:
                          description: Number of bits used by the subnet.
                          returned: success
                          type: int
                          example: 16
                      aliases:
                          description: Aliases assigned to the container by the network.
                          returned: success
                          type: list
                          elements: str
                          example: ['db']
                      globalIPv6:
                          description: IPv6 address assigned to the container.
                          returned: success
                          type: str
                          example: ''
                      globalIPv6PrefixLen:
                          description: IPv6 subnet length.
                          returned: success
                          type: int
                          example: 0
                      links:
                          description: List of container names to which this container is linked.
                          returned: success
                          type: list
                          elements: str
                          example: null
                      macAddress:
                          description: Mac Address assigned to the virtual NIC.
                          returned: success
                          type: str
                          example: "02:42:ac:11:00:02"
              state:
                  description: Information regarding the current disposition of the container.
                  returned: success
                  type: dict
                  contains:
                      running:
                          description: Whether or not the container is up with a running process.
                          returned: success
                          type: bool
                          example: true
                      status:
                          description: Description of the running state.
                          returned: success
                          type: str
                          example: running

actions:
  description: Provides the actions to be taken on each service as determined by compose.
  returned: when in check mode or I(debug) is C(yes)
  type: complex
  contains:
      service_name:
          description: Name of the service.
          returned: always
          type: complex
          contains:
              pulled_image:
                  description: Provides image details when a new image is pulled for the service.
                  returned: on image pull
                  type: complex
                  contains:
                      name:
                          description: name of the image
                          returned: always
                          type: str
                      id:
                          description: image hash
                          returned: always
                          type: str
              built_image:
                  description: Provides image details when a new image is built for the service.
                  returned: on image build
                  type: complex
                  contains:
                      name:
                          description: name of the image
                          returned: always
                          type: str
                      id:
                          description: image hash
                          returned: always
                          type: str

              action:
                  description: A descriptive name of the action to be performed on the service's containers.
                  returned: always
                  type: list
                  elements: str
                  contains:
                      id:
                          description: the container's long ID
                          returned: always
                          type: str
                      name:
                          description: the container's name
                          returned: always
                          type: str
                      short_id:
                          description: the container's short ID
                          returned: always
                          type: str
'''

import os
import re
import sys
import tempfile
import traceback
from contextlib import contextmanager
from distutils.version import LooseVersion

try:
    import yaml
    HAS_YAML = True
    HAS_YAML_EXC = None
except ImportError as dummy:
    HAS_YAML = False
    HAS_YAML_EXC = traceback.format_exc()

try:
    from docker.errors import DockerException
except ImportError:
    # missing Docker SDK for Python handled in ansible.module_utils.docker.common
    pass

try:
    from compose import __version__ as compose_version
    from compose.cli.command import project_from_options
    from compose.service import NoSuchImageError
    from compose.cli.main import convergence_strategy_from_opts, build_action_from_opts, image_type_from_opt
    from compose.const import DEFAULT_TIMEOUT, LABEL_SERVICE, LABEL_PROJECT, LABEL_ONE_OFF
    HAS_COMPOSE = True
    HAS_COMPOSE_EXC = None
    MINIMUM_COMPOSE_VERSION = '1.7.0'
except ImportError as dummy:
    HAS_COMPOSE = False
    HAS_COMPOSE_EXC = traceback.format_exc()
    DEFAULT_TIMEOUT = 10

from ansible_collections.community.general.plugins.module_utils.docker.common import (
    AnsibleDockerClient,
    DockerBaseClass,
    RequestException,
)


AUTH_PARAM_MAPPING = {
    u'docker_host': u'--host',
    u'tls': u'--tls',
    u'cacert_path': u'--tlscacert',
    u'cert_path': u'--tlscert',
    u'key_path': u'--tlskey',
    u'tls_verify': u'--tlsverify'
}


@contextmanager
def stdout_redirector(path_name):
    old_stdout = sys.stdout
    fd = open(path_name, 'w')
    sys.stdout = fd
    try:
        yield
    finally:
        sys.stdout = old_stdout


@contextmanager
def stderr_redirector(path_name):
    old_fh = sys.stderr
    fd = open(path_name, 'w')
    sys.stderr = fd
    try:
        yield
    finally:
        sys.stderr = old_fh


def make_redirection_tempfiles():
    dummy, out_redir_name = tempfile.mkstemp(prefix="ansible")
    dummy, err_redir_name = tempfile.mkstemp(prefix="ansible")
    return (out_redir_name, err_redir_name)


def cleanup_redirection_tempfiles(out_name, err_name):
    for i in [out_name, err_name]:
        os.remove(i)


def get_redirected_output(path_name):
    output = []
    with open(path_name, 'r') as fd:
        for line in fd:
            # strip terminal format/color chars
            new_line = re.sub(r'\x1b\[.+m', '', line)
            output.append(new_line)
    os.remove(path_name)
    return output


def attempt_extract_errors(exc_str, stdout, stderr):
    errors = [l.strip() for l in stderr if l.strip().startswith('ERROR:')]
    errors.extend([l.strip() for l in stdout if l.strip().startswith('ERROR:')])

    warnings = [l.strip() for l in stderr if l.strip().startswith('WARNING:')]
    warnings.extend([l.strip() for l in stdout if l.strip().startswith('WARNING:')])

    # assume either the exception body (if present) or the last warning was the 'most'
    # fatal.

    if exc_str.strip():
        msg = exc_str.strip()
    elif errors:
        msg = errors[-1].encode('utf-8')
    else:
        msg = 'unknown cause'

    return {
        'warnings': [w.encode('utf-8') for w in warnings],
        'errors': [e.encode('utf-8') for e in errors],
        'msg': msg,
        'module_stderr': ''.join(stderr),
        'module_stdout': ''.join(stdout)
    }


def get_failure_info(exc, out_name, err_name=None, msg_format='%s'):
    if err_name is None:
        stderr = []
    else:
        stderr = get_redirected_output(err_name)
    stdout = get_redirected_output(out_name)

    reason = attempt_extract_errors(str(exc), stdout, stderr)
    reason['msg'] = msg_format % reason['msg']
    return reason


class ContainerManager(DockerBaseClass):

    def __init__(self, client):

        super(ContainerManager, self).__init__()

        self.client = client
        self.project_src = None
        self.files = None
        self.project_name = None
        self.state = None
        self.definition = None
        self.hostname_check = None
        self.timeout = None
        self.remove_images = None
        self.remove_orphans = None
        self.remove_volumes = None
        self.stopped = None
        self.restarted = None
        self.recreate = None
        self.build = None
        self.dependencies = None
        self.services = None
        self.scale = None
        self.debug = None
        self.pull = None
        self.nocache = None

        for key, value in client.module.params.items():
            setattr(self, key, value)

        self.check_mode = client.check_mode

        if not self.debug:
            self.debug = client.module._debug

        self.options = dict()
        self.options.update(self._get_auth_options())
        self.options[u'--skip-hostname-check'] = (not self.hostname_check)

        if self.project_name:
            self.options[u'--project-name'] = self.project_name

        if self.files:
            self.options[u'--file'] = self.files

        if not HAS_COMPOSE:
            self.client.fail("Unable to load docker-compose. Try `pip install docker-compose`. Error: %s" %
                             HAS_COMPOSE_EXC)

        if LooseVersion(compose_version) < LooseVersion(MINIMUM_COMPOSE_VERSION):
            self.client.fail("Found docker-compose version %s. Minimum required version is %s. "
                             "Upgrade docker-compose to a min version of %s." %
                             (compose_version, MINIMUM_COMPOSE_VERSION, MINIMUM_COMPOSE_VERSION))

        if self.restarted and self.stopped:
            self.client.fail("Cannot use restarted and stopped at the same time.")

        self.log("options: ")
        self.log(self.options, pretty_print=True)

        if self.definition:
            if not HAS_YAML:
                self.client.fail("Unable to load yaml. Try `pip install PyYAML`. Error: %s" % HAS_YAML_EXC)

            if not self.project_name:
                self.client.fail("Parameter error - project_name required when providing definition.")

            self.project_src = tempfile.mkdtemp(prefix="ansible")
            compose_file = os.path.join(self.project_src, "docker-compose.yml")
            try:
                self.log('writing: ')
                self.log(yaml.dump(self.definition, default_flow_style=False))
                with open(compose_file, 'w') as f:
                    f.write(yaml.dump(self.definition, default_flow_style=False))
            except Exception as exc:
                self.client.fail("Error writing to %s - %s" % (compose_file, str(exc)))
        else:
            if not self.project_src:
                self.client.fail("Parameter error - project_src required.")

        try:
            self.log("project_src: %s" % self.project_src)
            self.project = project_from_options(self.project_src, self.options)
        except Exception as exc:
            self.client.fail("Configuration error - %s" % str(exc))

    def exec_module(self):
        result = dict()

        if self.state == 'present':
            result = self.cmd_up()
        elif self.state == 'absent':
            result = self.cmd_down()

        if self.definition:
            compose_file = os.path.join(self.project_src, "docker-compose.yml")
            self.log("removing %s" % compose_file)
            os.remove(compose_file)
            self.log("removing %s" % self.project_src)
            os.rmdir(self.project_src)

        if not self.check_mode and not self.debug and result.get('actions'):
            result.pop('actions')

        return result

    def _get_auth_options(self):
        options = dict()
        for key, value in self.client.auth_params.items():
            if value is not None:
                option = AUTH_PARAM_MAPPING.get(key)
                if option:
                    options[option] = value
        return options

    def cmd_up(self):

        start_deps = self.dependencies
        service_names = self.services
        detached = True
        result = dict(changed=False, actions=[], ansible_facts=dict(), services=dict())

        up_options = {
            u'--no-recreate': False,
            u'--build': False,
            u'--no-build': False,
            u'--no-deps': False,
            u'--force-recreate': False,
        }

        if self.recreate == 'never':
            up_options[u'--no-recreate'] = True
        elif self.recreate == 'always':
            up_options[u'--force-recreate'] = True

        if self.remove_orphans:
            up_options[u'--remove-orphans'] = True

        converge = convergence_strategy_from_opts(up_options)
        self.log("convergence strategy: %s" % converge)

        if self.pull:
            pull_output = self.cmd_pull()
            result['changed'] = pull_output['changed']
            result['actions'] += pull_output['actions']

        if self.build:
            build_output = self.cmd_build()
            result['changed'] = build_output['changed']
            result['actions'] += build_output['actions']

        if self.remove_orphans:
            containers = self.client.containers(
                filters={
                    'label': [
                        '{0}={1}'.format(LABEL_PROJECT, self.project.name),
                        '{0}={1}'.format(LABEL_ONE_OFF, "False")
                    ],
                }
            )

            orphans = []
            for container in containers:
                service_name = container.get('Labels', {}).get(LABEL_SERVICE)
                if service_name not in self.project.service_names:
                    orphans.append(service_name)

            if orphans:
                result['changed'] = True

        for service in self.project.services:
            if not service_names or service.name in service_names:
                plan = service.convergence_plan(strategy=converge)
                if plan.action != 'noop':
                    result['changed'] = True
                    result_action = dict(service=service.name)
                    result_action[plan.action] = []
                    for container in plan.containers:
                        result_action[plan.action].append(dict(
                            id=container.id,
                            name=container.name,
                            short_id=container.short_id,
                        ))
                    result['actions'].append(result_action)

        if not self.check_mode and result['changed'] and not self.stopped:
            out_redir_name, err_redir_name = make_redirection_tempfiles()
            try:
                with stdout_redirector(out_redir_name):
                    with stderr_redirector(err_redir_name):
                        do_build = build_action_from_opts(up_options)
                        self.log('Setting do_build to %s' % do_build)
                        self.project.up(
                            service_names=service_names,
                            start_deps=start_deps,
                            strategy=converge,
                            do_build=do_build,
                            detached=detached,
                            remove_orphans=self.remove_orphans,
                            timeout=self.timeout)
            except Exception as exc:
                fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                               msg_format="Error starting project %s")
                self.client.fail(**fail_reason)
            else:
                cleanup_redirection_tempfiles(out_redir_name, err_redir_name)

        if self.stopped:
            stop_output = self.cmd_stop(service_names)
            result['changed'] = stop_output['changed']
            result['actions'] += stop_output['actions']

        if self.restarted:
            restart_output = self.cmd_restart(service_names)
            result['changed'] = restart_output['changed']
            result['actions'] += restart_output['actions']

        if self.scale:
            scale_output = self.cmd_scale()
            result['changed'] = scale_output['changed']
            result['actions'] += scale_output['actions']

        for service in self.project.services:
            service_facts = dict()
            result['ansible_facts'][service.name] = service_facts
            result['services'][service.name] = service_facts
            for container in service.containers(stopped=True):
                inspection = container.inspect()
                # pare down the inspection data to the most useful bits
                facts = dict(
                    cmd=[],
                    labels=dict(),
                    image=None,
                    state=dict(
                        running=None,
                        status=None
                    ),
                    networks=dict()
                )
                if inspection['Config'].get('Cmd', None) is not None:
                    facts['cmd'] = inspection['Config']['Cmd']
                if inspection['Config'].get('Labels', None) is not None:
                    facts['labels'] = inspection['Config']['Labels']
                if inspection['Config'].get('Image', None) is not None:
                    facts['image'] = inspection['Config']['Image']
                if inspection['State'].get('Running', None) is not None:
                    facts['state']['running'] = inspection['State']['Running']
                if inspection['State'].get('Status', None) is not None:
                    facts['state']['status'] = inspection['State']['Status']

                if inspection.get('NetworkSettings') and inspection['NetworkSettings'].get('Networks'):
                    networks = inspection['NetworkSettings']['Networks']
                    for key in networks:
                        facts['networks'][key] = dict(
                            aliases=[],
                            globalIPv6=None,
                            globalIPv6PrefixLen=0,
                            IPAddress=None,
                            IPPrefixLen=0,
                            links=None,
                            macAddress=None,
                        )
                        if networks[key].get('Aliases', None) is not None:
                            facts['networks'][key]['aliases'] = networks[key]['Aliases']
                        if networks[key].get('GlobalIPv6Address', None) is not None:
                            facts['networks'][key]['globalIPv6'] = networks[key]['GlobalIPv6Address']
                        if networks[key].get('GlobalIPv6PrefixLen', None) is not None:
                            facts['networks'][key]['globalIPv6PrefixLen'] = networks[key]['GlobalIPv6PrefixLen']
                        if networks[key].get('IPAddress', None) is not None:
                            facts['networks'][key]['IPAddress'] = networks[key]['IPAddress']
                        if networks[key].get('IPPrefixLen', None) is not None:
                            facts['networks'][key]['IPPrefixLen'] = networks[key]['IPPrefixLen']
                        if networks[key].get('Links', None) is not None:
                            facts['networks'][key]['links'] = networks[key]['Links']
                        if networks[key].get('MacAddress', None) is not None:
                            facts['networks'][key]['macAddress'] = networks[key]['MacAddress']

                service_facts[container.name] = facts

        return result

    def cmd_pull(self):
        result = dict(
            changed=False,
            actions=[],
        )

        if not self.check_mode:
            for service in self.project.get_services(self.services, include_deps=False):
                if 'image' not in service.options:
                    continue

                self.log('Pulling image for service %s' % service.name)
                # store the existing image ID
                old_image_id = ''
                try:
                    image = service.image()
                    if image and image.get('Id'):
                        old_image_id = image['Id']
                except NoSuchImageError:
                    pass
                except Exception as exc:
                    self.client.fail("Error: service image lookup failed - %s" % str(exc))

                out_redir_name, err_redir_name = make_redirection_tempfiles()
                # pull the image
                try:
                    with stdout_redirector(out_redir_name):
                        with stderr_redirector(err_redir_name):
                            service.pull(ignore_pull_failures=False)
                except Exception as exc:
                    fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                                   msg_format="Error: pull failed with %s")
                    self.client.fail(**fail_reason)
                else:
                    cleanup_redirection_tempfiles(out_redir_name, err_redir_name)

                # store the new image ID
                new_image_id = ''
                try:
                    image = service.image()
                    if image and image.get('Id'):
                        new_image_id = image['Id']
                except NoSuchImageError as exc:
                    self.client.fail("Error: service image lookup failed after pull - %s" % str(exc))

                if new_image_id != old_image_id:
                    # if a new image was pulled
                    result['changed'] = True
                    result['actions'].append(dict(
                        service=service.name,
                        pulled_image=dict(
                            name=service.image_name,
                            id=new_image_id
                        )
                    ))
        return result

    def cmd_build(self):
        result = dict(
            changed=False,
            actions=[]
        )
        if not self.check_mode:
            for service in self.project.get_services(self.services, include_deps=False):
                if service.can_be_built():
                    self.log('Building image for service %s' % service.name)
                    # store the existing image ID
                    old_image_id = ''
                    try:
                        image = service.image()
                        if image and image.get('Id'):
                            old_image_id = image['Id']
                    except NoSuchImageError:
                        pass
                    except Exception as exc:
                        self.client.fail("Error: service image lookup failed - %s" % str(exc))

                    out_redir_name, err_redir_name = make_redirection_tempfiles()
                    # build the image
                    try:
                        with stdout_redirector(out_redir_name):
                            with stderr_redirector(err_redir_name):
                                new_image_id = service.build(pull=self.pull, no_cache=self.nocache)
                    except Exception as exc:
                        fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                                       msg_format="Error: build failed with %s")
                        self.client.fail(**fail_reason)
                    else:
                        cleanup_redirection_tempfiles(out_redir_name, err_redir_name)

                    if new_image_id not in old_image_id:
                        # if a new image was built
                        result['changed'] = True
                        result['actions'].append(dict(
                            service=service.name,
                            built_image=dict(
                                name=service.image_name,
                                id=new_image_id
                            )
                        ))
        return result

    def cmd_down(self):
        result = dict(
            changed=False,
            actions=[]
        )
        for service in self.project.services:
            containers = service.containers(stopped=True)
            if len(containers):
                result['changed'] = True
            result['actions'].append(dict(
                service=service.name,
                deleted=[container.name for container in containers]
            ))
        if not self.check_mode and result['changed']:
            image_type = image_type_from_opt('--rmi', self.remove_images)
            out_redir_name, err_redir_name = make_redirection_tempfiles()
            try:
                with stdout_redirector(out_redir_name):
                    with stderr_redirector(err_redir_name):
                        self.project.down(image_type, self.remove_volumes, self.remove_orphans)
            except Exception as exc:
                fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                               msg_format="Error stopping project - %s")
                self.client.fail(**fail_reason)
            else:
                cleanup_redirection_tempfiles(out_redir_name, err_redir_name)
        return result

    def cmd_stop(self, service_names):
        result = dict(
            changed=False,
            actions=[]
        )
        for service in self.project.services:
            if not service_names or service.name in service_names:
                service_res = dict(
                    service=service.name,
                    stop=[]
                )
                for container in service.containers(stopped=False):
                    result['changed'] = True
                    service_res['stop'].append(dict(
                        id=container.id,
                        name=container.name,
                        short_id=container.short_id
                    ))
                result['actions'].append(service_res)
        if not self.check_mode and result['changed']:
            out_redir_name, err_redir_name = make_redirection_tempfiles()
            try:
                with stdout_redirector(out_redir_name):
                    with stderr_redirector(err_redir_name):
                        self.project.stop(service_names=service_names, timeout=self.timeout)
            except Exception as exc:
                fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                               msg_format="Error stopping project %s")
                self.client.fail(**fail_reason)
            else:
                cleanup_redirection_tempfiles(out_redir_name, err_redir_name)
        return result

    def cmd_restart(self, service_names):
        result = dict(
            changed=False,
            actions=[]
        )

        for service in self.project.services:
            if not service_names or service.name in service_names:
                service_res = dict(
                    service=service.name,
                    restart=[]
                )
                for container in service.containers(stopped=True):
                    result['changed'] = True
                    service_res['restart'].append(dict(
                        id=container.id,
                        name=container.name,
                        short_id=container.short_id
                    ))
                result['actions'].append(service_res)

        if not self.check_mode and result['changed']:
            out_redir_name, err_redir_name = make_redirection_tempfiles()
            try:
                with stdout_redirector(out_redir_name):
                    with stderr_redirector(err_redir_name):
                        self.project.restart(service_names=service_names, timeout=self.timeout)
            except Exception as exc:
                fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                               msg_format="Error restarting project %s")
                self.client.fail(**fail_reason)
            else:
                cleanup_redirection_tempfiles(out_redir_name, err_redir_name)
        return result

    def cmd_scale(self):
        result = dict(
            changed=False,
            actions=[]
        )
        for service in self.project.services:
            if service.name in self.scale:
                service_res = dict(
                    service=service.name,
                    scale=0
                )
                containers = service.containers(stopped=True)
                scale = self.parse_scale(service.name)
                if len(containers) != scale:
                    result['changed'] = True
                    service_res['scale'] = scale - len(containers)
                    if not self.check_mode:
                        out_redir_name, err_redir_name = make_redirection_tempfiles()
                        try:
                            with stdout_redirector(out_redir_name):
                                with stderr_redirector(err_redir_name):
                                    service.scale(scale)
                        except Exception as exc:
                            fail_reason = get_failure_info(exc, out_redir_name, err_redir_name,
                                                           msg_format="Error scaling {0} - %s".format(service.name))
                            self.client.fail(**fail_reason)
                        else:
                            cleanup_redirection_tempfiles(out_redir_name, err_redir_name)
                    result['actions'].append(service_res)
        return result

    def parse_scale(self, service_name):
        try:
            return int(self.scale[service_name])
        except ValueError:
            self.client.fail("Error scaling %s - expected int, got %s",
                             service_name, str(type(self.scale[service_name])))


def main():
    argument_spec = dict(
        project_src=dict(type='path'),
        project_name=dict(type='str',),
        files=dict(type='list', elements='path'),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        definition=dict(type='dict'),
        hostname_check=dict(type='bool', default=False),
        recreate=dict(type='str', default='smart', choices=['always', 'never', 'smart']),
        build=dict(type='bool', default=False),
        remove_images=dict(type='str', choices=['all', 'local']),
        remove_volumes=dict(type='bool', default=False),
        remove_orphans=dict(type='bool', default=False),
        stopped=dict(type='bool', default=False),
        restarted=dict(type='bool', default=False),
        scale=dict(type='dict'),
        services=dict(type='list', elements='str'),
        dependencies=dict(type='bool', default=True),
        pull=dict(type='bool', default=False),
        nocache=dict(type='bool', default=False),
        debug=dict(type='bool', default=False),
        timeout=dict(type='int', default=DEFAULT_TIMEOUT)
    )

    mutually_exclusive = [
        ('definition', 'project_src'),
        ('definition', 'files')
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )
    if client.module._name in ('docker_service', 'community.general.docker_service'):
        client.module.deprecate("The 'docker_service' module has been renamed to 'docker_compose'.",
                                version='2.0.0', collection_name='community.general')  # was Ansible 2.12

    try:
        result = ContainerManager(client).exec_module()
        client.module.exit_json(**result)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())


if __name__ == '__main__':
    main()
