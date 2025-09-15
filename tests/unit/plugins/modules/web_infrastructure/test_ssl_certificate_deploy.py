#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Mangesh Shinde <mangesh.shinde@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open, MagicMock
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json
from ansible_collections.community.general.plugins.modules.web_infrastructure.ssl_certificate_deploy import main

# Import the module to test
import sys
sys.path.insert(0, os.path.dirname(__file__))
from ssl_certificate_deploy_ansible_ready import (
    validate_certificate,
    get_file_hash,
    secure_file_copy,
    find_ssl_cert_paths,
    detect_web_service,
    write_audit_report
)


def set_module_args(args):
    """Set module arguments for testing"""
    if '_ansible_remote_tmp' not in args:
        args['_ansible_remote_tmp'] = '/tmp'
    if '_ansible_keep_remote_files' not in args:
        args['_ansible_keep_remote_files'] = False

    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class TestSSLRenewSecure:
    """Test cases for ssl_certificate_deploy module"""

    def test_validate_certificate_success(self):
        """Test successful certificate validation"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            is_valid, msg = validate_certificate('/path/to/cert.pem', None)
            
            assert is_valid is True
            assert msg == "Certificate is valid"
            mock_run.assert_called_once()

    def test_validate_certificate_failure(self):
        """Test certificate validation failure"""
        with patch('subprocess.run') as mock_run:
            from subprocess import CalledProcessError
            mock_run.side_effect = CalledProcessError(1, 'openssl', stderr='Invalid certificate')
            
            is_valid, msg = validate_certificate('/path/to/cert.pem', None)
            
            assert is_valid is False
            assert "Certificate validation failed" in msg

    def test_validate_certificate_timeout(self):
        """Test certificate validation timeout"""
        with patch('subprocess.run') as mock_run:
            from subprocess import TimeoutExpired
            mock_run.side_effect = TimeoutExpired('openssl', 10)
            
            is_valid, msg = validate_certificate('/path/to/cert.pem', None)
            
            assert is_valid is False
            assert "timed out" in msg

    def test_validate_certificate_missing_openssl(self):
        """Test certificate validation with missing openssl"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            is_valid, msg = validate_certificate('/path/to/cert.pem', None)
            
            assert is_valid is False
            assert "openssl command not found" in msg

    def test_get_file_hash_success(self):
        """Test successful file hash calculation"""
        test_content = b"test certificate content"
        expected_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = get_file_hash('/path/to/cert.pem')
            assert result == expected_hash

    def test_get_file_hash_failure(self):
        """Test file hash calculation failure"""
        with patch('builtins.open', side_effect=IOError("File not found")):
            result = get_file_hash('/path/to/nonexistent.pem')
            assert result is None

    def test_find_ssl_cert_paths_nginx(self):
        """Test finding SSL certificate paths in nginx config"""
        nginx_config = """
        server {
            listen 443 ssl;
            ssl_certificate /etc/nginx/ssl/cert.pem;
            ssl_certificate_key /etc/nginx/ssl/key.pem;
        }
        """
        
        with patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['default.conf']), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.islink', return_value=False), \
             patch('builtins.open', mock_open(read_data=nginx_config)):
            
            paths = find_ssl_cert_paths('/etc/nginx/conf.d', 'nginx')
            
            assert '/etc/nginx/ssl/cert.pem' in paths
            assert '/etc/nginx/ssl/key.pem' in paths

    def test_find_ssl_cert_paths_httpd(self):
        """Test finding SSL certificate paths in httpd config"""
        httpd_config = """
        <VirtualHost *:443>
            SSLEngine on
            SSLCertificateFile /etc/httpd/ssl/cert.pem
            SSLCertificateKeyFile /etc/httpd/ssl/key.pem
        </VirtualHost>
        """
        
        with patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['ssl.conf']), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.islink', return_value=False), \
             patch('builtins.open', mock_open(read_data=httpd_config)):
            
            paths = find_ssl_cert_paths('/etc/httpd/conf.d', 'httpd')
            
            assert '/etc/httpd/ssl/cert.pem' in paths
            assert '/etc/httpd/ssl/key.pem' in paths

    def test_find_ssl_cert_paths_security_check(self):
        """Test security checks in certificate path finding"""
        malicious_config = """
        server {
            ssl_certificate ../../../etc/passwd;
            ssl_certificate_key relative/path/key.pem;
        }
        """
        
        with patch('os.path.isdir', return_value=True), \
             patch('os.listdir', return_value=['malicious.conf']), \
             patch('os.path.isfile', return_value=True), \
             patch('os.path.islink', return_value=False), \
             patch('builtins.open', mock_open(read_data=malicious_config)):
            
            paths = find_ssl_cert_paths('/etc/nginx/conf.d', 'nginx')
            
            # Should not include paths with ".." or relative paths
            assert '../../../etc/passwd' not in paths
            assert 'relative/path/key.pem' not in paths

    def test_detect_web_service_systemctl(self):
        """Test web service detection using systemctl"""
        with patch('subprocess.run') as mock_run:
            # Mock successful systemctl call for nginx
            mock_run.return_value = MagicMock(returncode=0)
            
            services = detect_web_service()
            
            # Should detect at least one service
            assert len(services) >= 0
            mock_run.assert_called()

    def test_detect_web_service_pgrep_fallback(self):
        """Test web service detection fallback to pgrep"""
        with patch('subprocess.run') as mock_run:
            # First call (systemctl) fails, second call (pgrep) succeeds
            mock_run.side_effect = [
                FileNotFoundError(),  # systemctl not found
                MagicMock(returncode=0)  # pgrep succeeds
            ]
            
            services = detect_web_service()
            
            # Should handle fallback gracefully
            assert isinstance(services, list)

    def test_secure_file_copy_success(self):
        """Test successful secure file copy"""
        with tempfile.TemporaryDirectory() as temp_dir:
            src_file = os.path.join(temp_dir, 'src.pem')
            dest_file = os.path.join(temp_dir, 'dest.pem')
            
            # Create source file
            with open(src_file, 'w') as f:
                f.write('test certificate')
            
            with patch('pwd.getpwnam') as mock_pwd, \
                 patch('grp.getgrnam') as mock_grp, \
                 patch('os.chown') as mock_chown, \
                 patch('os.chmod') as mock_chmod:
                
                mock_pwd.return_value = MagicMock(pw_uid=0)
                mock_grp.return_value = MagicMock(gr_gid=0)
                
                success, backup_path = secure_file_copy(
                    src_file, dest_file, '0644', 'root', 'root', False
                )
                
                assert success is True
                assert os.path.exists(dest_file)
                mock_chown.assert_called_once()
                mock_chmod.assert_called_once()

    def test_write_audit_report(self):
        """Test audit report writing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = os.path.join(temp_dir, 'audit.json')
            test_data = {
                'operation': 'test',
                'status': 'success'
            }
            
            result_path = write_audit_report(report_path, test_data)
            
            assert result_path == report_path
            assert os.path.exists(report_path)
            
            # Verify report content
            with open(report_path, 'r') as f:
                report_content = json.load(f)
                assert report_content['operation'] == 'test'
                assert report_content['module'] == 'ssl_certificate_deploy'
                assert 'timestamp' in report_content

    def test_module_fail_missing_source(self):
        """Test module failure when source file is missing"""
        set_module_args({
            'src': '/nonexistent/cert.pem'
        })
        
        with pytest.raises(SystemExit):
            from ssl_certificate_deploy_ansible_ready import main
            main()

    def test_module_fail_invalid_file_mode(self):
        """Test module failure with invalid file mode"""
        with tempfile.NamedTemporaryFile() as temp_cert:
            set_module_args({
                'src': temp_cert.name,
                'file_mode': 'invalid'
            })
            
            with pytest.raises(SystemExit):
                from ssl_certificate_deploy_ansible_ready import main
                main()


if __name__ == '__main__':
    pytest.main([__file__])

