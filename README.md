# Community General Collection

[![Run Status](https://api.shippable.com/projects/5e664a167c32620006c9fa50/badge?branch=main)](https://app.shippable.com/github/ansible-collections/community.general/dashboard)
[![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.general)](https://codecov.io/gh/ansible-collections/community.general)

This repo contains the `community.general` Ansible Collection. The collection includes many modules and plugins supported by Ansible community which are not part of more specialized community collections.

You can find [documentation for this collection on the Ansible docs site](https://docs.ansible.com/ansible/latest/collections/community/general/).

## Tested with Ansible

Tested with the current Ansible 2.9 and 2.10 releases and the current development version of Ansible. Ansible versions before 2.9.10 are not supported.

## External requirements

Some modules and plugins require external libraries. Please check the requirements for each plugin or module you use in the documentation to find out which requirements are needed.

## Included content

Please check the included content on the [Ansible Galaxy page for this collection](https://galaxy.ansible.com/community/general) or the [documentation on the Ansible docs site](https://docs.ansible.com/ansible/latest/collections/community/general/).

## Using this collection

Before using the General community collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install community.general

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: community.general
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

If you want to develop new content for this collection or improve what is already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATH`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.

For example, if you are working in the `~/dev` directory:

```
cd ~/dev
git clone git@github.com:ansible-collections/community.general.git collections/ansible_collections/community/general
export COLLECTIONS_PATH=$(pwd)/collections:$COLLECTIONS_PATH
```

You can find more information in the [developer guide for collections](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections), and in the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html).

### Running tests

See [here](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#testing-collections).

### Communication

We have a dedicated Working Group for Ansible development.

You can find other people interested on the following Freenode IRC channels -
- `#ansible` - For general use questions and support.
- `#ansible-devel` - For discussions on developer topics and code related to features or bugs.
- `#ansible-community` - For discussions on community topics and community meetings.

For more information about communities, meetings and agendas see [Community Wiki](https://github.com/ansible/community/wiki/Community).

For more information about [communication](https://docs.ansible.com/ansible/latest/community/communication.html)

### Publishing New Version

Basic instructions without release branches:

1. Create `changelogs/fragments/<version>.yml` with `release_summary:` section (which must be a string, not a list).
2. Run `antsibull-changelog release --collection-flatmap yes`
3. Make sure `CHANGELOG.rst` and `changelogs/changelog.yaml` are added to git, and the deleted fragments have been removed.
4. Tag the commit with `<version>`. Push changes and tag to the main repository.

## Release notes

See the [changelog](https://github.com/ansible-collections/community.general/blob/main/CHANGELOG.rst).

## Roadmap

See [this issue](https://github.com/ansible-collections/community.general/issues/582) for information on releasing, versioning and deprecation.

In general, we plan to release a major version every six months, and minor versions every two months. Major versions can contain breaking changes, while minor versions only contain new features and bugfixes.

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
