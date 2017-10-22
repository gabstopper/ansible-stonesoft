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
module: service_facts
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
      - protocol
      - tcp_service
      - udp_service
      - ip_service
      - icmp_service
      - url_category
      - icmp_ipv6_service
      - ethernet_service
      - application_situation
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
  service_facts:
    limit: 10

- name: Return only tcp service elements
  service_facts:
    element: tcp_service

- name: Return services with 80 in the value (will match defined ports)
  service_facts:
    limit: 10
    element: tcp_service
    filter: 80

- name: Find applications related to facebook
  service_facts:
    element: application_situation
    filter: facebook
'''    


RETURN = '''
services:
    description: All UDP Services, no filter
    returned: always
    type: list
    example: [{
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
    example: [{
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
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    import smc.elements.service as service
except ImportError:
    pass


ELEMENT_TYPES = dict(
    tcp_service=dict(type=service.TCPService, attr=['min_dst_port', 'max_dst_port']),
    udp_service=dict(type=service.UDPService, attr=['min_dst_port', 'max_dst_port']),
    application_situation=dict(type=service.ApplicationSituation, attr=['identifiable_with_tls_match']),
    icmp_service=dict(type=service.ICMPService, attr=['icmp_code', 'icmp_type']),
    icmp_ipv6_service=dict(type=service.ICMPIPv6Service, attr=['icmp_code', 'icmp_type']),
    ip_service=dict(type=service.IPService, attr=['protocol_number']),
    ethernet_service=dict(type=service.EthernetService, attr=['frame_type']),
    protocol=dict(type=service.Protocol),
    url_category=dict(type=service.URLCategory))


def service_dict_from_obj(element):
    """
    Resolve the service to the supported types and return a dict
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
            elements = [service_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'services': elements}
        return self.results

def main():
    ServiceFacts()
    
if __name__ == '__main__':
    main()

