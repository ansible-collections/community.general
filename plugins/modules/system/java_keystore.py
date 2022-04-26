#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, quidame <quidame@poivron.org>
# Copyright: (c) 2016, Guillaume Grossetie <ggrossetie@yuzutech.fr>
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
  ssl_backend:
    description:
      - Backend for loading private keys and certificates.
    type: str
    default: openssl
    choices:
      - openssl
      - cryptography
    version_added: 3.1.0
  keystore_type:
    description:
      - Type of the Java keystore.
      - When this option is omitted and the keystore doesn't already exist, the
        behavior follows C(keytool)'s default store type which depends on
        Java version; C(pkcs12) since Java 9 and C(jks) prior (may also
        be C(pkcs12) if new default has been backported to this version).
      - When this option is omitted and the keystore already exists, the current
        type is left untouched, unless another option leads to overwrite the
        keystore (in that case, this option behaves like for keystore creation).
      - When I(keystore_type) is set, the keystore is created with this type if
        it doesn't already exist, or is overwritten to match the given type in
        case of mismatch.
    type: str
    choices:
      - jks
      - pkcs12
    version_added: 3.3.0
requirements:
  - openssl in PATH (when I(ssl_backend=openssl))
  - keytool in PATH
  - cryptography >= 3.0 (when I(ssl_backend=cryptography))
author:
  - Guillaume Grossetie (@Mogztter)
  - quidame (@quidame)
extends_documentation_fragment:
  - files
seealso:
  - module: community.crypto.openssl_pkcs12
  - module: community.general.java_cert
notes:
  - I(certificate) and I(private_key) require that their contents are available
    on the controller (either inline in a playbook, or with the C(file) lookup),
    while I(certificate_path) and I(private_key_path) require that the files are
    available on the target host.
  - By design, any change of a value of options I(keystore_type), I(name) or
    I(password), as well as changes of key or certificate materials will cause
    the existing I(dest) to be overwritten.
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

err:
  description: Output from stderr of keytool/openssl command after error of given command.
  returned: failure
  type: str
  sample: "Keystore password is too short - must be at least 6 characters\n"

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

from ansible.module_utils.six import PY2
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_bytes, to_native

try:
    from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates
    from cryptography.hazmat.primitives.serialization import (
        BestAvailableEncryption,
        NoEncryption,
        load_pem_private_key,
        load_der_private_key,
    )
    from cryptography.x509 import (
        load_pem_x509_certificate,
        load_der_x509_certificate,
    )
    from cryptography.hazmat.primitives import hashes
    from cryptography.exceptions import UnsupportedAlgorithm
    from cryptography.hazmat.backends.openssl import backend
    HAS_CRYPTOGRAPHY_PKCS12 = True
except ImportError:
    HAS_CRYPTOGRAPHY_PKCS12 = False


class JavaKeystore:
    def __init__(self, module):
        self.module = module
        self.result = dict()

        self.keytool_bin = module.get_bin_path('keytool', True)

        self.certificate = module.params['certificate']
        self.keypass = module.params['private_key_passphrase']
        self.keystore_path = module.params['dest']
        self.name = module.params['name']
        self.password = module.params['password']
        self.private_key = module.params['private_key']
        self.ssl_backend = module.params['ssl_backend']
        self.keystore_type = module.params['keystore_type']

        if self.ssl_backend == 'openssl':
            self.openssl_bin = module.get_bin_path('openssl', True)
        else:
            if not HAS_CRYPTOGRAPHY_PKCS12:
                self.module.fail_json(msg=missing_required_lib('cryptography >= 3.0'))

        if module.params['certificate_path'] is None:
            self.certificate_path = create_file(self.certificate)
            self.module.add_cleanup_file(self.certificate_path)
        else:
            self.certificate_path = module.params['certificate_path']

        if module.params['private_key_path'] is None:
            self.private_key_path = create_file(self.private_key)
            self.module.add_cleanup_file(self.private_key_path)
        else:
            self.private_key_path = module.params['private_key_path']

    def update_permissions(self):
        file_args = self.module.load_file_common_arguments(self.module.params, path=self.keystore_path)
        return self.module.set_fs_attributes_if_different(file_args, False)

    def read_certificate_fingerprint(self, cert_format='PEM'):
        if self.ssl_backend == 'cryptography':
            if cert_format == 'PEM':
                cert_loader = load_pem_x509_certificate
            else:
                cert_loader = load_der_x509_certificate

            try:
                with open(self.certificate_path, 'rb') as cert_file:
                    cert = cert_loader(
                        cert_file.read(),
                        backend=backend
                    )
            except (OSError, ValueError) as e:
                self.module.fail_json(msg="Unable to read the provided certificate: %s" % to_native(e))

            fp = hex_decode(cert.fingerprint(hashes.SHA256())).upper()
            fingerprint = ':'.join([fp[i:i + 2] for i in range(0, len(fp), 2)])
        else:
            current_certificate_fingerprint_cmd = [
                self.openssl_bin, "x509", "-noout", "-in", self.certificate_path, "-fingerprint", "-sha256"
            ]
            (rc, current_certificate_fingerprint_out, current_certificate_fingerprint_err) = self.module.run_command(
                current_certificate_fingerprint_cmd,
                environ_update=None,
                check_rc=False
            )
            if rc != 0:
                return self.module.fail_json(
                    msg=current_certificate_fingerprint_out,
                    err=current_certificate_fingerprint_err,
                    cmd=current_certificate_fingerprint_cmd,
                    rc=rc
                )

            current_certificate_match = re.search(r"=([\w:]+)", current_certificate_fingerprint_out)
            if not current_certificate_match:
                return self.module.fail_json(
                    msg="Unable to find the current certificate fingerprint in %s" % (
                        current_certificate_fingerprint_out
                    ),
                    cmd=current_certificate_fingerprint_cmd,
                    rc=rc
                )

            fingerprint = current_certificate_match.group(1)
        return fingerprint

    def read_stored_certificate_fingerprint(self):
        stored_certificate_fingerprint_cmd = [
            self.keytool_bin, "-list", "-alias", self.name,
            "-keystore", self.keystore_path, "-v"
        ]
        (rc, stored_certificate_fingerprint_out, stored_certificate_fingerprint_err) = self.module.run_command(
            stored_certificate_fingerprint_cmd, data=self.password, check_rc=False)
        if rc != 0:
            if "keytool error: java.lang.Exception: Alias <%s> does not exist" % self.name \
                    in stored_certificate_fingerprint_out:
                return "alias mismatch"
            if re.match(
                    r'keytool error: java\.io\.IOException: ' +
                    '[Kk]eystore( was tampered with, or)? password was incorrect',
                    stored_certificate_fingerprint_out
            ):
                return "password mismatch"
            return self.module.fail_json(
                msg=stored_certificate_fingerprint_out,
                err=stored_certificate_fingerprint_err,
                cmd=stored_certificate_fingerprint_cmd,
                rc=rc
            )

        if self.keystore_type not in (None, self.current_type()):
            return "keystore type mismatch"

        stored_certificate_match = re.search(r"SHA256: ([\w:]+)", stored_certificate_fingerprint_out)
        if not stored_certificate_match:
            return self.module.fail_json(
                msg="Unable to find the stored certificate fingerprint in %s" % stored_certificate_fingerprint_out,
                cmd=stored_certificate_fingerprint_cmd,
                rc=rc
            )

        return stored_certificate_match.group(1)

    def current_type(self):
        magic_bytes = b'\xfe\xed\xfe\xed'
        with open(self.keystore_path, 'rb') as fd:
            header = fd.read(4)
        if header == magic_bytes:
            return 'jks'
        return 'pkcs12'

    def cert_changed(self):
        current_certificate_fingerprint = self.read_certificate_fingerprint()
        stored_certificate_fingerprint = self.read_stored_certificate_fingerprint()
        return current_certificate_fingerprint != stored_certificate_fingerprint

    def cryptography_create_pkcs12_bundle(self, keystore_p12_path, key_format='PEM', cert_format='PEM'):
        if key_format == 'PEM':
            key_loader = load_pem_private_key
        else:
            key_loader = load_der_private_key

        if cert_format == 'PEM':
            cert_loader = load_pem_x509_certificate
        else:
            cert_loader = load_der_x509_certificate

        try:
            with open(self.private_key_path, 'rb') as key_file:
                private_key = key_loader(
                    key_file.read(),
                    password=to_bytes(self.keypass),
                    backend=backend
                )
        except TypeError:
            # Re-attempt with no password to match existing behavior
            try:
                with open(self.private_key_path, 'rb') as key_file:
                    private_key = key_loader(
                        key_file.read(),
                        password=None,
                        backend=backend
                    )
            except (OSError, TypeError, ValueError, UnsupportedAlgorithm) as e:
                self.module.fail_json(
                    msg="The following error occurred while loading the provided private_key: %s" % to_native(e)
                )
        except (OSError, ValueError, UnsupportedAlgorithm) as e:
            self.module.fail_json(
                msg="The following error occurred while loading the provided private_key: %s" % to_native(e)
            )
        try:
            with open(self.certificate_path, 'rb') as cert_file:
                cert = cert_loader(
                    cert_file.read(),
                    backend=backend
                )
        except (OSError, ValueError, UnsupportedAlgorithm) as e:
            self.module.fail_json(
                msg="The following error occurred while loading the provided certificate: %s" % to_native(e)
            )

        if self.password:
            encryption = BestAvailableEncryption(to_bytes(self.password))
        else:
            encryption = NoEncryption()

        pkcs12_bundle = serialize_key_and_certificates(
            name=to_bytes(self.name),
            key=private_key,
            cert=cert,
            cas=None,
            encryption_algorithm=encryption
        )

        with open(keystore_p12_path, 'wb') as p12_file:
            p12_file.write(pkcs12_bundle)

        self.result.update(msg="PKCS#12 bundle created by cryptography backend")

    def openssl_create_pkcs12_bundle(self, keystore_p12_path):
        export_p12_cmd = [self.openssl_bin, "pkcs12", "-export", "-name", self.name, "-in", self.certificate_path,
                          "-inkey", self.private_key_path, "-out", keystore_p12_path, "-passout", "stdin"]

        # when keypass is provided, add -passin
        cmd_stdin = ""
        if self.keypass:
            export_p12_cmd.append("-passin")
            export_p12_cmd.append("stdin")
            cmd_stdin = "%s\n" % self.keypass
        cmd_stdin += "%s\n%s" % (self.password, self.password)

        (rc, export_p12_out, export_p12_err) = self.module.run_command(
            export_p12_cmd, data=cmd_stdin, environ_update=None, check_rc=False
        )

        self.result = dict(msg=export_p12_out, cmd=export_p12_cmd, rc=rc)
        if rc != 0:
            self.result['err'] = export_p12_err
            self.module.fail_json(**self.result)

    def create(self):
        """Create the keystore, or replace it with a rollback in case of
           keytool failure.
        """
        if self.module.check_mode:
            self.result['changed'] = True
            return self.result

        keystore_p12_path = create_path()
        self.module.add_cleanup_file(keystore_p12_path)

        if self.ssl_backend == 'cryptography':
            self.cryptography_create_pkcs12_bundle(keystore_p12_path)
        else:
            self.openssl_create_pkcs12_bundle(keystore_p12_path)

        if self.keystore_type == 'pkcs12':
            # Preserve properties of the destination file, if any.
            self.module.atomic_move(keystore_p12_path, self.keystore_path)
            self.update_permissions()
            self.result['changed'] = True
            return self.result

        import_keystore_cmd = [self.keytool_bin, "-importkeystore",
                               "-destkeystore", self.keystore_path,
                               "-srckeystore", keystore_p12_path,
                               "-srcstoretype", "pkcs12",
                               "-alias", self.name,
                               "-noprompt"]

        if self.keystore_type == 'jks':
            keytool_help = self.module.run_command([self.keytool_bin, '-importkeystore', '-help'])
            if '-deststoretype' in keytool_help[1] + keytool_help[2]:
                import_keystore_cmd.insert(4, "-deststoretype")
                import_keystore_cmd.insert(5, self.keystore_type)

        keystore_backup = None
        if self.exists():
            keystore_backup = self.keystore_path + '.tmpbak'
            # Preserve properties of the source file
            self.module.preserved_copy(self.keystore_path, keystore_backup)
            os.remove(self.keystore_path)

        (rc, import_keystore_out, import_keystore_err) = self.module.run_command(
            import_keystore_cmd, data='%s\n%s\n%s' % (self.password, self.password, self.password), check_rc=False
        )

        self.result = dict(msg=import_keystore_out, cmd=import_keystore_cmd, rc=rc)

        # keytool may return 0 whereas the keystore has not been created.
        if rc != 0 or not self.exists():
            if keystore_backup is not None:
                self.module.preserved_copy(keystore_backup, self.keystore_path)
                os.remove(keystore_backup)
            self.result['err'] = import_keystore_err
            return self.module.fail_json(**self.result)

        self.update_permissions()
        if keystore_backup is not None:
            os.remove(keystore_backup)
        self.result['changed'] = True
        return self.result

    def exists(self):
        return os.path.exists(self.keystore_path)


# Utility functions
def create_path():
    dummy, tmpfile = tempfile.mkstemp()
    os.remove(tmpfile)
    return tmpfile


def create_file(content):
    tmpfd, tmpfile = tempfile.mkstemp()
    with os.fdopen(tmpfd, 'w') as f:
        f.write(content)
    return tmpfile


def hex_decode(s):
    if PY2:
        return s.decode('hex')
    return s.hex()


def main():
    choose_between = (['certificate', 'certificate_path'],
                      ['private_key', 'private_key_path'])

    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type='str', required=True),
            dest=dict(type='path', required=True),
            certificate=dict(type='str', no_log=True),
            certificate_path=dict(type='path'),
            private_key=dict(type='str', no_log=True),
            private_key_path=dict(type='path', no_log=False),
            private_key_passphrase=dict(type='str', no_log=True),
            password=dict(type='str', required=True, no_log=True),
            ssl_backend=dict(type='str', default='openssl', choices=['openssl', 'cryptography']),
            keystore_type=dict(type='str', choices=['jks', 'pkcs12']),
            force=dict(type='bool', default=False),
        ),
        required_one_of=choose_between,
        mutually_exclusive=choose_between,
        supports_check_mode=True,
        add_file_common_args=True,
    )
    module.run_command_environ_update = dict(LANG='C', LC_ALL='C', LC_MESSAGES='C')

    result = dict()
    jks = JavaKeystore(module)

    if jks.exists():
        if module.params['force'] or jks.cert_changed():
            result = jks.create()
        else:
            result['changed'] = jks.update_permissions()
    else:
        result = jks.create()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
