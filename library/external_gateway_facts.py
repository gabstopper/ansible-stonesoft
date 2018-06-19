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
module: external_gateway_facts
short_description: Facts about external VPN gateways
description:
  - An external vpn gateway is a non-SMC managed endpoint used for
    terminating a VPN. It defines the remote side networks and settings
    specific to handling VPN. Use I(expand) to specify attributes that
    should be resolved to raw data instead of href.

version_added: '2.5'

options:
  expand:
    description:
      - Expand sub elements that only provide href data. Specify a list of
        external gateways by name
    type: list
    choices:
      - vpn_site
      - gateway_profile
    
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Facts related to external VPN gateways
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Retrieve all external GW's
    external_gateway_facts:
  
  - name: Get a specific external GW details
    external_gateway_facts:
      filter: myremotevpn
  
  - name: Get a specific external GW, and expand supported attributes
    external_gateway_facts:
      filter: myremotevpn
      expand:
        - gateway_profile
        - vpn_site

  - name: Get engine details for 'myfw' and save in editable YAML format
    register: results
    engine_facts:
      smc_logging:
        level: 10
        path: ansible-smc.log
      filter: newcluster
      as_yaml: true

  - name: Write the yaml using a jinja template
    template: src=templates/engine_yaml.j2 dest=./l3fw_cluster.yml
'''


RETURN = '''
external_gateway:
    description: Example external gateway data 
    returned: always
    type: list
    sample: [
        external_endpoint": [{
            "address": "33.33.33.35", 
            "balancing_mode": "active", 
            "dynamic": false, 
            "enabled": true, 
            "force_nat_t": true, 
            "ike_phase1_id_type": 3, 
            "ipsec_vpn": true, 
            "name": "endpoint2", 
            "nat_t": true, 
            "read_only": false, 
            "system": false, 
            "udp_encapsulation": false
        }], 
        "gateway_profile": "http://1.1.1.1:8082/6.4/elements/gateway_profile/3", 
        "name": "myremotevpn", 
        "read_only": false, 
        "system": false, 
        "trust_all_cas": true, 
        "trusted_certificate_authorities": [], 
        "vpn_site": [{
            "gateway": "http://1.1.1.1:8082/6.4/elements/external_gateway/47", 
            "name": "myremotevpn-site", 
            "read_only": false, 
            "site_element": [
                "http://1.1.1.1:8082/6.4/elements/network/708"
            ], 
            "system": false
        }]]
'''

from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    format_element)


try:
    from smc.vpn.elements import ExternalGateway
except ImportError:
    pass


def to_yaml(gw):
    external_gateway = {'name': gw.name}
    endpoints = []
    for endpoint in gw.external_endpoint:
        endpoints.append({
            'name': endpoint.name,
            'address': endpoint.address,
            'enabled': endpoint.enabled})
    external_gateway.update(external_endpoint=endpoints)
    # Obtain VPN sites
    vpn_site = {}
    site_elements = {} # Dict of typeof: [element names]
    for site in gw.vpn_site:
        vpn_site.update(name=site.name)
        for element in site.site_element:
            vpn_site.setdefault(element.typeof, []).append(
                element.name)
        break
    vpn_site.update(site_elements)
    external_gateway.update(vpn_site=vpn_site)
    return external_gateway
        
       
def to_dict(external_gw, expand=None):
    """
    Flatten the external gateway
    
    :param ExternalGateway external_gw
    :return dict
    """
    external_gw.data.update(external_endpoint=
        [format_element(ep) for ep in external_gw.external_endpoint])
    
    expand = expand if expand else []
    
    if 'gateway_profile' in expand:
        external_gw.data['gateway_profile'] = format_element(external_gw.gateway_profile)
    
    if 'vpn_site' in expand:
        vpn_site = []
        for site in external_gw.vpn_site:
            site.data['site_element'] = [format_element(s) for s in site.site_element]
            vpn_site.append(format_element(site))
        external_gw.data['vpn_site'] = vpn_site
    else:
        external_gw.data.update(vpn_site=
            [format_element(site) for site in external_gw.vpn_site])

    return format_element(external_gw)

expands = ('vpn_site', 'gateway_profile')

class ExternalGWFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            expand=dict(type='list', default=[])
        )
        self.element = 'external_gateway'
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.expand = None
        self.exact_match = None
        self.case_sensitive = None
        
        required_if=([
            ('as_yaml', True, ['filter'])])
        
        self.results = dict(
            ansible_facts=dict(
                external_gateway=[]
            )
        )
        super(ExternalGWFacts, self).__init__(self.module_args, required_if=required_if,
                                              is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        for attr in self.expand:
            if attr not in expands:
                self.fail(msg='Invalid expandable attribute: %s provided. Valid '
                    'options are: %s'  % (attr, expands))
           
        result = self.search_by_type(ExternalGateway)
        # Search by specific element type
        if self.filter:
            if self.as_yaml:
                elements = [to_yaml(gw) for gw in result
                            if gw.name == self.filter]
            else:
                elements = [to_dict(element, self.expand) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts']['external_gateway'] = elements
        return self.results

def main():
    ExternalGWFacts()
    
if __name__ == '__main__':
    main()
