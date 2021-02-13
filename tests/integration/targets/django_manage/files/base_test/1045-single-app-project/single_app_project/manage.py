#!/usr/bin/env python

from __future__ import absolute_import, division, print_function
__metaclass__ = type

# single_app_project/manage.py
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'single_app_project.core.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
