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
module: network_element_facts
short_description: Facts about networks elements in the SMC
description:
  - Network elements can be used as references in many areas of the
    configuration. This fact module provides the ability to retrieve
    information related to elements and their values.
version_added: '2.5'

options:
  element:
    description:
      - Type of network element to retrieve
    required: false
    default: '*'
    choices:
      - host
      - network
      - router
      - address_range
      - zone
      - domain_name
    type: str
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: All network elements, limit result to 10
  network_element_facts:
    limit: 10

- name: Find all hosts with an IP value of 1.1.1.1 
  network_element_facts:
    limit: 0
    element: host
    filter: 1.1.1.1

- name: Find an address range including 1.1.1.1
  network_element_facts:
    limit: 10
    element: address_range
    filter: 1.1.1.1
'''


RETURN = '''
elements:
    description: All elements, no filter
    returned: always
    type: list
    example: [{
        "name": "Any network", 
        "type": "network"
        }, 
        {
        "name": "akamaiedge.com", 
        "type": "domain_name"
    }]

elements:
    description: Return from all elements using filter of 10.10.10
    returned: always
    type: list    
    example: [{
        "comment": null, 
        "ipv4_network": "0.0.0.0/0", 
        "ipv6_network": "::/0", 
        "name": "Any network", 
        "type": "network"
        }, 
        {
        "name": "myfirewall", 
        "type": "single_fw"
        }, 
        {
        "comment": null, 
        "ipv4_network": "10.0.0.0/8", 
        "ipv6_network": null, 
        "name": "private-10.0.0.0/8", 
        "type": "network"
        }, 
        {
        "comment": null, 
        "ipv4_network": "10.10.10.0/24", 
        "ipv6_network": null, 
        "name": "network-10.10.10.0/24", 
        "type": "network"
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    import smc.elements.network as network
except ImportError:
    pass


ELEMENT_TYPES = dict(
    host=dict(type=network.Host, attr=['address', 'ipv6_address', 'secondary']),
    network=dict(type=network.Network, attr=['ipv4_network', 'ipv6_network']),
    address_range=dict(type=network.AddressRange, attr=['ip_range']),
    router=dict(type=network.Router, attr=['address', 'secondary', 'ipv6_address']),
    zone=dict(type=network.Zone),
    domain_name=dict(type=network.DomainName))


def element_dict_from_obj(element):
    """
    Resolve the element to the supported types and return a dict
    with the values of defined attributes
    
    :param Element element
    """
    known = ELEMENT_TYPES.get(element.typeof)
    if known:
        elem = {
            'name': element.name,
            'type': element.typeof,
            'comment': getattr(element, 'comment', None)}
    else:
        return dict(name=element.name, type=element.typeof)
    
    for attribute in known.get('attr', []):
        elem[attribute] = getattr(element, attribute, None)
    return elem

    
class NetworkElementFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(type='str', choices=list(ELEMENT_TYPES.keys()))
        )
    
        self.element = None
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                elements=[]
            )
        )
        
        super(NetworkElementFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        # Search by specific element type
        if self.element:
            result = self.search_by_type(ELEMENT_TYPES.get(self.element)['type'])
        else:
            self.element = 'network_elements'
            result = self.search_by_context()
        
        if self.filter:    
            elements = [element_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'elements': elements}
        return self.results

def main():
    NetworkElementFacts()
    
if __name__ == '__main__':
    main()