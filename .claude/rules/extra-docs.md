---
paths:
  - docs/docsite/rst/*.rst
---

# Extra docs Rules (RST files)

- The order of markers, from higher to lower level of headers, should be:
  ```
  ======
  ^^^^^^
  """"""
  ------
  ```
- Code blocks can only have the following languages:
  - ansible-output
  - console
  - ini
  - json
  - python
  - shell
  - text
  - yaml
  - yaml+jinja
- Use the [style guide](https://docs.ansible.com/projects/ansible/latest/dev_guide/style_guide/index.html) in the docs, except for:
  - Heading notation
  - Code block languages
- Use American English spelling (e.g. "behavior" not "behaviour", "customize" not "customise").
- All anchors created in the doc should be named with a prefix
  `ansible_collections.community.general.docsite.<filename-without-ext>.<something>`,
  where <something> is the actual thing being referred to.
