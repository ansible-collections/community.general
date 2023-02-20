#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, RSD Services S.A
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: java_cert

short_description: Uses keytool to import/remove certificate to/from java keystore (cacerts)
description:
  - This is a wrapper module around keytool, which can be used to import certificates
    and optionally private keys to a given java keystore, or remove them from it.
extends_documentation_fragment:
  - community.general.attributes
attributes:
  check_mode:
    support: full
  diff_mode:
    support: full
options:
  cert_url:
    description:
      - Basic URL to fetch SSL certificate from.
      - Exactly one of C(cert_url), C(cert_path) or C(pkcs12_path) is required to load certificate.
    type: str
  cert_port:
    description:
      - Port to connect to URL.
      - This will be used to create server URL:PORT.
    type: int
    default: 443
  cert_path:
    description:
      - Local path to load certificate from.
      - Exactly one of C(cert_url), C(cert_path) or C(pkcs12_path) is required to load certificate.
    type: path
  cert_alias:
    description:
      - Imported certificate alias.
      - The alias is used when checking for the presence of a certificate in the keystore.
    type: str
  trust_cacert:
    description:
      - Trust imported cert as CAcert.
    type: bool
    default: false
    version_added: '0.2.0'
  pkcs12_path:
    description:
      - Local path to load PKCS12 keystore from.
      - Unlike C(cert_url) and C(cert_path), the PKCS12 keystore embeds the private key matching
        the certificate, and is used to import both the certificate and its private key into the
        java keystore.
      - Exactly one of C(cert_url), C(cert_path) or C(pkcs12_path) is required to load certificate.
    type: path
  pkcs12_password:
    description:
      - Password for importing from PKCS12 keystore.
    type: str
  pkcs12_alias:
    description:
      - Alias in the PKCS12 keystore.
    type: str
  keystore_path:
    description:
      - Path to keystore.
    type: path
  keystore_pass:
    description:
      - Keystore password.
    type: str
    required: true
  keystore_create:
    description:
      - Create keystore if it does not exist.
    type: bool
    default: false
  keystore_type:
    description:
      - Keystore type (JCEKS, JKS).
    type: str
  executable:
    description:
      - Path to keytool binary if not used we search in PATH for it.
    type: str
    default: keytool
  state:
    description:
      - Defines action which can be either certificate import or removal.
      - When state is present, the certificate will always idempotently be inserted
        into the keystore, even if there already exists a cert alias that is different.
    type: str
    choices: [ absent, present ]
    default: present
requirements: [openssl, keytool]
author:
- Adam Hamsik (@haad)
'''

EXAMPLES = r'''
- name: Import SSL certificate from google.com to a given cacerts keystore
  community.general.java_cert:
    cert_url: google.com
    cert_port: 443
    keystore_path: /usr/lib/jvm/jre7/lib/security/cacerts
    keystore_pass: changeit
    state: present

- name: Remove certificate with given alias from a keystore
  community.general.java_cert:
    cert_url: google.com
    keystore_path: /usr/lib/jvm/jre7/lib/security/cacerts
    keystore_pass: changeit
    executable: /usr/lib/jvm/jre7/bin/keytool
    state: absent

- name: Import trusted CA from SSL certificate
  community.general.java_cert:
    cert_path: /opt/certs/rootca.crt
    keystore_path: /tmp/cacerts
    keystore_pass: changeit
    keystore_create: true
    state: present
    cert_alias: LE_RootCA
    trust_cacert: true

- name: Import SSL certificate from google.com to a keystore, create it if it doesn't exist
  community.general.java_cert:
    cert_url: google.com
    keystore_path: /tmp/cacerts
    keystore_pass: changeit
    keystore_create: true
    state: present

- name: Import a pkcs12 keystore with a specified alias, create it if it doesn't exist
  community.general.java_cert:
    pkcs12_path: "/tmp/importkeystore.p12"
    cert_alias: default
    keystore_path: /opt/wildfly/standalone/configuration/defaultkeystore.jks
    keystore_pass: changeit
    keystore_create: true
    state: present

- name: Import SSL certificate to JCEKS keystore
  community.general.java_cert:
    pkcs12_path: "/tmp/importkeystore.p12"
    pkcs12_alias: default
    pkcs12_password: somepass
    cert_alias: default
    keystore_path: /opt/someapp/security/keystore.jceks
    keystore_type: "JCEKS"
    keystore_pass: changeit
    keystore_create: true
    state: present
'''

RETURN = r'''
msg:
  description: Output from stdout of keytool command after execution of given command.
  returned: success
  type: str
  sample: "Module require existing keystore at keystore_path '/tmp/test/cacerts'"

rc:
  description: Keytool command execution return value.
  returned: success
  type: int
  sample: "0"

cmd:
  description: Executed command to get action done.
  returned: success
  type: str
  sample: "keytool -importcert -noprompt -keystore"
'''

import os
import tempfile
import re


# import module snippets
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import urlparse
from ansible.module_utils.six.moves.urllib.request import getproxies


def _get_keystore_type_keytool_parameters(keystore_type):
    ''' Check that custom keystore is presented in parameters '''
    if keystore_type:
        return ["-storetype", keystore_type]
    return []


def _check_cert_present(module, executable, keystore_path, keystore_pass, alias, keystore_type):
    ''' Check if certificate with alias is present in keystore
        located at keystore_path '''
    test_cmd = [
        executable,
        "-list",
        "-keystore",
        keystore_path,
        "-alias",
        alias,
        "-rfc"
    ]
    test_cmd += _get_keystore_type_keytool_parameters(keystore_type)

    (check_rc, stdout, dummy) = module.run_command(test_cmd, data=keystore_pass, check_rc=False)
    if check_rc == 0:
        return (True, stdout)
    return (False, '')


def _get_certificate_from_url(module, executable, url, port, pem_certificate_output):
    remote_cert_pem_chain = _download_cert_url(module, executable, url, port)
    with open(pem_certificate_output, 'w') as f:
        f.write(remote_cert_pem_chain)


def _get_first_certificate_from_x509_file(module, pem_certificate_file, pem_certificate_output, openssl_bin):
    """ Read a X509 certificate chain file and output the first certificate in the list """
    extract_cmd = [
        openssl_bin,
        "x509",
        "-in",
        pem_certificate_file,
        "-out",
        pem_certificate_output
    ]
    (extract_rc, dummy, extract_stderr) = module.run_command(extract_cmd, check_rc=False)

    if extract_rc != 0:
        # trying der encoded file
        extract_cmd += ["-inform", "der"]
        (extract_rc, dummy, extract_stderr) = module.run_command(extract_cmd, check_rc=False)

        if extract_rc != 0:
            # this time it's a real failure
            module.fail_json(msg="Internal module failure, cannot extract certificate, error: %s" % extract_stderr,
                             rc=extract_rc, cmd=extract_cmd)

    return extract_rc


def _get_digest_from_x509_file(module, pem_certificate_file, openssl_bin):
    """ Read a X509 certificate file and output sha256 digest using openssl """
    # cleanup file before to compare
    (dummy, tmp_certificate) = tempfile.mkstemp()
    module.add_cleanup_file(tmp_certificate)
    _get_first_certificate_from_x509_file(module, pem_certificate_file, tmp_certificate, openssl_bin)
    dgst_cmd = [
        openssl_bin,
        "dgst",
        "-r",
        "-sha256",
        tmp_certificate
    ]
    (dgst_rc, dgst_stdout, dgst_stderr) = module.run_command(dgst_cmd, check_rc=False)

    if dgst_rc != 0:
        module.fail_json(msg="Internal module failure, cannot compute digest for certificate, error: %s" % dgst_stderr,
                         rc=dgst_rc, cmd=dgst_cmd)

    return dgst_stdout.split(' ')[0]


def _export_public_cert_from_pkcs12(module, executable, pkcs_file, alias, password, dest):
    """ Runs keytools to extract the public cert from a PKCS12 archive and write it to a file. """
    export_cmd = [
        executable,
        "-list",
        "-noprompt",
        "-keystore",
        pkcs_file,
        "-alias",
        alias,
        "-storetype",
        "pkcs12",
        "-rfc"
    ]
    (export_rc, export_stdout, export_err) = module.run_command(export_cmd, data=password, check_rc=False)

    if export_rc != 0:
        module.fail_json(msg="Internal module failure, cannot extract public certificate from PKCS12, message: %s" % export_stdout,
                         stderr=export_err,
                         rc=export_rc)

    with open(dest, 'w') as f:
        f.write(export_stdout)


def get_proxy_settings(scheme='https'):
    """ Returns a tuple containing (proxy_host, proxy_port). (False, False) if no proxy is found """
    proxy_url = getproxies().get(scheme, '')
    if not proxy_url:
        return (False, False)
    else:
        parsed_url = urlparse(proxy_url)
        if parsed_url.scheme:
            (proxy_host, proxy_port) = parsed_url.netloc.split(':')
        else:
            (proxy_host, proxy_port) = parsed_url.path.split(':')
        return (proxy_host, proxy_port)


def build_proxy_options():
    """ Returns list of valid proxy options for keytool """
    (proxy_host, proxy_port) = get_proxy_settings()
    no_proxy = os.getenv("no_proxy")

    proxy_opts = []
    if proxy_host:
        proxy_opts.extend(["-J-Dhttps.proxyHost=%s" % proxy_host, "-J-Dhttps.proxyPort=%s" % proxy_port])

        if no_proxy is not None:
            # For Java's nonProxyHosts property, items are separated by '|',
            # and patterns have to start with "*".
            non_proxy_hosts = no_proxy.replace(',', '|')
            non_proxy_hosts = re.sub(r'(^|\|)\.', r'\1*.', non_proxy_hosts)

            # The property name is http.nonProxyHosts, there is no
            # separate setting for HTTPS.
            proxy_opts.extend(["-J-Dhttp.nonProxyHosts=%s" % non_proxy_hosts])
    return proxy_opts


def _download_cert_url(module, executable, url, port):
    """ Fetches the certificate from the remote URL using `keytool -printcert...`
          The PEM formatted string is returned """
    proxy_opts = build_proxy_options()
    fetch_cmd = [executable, "-printcert", "-rfc", "-sslserver"] + proxy_opts + ["%s:%d" % (url, port)]

    # Fetch SSL certificate from remote host.
    (fetch_rc, fetch_out, fetch_err) = module.run_command(fetch_cmd, check_rc=False)

    if fetch_rc != 0:
        module.fail_json(msg="Internal module failure, cannot download certificate, error: %s" % fetch_err,
                         rc=fetch_rc, cmd=fetch_cmd)

    return fetch_out


def import_pkcs12_path(module, executable, pkcs12_path, pkcs12_pass, pkcs12_alias,
                       keystore_path, keystore_pass, keystore_alias, keystore_type):
    ''' Import pkcs12 from path into keystore located on
        keystore_path as alias '''
    import_cmd = [
        executable,
        "-importkeystore",
        "-noprompt",
        "-srcstoretype",
        "pkcs12",
        "-srckeystore",
        pkcs12_path,
        "-srcalias",
        pkcs12_alias,
        "-destkeystore",
        keystore_path,
        "-destalias",
        keystore_alias
    ]
    import_cmd += _get_keystore_type_keytool_parameters(keystore_type)

    secret_data = "%s\n%s" % (keystore_pass, pkcs12_pass)
    # Password of a new keystore must be entered twice, for confirmation
    if not os.path.exists(keystore_path):
        secret_data = "%s\n%s" % (keystore_pass, secret_data)

    # Use local certificate from local path and import it to a java keystore
    (import_rc, import_out, import_err) = module.run_command(import_cmd, data=secret_data, check_rc=False)

    diff = {'before': '\n', 'after': '%s\n' % keystore_alias}
    if import_rc == 0 and os.path.exists(keystore_path):
        module.exit_json(changed=True, msg=import_out,
                         rc=import_rc, cmd=import_cmd, stdout=import_out,
                         error=import_err, diff=diff)
    else:
        module.fail_json(msg=import_out, rc=import_rc, cmd=import_cmd, error=import_err)


def import_cert_path(module, executable, path, keystore_path, keystore_pass, alias, keystore_type, trust_cacert):
    ''' Import certificate from path into keystore located on
        keystore_path as alias '''
    import_cmd = [
        executable,
        "-importcert",
        "-noprompt",
        "-keystore",
        keystore_path,
        "-file",
        path,
        "-alias",
        alias
    ]
    import_cmd += _get_keystore_type_keytool_parameters(keystore_type)

    if trust_cacert:
        import_cmd.extend(["-trustcacerts"])

    # Use local certificate from local path and import it to a java keystore
    (import_rc, import_out, import_err) = module.run_command(import_cmd,
                                                             data="%s\n%s" % (keystore_pass, keystore_pass),
                                                             check_rc=False)

    diff = {'before': '\n', 'after': '%s\n' % alias}
    if import_rc == 0:
        module.exit_json(changed=True, msg=import_out,
                         rc=import_rc, cmd=import_cmd, stdout=import_out,
                         error=import_err, diff=diff)
    else:
        module.fail_json(msg=import_out, rc=import_rc, cmd=import_cmd)


def delete_cert(module, executable, keystore_path, keystore_pass, alias, keystore_type, exit_after=True):
    ''' Delete certificate identified with alias from keystore on keystore_path '''
    del_cmd = [
        executable,
        "-delete",
        "-noprompt",
        "-keystore",
        keystore_path,
        "-alias",
        alias
    ]

    del_cmd += _get_keystore_type_keytool_parameters(keystore_type)

    # Delete SSL certificate from keystore
    (del_rc, del_out, del_err) = module.run_command(del_cmd, data=keystore_pass, check_rc=True)

    if exit_after:
        diff = {'before': '%s\n' % alias, 'after': None}

        module.exit_json(changed=True, msg=del_out,
                         rc=del_rc, cmd=del_cmd, stdout=del_out,
                         error=del_err, diff=diff)


def test_keytool(module, executable):
    ''' Test if keytool is actually executable or not '''
    module.run_command([executable], check_rc=True)


def test_keystore(module, keystore_path):
    ''' Check if we can access keystore as file or not '''
    if keystore_path is None:
        keystore_path = ''

    if not os.path.exists(keystore_path) and not os.path.isfile(keystore_path):
        # Keystore doesn't exist we want to create it
        module.fail_json(changed=False, msg="Module require existing keystore at keystore_path '%s'" % keystore_path)


def main():
    argument_spec = dict(
        cert_url=dict(type='str'),
        cert_path=dict(type='path'),
        pkcs12_path=dict(type='path'),
        pkcs12_password=dict(type='str', no_log=True),
        pkcs12_alias=dict(type='str'),
        cert_alias=dict(type='str'),
        cert_port=dict(type='int', default=443),
        keystore_path=dict(type='path'),
        keystore_pass=dict(type='str', required=True, no_log=True),
        trust_cacert=dict(type='bool', default=False),
        keystore_create=dict(type='bool', default=False),
        keystore_type=dict(type='str'),
        executable=dict(type='str', default='keytool'),
        state=dict(type='str', default='present', choices=['absent', 'present']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=[['state', 'present', ('cert_path', 'cert_url', 'pkcs12_path'), True],
                     ['state', 'absent', ('cert_url', 'cert_alias'), True]],
        required_together=[['keystore_path', 'keystore_pass']],
        mutually_exclusive=[
            ['cert_url', 'cert_path', 'pkcs12_path']
        ],
        supports_check_mode=True,
    )

    url = module.params.get('cert_url')
    path = module.params.get('cert_path')
    port = module.params.get('cert_port')

    pkcs12_path = module.params.get('pkcs12_path')
    pkcs12_pass = module.params.get('pkcs12_password', '')
    pkcs12_alias = module.params.get('pkcs12_alias', '1')

    cert_alias = module.params.get('cert_alias') or url
    trust_cacert = module.params.get('trust_cacert')

    keystore_path = module.params.get('keystore_path')
    keystore_pass = module.params.get('keystore_pass')
    keystore_create = module.params.get('keystore_create')
    keystore_type = module.params.get('keystore_type')
    executable = module.params.get('executable')
    state = module.params.get('state')

    # openssl dependency resolution
    openssl_bin = module.get_bin_path('openssl', True)

    if path and not cert_alias:
        module.fail_json(changed=False,
                         msg="Using local path import from %s requires alias argument."
                             % keystore_path)

    test_keytool(module, executable)

    if not keystore_create:
        test_keystore(module, keystore_path)

    alias_exists, alias_exists_output = _check_cert_present(
        module, executable, keystore_path, keystore_pass, cert_alias, keystore_type)

    (dummy, new_certificate) = tempfile.mkstemp()
    (dummy, old_certificate) = tempfile.mkstemp()
    module.add_cleanup_file(new_certificate)
    module.add_cleanup_file(old_certificate)

    if state == 'absent' and alias_exists:
        if module.check_mode:
            module.exit_json(changed=True)

        # delete and exit
        delete_cert(module, executable, keystore_path, keystore_pass, cert_alias, keystore_type)

    # dump certificate to enroll in the keystore on disk and compute digest
    if state == 'present':
        # The alias exists in the keystore so we must now compare the SHA256 hash of the
        # public certificate already in the keystore, and the certificate we  are wanting to add
        if alias_exists:
            with open(old_certificate, "w") as f:
                f.write(alias_exists_output)
            keystore_cert_digest = _get_digest_from_x509_file(module, old_certificate, openssl_bin)

        else:
            keystore_cert_digest = ''

        if pkcs12_path:
            # Extracting certificate with openssl
            _export_public_cert_from_pkcs12(module, executable, pkcs12_path, pkcs12_alias, pkcs12_pass, new_certificate)

        elif path:
            # Extracting the X509 digest is a bit easier. Keytool will print the PEM
            # certificate to stdout so we don't need to do any transformations.
            new_certificate = path

        elif url:
            # Getting the X509 digest from a URL is the same as from a path, we just have
            # to download the cert first
            _get_certificate_from_url(module, executable, url, port, new_certificate)

        new_cert_digest = _get_digest_from_x509_file(module, new_certificate, openssl_bin)

        if keystore_cert_digest != new_cert_digest:

            if module.check_mode:
                module.exit_json(changed=True)

            if alias_exists:
                # The certificate in the keystore does not match with the one we want to be present
                # The existing certificate must first be deleted before we insert the correct one
                delete_cert(module, executable, keystore_path, keystore_pass, cert_alias, keystore_type, exit_after=False)

            if pkcs12_path:
                import_pkcs12_path(module, executable, pkcs12_path, pkcs12_pass, pkcs12_alias,
                                   keystore_path, keystore_pass, cert_alias, keystore_type)
            else:
                import_cert_path(module, executable, new_certificate, keystore_path,
                                 keystore_pass, cert_alias, keystore_type, trust_cacert)

    module.exit_json(changed=False)


if __name__ == "__main__":
    main()
