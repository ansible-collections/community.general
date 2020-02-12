#!/usr/bin/python
#
# Copyright (c) 2018 Yunge Zhu, <yungez@microsoft.com>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_webapp_info


short_description: Get Azure web app facts

description:
    - Get facts for a specific web app or all web app in a resource group, or all web app in current subscription.

options:
    name:
        description:
            - Only show results for a specific web app.
    resource_group:
        description:
            - Limit results by resource group.
    return_publish_profile:
        description:
            - Indicate whether to return publishing profile of the web app.
        default: False
        type: bool
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.


author:
    - Yunge Zhu (@yungezz)

extends_documentation_fragment:
- community.general.azure
'''

EXAMPLES = '''
    - name: Get facts for web app by name
      azure_rm_webapp_info:
        resource_group: myResourceGroup
        name: winwebapp1

    - name: Get facts for web apps in resource group
      azure_rm_webapp_info:
        resource_group: myResourceGroup

    - name: Get facts for web apps with tags
      azure_rm_webapp_info:
        tags:
          - testtag
          - foo:bar
'''

RETURN = '''
webapps:
    description:
        - List of web apps.
    returned: always
    type: complex
    contains:
        id:
            description:
                - ID of the web app.
            returned: always
            type: str
            sample: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/sites/myWebApp
        name:
            description:
                - Name of the web app.
            returned: always
            type: str
            sample: winwebapp1
        resource_group:
            description:
                - Resource group of the web app.
            returned: always
            type: str
            sample: myResourceGroup
        location:
            description:
                - Location of the web app.
            returned: always
            type: str
            sample: eastus
        plan:
            description:
                - ID of app service plan used by the web app.
            returned: always
            type: str
            sample: /subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/myResourceGroup/providers/Microsoft.Web/serverfarms/myAppServicePlan
        app_settings:
            description:
                - App settings of the application. Only returned when web app has app settings.
            returned: always
            type: dict
            sample: {
                    "testkey": "testvalue",
                    "testkey2": "testvalue2"
                    }
        frameworks:
            description:
                - Frameworks of the application. Only returned when web app has frameworks.
            returned: always
            type: list
            sample: [
                    {
                        "name": "net_framework",
                        "version": "v4.0"
                    },
                    {
                        "name": "java",
                        "settings": {
                            "java_container": "tomcat",
                            "java_container_version": "8.5"
                        },
                        "version": "1.7"
                    },
                    {
                        "name": "php",
                        "version": "5.6"
                    }
                    ]
        availability_state:
            description:
                - Availability of this web app.
            returned: always
            type: str
            sample: Normal
        default_host_name:
            description:
                - Host name of the web app.
            returned: always
            type: str
            sample: vxxisurg397winapp4.azurewebsites.net
        enabled:
            description:
                - Indicates the web app enabled or not.
            returned: always
            type: bool
            sample: true
        enabled_host_names:
            description:
                - Enabled host names of the web app.
            returned: always
            type: list
            sample: [
                    "vxxisurg397winapp4.azurewebsites.net",
                    "vxxisurg397winapp4.scm.azurewebsites.net"
                    ]
        host_name_ssl_states:
            description:
                - SSL state per host names of the web app.
            returned: always
            type: list
            sample: [
                    {
                        "hostType": "Standard",
                        "name": "vxxisurg397winapp4.azurewebsites.net",
                        "sslState": "Disabled"
                    },
                    {
                        "hostType": "Repository",
                        "name": "vxxisurg397winapp4.scm.azurewebsites.net",
                        "sslState": "Disabled"
                    }
                    ]
        host_names:
            description:
                - Host names of the web app.
            returned: always
            type: list
            sample: [
                    "vxxisurg397winapp4.azurewebsites.net"
                    ]
        outbound_ip_addresses:
            description:
                - Outbound IP address of the web app.
            returned: always
            type: str
            sample: "40.71.11.131,40.85.166.200,168.62.166.67,137.135.126.248,137.135.121.45"
        ftp_publish_url:
            description:
                - Publishing URL of the web app when deployment type is FTP.
            returned: always
            type: str
            sample: ftp://xxxx.ftp.azurewebsites.windows.net
        state:
            description:
                - State of the web app.
            returned: always
            type: str
            sample: running
        publishing_username:
            description:
                - Publishing profile user name.
            returned: only when I(return_publish_profile=True).
            type: str
            sample: "$vxxisuRG397winapp4"
        publishing_password:
            description:
                - Publishing profile password.
            returned: only when I(return_publish_profile=True).
            type: str
            sample: "uvANsPQpGjWJmrFfm4Ssd5rpBSqGhjMk11pMSgW2vCsQtNx9tcgZ0xN26s9A"
        tags:
            description:
               - Tags assigned to the resource. Dictionary of string:string pairs.
            returned: always
            type: dict
            sample: { tag1: abc }
'''
try:
    from msrestazure.azure_exceptions import CloudError
    from msrest.polling import LROPoller
    from azure.common import AzureMissingResourceHttpError, AzureHttpError
except Exception:
    # This is handled in azure_rm_common
    pass

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

AZURE_OBJECT_CLASS = 'WebApp'


class AzureRMWebAppInfo(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str'),
            resource_group=dict(type='str'),
            tags=dict(type='list'),
            return_publish_profile=dict(type='bool', default=False),
        )

        self.results = dict(
            changed=False,
            webapps=[],
        )

        self.name = None
        self.resource_group = None
        self.tags = None
        self.return_publish_profile = False

        self.framework_names = ['net_framework', 'java', 'php', 'node', 'python', 'dotnetcore', 'ruby']

        super(AzureRMWebAppInfo, self).__init__(self.module_arg_spec,
                                                supports_tags=False,
                                                facts_module=True)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_webapp_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_webapp_facts' module has been renamed to 'azure_rm_webapp_info'", version='2.13')

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name:
            self.results['webapps'] = self.list_by_name()
        elif self.resource_group:
            self.results['webapps'] = self.list_by_resource_group()
        else:
            self.results['webapps'] = self.list_all()

        return self.results

    def list_by_name(self):
        self.log('Get web app {0}'.format(self.name))
        item = None
        result = []

        try:
            item = self.web_client.web_apps.get(self.resource_group, self.name)
        except CloudError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            curated_result = self.get_curated_webapp(self.resource_group, self.name, item)
            result = [curated_result]

        return result

    def list_by_resource_group(self):
        self.log('List web apps in resource groups {0}'.format(self.resource_group))
        try:
            response = list(self.web_client.web_apps.list_by_resource_group(self.resource_group))
        except CloudError as exc:
            request_id = exc.request_id if exc.request_id else ''
            self.fail("Error listing web apps in resource groups {0}, request id: {1} - {2}".format(self.resource_group, request_id, str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                curated_output = self.get_curated_webapp(self.resource_group, item.name, item)
                results.append(curated_output)
        return results

    def list_all(self):
        self.log('List web apps in current subscription')
        try:
            response = list(self.web_client.web_apps.list())
        except CloudError as exc:
            request_id = exc.request_id if exc.request_id else ''
            self.fail("Error listing web apps, request id {0} - {1}".format(request_id, str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                curated_output = self.get_curated_webapp(item.resource_group, item.name, item)
                results.append(curated_output)
        return results

    def list_webapp_configuration(self, resource_group, name):
        self.log('Get web app {0} configuration'.format(name))

        response = []

        try:
            response = self.web_client.web_apps.get_configuration(resource_group_name=resource_group, name=name)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} configuration, request id {1} - {2}'.format(name, request_id, str(ex)))

        return response.as_dict()

    def list_webapp_appsettings(self, resource_group, name):
        self.log('Get web app {0} app settings'.format(name))

        response = []

        try:
            response = self.web_client.web_apps.list_application_settings(resource_group_name=resource_group, name=name)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} app settings, request id {1} - {2}'.format(name, request_id, str(ex)))

        return response.as_dict()

    def get_publish_credentials(self, resource_group, name):
        self.log('Get web app {0} publish credentials'.format(name))
        try:
            poller = self.web_client.web_apps.list_publishing_credentials(resource_group, name)
            if isinstance(poller, LROPoller):
                response = self.get_poller_result(poller)
        except CloudError as ex:
            request_id = ex.request_id if ex.request_id else ''
            self.fail('Error getting web app {0} publishing credentials - {1}'.format(request_id, str(ex)))
        return response

    def get_webapp_ftp_publish_url(self, resource_group, name):
        import xmltodict

        self.log('Get web app {0} app publish profile'.format(name))

        url = None
        try:
            content = self.web_client.web_apps.list_publishing_profile_xml_with_secrets(resource_group_name=resource_group, name=name)
            if not content:
                return url

            full_xml = ''
            for f in content:
                full_xml += f.decode()
            profiles = xmltodict.parse(full_xml, xml_attribs=True)['publishData']['publishProfile']

            if not profiles:
                return url

            for profile in profiles:
                if profile['@publishMethod'] == 'FTP':
                    url = profile['@publishUrl']

        except CloudError as ex:
            self.fail('Error getting web app {0} app settings'.format(name))

        return url

    def get_curated_webapp(self, resource_group, name, webapp):
        pip = self.serialize_obj(webapp, AZURE_OBJECT_CLASS)

        try:
            site_config = self.list_webapp_configuration(resource_group, name)
            app_settings = self.list_webapp_appsettings(resource_group, name)
            publish_cred = self.get_publish_credentials(resource_group, name)
            ftp_publish_url = self.get_webapp_ftp_publish_url(resource_group, name)
        except CloudError as ex:
            pass
        return self.construct_curated_webapp(webapp=pip,
                                             configuration=site_config,
                                             app_settings=app_settings,
                                             deployment_slot=None,
                                             ftp_publish_url=ftp_publish_url,
                                             publish_credentials=publish_cred)

    def construct_curated_webapp(self,
                                 webapp,
                                 configuration=None,
                                 app_settings=None,
                                 deployment_slot=None,
                                 ftp_publish_url=None,
                                 publish_credentials=None):
        curated_output = dict()
        curated_output['id'] = webapp['id']
        curated_output['name'] = webapp['name']
        curated_output['resource_group'] = webapp['properties']['resourceGroup']
        curated_output['location'] = webapp['location']
        curated_output['plan'] = webapp['properties']['serverFarmId']
        curated_output['tags'] = webapp.get('tags', None)

        # important properties from output. not match input arguments.
        curated_output['app_state'] = webapp['properties']['state']
        curated_output['availability_state'] = webapp['properties']['availabilityState']
        curated_output['default_host_name'] = webapp['properties']['defaultHostName']
        curated_output['host_names'] = webapp['properties']['hostNames']
        curated_output['enabled'] = webapp['properties']['enabled']
        curated_output['enabled_host_names'] = webapp['properties']['enabledHostNames']
        curated_output['host_name_ssl_states'] = webapp['properties']['hostNameSslStates']
        curated_output['outbound_ip_addresses'] = webapp['properties']['outboundIpAddresses']

        # curated site_config
        if configuration:
            curated_output['frameworks'] = []
            for fx_name in self.framework_names:
                fx_version = configuration.get(fx_name + '_version', None)
                if fx_version:
                    fx = {
                        'name': fx_name,
                        'version': fx_version
                    }
                    # java container setting
                    if fx_name == 'java':
                        if configuration['java_container'] and configuration['java_container_version']:
                            settings = {
                                'java_container': configuration['java_container'].lower(),
                                'java_container_version': configuration['java_container_version']
                            }
                            fx['settings'] = settings

                    curated_output['frameworks'].append(fx)

            # linux_fx_version
            if configuration.get('linux_fx_version', None):
                tmp = configuration.get('linux_fx_version').split("|")
                if len(tmp) == 2:
                    curated_output['frameworks'].append({'name': tmp[0].lower(), 'version': tmp[1]})

        # curated app_settings
        if app_settings and app_settings.get('properties', None):
            curated_output['app_settings'] = dict()
            for item in app_settings['properties']:
                curated_output['app_settings'][item] = app_settings['properties'][item]

        # curated deploymenet_slot
        if deployment_slot:
            curated_output['deployment_slot'] = deployment_slot

        # ftp_publish_url
        if ftp_publish_url:
            curated_output['ftp_publish_url'] = ftp_publish_url

        # curated publish credentials
        if publish_credentials and self.return_publish_profile:
            curated_output['publishing_username'] = publish_credentials.publishing_user_name
            curated_output['publishing_password'] = publish_credentials.publishing_password
        return curated_output


def main():
    AzureRMWebAppInfo()


if __name__ == '__main__':
    main()
