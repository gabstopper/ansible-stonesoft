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
          - internal
          - external
        type: str
        required: true
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
- name: Create or add gateways to a policy VPN
  policy_vpn:
    name: mynewvpn
    central_gw:
      - name: myfirewall
        type: internal
    satellite_gw:
      - name: newextgw
        type: external
    tags:
      - footag

- name: Delete a single satellite gateway from this VPN
  policy_vpn:
    name: mynewvpn
    satellite_gw:
      - name: newextgw
        type: external
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
msg:
  description: Simple description message
  returned: always
  type: string
  sample: Successfully created engine
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
    :param list elements: fetched element hrefs
    :raises PolicyCommandFailed: Error assigning gateway
    :return: None
    """
    changed = False
    if elements:
        current = [gw.gateway.href for gw in vpn.central_gateway_node.all()]
        for element in elements:
            if element not in current:
                vpn.add_central_gateway(element)
                changed = True
    return changed


def add_satellite_gateway(vpn, elements):
    """
    Add a satellite VPN gateway. 
    
    :param PolicyVPN vpn: reference to VPN
    :param list elements: fetched element hrefs
    :raises PolicyCommandFailed: Error assigning gateway
    :return: None
    """
    changed = False
    if elements:
        current = [gw.gateway.href for gw in vpn.satellite_gateway_node.all()]
        for element in elements:
            if element not in current:
                vpn.add_satellite_gateway(element)
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
        for gw in vpn.central_gateway_node.all():
            if gw.gateway.href in elements:
                gw.delete()
                changed = True
    return changed


def delete_satellite_gateway(vpn, elements):
    """
    Delete a satellite gateway.
    
    :param PolicyVPN vpn: policy VPN reference
    :param list elements: list of element references
    :return: True | False depending on whether an operation taken
    :raises PolicyCommandFailed: failure during deletion
    """
    changed = False
    if elements:
        for gw in vpn.satellite_gateway_node.all():
            if gw.gateway.href in elements:
                gw.delete()  
                changed = True
    return changed


def resolve_gw(gateways):
    """
    Resolve gateways to references. If these gateways do not exist,
    then an exception is raised. This is done before any operations
    are performed to prevent partial / incomplete changes before
    failure.
    
    :param list gateways: list of central or satellite gateways by
        name provided from the playbook.
    :return list of href for each entry
    :raises PolicyCommandFailed: failure during deletion
    """
    if gateways:
        gw_as_element = []
        try:
            for gateway in gateways:
                typeof = gateway.get('type')
                if typeof == 'internal':
                    element = Engine.get(gateway.get('name'))
                    gw_as_element.append(element.internal_gateway.href)
                else: #type external
                    element = ExternalGateway.get(gateway.get('name'))
                    gw_as_element.append(element.href)
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
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.apply_nat = None
        self.vpn_profile = None
        self.central_gw = None
        self.satellite_gw = None
        
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
        vpn = PolicyVPN.objects.filter(self.name, exact_match=True).first()
        
        try:
            if state == 'present':
                lock = False # Used to flag whether policy needs to be locked
                if not vpn:
                    vpn = PolicyVPN.create(
                        name=self.name,
                        nat=self.apply_nat,
                        vpn_profile=self.vpn_profile)
                    changed = True
                
                if self.central_gw:
                    self.central_gw = resolve_gw(self.central_gw)
                    lock = True
                
                if self.satellite_gw:
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
    
    def _validate_subspec(self, gw):
        choices = ['internal', 'external']
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