from ansible.errors import AnsibleError, AnsibleOptionsError

sdk_is_missing = False
try:
    from pam.secrets.server import (
      SecretServer,
      SecretServerError,
    )
except ImportError:
    sdk_is_missing = True
from ansible.utils.display import Display
from ansible.plugins.lookup import LookupBase


display = Display()


class LookupModule(LookupBase):
    @staticmethod
    def Client(server_parameters):
        return SecretServer(**server_parameters)

    def run(self, terms, variables, **kwargs):
        if sdk_is_missing:
            raise AnsibleError("python-pss-sdk must be installed to use this plugin")
        self.set_options(var_options=variables, direct=kwargs)
        secret_server = LookupModule.Client(
            {
                "base_url": terms[1],
                "api_key": terms[2],
            }
        )
        result = []
        for term in terms[0]:
             display.debug("pss_lookup term: %s" % term)
             try:
                 display.vvv(u"Secret Server lookup of Secret with ID %s" % term)
                 result.append({term:secret_server.get_pam_secret(term)})
             except SecretServerError as error:
                 raise AnsibleError("Secret Server lookup failure: %s" % error.message)
        return result
