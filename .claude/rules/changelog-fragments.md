# Writing Changelog Fragments Rules:

Changelog Fragments:

- MUST be created for modifications in the productive code (mostly code under `plugins/`)
- MUST NOT be created for:
  - New modules or new plugins.
  - Changes touching only documentation, comments, and/or tests.
- MUST be files in `changelogs/fragments` named as `<PR number>-<some description, possibly matching the branch name>.yml`.
- MUST have a dict as the top-level element, and the keys MUST be one of: minor_changes, breaking_changes, deprecated_features, removed_features, bugfixes.
- MUST list, under each top-level element, one entry for each file changed in the PR.
- MUST use the format:
  ```
    - <component spec> - <description> (<URLs>).
  ```
  for the entries.
  - The "component spec" is different for different types of plugins, in this order:
    - Modules (`plugins/modules`): "<plugin-name>" (or <module-name>)
    - Module utils (`plugins/module_utils`): "<plugin-name> module utils"
    - Plugin utils (`plugins/plugin_utils`): "<plugin-name> plugin utils"
    - All other plugins (`plugins/<PLUGIN_TYPE>/`): "<plugin-name> <PLUGIN_TYPE> plugin"
    - Plugin filenames starting with `_` are not to be added to the changelog fragment
  - The description MUST be concise — one sentence stating what changed, from the user's perspective.
    Do NOT explain why the change was made, how it was implemented, or what Python constructs were used. Do not provide examples of values.
    The audience is end users and operators, not developers; avoid implementation details.
    Exception: if the mechanism itself is directly relevant to the user (e.g. a new retry behavior
    that affects timing or side effects), a brief mention is acceptable — but only if it adds real value.
    No need to provide details that can be found in the issue or in the PR.
    That content should be in RST format, so for example symbol names must be enclosed in double back ticks, as in "``symbol``".
    Use American English spelling (e.g. "behavior" not "behaviour", "customize" not "customise").
    Description must start with lower-case - do not capitalize it.
  - The URLs - the URL of the current PR and, if the PR fixes one or more issues, the URLs of those issues as well.
    Preferably the issues before the PR. The URLs must be separated with `, `.
- SHOULD NOT mix `bugfixes` with other changes: fixes are backported and no new features should come along
- SHOULD NOT mix `deprecated_features` with other changes


Given the fact that the PR number is required for the file name and for the URLs part of the entry,
the fragment must be generated (then commited and pushed) after the PR is first created.

After drafting a changelog fragment, always present it to the user for review and explicit
approval before committing or pushing it.
