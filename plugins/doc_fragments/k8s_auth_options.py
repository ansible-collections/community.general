# -*- coding: utf-8 -*-

# Copyright: (c) 2018,  Red Hat | Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Options for authenticating with the API.
# NOTE: This file is a copy of the one from community.kubernetes.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
  host:
    description:
    - Provide a URL for accessing the API. Can also be specified via K8S_AUTH_HOST environment variable.
    type: str
  api_key:
    description:
    - Token used to authenticate with the API. Can also be specified via K8S_AUTH_API_KEY environment variable.
    type: str
  kubeconfig:
    description:
    - Path to an existing Kubernetes config file. If not provided, and no other connection
      options are provided, the openshift client will attempt to load the default
      configuration file from I(~/.kube/config.json). Can also be specified via K8S_AUTH_KUBECONFIG environment
      variable.
    type: path
  context:
    description:
    - The name of a context found in the config file. Can also be specified via K8S_AUTH_CONTEXT environment variable.
    type: str
  username:
    description:
    - Provide a username for authenticating with the API. Can also be specified via K8S_AUTH_USERNAME environment
      variable.
    - Please note that this only works with clusters configured to use HTTP Basic Auth. If your cluster has a
      different form of authentication (e.g. OAuth2 in OpenShift), this option will not work as expected and you
      should look into the C(k8s_auth) module, as that might do what you need.
    type: str
  password:
    description:
    - Provide a password for authenticating with the API. Can also be specified via K8S_AUTH_PASSWORD environment
      variable.
    - Please read the description of the C(username) option for a discussion of when this option is applicable.
    type: str
  client_cert:
    description:
    - Path to a certificate used to authenticate with the API. Can also be specified via K8S_AUTH_CERT_FILE environment
      variable.
    type: path
    aliases: [ cert_file ]
  client_key:
    description:
    - Path to a key file used to authenticate with the API. Can also be specified via K8S_AUTH_KEY_FILE environment
      variable.
    type: path
    aliases: [ key_file ]
  ca_cert:
    description:
    - Path to a CA certificate used to authenticate with the API. The full certificate chain must be provided to
      avoid certificate validation errors. Can also be specified via K8S_AUTH_SSL_CA_CERT environment variable.
    type: path
    aliases: [ ssl_ca_cert ]
  validate_certs:
    description:
    - Whether or not to verify the API server's SSL certificates. Can also be specified via K8S_AUTH_VERIFY_SSL
      environment variable.
    type: bool
    aliases: [ verify_ssl ]
  proxy:
    description:
    - The URL of an HTTP proxy to use for the connection. Can also be specified via K8S_AUTH_PROXY environment variable.
    - Please note that this module does not pick up typical proxy settings from the environment (e.g. HTTP_PROXY).
    type: str
  persist_config:
    description:
    - Whether or not to save the kube config refresh tokens.
      Can also be specified via K8S_AUTH_PERSIST_CONFIG environment variable.
    - When the k8s context is using a user credentials with refresh tokens (like oidc or gke/gcloud auth),
      the token is refreshed by the k8s python client library but not saved by default. So the old refresh token can
      expire and the next auth might fail. Setting this flag to true will tell the k8s python client to save the
      new refresh token to the kube config file.
    - Default to false.
    - Please note that the current version of the k8s python client library does not support setting this flag to True yet.
    - "The fix for this k8s python library is here: https://github.com/kubernetes-client/python-base/pull/169"
    type: bool
notes:
  - "The OpenShift Python client wraps the K8s Python client, providing full access to
    all of the APIS and models available on both platforms. For API version details and
    additional information visit https://github.com/openshift/openshift-restclient-python"
  - "To avoid SSL certificate validation errors when C(validate_certs) is I(True), the full
    certificate chain for the API server must be provided via C(ca_cert) or in the
    kubeconfig file."
'''
