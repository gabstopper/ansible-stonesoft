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
module: route_vpn
short_description: Create a route based VPN
description:
  - Create a route based VPN. Route VPN's are typically created between a managed
    Stonesoft FW and a 3rd party device (AWS, Azure, etc). You must pre-create
    the internal FW prior to running this module. If doing an IPSEC wrapped VPN,
    you must also specify a tunnel interface for which to bind (must be pre-created)
    and specify an IP address/interface id to specify the ISAKMP listener.

version_added: '2.5'

options:
  name:
    description:
      - The name for this route VPN. 
    required: true
    type: str
  type:
    description:
      - The type of IPSEC vpn to create
    type: str
    choices: ['ipsec', 'gre']
    default: ipsec
  local_gw:
    description:
      - Represents the locally managed Stonesoft FW gateway by name
    type: str
    suboptions:
      name:
        description:
          - The name of the Stonesoft FW gateway
        type: str
        required: true
      tunnel_interface:
        description:
          - The ID for the tunnel interface
        type: str
        required: true
      interface_id:
        description:
          - The interface ID to enable IPSEC. If multiple IP addresses exist
            on the interface, IPSEC will be enabled on all. Use I(interface_ip) as
            an alternative.
        type: str
        required: true
      interface_ip:
        description:
          - An interface IP addresses to enable IPSEC. This is an alternative to using
            I(interface_id) since you can specify an exact IP address, independent of the
            interface ID.
        type: str
  remote_gw:
    description:
      - The name of the remote GW. If the remote gateway is an Stonesoft FW, it must
        pre-exist. Use the local_gw documentation for settings. If it is an External Gateway,
        this module can pre-create the gateway based on the gateway settings provided. 
    type: str
    suboptions:
      name:
        description:
          - The name of the External Gateway. If the gateway does not exist, it will be created
            if you provide the I(address) and I(networks) parameters.
        type: str
        required: true
      address:
        description:
          - IP address for the remote external gateway. Required if you want the gateway auto
            created.
        type: str
      preshared_key:
        description:
          - If this is an External Gateway, you must provide a pre-shared key to be used between
            the gateways. If the gateway is another Stonesoft FW, a key will be auto-generated.
        type: str
      network:
        description:
          - Specify the networks for the External Gateway in cidr format. If the network elements
            already exist, they will be used. They will be auto-created using a syntax of
            'network-1.1.1.0/24'. Required for External Gateways that are created.
        type: list
  state:
    description:
      - Specify a create or delete operation
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
- name: Create a new Route VPN with an external gateway
    route_vpn:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      name: mynrbvpn
      type: ipsec
      local_gw:
        name: myfw
        tunnel_interface: 1000
        interface_id: 1
      remote_gw:
        name: extgw3
        type: external_gateway
        address: 33.33.33.41
        preshared_key: abc123
        network:
          - 172.18.1.0/24
          - 172.18.2.0/24
          - 172.18.15.0/24

- name: Create a new Route VPN between two Stonesoft Fws
    route_vpn:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      name: mynrbvpn
      type: ipsec
      local_gw:
        name: myfw
        tunnel_interface: 1000
        interface_id: 1
        interface_ip: 10.10.10.10
      remote_gw:
        name: dingo
        tunnel_interface: 1000
        interface_ip: 36.35.35.37
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
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    get_or_create,
    ro_element_type_dict,
    element_type_dict,
    format_element)


try:
    from smc.vpn.route import RouteVPN, TunnelEndpoint
    from smc.vpn.elements import ExternalGateway
    from smc.core.engine import Engine
    from smc.api.exceptions import SMCException
except ImportError:
    pass

    
def vpn_element_type_dict():
    types = dict(
        external_gateway=dict(type=ExternalGateway))
    
    for t in types.keys():
        types[t]['attr'] = ['name']
    return types


class StonesoftRouteVPN(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            type=dict(default='ipsec', type='str', choices=['ipsec', 'gre']),
            local_gw=dict(type='dict'),
            remote_gw=dict(type='dict'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.type = None
        self.local_gw = None
        self.remote_gw = None
        self.tags = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftRouteVPN, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        rbvpn = self.fetch_element(RouteVPN)

        try:
            if state == 'present':
                
                self._fail_on_invalid_gw(self.local_gw)
    
                if self.type == 'ipsec':
                    if ('interface_id' or 'interface_ip') not in self.local_gw:
                        self.fail(msg='You must provide interface_id or interface_address '
                            'to enable IPSEC on an interface.')
                
                local_name = self.local_gw.get('name')
                local_gw = self.get_engine(local_name)
                    
                # A remote gateway can be an internal NGFW from within the
                # same SMC, or can be an ExternalGateway.    
                if 'type' in self.remote_gw:
                    if 'preshared_key' not in self.remote_gw:
                        self.fail(msg='You must provide a preshared_key for a 3rd '
                            'party gateway.')

                    if not self.remote_gw.get('network', []):
                        self.fail(msg='You must provide networks to identify the '
                            'remote site protected address space.')
                    
                    if 'address' not in self.remote_gw:
                        self.fail(msg='You must provide an address for the remote '
                            'gateway to configure a RBVPN.')
                
                    # Fails if external gateway does not exist
                    remote_gw = get_or_create(
                        dict(external_gateway={'name': self.remote_gw.get('name')}),
                        vpn_element_type_dict(), check_mode=self.check_mode)
                    
                    networks = []
                    for network in self.remote_gw['network']:
                        networks.append(get_or_create(
                            dict(network={'name': 'network-{}'.format(network),
                                          'ipv4_network': network}),
                            element_type_dict(), hint=network, check_mode=self.check_mode))
                    
                    if self.check_mode:
                        if remote_gw is not None:
                            self.results['state'].append(remote_gw)
                        for network in networks:
                            if network:
                                self.results['state'].append(network)

                else: # Remote gateway claims to be an internal engine
                    self._fail_on_invalid_gw(self.remote_gw)
                    
                    remote_name = self.remote_gw.get('name')
                    remote_gw = self.get_engine(remote_name)
                
                if self.check_mode:
                    return self.results
                
                # Build out the RBVPN components if we haven't failed here
                local_tunnel_if = local_gw.tunnel_interface.get(
                    self.local_gw.get('tunnel_interface'))
                
                self.enable_vpn_endpoint(local_gw, self.local_gw)
                
                if isinstance(remote_gw, Engine):
                    self.enable_vpn_endpoint(remote_gw, self.remote_gw)
                    tunnel_if = remote_gw.tunnel_interface.get(
                        self.remote_gw.get('tunnel_interface'))
        
                    remote_gateway = TunnelEndpoint.create_ipsec_endpoint(
                        remote_gw.vpn.internal_gateway, tunnel_if)
                else:
                    # An ExternalGateway defines the remote side as a 3rd party gateway
                    # Add the address of the remote gateway and the network element created
                    # that defines the remote network/s.
                    remote_name = self.remote_gw.get('name')
                    remote_address = self.remote_gw.get('address')
                    if not remote_gw.external_endpoint.get_contains(remote_address):
                        remote_gw.external_endpoint.create(
                            name=remote_name, address=self.remote_gw.get('address'))
                        self.results['changed'] = True
                    if not remote_gw.vpn_site.get_exact('{}-site'.format(remote_name)):
                        remote_gw.vpn_site.create(name='{}-site'.format(remote_name), site_element=networks)
                        self.results['changed'] = True
                    remote_gateway = TunnelEndpoint.create_ipsec_endpoint(remote_gw)
                
                # Create the tunnel endpoints
                if not rbvpn:
                    local_gateway = TunnelEndpoint.create_ipsec_endpoint(
                        local_gw.vpn.internal_gateway, local_tunnel_if)
                    
                    vpn = RouteVPN.create_ipsec_tunnel(
                        name=self.name,
                        preshared_key=self.remote_gw.get('preshared_key'),
                        local_endpoint=local_gateway, 
                        remote_endpoint=remote_gateway)

                    self.results['changed'] = True
                    self.results['state'] = format_element(vpn)
                
            elif state == 'absent':

                if rbvpn:
                    rbvpn.delete()
                
        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())

        return self.results
    
    def get_engine(self, name):
        """
        Get the engine. If in check_mode, just set the results.
        Otherwise return the engine or raise the error.
        
        :param str name: name of engine to fetch
        :raises SMCException: engine not found 
        :rtype: Engine
        """
        try:
            engine = Engine.get(name)
            return engine
        except SMCException:
            if self.check_mode:
                self.results['state'].append(
                    dict(name=name,
                         type='engine',
                         msg='Specified element does not exist'))
                return
            raise

    def enable_vpn_endpoint(self, engine, gateway):
        """
        Enable the IPSEC VPN endpoint on all addresses of an
        interface ID or a specific address
        
        :param Engine engine: the engine reference
        :param dict gateway: the gateway dict
        :return: None
        """
        endpoints = engine.vpn.internal_endpoint
        if 'interface_id' in gateway:
            # Raises if interface does not exist
            intf = engine.interface.get(gateway['interface_id'])
            for addr, _, _ in intf.addresses:
                endpoint = endpoints.get_contains(addr)
                if not endpoint.enabled:
                    endpoint.update(enabled=True)
                    self.results['changed'] = True
        else: # Enable on the specific address specified
            vpn_endpoint = endpoints.get_exact(gateway['interface_ip'])
            if not vpn_endpoint:
                self.fail(msg='Interface IP: {} is not found on this engine '
                    .format(gateway.get('interface_ip')))
            if not vpn_endpoint.enabled:
                vpn_endpoint.update(enabled=True)
                self.results['changed'] = True
       
    def _fail_on_invalid_gw(self, gw):
        """
        An internal GW needs to have at minimum a name which identifies the
        engine name. If this is an external gateway, it also needs a name
        for creation or modification.
        """
        required = ('name', 'tunnel_interface')
        for req in required:
            if req not in gw:
                self.fail(msg='Missing required field/s for gateway. Fields '
                    'needed: {}'.format(list(required)))

def main():
    StonesoftRouteVPN()
    
if __name__ == '__main__':
    main()