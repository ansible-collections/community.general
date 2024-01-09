<!-- 
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

# Gitlab integration tests

1. to run integration tests locally, I've setup a podman pod with both gitlab-ee image and the testing image
2. gitlab's related information were taken from [here](https://docs.gitlab.com/ee/install/docker.html), about the variable it needs (hostname, ports, volumes); volumes were pre-made before launching the image
3. image that run integration tests is started with `podman run --rm -it --pod <pod_name> --name <image_name> --network=host --volume <path_to_git_repo>/ansible_community/community.general:<container_path_to>/workspace/ansible_collections/community/general quay.io/ansible/azure-pipelines-test-container:4.0.1`
4. into the testing image, run 
```sh
pip install https://github.com/ansible/ansible/archive/devel.tar.gz --disable-pip-version-check
cd <container_path_to>/workspace/ansible_collections/community/general
ansible-test integration gitlab_label -vvv
```

While debugging with `q` package, open a second terminal and run `podman exec -it <image_name> /bin/bash` and inside it do `tail -f /tmp/q` .
