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
  mgmt_interface:
    description:
      - The management interface id. In the intent is to create the fw, C(interfaces) must also
        be specified with a matching interface_id
    default: 0
    required: true
  interfaces:
    description:
      - List of interface definitions for this FW
    type: list
    required: true
    suboptions:
      address:
        description:
          - IP address for this interface
        type: str
        required: true
      network_value:
        description:
          - Network CIDR for the C(address) specified
        type: str
        required: true
      interface_id:
        description:
          - Interface ID for this interface. 
        type: str
        required: true
      zone_ref: 
        description:
          - Optional zone for this interface, by name. If zone doesn't exist, it will be created
        type: str
      type:
        description:
          - Type of interface. Default type is physical_interface. If this is designated as
            an interface type other than physical, you must specify the type.
        type: str
        default: physical_interface
        choices:
          - physical_interface
          - tunnel_interface
      enable_vpn:
        description:
          - Enable VPN on this interface
        type: bool
        default: false
  default_nat:
    description:
      - Whether to enable default NAT on the FW. Default NAT will identify
        internal networks and use the external interface IP for outgoing traffic
    type: bool
    default: false
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW.
  log_server:
    description:
      - Specify a log server to use. This is useful if multiple log servers are
        available.
    type: str
  location:
    description:
      - Location for this FW. Used for FW's that are behind NAT
    type: str
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
- name: Create a single layer 3 firewall
  register: result
  l3fw:
    smc_logging:
      level: 10
      path: ansible-smc.log
    name: myfw
    mgmt_interface: 10
    interfaces:
      - interface_id: 0
        address: 1.1.1.2
        network_value: 1.1.1.0/16
        zone_ref: management
      - interface_id: 10
        address: 10.10.10.1
        network_value: 10.10.10.0/24
        zone_ref: external
        enable_vpn: yes
      - interface_id: 11
      - interface_id: 1000
        address: 11.11.11.1
        network_value: 11.11.11.0/24
        zone_ref: awsvpn
        type: tunnel_interface 
    domain_server_address:
      - 10.0.0.1
      - 10.0.0.2
    default_nat: yes
    enable_antivirus: yes
    enable_gti: yes
    enable_sidewinder_proxy: yes
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
state:
  description: The current state of the element
  return: always
  type: dict
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.core.engines import Layer3Firewall
    from smc.api.exceptions import SMCException, InterfaceNotFound
except ImportError:
    pass


class StonesoftFirewall(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            mgmt_interface=dict(type='int', default=0),
            default_nat=dict(default=False, type='bool'),
            domain_server_address=dict(default=[], type='list'),
            interfaces=dict(type='list'),
            location=dict(type='str'),
            log_server=dict(type='str'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_gti=dict(default=False, type='bool'),
            enable_ospf=dict(default=False, type='bool'),
            enable_sidewinder_proxy=dict(default=False, type='bool'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.mgmt_interface = None
        self.default_nat = None
        self.interfaces = None
        self.domain_server_address = None
        self.location = None
        self.log_server = None
        self.enable_antivirus = None
        self.enable_gti = None
        self.enable_ospf = None
        self.enable_sidewinder_proxy = None
        
        self.results = dict(
            changed=False,
            state=dict()
        )
        super(StonesoftFirewall, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(Layer3Firewall)
        
        try:
            if state == 'present':
                if not engine:
                    # Find interface designated as management
                    if not self.interfaces:
                        self.fail(msg='You must define at least 1 interface when creating a NGFW')

                    # Internal Endpoints are referenced by their IP address
                    enable_vpn = []
                
                    mgmt_index = None
                    for num, value in enumerate(self.interfaces):
                        if 'interface_id' not in value:
                            self.fail(msg='Interface requires at least interface_id be '
                                'defined.')
                        
                        if value.get('type', None) == 'tunnel_interface' and \
                            ('address' not in value or 'network_value' not in value):
                            self.fail(msg='Missing either address or network_value for tunnel interface')
                        
                        if str(value.get('interface_id')) == str(self.mgmt_interface):
                            mgmt_index = num
                        
                        vpn = value.pop('enable_vpn', None)
                        if vpn: # True
                            enable_vpn.append(value['address'])
                    
                    if mgmt_index is None:
                        self.fail(msg='Management interface definition not found in interfaces. '
                            'Management interface specified: {}'.format(self.mgmt_interface))
                
                    if self.check_mode:
                        return self.results
                
                    mgmt = self.interfaces.pop(mgmt_index)
                    
                    engine = Layer3Firewall.create(
                        name=self.name,
                        mgmt_ip=mgmt.get('address'),
                        mgmt_network=mgmt.get('network_value'),
                        mgmt_interface=self.mgmt_interface,
                        log_server_ref=self.log_server,
                        default_nat=self.default_nat,
                        domain_server_address=self.domain_server_address,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        location_ref=self.location,
                        enable_ospf=self.enable_ospf,
                        sidewinder_proxy_enabled=self.enable_sidewinder_proxy,
                        ospf_profile=None,
                        interfaces=self.interfaces)
                  
                    if enable_vpn:
                        for internal_gw in engine.vpn_endpoint:
                            if internal_gw.name in enable_vpn:
                                internal_gw.update(enabled=True)
                    
                    if self.tags:
                        if self.add_tags(engine, self.tags):
                            changed = True
                    
                    changed = True

                else: # Engine exists, check for modifications
                    # Start with engine properties..
                    status = engine.default_nat.status
                    if self.default_nat:
                        if not status:
                            engine.default_nat.enable()
                            changed = True
                    else: # False or None
                        if status:
                            engine.default_nat.disable()
                            changed = True
                    
                    status = engine.antivirus.status
                    if self.enable_antivirus:
                        if not status:
                            engine.antivirus.enable()
                            changed = True
                    else:
                        if status:
                            engine.antivirus.disable()
                            changed = True
                    
                    dns = [d.value for d in engine.dns]
                    missing = [entry for entry in self.domain_server_address
                               if entry not in dns]
                    # Remove unneeded
                    unneeded = [entry for entry in dns
                                if entry not in self.domain_server_address
                                if entry is not None]
                    if missing:
                        engine.dns.add(missing)
                        changed = True
                    
                    if unneeded:
                        engine.dns.remove(unneeded)
                        changed = True
                
                    if self.check_mode:
                        return self.results
                    # Update checkpoint. Adding and removing interfaces will
                    # already automatically update the engine.
                    if changed:
                        engine.update()
                    
                    # Interfaces to enable VPN
                    enable_vpn = {}
                    # Iterate the interfaces. Add interfaces that do not exist.
                    # Then remove interfaces that are not defined in the
                    # playbook yml.
                    for interface in self.interfaces:
                        interface_id = interface['interface_id']
                        try:
                            itf = engine.interface.get(interface_id)
                            # If this interface does not have IP addresses assigned,
                            # then assign. It is not currently possible to unassign
                            # addresses. Instead, delete the interface
                            if 'address' in interface and 'network_value' in interface:
                                if 'enable_vpn' in interface:
                                    enable_vpn[interface.get('address')] = interface.pop('enable_vpn')
                                
                                addresses = itf.addresses
                                if not addresses:
                                    engine.physical_interface.add_layer3_interface(
                                        **interface)
                                    changed = True
                                else:
                                    # Has addresses, change if different
                                    for sub in itf.interfaces:
                                        if sub.address != interface['address']:
                                            itf.change_single_ipaddress(
                                                address=interface['address'],
                                                network_value=interface['network_value'])
                                            changed = True

                        except InterfaceNotFound:
                            if 'address' in interface and 'network_value' in interface:
                                if interface.get('type', None) == 'tunnel_interface':
                                    engine.tunnel_interface.add_single_node_interface(
                                        tunnel_id=interface_id,
                                        address=interface['address'],
                                        network_value=interface['network_value'],
                                        zone_ref=interface.get('zone_ref', None))
                                    changed = True
                                else:
                                    if 'enable_vpn' in interface:
                                        enable_vpn[interface.get('address')] = interface.pop('enable_vpn')
                                    
                                    engine.physical_interface.add_layer3_interface(
                                        **interface)

                                    changed = True
                            else:
                                # Interface with no addresses, ignore enable_vpn
                                engine.physical_interface.add(
                                    interface_id, zone_ref=interface.get('zone_ref', None))
                                changed = True
                    
                    # Check the VPN settings for the interfaces. If you want
                    # to explicitly disable VPN, set enable_vpn: False in the
                    # playbook
                    for vpn in engine.vpn_endpoint:
                        if vpn.name in enable_vpn:
                            #self.fail(msg="VPN name in: %s" % vpn.name)
                            if not vpn.enabled and enable_vpn.get(vpn.name):
                                vpn.update(enabled=True)
                                changed = True
                            elif vpn.enabled and not enable_vpn.get(vpn.name):
                                vpn.update(enabled=False)
                                changed = True
                
                    if self.tags:
                        if self.add_tags(engine, self.tags):
                            changed = True
                    else:
                        if self.clear_tags(engine):
                            changed = True

                self.results.update(
                    state=engine.data,
                    changed=changed)
                
            elif state == 'absent':
                if engine:
                    engine.delete()
                    changed = True

        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results


def main():
    StonesoftFirewall()
    
if __name__ == '__main__':
    main()
