# Architecture and Supported Versions

- Ansible architecture prescribes a controller node, where the Ansible CLI commands are executed, and target nodes, where the Ansible tasks are executed.
- Plugins types:
  - doc_fragments are not executed
  - modules and module_utils are executed in the target nodes
  - all other types are executed in the controller node

- Check the description of issue 11482 for the supported versions of `community.general`
  and the corresponding supported versions of `ansible-core` and Python for each one.
