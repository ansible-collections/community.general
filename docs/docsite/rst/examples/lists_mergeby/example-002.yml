---
- name: Merge two lists by common attribute 'name'
  set_fact:
    list3: "{{ [list1, list2]|
               community.general.lists_mergeby('name') }}"
  vars:
    list1:
      - name: foo
        extra: true
      - name: bar
        extra: false
      - name: meh
        extra: true
    list2:
      - name: foo
        path: /foo
      - name: baz
        path: /baz
- debug:
    var: list3
