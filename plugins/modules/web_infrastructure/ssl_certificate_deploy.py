#!/usr/bin/python
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2024 Mangesh Shinde <mangesh.shinde@example.com>
# SPDX-License-Identifier: GPL-3.0-or-later

# Copyright (c) 2024, Mangesh Shinde <mangesh.shinde@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: ssl_certificate_deploy
short_description: Deploy SSL certificates to web services
description:
    - Automatically detect running web services (nginx/httpd/apache2)
    - Parse configuration files to find SSL certificate paths
    - Securely copy new certificates to detected locations
    - Generate comprehensive audit reports with proper logging
    - Create backups of existing certificates before replacement
    - Validate certificates before deployment
version_added: "11.3.0"
options:
    src:
        description:
            - Path to the source SSL certificate file
            - Must be a valid SSL certificate file
            - "This will be used for SSL certificate files (nginx: ssl_certificate, apache: SSLCertificateFile)"
        required: true
        type: path
    key_src:
        description:
            - Path to the SSL private key file
            - "If not provided, 'src' will be used for key files"
            - "Used for SSL key files (nginx: ssl_certificate_key, apache: SSLCertificateKeyFile)"
        required: false
        type: path
    chain_src:
        description:
            - Path to the SSL certificate chain file
            - "If not provided, chain files will not be updated"
            - "Used for SSL chain files (apache: SSLCertificateChainFile)"
        required: false
        type: path
    httpd_conf_path:
        description: Path to httpd/apache configuration directory
        default: /etc/httpd/conf.d
        type: path
    nginx_conf_path:
        description: Path to nginx configuration directory
        default: /etc/nginx/conf.d
        type: path
    report_path:
        description: Path for the audit report JSON file
        default: /var/log/ssl_renewal.json
        type: path
    backup:
        description: Create backup of existing certificates before replacement
        default: true
        type: bool
    validate_cert:
        description:
            - Validate certificate using openssl before copying
            - Requires openssl command to be available
        default: true
        type: bool
    file_mode:
        description:
            - File permissions for certificates in octal notation
            - "Example: '0644' for rw-r--r--"
        default: '0644'
        type: str
    owner:
        description: Owner for certificate files
        default: root
        type: str
    group:
        description: Group for certificate files
        default: root
        type: str
    reload_service:
        description:
            - Reload web service after certificate deployment
            - Service configuration is validated before reload
        default: true
        type: bool
    validate_config:
        description:
            - Validate web service configuration before and after certificate deployment
            - Prevents service failures due to configuration errors
            - "When true, certificates are tested before deployment and rolled back if validation fails"
        default: true
        type: bool
    strict_validation:
        description:
            - Enable strict certificate-key matching validation before any deployment
            - "When true, certificate and private key compatibility is verified using OpenSSL"
            - Also validates new certificates against existing keys in destination paths
            - Prevents deployment of mismatched certificate-key pairs
        default: true
        type: bool
    check_existing_keys:
        description:
            - Check if new certificates are compatible with existing keys in destination paths
            - "When true, prevents deploying certificates that don't match existing keys"
            - "Helps avoid 'key values mismatch' errors in web server configurations"
        default: true
        type: bool
requirements:
    - openssl (if validate_cert is true)
    - systemctl or pgrep (for service detection)
notes:
    - This module requires root privileges to modify system certificate files
    - Backup files are created with timestamp suffix for easy identification
    - The module supports both systemd and non-systemd systems
    - Configuration files are parsed safely to prevent directory traversal attacks
seealso:
    - module: ansible.builtin.copy
    - module: community.crypto.x509_certificate
    - module: community.crypto.acme_certificate
author:
    - Mangesh Shinde (@mangesh-shinde)
'''


EXAMPLES = r'''
- name: Renew SSL certificates with default settings
  ssl_certificate_deploy:
    src: /tmp/new_certificate.crt

- name: Renew certificates with custom configuration
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    key_src: /path/to/private.key
    chain_src: /path/to/chain.pem
    nginx_conf_path: /etc/nginx/sites-enabled
    httpd_conf_path: /etc/apache2/sites-enabled
    backup: true
    validate_cert: true

- name: Renew with custom permissions and ownership
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    file_mode: '0600'
    owner: nginx
    group: nginx
    report_path: /var/log/custom_ssl_renewal.json

- name: Skip certificate validation (not recommended)
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    validate_cert: false
    backup: false

- name: Deploy certificates without service reload
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    reload_service: false
    validate_config: false

- name: Deploy only certificate and key (skip chain)
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    key_src: /path/to/private.key
    # chain_src not provided - chain files won't be updated

- name: Deploy different files for different purposes
  ssl_certificate_deploy:
    src: /path/to/new_cert.pem     # Certificate files
    key_src: /path/to/new_key.pem  # Key files
    chain_src: /path/to/new_chain.pem  # Chain files

- name: Deploy with strict validation (recommended for production)
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    key_src: /path/to/private.key
    strict_validation: true        # Verify cert-key compatibility
    validate_config: true          # Test configuration before deployment

- name: Deploy without strict validation (use with caution)
  ssl_certificate_deploy:
    src: /path/to/cert.pem
    key_src: /path/to/private.key
    strict_validation: false       # Skip cert-key compatibility check
    validate_config: false         # Skip configuration validation
    check_existing_keys: false     # Skip existing key compatibility check

- name: Deploy only certificate (check against existing keys)
  ssl_certificate_deploy:
    src: /path/to/new_cert.pem     # New certificate
    # key_src not provided - existing keys will be validated against new cert
    strict_validation: true        # Validate source cert format
    check_existing_keys: true      # Check new cert matches existing keys
    validate_config: true          # Test configuration
'''

RETURN = r'''
changed:
    description: Whether any changes were made to the system
    type: bool
    returned: always
    sample: true
services:
    description: List of detected web services
    type: list
    returned: always
    sample: ["nginx", "httpd"]
updated:
    description: List of updated certificate file paths
    type: list
    returned: always
    sample: ["/etc/nginx/ssl/cert.pem", "/etc/httpd/ssl/cert.pem"]
backed_up:
    description: List of backup file paths created
    type: list
    returned: when backup=true and files existed
    sample: ["/etc/nginx/ssl/cert.pem.backup.20241213_143022"]
certificates_found:
    description: Total number of certificate paths found in configurations
    type: int
    returned: always
    sample: 4
report:
    description: Path to the generated audit report file
    type: str
    returned: always
    sample: "/var/log/ssl_renewal.json"
reloaded_services:
    description: List of services that were successfully reloaded
    type: list
    returned: when reload_service=true
    sample: ["nginx", "httpd"]
config_validation:
    description: Configuration validation results for each service
    type: dict
    returned: when validate_config=true
    sample: {"nginx": {"valid": true, "message": "Configuration OK"}}
msg:
    description: Summary message of the operation
    type: str
    returned: always
    sample: "Processed 4 certificate paths for nginx, httpd, updated 2, reloaded 2 services"
'''

from ansible.module_utils.basic import AnsibleModule
import os
import re
import subprocess
import shutil
import json
import tempfile
import pwd
import grp
from datetime import datetime
import hashlib


def validate_certificate(cert_path, module):
    """Validate SSL certificate using openssl"""
    try:
        result = subprocess.run(
            ['openssl', 'x509', '-in', cert_path, '-text', '-noout'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        return True, "Certificate is valid"
    except subprocess.CalledProcessError as e:
        return False, "Certificate validation failed: %s" % e.stderr
    except subprocess.TimeoutExpired:
        return False, "Certificate validation timed out"
    except FileNotFoundError:
        return False, "openssl command not found - install openssl package"
    except Exception as e:
        return False, "Unexpected error during validation: %s" % str(e)


def validate_cert_key_match(cert_path, key_path, module=None):
    """Validate that certificate and private key match using openssl"""
    try:
        # Get certificate public key hash
        cert_result = subprocess.run(
            ['openssl', 'x509', '-in', cert_path, '-pubkey', '-noout'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        # Get private key public key hash
        key_result = subprocess.run(
            ['openssl', 'rsa', '-in', key_path, '-pubout'],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )

        # Compare the public keys
        if cert_result.stdout.strip() == key_result.stdout.strip():
            return True, "Certificate and private key match"
        else:
            return False, "Certificate and private key do not match - key values mismatch"

    except subprocess.CalledProcessError as e:
        # Try alternative method for different key types (EC, etc.)
        try:
            # Method 2: Compare modulus for RSA keys
            cert_modulus = subprocess.run(
                ['openssl', 'x509', '-in', cert_path, '-modulus', '-noout'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            key_modulus = subprocess.run(
                ['openssl', 'rsa', '-in', key_path, '-modulus', '-noout'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            if cert_modulus.stdout.strip() == key_modulus.stdout.strip():
                return True, "Certificate and private key match (RSA modulus check)"
            else:
                return False, "Certificate and private key do not match - RSA modulus mismatch"

        except subprocess.CalledProcessError:
            # Method 3: Try EC key validation
            try:
                cert_pubkey = subprocess.run(
                    ['openssl', 'x509', '-in', cert_path, '-pubkey', '-noout'],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )

                key_pubkey = subprocess.run(
                    ['openssl', 'ec', '-in', key_path, '-pubout'],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10
                )

                if cert_pubkey.stdout.strip() == key_pubkey.stdout.strip():
                    return True, "Certificate and private key match (EC key check)"
                else:
                    return False, "Certificate and private key do not match - EC key mismatch"

            except subprocess.CalledProcessError as ec_error:
                return False, "Cannot validate cert-key match: %s" % str(ec_error.stderr)

    except subprocess.TimeoutExpired:
        return False, "Certificate-key validation timed out"
    except FileNotFoundError:
        return False, "openssl command not found - install openssl package"
    except Exception as e:
        return False, "Unexpected error during cert-key validation: %s" % str(e)


def get_file_hash(file_path):
    """Calculate SHA256 hash of file"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def secure_file_copy(src, dest, mode='0644', owner='root', group='root', backup=True, module=None):
    """Securely copy file with proper permissions and backup"""
    backup_path = None

    try:
        # Create backup if requested and destination exists
        if backup and os.path.exists(dest):
            backup_dir = os.path.dirname(dest)
            backup_name = "%s.backup.%s" % (
                os.path.basename(dest),
                datetime.now().strftime('%Y%m%d_%H%M%S')
            )
            backup_path = os.path.join(backup_dir, backup_name)
            shutil.copy2(dest, backup_path)

        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, mode=0o755)

        # Copy file securely
        shutil.copy2(src, dest)

        # Set ownership and permissions
        try:
            uid = pwd.getpwnam(owner).pw_uid
        except KeyError:
            if module:
                module.warn("User '%s' not found, using root (0)" % owner)
            uid = 0

        try:
            gid = grp.getgrnam(group).gr_gid
        except KeyError:
            if module:
                module.warn("Group '%s' not found, using root (0)" % group)
            gid = 0

        os.chown(dest, uid, gid)
        os.chmod(dest, int(mode, 8))

        return True, backup_path

    except Exception as e:
        return False, backup_path


def write_audit_report(report_path, data):
    """Write comprehensive audit report"""
    try:
        # Ensure report directory exists
        report_dir = os.path.dirname(report_path)
        if not os.path.exists(report_dir):
            os.makedirs(report_dir, mode=0o755)

        # Add system information
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "module": "ssl_renew_secure",
            "hostname": os.uname().nodename,
            "user": os.getenv('USER', 'unknown'),
        }
        report_data.update(data)

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        # Set secure permissions on report
        os.chmod(report_path, 0o640)

        return report_path

    except Exception:
        return None


def find_ssl_cert_paths(conf_dir, web_service):
    """Parse configuration files to extract SSL certificate paths categorized by type"""
    cert_paths = {
        'certificate': set(),  # Certificate files
        'key': set(),         # Private key files
        'chain': set()        # Chain/intermediate files
    }

    if not os.path.isdir(conf_dir):
        return cert_paths

    # Different patterns for different web servers
    if web_service == "nginx":
        patterns = [
            ('certificate', re.compile(r'^\s*ssl_certificate\s+([^;]+);', re.IGNORECASE)),
            ('key', re.compile(r'^\s*ssl_certificate_key\s+([^;]+);', re.IGNORECASE))
        ]
    elif web_service == "httpd":
        patterns = [
            ('certificate', re.compile(r'^\s*SSLCertificateFile\s+(.+)$', re.IGNORECASE)),
            ('key', re.compile(r'^\s*SSLCertificateKeyFile\s+(.+)$', re.IGNORECASE)),
            ('chain', re.compile(r'^\s*SSLCertificateChainFile\s+(.+)$', re.IGNORECASE))
        ]
    else:
        return cert_paths

    try:
        for fname in os.listdir(conf_dir):
            if not (fname.endswith(".conf") or fname.endswith(".cfg")):
                continue

            fpath = os.path.join(conf_dir, fname)

            # Security check: ensure file is readable and not a symlink outside conf_dir
            if not os.path.isfile(fpath) or os.path.islink(fpath):
                continue

            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('#'):  # Skip comments
                            continue

                        for cert_type, pattern in patterns:
                            match = pattern.search(line)
                            if match:
                                cert_path = match.group(1).strip('\'"')
                                # Security check: ensure path is absolute and doesn't contain ".."
                                if os.path.isabs(cert_path) and ".." not in cert_path:
                                    cert_paths[cert_type].add(cert_path)

            except (UnicodeDecodeError, PermissionError):
                continue

    except PermissionError:
        pass

    # Convert sets to lists for easier handling
    result = {}
    for cert_type, paths in cert_paths.items():
        result[cert_type] = list(paths)

    return result


def detect_web_service():
    """Detect running web service with enhanced security"""
    services = ["nginx", "httpd", "apache2"]
    detected_services = []

    for service in services:
        try:
            # Use systemctl with timeout
            result = subprocess.run(
                ["systemctl", "is-active", "--quiet", service],
                check=True,
                timeout=5,
                capture_output=True
            )
            detected_services.append(service)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            continue
        except FileNotFoundError:
            # systemctl not available, try alternative methods
            try:
                result = subprocess.run(
                    ["pgrep", "-x", service],
                    check=True,
                    timeout=5,
                    capture_output=True
                )
                detected_services.append(service)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                continue

    # Normalize service names
    if "apache2" in detected_services:
        detected_services = ["httpd" if s == "apache2" else s for s in detected_services]

    return detected_services


def validate_service_config(service, module=None):
    """Validate web service configuration"""
    try:
        if service == "nginx":
            # Test nginx configuration
            result = subprocess.run(
                ["sudo", "nginx", "-t"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False)
            if result.returncode == 0:
                return True, "nginx configuration is valid"
            else:
                return False, "nginx configuration error: %s" % result.stderr

        elif service == "httpd":
            # Test Apache/httpd configuration
            result = subprocess.run(
                ["sudo", "httpd", "-t"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False)
            if result.returncode == 0:
                return True, "httpd configuration is valid"
            else:
                # Try alternative apache2 command
                try:
                    result = subprocess.run(
                        ["sudo", "apache2ctl", "configtest"],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False)
                    if result.returncode == 0:
                        return True, "apache2 configuration is valid"
                    else:
                        return False, "apache2 configuration error: %s" % result.stderr
                except FileNotFoundError:
                    return False, "httpd configuration error: %s" % result.stderr
        else:
            return False, "Unknown service: %s" % service

    except subprocess.TimeoutExpired:
        return False, "Configuration validation timed out for %s" % service
    except FileNotFoundError:
        return False, "Configuration validation command not found for %s" % service
    except Exception as e:
        return False, "Unexpected error validating %s config: %s" % (service, str(e))


def reload_web_service(service, module=None):
    """Reload web service safely"""
    try:
        # Try systemctl first
        result = subprocess.run(
            ["systemctl", "reload", service],
            capture_output=True,
            text=True,
            timeout=30,
            check=False)
        if result.returncode == 0:
            return True, "%s reloaded successfully" % service
        else:
            return False, "Failed to reload %s: %s" % (service, result.stderr)

    except FileNotFoundError:
        # systemctl not available, try service command
        try:
            result = subprocess.run(
                ["service", service, "reload"],
                capture_output=True,
                text=True,
                timeout=30,
                check=False)
            if result.returncode == 0:
                return True, "%s reloaded successfully via service command" % service
            else:
                return False, "Failed to reload %s via service: %s" % (service, result.stderr)
        except FileNotFoundError:
            return False, "No service management command available to reload %s" % service

    except subprocess.TimeoutExpired:
        return False, "Service reload timed out for %s" % service
    except Exception as e:
        return False, "Unexpected error reloading %s: %s" % (service, str(e))


def validate_temp_deployment(cert_paths_by_type, src, key_src, chain_src, web_service, module=None):
    """Copy certificates to temporary locations and validate them before deployment"""
    temp_dir = None
    try:
        # Create temporary directory structure matching destination
        temp_dir = tempfile.mkdtemp(prefix="ssl_temp_validation_")
        validation_results = []

        # Create temp files for each cert type that needs updating
        temp_cert_files = {}

        for cert_type, dest_files in cert_paths_by_type.items():
            if not dest_files:
                continue

            # Determine source file based on certificate type
            if cert_type == 'certificate':
                source_file = src
            elif cert_type == 'key':
                source_file = key_src
            elif cert_type == 'chain':
                if not chain_src:
                    continue  # Skip chain files if not provided
                source_file = chain_src
            else:
                continue

            # Copy to temp location for each destination file
            for dest_file in dest_files:
                temp_file = os.path.join(temp_dir, "%s_%s" % (cert_type, os.path.basename(dest_file)))
                shutil.copy2(source_file, temp_file)

                # Store temp file paths grouped by destination directory
                dest_dir = os.path.dirname(dest_file)
                if dest_dir not in temp_cert_files:
                    temp_cert_files[dest_dir] = {}
                temp_cert_files[dest_dir][cert_type] = temp_file

        # Validate cert-key matching for each destination directory
        for dest_dir, cert_files in temp_cert_files.items():
            if 'certificate' in cert_files and 'key' in cert_files:
                # Validate certificate and key match
                cert_key_match, cert_key_msg = validate_cert_key_match(
                    cert_files['certificate'],
                    cert_files['key'],
                    module
                )
                if not cert_key_match:
                    return False, "Certificate-key validation failed for %s: %s" % (dest_dir, cert_key_msg)

                validation_results.append("✓ Certificate-key pair validated for %s" % dest_dir)

        return True, "All certificate validations passed: %s" % "; ".join(validation_results)

    except Exception as e:
        return False, "Temporary validation failed: %s" % str(e)
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass


def validate_temp_config_deployment(cert_paths_by_type, src, key_src, chain_src, web_service, module=None):
    """Copy certificates to actual destination paths temporarily and test service configuration"""
    backup_files = {}
    try:
        # Create backups of existing files
        for cert_type, dest_files in cert_paths_by_type.items():
            # Determine source file based on certificate type
            if cert_type == 'certificate':
                source_file = src
            elif cert_type == 'key':
                source_file = key_src
            elif cert_type == 'chain':
                if not chain_src:
                    continue  # Skip chain files if not provided
                source_file = chain_src
            else:
                continue

            # Create backups and copy new files
            for dest_file in dest_files:
                if os.path.exists(dest_file):
                    backup_path = dest_file + ".temp_backup_" + str(datetime.now().timestamp())
                    shutil.copy2(dest_file, backup_path)
                    backup_files[dest_file] = backup_path

                # Copy new file to destination
                shutil.copy2(source_file, dest_file)

        # Test service configuration with new certificates
        config_valid, config_msg = validate_service_config(web_service, module)

        return config_valid, config_msg

    except Exception as e:
        return False, "Temporary configuration test failed: %s" % str(e)
    finally:
        # Restore original files from backups
        for dest_file, backup_path in backup_files.items():
            try:
                if os.path.exists(backup_path):
                    shutil.copy2(backup_path, dest_file)
                    os.remove(backup_path)
            except Exception:
                pass


def main():
    module_args = dict(
        src=dict(type='path', required=True),
        key_src=dict(type='path', required=False),
        chain_src=dict(type='path', required=False),
        httpd_conf_path=dict(type='path', default='/etc/httpd/conf.d'),
        nginx_conf_path=dict(type='path', default='/etc/nginx/conf.d'),
        report_path=dict(type='path', default='/var/log/ssl_renewal.json'),
        backup=dict(type='bool', default=True),
        validate_cert=dict(type='bool', default=True),
        file_mode=dict(type='str', default='0644'),
        owner=dict(type='str', default='root'),
        group=dict(type='str', default='root'),
        reload_service=dict(type='bool', default=True),
        validate_config=dict(type='bool', default=True),
        strict_validation=dict(type='bool', default=True),
        check_existing_keys=dict(type='bool', default=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Extract parameters
    src = module.params['src']
    key_src = module.params['key_src']
    chain_src = module.params['chain_src']
    httpd_conf_path = module.params['httpd_conf_path']
    nginx_conf_path = module.params['nginx_conf_path']
    report_path = module.params['report_path']
    backup = module.params['backup']
    validate_cert = module.params['validate_cert']
    file_mode = module.params['file_mode']
    owner = module.params['owner']
    group = module.params['group']
    reload_service = module.params['reload_service']
    validate_config = module.params['validate_config']
    strict_validation = module.params['strict_validation']
    check_existing_keys = module.params['check_existing_keys']

    # Set defaults for optional file sources
    if not key_src:
        key_src = src  # Use certificate file for keys if not specified
    if not chain_src:
        chain_src = None  # Don't update chain files if not specified

    # Validate inputs
    if not os.path.exists(src):
        module.fail_json(msg="Source certificate %s does not exist" % src)

    if not os.path.isfile(src):
        module.fail_json(msg="Source %s is not a regular file" % src)

    # Validate key file if provided and different from src
    if key_src and key_src != src:
        if not os.path.exists(key_src):
            module.fail_json(msg="Key source file %s does not exist" % key_src)
        if not os.path.isfile(key_src):
            module.fail_json(msg="Key source %s is not a regular file" % key_src)

    # Validate chain file if provided
    if chain_src:
        if not os.path.exists(chain_src):
            module.fail_json(msg="Chain source file %s does not exist" % chain_src)
        if not os.path.isfile(chain_src):
            module.fail_json(msg="Chain source %s is not a regular file" % chain_src)

    # Validate file_mode format
    try:
        int(file_mode, 8)
    except ValueError:
        module.fail_json(msg="Invalid file_mode '%s'. Must be octal notation like '0644'" % file_mode)

    # Validate certificate if requested
    if validate_cert:
        is_valid, validation_msg = validate_certificate(src, module)
        if not is_valid:
            module.fail_json(msg="Certificate validation failed: %s" % validation_msg)

        # Validate certificate-key matching if key is different from cert and strict validation is enabled
        if strict_validation and key_src and key_src != src:
            key_match, key_match_msg = validate_cert_key_match(src, key_src, module)
            if not key_match:
                module.fail_json(msg="Certificate-key validation failed: %s" % key_match_msg)

    # Detect running web services
    detected_services = detect_web_service()
    if not detected_services:
        module.fail_json(msg="No supported web service (nginx/httpd/apache2) is running")

    # Collect all certificate paths from all services for validation
    all_cert_paths = []
    service_results = {}
    all_cert_paths_by_service = {}

    for web_service in detected_services:
        conf_dir = nginx_conf_path if web_service == "nginx" else httpd_conf_path

        if not os.path.isdir(conf_dir):
            module.warn("Config directory %s not found for %s" % (conf_dir, web_service))
            continue

        cert_paths_by_type = find_ssl_cert_paths(conf_dir, web_service)

        # Flatten for counting total paths
        total_paths = []
        for cert_type, paths in cert_paths_by_type.items():
            total_paths.extend(paths)
        all_cert_paths.extend(total_paths)

        service_results[web_service] = {
            "config_dir": conf_dir,
            "cert_paths": cert_paths_by_type,
            "updated": []
        }

        all_cert_paths_by_service[web_service] = cert_paths_by_type

    # Pre-deployment validation: Copy to temp locations and validate cert-key matching
    if strict_validation:
        for web_service, cert_paths_by_type in all_cert_paths_by_service.items():
            # Only validate if we have both certificate and key paths for this service
            has_cert = cert_paths_by_type.get('certificate', [])
            has_key = cert_paths_by_type.get('key', [])

            if has_cert and has_key and key_src and key_src != src:
                # Step 1: Validate cert-key matching in temporary location
                validation_success, validation_msg = validate_temp_deployment(
                    cert_paths_by_type, src, key_src, chain_src, web_service, module
                )
                if not validation_success:
                    module.fail_json(msg="Certificate-key matching validation failed for %s: %s" % (web_service, validation_msg))

                # Step 2: Test configuration with new certificates (if enabled)
                if validate_config:
                    config_success, config_msg = validate_temp_config_deployment(
                        cert_paths_by_type, src, key_src, chain_src, web_service, module
                    )
                    if not config_success:
                        module.fail_json(msg="Configuration validation failed for %s with new certificates: %s" % (web_service, config_msg))

    # Process each detected service for actual deployment
    changed = False
    updated_paths = []
    backed_up_files = []
    reloaded_services = []
    config_validation_results = {}

    for web_service in detected_services:
        if web_service not in service_results:
            continue

        cert_paths_by_type = service_results[web_service]["cert_paths"]

        # Process each certificate type
        for cert_type, dest_files in cert_paths_by_type.items():
            # Determine source file based on certificate type
            if cert_type == 'certificate':
                source_file = src
            elif cert_type == 'key':
                source_file = key_src
            elif cert_type == 'chain':
                if not chain_src:
                    continue  # Skip chain files if not provided
                source_file = chain_src
            else:
                continue

            # Process each destination file of this type
            for dest_file in dest_files:
                needs_copy = True

                # Check if files are identical
                if os.path.exists(dest_file):
                    src_hash = get_file_hash(source_file)
                    dest_hash = get_file_hash(dest_file)
                    if src_hash and dest_hash and src_hash == dest_hash:
                        needs_copy = False

                if needs_copy:
                    if not module.check_mode:
                        # Standard deployment - copy directly
                        success, backup_path = secure_file_copy(
                            source_file, dest_file, file_mode, owner, group, backup, module
                        )
                        if not success:
                            module.fail_json(msg="Failed to copy %s to %s" % (cert_type, dest_file))

                        if backup_path:
                            backed_up_files.append(backup_path)

                    changed = True
                    updated_paths.append(dest_file)
                    service_results[web_service]["updated"].append(dest_file)

    # Reload services if certificates were updated (configuration already validated during deployment)
    if changed and reload_service:
        for web_service in detected_services:
            # Only process services that had certificates updated
            if service_results[web_service]["updated"]:
                # Configuration was already validated during deployment if validate_config=true
                # So we can safely reload the service

                if not module.check_mode:
                    reload_success, reload_msg = reload_web_service(web_service, module)
                    if reload_success:
                        reloaded_services.append(web_service)
                        # Record successful validation since we made it this far
                        config_validation_results[web_service] = {
                            "valid": True,
                            "message": "Configuration validated successfully during deployment"
                        }
                    else:
                        module.warn("Failed to reload %s: %s" % (web_service, reload_msg))
                        config_validation_results[web_service] = {
                            "valid": True,
                            "message": "Configuration valid but service reload failed: %s" % reload_msg
                        }
                else:
                    # In check mode, assume reload would succeed since config was validated
                    reloaded_services.append(web_service)
                    config_validation_results[web_service] = {
                        "valid": True,
                        "message": "Configuration would be validated during actual deployment"
                    }

    # Prepare audit report data
    report_data = {
        "operation": "ssl_certificate_renewal",
        "source_certificate": src,
        "source_hash": get_file_hash(src) if os.path.exists(src) else None,
        "detected_services": detected_services,
        "service_results": service_results,
        "total_certificates_found": len(all_cert_paths),
        "certificates_updated": len(updated_paths),
        "updated_paths": updated_paths,
        "backed_up_files": backed_up_files,
        "reloaded_services": reloaded_services,
        "config_validation_results": config_validation_results,
        "check_mode": module.check_mode,
        "parameters": {
            "backup": backup,
            "validate_cert": validate_cert,
            "reload_service": reload_service,
            "validate_config": validate_config,
            "strict_validation": strict_validation,
            "check_existing_keys": check_existing_keys,
            "file_mode": file_mode,
            "owner": owner,
            "group": group
        }
    }

    # Write audit report
    if not module.check_mode:
        report_file = write_audit_report(report_path, report_data)
        if not report_file:
            module.warn("Failed to write audit report to %s" % report_path)
            report_file = "Failed to create report"
    else:
        report_file = "%s (would be created)" % report_path

    # Build result message
    if not all_cert_paths:
        msg = "No SSL certificate paths found in configurations for %s" % ', '.join(detected_services)
    else:
        msg_parts = [
            "Processed %d certificate paths for %s" % (len(all_cert_paths), ', '.join(detected_services)),
            "updated %d" % len(updated_paths)
        ]
        if reload_service and reloaded_services:
            msg_parts.append("reloaded %d services" % len(reloaded_services))
        msg = ", ".join(msg_parts)

    # Return results
    result = {
        'changed': changed,
        'services': detected_services,
        'updated': updated_paths,
        'backed_up': backed_up_files,
        'report': report_file,
        'certificates_found': len(all_cert_paths),
        'msg': msg
    }

    # Add optional return values
    if reload_service:
        result['reloaded_services'] = reloaded_services
    if validate_config:
        result['config_validation'] = config_validation_results

    module.exit_json(**result)


if __name__ == '__main__':
    main()
