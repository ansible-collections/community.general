# Github Issues Rules

- Classify issues correctly: features are not bugfixes even if they address a gap or missing
  behavior. Use the issues template's categories accurately.
  - For an issue to be considered a bug, it must refer to a behavior promised in the
    plugin documentation or something that defeats its purpose. Elective preferences are not bugs. Missing features are not bugs.

- The "Community.general Version" and "Ansible Version" fields must report the versions used to detect the problem and they should be
  supported versions of: the collection itself, ansible-core, Python.

- MUST use one of the templates in `.github/ISSUE_TEMPLATE`
  - Component name: one per line, use the relative path in the repo, one per line
  - Community.general version: if bug exists in `main` branch, report the version from galaxy.yml
  - Do generate the Code of Conduct checkbox - I am responsible for what you do, my child
- When the issue is about code:

  The issue title must follow:
  | Case | Format | Example |
  | --- | --- | --- |
  | Module issue | `<name>: <summary>` | `postgresql_db: fails when password contains special characters` |
  | Non-module plugin | `<name> <type> plugin: <summary>` | `passwordstore lookup plugin: add support for multiline secrets` |
  | New plugin request | `<name>: new module` or `<name>: new <type> plugin` | `proxmox_vm: new module` |
  | Multiple related plugins | `<common_prefix>*: <summary>` | `proxmox*: multiple modules fail with newer API versions` |
  | Multiple unrelated plugins | `multiple: <summary>` | `multiple: deprecation warnings not shown correctly` |

  - Use lowercase for the summary part (after the colon).
  - Strip noise words: "Issue with", "Bug:", "[BUG]", "[FR]", "Request:".
  - When in doubt about the plugin name, skim the issue body for FQCN references or task examples.

- When the issue is NOT about code:

  An issue title like below is _suggested_ (never enforced) to the user:

  | Case | Format | Example |
  | --- | --- | --- |
  | Non-plugin (CI, docs, infra) | `docs:`, `ci:`, `testing:`, `build:`, `meta:` prefix | `docs: update contribution guidelines` |
