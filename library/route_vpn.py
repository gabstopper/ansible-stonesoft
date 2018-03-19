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
      - Represents the locally managed Stonesoft FW gateway. If the remote_gw is also
        a Stonesoft managed device, use the same parameters to define
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
      address:
        description:
          - An interface IP addresses to enable IPSEC. If there are multiple IP addresses
            on a single interface specified with I(interface_id) and you want to bind to
            only that address
        type: str
        required: false
  remote_gw:
    description:
      - The name of the remote GW. If the remote gateway is an Stonesoft FW, it must
        pre-exist. Use the local_gw documentation for settings. If it is an External Gateway,
        this module will create the gateway based on the gateway settings provided if it
        doesn't already exist. This documents an External Gateway configuration
    type: str
    suboptions:
      name:
        description:
          - The name of the External Gateway. If the gateway does not exist, it will be created
            if you provide the I(address) and I(networks) parameters.
        type: str
        required: true
      preshared_key:
        description:
          - If this is an External Gateway, you must provide a pre-shared key to be used between
            the gateways. If the gateway is another Stonesoft FW, a key will be auto-generated.
        type: str
      type:
        description:
          - Set to external_gateway if this is an external gateway element type
        type: str
      vpn_site:
        description:
          - Defines the VPN site for the protected networks on other end of external gateway
        type: dict
        suboptions:
          name:
            description:
              - Name of VPN site
            type: str
            required: true
          network:
            description:
              - A valid element type from SMC. Typically this is network or host. List elements
                should be valid names of the specified element
            type: list
      external_endpoint:
        description:
          - The external endpoint gateways where the RBVPN will terminate. Any options that are
            supported by the smcpython ExternalEndpoint.create constructor are supported values
            for this definition
        type: list
        required: true
        suboptions:
          name:
            description: 
              - Name of the external endpoint
            type: str
            required: True
          address:
            description:
              - A valid IP address of the external gateway
            type: str
            required: true
          enabled:
            description:
              - Whether to enable the gateway. 
            type: bool
  tags:
    description:
      - Provide an optional category tag to the engine. If the category does not
        exist, it will be created
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
    name: myrbvpn
    type: ipsec
    local_gw:
      name: newcluster
      tunnel_interface: 1001
      interface_id: 1
      #address: 2.2.2.2
    remote_gw:
      name: extgw3
      preshared_key: abc123
      type: external_gateway
      vpn_site:
        name: site12
        network:
          - network-172.18.1.0/24
          - network-172.18.2.0/24
        host:
          - hosta
      external_endpoint:
        - name: endpoint1
          address: 33.33.33.41
          enabled: true
        - name: endpoint2
          address: 34.34.34.34
          force_nat_t: true
          enabled: true
    tags:
      - footag

- name: Create a new Route VPN with internal gateways
  route_vpn:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    name: myrbvpn
    type: ipsec
    local_gw:
      name: newcluster
      tunnel_interface: 1001
      interface_id: 1
      #address: 2.2.2.2
    remote_gw:
      name: myfw
      tunnel_interface: 1000
      interface_id: 0  
  tags:
    - footag     
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
    StonesoftModuleBase, Cache)


try:
    from smc.vpn.route import RouteVPN, TunnelEndpoint
    from smc.vpn.elements import ExternalGateway
    from smc.core.engine import Engine
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class StonesoftRouteVPN(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            type=dict(default='ipsec', type='str', choices=['ipsec', 'gre']),
            local_gw=dict(type='dict', required=True),
            remote_gw=dict(type='dict', required=True),
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
        changed = False
        
        if state == 'present':
        
            local_engine = self.get_managed_gateway(self.local_gw)
            local_tunnel_interface = self.get_tunnel_interface(
                local_engine, self.local_gw.get('tunnel_interface'))
            local_internal_endpoint = self.get_ipsec_endpoint(
                local_engine, self.local_gw.get('interface_id'),
                address=self.local_gw.get('address'))
            
            if self.remote_gw.get('type', None) != 'external_gateway':
                remote_engine = self.get_managed_gateway(self.remote_gw)
                remote_tunnel_interface = self.get_tunnel_interface(
                    remote_engine, self.remote_gw.get('tunnel_interface'))
                remote_internal_endpoint = self.get_ipsec_endpoint(
                    remote_engine, self.remote_gw.get('interface_id'),
                    address=self.remote_gw.get('address'))
            else:
                # External Gateway
                req = ('name', 'preshared_key', 'external_endpoint')
                for required in req:
                    if required not in self.remote_gw:
                        self.fail(msg='Missing required field for the external endpoint '
                            'configuration: %s' % required)
                
                external_gateway = dict(name=self.remote_gw['name'])
                # External Endpoints are defined in the External Gateway.
                # Build the data structures for a call to ExternalGateway.update_or_create
                external_endpoint = []
                for endpoint in self.remote_gw['external_endpoint']:
                    if 'name' not in endpoint or 'address' not in endpoint:
                        self.fail(msg='An external endpoint must have at least a '
                            'name and an address definition.')
                    external_endpoint.append(endpoint)
                external_gateway.update(external_endpoint=external_endpoint)
                
                # Verify specified VPN Sites exist before continuing
                if 'vpn_site' in self.remote_gw:
                    site_name = self.remote_gw.get('vpn_site', {}).pop('name', None)
                    if not site_name:
                        self.fail(msg='A VPN site requires a name to continue')
                    
                    # Get the elements
                    cache = Cache()
                    cache.add(self.remote_gw.get('vpn_site', {}))
                    if cache.missing:
                        self.fail(msg='Could not find the specified elements for the '
                            'VPN site configuration: %s' % cache.missing)
                    site_element = [value.href for _, values in cache.cache.items()
                        for value in values]
                    external_gateway.update(
                        vpn_site=[dict(name=site_name, site_element=site_element)])

        try:
            if state == 'present':
                
                if self.check_mode:
                    return self.results
 
                # Create the tunnel endpoints
                if not rbvpn:
                    local_gateway = TunnelEndpoint.create_ipsec_endpoint(
                        local_engine.vpn.internal_gateway, local_tunnel_interface)
                    
                    # Enable the IPSEC listener on specified interface/s
                    if self.update_ipsec_listener(local_internal_endpoint):
                        changed = True
                    
                    is_external = self.remote_gw.get('type', None) == 'external_gateway'
                    if not is_external:
                        remote_gateway = TunnelEndpoint.create_ipsec_endpoint(
                            remote_engine.vpn.internal_gateway, remote_tunnel_interface)
                        
                        if self.update_ipsec_listener(remote_internal_endpoint):
                            changed = True
                        
                    else: # Update or Create
                        gw, created = ExternalGateway.update_or_create(with_status=True, **external_gateway)
                        remote_gateway = TunnelEndpoint.create_ipsec_endpoint(gw) 
                        if created:
                            changed = True
                    
                    vpn = dict(
                        name=self.name,
                        local_endpoint=local_gateway,
                        remote_endpoint=remote_gateway)
                    
                    if is_external:
                        vpn.update(preshared_key=self.remote_gw['preshared_key'])
                    
                    routevpn = RouteVPN.create_ipsec_tunnel(**vpn)
                    changed = True
                    
                    self.results['state'] = routevpn.data.data
                    self.results['changed'] = changed
        
            elif state == 'absent':
                if rbvpn:
                    rbvpn.delete()
                    changed = True
                
        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())

        self.results['changed'] = changed        
        return self.results
    
    def get_ipsec_endpoint(self, engine, interface_id, address=None):
        """
        Get the internal endpoint for which to enable IPSEC on for the
        internal FW. This is required for IPSEC based RBVPN.
        
        :param engine Engine: engine reference, already obtained
        :param str interface_id: interface ID specified for IPSEC listener
        :rtype: list(InternalEndpoint)
        """
        try:
            interface = engine.interface.get(interface_id)
        except SMCException as e:
            self.fail(msg='Fetch IPSEC interface for endpoint failed: %s' % str(e))
        
        internal_endpoint = engine.vpn.internal_endpoint # Collection
        endpoints = []
        if address:
            ep = internal_endpoint.get_exact(address)
            if ep:
                endpoints.append(ep)
        else: # Get all endpoints for the interface
            for addr, network, nicid in interface.addresses:  # @UnusedVariable
                if internal_endpoint.get_exact(addr):
                    endpoints.append(
                        internal_endpoint.get_exact(addr))
        if not endpoints:
            self.fail(msg='No IPSEC endpoint interfaces found. The specified '
                'interface ID was: %s and address: %s' % (interface_id, address))
        return endpoints
    
    def update_ipsec_listener(self, internal_endpoints):
        """
        Update the internal endpoint to enable the IPSEC listener on
        the specified interface/s.
        
        :param list(InternalEndpoint) internal_endpoints: internal endpoints
        :rtype: bool
        """
        changed = False
        for endpoint in internal_endpoints:
            if not endpoint.enabled:
                endpoint.update(enabled=True)
                changed = True
        return changed
                        
    def get_tunnel_interface(self, engine, interface_id):
        """
        Get the specified Tunnel Interface for the gateway.
        
        :param engine Engine: engine ref
        :param str interface_id: pulled from gateway yaml
        :rtype: TunnelInterface
        """
        tunnel_interface = None
        for interface in engine.tunnel_interface:
            if interface.interface_id == str(interface_id):
                tunnel_interface = interface
                break
        
        if not tunnel_interface:
            self.fail(msg='Cannot tunnel interface: %s for specified gateway '
                '%s' % (interface_id, engine.name))
        return tunnel_interface
                
    def get_managed_gateway(self, gw):
        """
        If the gateway is a locally managed SMC gateway, tunnel interface and
        an IPSEC interface is required.
        
        :param dict local_gw,remote_gw: yaml definition
        :rtype: Engine
        """
        for req in ('name', 'tunnel_interface', 'interface_id'):
            if req not in gw:
                self.fail(msg='Managed gateway requires name, interface_id and '
                    'tunnel_interface fields')
        
        managed_gw = Engine.get(gw.get('name'), raise_exc=False)
        if not managed_gw:
            self.fail(msg='The specified managed gateway specified does not '
                'exist: %s' % gw.get('name'))
        return managed_gw

       
def main():
    StonesoftRouteVPN()
    
if __name__ == '__main__':
    main()