#!/usr/bin/env bash

set -eux

ansible localhost -m include_role -a 'name=../setup_paramiko'

./test.sh
