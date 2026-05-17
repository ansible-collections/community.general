---
paths:
  - plugins/modules/**.py
  - plugins/module_utils/**.py
---

# Deprecation Rules

Reference guide: https://github.com/russoz-ansible/ansible-contrib-unofficial/blob/main/deprecations.md

## Deprecating a parameter with no default value

Use `removed_in_version` + `removed_from_collection` in `argument_spec`, plus a description note in the docs.

## Deprecating a parameter that has a default value

Do NOT use `removed_in_version` — it triggers on every run because the parameter is always resolved (via its default), even when the user never explicitly set it.

Instead:
- Remove `default` from `argument_spec`
- Remove `default:` from the docs; describe the old default in the description text alongside the deprecation note
- In `main()`, detect `None` (meaning the user didn't set it), apply the old default manually, and call:
  ```python
  module.deprecate(
      "The <param> option will be removed ...",
      version="X.Y.0",
      collection_name="community.general",
  )
  ```

## Removal target versions

- Default: plan removal at `(X+2).0.0` from the current major version
- May be pushed to `(X+3).0.0` depending on the situation
