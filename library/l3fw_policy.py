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
module: l3fw_policy
short_description: Create or delete layer 3 FW policies
description:
  - Top level module for creating and deleting firewall policies
version_added: '2.5'

options:
  name:
    description:
      - Name of the policy, required if I(action=create) or I(action=delete)
  policy_template:
    description:
      - An optional policy template to use when I(action=create). If no
        template is specified, a default policy template is assigned.
  tags:
    description:
      - Optional tags to add to the policy
    type: list

extends_documentation_fragment: stonesoft

requirements:
  - smc-python

author:
  - David LePage (@gabstopper)
'''

EXAMPLES = '''
# Create a new policy using the default Firewall Inspection Template
- name: create policy
  tasks:
  - name: add a firewall policy
    l3_policy:
      name: somepolicy
      tags:
        - footag

# Delete a policy
- name: Delete policy
  tasks:
  - name: Delete my policy
    l3_policy:
      name: somepolicy
      state: absent
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
msg:
  description: Simple description message
  returned: always
  type: string
  sample: Successfully created policy foo
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.api.exceptions import SMCException
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class StonesoftFWPolicy(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            policy_template=dict(type='str'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.policy_template = None
        
        self.results = dict(
            changed=False,
            msg=''
        )
        super(StonesoftFWPolicy, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if state == 'present':
            
            if not self.policy_template:
                self.policy_template = 'Firewall Inspection Template'
        
            try:
                policy = FirewallPolicy.create(name=self.name, template=self.policy_template)
                if self.tags:
                    policy.add_category(self.tags)
                    
            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successful creation of policy: %s, template: %s' % \
                                    (self.name, self.policy_template), changed=True)
            
        elif state == 'absent':
            try:
                FirewallPolicy(self.name).delete()
            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successfully deleted policy: %s' % self.name, changed=True)

        return self.results

    
def main():
    StonesoftFWPolicy()
    
if __name__ == '__main__':
    main()

