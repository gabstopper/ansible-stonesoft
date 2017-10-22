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
module: vpn_external_gw
short_description: Represents a 3rd party gateway used for VPN
description:
  - An external gateway is a non-SMC managed VPN endpoint that represents
    the other side of a VPN tunnel.
version_added: '2.5'

options:
  name:
    description:
      - The name of the external gateway
    required: true
  endpoint_ip:
    description:
      - The endpoint IP of the VPN gateway. This is mutually exclusive with
        I(endpoint_dynamic)
    type: str
  endpoint_dynamic:
    description:
      - If the VPN gateway is dynamic (dhcp) then set this value. This is
        mutually exclusive with I(endpoint_ip).
    type: bool
  networks:
    description:
      - The networks in cidr format for the remote side. If the network
        elements are not found, they will be created.
    type: list
  nat_t:
    description:
      - Whether to enable nat-t on this VPN.
    default: true
  mode:
    description:
      - The role for this VPN gateway. 
    type: str
    choices:
      - active
      - standby
      - aggregate
  enabled:
    description:
      - Whether to enable the VPN endpoint
    default: true
  tags:
    description:
      - Any tags for this gateway
  state:
    description:
      - Create or delete flag
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
- name: Create an external gateway
  vpn_external_gw:
    name: newextgw
    endpoint_ip: 1.1.1.1
    networks:
      - 3.3.3.0/24
      - 4.4.4.0/24
    nat_t: yes
    mode: active
    tags: 
      - footag

- name: Delete an external gateway
  vpn_external_gw:
    name: myextgw
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
    from smc.vpn.elements import ExternalGateway
    from smc.elements.network import Network
    from smc.api.exceptions import SMCException
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class ExternalVPNGW(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            endpoint_ip=dict(type='str'),
            endpoint_dynamic=dict(type='bool', default=False),
            networks=dict(type='list'),
            nat_t=dict(default=True, type='bool'),
            mode=dict(default='active', choices=['active', 'standby', 'aggregate']),
            enabled=dict(default=True, type='bool'),
            tags=dict(type='list'),
            state=dict(default='present', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.enabled = None
        self.networks = None
        self.nat_t = None
        self.mode = None
        self.endpoint_ip = None
        self.endpoint_dynamic = None

        mutually_exclusive = [
            [ 'endpoint_ip', 'endpoint_dynamic' ]
        ]
        
        self.results = dict(
            changed=False,
            msg=''
        )
        super(ExternalVPNGW, self).__init__(self.module_args, mutually_exclusive=mutually_exclusive)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if state == 'present':
            try:
                ext_gw = ExternalGateway.create(self.name)
                ext_gw.external_endpoint.create(
                    name=self.name,
                    address=self.endpoint_ip,
                    enabled=self.enabled,
                    balancing_mode=self.mode, 
                    ipsec_vpn=True,
                    nat_t=self.nat_t, 
                    dynamic=self.endpoint_dynamic)
                
                networks = []
                for site in self.networks:
                    network = Network.get_or_create(
                        filter_key={'ipv4_network': site},
                        name='network-{}'.format(site),
                        ipv4_network=site)
                    networks.append(network)
                        
                ext_gw.vpn_site.create(name=self.name, site_element=networks)
                    
                if self.tags:
                    ext_gw.add_category(self.tags)
                
            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successfully created external gw', changed=True)
            
        elif state == 'absent':
            try:
                ExternalGateway(self.name).delete()
   
            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successfully deleted external gw', changed=True)

        return self.results


def main():
    ExternalVPNGW()
    
if __name__ == '__main__':
    main()


