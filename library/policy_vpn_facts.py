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
module: policy_vpn_facts
short_description: Facts about configured Policy VPNs
description:
  - A Policy VPN provides IPSEC functionality between either SMC managed or non
    managed devices. This will represent central and satllite gateways in the
    VPN configuration.
version_added: '2.5'
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


RETURN = '''
policy_vpn:
    description: Return all policy VPNs
    returned: always
    type: list
    example: [{
        "name": "mynewvpn", 
        "type": "vpn"
    }]

policy_vpn:
    description: Return policy VPN details using filter
    returned: always
    type: list
    example: [
        {
            "central_gateways": [
                {
                    "name": "ve-1 - Primary", 
                    "type": "internal_gateway"
                }, 
                {
                    "name": "sg_vm_vpn", 
                    "type": "internal_gateway"
                }, 
                {
                    "name": "ve-4 - Primary", 
                    "type": "internal_gateway"
                }
            ], 
            "comment": null, 
            "gateway_tunnel": [
                {
                    "enabled": true, 
                    "tunnel_side_a": "sg_vm_vpn", 
                    "tunnel_side_a_type": "internal_gateway", 
                    "tunnel_side_b": "ve-1 - Primary", 
                    "tunnel_side_b_type": "internal_gateway"
                }, 
                {
                    "enabled": true, 
                    "tunnel_side_a": "sg_vm_vpn", 
                    "tunnel_side_a_type": "internal_gateway", 
                    "tunnel_side_b": "ve-4 - Primary", 
                    "tunnel_side_b_type": "internal_gateway"
                }
            ], 
            "mobile_vpn_topology_mode": "None", 
            "name": "Amazon AWS", 
            "nat": true, 
            "satellite_gateways": [], 
            "tags": [], 
            "type": "vpn", 
            "vpn_profile": "VPN-A Suite"
        }
    ]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.vpn.policy import PolicyVPN
except ImportError:
    pass


def vpn_dict_from_obj(vpn):
    """
    Characteristics of the policy VPN
    
    :param PolicyVPN vpn
    """
    vpn.open()
    elem = {
        'name': vpn.name,
        'type': vpn.typeof,
        'comment': getattr(vpn, 'comment', None),
        'mobile_vpn_topology_mode': getattr(vpn, 'mobile_vpn_topology_mode', None),
        'nat': getattr(vpn, 'nat', False),
        'vpn_profile': vpn.vpn_profile.name,
        'central_gateways': [],
        'satellite_gateways': [],
        'gateway_tunnel': [],
        'tags': []
    }
    
    for tag in vpn.categories:
        elem['tags'].append(tag.name)
    
    for gw in vpn.central_gateway_node.all():
        elem['central_gateways'].append(
            dict(name=gw.name, type=gw.gateway.typeof))
    
    for gw in vpn.satellite_gateway_node.all():
        elem['satellite_gateways'].append(
            dict(name=gw.name, type=gw.gateway.typeof))
    
    # Mapped tunnels
    for tunnel in vpn.tunnels:
        tunnel_map = {}
        tunnela = tunnel.tunnel_side_a
        tunnelb = tunnel.tunnel_side_b
        
        # Gateways
        gw_tunnela = tunnela.gateway
        gw_tunnelb = tunnelb.gateway
        
        tunnel_map.update(
            tunnel_side_a=gw_tunnela.name,
            tunnel_side_a_type=gw_tunnela.typeof,
            tunnel_side_b=gw_tunnelb.name,
            tunnel_side_b_type=gw_tunnelb.typeof,
            enabled=tunnel.enabled
        )
        elem['gateway_tunnel'].append(tunnel_map)
    
    vpn.close()
    return elem


class PolicyVPNFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.element = 'vpn'
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                policy_vpn=[]
            )
        )
        
        super(PolicyVPNFacts, self).__init__({}, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_type(PolicyVPN)
        # Search by specific element type
        if self.filter:    
            elements = [vpn_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'policy_vpn': elements}
        return self.results

def main():
    PolicyVPNFacts()
    
if __name__ == '__main__':
    main()
