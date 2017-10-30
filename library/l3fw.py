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
module: l3fw
short_description: Create or delete a Stonesoft Layer 3 firewall
description:
  - Create or delete a Stonesoft Layer 3 Firewall on the Stonesoft
    Management Center.
version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall to add or delete
    required: true
  mgmt_ip:
    description:
      - The management IP for the firewall management interface.
  mgmt_network:
    description:
      - The management network for this management interface.
        Specify in cidr format
  mgmt_interface:
    description:
      - The management interface id
    default: 0
  default_nat:
    description:
      - Whether to enable default NAT on the FW. Default NAT will identify
        internal networks and use the external interface IP for outgoing traffic
    type: bool
    default: false
  reverse_connection:
    description:
      - Whether this interface is a DHCP interface. Setting the interface to
        reverse connection forces the firewall to initiate connections versus
        the other way around
    type: bool
    default: false
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW.
  zone_ref:
    description:
      - A zone name for the FW management interface.
  enable_antivirus:
    description:
      - Enable Anti-Virus engine on the FW
    type: bool
    default: false
  enable_gti:
    description:
      - Enable file reputation
    type: bool
    default: false
  enable_ospf:
    description:
      - Enable OSPF on the FW management interface
    type: bool
    default: false
  enable_sidewinder_proxy:
    description:
      - Enable Sidewinder proxy capability on the FW
    type: bool
    default: false
  enable_vpn:
    description:
      - Enable VPN on the interface designated for management
    type: bool
    default: false
  tags:
    description:
      - Provide an optional category tag to the engine. If the category does not
        exist, it will be created
    type: list
  state:
    description:
      - Create or delete layer 3 FW
    required: false
    default: present
    choices:
      - present
      - absent
      
extends_documentation_fragment: stonesoft

notes:
  - Login credential information is either obtained by providing them directly
    to the task/play, specifying an alt_filepath to read the credentials from to
    the play, or from environment variables (in that order). See
    U(http://smc-python.readthedocs.io/en/latest/pages/session.html) for more
    information.

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)

'''

EXAMPLES = '''
# Create a basic layer 3 firewall. Credentials are retrieved from
# either users home dir (~.smcrc) or environment variables
- name: create a simple firewall
  l3fw:
    name: myfirewall
    mgmt_ip: 1.1.1.1
    mgmt_network: 1.1.1.0/24

# Create a layer 3 firewall, using an alternate file for credentials
- name: launch ansible cloudformation example
  l3fw:
    smc_alt_filepath: /Users/davidlepage/smc
    name: 'myfirewall'
    mgmt_ip: 1.1.1.1
    mgmt_network: 1.1.1.0/24
    mgmt_interface: 1
    default_nat: yes
    domain_server_address:
        - 10.0.0.1
        - 10.0.0.2
    enable_antivirus: yes
    enable_gti: yes
    enable_sidewinder_proxy: yes
    enable_vpn: yes
    tags:
      - footag

# Delete a layer 3 firewall, using environment variables for credentials
- name: delete firewall by name
  l3fw:
    name: myfirewall
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
    from smc.core.engines import Layer3Firewall
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class StonesoftFirewall(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            mgmt_ip=dict(type='str'),
            mgmt_network=dict(type='str'),
            mgmt_interface=dict(default=0),
            default_nat=dict(default=False, type='bool'),
            reverse_connection=dict(default=False, type='bool'),
            domain_server_address=dict(default=[], type='list'),
            zone_ref=dict(type='str'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_gti=dict(default=False, type='bool'),
            enable_ospf=dict(default=False, type='bool'),
            enable_sidewinder_proxy=dict(default=False, type='bool'),
            enable_vpn=dict(default=False, type='bool'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.mgmt_ip = None
        self.mgmt_network = None
        self.mgmt_interface = None
        self.default_nat = False
        self.reverse_connection = False
        self.domain_server_address = None
        self.zone_ref = None
        self.enable_antivirus = False
        self.enable_gti = False
        self.enable_ospf = None
        self.enable_sidewinder_proxy = None
        self.enable_vpn = None
        
        required_if=([
            ('state', 'present', ['name', 'mgmt_ip', 'mgmt_network']),
            ('state', 'absent', ['name'])
        ])
        
        self.results = dict(
            changed=False
        )
        super(StonesoftFirewall, self).__init__(self.module_args, required_if=required_if)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(Layer3Firewall)
        
        try:
            if state == 'present':
                if not engine:
                    engine = Layer3Firewall.create(
                        name=self.name,
                        mgmt_ip=self.mgmt_ip,
                        mgmt_network=self.mgmt_network,
                        mgmt_interface=self.mgmt_interface,
                        log_server_ref=None,
                        default_nat=self.default_nat,
                        reverse_connection=self.reverse_connection,
                        domain_server_address=self.domain_server_address,
                        zone_ref=self.zone_ref,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        location_ref=None,
                        enable_ospf=self.enable_ospf,
                        sidewinder_proxy_enabled=self.enable_sidewinder_proxy,
                        ospf_profile=None)
                    changed = True
                
                if self.enable_vpn is not None and self.enable_vpn:
                    for internal_gw in engine.vpn_endpoint:
                        internal_gw.update(enabled=True)
                    
                if self.tags:
                    if self.add_tags(engine, self.tags):
                        engine.add_category(self.tags)
                        changed = True
                
            elif state == 'absent':
                if engine:
                    if not self.tags:
                        engine.delete()
                        changed = True
                    else:
                        if self.remove_tags(engine, self.tags):
                            changed = True

        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results


def main():
    StonesoftFirewall()
    
if __name__ == '__main__':
    main()
