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
module: external_gateway
short_description: Represents a 3rd party gateway used for a VPN configuration
description:
  - An external gateway is a non-SMC managed VPN endpoint used in either policy
    or route based VPN. When deleting an endpoint, only tags, endpoints and the
    top level external gateway can be removed. External GW settings can be modified
    if state is present and the gateway already exists.

version_added: '2.5'

options:
  name:
    description:
      - The name of the external gateway
    required: true
  sites:
    description:
      - VPN sites defined the networks for this VPN. A site entry should be a network
        CIDR address. If the network does not exist, the element will be created.
    type: str
  endpoint:
    description:
      - An endpoint represents an external VPN gateway and it's remote
        site settings such as IP address, remote site networks, etc.
    suboptions:
      name:
        description:
          - Name for the endpoint, unique identifier
        required: true
      address:
        description:
          - The endpoint IP of the VPN gateway. This is mutually exclusive with
            I(endpoint_dynamic)
        type: str
      dynamic:
        description:
          - If the VPN gateway is dynamic (dhcp) then set this value. This is
            mutually exclusive with I(endpoint_ip).
        type: bool
      ike_phase1_id_type:
        description:
          - An IKE phase1 id is required if I(dynamic=yes). This specifies the type
            of selector to use to identify the dynamic endpoint
        choices:
          - 0 (DNS)
          - 1 (Email address)
          - 2 (Distinguished name)
          - 3 (IP address)
      ike_phase1_id_value:
        description:
          - Value of ika_phase1_id_type. This should conform to the type selected. For
            example, if email address is used, format should be a@a.com. Required if I(dynamic=yes)
        type: str
      nat_t:
        description:
          - Whether to enable nat-t on this VPN.
        default: true
      force_nat_t:
        description:
          - Whether to force NAT_T on the VPN
        default: false
      balancing_mode:
        description:
          - The role for this VPN gateway. 
        type: str
        choices:
          - active
          - standby
          - aggregate
        default: active
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
- name: Create an external gateway with static IP addresses
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Create an external gateway
    external_gateway:
      name: myremotevpn
      sites:
        - 1.1.1.0/24
      endpoint:
        - name: endpoint1
          address: 33.33.33.40
          force_nat_t: no
          balancing_mode: active
        - name: endpoint2
          address: 33.33.33.35
          force_nat_t: yes
          balancing_mode: active
      tags: footag

- name: Create an external gateway using dynamic IP
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Create an external gateway
    external_gateway:
      name: dynamicendpoint
      sites:
        - 1.1.1.0/24
      endpoint:
        - name: mydynamicendpoint
          dynamic: yes
          ike_phase1_id_type: 1
          ike_phasee1_id_value: a@a.com
      tags: footag

- name: Modify an existing external endpoint
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Change balancing mode from active to standby
    external_gateway:
      name: myremotevpn
      endpoint:
        - name: endpoint1
          balancing_mode: standby

- name: Delete an external gateway
  external_vpn_gw:
    name: myextgw
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
    from smc.vpn.elements import ExternalGateway
    from smc.elements.network import Network
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def endpoint_spec(endpoint):
    """
    Define the endpoint and defaults
    """
    spec = dict(
        name=endpoint.get('name'),
        address=endpoint.get('address'),
        enabled=endpoint.get('enabled', True),
        balancing_mode=endpoint.get('balancing_mode', 'active'), 
        ipsec_vpn=endpoint.get('ipsec_vpn', True),
        nat_t=endpoint.get('nat_t', True), 
        dynamic=endpoint.get('dynamic', False))
    
    if endpoint.get('force_nat_t', False):
        spec.update(nat_t=True, force_nat_t=True)
    
    if spec['dynamic']:
        spec.update(
            ike_phase1_id_type=endpoint.get('ike_phase1_id_type'),
            ike_phase1_id_value=endpoint.get('ike_phase1_id_value'))
    return spec


def _get_endpoint_obj(endpoint, current):
    """
    Fetch the specific endpoint from a list of existing external
    endpoints. This is used to operate on the element. 
    
    :param str endpoint_name: name of external endpoint to find
    :param list current: list of ExternalEndpoint from the ExternalGateway
    :return
    """
    for match in current:
        if match.name.startswith(endpoint.get('name')):
            return match


class ExternalVPNGW(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            endpoint=dict(type='list'),
            sites=dict(type='list'),
            tags=dict(type='list'),
            state=dict(default='present', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.sites = None
        self.endpoint = None
        
        self.results = dict(
            changed=False,
        )
        super(ExternalVPNGW, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        ext_gw = self.fetch_element(ExternalGateway)

        try:        
            if state == 'present':
                if not ext_gw:
                    ext_gw = ExternalGateway.create(self.name)
                    changed = True

                if self.endpoint:
                    # Current endpoints
                    current = [e for e in ext_gw.external_endpoint.all()]
                    for endpoint in self.endpoint:
                        # Does it already exist?
                        obj = _get_endpoint_obj(endpoint, current)
                        if obj:
                            # Check for modifications
                            address=endpoint.get('address')
                            enabled=endpoint.get('enabled')
                            balancing_mode=endpoint.get('balancing_mode') 
                            nat_t=endpoint.get('nat_t')
                            dynamic=endpoint.get('dynamic')
                            force_nat_t=endpoint.get('force_nat_t')
                            
                            if address and dynamic is not None:
                                self.fail('You cannot specify and endpoint IP address '
                                    'and a dynamic endpoint at the same time')
                            
                            data = {}
                            if address and address != obj.address:
                                data.update(address=address)
                            if enabled is not None:
                                if enabled and not obj.enabled:
                                    data.update(enabled=True)
                                elif obj.enabled and not enabled:
                                    data.update(enabled=False)
                            if balancing_mode != obj.balancing_mode and \
                                balancing_mode in ['active', 'standby', 'aggregate']:
                                data.update(balancing_mode=balancing_mode)
                            if force_nat_t is not None:
                                if force_nat_t and not obj.force_nat_t:
                                    data.update(force_nat_t=True, nat_t=True)
                                elif obj.force_nat_t and not force_nat_t:
                                    data.update(force_nat_t=False)
                            if nat_t is not None and force_nat_t is None:
                                if nat_t and not obj.nat_t:
                                    data.update(nat_t=True)
                                elif obj.nat_t and not nat_t:
                                    data.update(nat_t=False)
                            
                            if data:
                                obj.update(**data)
                                changed = True    
                        else:
                            # Create the new endpoint
                            spec = endpoint_spec(endpoint)
                            if not spec['address'] and not spec['dynamic']:
                                self.fail(msg='Creating an endpoint requires an address or '
                                    'set dynamic: yes')
                            elif spec['dynamic'] and not (spec['ike_phase1_id_type'] or \
                                    spec['ike_phase1_id_value']):
                                self.fail(msg='When specifying a dynamic endpoint, you must '
                                    'also specify fields ike_phase1_id_type and ike_phase1_id_value')
                            
                            ext_gw.external_endpoint.create(**spec)
                            changed = True
                    
                if self.sites:
                    networks = []
                    for address in self.sites:
                        network = Network.get_or_create(
                            filter_key={'ipv4_network': address},
                            name='network-{}'.format(address),
                            ipv4_network=address)
                        networks.append(network)
                        
                    ext_gw.vpn_site.create(
                        name='{}-site'.format(self.name),
                        site_element=networks)
        
                if self.tags:
                    if self.add_tags(ext_gw, self.tags):
                        changed = True
                            
            elif state == 'absent':
                if not self.endpoint and not self.tags:
                    if ext_gw:
                        ext_gw.delete()
                        changed = True
                else:
                    if ext_gw:
                        if self.endpoint:
                            endpoint_names = [endpt for endpt in self.endpoint if 'name' in endpt]
                            if endpoint_names:
                                current = [e for e in ext_gw.external_endpoint.all()]
                                for endpoint in endpoint_names:
                                    obj = _get_endpoint_obj(endpoint, current)
                                    if obj:
                                        obj.delete()
                                        changed = True
                        if self.tags:
                            if self.remove_tags(ext_gw, self.tags):
                                changed = True
                    
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())

        self.results['changed'] = changed
        return self.results
    

def main():
    ExternalVPNGW()
    
if __name__ == '__main__':
    main()


