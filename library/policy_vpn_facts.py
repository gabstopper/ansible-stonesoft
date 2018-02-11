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

options:
  expand:
    description:
      - Optionally expand element attributes that contain only href. You can also
        specify the name of a central gateway or satellite gateway to have it's
        contents expanded also.
    type: list
    choices:
      - vpn_profile
  
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
    sample: [{
        "name": "mynewvpn", 
        "type": "vpn"
    }]

policy_vpn:
    description: Return policy VPN details using filter
    returned: always
    type: list
    sample: [
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

from ansible.module_utils.six import string_types
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    format_element)


try:
    from smc.vpn.policy import PolicyVPN
except ImportError:
    pass


def to_dict(vpn, expand=None):
    """
    Flatten the policy VPN
    
    :param policy_vpn PolicyVPN
    :return dict
    """
    expand = expand if expand else []
    
    gateway_cache = {} # Cache gateways to reduce repetitive queries
    vpn.open()
    if 'vpn_profile' in expand:
        vpn.data['vpn_profile'] = format_element(vpn.vpn_profile)

    central = []
    for cgw in vpn.central_gateway_node:
        gateway_cache[cgw.href] = cgw
        gateway_cache[cgw.gateway.href] = cgw.gateway
        
        vpn_site = []
        for site in cgw.enabled_sites:
            if cgw.gateway.name in expand:
                site.data['site_element'] = [format_element(s) for s in site.vpn_site.site_element]
                vpn_site.append(format_element(site))
            else:
                vpn_site.append(format_element(site.vpn_site))

        central.append({'name': cgw.gateway.name, 'type': cgw.gateway.typeof, 'vpn_site': vpn_site})
    
    satellite = []
    for sgw in vpn.satellite_gateway_node:
        gateway_cache[sgw.href] = sgw
        gateway_cache[sgw.gateway.href] = sgw.gateway
        
        vpn_site = []
        for site in sgw.enabled_sites:
            if sgw.gateway.name in expand:
                site.data['site_element'] = [format_element(s) for s in site.vpn_site.site_element]
                vpn_site.append(format_element(site))
            else:
                vpn_site.append(format_element(site.vpn_site))

        satellite.append({'name': sgw.gateway.name, 'type': sgw.gateway.typeof, 'vpn_site': vpn_site})
    
    gateway_tunnel = []
    
    for tunnel in vpn.tunnels:
        tunnel_map = {}
        
        tunnela = gateway_cache.get(tunnel.data.get('gateway_node_1')).gateway
        tunnelb = gateway_cache.get(tunnel.data.get('gateway_node_2')).gateway
       
        tunnel_map.update(
            tunnel_side_a=tunnela.name,
            tunnel_side_a_type=tunnela.typeof,
            tunnel_side_b=tunnelb.name,
            tunnel_side_b_type=tunnelb.typeof,
            enabled=tunnel.enabled)
    
        gateway_tunnel.append(tunnel_map)

    vpn.data.update(central_gateway=central, satellite_gateway=satellite,
                    gateway_tunnel=gateway_tunnel)       
    vpn.close()
    return format_element(vpn)


class PolicyVPNFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            expand=dict(type='list', default=[])
        )
        self.element = 'vpn'
        self.limit = None
        self.filter = None
        self.expand = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                policy_vpn=[]
            )
        )
        super(PolicyVPNFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        for specified in self.expand:
            if not isinstance(specified, string_types):
                self.fail(msg='Expandable attributes should be in string format, got: {}'.format(
                    type(specified)))

        result = self.search_by_type(PolicyVPN)
        # Search by specific element type
        if self.filter:    
            elements = [to_dict(element, self.expand) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts']['policy_vpn'] = elements
        return self.results

def main():
    PolicyVPNFacts()
    
if __name__ == '__main__':
    main()
