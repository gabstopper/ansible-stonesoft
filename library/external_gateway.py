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
    or route based VPN.

version_added: '2.5'

options:
  name:
    description:
      - The name of the external gateway
    required: true
  vpn_site:
    description:
      - VPN sites defined the networks for this VPN. A site entry should be a network
        CIDR address. If the network does not exist, the element will be created.
    type: dict
    suboptions:
      element type:
        description:
          - This is the type of element that is referenced in the SMC. For example, network,
            host, group, etc. This should be a dict of lists, where the dict key is the element
            type and the list value is the name of each element.
        required: true
  external_endpoint:
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
- name: Create a static IP based external gateway
  register: result
  external_gateway:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    external_endpoint:
    -   address: 33.33.33.41
        enabled: true
        name: extgw3 (33.33.33.41)
    -   address: 34.34.34.34
        enabled: true
        name: endpoint2 (34.34.34.34)
    -   address: 44.44.44.44
        enabled: true
        name: extgw4 (44.44.44.44)
    -   address: 33.33.33.50
        enabled: true
        name: endpoint1 (33.33.33.50)
    name: extgw3555
    vpn_site:
        group:
        - hostgroup
        host:
        - hosta
        name: site12a
        network:
        - network-172.18.1.0/24
        - network-172.18.2.0/24


- name: Delete an external gateway
  external_vpn_gw:
    name: myextgw
    state: absent
'''


RETURN = '''
state:
  description: Output of operations performed on gateway
  returned: always
  type: list
  example: 
        [{'action': 'created', 'type': 'external_gateway', 'name': u'_extgw3'},
         {'action': 'modified', 'type': 'external_gateway', 'name': u'_extgw3'},
         {'action': 'deleted', 'type': 'external_gateway', 'name': u'_extgw3'}]
'''

import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache, delete_element)

try:
    from smc.vpn.elements import ExternalGateway
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class ExternalVPNGW(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            external_endpoint=dict(type='list', default=[]),
            vpn_site=dict(type='dict'),
            tags=dict(type='list'),
            ignore_err_if_not_found=dict(type='bool', default=True),
            state=dict(default='present', choices=['present', 'absent'])
        )
        self.tags = None
        self.name = None
        self.vpn_site = None
        self.external_endpoint = None
        self.ignore_err_if_not_found = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(ExternalVPNGW, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        if state == 'present':
            external_gateway = {'name': self.name}
            
            # External Endpoints are defined in the External Gateway.
            # Build the data structures for a call to ExternalGateway.update_or_create
            external_endpoint = []
            for endpoint in self.external_endpoint:
                if 'name' not in endpoint or 'address' not in endpoint:
                    self.fail(msg='An external endpoint must have at least a '
                        'name and an address definition.')
                external_endpoint.append(endpoint)
            external_gateway.update(external_endpoint=external_endpoint)

            if self.vpn_site:
                site_name = self.vpn_site.pop('name', None)
                if not site_name:
                    self.fail(msg='VPN site requires a name attribute')
            
                cache = Cache()
                cache.add(self.vpn_site)
                if cache.missing:
                    self.fail(msg='Could not find the specified elements for the '
                        'VPN site configuration: %s' % cache.missing)
                
                site_element = [value.href for _, values in cache.cache.items()
                        for value in values]
                external_gateway.update(
                    vpn_site=[dict(name=site_name, site_element=site_element)])
        
        try:        
            if state == 'present':
                
                gateway, updated, created = ExternalGateway.update_or_create(
                    with_status=True, **external_gateway)
                
                if created or updated:
                    self.results['state'].append(
                        {'name': gateway.name, 'type': gateway.typeof,
                         'action': 'created' if created else 'modified'})
                    changed = True

                if self.tags:
                    if self.add_tags(gateway, self.tags):
                        changed = True
            
            elif state == 'absent':
                result = delete_element(ExternalGateway(self.name),
                    self.ignore_err_if_not_found) 

                if 'action' in result:
                    changed = True 
                self.results['state'].append(result) 

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed         
        return self.results
    

def main():
    ExternalVPNGW()
    
if __name__ == '__main__':
    main()


