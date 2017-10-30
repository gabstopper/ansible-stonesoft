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
module: policy_vpn
short_description: Create, modify or delete Policy VPNs
description:
  - Manage a policy VPN. This module provides the ability to fully create
    a VPN, along with modifying central / satellite gateways as well as
    tags. Only satellite gateways, central gateways and tags can be deleted.
    All other options provided in the constructor can be modified or added.
version_added: '2.5'

options:
  name:
    description:
      - The name of the policy VPN
    required: true
  vpn_profile:
    description:
      - Optional VPN profile to use for this policy VPN
    default: 'VPN-A Suite'
  apply_nat:
    description:
      - Whether to apply NAT to this VPN. Doing so may require NAT rules be in place.
  central_gw:
    description:
      - Central gateways to add to the policy VPN. Can be SMC managed internal hosts or
        external gateways.
    suboptions:
      name:
        description:
          - Name of the central gateway to add
        type: str
        required: true
      type:
        description:
          - Type of element, either external gateway or internal SMC managed engine.
        choices:
          - internal_gateway
          - external_gateway
        type: str
        required: true
      preshared_key:
        description:
          - Set a preshared key. This is only required if the gateway is an external_gateway
  satellite_gw:
    description:
      - Central gateways to add to the policy VPN. Can be SMC managed internal hosts or
        external gateways.
    suboptions:
      name:
        description:
          - Name of the satellite gateway to add
        type: str
        required: true
      type:
        description:
          - Type of element, either external gateway or internal SMC managed engine.
        choices:
          - internal
          - external
        type: str
        required: true
      preshared_key:
        description:
          - Set a preshared key. This is only required if the gateway is an external_gateway
        type: str
  gateway_tunnel:
    description:
      - Used when modifying a specific gateway tunnel configuration. This can be used to
        change a preshared key or disable a specific tunnel
    suboptions:
      tunnel_side_a:
        description:
          - The A side of the tunnel. Use facts to retrieve this value.
        type: str
        required: true
      tunnel_side_b:
        description:
          - The B side of the tunnel. Use facts to retrieve this value.
        type: str
        required: true
      preshared_key:
        description:
          - Reset the preshared key for this tunnel
        type: str
      enabled:
        description:
          - Enable or disable this tunnel
        type: bool
  tags:
    description:
      - Optional tags to add to this engine
    type: list
  state:
    description:
      - Create or delete a firewall cluster
    required: false
    default: present
    choices:
      - present
      - absent

extends_documentation_fragment: stonesoft

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''
            

EXAMPLES = '''
- name: Add gateways to a policy VPN (VPN is created if it doesn't exist)
  policy_vpn:
    name: mynewvpn
    central_gw:
      - name: myfirewall
        type: internal_gateway
    satellite_gw:
      - name: newextgw
        type: external_gateway
    tags:
      - footag

# Retrieve tunnel_side_a and tunnel_side_b values by calling policy_vpn_facts
- name: Change a preshared key for existing tunnel and enable the tunnel
  policy_vpn:
    name: mynewvpn
    gateway_tunnel:
      - tunnel_side_a: anothergw
        tunnel_side_b: fw33 - Primary
        preshared_key: abc123
        enabled: yes
          
- name: Delete a single satellite gateway from this VPN
  policy_vpn:
    name: mynewvpn
    satellite_gw:
      - name: newextgw
        type: external_gateway
    state: absent

- name: Delete tags from a policy VPN
  policy_vpn:
    name: mynewvpn
    tags:
      - footag
    state: absent
    
- name: Delete the entire policy VPN
  policy_vpn:
    name: mynewvpn
    state: absent
'''


RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.vpn.policy import PolicyVPN
    from smc.core.engine import Engine
    from smc.vpn.elements import ExternalGateway, VPNProfile
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def add_central_gateway(vpn, elements):
    """
    Add a central VPN gateway.
    
    :param PolicyVPN vpn: reference to VPN
    :param list elements: instances of Element
    :raises PolicyCommandFailed: Error assigning gateway
    :return: None
    """
    changed = False
    if elements:
        current = [gw.gateway.href for gw in vpn.central_gateway_node.all()]
        for element in elements:
            if element.href not in current:
                vpn.add_central_gateway(element.href)
                changed = True
    return changed


def add_satellite_gateway(vpn, elements):
    """
    Add a satellite VPN gateway. 
    
    :param PolicyVPN vpn: reference to VPN
    :param list elements: instances of Element
    :raises PolicyCommandFailed: Error assigning gateway
    :return: None
    """
    changed = False
    if elements:
        current = [gw.gateway.href for gw in vpn.satellite_gateway_node.all()]
        for element in elements:
            if element.href not in current:
                vpn.add_satellite_gateway(element.href)
                changed = True

    return changed


def delete_central_gateway(vpn, elements):
    """
    Delete a central gateway.
    
    :param PolicyVPN vpn: policy VPN reference
    :param list elements: list of element references
    :return: True | False depending on whether an operation taken
    :raises PolicyCommandFailed: failure during deletion
    """
    changed = False
    if elements:
        element_map = {element.href: element for element in elements}
        for gw in vpn.central_gateway_node.all():
            if gw.gateway.href in element_map:
                gw.delete()
                changed = True
    return changed


def delete_satellite_gateway(vpn, elements):
    """
    Delete a satellite gateway.
    
    :param PolicyVPN vpn: policy VPN reference
    :param list elements: list of Element instances
    :return: True | False depending on whether an operation taken
    :raises PolicyCommandFailed: failure during deletion
    """
    changed = False
    if elements:
        element_map = {element.href: element for element in elements}
        for gw in vpn.satellite_gateway_node.all():
            if gw.gateway.href in element_map:
                gw.delete()  
                changed = True
    return changed


def change_gateway_tunnel(policy, gateway):
    """
    Change the preshared key for the specified tunnels.
    
    :param list gateway_tunnels
    :rtype: bool
    """
    changed = False
    for tunnel in policy.tunnels:
        if tunnel.tunnel_side_a.name == gateway.get('tunnel_side_a'):
            # Short circuit, if side A doesn't match, don't check B
            if tunnel.tunnel_side_b.name == gateway.get('tunnel_side_b'):
                values = {}
                if 'preshared_key' in gateway:
                    values.update(preshared_key=gateway['preshared_key'])
                if 'enabled' in gateway:
                    enable = gateway['enabled']
                    if tunnel.enabled and not enable:
                        values.update(enabled=False)
                    elif enable and not tunnel.enabled:
                        values.update(enabled=True)
                if values:
                    tunnel.update(**values)
                    policy.save()
                    changed = True
                break
    return changed


def resolve_gw(gateways):
    """
    Resolve gateways to references. If these gateways do not exist,
    then an exception is raised. This is done before any operations
    are performed to prevent partial / incomplete changes before
    failure.
    
    :param list gateways: list of central or satellite gateways by
        name provided from the playbook.
    :return list of elements
    :raises PolicyCommandFailed: failure during deletion
    """
    if gateways:
        gw_as_element = []
        try:
            for gateway in gateways:
                typeof = gateway.get('type')
                if typeof == 'internal_gateway':
                    element = Engine.get(gateway.get('name'))
                    gw_as_element.append(element.internal_gateway)
                else: #type external
                    element = ExternalGateway.get(gateway.get('name'))
                    gw_as_element.append(element)
        except SMCException:
            raise SMCException('Gateway %s specified does not exist. No changes '
                'will be made' % gateway.get('name'))
        return gw_as_element
        

class StonesoftPolicyVPN(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            vpn_profile=dict(type='str'),
            apply_nat=dict(default=False, type='bool'),
            central_gw=dict(type='list'),
            satellite_gw=dict(type='list'),
            gateway_tunnel=dict(type='list'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.apply_nat = None
        self.vpn_profile = None
        self.central_gw = None
        self.satellite_gw = None
        self.gateway_tunnel = None
        
        self.results = dict(
            changed=False,
        )
        super(StonesoftPolicyVPN, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        for gw in [self.central_gw, self.satellite_gw]:
            if gw:
                self._validate_subspec(gw)
        
        changed = False
        vpn = self.fetch_element(PolicyVPN)
        
        try:
            if state == 'present':

                lock = False # Used to flag whether policy needs to be locked
                if not vpn:
                    vpn = PolicyVPN.create(
                        name=self.name,
                        nat=self.apply_nat,
                        vpn_profile=self.vpn_profile)
                    changed = True
                
                if self.gateway_tunnel:
                    self._validate_tunnel(self.gateway_tunnel)
                    lock = True

                if self.central_gw:
                    self._validate_external_gw(self.central_gw)
                    self.central_gw = resolve_gw(self.central_gw)
                    lock = True
                
                if self.satellite_gw:
                    self._validate_external_gw(self.satellite_gw)
                    self.satellite_gw = resolve_gw(self.satellite_gw)
                    lock = True
                
                # Update profile if provided and they are different
                if self.vpn_profile:
                    if vpn.vpn_profile.name != self.vpn_profile:
                        pf = VPNProfile(self.vpn_profile).href
                        vpn.update(vpn_profile=pf)
                        changed = True
                
                # Make sure NAT setting matches
                if vpn.nat != self.apply_nat:
                    vpn.enable_disable_nat()
                    vpn.update()
                    changed = True
                        
                if lock:
                    vpn.open()
                    if add_central_gateway(vpn, self.central_gw):
                        changed = True
                    if add_satellite_gateway(vpn, self.satellite_gw):
                        changed = True
                    if self.gateway_tunnel:
                        for gateway in self.gateway_tunnel:
                            if change_gateway_tunnel(vpn, gateway):
                                changed = True
                    vpn.save()
                    vpn.close()
                
                if self.tags:
                    if self.add_tags(vpn, self.tags):
                        changed = True
            
            elif state == 'absent':

                # If no gateways are provided, delete the whole VPN
                if not self.central_gw and not self.satellite_gw and not self.tags:
                    if vpn:
                        vpn.delete()
                        changed = True
                else:
                    if vpn:
                        lock = False
                        if self.central_gw:
                            self.central_gw = resolve_gw(self.central_gw)
                            lock = True
                        
                        if self.satellite_gw:
                            self.satellite_gw = resolve_gw(self.satellite_gw)
                            lock = True
                        
                        if lock:
                            vpn.open()
                            if delete_central_gateway(vpn, self.central_gw):
                                changed = True
                            if delete_satellite_gateway(vpn, self.satellite_gw):
                                changed = True
                            vpn.save()
                            vpn.close()
                        
                        if self.tags:
                            if self.remove_tags(vpn, self.tags):
                                changed = True
                
        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
           
        self.results['changed'] = changed
        return self.results
    
    def _validate_tunnel(self, tunnels):
        """
        Validate gateway tunnel setting has tunnel side A, B and at
        least one of preshared key or enabled
        """
        required = ['tunnel_side_a', 'tunnel_side_b']
        for gateway in tunnels:
            for req in required:
                if gateway.get(req) is None:
                    self.fail(msg='You must provide tunnel_side_a and '
                        'tunnel_side_b to modify an existing gateway tunnel')
            
            if gateway.get('preshared_key') is None and \
                gateway.get('enabled') is None:
                
                self.fail(msg='To modify an existing gateway tunnel you must provide '
                    'a value for either preshared_key or enabled')
        
    def _validate_external_gw(self, gateways):
        """
        This is only called during create operations. The external gateway
        must provide a preshared_key field. This will set the key for all
        tunnels initially.
        """
        if gateways:
            for gateway in gateways:
                typeof = gateway.get('type')
                if typeof == 'external_gateway':
                    if not gateway.get('preshared_key'):
                        self.fail(msg='When creating an external gateway you must '
                            'specify a preshared_key')
    
    def _validate_subspec(self, gw):
        """
        Validate that the central and satellite gateways have the
        type field specified.
        """
        choices = ['internal_gateway', 'external_gateway']
        for entry in gw:
            if 'name' not in entry:
                self.fail(msg='VPN Gateway fields require a name field')
            if 'type' not in entry:
                self.fail(msg='A VPN Gateway definition is missing the type field and value')
            elif entry['type'] not in choices:
                self.fail(msg='Invalid option value for type field on VPN Gateway. '
                    'Valid options: %s' % choices)

def main():
    StonesoftPolicyVPN()
    
if __name__ == '__main__':
    main()