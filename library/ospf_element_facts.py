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
module: ospf_element_facts
short_description: Facts about OSPF based elements in the SMC
description:
  - BGP elements are the building blocks to building a BGP configuration on
    a layer 3 engine. Use this module to obtain available elements and their
    values.

version_added: '2.5'

options:
  element:
    description:
      - Type of OSPF element to retrieve
    required: true
    choices:
      - ospfv2_area
      - ospfv2_profile
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
- name: Facts about OSPF elements
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Find all OSPF v2 areas
    ospf_element_facts:
      element: ospfv2_area

  - name: Find a specific OSPF area with details
    ospf_element_facts:
      element: ospfv2_area
      filter: myarea
  
  - name: Find an OSPF profile containing name 'Default'
    ospf_element_facts:
      element: ospfv2_profile
      filter: Default

  - name: Get details for autonomous system myas and save as yaml
    register: results
    ospf_element_facts:
      smc_logging:
        level: 10
        path: ansible-smc.log
      element: ospfv2_profile
      filter: myprofile
      exact_match: false
      as_yaml: true

  - name: Write the yaml using a jinja template
    template: src=templates/facts_yaml.j2 dest=./ospf_element.yml
    vars:
      playbook: ospf_element
'''

RETURN = '''
elements:
    description: List all OSPF Areas
    returned: always
    type: list    
    sample: [
        {
            "name": "myarea", 
            "type": "ospfv2_area"
        }, 
        {
            "name": "myarea2", 
            "type": "ospfv2_area"
        }, 
        {
            "name": "foo", 
            "type": "ospfv2_area"
        }]

elements:
    description: List a specific OSPF profile
    returned: always
    type: list
    sample: [
    {
        "comment": "added by ansible", 
        "default_metric": 123, 
        "domain_settings_ref": "Default OSPFv2 Domain Settings", 
        "external_distance": 110, 
        "inter_distance": 130, 
        "intra_distance": 110, 
        "name": "myprofile", 
        "redistribution_entry": [
            {
                "enabled": true, 
                "metric_type": "external_1", 
                "type": "bgp"
            }, 
            {
                "enabled": true, 
                "filter": {
                    "route_map": [
                        "myroutemap"
                    ]
                }, 
                "metric": 2, 
                "metric_type": "external_1", 
                "type": "static"
            }, 
            {
                "enabled": true, 
                "filter": {
                    "ip_access_list": [
                        "myacl"
                    ]
                }, 
                "metric_type": "external_2", 
                "type": "connected"
            }, 
            {
                "enabled": false, 
                "metric_type": "external_1", 
                "type": "kernel"
            }, 
            {
                "enabled": false, 
                "metric_type": "external_1", 
                "type": "default_originate"
            }]
    }]


'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase, format_element


try:
    from smc.routing.route_map import RouteMap
    from smc.routing.access_list import IPAccessList
    from smc.base.model import lookup_class
except ImportError:
    pass


ospf_elements = ('ospfv2_area', 'ospfv2_interface_settings', 'ospfv2_key_chain',
    'ospfv2_profile', 'ospfv2_domain_settings')


def area_to_yaml(area):
    yaml = {}
    yaml.update(
        name=area.name,
        comment=area.comment,
        area_type=area.area_type,
        interface_settings_ref=area.interface_settings_ref.name)
    
    for filt in ('inbound_filters', 'outbound_filters'):
        if len(getattr(area, '%s_ref' % filt)):
            for _filt in getattr(area, filt):
                _filter = {_filt.typeof: [_filt.name]}
                yaml.setdefault(filt, {}).update(_filter)
            
    return yaml
        

def profile_to_yaml(profile):
    yaml = {}
    yaml.update(
        name=profile.name,
        comment=profile.comment,
        external_distance=profile.external_distance,
        inter_distance=profile.inter_distance,
        intra_distance=profile.intra_distance,
        domain_settings_ref=profile.domain_settings_ref.name,
        default_metric=profile.data.get('default_metric', None)
        )
    redist_entries = []
    for redist in profile.data.get('redistribution_entry', []):
        filter_type = redist.pop('filter_type', 'none')
        if filter_type != 'none':
            if filter_type == 'route_map_policy':
                redist.update(
                    filter={'route_map': [RouteMap.from_href(
                        redist.pop('redistribution_rm_ref')).name]})
            elif filter_type == 'access_list':
                redist.update(
                    filter={'ip_access_list': [IPAccessList.from_href(
                        redist.pop('redistribution_filter_ref')).name]})
        redist_entries.append(redist)
    yaml.update(redistribution_entry=redist_entries)
    return yaml


def convert_to_dict(element):
    if element.typeof == 'ospfv2_area':
        return {element.typeof: area_to_yaml(element)}
    elif element.typeof == 'ospfv2_profile':
        return {element.typeof: profile_to_yaml(element)}
    else:
        return {element.typeof: format_element(element)}
    

class OSPFElementFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(required=True, type='str', choices=list(ospf_elements))
        )
    
        self.element = None
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.exact_match = None
        self.case_sensitive = None
        
        required_if=([
            ('as_yaml', True, ['filter'])])
        
        self.results = dict(
            ansible_facts=dict(
                ospf_element=[]
            )
        )
        super(OSPFElementFacts, self).__init__(self.module_args, required_if=required_if,
                                               is_fact=True)
        
    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_type(lookup_class(self.element))
        if self.filter:
            if self.as_yaml:
                elements = [convert_to_dict(element) for element in result
                            if element.name == self.filter]
            else:
                elements = [convert_to_dict(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts']['ospf_element'] = [{'elements': elements}]\
            if elements else []
        
        return self.results


def main():
    OSPFElementFacts()
    
if __name__ == '__main__':
    main()
