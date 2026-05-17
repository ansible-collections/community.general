# Github Pull Request Rules

- MUST use the template `.github/pull_request_template.md`
- MUST create the PR in the upstream repository
- Classify PRs correctly: features are not bugfixes even if they address a gap or missing
  behavior. Use the PR template's categories accurately.
- Do not comment in the description about the state of the changelog fragment.
- The PR title should be in one of the forms:
  - `<module>: <short-description>` e.g. `xfconf: adjust return value`
  - `<plugin> <plugin-type> plugin: <short-description>` e.g. `pbrun become plugin: refactor function xyz()`
  - `new module/<plugin-type> plugin: <name> <short-description>` e.g. `new module: xyz interacts with XyZ service` or
    `new inventory plugin: abc retrieves hosts from ABC daemon`
- PR title should use short names for modules/plugins, e.g. `xfconf` instead of `community.general.xfconf`
- PR title should use single backticks for terms like commands, variables, functions, etc. E.g. "xfconf: use command `xfconf-query`"
- PR title may have a prefix indicating it is a work in progress. E.g. "[WIP] xfconf: use command `xfconf-query`"
- If the PR fixes issues, add one line with `Fixes #<issue-number>` for each issue being solved to the PR description
- When a fix is speculative or lacks test coverage, use hedged language in the PR description (e.g. "may address" rather than "this fixes").
- Keep PR descriptions concise; do not explain implementation choices or reproduce information already visible in the diff or commit messages.
