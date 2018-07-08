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
module: bgp_element_facts
short_description: Facts about BGP based elements in the SMC
description:
  - BGP elements are the building blocks to building a BGP configuration on
    a layer 3 engine. Use this module to obtain available elements and their
    values.

version_added: '2.5'

options:
  element:
    description:
      - Type of bgp element to retrieve
    required: true
    choices:
      - ip_access_list
      - ip_prefix_list
      - ipv6_access_list
      - ipv6_prefix_list 
      - as_path_access_list
      - community_access_list
      - extended_community_access_list
      - external_bgp_peer
      - bgp_peering
      - autonomous_system
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
- name: BGP Facts
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Retrieve all data about ane external bgp peer
    bgp_facts:
      element: external_bgp_peer
      filter: externalpeer

- name: BGP Facts
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Return all data about specified autonomous system
    bgp_facts:
      element: autonomous_system
      filter: remoteas
 
- name: Routing facts about an engine
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Find details about specific profile
    bgp_facts:
      element: bgp_profile
      filter: Default BGP Profile
      case_sensitive: no
'''

RETURN = '''
elements:
    description: List all BGP Profiles
    returned: always
    type: list    
    sample: [{
        "name": "Default BGP Profile", 
        "type": "bgp_profile"
    }]

elements:
    description: Details of a specific autonomous system
    returned: always
    type: list    
    sample: [{
        "as_number": 12000, 
        "comment": null, 
        "name": "myas", 
        "type": "autonomous_system"
    }]

elements:
    description: Details about BGP Peering profile
    returned: always
    type: list    
    sample: [{
        "comment": null, 
        "connected_check": "disabled", 
        "connection_profile": {
            "connect_retry": 120, 
            "name": "Default BGP Connection Profile", 
            "session_hold_timer": 180, 
            "session_keep_alive": 60, 
            "type": "bgp_connection_profile"
        }, 
        "default_originate": false, 
        "dont_capability_negotiate": false, 
        "local_as_option": "not_set", 
        "max_prefix_option": "not_enabled", 
        "name": "mypeering", 
        "next_hop_self": true, 
        "orf_option": "disabled", 
        "override_capability": false, 
        "read_only": false, 
        "remove_private_as": false, 
        "route_reflector_client": false, 
        "send_community": "no", 
        "soft_reconfiguration": true, 
        "system": false, 
        "ttl_option": "disabled", 
        "type": "bgp_peering"
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.base.model import lookup_class
except ImportError:
    pass


bgp_elements = (
    'ip_access_list', 'ip_prefix_list', 'ipv6_access_list',
    'ipv6_prefix_list', 'as_path_access_list', 'community_access_list',
    'extended_community_access_list', 'external_bgp_peer', 'bgp_peering',
    'autonomous_system'
)


def serialize_namedtuple_obj(element):
    """
    Pass in instance of the access or prefix list class obtained
    Element.from_href and iterate through the entries, returning
    as a dict
    """
    return {element.typeof:
        {'name': element.name,
         'comment': element.comment,
         'entries': [entry._asdict() for entry in element]
         }
    }


def convert_to_dict(element):
    """
    Convert to dict takes an instance returned from the search query
    and converts it into a dict.
    
    :rtype: dict
    """
    if 'access_list' in element.typeof or 'prefix_list' in element.typeof:
        return serialize_namedtuple_obj(element)
    elif 'autonomous_system' in element.typeof:
        return as_system_dict(element)
    elif 'bgp_peering' in element.typeof:
        return bgp_peering_dict(element)
    elif 'external_bgp_peer' in element.typeof:
        return bgp_peer_dict(element)
    return {}


def as_system_dict(element):
    """
    Autonomous System representation.
    """
    return {'autonomous_system': {
        'name': element.name,
        'as_number': element.as_number,
        'comment': element.comment
        }
    }
        

def bgp_peer_dict(element):
    """
    External BGP Peer representation
    """
    return {'external_bgp_peer': {
        'name': element.name,
        'neighbor_ip': element.neighbor_ip,
        'neighbor_as': element.neighbor_as.name,
        'neighbor_port': element.neighbor_port,
        'comment': element.comment
        }
    }


def bgp_peering_dict(element):
    """
    Representation of a BGP Peering
    """
    return {'bgp_peering': {
        'name': element.name,
        'comment': element.comment}}



class BGPElementFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(required=True, type='str', choices=list(bgp_elements))
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
                bgp_element=[]
            )
        )
        super(BGPElementFacts, self).__init__(self.module_args, required_if=required_if,
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
        
        self.results['ansible_facts']['bgp_element'] = [{'elements': elements}]\
            if elements else []
        return self.results
    
def main():
    BGPElementFacts()
    
if __name__ == '__main__':
    main()
