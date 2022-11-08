#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2016, Guillaume Grossetie <ggrossetie@yuzutech.fr>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: java_keystore
short_description: Create or delete a Java keystore in JKS format.
description:
     - Create or delete a Java keystore in JKS format for a given certificate.
options:
    name:
        description:
          - Name of the certificate.
        required: true
    certificate:
        description:
          - Certificate that should be used to create the key store.
        required: true
    private_key:
        description:
          - Private key that should be used to create the key store.
        required: true
    private_key_passphrase:
        description:
          - Pass phrase for reading the private key, if required.
        type: str
        required: false
        version_added: '0.2.0'
    password:
        description:
          - Password that should be used to secure the key store.
        required: true
    dest:
        description:
          - Absolute path where the jks should be generated.
        required: true
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
    force:
        description:
          - Key store will be created even if it already exists.
        required: false
        type: bool
        default: 'no'
requirements: [openssl, keytool]
author: Guillaume Grossetie (@Mogztter)
'''

EXAMPLES = '''
- name: Create a key store for the given certificate (inline)
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

- name: Create a key store for the given certificate (lookup)
  community.general.java_keystore:
    name: example
    certificate: "{{lookup('file', '/path/to/certificate.crt') }}"
    private_key: "{{lookup('file', '/path/to/private.key') }}"
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
  sample: "openssl x509 -noout -in /tmp/cert.crt -fingerprint -sha256"
'''


from ansible.module_utils.basic import AnsibleModule
import os
import re


def read_certificate_fingerprint(module, openssl_bin, certificate_path):
    current_certificate_fingerprint_cmd = [openssl_bin, "x509", "-noout", "-in", certificate_path, "-fingerprint", "-sha256"]
    (rc, current_certificate_fingerprint_out, current_certificate_fingerprint_err) = run_commands(module, current_certificate_fingerprint_cmd)
    if rc != 0:
        return module.fail_json(msg=current_certificate_fingerprint_out,
                                err=current_certificate_fingerprint_err,
                                rc=rc,
                                cmd=current_certificate_fingerprint_cmd)

    current_certificate_match = re.search(r"=([\w:]+)", current_certificate_fingerprint_out)
    if not current_certificate_match:
        return module.fail_json(
            msg="Unable to find the current certificate fingerprint in %s" % current_certificate_fingerprint_out,
            rc=rc,
            cmd=current_certificate_fingerprint_err
        )

    return current_certificate_match.group(1)


def read_stored_certificate_fingerprint(module, keytool_bin, alias, keystore_path, keystore_password):
    stored_certificate_fingerprint_cmd = [keytool_bin, "-list", "-alias", alias, "-keystore", keystore_path, "-storepass", keystore_password, "-v"]
    (rc, stored_certificate_fingerprint_out, stored_certificate_fingerprint_err) = run_commands(module, stored_certificate_fingerprint_cmd)
    if rc != 0:
        if "keytool error: java.lang.Exception: Alias <%s> does not exist" % alias not in stored_certificate_fingerprint_out:
            return module.fail_json(msg=stored_certificate_fingerprint_out,
                                    err=stored_certificate_fingerprint_err,
                                    rc=rc,
                                    cmd=stored_certificate_fingerprint_cmd)
        else:
            return None
    else:
        stored_certificate_match = re.search(r"SHA256: ([\w:]+)", stored_certificate_fingerprint_out)
        if not stored_certificate_match:
            return module.fail_json(
                msg="Unable to find the stored certificate fingerprint in %s" % stored_certificate_fingerprint_out,
                rc=rc,
                cmd=stored_certificate_fingerprint_cmd
            )

        return stored_certificate_match.group(1)


def run_commands(module, cmd, data=None, check_rc=True):
    return module.run_command(cmd, check_rc=check_rc, data=data)


def create_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    return path


def create_tmp_certificate(module):
    return create_file("/tmp/%s.crt" % module.params['name'], module.params['certificate'])


def create_tmp_private_key(module):
    return create_file("/tmp/%s.key" % module.params['name'], module.params['private_key'])


def cert_changed(module, openssl_bin, keytool_bin, keystore_path, keystore_pass, alias):
    certificate_path = create_tmp_certificate(module)
    try:
        current_certificate_fingerprint = read_certificate_fingerprint(module, openssl_bin, certificate_path)
        stored_certificate_fingerprint = read_stored_certificate_fingerprint(module, keytool_bin, alias, keystore_path, keystore_pass)
        return current_certificate_fingerprint != stored_certificate_fingerprint
    finally:
        os.remove(certificate_path)


def create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass):
    if module.check_mode:
        module.exit_json(changed=True)
    else:
        certificate_path = create_tmp_certificate(module)
        private_key_path = create_tmp_private_key(module)
        try:
            if os.path.exists(keystore_path):
                os.remove(keystore_path)

            keystore_p12_path = "/tmp/keystore.p12"
            if os.path.exists(keystore_p12_path):
                os.remove(keystore_p12_path)

            export_p12_cmd = [openssl_bin, "pkcs12", "-export", "-name", name, "-in", certificate_path,
                              "-inkey", private_key_path, "-out",
                              keystore_p12_path, "-passout", "stdin"]

            # when keypass is provided, add -passin
            cmd_stdin = ""
            if keypass:
                export_p12_cmd.append("-passin")
                export_p12_cmd.append("stdin")
                cmd_stdin = "%s\n" % keypass

            cmd_stdin += "%s\n%s" % (password, password)
            (rc, export_p12_out, export_p12_err) = run_commands(module, export_p12_cmd, data=cmd_stdin)
            if rc != 0:
                return module.fail_json(msg=export_p12_out,
                                        rc=rc,
                                        cmd=export_p12_cmd)

            import_keystore_cmd = [keytool_bin, "-importkeystore",
                                   "-destkeystore", keystore_path,
                                   "-srckeystore", keystore_p12_path,
                                   "-srcstoretype", "pkcs12",
                                   "-alias", name,
                                   "-deststorepass", password,
                                   "-srcstorepass", password,
                                   "-noprompt"]
            (rc, import_keystore_out, import_keystore_err) = run_commands(module, import_keystore_cmd, data=None)
            if rc == 0:
                update_jks_perm(module, keystore_path)
                return module.exit_json(changed=True,
                                        msg=import_keystore_out,
                                        rc=rc,
                                        cmd=import_keystore_cmd,
                                        stdout_lines=import_keystore_out)
            else:
                return module.fail_json(msg=import_keystore_out,
                                        rc=rc,
                                        cmd=import_keystore_cmd)
        finally:
            os.remove(certificate_path)
            os.remove(private_key_path)


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
                return module.exit_json(changed=False)
    else:
        create_jks(module, name, openssl_bin, keytool_bin, keystore_path, password, keypass)


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        self.add_file_common_args = True
        argument_spec = dict(
            name=dict(required=True),
            certificate=dict(required=True, no_log=True),
            private_key=dict(required=True, no_log=True),
            password=dict(required=True, no_log=True),
            dest=dict(required=True),
            force=dict(required=False, default=False, type='bool'),
            private_key_passphrase=dict(required=False, no_log=True, type='str')
        )
        self.argument_spec = argument_spec


def main():
    spec = ArgumentSpec()
    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        add_file_common_args=spec.add_file_common_args,
        supports_check_mode=spec.supports_check_mode
    )
    process_jks(module)


if __name__ == '__main__':
    main()
