[![GitHub Actions CI/CD build status — Collection test suite](https://github.com/ansible-collection-migration/community.general/workflows/Collection%20test%20suite/badge.svg?branch=master)](https://github.com/ansible-collection-migration/community.general/actions?query=workflow%3A%22Collection%20test%20suite%22)
[![License](https://img.shields.io/badge/license-GPL%20v3.0-brightgreen.svg)](LICENSE)

# Ansible Collection: community.general

This collection provides community supported modules and plugins.

## Requirements

- ansible version >= 2.9

## Installation

To install the collection hosted in Galaxy:

```bash
ansible-galaxy collection install community.general
```

To upgrade to the latest version of the collection:

```bash
ansible-galaxy collection install community.general --force
```

## Usage

### Playbooks

To use a module from Vultr collection, please reference the full namespace, collection name, and modules name that you want to use:

```yaml
---
- name: Using the collection
  hosts: localhost
  tasks:
    - community.general.<module>:
      ...
```

Or you can add full namepsace and collecton name in the `collections` element:

```yaml
---
- name: Using the collection
  hosts: localhost
  collections:
    - community.general
  tasks:
    - <module>:
      ...
```

### Plugins

To use a pluign, please reference the full namespace, collection name, and plugins name that you want to use.

For an inventory plugin e.g.:

```yaml
plugin: community.general.<plugin>
```

## Contributing

There are many ways in which you can participate in the project, for example:

- Submit bugs and feature requests, and help us verify as they are checked in.
- Review source code changes.
- Review the documentation and make pull requests for anything from typos to new content.

### Support

Join us on IRC Freenode in channel `#ansible-community`.

## License

GNU General Public License v3.0

See [COPYING](COPYING) to see the full text.
