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
module: vpn_external_gw_facts
short_description: Facts about external VPN gateways
description:
  - An external vpn gateway is a non-SMC managed endpoint used for
    terminating a VPN. It defines the remote side networks and settings
    specific to handling VPN.
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
- name: Return all external gateways
  vpn_external_gw_facts:

- name: Return external gateway configuration using filter
  vpn_external_gw_facts:
    filter: extgw      
'''


RETURN = '''
vpn_gateway:
    description: Return policies with 'Layer 3' as filter
    returned: always
    type: list
    example: [{
        "comment": null, 
        "external_endpoint": [{
            "address": "1.1.1.1", 
            "balancing_mode": "active", 
            "dynamic": false, 
            "enabled": true, 
            "force_nat_t": false, 
            "nat_t": true
        }, 
        {
            "address": null, 
            "balancing_mode": "active", 
            "dynamic": true, 
            "enabled": false, 
            "force_nat_t": false, 
            "nat_t": true
        }], 
        "name": "newextgw", 
        "tags": ["footag"], 
        "type": "external_gateway", 
        "vpn_sites": [{
            "name": "newextgw", 
            "values": [
                {
                    "name": "network-4.4.4.0/24", 
                    "type": "network"
                }, 
                {
                    "name": "network-3.3.3.0/24", 
                    "type": "network"
                }, 
                {
                    "name": "172.18.1.254", 
                    "type": "host"
                }
            ]
        }]
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.vpn.elements import ExternalGateway
except ImportError:
    pass


def gw_dict_from_obj(element):
    """
    Resolve the gateway to the supported types and return a
    dict with the values of defined attributes
    
    :param Element element
    """
    elem = {
        'name': element.name,
        'type': element.typeof,
        'comment': getattr(element, 'comment', None),
        'external_endpoint': [],
        'vpn_sites': [],
        'tags': []
    }
    
    for endpoint in element.external_endpoint.all():
        elem['external_endpoint'].append(
            dict(address=getattr(endpoint, 'address', None),
                 dynamic=getattr(endpoint, 'dynamic', False),
                 enabled=endpoint.enabled,
                 nat_t=getattr(endpoint, 'nat_t', False),
                 force_nat_t=getattr(endpoint, 'force_nat_t', False),
                 balancing_mode=endpoint.balancing_mode))
    
    for site in element.vpn_site.all():
        site_list = []
        for sites in site.site_element:
            site_list.append(
                dict(name=sites.name,
                     type=sites.typeof))
        
        elem['vpn_sites'].append(
            dict(name=site.name, values=site_list))
        
    for tag in element.categories:
        elem['tags'].append(tag.name)
    
    return elem


class ExternalGWFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.element = 'external_gateway'
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                vpn_gateway=[]
            )
        )
        
        super(ExternalGWFacts, self).__init__({}, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_type(ExternalGateway)
        # Search by specific element type
        if self.filter:    
            elements = [gw_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'vpn_gateway': elements}
        return self.results

def main():
    ExternalGWFacts()
    
if __name__ == '__main__':
    main()
