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
module: firewall_rule
short_description: Create, modify or delete a firewall rule
description:
  - Firewall rules can be added or removed from either a top level policy
    or a sub-policy. When creating the rule, if source/destination or service
    is not provided, the value will be set to 'none' and the rule will end up
    being skipped. In addition, after making a rule change, a policy refresh
    is required.

version_added: '2.5'

options:
  name:
    description:
      - A unique name for the rule. Rules are searchable by name so this should
        be something that represents the purpose of the rule.
    required: true
    type: str
  policy:
    description:
      - Name of the policy for the rule. This is required if I(sub_policy)
        is not set.
    type: str
  sub_policy:
    description:
      - Name of the sub policy for the rule. This is required if I(policy) is
        not set.
    type: str
  source:
    description:
      - Source elements to add to the rule. Elements need to specify the type of
        element to add. If source is not provided, the rule source cell will be
        set to none and the rule will be disabled.
    type: list
    default: 'none'
    suboptions:
    
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.policy.layer3 import FirewallSubPolicy
    from smc.api.exceptions import SMCException
except ImportError:
    pass


NETWORK_ELEMENTS = ['host', 'network', 'address_range', 'router', 'alias',
                    'domain_name', 'interface_zone', 'group', 'ip_list',
                    'country', 'engine']

            
class FirewallRule(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            policy=dict(type='str'),
            sub_policy=dict(type='str'),
            source=dict(type='list'),
            destination=dict(type='list'),
            action=dict(type='str', choices=[
                'allow', 'discard', 'refuse', 'continue', 'jump', 'use_vpn', 'apply_blacklist']),
            service=dict(type='list'),
            get_or_create=dict(default=True, type='bool'),
            jump_policy=dict(type='str'),
            vpn_policy=dict(type='str'),
            blacklist_target=dict(type='str'),
            logging=dict(type='str'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.policy = None
        self.sub_policy = None
        self.source = None
        self.destination = None
        self.action = None
        self.service = None
        self.get_or_create = None
        self.jump_policy = None
        self.vpn_policy = None
        self.blacklist_target = None
        
        mutually_exclusive = [
            ['policy', 'sub_policy'],
        ]
        
        required_one_of = [
            [ 'policy', 'sub_policy' ]
        ]
        
        required_if=([
            ('action', 'jump', ['jump_policy']),
            ('action', 'use_vpn', ['vpn_policy']),
            ('action', 'apply_blacklist', ['blacklist_target'])
        ])
        
        self.results = dict(
            changed=False
        )
        super(FirewallRule, self).__init__(self.module_args,
            mutually_exclusive=mutually_exclusive, required_one_of=required_one_of,
            required_if=required_if)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:
            if self.policy:
                policy = FirewallPolicy.get(self.policy)
            else:
                policy = FirewallSubPolicy.get(self.sub_policy)
            
            if state == 'present':
                pass

            elif state == 'absent':
                pass

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def _valid_network_element(self, elements):
        for element in elements:
            if not any(key in NETWORK_ELEMENTS for key in element.keys()):
                self.fail(msg='Missing or invalid network element type '
                    'specified. Valid types: %s' % NETWORK_ELEMENTS)
    
            

def main():
    FirewallRule()
    
if __name__ == '__main__':
    main()
    