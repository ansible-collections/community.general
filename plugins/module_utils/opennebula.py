#
# Copyright 2018 www.privaz.io Valletech AB
#
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import annotations


import time
import ssl
from os import environ
from ansible.module_utils.basic import AnsibleModule


IMAGE_STATES = [
    "INIT",
    "READY",
    "USED",
    "DISABLED",
    "LOCKED",
    "ERROR",
    "CLONE",
    "DELETE",
    "USED_PERS",
    "LOCKED_USED",
    "LOCKED_USED_PERS",
]
HAS_PYONE = True

try:
    from pyone import OneException
    from pyone.server import OneServer
except ImportError:
    OneException = Exception
    HAS_PYONE = False


# A helper function to mitigate https://github.com/OpenNebula/one/issues/6064.
# It allows for easily handling lists like "NIC" or "DISK" in the JSON-like template representation.
# There are either lists of dictionaries (length > 1) or just dictionaries.
def flatten(to_flatten, extract=False):
    """Flattens nested lists (with optional value extraction)."""

    def recurse(to_flatten):
        return sum(map(recurse, to_flatten), []) if isinstance(to_flatten, list) else [to_flatten]

    value = recurse(to_flatten)
    if extract and len(value) == 1:
        return value[0]
    return value


# A helper function to mitigate https://github.com/OpenNebula/one/issues/6064.
# It renders JSON-like template representation into OpenNebula's template syntax (string).
def render(to_render):
    """Converts dictionary to OpenNebula template."""

    def recurse(to_render):
        for key, value in sorted(to_render.items()):
            if value is None:
                continue
            if isinstance(value, dict):
                yield f"{key}=[{','.join(recurse(value))}]"
                continue
            if isinstance(value, list):
                for item in value:
                    yield f"{key}=[{','.join(recurse(item))}]"
                continue
            if isinstance(value, str):
                _value = value.replace("\\", "\\\\").replace('"', '\\"')
                yield f'{key}="{_value}"'
                continue
            yield f'{key}="{value}"'

    return "\n".join(recurse(to_render))


class OpenNebulaModule:
    """
    Base class for all OpenNebula Ansible Modules.
    This is basically a wrapper of the common arguments, the pyone client and
    some utility methods.
    """

    common_args = dict(
        api_url=dict(type="str", aliases=["api_endpoint"], default=environ.get("ONE_URL")),
        api_username=dict(type="str", default=environ.get("ONE_USERNAME")),
        api_password=dict(type="str", no_log=True, aliases=["api_token"], default=environ.get("ONE_PASSWORD")),
        validate_certs=dict(default=True, type="bool"),
        wait_timeout=dict(type="int", default=300),
    )

    def __init__(
        self, argument_spec, supports_check_mode=False, mutually_exclusive=None, required_one_of=None, required_if=None
    ):
        module_args = OpenNebulaModule.common_args.copy()
        module_args.update(argument_spec)

        self.module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=supports_check_mode,
            mutually_exclusive=mutually_exclusive,
            required_one_of=required_one_of,
            required_if=required_if,
        )
        self.result = dict(changed=False, original_message="", message="")
        self.one = self.create_one_client()

        self.resolved_parameters = self.resolve_parameters()

    def create_one_client(self):
        """
        Creates an XMLPRC client to OpenNebula.

        Returns: the new xmlrpc client.

        """

        # context required for not validating SSL, old python versions won't validate anyway.
        if hasattr(ssl, "_create_unverified_context"):
            no_ssl_validation_context = ssl._create_unverified_context()
        else:
            no_ssl_validation_context = None

        # Check if the module can run
        if not HAS_PYONE:
            self.fail("pyone is required for this module")

        if self.module.params.get("api_url"):
            url = self.module.params.get("api_url")
        else:
            self.fail("Either api_url or the environment variable ONE_URL must be provided")

        if self.module.params.get("api_username"):
            username = self.module.params.get("api_username")
        else:
            self.fail("Either api_username or the environment variable ONE_USERNAME must be provided")

        if self.module.params.get("api_password"):
            password = self.module.params.get("api_password")
        else:
            self.fail("Either api_password or the environment variable ONE_PASSWORD must be provided")

        session = f"{username}:{password}"

        if not self.module.params.get("validate_certs") and "PYTHONHTTPSVERIFY" not in environ:
            return OneServer(url, session=session, context=no_ssl_validation_context)
        else:
            return OneServer(url, session)

    def close_one_client(self):
        """
        Close the pyone session.
        """
        self.one.server_close()

    def fail(self, msg):
        """
        Utility failure method, will ensure pyone is properly closed before failing.
        Args:
            msg: human readable failure reason.
        """
        if hasattr(self, "one"):
            self.close_one_client()
        self.module.fail_json(msg=msg)

    def exit(self):
        """
        Utility exit method, will ensure pyone is properly closed before exiting.

        """
        if hasattr(self, "one"):
            self.close_one_client()
        self.module.exit_json(**self.result)

    def resolve_parameters(self):
        """
        This method resolves parameters provided by a secondary ID to the primary ID.
        For example if cluster_name is present, cluster_id will be introduced by performing
        the required resolution

        Returns: a copy of the parameters that includes the resolved parameters.

        """

        resolved_params = dict(self.module.params)

        if "cluster_name" in self.module.params:
            clusters = self.one.clusterpool.info()
            for cluster in clusters.CLUSTER:
                if self.module.params.get("cluster_name") == cluster.NAME:
                    resolved_params["cluster_id"] = cluster.ID

        return resolved_params

    def is_parameter(self, name):
        """
        Utility method to check if a parameter was provided or is resolved
        Args:
            name: the parameter to check
        """
        if name in self.resolved_parameters:
            return self.get_parameter(name) is not None
        else:
            return False

    def get_parameter(self, name):
        """
        Utility method for accessing parameters that includes resolved ID
        parameters from provided Name parameters.
        """
        return self.resolved_parameters.get(name)

    def get_host_by_name(self, name):
        """
        Returns a host given its name.
        Args:
            name: the name of the host

        Returns: the host object or None if the host is absent.

        """
        hosts = self.one.hostpool.info()
        for h in hosts.HOST:
            if name == h.NAME:
                return h
        return None

    def get_cluster_by_name(self, name):
        """
        Returns a cluster given its name.
        Args:
            name: the name of the cluster

        Returns: the cluster object or None if the host is absent.
        """

        clusters = self.one.clusterpool.info()
        for c in clusters.CLUSTER:
            if name == c.NAME:
                return c
        return None

    def get_template_by_name(self, name):
        """
        Returns a template given its name.
        Args:
            name: the name of the template

        Returns: the template object or None if the host is absent.

        """
        templates = self.one.templatepool.info()
        for t in templates.TEMPLATE:
            if name == t.NAME:
                return t
        return None

    def cast_template(self, template):
        """
        OpenNebula handles all template elements as strings
        At some point there is a cast being performed on types provided by the user
        This function mimics that transformation so that required template updates are detected properly
        additionally an array will be converted to a comma separated list,
        which works for labels and hopefully for something more.

        Args:
            template: the template to transform

        Returns: the transformed template with data casts applied.
        """

        # TODO: check formally available data types in templates
        # TODO: some arrays might be converted to space separated

        for key in template:
            value = template[key]
            if isinstance(value, dict):
                self.cast_template(template[key])
            elif isinstance(value, list):
                template[key] = ", ".join(value)
            elif not isinstance(value, str):
                template[key] = str(value)

    def requires_template_update(self, current, desired):
        """
        This function will help decide if a template update is required or not
        If a desired key is missing from the current dictionary an update is required
        If the intersection of both dictionaries is not deep equal, an update is required
        Args:
            current: current template as a dictionary
            desired: desired template as a dictionary

        Returns: True if a template update is required
        """

        if not desired:
            return False

        self.cast_template(desired)
        intersection = dict()
        for dkey in desired.keys():
            if dkey in current.keys():
                intersection[dkey] = current[dkey]
            else:
                return True
        return desired != intersection

    def wait_for_state(
        self,
        element_name,
        state,
        state_name,
        target_states,
        invalid_states=None,
        transition_states=None,
        wait_timeout=None,
    ):
        """
        Args:
            element_name: the name of the object we are waiting for: HOST, VM, etc.
            state: lambda that returns the current state, will be queried until target state is reached
            state_name: lambda that returns the readable form of a given state
            target_states: states expected to be reached
            invalid_states: if any of this states is reached, fail
            transition_states: when used, these are the valid states during the transition.
            wait_timeout: timeout period in seconds. Defaults to the provided parameter.
        """

        if not wait_timeout:
            wait_timeout = self.module.params.get("wait_timeout")

        start_time = time.time()

        while (time.time() - start_time) < wait_timeout:
            current_state = state()

            if current_state in invalid_states:
                self.fail(f"invalid {element_name} state {state_name(current_state)}")

            if transition_states:
                if current_state not in transition_states:
                    self.fail(f"invalid {element_name} transition state {state_name(current_state)}")

            if current_state in target_states:
                return True

            time.sleep(self.one.server_retry_interval())

        self.fail(msg="Wait timeout has expired!")

    def run_module(self):
        """
        trigger the start of the execution of the module.
        Returns:

        """
        try:
            self.run(self.one, self.module, self.result)
        except OneException as e:
            self.fail(msg=f"OpenNebula Exception: {e}")

    def run(self, one, module, result):
        """
        to be implemented by subclass with the actual module actions.
        Args:
            one: the OpenNebula XMLRPC client
            module: the Ansible Module object
            result: the Ansible result
        """
        raise NotImplementedError("Method requires implementation")

    def get_image_list_id(self, image, element):
        """
        This is a helper function for get_image_info to iterate over a simple list of objects
        """
        list_of_id = []

        if element == "VMS":
            image_list = image.VMS
        if element == "CLONES":
            image_list = image.CLONES
        if element == "APP_CLONES":
            image_list = image.APP_CLONES

        for iter in image_list.ID:
            list_of_id.append(
                # These are optional so firstly check for presence
                getattr(iter, "ID", "Null"),
            )
        return list_of_id

    def get_image_snapshots_list(self, image):
        """
        This is a helper function for get_image_info to iterate over a dictionary
        """
        list_of_snapshots = []

        for iter in image.SNAPSHOTS.SNAPSHOT:
            list_of_snapshots.append(
                {
                    "date": iter["DATE"],
                    "parent": iter["PARENT"],
                    "size": iter["SIZE"],
                    # These are optional so firstly check for presence
                    "allow_orhans": getattr(image.SNAPSHOTS, "ALLOW_ORPHANS", "Null"),
                    "children": getattr(iter, "CHILDREN", "Null"),
                    "active": getattr(iter, "ACTIVE", "Null"),
                    "name": getattr(iter, "NAME", "Null"),
                }
            )
        return list_of_snapshots

    def get_image_info(self, image):
        """
        This method is used by one_image and one_image_info modules to retrieve
        information from XSD scheme of an image
        Returns: a copy of the parameters that includes the resolved parameters.
        """
        info = {
            "id": image.ID,
            "name": image.NAME,
            "state": IMAGE_STATES[image.STATE],
            "running_vms": image.RUNNING_VMS,
            "used": bool(image.RUNNING_VMS),
            "user_name": image.UNAME,
            "user_id": image.UID,
            "group_name": image.GNAME,
            "group_id": image.GID,
            "permissions": {
                "owner_u": image.PERMISSIONS.OWNER_U,
                "owner_m": image.PERMISSIONS.OWNER_M,
                "owner_a": image.PERMISSIONS.OWNER_A,
                "group_u": image.PERMISSIONS.GROUP_U,
                "group_m": image.PERMISSIONS.GROUP_M,
                "group_a": image.PERMISSIONS.GROUP_A,
                "other_u": image.PERMISSIONS.OTHER_U,
                "other_m": image.PERMISSIONS.OTHER_M,
                "other_a": image.PERMISSIONS.OTHER_A,
            },
            "type": image.TYPE,
            "disk_type": image.DISK_TYPE,
            "persistent": image.PERSISTENT,
            "regtime": image.REGTIME,
            "source": image.SOURCE,
            "path": image.PATH,
            "fstype": getattr(image, "FSTYPE", "Null"),
            "size": image.SIZE,
            "cloning_ops": image.CLONING_OPS,
            "cloning_id": image.CLONING_ID,
            "target_snapshot": image.TARGET_SNAPSHOT,
            "datastore_id": image.DATASTORE_ID,
            "datastore": image.DATASTORE,
            "vms": self.get_image_list_id(image, "VMS"),
            "clones": self.get_image_list_id(image, "CLONES"),
            "app_clones": self.get_image_list_id(image, "APP_CLONES"),
            "snapshots": self.get_image_snapshots_list(image),
            "template": image.TEMPLATE,
        }
        return info
