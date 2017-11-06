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
module: l3fw_interface
short_description: Create or delete a layer 3 physical or tunnel interface
description:
  - Create or delete a layer 3 physical or tunnel interface on a single firewall.

version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall to add the layer 3 interface
    required: true
  interface_id:
    description:
      - The interface id to assign to interface
    required: true
  interface_type:
    description:
      - Type of interface to create
    choices:
      - physical
      - tunnel
    default: physical
  address:
    description:
      - The address to assign to the interface. Required if I(state=present)
  network_value:
    description:
      - The network and cidr mask for this interface. For example 1.1.1.0/24
  zone_ref:
    description:
      - Assign a zone to this interface. Zone should be by name.
  enable_vpn:
    description:
      - Enable IPSEC VPN on this interface. This is only available on physical
        interfaces.
    default: false
  state:
    description:
      - Create or delete layer 3 interface
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
# Create a layer 3 interface
- name: add a layer 3 interface to a single fw
  l3fw_interface:
    name: myfirewall
    interface_id: 5
    address: 5.5.5.5
    network_value: 5.5.5.0/24
- name: add another interface
  l3fw_interface:
    name: myfirewall
    interface_id: 6
    address: 6.6.6.6
    network_value: 6.6.6.0/24
    enable_vpn: yes

# Create a tunnel interface
- name: add a layer 3 interface to a single fw
  l3fw_interface:
    name: myfirewall
    interface_id: 2000
    address: 5.5.5.5
    network_value: 5.5.5.0/24
    interface_type: tunnel
      
# Delete a layer 3 interface
- name: delete interface 5
  l3fw_interface:
    name: myfirewall
    interface_id: 5
    state: 'absent'
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
    from smc.core.engines import Engine
    from smc.api.exceptions import SMCException, EngineCommandFailed
except ImportError:
    # Caught in StonesoftModuleBase
    pass


def set_boolean(attribute, value):
    pass

    
class StonesoftFWInterface(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            interface_id=dict(type='int', required=True),
            address=dict(type='str'),
            network_value=dict(type='str'),
            interface_type=dict(type='str', default='physical'),
            zone_ref=dict(type='str'),
            enable_vpn=dict(type='bool'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.interface_id = None
        self.address = None
        self.network_value = None
        self.interface_type = None
        self.zone_ref = None
        self.enable_vpn = None
        
        required_if=([
            ('state', 'present', ['address', 'network_value'])
        ])
        
        self.results = dict(
            changed=False
        )
        super(StonesoftFWInterface, self).__init__(self.module_args, required_if=required_if)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(Engine)
    
        try:
            if state == 'present':
                
                if engine:
                    # Check if interface exists before trying to create
                    try:
                        interface = engine.interface.get(self.interface_id)
                    except EngineCommandFailed:
                        # Interface doesn't exist
                        if self.interface_type == 'physical':
                            engine.physical_interface.add_layer3_interface(
                                interface_id=self.interface_id,
                                address=self.address,
                                network_value=self.network_value,
                                zone_ref=self.zone_ref)
                        else: # Tunnel
                            engine.tunnel_interface.add_single_node_interface(
                                tunnel_id=self.interface_id,
                                address=self.address,
                                network_value=self.network_value,
                                zone_ref=self.zone_ref)
                        
                        changed = True
                        
                    if self.enable_vpn is not None:
                        if self.interface_type == 'physical':
                            # Get the internal endpoint
                            for gw in engine.vpn_endpoint:
                                if gw.interface_id == str(self.interface_id):
                                    if self.enable_vpn and not gw.enabled: 
                                        gw.update(enabled=True)
                                        changed = True
                                    elif gw.enabled and not self.enable_vpn:
                                        gw.update(enabled=False)
                                        changed = True
        
            elif state == 'absent':
                if engine:
                    interface = engine.interface.get(self.interface_id)
                    interface.delete()
                    changed = True
                
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
    
        self.results['changed'] = changed
        return self.results


def main():
    StonesoftFWInterface()

if __name__ == '__main__':
    main()