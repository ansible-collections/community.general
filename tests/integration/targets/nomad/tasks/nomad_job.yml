- name: create job
  nomad_job:
    host: localhost
    state: present
    source_hcl: "{{ lookup('file', 'job.hcl') }}"
    timeout: 120
  register: deploy_job

- assert:
    that:
      - deploy_job is changed

