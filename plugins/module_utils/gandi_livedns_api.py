# -*- coding: utf-8 -*-
# Copyright (c) 2019 Gregory Thiemonge <gregory.thiemonge@gmail.com>
# Simplified BSD License (see LICENSES/BSD-2-Clause.txt or https://opensource.org/licenses/BSD-2-Clause)
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json

from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.urls import fetch_url


class GandiLiveDNSAPI(object):

    api_endpoint = 'https://api.gandi.net/v5/livedns'
    changed = False

    error_strings = {
        400: 'Bad request',
        401: 'Permission denied',
        404: 'Resource not found',
    }

    attribute_map = {
        'record': 'rrset_name',
        'type': 'rrset_type',
        'ttl': 'rrset_ttl',
        'values': 'rrset_values'
    }

    def __init__(self, module):
        self.module = module
        self.api_key = module.params['api_key']

    def _build_error_message(self, module, info):
        s = ''
        body = info.get('body')
        if body:
            errors = module.from_json(body).get('errors')
            if errors:
                error = errors[0]
                name = error.get('name')
                if name:
                    s += '{0} :'.format(name)
                description = error.get('description')
                if description:
                    s += description
        return s

    def _gandi_api_call(self, api_call, method='GET', payload=None, error_on_404=True):
        headers = {'Authorization': 'Apikey {0}'.format(self.api_key),
                   'Content-Type': 'application/json'}
        data = None
        if payload:
            try:
                data = json.dumps(payload)
            except Exception as e:
                self.module.fail_json(msg="Failed to encode payload as JSON: %s " % to_native(e))

        resp, info = fetch_url(self.module,
                               self.api_endpoint + api_call,
                               headers=headers,
                               data=data,
                               method=method)

        error_msg = ''
        if info['status'] >= 400 and (info['status'] != 404 or error_on_404):
            err_s = self.error_strings.get(info['status'], '')

            error_msg = "API Error {0}: {1}".format(err_s, self._build_error_message(self.module, info))

        result = None
        try:
            content = resp.read()
        except AttributeError:
            content = None

        if content:
            try:
                result = json.loads(to_text(content, errors='surrogate_or_strict'))
            except (getattr(json, 'JSONDecodeError', ValueError)) as e:
                error_msg += "; Failed to parse API response with error {0}: {1}".format(to_native(e), content)

        if error_msg:
            self.module.fail_json(msg=error_msg)

        return result, info['status']

    def build_result(self, result, domain):
        if result is None:
            return None

        res = {}
        for k in self.attribute_map:
            v = result.get(self.attribute_map[k], None)
            if v is not None:
                if k == 'record' and v == '@':
                    v = ''
                res[k] = v

        res['domain'] = domain

        return res

    def build_results(self, results, domain):
        if results is None:
            return []
        return [self.build_result(r, domain) for r in results]

    def get_records(self, record, type, domain):
        url = '/domains/%s/records' % (domain)
        if record:
            url += '/%s' % (record)
            if type:
                url += '/%s' % (type)

        records, status = self._gandi_api_call(url, error_on_404=False)

        if status == 404:
            return []

        if not isinstance(records, list):
            records = [records]

        # filter by type if record is not set
        if not record and type:
            records = [r
                       for r in records
                       if r['rrset_type'] == type]

        return records

    def create_record(self, record, type, values, ttl, domain):
        url = '/domains/%s/records' % (domain)
        new_record = {
            'rrset_name': record,
            'rrset_type': type,
            'rrset_values': values,
            'rrset_ttl': ttl,
        }
        record, status = self._gandi_api_call(url, method='POST', payload=new_record)

        if status in (200, 201,):
            return new_record

        return None

    def update_record(self, record, type, values, ttl, domain):
        url = '/domains/%s/records/%s/%s' % (domain, record, type)
        new_record = {
            'rrset_values': values,
            'rrset_ttl': ttl,
        }
        record = self._gandi_api_call(url, method='PUT', payload=new_record)[0]
        return record

    def delete_record(self, record, type, domain):
        url = '/domains/%s/records/%s/%s' % (domain, record, type)

        self._gandi_api_call(url, method='DELETE')

    def delete_dns_record(self, record, type, values, domain):
        if record == '':
            record = '@'

        records = self.get_records(record, type, domain)

        if records:
            cur_record = records[0]

            self.changed = True

            if values is not None and set(cur_record['rrset_values']) != set(values):
                new_values = set(cur_record['rrset_values']) - set(values)
                if new_values:
                    # Removing one or more values from a record, we update the record with the remaining values
                    self.update_record(record, type, list(new_values), cur_record['rrset_ttl'], domain)
                    records = self.get_records(record, type, domain)
                    return records[0], self.changed

            if not self.module.check_mode:
                self.delete_record(record, type, domain)
        else:
            cur_record = None

        return None, self.changed

    def ensure_dns_record(self, record, type, ttl, values, domain):
        if record == '':
            record = '@'

        records = self.get_records(record, type, domain)

        if records:
            cur_record = records[0]

            do_update = False
            if ttl is not None and cur_record['rrset_ttl'] != ttl:
                do_update = True
            if values is not None and set(cur_record['rrset_values']) != set(values):
                do_update = True

            if do_update:
                if self.module.check_mode:
                    result = dict(
                        rrset_type=type,
                        rrset_name=record,
                        rrset_values=values,
                        rrset_ttl=ttl
                    )
                else:
                    self.update_record(record, type, values, ttl, domain)

                    records = self.get_records(record, type, domain)
                    result = records[0]
                self.changed = True
                return result, self.changed
            else:
                return cur_record, self.changed

        if self.module.check_mode:
            new_record = dict(
                rrset_type=type,
                rrset_name=record,
                rrset_values=values,
                rrset_ttl=ttl
            )
            result = new_record
        else:
            result = self.create_record(record, type, values, ttl, domain)

        self.changed = True
        return result, self.changed
