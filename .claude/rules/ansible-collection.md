# Ansible Collection Rules

- This collection follows Semantic Versioning.
- Being an Ansible collection, its version number is specificied in the `galaxy.yml`.
- The version set there, for the `main` branch is the next version to be released.
- For this collection, you will want to read the description
  of the issue: https://github.com/ansible-collections/community.general/issues/11482
- The guidelines for contributors are found in the `CONTRIBUTING.md`.
- It is very important to maintain backwards compatibility in the changes.
- When something needs to change and break that, a longer process must be taken,
  involving deprecations and sometimes feature flags to enable the new behaviour.
- Deprecations usually plan for the removal of the deprecated code in two major versions (X+2).0.0 from
  the current version. Depending on the situation, this target may be pushed for the (X+3).0.0 version.
- If a deprecation is needed, ingest https://github.com/russoz-ansible/ansible-contrib-unofficial/blob/main/deprecations.md for more information on how to implement the deprecations.
- Always refer to modules and plugins by their FQCN
- When setting `version_added` on a new parameter or plugin, always read `galaxy.yml` and use
  that version string directly — it holds the next version to be released on `main`
