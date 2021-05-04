#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Guillaume Grossetie <ggrossetie@yuzutech.fr>
# Copyright: (c) 2021, quidame <quidame@poivron.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: java_keystore
short_description: Create a Java keystore in JKS format
description:
  - Bundle a x509 certificate and its private key into a Java Keystore in JKS format.
options:
  name:
    description:
      - Name of the certificate in the keystore.
      - If the provided name does not exist in the keystore, the module
        will re-create the keystore. This behavior changed in community.general 3.0.0,
        before that the module would fail when the name did not match.
    type: str
    required: true
  certificate:
    description:
      - Content of the certificate used to create the keystore.
      - If the fingerprint of the provided certificate does not match the
        fingerprint of the certificate bundled in the keystore, the keystore
        is regenerated with the provided certificate.
      - Exactly one of I(certificate) or I(certificate_path) is required.
    type: str
  certificate_path:
    description:
      - Location of the certificate used to create the keystore.
      - If the fingerprint of the provided certificate does not match the
        fingerprint of the certificate bundled in the keystore, the keystore
        is regenerated with the provided certificate.
      - Exactly one of I(certificate) or I(certificate_path) is required.
    type: path
    version_added: '3.0.0'
  private_key:
    description:
      - Content of the private key used to create the keystore.
      - Exactly one of I(private_key) or I(private_key_path) is required.
    type: str
  private_key_path:
    description:
      - Location of the private key used to create the keystore.
      - Exactly one of I(private_key) or I(private_key_path) is required.
    type: path
    version_added: '3.0.0'
  private_key_passphrase:
    description:
      - Passphrase used to read the private key, if required.
    type: str
    version_added: '0.2.0'
  password:
    description:
      - Password that should be used to secure the keystore.
      - If the provided password fails to unlock the keystore, the module
        will re-create the keystore with the new passphrase. This behavior
        changed in community.general 3.0.0, before that the module would fail
        when the password did not match.
    type: str
    required: true
  dest:
    description:
      - Absolute path of the generated keystore.
    type: path
    required: true
  force:
    description:
      - Keystore is created even if it already exists.
    type: bool
    default: 'no'
  owner:
    description:
      - Name of the user that should own jks file.
    required: false
  group:
    description:
      - Name of the group that should own jks file.
    required: false
  mode:
    description:
      - Mode the file should be.
    required: false
requirements:
  - openssl in PATH
  - keytool in PATH
author:
  - Guillaume Grossetie (@Mogztter)
  - quidame (@quidame)
extends_documentation_fragment:
  - files
seealso:
  - module: community.general.java_cert
notes:
  - I(certificate) and I(private_key) require that their contents are available
    on the controller (either inline in a playbook, or with the C(file) lookup),
    while I(certificate_path) and I(private_key_path) require that the files are
    available on the target host.
'''

EXAMPLES = '''
- name: Create a keystore for the given certificate/private key pair (inline)
  community.general.java_keystore:
    name: example
    certificate: |
      -----BEGIN CERTIFICATE-----
      h19dUZ2co2fI/ibYiwxWk4aeNE6KWvCaTQOMQ8t6Uo2XKhpL/xnjoAgh1uCQN/69
      MG+34+RhUWzCfdZH7T8/qDxJw2kEPKluaYh7KnMsba+5jHjmtzix5QIDAQABo4IB
      -----END CERTIFICATE-----
    private_key: |
      -----BEGIN RSA PRIVATE KEY-----
      DBVFTEVDVFJJQ0lURSBERSBGUkFOQ0UxFzAVBgNVBAsMDjAwMDIgNTUyMDgxMzE3
      GLlDNMw/uHyME7gHFsqJA7O11VY6O5WQ4IDP3m/s5ZV6s+Nn6Lerz17VZ99
      -----END RSA PRIVATE KEY-----
    password: changeit
    dest: /etc/security/keystore.jks

- name: Create a keystore for the given certificate/private key pair (with files on controller)
  community.general.java_keystore:
    name: example
    certificate: "{{ lookup('file', '/path/to/certificate.crt') }}"
    private_key: "{{ lookup('file', '/path/to/private.key') }}"
    password: changeit
    dest: /etc/security/keystore.jks

- name: Create a keystore for the given certificate/private key pair (with files on target host)
  community.general.java_keystore:
    name: snakeoil
    certificate_path: /etc/ssl/certs/ssl-cert-snakeoil.pem
    private_key_path: /etc/ssl/private/ssl-cert-snakeoil.key
    password: changeit
    dest: /etc/security/keystore.jks
'''

RETURN = '''
msg:
  description: Output from stdout of keytool/openssl command after execution of given command or an error.
  returned: changed and failure
  type: str
  sample: "Unable to find the current certificate fingerprint in ..."

rc:
  description: keytool/openssl command execution return value
  returned: changed and failure
  type: int
  sample: "0"

cmd:
  description: Executed command to get action done
  returned: changed and failure
  type: str
  sample: "/usr/bin/openssl x509 -noout -in /tmp/user/1000/tmp8jd_lh23 -fingerprint -sha256"
'''


import os
import re
import tempfile

from ansible.module_utils.basic import AnsibleModule


def read_certificate_fingerprint(module, openssl_bin, certificate_path):
    current_certificate_fingerprint_cmd = [openssl_bin, "x509", "-noout", "-in", certificate_path, "-fingerprint", "-sha256"]
    (rc, current_certificate_fingerprint_out, current_certificate_fingerprint_err) = run_commands(module, current_certificate_fingerprint_cmd)
    if rc != 0:
        return module.fail_json(msg=current_certificate_fingerprint_out,
                                err=current_certificate_fingerprint_err,
                                cmd=current_certificate_fingerprint_cmd,
                                rc=rc)

    current_certificate_match = re.search(r"=([\w:]+)", current_certificate_fingerprint_out)
    if not current_certificate_match:
        return module.fail_json(msg="Unable to find the current certificate fingerprint in %s" % current_certificate_fingerprint_out,
                                cmd=current_certificate_fingerprint_cmd,
                                rc=rc)

    return current_certificate_match.group(1)


def read_stored_certificate_fingerprint(module, keytool_bin, alias, keystore_path, keystore_password):
    stored_certificate_fingerprint_cmd = [keytool_bin, "-list", "-alias", alias, "-keystore", keystore_path, "-storepass:env", "STOREPASS", "-v"]
    (rc, stored_certificate_fingerprint_out, stored_certificate_fingerprint_err) = run_commands(
        module, stored_certificate_fingerprint_cmd, environ_update=dict(STOREPASS=keystore_password))
    if rc != 0:
        if "keytool error: java.lang.Exception: Alias <%s> does not exist" % alias in stored_certificate_fingerprint_out:
            return "alias mismatch"
        if re.match(r'keytool error: java\.io\.IOException: [Kk]eystore( was tampered with, or)? password was incorrect',
                    stored_certificate_fingerprint_out):
            return "password mismatch"
        return module.fail_json(msg=stored_certificate_fingerprint_out,
                                err=stored_certificate_fingerprint_err,
                                cmd=stored_certificate_fingerprint_cmd,
                                rc=rc)

    stored_certificate_match = re.search(r"SHA256: ([\w:]+)", stored_certificate_fingerprint_out)
    if not stored_certificate_match:
        return module.fail_json(msg="Unable to find the stored certificate fingerprint in %s" % stored_certificate_fingerprint_out,
                                cmd=stored_certificate_fingerprint_cmd,
                                rc=rc)

    return stored_certificate_match.group(1)


def run_commands(module, cmd, data=None, environ_update=None, check_rc=False):
    return module.run_command(cmd, check_rc=check_rc, data=data, environ_update=environ_update)


def create_path():
    dummy, tmpfile = tempfile.mkstemp()
    os.remove(tmpfile)
    return tmpfile


def create_file(content):
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, 'w') as f:
        f.write(content)
    return tmpfile


def create_tmp_certificate(module):
    return create_file(module.params['certificate'])


def create_tmp_private_key(module):
    return create_file(module.params['private_key'])


def cert_changed(module, openssl_bin, keytool_bin, keystore_path, keystore_pass, alias):
    certificate_path = module.params['certificate_path']
    if certificate_path is None:
        certificate_path = create_tmp_certificate(module)
    try:
        current_certificate_fingerprint = read_certificate_fingerprint(module, openssl_bin, certificate_path)
        stored_certificate_fingerprint = read_stored_certificate_fingerprint(module, keytool_bin, alias, keystore_path, keystore_pass)
        return current_certificate_fingerprint != stored_certificate_fingerprint
    finally:
        if module.params['certificate_path'] is None:
            os.remove(certificate_path)


def create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass):
    if module.check_mode:
        return module.exit_json(changed=True)

    certificate_path = module.params['certificate_path']
    if certificate_path is None:
        certificate_path = create_tmp_certificate(module)

    private_key_path = module.params['private_key_path']
    if private_key_path is None:
        private_key_path = create_tmp_private_key(module)

    keystore_p12_path = create_path()

    try:
        if os.path.exists(keystore_path):
            os.remove(keystore_path)

        export_p12_cmd = [openssl_bin, "pkcs12", "-export", "-name", name, "-in", certificate_path,
                          "-inkey", private_key_path, "-out", keystore_p12_path, "-passout", "stdin"]

        # when keypass is provided, add -passin
        cmd_stdin = ""
        if keypass:
            export_p12_cmd.append("-passin")
            export_p12_cmd.append("stdin")
            cmd_stdin = "%s\n" % keypass
        cmd_stdin += "%s\n%s" % (password, password)

        (rc, export_p12_out, dummy) = run_commands(module, export_p12_cmd, data=cmd_stdin)
        if rc != 0:
            return module.fail_json(msg=export_p12_out,
                                    cmd=export_p12_cmd,
                                    rc=rc)

        import_keystore_cmd = [keytool_bin, "-importkeystore",
                               "-destkeystore", keystore_path,
                               "-srckeystore", keystore_p12_path,
                               "-srcstoretype", "pkcs12",
                               "-alias", name,
                               "-deststorepass:env", "STOREPASS",
                               "-srcstorepass:env", "STOREPASS",
                               "-noprompt"]

        (rc, import_keystore_out, dummy) = run_commands(module, import_keystore_cmd, data=None,
                                                        environ_update=dict(STOREPASS=password))
        if rc != 0:
            return module.fail_json(msg=import_keystore_out,
                                    cmd=import_keystore_cmd,
                                    rc=rc)

        update_jks_perm(module, keystore_path)
        return module.exit_json(changed=True,
                                msg=import_keystore_out,
                                cmd=import_keystore_cmd,
                                rc=rc)
    finally:
        if module.params['certificate_path'] is None:
            os.remove(certificate_path)
        if module.params['private_key_path'] is None:
            os.remove(private_key_path)
        os.remove(keystore_p12_path)


def update_jks_perm(module, keystore_path):
    try:
        file_args = module.load_file_common_arguments(module.params, path=keystore_path)
    except TypeError:
        # The path argument is only supported in Ansible-base 2.10+. Fall back to
        # pre-2.10 behavior for older Ansible versions.
        module.params['path'] = keystore_path
        file_args = module.load_file_common_arguments(module.params)
    module.set_fs_attributes_if_different(file_args, False)


def process_jks(module):
    name = module.params['name']
    password = module.params['password']
    keypass = module.params['private_key_passphrase']
    keystore_path = module.params['dest']
    force = module.params['force']
    openssl_bin = module.get_bin_path('openssl', True)
    keytool_bin = module.get_bin_path('keytool', True)

    if os.path.exists(keystore_path):
        if force:
            create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass)
        else:
            if cert_changed(module, openssl_bin, keytool_bin, keystore_path, password, name):
                create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass)
            else:
                if not module.check_mode:
                    update_jks_perm(module, keystore_path)
                module.exit_json(changed=False)
    else:
        create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass)


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.add_file_common_args = True
        argument_spec = dict(
            name=dict(type='str', required=True),
            dest=dict(type='path', required=True),
            certificate=dict(type='str', no_log=True),
            certificate_path=dict(type='path'),
            private_key=dict(type='str', no_log=True),
            private_key_path=dict(type='path', no_log=False),
            private_key_passphrase=dict(type='str', no_log=True),
            password=dict(type='str', required=True, no_log=True),
            force=dict(type='bool', default=False),
        )
        choose_between = (
            ['certificate', 'certificate_path'],
            ['private_key', 'private_key_path'],
        )
        self.argument_spec = argument_spec
        self.required_one_of = choose_between
        self.mutually_exclusive = choose_between


def main():
    spec = ArgumentSpec()
    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        required_one_of=spec.required_one_of,
        mutually_exclusive=spec.mutually_exclusive,
        supports_check_mode=spec.supports_check_mode,
        add_file_common_args=spec.add_file_common_args,
    )
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')
    process_jks(module)


if __name__ == '__main__':
    main()
