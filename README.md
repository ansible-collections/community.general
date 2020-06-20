[![Run Status](https://api.shippable.com/projects/5e664a167c32620006c9fa50/badge?branch=master)](https://app.shippable.com/github/ansible-collections/community.general/dashboard) [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.general)](https://codecov.io/gh/ansible-collections/community.general)

# Ansible Collection: community.general

This repo contains the `community.general` Ansible Collection.

The collection includes the modules and plugins supported by Ansible community.


## Installation and Usage

### Installing the Collection from Ansible Galaxy

Before using the General community collection, you need to install the collection with the `ansible-galaxy` CLI:

    ansible-galaxy collection install community.general

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml` using the format:

```yaml
collections:
- name: community.general
```

## Testing and Development

If you want to develop new content for this collection or improve what is already here, the easiest way to work on the collection is to clone it into one of the configured [`COLLECTIONS_PATHS`](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#collections-paths), and work on it there.

You can find more information in the [developer guide for collections](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections)

### Testing with `ansible-test`

See [here](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#testing-collections).

## Release notes

See [here](https://github.com/ansible-collections/community.general/tree/master/CHANGELOG.rst).

## Publishing New Version

Basic instructions without release branches:

1. Create `changelogs/fragments/<version>.yml` with `release_summary:` section (which must be a string, not a list).
2. Run `antsibull-changelog release --collection-flatmap yes`
3. Make sure `CHANGELOG.rst` and `changelogs/changelog.yaml` are added to git, and the deleted fragments have been removed.
4. Tag the commit with `<version>`. Push changes and tag to the main repository.

## More Information

TBD

## Communication

We have a dedicated Working Group for Ansible development.

You can find other people interested on the following Freenode IRC channels -
- `#ansible` - For general use questions and support.
- `#ansible-devel` - For discussions on developer topics and code related to features or bugs.
- `#ansible-community` - For discussions on community topics and community meetings.

For more information about communities, meetings and agendas see [Community Wiki](https://github.com/ansible/community/wiki/Community).

For more information about [communication](https://docs.ansible.com/ansible/latest/community/communication.html)

## License

GNU General Public License v3.0 or later

See [LICENSE](COPYING) to see the full text.
