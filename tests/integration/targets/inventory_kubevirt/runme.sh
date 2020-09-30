#!/usr/bin/env bash

if [[ $(python --version 2>&1) =~ 2\.6 ]]
  then
    echo "Openshift client is not supported on Python 2.6"
    exit 0
fi

set -eux

uname -a
if [[ $(uname -a) =~ FreeBSD\ 12\.0-RELEASE ]]
  then
    # On FreeBSD 12.0 images, upgrade setuptools to avoid error with multidict
    # This is a bug in pip, which happens because the old setuptools from outside
    # the venv leaks into the venv (https://github.com/pypa/pip/issues/6264).
    # Since it is not fixed in latest pip (which is available in the venv), we
    # need to upgrade setuptools outside the venv.
    pip3 install --upgrade setuptools
fi

source virtualenv.sh
python --version
pip --version
pip show setuptools
pip install openshift -c constraints.txt

./server.py &

cleanup() {
  kill -9 "$(jobs -p)"
}

trap cleanup INT TERM EXIT

# Fake auth file
mkdir -p ~/.kube/
cat <<EOF > ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    insecure-skip-tls-verify: true
    server: http://localhost:12345
  name: development
contexts:
- context:
    cluster: development
    user: developer
  name: dev-frontend
current-context: dev-frontend
kind: Config
preferences: {}
users:
- name: developer
  user:
    token: ZDNg7LzSlp8a0u0fht_tRnPMTOjxqgJGCyi_iy0ecUw
EOF

#################################################
#   RUN THE PLUGIN
#################################################

# run the plugin second
export ANSIBLE_INVENTORY_ENABLED=community.general.kubevirt
export ANSIBLE_INVENTORY=test.kubevirt.yml

cat << EOF > "$OUTPUT_DIR/test.kubevirt.yml"
plugin: community.general.kubevirt
connections:
  - namespaces:
      - default
EOF

ANSIBLE_JINJA2_NATIVE=1 ansible-inventory -vvvv -i "$OUTPUT_DIR/test.kubevirt.yml" --list --output="$OUTPUT_DIR/plugin.out"

#################################################
#   DIFF THE RESULTS
#################################################

./inventory_diff.py "$(pwd)/test.out" "$OUTPUT_DIR/plugin.out"
