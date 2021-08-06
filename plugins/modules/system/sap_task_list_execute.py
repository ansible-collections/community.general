#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Rainer Leber <rainerleber@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: sap_task_list_execute
short_description: Perform SAP Task list execution.
version_added: "3.5.0"
description:
  - The C(sap_task_list_execute) module depends on C(pyrfc) Python library (version 2.4.0 and upwards).
    Depending on distribution you are using, you may need to install additional packages to
    have these available.
  - Tasks in the task list which requires manual activities will be confirmed automatically.
  - This module will use the RFC Package C(STC_TM_API).

options:
  conn_username:
    description: The required username for the SAP system.
    required: true
    type: str
  conn_password:
    description: The required password for the SAP system.
    required: true
    type: str
  host:
    description: The required host for the SAP system. Can be either an FQDN or IP Address.
    required: true
    type: str
  sysnr:
    description:
      - The system number of the SAP system.
      - You must quote the value to ensure retaining the leading zeros.
      - Defaults to C('00')
    default: '00'
    type: str
  client:
    description:
      - The client number to connect to.
      - You must quote the value to ensure retaining the leading zeros.
      - Defaults to C('000')
    default : '000'
    type: str
  task_to_execute:
    description: The task list which will be executed.
    required: true
    type: str
  task_parameters:
    description:
      - The tasks and the parameters for execution.
      - If the task list do not need any parameters. This could be empty.
      - If only specific tasks from the task list should be executed.
        The tasks even when no parameter is needed must be provided.
        Alongside with the module parameter C(task_skip=true).
    type: list
    elements: dict
    suboptions:
      TASKNAME:
        description: The name of the task in the task list.
        type: str
        required: true
      FIELDNAME:
        description: The name of the field of the task.
        type: str
      VALUE:
        description: The value which have to be set.
        type: raw
  task_settings:
    description:
      - Setting for the execution of the task list. This can be the following as in TCODE SE80 described.
          Check Mode C(CHECKRUN), Background Processing Active C(BATCH) (this is the default value),
          Asynchronous Execution C(ASYNC), Trace Mode C(TRACE), Server Name C(BATCH_TARGET).
    default: ['BATCH']
    type: list
    elements: str
  task_skip:
    description:
      - If this parameter is true not defined tasks in C(task_parameters) are skipped.
      - This could be the case when only certain tasks should run from the task list.
    default: false
    type: bool

notes:
    - Does not support C(check_mode).
author:
    - Rainer Leber (@rainerleber)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test task execution
  community.general.sap_task_list_execute:
    conn_username: DDIC
    conn_password: Passwd1234
    host: 10.1.8.10
    sysnr: '01'
    client: '000'
    task_to_execute: SAP_BASIS_SSL_CHECK
    task_settings: batch

- name: Pass in input parameters
  community.general.sap_task_list_execute:
    conn_username: DDIC
    conn_password: Passwd1234
    host: 10.1.8.10
    sysnr: '00'
    client: '000'
    task_to_execute: SAP_BASIS_SSL_CHECK
    task_parameters :
      - { 'TASKNAME': 'CL_STCT_CHECK_SEC_CRYPTO', 'FIELDNAME': 'P_OPT2', 'VALUE': 'X' }
      - TASKNAME: CL_STCT_CHECK_SEC_CRYPTO
        FIELDNAME: P_OPT3
        VALUE: X
    task_settings: batch

# Exported environement variables.
- name: Hint if module will fail with error message like ImportError libsapnwrfc.so...
  community.general.sap_task_list_execute:
    conn_username: DDIC
    conn_password: Passwd1234
    host: 10.1.8.10
    sysnr: '00'
    client: '000'
    task_to_execute: SAP_BASIS_SSL_CHECK
    task_settings: batch
  environment:
    SAPNWRFC_HOME: /usr/local/sap/nwrfcsdk
    LD_LIBRARY_PATH: /usr/local/sap/nwrfcsdk/lib
'''

RETURN = r'''
msg:
  description: A small execution description
  type: str
  returned: always
  sample: 'Successfull'
out:
  description: A complete description of the executed tasks. If this is available.
  type: list
  elements: dict
  returned: on success
  sample: [...,{
              "LOG": {
                  "STCTM_S_LOG": [
                      {
                          "ACTIVITY": "U_CONFIG",
                          "ACTIVITY_DESCR": "Configuration changed",
                          "DETAILS": null,
                          "EXEC_ID": "20210728184903.815739",
                          "FIELD": null,
                          "ID": "STC_TASK",
                          "LOG_MSG_NO": "000000",
                          "LOG_NO": null,
                          "MESSAGE": "For radiobutton group ICM too many options are set; choose only one option",
                          "MESSAGE_V1": "ICM",
                          "MESSAGE_V2": null,
                          "MESSAGE_V3": null,
                          "MESSAGE_V4": null,
                          "NUMBER": "048",
                          "PARAMETER": null,
                          "PERIOD": "M",
                          "PERIOD_DESCR": "Maintenance",
                          "ROW": "0",
                          "SRC_LINE": "170",
                          "SRC_OBJECT": "CL_STCTM_REPORT_UI            IF_STCTM_UI_TASK~SET_PARAMETERS",
                          "SYSTEM": null,
                          "TIMESTMP": "20210728184903",
                          "TSTPNM": "DDIC",
                          "TYPE": "E"
                      },...
                    ]}}]
'''

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.json_utils import json
from xml.etree.ElementTree import XML
import traceback
try:
    from pyrfc import Connection
except ImportError:
    HAS_PYRFC_LIBRARY = False
    PYRFC_LIBRARY_IMPORT_ERROR = traceback.format_exc()
else:
    HAS_PYRFC_LIBRARY = True


def xml_dict(xml_raw):
    # adapted from: http://code.activestate.com/recipes/410469-xml-as-dictionary/
    list_out = []
    dict_out = {}
    if xml_raw:
        dict_out.update(dict(xml_raw.items()))
    for element in xml_raw:
        if element:
            # treat like dict - we assume that if the first two tags
            # in a series are different, then they are all different.
            if len(element) == 1 or element[0].tag != element[1].tag:
                aDict = xml_dict(element)
            # treat like list - if the first two tags
            # in a series are the same, then the rest are the same.
            else:
                for list_return in element:
                    if list_return:
                        # treat like dict
                        if len(list_return) == 1 or list_return[0].tag != list_return[1].tag:
                            list_out.append(xml_dict(list_return))
                        # treat like list
                        elif list_return[0].tag == list_return[1].tag:
                            list_out.append(list_out.xml_list(list_return))
                    elif list_return.text:
                        text = list_return.text.strip()
                        if text:
                            list_out.append(text)
                # put the list in dictionary;
                # the key is the tag name the list elements all share in common
                # the value is the list itself
                aDict = {element[0].tag: list_out}
            # if the tag has attributes, add those to the dict
            if element.items():
                aDict.update(dict(element.items()))
            dict_out.update({element.tag: aDict})
        elif element.items():
            dict_out.update({element.tag: dict(element.items())})
        # if there are no child tags and no attributes, extract the text
        else:
            dict_out.update({element.tag: element.text})
    return dict_out


def call_rfc_method(connection, method_name, kwargs):
    # PyRFC call function
    return connection.call(method_name, **kwargs)


def process_exec_settings(task_settings):
    # processes task settings to objects
    exec_settings = {}
    for settings in task_settings:
        temp_dict = {settings.upper(): 'X'}
        for key, value in temp_dict.items():
            exec_settings[key] = value
    return exec_settings


def run_module():

    params_spec = dict(
        TASKNAME=dict(type='str', required=True),
        FIELDNAME=dict(type='str'),
        VALUE=dict(type='raw'),
    )

    # define available arguments/parameters a user can pass to the module
    module = AnsibleModule(
        argument_spec=dict(
            # values for connection
            conn_username=dict(type='str', required=True),
            conn_password=dict(type='str', required=True, no_log=True),
            host=dict(type='str', required=True),
            sysnr=dict(type='str', default="00"),
            client=dict(type='str', default="000"),
            # values for execution tasks
            task_to_execute=dict(type='str', required=True),
            task_parameters=dict(type='list', elements='dict', options=params_spec),
            task_settings=dict(type='list', elements='str', default=['BATCH']),
            task_skip=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
    )
    result = dict(changed=False, msg='', out={}, json_out={}, error={}, )

    params = module.params

    username = (params['conn_username']).upper()
    password = params['conn_password']
    host = params['host']
    sysnr = params['sysnr']
    client = params['client']

    task_parameters = params['task_parameters']
    task_to_execute = params['task_to_execute']
    task_settings = params['task_settings']
    task_skip = params['task_skip']

    if not HAS_PYRFC_LIBRARY:
        module.fail_json(
            msg=missing_required_lib('pyrfc'),
            exception=PYRFC_LIBRARY_IMPORT_ERROR)

    # basic RFC connection with pyrfc
    try:
        conn = Connection({'user': username, 'passwd': password, 'ashost': host, 'sysnr': sysnr, 'client': client})
    except Exception as err:
        result['error'] = str(err)
        result['msg'] = 'Something went wrong connecting to the SAP system.'
        module.fail_json(**result)

    try:
        raw_params = call_rfc_method(conn, 'STC_TM_SCENARIO_GET_PARAMETERS',
                                     {'I_SCENARIO_ID': task_to_execute})
    except Exception as err:
        result['error'] = str(err)
        result['msg'] = 'The task list does not exsist.'
        module.fail_json(**result)
    exec_settings = process_exec_settings(task_settings)
    # initialize session task
    session_init = call_rfc_method(conn, 'STC_TM_SESSION_BEGIN',
                                   {'I_SCENARIO_ID': task_to_execute,
                                    'I_INIT_ONLY': 'X'})
    # Confirm Tasks which requires manual activities from Task List Run
    for task in raw_params['ET_PARAMETER']:
        call_rfc_method(conn, 'STC_TM_TASK_CONFIRM',
                        {'I_SESSION_ID': session_init['E_SESSION_ID'],
                         'I_TASKNAME': task['TASKNAME']})
    if task_skip:
        for task in raw_params['ET_PARAMETER']:
            call_rfc_method(conn, 'STC_TM_TASK_SKIP',
                            {'I_SESSION_ID': session_init['E_SESSION_ID'],
                             'I_TASKNAME': task['TASKNAME'], 'I_SKIP_DEP_TASKS': 'X'})
    # unskip defined tasks
    if task_parameters is not None:
        for task in task_parameters:
            call_rfc_method(conn, 'STC_TM_TASK_UNSKIP',
                            {'I_SESSION_ID': session_init['E_SESSION_ID'],
                             'I_TASKNAME': task['TASKNAME'], 'I_UNSKIP_DEP_TASKS': 'X'})
    # set parameters
    if task_parameters is not None:
        call_rfc_method(conn, 'STC_TM_SESSION_SET_PARAMETERS',
                        {'I_SESSION_ID': session_init['E_SESSION_ID'],
                         'IT_PARAMETER': task_parameters})
    # start the task
    try:
        session_start = call_rfc_method(conn, 'STC_TM_SESSION_RESUME',
                                        {'I_SESSION_ID': session_init['E_SESSION_ID'],
                                         'IS_EXEC_SETTINGS': exec_settings})
    except Exception as err:
        result['error'] = str(err)
        result['msg'] = 'Something went wrong. See error.'
        module.fail_json(**result)
    # get task logs because the execution may successfully but the tasks shows errors or warnings
    # returned value is ABAPXML https://help.sap.com/doc/abapdocu_755_index_htm/7.55/en-US/abenabap_xslt_asxml_general.htm
    session_log = call_rfc_method(conn, 'STC_TM_SESSION_GET_LOG',
                                  {'I_SESSION_ID': session_init['E_SESSION_ID']})
    try:
        log_xml = XML(session_log['E_LOG'])
        task_list = xml_dict(log_xml)['{http://www.sap.com/abapxml}values']['SESSION']['TASKLIST']
    except KeyError:
        task_list = "No logs available."
    result['changed'] = True
    result['msg'] = session_start['E_STATUS_DESCR']
    result['json_out'] = json.dumps(task_list)
    result['out'] = task_list

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
