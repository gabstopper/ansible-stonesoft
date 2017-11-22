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
  interfaces:
    description:
      - List of interface definitions for this FW
    type: list
    suboptions:
      address:
        description:
          - IP address for this interface
        type: str
      network_value:
        description:
          - Network CIDR for the C(address) specified
        type: str
      interface_id:
        description:
          - Interface ID for this interface. 
        required: true
        type: str
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
state:
  description: The current state of the element
  return: always
  type: dict
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.core.engines import Layer3Firewall
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def to_dict(element):
    links = ('link', 'key')
    for node in element.data.get('nodes'):
        for _, data in node.items():
            for elem in links:
                data.pop(elem, None)
    for interface in element.data.get('physicalInterfaces'):
        for _, data in interface.items():
            for elem in links:
                data.pop(elem, None)
            for vlan in data.get('vlanInterfaces', []):
                for elem in links:
                    vlan.pop(elem, None)

    for link in links:
        element.data.pop(link, None)
    return element.data


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
                    
                    management = False
                    for interface in self.interfaces:
                        if interface.get('interface_id') == self.mgmt_interface:
                            management = True
                            if 'address' not in interface or 'network_value' not in interface:
                                self.fail(msg='Management interface require address and network_value fields')
                            break
                    
                    if not management:
                        self.fail(msg='Management interface definition not found in interfaces. '
                            'Management interface specified: {}'.format(self.mgmt_interface))
                
                # Internal Endpoints are referenced by their IP address
                enable_vpn = []
                
                if self.interfaces:
                    for interface in self.interfaces:
                        if 'interface_id' not in interface:
                            self.fail(msg='Interface requires at least interface_id be '
                                'defined.')
                            
                        if interface.get('type', None) == 'tunnel_interface' and \
                            ('address' not in interface or 'network_value' not in interface):
                            self.fail(msg='Missing either address or network_value for tunnel interface')
                            
                        if not engine and 'enable_vpn' in interface:
                            value = interface.pop('enable_vpn')
                            if value: # True
                                enable_vpn.append(interface['address'])
                
                if self.check_mode:
                    return self.results
                    
                if not engine:
                    engine = Layer3Firewall.create_with_many(
                        name=self.name, 
                        interfaces=self.interfaces,
                        mgmt_interface=self.mgmt_interface,
                        log_server_ref=self.log_server,
                        default_nat=self.default_nat,
                        domain_server_address=self.domain_server_address,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        location_ref=self.location,
                        enable_ospf=self.enable_ospf,
                        sidewinder_proxy_enabled=self.enable_sidewinder_proxy,
                        ospf_profile=None)
                    
                    if enable_vpn:
                        for internal_gw in engine.vpn_endpoint:
                            if internal_gw.name in enable_vpn:
                                internal_gw.update(enabled=True)
                    
                    changed = True
                else:
                    for interface in self.interfaces:
                        interface_id = interface['interface_id']
                        try:
                            itf = engine.interface.get(interface_id)
                            # If this interface does not have IP addresses assigned,
                            # then assign it if specified
                            if 'address' in interface and 'network_value' in interface:
                                addresses = itf.addresses
                                if not addresses:
                                    engine.physical_interface.add_layer3_interface(
                                        interface_id=interface_id,
                                        address=interface['address'],
                                        network_value=interface['network_value'],
                                        zone_ref=interface.get('zone', None))
                                    changed = True

                        except SMCException:
                            if 'address' in interface and 'network_value' in interface:
                                if interface.get('type', None) == 'tunnel_interface':
                                    engine.tunnel_interface.add_single_node_interface(
                                        tunnel_id=interface_id,
                                        address=interface['address'],
                                        network_value=interface['network_value'],
                                        zone_ref=interface.get('zone_ref', None))
                                else:
                                    engine.physical_interface.add_layer3_interface(
                                        interface_id=interface_id,
                                        address=interface['address'],
                                        network_value=interface['network_value'],
                                        zone_ref=interface.get('zone_ref', None))
                                    
                                    if interface.get('enable_vpn', None):
                                        for internal_gw in engine.vpn_endpoint:
                                            if internal_gw.name == interface['address']:
                                                internal_gw.update(enabled=True)
                                                break
                                    changed = True
                            else:
                                # Interface with no addresses, ignore enable_vpn
                                engine.physical_interface.add(
                                    interface_id, zone_ref=interface.get('zone_ref', None))
                                changed = True
    
                if self.tags:
                    if self.add_tags(engine, self.tags):
                        engine.add_category(self.tags)
                        changed = True
                
                self.results['state'] = to_dict(engine)
                
            elif state == 'absent':
                if engine:
                    if self.interfaces:
                        for interface in self.interfaces:
                            if 'interface_id' in interface:
                                try:
                                    itf = engine.interface.get(interface['interface_id'])
                                    itf.delete()
                                    changed = True
                                except SMCException:
                                    pass
                    if self.tags:
                        if self.remove_tags(engine, self.tags):
                            changed = True
                            
                    if not self.interfaces and not self.tags:
                        engine.delete()
                    else:
                        self.results['state'] = to_dict(engine)

        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results


def main():
    StonesoftFirewall()
    
if __name__ == '__main__':
    main()
