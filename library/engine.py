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
module: engine
short_description: Operations on single or cluster layer 3 firewalls
description:
  - Create or delete a Stonesoft Layer 3 Firewall on the Stonesoft
    Management Center.

version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall cluster to add or delete
    required: true
  cluster_mode:
    description:
       - How to perform clustering, either balancing or standby
    choices: ['balancing', 'standby']
    default: standby
  primary_mgt:
    description:
      - Identify the interface to be specified as management. When creating a new
        cluster, the primary mgt must be a non-VLAN interface. You can move it to
        a VLAN interface after creation. If the interface cannot be used as this
        management type, operation is skipped.
    type: str
    required: true
  backup_mgt:
    description:
      - Specify an interface by ID that will be the backup management. If the
        interface is a VLAN, specify in '2.4' format (interface 2, vlan 4). If the interface
        cannot be used as this management type, operation is skipped.
    type: str
  primary_heartbeat:
    description:
      - Specify an interface for the primary heartbeat interface. This will
        default to the same interface as primary_mgt if not specified. If the interface
        cannot be used as this management type, operation is skipped.
    type: str
  backup_heartbeat:
    description:
      - Specify an interface by ID that will be the backup heartbeat. If the interface
        is a VLAN, specify in '2.4' format. If the interface cannot be used as this management
        type, operation is skipped.
  location:
    description:
      - Location identifier for the engine. Used when engine is behind NAT. If
        a location is set on the engine and you want to reset to unspecified,
        then use the keyword None.
    type: str
  interfaces:
    description:
        - Define the interface settings for this cluster interface, such as 
          address, network and node id.
    required: true
    suboptions:
      interface_id:
        description:
          - The cluster nic ID for this interface. Required.
        type: int
        required: true
      cluster_virtual:
        description:
          - The cluster virtual (shared) IP address for all cluster members. Not
            required if only creating NDI's
        type: str
        required: false
      network_value:
        description:
          - The cluster netmask for the cluster_vip. Required if I(cluster_virtual)
        type: str
      macaddress:
        description:
          - The mac address to assign to the cluster virtual IP interface. This is
            required if I(cluster_virtual)
        type: str
      zone_ref:
        description:
          - Optional zone name for this interface
        type: str
      nodes:
        description:
          - List of the nodes for this interface
        type: list
        required: true
        suboptions:
          address:
            description:
              - The IP address for this cluster node member. Required.
            type: str
            required: true
          network_value:
            description:
              - The netmask for this cluster node address. Required.
            type: str
            required: true
          nodeid:
            description:
              - The node ID for the cluster node. Required for each node in the cluster.
            type: int
            required: true
      comment:
        description:
          - Optional comment for this interface. If you want to unset the interface comment,
            set to an empty string or define with no value
        type: str
  default_nat:
    description:
      - Whether to enable default NAT on the FW. Default NAT will identify
        internal networks and use the external interface IP for outgoing
        traffic
    type: bool
    default: false
  antispoofing_network:
    description:
      - Antispoofing networks are automatically added to the route antispoofing
        configuration. The dict should have a key specifying the element type from
        SMC. The dict key value should be a list of the element types by name.
    type: dict
    choices:
    - network
    - group
    - host
  snmp:
    description:
      - SNMP settings for the engine
    type: dict
    suboptions:
      enabled:
        description:
          - Set this to False if enabled on the engine and wanting to remove
            the configuration.
        type: bool
      snmp_agent:
        description:
          - The name of the SNMP agent from within the SMC
        type: str
        required: true
      snmp_location:
        description:
          - Optional SNMP location string to add the SNMP configuration
        type: str
        required: false
      snmp_interface:
        description:
          - A list of interface IDs to enable SNMP. If enabling on a VLAN, use
            '2.3' syntax. If omitted, snmp is enabled on all interfaces
        type: list
        required: false
  policy_vpn:
    description:
      - Defines any policy based VPN membership for thie engine. You can specify
        multiple and whether the engine should be a central gateway or satellite
        gateway and whether it should be enabled for mobile gateway. Updating policy
        VPN on the engine directly requires SMC version >= 6.3.x
    type: list
    suboptions:
      name:
        description:
          - The name of the policy VPN.
        required: true
        type: str
      central_gateway:
        description:
          - Whether this engine should be a central gateway. Mutually exclusive with I(satellite_gateway)
        type: bool
      satellite_gateway:
        description:
          - Whether this engine should be a satellite gateway. Mutually exclusive with I(central_gateway)
        type: bool
      mobile_gateway:
        description:
          - Whether this engine should be enabled for remote VPN for mobile gateways (client VPN)
        type: bool
  netlinks:
    description:
      - Netlinks are a list of dicts defining where to place netlinks and any destinations on a
        given routing interface. Suboptions define the dict structure for each list dict
    type: list
    suboptions:
      name:
        decscription:
          - Name of the netlink. The netlink must pre-exist. Create using network_elements playbook
        type: str
        required: true
      interface_id:
        description:
          - The interface ID which to bind the netlink to. For VLAN, should be in dot syntax, i.e. 1.2,
            indicating interface 1, VLAN 2
        type: str
        required: true
      destination:
        description:
          - Destination elements specifying the networks, hosts, groups behind this netlink. Suboptions
            define the dict format for each list member
        type: list
        suboptions:
          name:
            description:
              - Name of the element
            type: str
            required: true
          type:
            description:
              - Type of element. Element type specifies the element type to look up. Element types are
                defined in network_elements module
            type: str
            required: true
  bgp:
    description:
      - If enabling BGP on the engine, provide BGP related settings
    type: dict
    suboptions:
      enabled:
        description:
          - Set to true or false to specify whether to configure BGP
        type: bool
      router_id:
        description:
          - Optional router ID to identify this BGP peer
        type: str
      autonomous_system:
        description:
          - The autonomous system for this engine. Provide additional arguments to
            allow for get or create logic
        suboptions:
          name:
            description:
                - Name of this AS
            type: str
            required: true
          as_number:
            description:
              - AS number for this BGP peer. Can be in dotted format
            type: str
            required: true
          comment:
            description:
              - Optional comment for AS
            type: str
      announced_network:
        description:
          - Announced networks identify the network and optional route map for
            internal networks announced over BGP. The list should be a dict with
            the key identifying the announced network type from SMC. The key should
            have a dict with name and route_map (optional) if the element should have
            an associated route_map.
        type: list
        choices:
            - network
            - group
            - host
      bgp_peering:
        description:
          - BGP Peerings to add to specified interfaces.
        type: list
        suboptions:
          name:
            description:
              - Name of the BGP Peering
            type: str
          external_bgp_peer:
            description:
              - If the external BGP peer next hop is an external bgp peer SMC element,
                use this identifier. Otherwise use engine if its another managed SMC FW.
            type: str
          engine:
            description:
              - If the external BGP peer next hop is an engine SMC element, use this
                identifier. Otherwise use external_bgp_peer if an unmanaged endpoint.
            type: str
          interface_id:
            description:
              - List of dict with two possible valid keys interface_id and network.
                Provide interface_id to specify the interfaces where the BGP Peering
                should be placed. Optionally provide the network key value if the
                interface has multiple addresses and you want to bind to only one.
            type: str
          network:
            description:
              - Optional network to bind to on the specified interface. Use if multiple
                IP addresses exist and you want to bind to only one.
            type: str
  enable_vpn:
    description:
      - Provide a list of IP addresses for which to enable VPN endpoints on. This should be a
        list of string IP address identifiers. If enabling on a DHCP address, use the value specified
        in the SMC under VPN endpoints, i.e. First DHCP Interface ip. 
    type: list
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW. Required to enable
        Antivirus, GTI and URL Filtering on the NGFW.
    type: list
    suboptions:
      name:
        description:
          - Name of the element, can be IP address or element
        type: str
      type:
        description:
          - Type of element. Valid entries are ipaddress, host, dns_server or
            dynamic_interface_alias. If using an element that is not ipaddress,
            it must pre-exist in the SMC
        type: str
  antivirus:
    description:
      - Enable Anti-Virus engine on the FW
    type: bool
    default: false
  file_reputation:
    description:
      - Enable file reputation
    type: bool
    default: false
  comment:
    description:
      - Optional comment tag for the engine
    type: str
  tags:
    description:
      - Optional tags to add to this engine
    type: list
  skip_interfaces:
    description:
      - Optionally skip the analysis of interface changes. This is only relevant when
        running the playbook against an already created engine. This must be false if
        attempting to add interfaces.
    type: bool
    default: false
  delete_undefined_interfaces:
    description:
      - Delete interfaces from engine cluster that are not defined in the YAML file. This can
        be used as a strategy to remove interfaces. One option is to retrieve the full engine
        json using engine_facts as yaml, then remove the interfaces from the yaml and set this
        to True.
    type: bool
    default: false
  state:
    description:
      - Create or delete a firewall cluster
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
- name: Firewall Template
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Layer 3 FW template
    engine:
      smc_logging:
        level: 10
        path: ansible-smc.log
      antispoofing_network:
        group:
        - group1
        host:
        - 2.2.2.23
        network:
        - gateway_129.47.0.0/16
        - gateway_129.48.0.0/16
      antivirus: true
      bgp:
        announced_network:
        - network:
            name: network-1.1.1.0/24
            route_map: myroutemap
        autonomous_system:
          as_number: 200
          comment: null
          name: as-200
        bgp_peering:
        - external_bgp_peer: bgppeer
          interface_id: '1000'
          name: bgppeering
        bgp_profile: Default BGP Profile
        enabled: true
        router_id: 2.3.4.5
      default_nat: true
      domain_server_address:
      - name: 8.8.8.8
        type: ipaddress
      - name: Localhost
        type: host
      file_reputation: true
      interfaces:
      - interface_id: '1000'
        interfaces:
        - nodes:
          - address: 10.10.10.1
            network_value: 10.10.10.1/32
            nodeid: 1
        type: tunnel_interface
      - interface_id: '2'
        interfaces:
        - nodes:
          - address: 21.21.21.21
            network_value: 21.21.21.0/24
            nodeid: 1
          vlan_id: '1'
      - interface_id: '1'
        interfaces:
        - nodes:
          - address: 2.2.2.1
            network_value: 2.2.2.0/24
            nodeid: 1
      - interface_id: '0'
        interfaces:
        - nodes:
          - address: 1.1.1.1
            network_value: 1.1.1.0/24
            nodeid: 1
      name: myfw3
      netlinks:
      - destination:
        - name: IP_10.3.3.1
          type: host
        interface_id: '2.1'
        name: netlink-21.21.21.0
      ospf:
        enabled: true
        ospf_areas:
        - interface_id: '2.1'
          name: myarea
          network: 21.21.21.0/24
        ospf_profile: Default OSPFv2 Profile
        router_id: 1.1.1.1
      policy_vpn:
      - central_gateway: true
        mobile_gateway: false
        name: myvpn
        satellite_gateway: false
      primary_mgt: '0'
      snmp:
        snmp_agent: fooagent
        snmp_interface:
        - '1'
        snmp_location: test
      type: single_fw


# Delete a layer 3 firewall, using environment variables for credentials
- name: delete firewall by name
  engine:
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
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, Cache

try:
    from smc.core.engines import Layer3Firewall, FirewallCluster
    from smc.core.engine import Engine
    from smc.vpn.policy import GatewayNode
    from smc.routing.bgp import AutonomousSystem, BGPPeering
    from smc.api.exceptions import SMCException, PolicyCommandFailed, \
        UnsupportedEngineFeature, InterfaceNotFound
    from smc.core.interfaces import TunnelInterface, Layer3PhysicalInterface, \
        Layer2PhysicalInterface, ClusterPhysicalInterface, PhysicalInterface
except ImportError:
    pass


class _Interface(object):
    def __init__(self, interface):
        self.interfaces = []
        self.interface_id = None
        #self.macaddress = None #: provide macaddress for cvi
        #self.zone_ref = None #: optional zone
        #self.comment = None #: optional comment
        for name, value in interface.items():
            setattr(self, name, value)
    
    def __iter__(self):
        for interface in self.interfaces:
            yield interface
    
    def __len__(self):
        return len(self.interfaces)
        
    @property
    def nodes(self):
        for interface in self:
            for node in interface.get('nodes', []):
                yield node
    
    @property
    def vlan_ids(self):
        """
        Return all defined VLAN ids
        """
        return [str(interface['vlan_id']) for interface in self.interfaces
                if 'vlan_id' in interface]

    def __repr__(self):
        return 'YamlInterface(interface_id={}, vlans={})'.format(
            self.interface_id, self.vlan_ids)


class SingleFWInterface(_Interface):
    def __init__(self, interface):
        super(SingleFWInterface, self).__init__(interface)

        if getattr(self, 'type', None) is None:
            self.interface = 'single_node_interface'

    def as_obj(self):
        if getattr(self, 'type', None) == 'tunnel_interface':
            return TunnelInterface(**vars(self))
        return Layer3PhysicalInterface(**vars(self))
    

class ClusterFWInterface(_Interface):
    def __init__(self, interface):
        super(ClusterFWInterface, self).__init__(interface)
        
        if hasattr(self, 'macaddress') and not hasattr(self, 'cvi_mode'):
            self.cvi_mode = 'packetdispatch'
    
    def as_obj(self):
        if getattr(self, 'type', None) == 'tunnel_interface':
            return TunnelInterface(**vars(self))
        return ClusterPhysicalInterface(**vars(self))


class Interfaces(object):
    """
    All interfaces defined by the YAML. Use this container
    to manage interfaces that might have single or VLAN type
    interfaces.
    
    :return: Interface
    """
    type_map = {'single_fw': SingleFWInterface,
                'fw_cluster': ClusterFWInterface}
    
    def __init__(self, typeof, interfaces):
        self._type = typeof
        self._interfaces = interfaces
    
    def __iter__(self):
        for interface in self._interfaces:
            yield self.type_map.get(self._type)(interface)

    def __contains__(self, interface_id):
        if '.' in str(interface_id):
            itf, vlan = str(interface_id).split('.')
            if self.get(itf) and vlan in self.get(itf).vlan_ids:
                return True
        elif self.get(interface_id):
            return True
        return False
        
    def get(self, interface_id):
        """
        Get the interface by ID
        """
        for interface in self:
            if str(interface.interface_id) == str(interface_id):
                return interface


def get_or_create_asystem(as_system):
    return AutonomousSystem.get_or_create(
        name=as_system.get('name'),
        as_number=as_system.get('as_number'),
        comment=as_system.get('comment'),
        with_status=True)


def get_or_create_bgp_peering(name):
    return BGPPeering.get_or_create(
        name=name, with_status=True)


def engine_types():
    return ['single_fw', 'fw_cluster']


def compat_pre643_update_policy_vpn(policy, internal_gw, vpn_def):
    """
    Compatible call for SMC version < 6.3.4. This is a far less optimal
    set of instructions as it generates many more possible queries to
    SMC. It is recommended to require SMC 6.3.4 as VPN references can
    be obtained from the engine json versus having to open an search
    a given VPN policy.
    
    :param PolicyVPN policy: policy as element
    :param InternalGateway internal_gw: the engines internal (VPN) gateway
        reference
    :param dict vpn_def: vpn def in the native yaml provided
    :rtype: bool
    """
    changed = False
    policy.open()
    # Find the central or satellite gateway that should be enabled first, and
    # remove the other gateway side if it exists
    if vpn_def.get('central_gateway') is not None:
        if vpn_def['central_gateway']:
            for gateway in policy.satellite_gateway_node:
                if gateway.name == internal_gw.name:
                    gateway.delete()
                    changed = True
                    break
            try:
                policy.add_central_gateway(internal_gw)
            except PolicyCommandFailed as e:
                if 'already exists' in str(e):
                    pass
        else: # Policy VPN should be disabled on central gateway
            for gateway in policy.central_gateway_node:
                if gateway.name == internal_gw.name:
                    gateway.delete()
                    changed = True
                    break
    
    if vpn_def.get('satellite_gateway') is not None:
        # If central gateway was provided, we would have already deleted it
        # so check for non-existence before reiterating the gw's
        if vpn_def['satellite_gateway']:
            # Only check central gateway if it's not defined as it would
            # not have been matched above
            if vpn_def.get('central_gateway') is None:
                for gateway in policy.central_gateway_node:
                    if gateway.name == internal_gw.name:
                        gateway.delete()
                        changed = True
                        break
            try:
                policy.add_satellite_gateway(internal_gw)
            except PolicyCommandFailed as e:
                if 'already exists' in str(e):
                    pass
        else: # Satellite gateway should be disabled
            for gateway in policy.satellite_gateway_node:
                if gateway.name == internal_gw.name:
                    gateway.delete()
                    changed = True
                    break
    
    if vpn_def.get('mobile_gateway') is not None:
        pass #Requires version 6.3.4 SMC to add mobile gateway
            
    policy.save()
    policy.close()
    return changed


def open_policy(policy, internal_gw, vpn_def, delete_first=None):
    """
    Operate on the VPN policy. The vpn_def defines a dict
    specifying how to operate on the relevant VPN site types.
    Example:
    {'satellite_gateway': False, 'central_gateway': True, mobile_gateway: True}
    Any one of these types can be out if no operations are required.
    True will require an add operation, whereas False will perform
    a delete.
    
    :param PolicyVPN policy: policy vpn element
    :param InternalGateway internal_gw: NGFW interface gateway ref
    :param dict vpn_def: vpn def as provided by yaml
    :param list delete_first: if using 6.3.4, delete first will have
        gateway elements retrieved from engine json that should be
        deleted before potentially changing the VPN policy but the
        policy must first be opened first
    :rtype: bool
    """
    changed = False
    policy.open()
    if delete_first:
        for gateway in delete_first:
            node = GatewayNode(href=gateway)
            node.delete()
        policy.save()
    if vpn_def.get('central_gateway'):
        policy.add_central_gateway(internal_gw)
        changed = True
    elif vpn_def.get('satellite_gateway'):
        policy.add_satellite_gateway(internal_gw)
        changed = True
    if vpn_def.get('mobile_gateway'):
        policy.add_mobile_gateway(internal_gw)
        changed = True
    policy.save()
    policy.close()
    return changed
    
   
class StonesoftEngine(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            type=dict(type='str', choices=engine_types()),
            cluster_mode=dict(type='str', choices=['standby', 'balancing']),
            interfaces=dict(type='list', default=[]),
            domain_server_address=dict(type='list', default=[]),
            location=dict(type='str'),
            bgp=dict(type='dict'),
            ospf=dict(type='dict'),
            antispoofing_network=dict(type='dict'),
            netlinks=dict(type='list', default=[]),
            comment=dict(type='str'),
            log_server=dict(type='str'),
            snmp=dict(type='dict', default={}),
            default_nat=dict(type='bool'),
            antivirus=dict(type='bool'),
            file_reputation=dict(type='bool'),
            primary_mgt=dict(type='str'),
            backup_mgt=dict(type='str'),
            primary_heartbeat=dict(type='str'),
            backup_heartbeat=dict(type='str'),
            policy_vpn=dict(type='list'),
            enable_vpn=dict(type='list', default=[]),
            tags=dict(type='list'),
            skip_interfaces=dict(type='bool', default=False),
            delete_undefined_interfaces=dict(type='bool', default=False),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.type = None
        self.cluster_mode = None
        self.location = None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.bgp = None
        self.ospf = None
        self.antispoofing_network = None
        self.netlinks = None
        self.log_server = None
        self.snmp = None
        self.comment = None
        self.default_nat = None
        self.antivirus = None
        self.file_reputation = None
        self.policy_vpn = False
        self.enable_vpn = []
        self.skip_interfaces = None
        self.delete_undefined_interfaces = None
        self.tags = None
        
        self.results = dict(
            changed=False,
            engine=dict(),
            state=[]
        )
        super(StonesoftEngine, self).__init__(self.module_args, supports_check_mode=True)
        
           
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(Engine)
        
        if state == 'present':
            if not engine:
                # Find interface designated as management
                if not self.interfaces:
                    self.fail(msg='You must provide at least one interface '
                        'configuration to create a firewall.')
                
                if not self.primary_mgt:
                    self.fail(msg='You must provide a primary_mgt interface to create '
                        'an engine.')
                
                if not self.type:
                    self.fail(msg='You must specify an engine by type when creating a '
                        'new engine. Types: %s' % engine_types())
                
                if 'fw_cluster' in self.type and not self.cluster_mode:
                    self.fail(msg='You must define a cluster mode to create an engine')

                itf = self.check_interfaces()
                
                # Management interface
                if not self.primary_mgt in itf:
                    self.fail(msg='Management interface is not defined. Management was '
                        'specified on interface: %s' % self.primary_mgt)
                
            else:
                self.type = engine.type
                if self.interfaces and not self.skip_interfaces:
                    itf = self.check_interfaces()

                else:
                    itf = []

            cache = Cache()
            
            #TODO: Remove DNS entries
            for dns in self.domain_server_address:
                if not isinstance(dns, dict):
                    self.fail(msg='DNS entries must be in dict format with keys name and type, '
                        'received: %s' % dns)
                element_type = dns.get('type')
                if element_type not in ('ipaddress', 'host', 'dns_server', 'dynamic_interface_alias'):
                    self.fail(msg='DNS server entries can only be of type ipaddress, '
                        'host or dns_server. Specified: %s' % dns)
                if element_type in ('host', 'dns_server', 'dynamic_interface_alias'):
                    cache._add_entry(element_type, dns.get('name'))
            
            if cache.missing:
                self.fail(msg='DNS entries specified are missing: %s' % cache.missing)
            
            # SNMP settings
            if self.snmp and self.snmp.get('enabled', True):
                cache._add_entry('snmp_agent', self.snmp.get('snmp_agent', None))
                if cache.missing:
                    self.fail(msg='SNMP configured but the SNMP Agent specified is not '
                        'found: %s' % cache.missing)
            
            # Only validate BGP if it's specifically set to enabled    
            if self.bgp and self.bgp.get('enabled', True):
                # BGP Profile if specified
                if self.bgp.get('bgp_profile', None):
                    cache._add_entry('bgp_profile', self.bgp['bgp_profile'])
                    if cache.missing:
                        self.fail(msg='A BGP Profile was specified that does not exist: '
                            '%s' % self.bgp['bgp_profile'])
                
                # Get external bgp peers, can be type 'engine' or 'external_bgp_peer'
                # Can also be empty if you don't want to attach a peer.
                peerings = self.bgp.get('bgp_peering', [])
                for peer in peerings:
                    if 'name' not in peer or 'interface_id' not in peer:
                        self.fail(msg='BGP Peering requires a name and interface_id for the '
                            'BGP Peering element. Info provided: %s' % peer)
                    
                    # The specified interface ID must exist for the BGP Peering to succeed. If
                    # the interface is defined in yaml, we'll assume it will be created. If the
                    # engine exists, check if it's defined or if it already exists
                    peer_id = str(peer['interface_id'])
                    if peer_id not in itf and not engine:
                        self.fail(msg='Interface ID: %s specified for BGP Peering does not '
                            'exist. You must specify a valid interface to bind the peer '
                            % peer_id)
                    elif engine and (peer_id not in engine.interface and peer_id not in itf):
                        self.fail(msg='BGP Peering interface id: %s specified does not exist '
                            'on the current engine: %s' % (peer_id, engine.name))
                    if 'external_bgp_peer' not in peer and 'engine' not in peer:
                        self.fail(msg='Missing the external_bgp_peer or engine parameter '
                            'which defines the next hop for the BGP Peering')
                    if 'external_bgp_peer' in peer:
                        cache._add_entry('external_bgp_peer', peer['external_bgp_peer'])
                    elif 'engine' in peer:
                        cache._add_entry('engine', peer['engine'])
        
                if cache.missing:
                    self.fail(msg='Missing external BGP Peering elements: %s' % cache.missing)
                
                as_system = self.bgp.get('autonomous_system', {})
                if not engine:
                    # We are trying to enable BGP on a new engine, Autonomous System
                    # is required
                    if not as_system:
                        self.fail(msg='You must specify an Autonomous System when enabling '
                            'BGP on a newly created engine.')
                if as_system:
                    if 'name' not in as_system or 'as_number' not in as_system:
                        self.fail(msg='Autonomous System requires a name and and '
                            'as_number value.')
                    
                networks = self.bgp.get('announced_network', [])
                announced_networks = self.validate_and_extract_announced(networks)
                cache.add(announced_networks)
                if cache.missing:
                    self.fail(msg='Missing elements in announced configuration: %s' % cache.missing)
            
            # Only validate OSPF if it's specifically set to enabled    
            if self.ospf and self.ospf.get('enabled', True):
                # OSPF Profile if specified
                if self.ospf.get('ospf_profile', None):
                    cache._add_entry('ospfv2_profile', self.ospf['ospf_profile'])
                    if cache.missing:
                        self.fail(msg='A OSPF Profile was specified that does not exist: '
                            '%s' % self.ospf['ospf_profile'])
                
                # Get OSPF Areas assigned. These are optional but if they exist, the
                # OSPF area must already exist
                for area in self.ospf.get('ospf_areas', []):
                    if 'interface_id' not in area or 'name' not in area:
                        self.fail(msg='An OSPF area must have a name and an interface_id '
                            'value identifying the interface to attach to: %s' % area)
                    
                    cache._add_entry('ospfv2_area', area.get('name'))
                    if cache.missing:
                        self.fail(msg='OSPF area referenced in configuration must pre-exist. OSPF '
                            'referenced was: %s' % area.get('name'))
                    
                    peer_id = str(area['interface_id'])
                    if peer_id not in itf and not engine:
                        self.fail(msg='Interface ID: %s specified for OSPF Area does not '
                            'exist. You must specify a valid interface to bind the peer '
                            % peer_id)
                    elif engine and (peer_id not in engine.interface and peer_id not in itf):
                        self.fail(msg='OSPF Area interface id: %s specified does not exist '
                            'on the current engine: %s' % (peer_id, engine.name))
            
            # Validate antispoofing networks if dynamic routing is enabled
            if self.antispoofing_network and ((self.ospf and self.ospf.get('enabled')) \
                or (self.bgp and self.bgp.get('enabled'))):
            
                self.validate_antispoofing_network(self.antispoofing_network)
                cache.add(self.antispoofing_network)
                if cache.missing:
                    self.fail(msg='Missing elements in antispoofing configuration: %s' %
                        cache.missing)
                         
            if self.policy_vpn:
                # Policy VPN requires at least a name in order to be configured. Set the
                # gateway types on the element to set or unset the engine from the specified
                # VPN. Setting an existing Policy VPN to False on a gateway where it was set
                # to True will remove it from the gateway. Make setting the gateways optional
                for vpn in self.policy_vpn:
                    if 'name' not in vpn:
                        self.fail(msg='Policy VPN name is not defined')
                    
                    if vpn.get('central_gateway') and vpn.get('satellite_gateway'):
                        self.fail(msg='When specifying policy vpn you must choose either '
                            'a central gateway or satellite gateway, not both')
                    cache._add_entry('vpn', vpn.get('name'))

                if cache.missing:
                    self.fail(msg='Missing elements in Policy VPN configuration: %s' % cache.missing)
                    
            if self.netlinks:
                # Netlinks can be specified on an interface along with destination elements
                # 'behind' these netlinks. Netlinks can only be placed on physical interface
                # types and not tunnel interfaces
                for netlink in self.netlinks:
                    if 'name' not in netlink or 'interface_id' not in netlink:
                        self.fail(msg='Netlink requires a name and interface_id for the '
                            'Netlink element. Info provided: %s' % netlink)
                    
                    int_id = str(netlink['interface_id'])
                    if int_id not in itf and not engine:
                        self.fail(msg='Interface ID: %s specified for netlink does not '
                            'exist. You must specify a valid interface to bind the netlink'
                            % int_id)
                    elif engine and (int_id not in engine.physical_interface and int_id not in itf):
                        self.fail(msg='Netlink interface id: %s specified does not exist '
                            'on the current engine: %s' % (int_id, engine.name))

                    # Destination elements for netlink are optional
                    if netlink.get('destination', []) and isinstance(netlink['destination'], list):
                        for dest in netlink['destination']:
                            if 'name' not in dest or 'type' not in dest:
                                self.fail(msg='Netlink destination element reference must '
                                    'contain name and type key values. Provided: %s' % dest)
                            cache._add_entry(dest['type'], dest['name'])

                    # Add the netlink
                    cache._add_entry('netlink', netlink['name'])
                    
                if cache.missing:
                    self.fail(msg='Missing elements in netlink configuration: %s' % cache.missing)
            
            self.cache = cache

        try:
            
            if state == 'present':
                if not engine:

                    interfaces = [vars(intf) for intf in itf]
                    
                    firewall = {'interfaces': interfaces}
                    firewall.update(
                        name=self.name,
                        primary_mgt=self.primary_mgt,
                        backup_mgt=self.backup_mgt,
                        log_server_ref=self.log_server,
                        domain_server_address=self.get_dns_entries(),
                        default_nat=self.default_nat,
                        enable_antivirus=self.antivirus,
                        enable_gti=self.file_reputation,
                        location_ref=self.location,
                        snmp=self.snmp,
                        comment=self.comment)
                    
                    if self.check_mode:
                        return self.results
                    
                    if 'fw_cluster' in self.type:
                        firewall.update(
                            cluster_mode=self.cluster_mode,
                            primary_heartbeat=self.primary_heartbeat)
                        
                        engine = FirewallCluster.create_bulk(**firewall)
                    else:
                        engine = Layer3Firewall.create_bulk(**firewall)
                    
                    self.results['state'].append(
                        {'name': engine.name, 'type': engine.type, 'action': 'created'})
                    changed = True
                
                else: # Engine exists, check for modifications
                    
                    # Changes made up to check mode are done on the
                    # cached instance of the engine and not sent to SMC
                    if self.update_general(engine):
                        changed = True
                    
                    if self.update_snmp(engine):
                        changed = True
                    
                    if 'fw_cluster' in self.type and \
                        (self.cluster_mode and engine.cluster_mode != self.cluster_mode):
                        engine.data.update(cluster_mode=self.cluster_mode)
                        changed = True
                    
                    if self.check_mode:
                        return self.results
                    
                    # Check engine location value
                    if self.update_location(engine):
                        changed = True
                    
                    # First actual engine update happens here
                    if changed:
                        engine.update()
                    
                    # Reset management interfaces before operating on interfaces
                    # in case interfaces are removed that might have previously
                    # been used as interface options (primary mgt, etc)
                    if self.reset_management(engine):
                        changed = True
                    
                    # Set skip interfaces to bypass interface checks
                    if not self.skip_interfaces:
                        self.update_interfaces(engine)
                    
                    # Lastly, delete top level interfaces that are not defined in 
                    # the YAML or added while looping. Only delete if skip_interfaces
                    # was not provided and that delete_undefined_interfaces is set to True
                    if not self.skip_interfaces and self.delete_undefined_interfaces:
                        self.check_for_deletes(engine)
                    
                ######                
                # Check for configurations that are not fed into the engine during creation
                # and would require a post create modification because the settings are
                # nested outside of the core engine blob by reference
                #
                # Start with dynamic routing 
                ######
                engine_needs_update = False
                
                if self.bgp:
                    if self.update_bgp(engine.dynamic_routing.bgp):
                        changed = True
                        engine_needs_update = True
                    
                    if engine.dynamic_routing.bgp.status:
                        if self.update_bgp_peering(engine):
                            changed = True
                
                if self.ospf:
                    if self.update_ospf(engine.dynamic_routing.ospf):
                        changed = True
                        engine_needs_update = True
                    
                    if engine.dynamic_routing.ospf.status:
                        if self.update_ospf_area(engine):
                            changed = True
                
                # Check if antispoofing networks are defined
                if self.antispoofing_network and (engine.dynamic_routing.ospf.status \
                    or engine.dynamic_routing.bgp.status):
                    if self.update_antispoofing(engine):
                        changed = True
                        engine_needs_update = True

                if engine_needs_update:
                    engine.update()
                
                # Remainder of updates are done through references and
                # therefore the core engine no longer needs updates
                for _endpoint in self.enable_vpn:
                    endpoint = engine.vpn_endpoint.get_contains(_endpoint)
                    if not endpoint.enabled:
                        endpoint.update(enabled=True)
                        changed = True
                        
                if self.netlinks:
                    if self.update_netlinks(engine):
                        changed = True
                
                if self.policy_vpn:
                    if self.update_policy_vpn(engine):
                        changed = True
                
                if self.tags:
                    if self.add_tags(engine, self.tags):
                        changed = True
                else:
                    if self.clear_tags(engine):
                        changed = True

            elif state == 'absent':
                if engine:
                    engine.delete()
                    self.results['state'].append(
                        {'name': engine.name, 'type': engine.type, 'action': 'delete'})
                    changed = True

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        if not changed and self.results.get('state'):
            changed = True
        self.results['changed'] = changed    
        return self.results

    def reset_management(self, engine):
        """
        Before deleting old interfaces, check the primary management
        interface setting and reset if necessary. This is done last
        in case primary management is moved to a new interface that
        was just created. If the management interface is not valid for
        the engine type or cannot be found, it is skipped.
        
        :param Engine engine: engine ref
        :rtype: bool
        """
        changed = False
        mgt = ('primary_mgt', 'backup_mgt', 'primary_heartbeat', 'backup_heartbeat')
        interface_options = engine.interface_options
        try:
            for option in mgt:
                if getattr(self, option):
                    if option in ('primary_heartbeat', 'backup_heartbeat') and \
                        not 'fw_cluster' in self.type:
                        continue
                    management = engine.interface.get(getattr(self, option))
                    if not isinstance(management, PhysicalInterface):
                        continue
                    if not getattr(management, 'is_%s' % option):
                        getattr(interface_options, 'set_%s' % option)(getattr(self, option))
                        # Check to see if it now matches
                        if getattr(management, 'is_%s' % option):
                            changed = True
                            self.results['state'].append({
                                'name': 'interface %s' % getattr(self, option),
                                'type': option,
                                'action': 'updated'})
        except InterfaceNotFound:
            pass
        
        return changed
    
    def check_for_deletes(self, engine):
        """
        Check for interfaces that should be deleted. This is only called
        when delete_undefined_interfaces is set to True. It is recommended
        to pull the engine as yaml, remove the interfaces to be deleted,
        then run the playbook.
        """
        yaml = Interfaces(self.type, self.interfaces)
        for interface in engine.interface:
            if isinstance(interface, Layer2PhysicalInterface):
                continue
            defined = yaml.get(interface.interface_id)
            if defined is None:
                self.results['state'].append({
                    'name': 'interface %s' % interface.interface_id,
                    'type': interface.typeof,
                    'action': 'delete'})
                interface.delete()
            else:
                vlan_updated = False
                if interface.has_vlan:
                    defined_vlans = defined.vlan_ids
                    vlan_interfaces = []
                    for vlan in interface.vlan_interface:
                        if vlan.vlan_id in defined_vlans:
                            vlan_interfaces.append(vlan)
                        else:
                            vlan_updated = True
                            self.results['state'].append({
                                'name': 'interface %s' % vlan.interface_id,
                                'type': 'vlan_interface',
                                'action': 'delete'})
                    if vlan_updated:
                        interface.data['vlanInterfaces'] = vlan_interfaces
                        interface.update()
    
    def update_interfaces(self, engine):
        """
        Update the interfaces on engine if necessary. You can also
        optionally set 'skip_interfaces' to bypass this check.
        
        :param engine Engine: ref to engine
        :rtype: tuple(interfaces, bool)
        """
        yaml = Interfaces(self.type, self.interfaces)
        
        for yaml_interface in yaml:
            interface, updated, created = engine.interface.update_or_create(
                yaml_interface.as_obj())
            
            if updated or created:
                self.results['state'].append({
                    'name': 'interface %s' % interface.interface_id,
                    'type': interface.typeof,
                    'action': 'created' if created else 'updated'})        

    def update_general(self, engine):
        """
        Update general settings on the engine
        
        :rtype: bool
        """
        changed = False
        for feature in ('default_nat', 'file_reputation', 'antivirus'):
            if getattr(self, feature, None) is not None:
                status = getattr(engine, feature).status
                if not status and getattr(self, feature):
                    getattr(engine, feature).enable()
                    changed = True
                elif status and not getattr(self, feature):
                    getattr(engine, feature).disable()
                    changed = True
        
        if self.domain_server_address:
            dns_elements = [d.value if d.value else d.element
                for d in engine.dns]
            entries = self.get_dns_entries() # From yaml
            
            if len(dns_elements) != len(entries) or set(dns_elements) ^ set(entries):
                engine.data.update(domain_server_address=[])
                engine.dns.add(entries)
                changed = True

        return changed
    
    def update_netlinks(self, engine):
        """
        Update netlinks on the engine
        
        :param Engine engine: engine reference
        :rtype: bool
        """
        changed = False
        for netlink in self.netlinks:
            route_node = engine.routing.get(netlink['interface_id'])
            static_netlink = self.cache.get('netlink', netlink['name'])
            netlink_gw = [self.cache.get(dest.get('type'), dest.get('name'))
                for dest in netlink.get('destination', [])]
            result = route_node.add_traffic_handler(
                static_netlink, netlink_gw)
            if result:
                self.results['state'].append(
                    {'name': 'interface %s' % netlink['interface_id'],
                     'type': 'netlink', 'action': 'created'})
                changed = True
        return changed
    
    def update_policy_vpn(self, engine):
        """
        Update the policy VPN. Requires version 6.3.x SMC or skipped
        
        :param engine Engine: engine reference
        :rtype: bool
        """
        changed = False
        try:
            vpn_mappings = engine.vpn_mappings
        except UnsupportedEngineFeature:
            return changed
        
        internal_gw = engine.vpn.internal_gateway
        for vpn_def in self.policy_vpn:
            policy_element = self.cache.get('vpn', vpn_def.get('name'))
            vpn = vpn_mappings.get(vpn_ref=policy_element.href) # VPNMapping
            if vpn:
                if not vpn.gateway_nodes_usage: # pre-6.3.4
                    if compat_pre643_update_policy_vpn(
                        policy_element, internal_gw, vpn_def):
                        changed = True
                else:
                    delete_first = set([]) #Track gateways that might need to be deleted
                    change_needed = False
                    if vpn_def.get('central_gateway') is not None:
                        if vpn_def['central_gateway']:
                            if not vpn.is_central_gateway:
                                change_needed = True
                                if vpn.is_satellite_gateway:
                                    delete_first.add(vpn._satellite_gateway)
                        elif vpn.is_central_gateway:
                            delete_first.add(vpn._central_gateway)
                            
                    if vpn_def.get('satellite_gateway') is not None:
                        if vpn_def['satellite_gateway']:
                            if not vpn.is_satellite_gateway:
                                change_needed = True
                                if vpn.is_central_gateway:
                                    delete_first.add(vpn._central_gateway)
                        elif vpn.is_satellite_gateway:
                            delete_first.add(vpn._satellite_gateway)
                    
                    if vpn_def.get('mobile_gateway') is not None:
                        pass

                    if change_needed or delete_first:
                        if open_policy(policy_element, internal_gw, vpn_def, delete_first):
                            changed = True
            else:
                if open_policy(policy_element, internal_gw, vpn_def):
                    changed = True
        
        if changed:
            self.results['state'].append(
                {'name': engine.name, 'type': 'policy_vpn', 'action': 'updated'})     
        return changed

    def update_snmp(self, engine):
        """
        Check for updates to SNMP on the engine
        
        :rtype: bool
        """
        changed = False
        
        if not self.snmp:
            return changed
        
        snmp = engine.snmp
        enable = self.snmp.pop('enabled', True)
        if not enable:
            if snmp.status:
                snmp.disable()
                changed = True
            return changed
        
        cfg = dict()
        if 'snmp_agent' in self.snmp:
            cfg.update(snmp_agent=self.cache.get(
                'snmp_agent', self.snmp.get('snmp_agent')))
        if 'snmp_location' in self.snmp:
            cfg.update(snmp_location=self.snmp.get('snmp_location'))
        if 'snmp_interface' in self.snmp:
            cfg.update(snmp_interface=self.snmp.get('snmp_interface'))
        
        modified = snmp.update_configuration(**cfg)
        if modified:
            self.results['state'].append(
                {'name': 'snmp', 'type': 'configuration', 'action': 'updated'})
            changed = True

        return changed
    
    def update_location(self, engine):
        """
        Check for an update on the engine location
        If the engine has a location and you want to reset it to
        unspecified, use 'None'.
        
        :rtype: bool
        """
        changed = False
        
        if self.location:
            location = engine.location # 1 Query
            if self.location.lower() == 'none':
                if location:
                    engine.location = None
                    changed = True
            elif not location:
                engine.location = self.location
                changed = True
            elif location and self.location != location.name:
                engine.location = self.location
                changed = True
        return changed

    def update_bgp(self, bgp):
        """
        Check for BGP update
        
        :param bgp BGP: reference from engine
        :rtype: bool
        """
        changed = False
        
        enabled = self.bgp.get('enabled', True)
        if not enabled:
            if bgp.status:
                bgp.disable()
                changed = True
            return changed
                        
        autonomous_system, created = get_or_create_asystem(
            self.bgp.get('autonomous_system'))
        if created:
            changed = True
        
        announced_network = self.bgp.get('announced_network')
        if announced_network is not None:
            announced_ne_setting = []
            for entry in announced_network:
                for typeof, dict_value in entry.items():
                    name = self.cache.get(typeof, dict_value.get('name'))
                    route_map = self.cache.get('route_map', dict_value.get('route_map'))
                    announced_ne_setting.append(
                        (name, route_map))
        
        cfg = dict()
        if autonomous_system:
            cfg.update(autonomous_system=autonomous_system)
        if announced_network is not None:
            cfg.update(announced_networks=announced_ne_setting)
        if 'bgp_profile' in self.bgp:
            cfg.update(bgp_profile=self.cache.get(
                'bgp_profile', self.bgp.get('bgp_profile', None)))
        if 'router_id' in self.bgp:
            cfg.update(router_id=self.bgp.get('router_id'))
        
        updated = bgp.update_configuration(
            enabled=True, **cfg)
    
        if updated:
            self.results['state'].append(
                {'name': 'bgp', 'type': 'configuration', 'action': 'updated'})
            changed = True
        return changed
    
    def update_ospf(self, ospf):
        """
        Update OSPF on the engine
        
        :param OSPF ospf: engine OSPF reference
        :rtype: bool
        """
        changed = False
        
        enabled = self.ospf.get('enabled', True)
        if not enabled:
            if ospf.status:
                ospf.disable()
                changed = True
            return changed
        
        cfg = dict()
        if 'ospf_profile' in self.ospf:
            cfg.update(ospf_profile=self.cache.get(
                'ospfv2_profile', self.ospf.get('ospf_profile')))
        if 'router_id' in self.ospf:
            cfg.update(router_id=self.ospf.get('router_id'))
        
        updated = ospf.update_configuration(
            enabled=True, **cfg)
        
        if updated:
            self.results['state'].append(
                {'name': 'ospf', 'type': 'configuration', 'action': 'updated'})
            changed = True
        return changed

    def update_ospf_area(self, engine):
        """
        Update the OSPF area on the interface
        
        :param Engine engine: engine reference
        :rtype: bool
        """
        changed = False
        for ospf_area in self.ospf.get('ospf_areas', []):
            iface = engine.routing.get(ospf_area.get('interface_id'))
            if iface.add_ospf_area(
                self.cache.get('ospfv2_area', ospf_area.get('name'))):
                
                self.results['state'].append(
                    {'name': 'interface %s' % ospf_area.get('interface_id'),
                     'type': 'ospfv2_area', 'action': 'updated'})
                changed = True
        return changed
    
    def update_bgp_peering(self, engine):
        """
        Update BGP Peering on the interface. Updates only occur if
        BGP peering does not already exist on interface
        
        :param Engine engine: engine ref
        :rtype: bool
        """
        changed = False
        peerings = self.bgp.get('bgp_peering', None)
        if not peerings:
            return changed
        
        for peer in peerings:
            bgp_peering, created = get_or_create_bgp_peering(peer.pop('name'))
            if created:
                changed = True
            
            if 'external_bgp_peer' in peer:
                extpeer = self.cache.get('external_bgp_peer', peer.get('external_bgp_peer'))
            elif 'engine' in peer:
                extpeer = self.cache.get('engine', peer.get('engine'))
        
            interface_id = peer.get('interface_id')
            network = peer.get('network') # Optionally bind to network
            routing = engine.routing.get(interface_id)
            
            modified = routing.add_bgp_peering(
                bgp_peering, extpeer, network)
            if modified:
                self.results['state'].append(
                    {'name': 'interface %s' % interface_id,
                     'type': 'bgp_peering', 'action': 'updated'})
                changed = True
        
        return changed
    
    def update_antispoofing(self, engine):
        """
        Update any antispoofing networks. 
        
        :param Engine engine: engine reference
        :rtype: bool
        """
        changed = False
        elements = [self.cache.get(typeof, _element)
            for typeof, element in self.antispoofing_network.items()
            for _element in element]
        
        if engine.dynamic_routing.update_antispoofing(elements):
            self.results['state'].append(
                {'name': 'dynamic routing', 'type': 'antispoofing',
                 'action': 'updated'})
            changed = True
        return changed
    
    def check_interfaces(self):
        """
        Check interfaces to validate node settings
        
        :rtype: Interfaces
        """
        node_req = set(['address', 'network_value', 'nodeid'])
        dynamic_node_req = set(['dynamic', 'dynamic_index'])
        itf = Interfaces(self.type, self.interfaces)
        for interface in itf:
            if interface.interface_id is None:
                self.fail(msg='interface_id is required for all interface '
                    'definitions, data: %s' % vars(interface))
            
            if 'fw_cluster' in self.type:    
                if getattr(interface, 'cvi_mode', None) and not getattr(interface, 'macaddress', None):
                    self.fail(msg='You must have a macaddress defined when defining '
                        'a CVI mode for an interface, interface_id: %s' % interface.interface_id)
            
                # Validate interfaces
                for _interface in interface:
                    # CVI's require a macaddress and cvi_mode
                    if _interface.get('cluster_virtual') and (not getattr(interface, 'macaddress', None)\
                        or not getattr(interface, 'cvi_mode', None)):
                        # TunnelInterface is exempt. Can't define macaddress on this type
                        if not getattr(interface, 'type', None) == 'tunnel_interface':
                            self.fail(msg='Cluster virtual interface require a macaddress and '
                                'cvi_mode be defined, invalid entry, interface_id: %s' %
                                interface.interface_id)
        
            for node in getattr(interface, 'nodes', []):
                node_values = set(node.keys())
                if not all(elem in node_values for elem in node_req) and \
                    not all(elem in node_values for elem in dynamic_node_req):
                    self.fail(msg='Invalid or missing field for node. Nodes must define '
                        'an interface address using: %s or a dynamic address using: %s. '
                        'Provided values: %s' % (list(node_req), list(dynamic_node_req),
                        list(node_values)))
#                 if node_values ^ node_req and node_values ^ dynamic_node_req:
#                     self.fail(msg='Invalid or missing field for node. Nodes must define '
#                         'an interface address using: %s or a dynamic address using: %s. '
#                         'Provided values: %s' % (list(node_req), list(dynamic_node_req),
#                             list(node_values)))
        return itf
    
    def get_dns_entries(self):
        """
        Get the DNS entries in the required format.
        
        :return: return a list of IP and Element types to be used for DNS
            on the engine
        :rtype: list
        """
        elements = []
        for dns in self.domain_server_address:
            element_type = dns.get('type')
            if element_type in ('host', 'dns_server', 'dynamic_interface_alias'):
                elements.append(
                    self.cache.get(element_type, dns.get('name')))
                continue
            elements.append(dns.get('name'))
        return elements
        
    def validate_antispoofing_network(self, s):
        """
        Validate the input antispoofing format:
        
        Expected format for antispoofing networks:
            {'network': [net1, net2],
             'host': [hosta, hostb}]}
        
        :return: None
        """
        valid = ('network', 'group', 'host')
        for typeof, values in s.items():
            if typeof not in valid:
                self.fail(msg='Antispoofing network definition used an invalid '
                    'element type: %s, valid: %s' % (typeof, list(valid)))
            elif not hasattr(values, '__iter__'):
                self.fail(msg='Antispoofing element values should be in list '
                    'format: %s, type: %s' % (values, type(values)))
    
    def validate_and_extract_announced(self, s):
        """
        Validate the announced network structure and format for
        inclusion into the cache for later use.
        
        Expected format for announced networks:
            [{'network': {'name': u'foo',
                          'route_map': u'myroutemap'}},
             {'host': {'name': u'All Routers (Site-Local)'}}]
        
        :return: dict with key: typeof, values=['name1', 'name2']
        """
        valid = ('network', 'group', 'host')
        for_cache = {}
        for announced in s:
            if not isinstance(announced, dict):
                self.fail(msg='Announced network type should be defined with '
                    'name and optionally route_map as a dict. Invalid entry '
                    'was: %s' % announced)
            for typeof, sub_dict in announced.items():
                if not isinstance(sub_dict, dict):
                    self.fail(msg='Announced network sub values must be of type dict. '
                        'Type was: %s' % type(sub_dict))
                if typeof not in valid:
                    self.fail(msg='Invalid announced network type was provided: %s, '
                        'valid types: %s' % (typeof, list(valid)))
                if 'name' not in sub_dict:
                    self.fail(msg='Announced Networks requires a name. Provided data '
                        'was: %s' % sub_dict)
                if 'route_map' in sub_dict:
                    for_cache.setdefault('route_map', []).append(
                        sub_dict['route_map'])
                for_cache.setdefault(typeof, []).append(sub_dict['name'])
        return for_cache

    
def main():
    StonesoftEngine()
    
if __name__ == '__main__':
    main()
