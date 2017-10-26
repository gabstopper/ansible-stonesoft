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
module: l3fw_policy_facts
short_description: Facts about layer 3 firewall policies
description:
  - Layer 3 firewall policies used on firewall based engines. Also provides information
    on linked policies such as inspection and the base level template.
version_added: '2.5'
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Show all policies
  l3fw_policy_facts:
    
- name: Show policy information for policies contained 'Layer 3'
    l3fw_policy_facts:
      filter: Layer 3
'''


RETURN = '''
policies:
    description: Return all policies
    returned: always
    type: list
    example: [{
        "name": "Master Engine Policy", 
        "type": "fw_policy"
        },
        {
        "name": "Layer 3 Router Policy", 
        "type": "fw_policy"
    }]

policies:
    description: Return policies with 'Layer 3' as filter
    returned: always
    type: list
    example: [{
        "comment": null, 
        "inspection_policy": "High-Security Inspection Policy",
        "file_filtering_policy": "Legacy Anti-Malware",
        "name": "Layer 3 Virtual FW Policy", 
        "tags": ['footag'], 
        "template": "Firewall Inspection Template", 
        "type": "fw_policy"
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.policy.layer3 import FirewallPolicy
except ImportError:
    pass


def policy_dict_from_obj(element):
    """
    Resolve the category to the supported types and return a dict
    with the values of defined attributes
    
    :param Element element
    """
    elem = {
        'name': element.name,
        'type': element.typeof,
        'tags': [],
        'template': element.template.name,
        'inspection_policy': element.inspection_policy.name,
        'file_filtering_policy': element.file_filtering_policy.name 
            if element.file_filtering_policy else None,
        'comment': getattr(element, 'comment', None)}
    
    for tag in element.categories:
        elem['tags'].append(tag.name)
    
    return elem


class FWPolicyFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.element = 'fw_policy'
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                policies=[]
            )
        )
        super(FWPolicyFacts, self).__init__({}, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_type(FirewallPolicy)
        # Search by specific element type
        if self.filter:    
            elements = [policy_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'policies': elements}
        return self.results

def main():
    FWPolicyFacts()
    
if __name__ == '__main__':
    main()