#!/usr/bin/python
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: firewall_nat_rule
short_description: Create, modify or delete a firewall NAT rule
description:
  - Firewall NAT rules can be added or removed from either a top level policy
    or a sub-policy. Source, destination and service elements can be used and
    referenced by their type and name (they must be pre-created).

version_added: '2.5'
'''
import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache)


try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.policy.layer3 import FirewallSubPolicy
    from smc.api.exceptions import SMCException
except ImportError:
    pass


rule_targets = ('address_range', 'country', 'domain_name', 'expression', 'group', 'host',
    'ip_list', 'network', 'engine', 'router', 'netlink', 'interface_zone', 'alias')

service_targets = ('service_group', 'tcp_service_group', 'udp_service_group', 'ip_service_group',
    'icmp_service_group', 'tcp_service', 'udp_service', 'ip_service', 'ethernet_service', 'icmp_service')


def validate_rule(rule):
    """
    Validate the rule by checking fields that do not require a call
    to the SMC. Sources, Destinations and Services are not validated
    in this initial check.
    
    :param dict rule: firewall rule defined in yaml
    :return: None
    """
    if 'tag' not in rule and 'name' not in rule:
        raise Exception('A rule must have either a rule tag or a '
            'name field: %s' % rule)
    
    for nat in ('dynamic_src_nat', 'static_src_nat', 'static_dst_nat'):
        pass
    
    
class FirewallNATRule(StonesoftModuleBase):
    def __init__(self):
        self.module_args = dict(
            policy=dict(type='str'),
            sub_policy=dict(type='str'),
            rules=dict(type='list', default=[]),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.policy = None
        self.sub_policy = None
        self.rules = None
        
        mutually_exclusive = [
            ['policy', 'sub_policy'],
        ]
         
        required_one_of = [
            [ 'policy', 'sub_policy' ]
        ]
        
        self.results = dict(
            changed=False,
            state=[]
        )
        
        super(FirewallNATRule, self).__init__(self.module_args,
            mutually_exclusive=mutually_exclusive, required_one_of=required_one_of,
            supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:            
            # Now that we have valid option settings, we can hit the db
            if self.policy:
                policy = FirewallPolicy.get(self.policy)
            else:
                policy = FirewallSubPolicy.get(self.sub_policy)
            
            if state == 'present':
                
                for rule in self.rules:
                    try:
                        validate_rule(rule)
                    except Exception as e:
                        self.fail(msg=str(e))
                
                self.cache = Cache()
                        
                for rule in self.rules:
                    # Resolve elements if they exist, calls to SMC could happen here
                    if 'sources' in rule:
                        self.field_resolver(rule.get('sources'), rule_targets)
                    
                    if 'destinations' in rule:
                        self.field_resolver(rule.get('destinations'), rule_targets)
                    
                    if 'services' in rule:
                        self.field_resolver(rule.get('services'), service_targets)
                    
            
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def field_resolver(self, elements, types):
        """
        Field resolver, specific to retrieving network or service level
        elements in different formats. If elements are referencing existing
        elements, they will be loaded in the cache for retrieval.
        
        Format #1, as list (elements are expected to exist):
            - tcp_service:
                - service1
                - service2
        
        Format #2, as dict, only used for specifying any:
            any: true
        
        Format #3, if you have retrieved the rule and the sources, services,
        and destinations are in href format, pass through.
        
            - sources:
                - http://1.1.1.1/elements/host/1
                - http://1.1.1.1/elements/host/2
                ...
    
        .. note:: This is optimal if sources, destinations or services are
            not being changed as it will not result in queries to SMC. This
            is accomplished by not setting `expand` when running the facts
            module as_yaml.
            
        :param list elements: list of elements as parsed from YAML file
        :param dict type_dict: type dictionary for elements that should be
            supported for this run.
        """
        if isinstance(elements, dict):
            if 'any' in elements or 'none' in elements:
                return
            
            for name, value in elements.items():
                if name not in types:
                    self.fail(msg='Invalid element type specified: %s. Valid '
                        'types are: %s' % (name, list(types)))
                if not isinstance(value, list):
                    self.fail(msg='Elements specified for type: %s should be in list '
                        'format, got: %s' % (name, type(value)))
            
            self.cache.add_many([elements])

        elif isinstance(elements, list):
            for entry in elements:
                if not entry.startswith('http'):
                    self.fail(msg='List entry is expected to be the raw href of '
                        'the element. Received: %s' % entry)
                    
def main():
    FirewallNATRule()
    
if __name__ == '__main__':
    main()

        
