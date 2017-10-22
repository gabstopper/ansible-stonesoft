"""
Base spec for Stonesoft Management Center connections. This is a session
that will be re-used for multiple operations against the management
server. When running a playbook, be sure to disconnect the session once
complete.
"""

import traceback
from ansible.module_utils.basic import AnsibleModule


try:
    from smc import session
    from smc.base.collection import Search
    from smc.api.exceptions import ConfigLoadError, SMCException
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def smc_argument_spec():
    return dict(
        smc_address=dict(type='str'),
        smc_api_key=dict(type='str', no_log=True),
        smc_api_version=dict(type='str'),
        smc_timeout=dict(default=30, type='int'),
        smc_domain=dict(type='str'),
        smc_alt_filepath=dict(type='str'),
        smc_extra_args=dict(type='dict')
    )


def fact_argument_spec():
    return dict(
        filter=dict(type='str'),
        limit=dict(default=0, type='int'),
        exact_match=dict(default=False, type='bool'),
        case_sensitive=dict(default=True, type='bool')
    )


class StonesoftModuleBase(object):
    def __init__(self, module_args, required_if=None, bypass_checks=False,
                 no_log=False, check_invalid_arguments=True,
                 mutually_exclusive=None, required_together=None,
                 required_one_of=None, add_file_common_args=False,
                 supports_check_mode=False, is_fact=False):
        
        argument_spec = smc_argument_spec()
        if is_fact:
            argument_spec.update(fact_argument_spec())
        argument_spec.update(module_args)
        
        self.module = AnsibleModule(
            argument_spec=argument_spec,
            required_if=required_if,
            bypass_checks=bypass_checks,
            no_log=no_log,
            check_invalid_arguments=check_invalid_arguments,
            mutually_exclusive=mutually_exclusive,
            required_together=required_together,
            required_one_of=required_one_of,
            add_file_common_args=add_file_common_args,
            supports_check_mode=supports_check_mode)
        
        if not HAS_LIB:
            self.module.fail_json(msg='Could not import smc-python required by this module')
            
        self.connect(self.module.params)
        
        result = self.exec_module(**self.module.params)
        self.success(**result)
    
    def connect(self, params):
        # Get the SMC connection. If the credentials are provided in the module,
        # then use them. Otherwise credentials gathering falls back to using
        # smc-python native methods:
        try:
            if params.get('smc_address') and params.get('smc_api_key'):
                extra_args = params.get('smc_extra_args')
                # When connection parameters are defined, alt_filepath is ignored.
                session.login(
                    url=params.get('smc_address'),
                    api_key=params.get('smc_api_key'),
                    api_version=params.get('smc_api_version'),
                    timeout=params.get('smc_timeout'),
                    domain=params.get('smc_domain'),
                    **(extra_args or {}))
            elif params.get('smc_alt_filepath'):
                # User specified to look in file
                session.login(alt_filepath=params['smc_alt_filepath'])
            else:
                # From user ~.smcrc or environment
                session.login()
        
        except (ConfigLoadError, SMCException) as err:
            self.fail(msg=str(err), exception=traceback.format_exc())

    def disconnect(self):
        try:
            session.logout()
        except SMCException:
            pass
    
    def exec_module(self):
        self.fail(msg='Sub-modules should implement exec_module. Called from: {}'.format(self.__class__.__name__))
    
    def search_by_context(self):
        # Only used by fact modules. Fact modules need to implement a single
        # attribute `element` that identifies the SMC entry point used for
        # the search. See engine_facts for an example.
        # This is a generic iterator using SMC context_filters
        if self.filter:
            # Find specific engine
            iterator = Search.objects\
                .context_filter(self.element)\
                .filter(self.filter,
                        exact_match=self.exact_match,
                        case_sensitive=self.case_sensitive)
                    
        else:
            # Find all engines
            iterator = Search.objects.context_filter(self.element)
        
        if self.limit >= 1:
            iterator = iterator.limit(self.limit)
               
        return list(iterator)
    
    def search_by_type(self, typeof):
        # Only used by fact modules. Fact modules need to implement a single
        # attribute `element` that identifies the SMC entry point used for
        # the search. See engine_facts for an example.
        # This is an iterator by the specific SMC element type
        if self.filter:
            iterator = typeof.objects\
                .filter(self.filter,
                        exact_match=self.exact_match,
                        case_sensitive=self.case_sensitive)
        else:
            iterator = typeof.objects.all()
        
        if self.limit >= 1:
            iterator = iterator.limit(self.limit)
        
        return list(iterator)

    def fail(self, msg, **kwargs):
        self.disconnect()
        self.module.fail_json(msg=msg, **kwargs)
        
    def success(self, **result):
        self.disconnect()
        self.module.exit_json(**result)
        
        

