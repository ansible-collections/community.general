#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: win_scheduled_task
short_description: Manage scheduled tasks
description:
- Creates/modified or removes Windows scheduled tasks.
options:
  # module definition options
  name:
    description:
    - The name of the scheduled task without the path.
    type: str
    required: yes
  path:
    description:
    - Task folder in which this task will be stored.
    - Will create the folder when C(state=present) and the folder does not
      already exist.
    - Will remove the folder when C(state=absent) and there are no tasks left
      in the folder.
    type: str
    default: \
  state:
    description:
    - When C(state=present) will ensure the task exists.
    - When C(state=absent) will ensure the task does not exist.
    type: str
    choices: [ absent, present ]
    default: present

  # Action options
  actions:
    description:
    - A list of action to configure for the task.
    - See suboptions for details on how to construct each list entry.
    - When creating a task there MUST be at least one action but when deleting
      a task this can be a null or an empty list.
    - The ordering of this list is important, the module will ensure the order
      is kept when modifying the task.
    - This module only supports the C(ExecAction) type but can still delete the
      older legacy types.
    type: list
    suboptions:
      path:
        description:
        - The path to the executable for the ExecAction.
        type: str
        required: yes
      arguments:
        description:
        - An argument string to supply for the executable.
        type: str
      working_directory:
        description:
        - The working directory to run the executable from.
        type: str

  # Trigger options
  triggers:
    description:
    - A list of triggers to configure for the task.
    - See suboptions for details on how to construct each list entry.
    - The ordering of this list is important, the module will ensure the order
      is kept when modifying the task.
    - There are multiple types of triggers, see U(https://msdn.microsoft.com/en-us/library/windows/desktop/aa383868.aspx)
      for a list of trigger types and their options.
    - The suboption options listed below are not required for all trigger
      types, read the description for more details.
    type: list
    suboptions:
      type:
        description:
        - The trigger type, this value controls what below options are
          required.
        type: str
        required: yes
        choices: [ boot, daily, event, idle, logon, monthlydow, monthly, registration, time, weekly, session_state_change ]
      enabled:
        description:
        - Whether to set the trigger to enabled or disabled
        - Used in all trigger types.
        type: bool
      start_boundary:
        description:
        - The start time for the task, even if the trigger meets the other
          start criteria, it won't start until this time is met.
        - If you wish to run a task at 9am on a day you still need to specify
          the date on which the trigger is activated, you can set any date even
          ones in the past.
        - Required when C(type) is C(daily), C(monthlydow), C(monthly),
          C(time), C(weekly), (session_state_change).
        - Optional for the rest of the trigger types.
        - This is in ISO 8601 DateTime format C(YYYY-MM-DDThh:mm:ss).
        type: str
      end_boundary:
        description:
        - The end time for when the trigger is deactivated.
        - This is in ISO 8601 DateTime format C(YYYY-MM-DDThh:mm:ss).
        type: str
      execution_time_limit:
        description:
        - The maximum amount of time that the task is allowed to run for.
        - Optional for all the trigger types.
        - Is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
        type: str
      delay:
        description:
        - The time to delay the task from running once the trigger has been
          fired.
        - Optional when C(type) is C(boot), C(event), C(logon),
          C(registration), C(session_state_change).
        - Is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
        type: str
      random_delay:
        description:
        - The delay time that is randomly added to the start time of the
          trigger.
        - Optional when C(type) is C(daily), C(monthlydow), C(monthly),
          C(time), C(weekly).
        - Is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
        type: str
      subscription:
        description:
        - Only used and is required for C(type=event).
        - The XML query string that identifies the event that fires the
          trigger.
        type: str
      user_id:
        description:
        - The username that the trigger will target.
        - Optional when C(type) is C(logon), C(session_state_change).
        - Can be the username or SID of a user.
        - When C(type=logon) and you want the trigger to fire when a user in a
          group logs on, leave this as null and set C(group) to the group you
          wish to trigger.
        type: str
      days_of_week:
        description:
        - The days of the week for the trigger.
        - Can be a list or comma separated string of full day names e.g. monday
          instead of mon.
        - Required when C(type) is C(weekly), C(type=session_state_change).
        - Optional when C(type=monthlydow).
        type: str
      days_of_month:
        description:
        - The days of the month from 1 to 31 for the triggers.
        - If you wish to set the trigger for the last day of any month
          use C(run_on_last_day_of_month).
        - Can be a list or comma separated string of day numbers.
        - Required when C(type=monthly).
        type: str
      weeks_of_month:
        description:
        - The weeks of the month for the trigger.
        - Can be a list or comma separated string of the numbers 1 to 4
          representing the first to 4th week of the month.
        - Optional when C(type=monthlydow).
        type: str
      months_of_year:
        description:
        - The months of the year for the trigger.
        - Can be a list or comma separated string of full month names e.g.
          march instead of mar.
        - Optional when C(type) is C(monthlydow), C(monthly).
        type: str
      run_on_last_week_of_month:
        description:
        - Boolean value that sets whether the task runs on the last week of the
          month.
        - Optional when C(type) is C(monthlydow).
        type: bool
      run_on_last_day_of_month:
        description:
        - Boolean value that sets whether the task runs on the last day of the
          month.
        - Optional when C(type) is C(monthly).
        type: bool
      weeks_interval:
        description:
        - The interval of weeks to run on, e.g. C(1) means every week while
          C(2) means every other week.
        - Optional when C(type=weekly).
        type: int
      repetition:
        description:
        - Allows you to define the repetition action of the trigger that defines how often the task is run and how long the repetition pattern is repeated
          after the task is started.
        - It takes in the following keys, C(duration), C(interval), C(stop_at_duration_end)
        suboptions:
          duration:
            description:
            - Defines how long the pattern is repeated.
            - The value is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
            - By default this is not set which means it will repeat indefinitely.
            type: str
          interval:
            description:
            - The amount of time between each restart of the task.
            - The value is written in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
            type: str
          stop_at_duration_end:
            description:
            - Whether a running instance of the task is stopped at the end of the repetition pattern.
            type: bool

  # Principal options
  display_name:
    description:
    - The name of the user/group that is displayed in the Task Scheduler UI.
    type: str
  group:
    description:
    - The group that will run the task.
    - C(group) and C(username) are exclusive to each other and cannot be set
      at the same time.
    - C(logon_type) can either be not set or equal C(group).
    type: str
  logon_type:
    description:
    - The logon method that the task will run with.
    - C(password) means the password will be stored and the task has access
      to network resources.
    - C(s4u) means the existing token will be used to run the task and no
      password will be stored with the task. Means no network or encrypted
      files access.
    - C(interactive_token) means the user must already be logged on
      interactively and will run in an existing interactive session.
    - C(group) means that the task will run as a group.
    - C(service_account) means that a service account like System, Local
      Service or Network Service will run the task.
    type: str
    choices: [ none, password, s4u, interactive_token, group, service_account, token_or_password ]
  run_level:
    description:
    - The level of user rights used to run the task.
    - If not specified the task will be created with limited rights.
    type: str
    choices: [ limited, highest ]
    aliases: [ runlevel ]
  username:
    description:
    - The user to run the scheduled task as.
    - Will default to the current user under an interactive token if not
      specified during creation.
    - The user account specified must have the C(SeBatchLogonRight) logon right
      which can be added with M(win_user_right).
    type: str
    aliases: [ user ]
  password:
    description:
    - The password for the user account to run the scheduled task as.
    - This is required when running a task without the user being logged in,
      excluding the builtin service accounts and Group Managed Service Accounts (gMSA).
    - If set, will always result in a change unless C(update_password) is set
      to C(no) and no other changes are required for the service.
    type: str
  update_password:
    description:
    - Whether to update the password even when not other changes have occurred.
    - When C(yes) will always result in a change when executing the module.
    type: bool
    default: yes

  # RegistrationInfo options
  author:
    description:
    - The author of the task.
    type: str
  date:
    description:
    - The date when the task was registered.
    type: str
  description:
    description:
    - The description of the task.
    type: str
  source:
    description:
    - The source of the task.
    type: str
  version:
    description:
    - The version number of the task.
    type: str

  # Settings options
  allow_demand_start:
    description:
    - Whether the task can be started by using either the Run command or the
      Context menu.
    type: bool
  allow_hard_terminate:
    description:
    - Whether the task can be terminated by using TerminateProcess.
    type: bool
  compatibility:
    description:
    - The integer value with indicates which version of Task Scheduler a task
      is compatible with.
    - C(0) means the task is compatible with the AT command.
    - C(1) means the task is compatible with Task Scheduler 1.0.
    - C(2) means the task is compatible with Task Scheduler 2.0.
    type: int
    choices: [ 0, 1, 2 ]
  delete_expired_task_after:
    description:
    - The amount of time that the Task Scheduler will wait before deleting the
      task after it expires.
    - A task expires after the end_boundary has been exceeded for all triggers
      associated with the task.
    - This is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
    type: str
  disallow_start_if_on_batteries:
    description:
    - Whether the task will not be started if the computer is running on
      battery power.
    type: bool
  enabled:
    description:
    - Whether the task is enabled, the task can only run when C(yes).
    type: bool
  execution_time_limit:
    description:
    - The amount of time allowed to complete the task.
    - When set to `PT0S`, the time limit is infinite.
    - When omitted, the default time limit is 72 hours.
    - This is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
    type: str
  hidden:
    description:
    - Whether the task will be hidden in the UI.
    type: bool
  multiple_instances:
    description:
    - An integer that indicates the behaviour when starting a task that is
      already running.
    - C(0) will start a new instance in parallel with existing instances of
      that task.
    - C(1) will wait until other instances of that task to finish running
      before starting itself.
    - C(2) will not start a new instance if another is running.
    - C(3) will stop other instances of the task and start the new one.
    type: int
    choices: [ 0, 1, 2, 3 ]
  priority:
    description:
    - The priority level (0-10) of the task.
    - When creating a new task the default is C(7).
    - See U(https://msdn.microsoft.com/en-us/library/windows/desktop/aa383512.aspx)
      for details on the priority levels.
    type: int
  restart_count:
    description:
    - The number of times that the Task Scheduler will attempt to restart the
      task.
    type: int
  restart_interval:
    description:
    - How long the Task Scheduler will attempt to restart the task.
    - If this is set then C(restart_count) must also be set.
    - The maximum allowed time is 31 days.
    - The minimum allowed time is 1 minute.
    - This is in the ISO 8601 Duration format C(P[n]Y[n]M[n]DT[n]H[n]M[n]S).
    type: str
  run_only_if_idle:
    description:
    - Whether the task will run the task only if the computer is in an idle
      state.
    type: bool
  run_only_if_network_available:
    description:
    - Whether the task will run only when a network is available.
    type: bool
  start_when_available:
    description:
    - Whether the task can start at any time after its scheduled time has
      passed.
    type: bool
  stop_if_going_on_batteries:
    description:
    - Whether the task will be stopped if the computer begins to run on battery
      power.
    type: bool
  wake_to_run:
    description:
    - Whether the task will wake the computer when it is time to run the task.
    type: bool
notes:
- In Ansible 2.4 and earlier, this could only be run on Server 2012/Windows 8
  or newer. Since Ansible 2.5 this restriction has been lifted.
- The option names and structure for actions and triggers of a service follow
  the C(RegisteredTask) naming standard and requirements, it would be useful to
  read up on this guide if coming across any issues U(https://msdn.microsoft.com/en-us/library/windows/desktop/aa382542.aspx).
- A Group Managed Service Account (gMSA) can be used by setting C(logon_type) to C(password)
  and omitting the password parameter. For more information on gMSAs,
  see U(https://techcommunity.microsoft.com/t5/Core-Infrastructure-and-Security/Windows-Server-2012-Group-Managed-Service-Accounts/ba-p/255910)
seealso:
- module: win_scheduled_task_stat
- module: win_user_right
author:
- Peter Mounce (@petemounce)
- Jordan Borean (@jborean93)
'''

EXAMPLES = r'''
- name: Create a task to open 2 command prompts as SYSTEM
  win_scheduled_task:
    name: TaskName
    description: open command prompt
    actions:
    - path: cmd.exe
      arguments: /c hostname
    - path: cmd.exe
      arguments: /c whoami
    triggers:
    - type: daily
      start_boundary: '2017-10-09T09:00:00'
    username: SYSTEM
    state: present
    enabled: yes

- name: Create task to run a PS script as NETWORK service on boot
  win_scheduled_task:
    name: TaskName2
    description: Run a PowerShell script
    actions:
    - path: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
      arguments: -ExecutionPolicy Unrestricted -NonInteractive -File C:\TestDir\Test.ps1
    triggers:
    - type: boot
    username: NETWORK SERVICE
    run_level: highest
    state: present

- name: Update Local Security Policy to allow users to run scheduled tasks
  win_user_right:
    name: SeBatchLogonRight
    users:
    - LocalUser
    - DOMAIN\NetworkUser
    action: add

- name: Change above task to run under a domain user account, storing the passwords
  win_scheduled_task:
    name: TaskName2
    username: DOMAIN\User
    password: Password
    logon_type: password

- name: Change the above task again, choosing not to store the password
  win_scheduled_task:
    name: TaskName2
    username: DOMAIN\User
    logon_type: s4u

- name: Change above task to use a gMSA, where the password is managed automatically
  win_scheduled_task:
    name: TaskName2
    username: DOMAIN\gMsaSvcAcct$
    logon_type: password

- name: Create task with multiple triggers
  win_scheduled_task:
    name: TriggerTask
    path: \Custom
    actions:
    - path: cmd.exe
    triggers:
    - type: daily
    - type: monthlydow
    username: SYSTEM

- name: Set logon type to password but don't force update the password
  win_scheduled_task:
    name: TriggerTask
    path: \Custom
    actions:
    - path: cmd.exe
    username: Administrator
    password: password
    update_password: no

- name: Disable a task that already exists
  win_scheduled_task:
    name: TaskToDisable
    enabled: no

- name: Create a task that will be repeated every minute for five minutes
  win_scheduled_task:
    name: RepeatedTask
    description: open command prompt
    actions:
    - path: cmd.exe
      arguments: /c hostname
    triggers:
    - type: registration
      repetition:
        interval: PT1M
        duration: PT5M
        stop_at_duration_end: yes
'''

RETURN = r'''
'''
