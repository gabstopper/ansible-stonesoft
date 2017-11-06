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
module: service_element_facts
short_description: Facts about service elements in the SMC
description:
  - Service elements can be used as references in many areas of the
    configuration. This fact module provides the ability to retrieve
    information related to elements and their values.

version_added: '2.5'
    
options:
  element:
    description:
      - Type of service element to retrieve
    required: false
    default: '*'
    choices:
      - service_group
      - icmp_service
      - protocol
      - rpc_service
      - icmp_service_group
      - url_category
      - application_situation
      - ip_service_group
      - icmp_ipv6_service
      - ip_service
      - tcp_service
      - tcp_service_group
      - udp_service
      - udp_service_group
      - ethernet_service
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
- name: Return all services with limit
  service_element_facts:
    limit: 10

- name: Return only tcp service elements
  service_element_facts:
    element: tcp_service

- name: Return services with 80 in the value (will match defined ports)
  service_element_facts:
    limit: 10
    element: tcp_service
    filter: 80

- name: Find applications related to facebook
  service_element_facts:
    element: application_situation
    filter: facebook
'''    


RETURN = '''
services:
    description: All UDP Services, no filter
    returned: always
    type: list
    sample: [{
        "name": "api-udp1", 
        "type": "udp_service"
        }, 
        {
        "name": "Destination Port 0 (UDP)", 
        "type": "udp_service"
    }]

services:
    description: All TCP services with filter of '80'
    returned: always
    type: list    
    sample: [{
        "comment": "", 
        "max_dst_port": null, 
        "min_dst_port": 443, 
        "name": "tcp80443", 
        "type": "tcp_service"
        }, 
        {
        "comment": "Element created for NAT Service", 
        "max_dst_port": null, 
        "min_dst_port": 80, 
        "name": "HTTP_tcp_port_80", 
        "type": "tcp_service"
    }]
'''

from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    service_type_dict,
    element_dict_from_obj,
    ro_service_type_dict)


ELEMENT_TYPES = service_type_dict()
ELEMENT_TYPES.update(ro_service_type_dict())


class ServiceFacts(StonesoftModuleBase):
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
                services=[]
            )
        )
        super(ServiceFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        # Search by specific element type
        if self.element:
            result = self.search_by_type(ELEMENT_TYPES.get(self.element)['type'])
        else:
            self.element = 'services_and_applications'
            result = self.search_by_context()
        
        if self.filter:
            elements = [element_dict_from_obj(element, ELEMENT_TYPES) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'services': elements}
        return self.results

def main():
    ServiceFacts()
    
if __name__ == '__main__':
    main()

