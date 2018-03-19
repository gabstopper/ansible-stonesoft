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
      - autonomous_system
      - bgp_profile
      - external_bgp_peer
      - bgp_peering
      - bgp_connection_profile
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
    import smc.routing.bgp as bgp
except ImportError:
    pass


def as_system_dict(data):
    """
    Autonomous System representation.
    """
    return dict(
        name=data.name,
        type=data.typeof,
        as_number=data.as_number)
    

def bgp_peer_dict(data):
    """
    External BGP Peer representation
    """
    return dict(
        neighbor_ip=data.neighbor_ip,
        neighbor_port=data.neighbor_port,
        neighbor_as= as_system_dict(data.neighbor_as))


def bgp_profile_dict(data):
    """
    BGP Profile representation
    """
    return dict(
        port=data.port,
        internal_distance=data.internal_distance,
        external_distance=data.external_distance,
        local_distance=data.local_distance,
        subnet_distance=data.subnet_distance)


def bgp_cxn_profile_dict(data):
    """
    Representation of BGP Connection Profile
    """
    return dict(
        name=data.name,
        type=data.typeof,
        connect_retry=data.connect_retry,
        session_hold_timer=data.session_hold_timer,
        session_keep_alive=data.session_keep_alive)


def bgp_peering_dict(data):
    """
    Representation of a BGP Peering
    """
    for attr in ['key', 'link']:
        data.data.pop(attr, None)
    data.data.update(
        connection_profile=bgp_cxn_profile_dict(data.connection_profile))
    return data.data

    
ELEMENT_TYPES = dict(
    autonomous_system=dict(type=bgp.AutonomousSystem, func=as_system_dict),
    bgp_profile=dict(type=bgp.BGPProfile, func=bgp_profile_dict),
    external_bgp_peer=dict(type=bgp.ExternalBGPPeer, func=bgp_peer_dict),
    bgp_peering=dict(type=bgp.BGPPeering, func=bgp_peering_dict),
    bgp_connection_profile=dict(type=bgp.BGPConnectionProfile, func=bgp_cxn_profile_dict))


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
        
        elem.update(known['func'](element))
        return elem
    else:
        return dict(name=element.name, type=element.typeof)


class BGPFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(required=True, type='str', choices=list(ELEMENT_TYPES.keys()))
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
        super(BGPFacts, self).__init__(self.module_args, is_fact=True)
        
    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        # Search by specific element type
        result = self.search_by_type(ELEMENT_TYPES.get(self.element)['type'])
        
        if self.filter:    
            elements = [element_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'elements': elements}
        return self.results

def main():
    BGPFacts()
    
if __name__ == '__main__':
    main()
