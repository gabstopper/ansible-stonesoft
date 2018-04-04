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
module: l3fw_cluster
short_description: Create or delete Stonesoft FW clusters
description:
  - Firewall clusters can be created with up to 16 nodes per cluster. Each
    cluster_node specified will define a unique cluster member and dictate
    the number of cluster nodes.
    You can fetch an existing engine using engine_facts and optionally save
    this as YAML to identify differences between runs.
    Interfaces and VLANs can be added, modified or removed. By default if the
    interface is not defined in the YAML, but exists on the engine, it will be
    deleted.
    To change an interface ID or VLAN id, you must delete the old and recreate
    the new interface definition. In addition, it is not possible to modify
    interfaces that have multiple IP addresses defined (they will be skipped).

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
        a VLAN interface after creation.
    type: str
    required: true
  backup_mgt:
    description:
      - Specify an interface by ID that will be the backup management. If the
        interface is a VLAN, specify in '2.4' format (interface 2, vlan 4).
    type: str
  primary_heartbeat:
    description:
      - Specify an interface for the primary heartbeat interface. This will
        default to the same interface as primary_mgt if not specified.
    type: str
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
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW. Required to enable
        Antivirus, GTI and URL Filtering on the NGFW.
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
  - name: Create a single layer 3 firewall
    l3fw_cluster:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      antivirus: false
      backup_mgt: '2.34'
      bgp:
          announced_network:
          -   network:
                  name: foonet
                  route_map: newroutemap
          antispoofing_network:
              group:
              - group1
              host:
              - 2.2.2.3
              network:
              - foo
          autonomous_system:
              as_number: 4261608949
              comment: optional
              name: myas
          bgp_profile: Default BGP Profile
          enabled: true
          router_id: 1.2.3.4
      cluster_mode: balancing
      comment: my new firewall
      default_nat: false
      domain_server_address:
      - 8.8.8.8
      file_reputation: false
      interfaces:
      -   interface_id: '1000'
          interfaces:
          -   nodes:
              -   address: 100.100.100.1
                  network_value: 100.100.100.0/24
                  nodeid: 1
              -   address: 100.100.100.2
                  network_value: 100.100.100.0/24
                  nodeid: 2
          type: tunnel_interface
          zone_ref: AWSTunnel
      -   cvi_mode: packetdispatch
          interface_id: '21'
          interfaces:
          -   cluster_virtual: 22.22.22.254
              network_value: 22.22.22.0/24
              nodes:
              -   address: 22.22.22.1
                  network_value: 22.22.22.0/24
                  nodeid: 1
              -   address: 22.22.22.2
                  network_value: 22.22.22.0/24
                  nodeid: 2
              vlan_id: '21'
          -   cluster_virtual: 21.21.21.254
              network_value: 21.21.21.0/24
              nodes:
              -   address: 21.21.21.2
                  network_value: 21.21.21.0/24
                  nodeid: 2
              -   address: 21.21.21.1
                  network_value: 21.21.21.0/24
                  nodeid: 1
              vlan_id: '20'
          macaddress: 02:02:02:20:20:22
      -   interface_id: '4'
          interfaces:
          -   nodes:
              -   address: 5.5.5.2
                  network_value: 5.5.5.0/24
                  nodeid: 1
              -   address: 5.5.5.3
                  network_value: 5.5.5.0/24
                  nodeid: 2
          zone_ref: heartbeat
      -   cvi_mode: packetdispatch
          interface_id: '0'
          interfaces:
          -   cluster_virtual: 1.1.1.1
              network_value: 1.1.1.0/24
              nodes:
              -   address: 1.1.1.2
                  network_value: 1.1.1.0/24
                  nodeid: 1
              -   address: 1.1.1.3
                  network_value: 1.1.1.0/24
                  nodeid: 2
          macaddress: 02:02:02:02:02:02
      -   comment: foocomment
          interface_id: '2'
          interfaces:
          -   comment: vlan comment
              nodes:
              -   address: 34.34.34.35
                  network_value: 34.34.34.0/24
                  nodeid: 2
              -   address: 34.34.34.34
                  network_value: 34.34.34.0/24
                  nodeid: 1
              vlan_id: '34'
          -   nodes:
              -   address: 35.35.35.35
                  network_value: 35.35.35.0/24
                  nodeid: 1
              -   address: 35.35.35.36
                  network_value: 35.35.35.0/24
                  nodeid: 2
              vlan_id: '35'
      location: foolocation
      name: newcluster2
      primary_heartbeat: '4'
      primary_mgt: '0'
      snmp:
          snmp_agent: myagent
          snmp_interface:
          - '2.35'
          - '2.34'
          - '0'
          snmp_location: snmplocation
      tags:
      - footag
      #skip_interfaces: false
      #delete_undefined_interfaces: false
      #state: absent

# Delete a cluster
- name: layer 3 cluster with 3 members
  l3fw_cluster:
    name: mycluster
    state: absent
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: Full json definition of NGFW
  returned: always
  type: dict
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, Cache


try:
    from smc.core.engines import FirewallCluster
    from smc.core.interfaces import ClusterPhysicalInterface, TunnelInterface
    from smc.api.exceptions import SMCException
    from smc.routing.bgp import AutonomousSystem, BGPPeering
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class YamlInterface(object):
    def __init__(self, interface):
        self.interfaces = []
        self.interface_id = None
        #self.macaddress = None #: provide macaddress for cvi
        #self.zone_ref = None #: optional zone
        #self.comment = None #: optional comment
        for name, value in interface.items():
            setattr(self, name, value)
        
        if hasattr(self, 'macaddress') and not hasattr(self, 'cvi_mode'):
            self.cvi_mode = 'packetdispatch'
    
    def as_obj(self):
        if getattr(self, 'type', None) == 'tunnel_interface':
            return TunnelInterface(interface=vars(self))
        return ClusterPhysicalInterface(**vars(self))

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


class Interfaces(object):
    """
    All interfaces defined by the YAML. Use this container
    to manage interfaces that might have single or VLAN type
    interfaces.
    
    :return: Interface
    """
    def __init__(self, interfaces):
        self._interfaces = interfaces
    
    def __iter__(self):
        for interface in self._interfaces:
            yield YamlInterface(interface)
    
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


class StonesoftCluster(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_mode=dict(type='str', choices=['standby', 'balancing']),
            interfaces=dict(type='list', default=[]),
            domain_server_address=dict(default=[], type='list'),
            location=dict(type='str'),
            bgp=dict(type='dict'),
            comment=dict(type='str'),
            log_server=dict(type='str'),
            snmp=dict(type='dict', default={}),
            default_nat=dict(type='bool'),
            antivirus=dict(type='bool'),
            file_reputation=dict(type='bool'),
            primary_mgt=dict(type='str'),
            backup_mgt=dict(type='str'),
            primary_heartbeat=dict(type='str'),
            tags=dict(type='list'),
            skip_interfaces=dict(type='bool', default=False),
            delete_undefined_interfaces=dict(type='bool', default=False),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cluster_mode = None
        self.location = None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.bgp = None
        self.log_server = None
        self.snmp = None
        self.comment = None
        self.default_nat = None
        self.antivirus = None
        self.file_reputation = None
        self.skip_interfaces = None
        self.delete_undefined_interfaces = None
        self.tags = None
        
        self.results = dict(
            changed=False,
            engine=dict(),
            state=[]
        )
        super(StonesoftCluster, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(FirewallCluster)
        
        if state == 'present':
            # Resolve dependencies
            if not engine:
                if not self.interfaces:
                    self.fail(msg='You must provide at least one interface '
                        'configuration to create a cluster.')
                
                if not self.primary_mgt:
                    self.fail(msg='You must provide a primary_mgt interface to create '
                        'an engine.')
                
                if not self.cluster_mode:
                    self.fail(msg='You must define a cluster mode to create an engine')
                
                itf = self.check_interfaces()
                
                # Management interface
                if not self.primary_mgt in itf:
                    self.fail(msg='Management interface is not defined. Management was '
                        'specified on interface: %s' % self.primary_mgt)
            
            if engine and self.interfaces and not self.skip_interfaces:
                itf = self.check_interfaces()
            
            cache = Cache()
            
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
                    if 'name' not in peer:
                        self.fail(msg='BGP Peering requires a name field to identify the '
                            'BGP Peering element. Peer info provided: %s' % peer)
                    if 'external_bgp_peer' not in peer and 'engine' not in peer:
                        self.fail(msg='Missing the external_bgp_peer or engine parameter '
                            'which defines the next hop for the BGP Peering')
                    if 'external_bgp_peer' in peer:
                        cache._add_entry('external_bgp_peer', peer['external_bgp_peer'])
                    elif 'engine' in peer:
                        cache._add_entry('fw_cluster', peer['engine'])
        
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

                spoofing = self.bgp.get('antispoofing_network', {})
                self.validate_antispoofing_network(spoofing)
                cache.add(spoofing)
                if cache.missing:
                    self.fail(msg='Missing elements in antispoofing configuration: %s' %
                        cache.missing)
                    
                networks = self.bgp.get('announced_network', [])
                announced_networks = self.validate_and_extract_announced(networks)
                cache.add(announced_networks)
                if cache.missing:
                    self.fail(msg='Missing elements in announced configuration: %s' % cache.missing)
                
            self.cache = cache
        
        try:
            
            if state == 'present':
                if not engine:

                    interfaces = [vars(intf) for intf in itf]
                    
                    cluster = {'interfaces': interfaces}
                    cluster.update(
                        name=self.name,
                        cluster_mode=self.cluster_mode,
                        primary_mgt=self.primary_mgt,
                        backup_mgt=self.backup_mgt,
                        primary_heartbeat=self.primary_heartbeat,
                        log_server_ref=self.log_server,
                        domain_server_address=self.domain_server_address,
                        default_nat=self.default_nat,
                        enable_antivirus=self.antivirus,
                        enable_gti=self.file_reputation,
                        location_ref=self.location,
                        snmp=self.snmp,
                        comment=self.comment)
                    
                    if self.check_mode:
                        return self.results
                    
                    engine = FirewallCluster.create_bulk(**cluster)
                    changed = True
                    
                else: # Engine exists, check for modifications
                    
                    # Changes made up to check mode are done on the
                    # cached instance of the engine and not sent to SMC
                    if self.update_general(engine):
                        changed = True
                    
                    if self.update_snmp(engine):
                        changed = True
                    
                    if self.cluster_mode and engine.cluster_mode != self.cluster_mode:
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
                # Check for BGP configuration on either newly created engine
                # or on the existing
                ######
                if self.bgp:
                    bgp = engine.bgp
                    enabled = self.bgp.get('enabled', True)
                    if not enabled and bgp.status:
                        bgp.disable()
                        changed = True
                    
                    elif enabled:
                        
                        if self.update_bgp(bgp):

                            autonomous_system, created = get_or_create_asystem(
                                self.bgp.get('autonomous_system'))
                            
                            if created:
                                changed = True
                            
                            bgp.disable() # Reset BGP configuration
                            bgp.enable(
                                autonomous_system,
                                announced_networks=[],
                                antispoofing_networks=self.antispoofing_format(),
                                router_id=self.bgp.get('router_id', ''),
                                bgp_profile=self.cache.get('bgp_profile',
                                    self.bgp.get('bgp_profile', None)))
                            
                            for network in self.announced_network_format():
                                bgp.advertise_network(**network)
                            changed = True
                    
                    if changed:
                        engine.update()
                
                    if enabled:
                        # BGP Peering is last since the BGP configuration may be placed
                        # on interfaces that might have been modified or added. It is
                        # possible that this could fail 
                        peerings = self.bgp.get('bgp_peering', None)
                        if peerings:
                            for peer in peerings:
                                peering, created = get_or_create_bgp_peering(
                                    peer.pop('name'))
                                if created:
                                    changed = True
                                # Update the peering on the interface
                                if self.update_bgp_peering(engine, peering, peer):
                                    changed = True
                    
                if self.tags:
                    if self.add_tags(engine, self.tags):
                        changed = True
                else:
                    if self.clear_tags(engine):
                        changed = True

                self.results['engine'] = engine.data.data
                
            elif state == 'absent':
                if engine:
                    engine.delete()
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
        was just created.
        
        :param Engine engine: engine ref
        :rtype: bool
        """
        changed = False
        if self.primary_mgt:
            management = engine.interface.get(self.primary_mgt)
            if not management.is_primary_mgt:
                engine.interface_options.set_primary_mgt(self.primary_mgt)
                changed = True
        
        if self.backup_mgt:
            if engine.interface_options.backup_mgt != self.backup_mgt:
                engine.interface_options.set_backup_mgt(self.backup_mgt)
                changed = True
        
        if self.primary_heartbeat:
            if engine.interface_options.primary_heartbeat != self.primary_heartbeat:
                engine.interface_options.set_primary_heartbeat(self.primary_heartbeat)
                changed = True
        return changed
    
    def check_interfaces(self):
        """
        Check interfaces to validate node settings
        
        :rtype: Interfaces
        """
        node_req = set(['address', 'network_value', 'nodeid'])
        itf = Interfaces(self.interfaces)
        for interface in itf:
            if interface.interface_id is None:
                self.fail(msg='interface_id is required for all interface '
                    'definitions, data: %s' % vars(interface))
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
            
            for node in interface.nodes:
                node_values = set(node.keys())
                differences = node_values ^ node_req
                if differences:
                    self.fail(msg='Invalid or missing field for node. Valid fields '
                        'are %s. Difference was: %s' % (list(node_req),
                            list(differences)))
        return itf
    
    def update_interfaces(self, engine):
        """
        Update the interfaces on engine if necessary. You can also
        optionally set 'skip_interfaces' to bypass this check.
        
        :param engine Engine: ref to engine
        :rtype: tuple(interfaces, bool)
        """
        yaml = Interfaces(self.interfaces)
        
        for yaml_interface in yaml:
            interface, updated, created = engine.interface.update_or_create(
                yaml_interface.as_obj())
            
            if updated or created:
                self.results['state'].append({
                    'interface_id': interface.interface_id,
                    'type': interface.typeof,
                    'action': 'created' if created else 'updated'})        
    
    def check_for_deletes(self, engine):
        """
        Check for interfaces that should be deleted. This is only called
        when delete_undefined_interfaces is set to True. It is recommended
        to pull the engine as yaml, remove the interfaces to be deleted,
        then run the playbook.
        """
        yaml = Interfaces(self.interfaces)
        for interface in engine.interface:
            defined = yaml.get(interface.interface_id)
            if defined is None:
                self.results['state'].append({
                    'interface_id': interface.interface_id,
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
                                'interface_id': vlan.interface_id,
                                'type': 'vlan_interface',
                                'action': 'delete'})
                    if vlan_updated:
                        interface.data['vlanInterfaces'] = vlan_interfaces
                        interface.update()
                        
    def update_general(self, engine):
        """
        Update general settings on the engine
        
        :rtype: bool
        """
        changed = False
        if self.default_nat is not None:
            status = engine.default_nat.status
            if not status and self.default_nat:
                engine.default_nat.enable()
                changed = True
            elif status and not self.default_nat: # False or None
                engine.default_nat.disable()
                changed = True
        
        if self.file_reputation is not None:
            status = engine.file_reputation.status
            if not status and self.file_reputation:
                engine.file_reputation.enable()
                changed = True
            elif status and not self.file_reputation:
                engine.file_reputation.disable()
                changed = True
        
        if self.antivirus is not None:
            status = engine.antivirus.status
            if not status and self.antivirus:
                engine.antivirus.enable()
                changed = True
            elif status and not self.antivirus:
                engine.antivirus.disable()
                changed = True
        
        if self.domain_server_address:
            dns = [d.value for d in engine.dns]
            # DNS changes, wipe old and add new
            if set(dns) ^ set(self.domain_server_address):
                engine.data.update(domain_server_address=[])
                engine.dns.add(self.domain_server_address)
                changed = True
        return changed
                            
    def update_snmp(self, engine):
        """
        Check for updates to SNMP on the engine
        
        :rtype: bool
        """
        changed = False
        if self.snmp:
            snmp = engine.snmp
            enable = self.snmp.pop('enabled', True)
            if not enable:
                if snmp.status:
                    snmp.disable()
                    changed = True
            else:
                if not snmp.status:
                    agent = self.cache.get('snmp_agent', self.snmp.pop('snmp_agent'))
                    snmp.enable(snmp_agent=agent, **self.snmp)
                    changed = True
                else: # Enabled check for changes
                    update_snmp = False
                    if snmp.agent.name != self.snmp.get('snmp_agent', ''):
                        update_snmp = True
                    if snmp.location != self.snmp.get('snmp_location'):
                        update_snmp = True
                    
                    snmp_interfaces = [interface.interface_id for interface in snmp.interface]
                    yaml_snmp_interfaces = map(str, self.snmp.get('snmp_interface', []))
                    if not set(snmp_interfaces) == set(yaml_snmp_interfaces):
                        update_snmp = True
                    
                    if update_snmp:
                        agent = self.cache.get('snmp_agent', self.snmp.pop('snmp_agent'))
                        snmp.enable(snmp_agent=agent, **self.snmp)
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
        
        :param bgp BGP: reference from engine.bgp
        :rtype: bool (needs update)
        """
        if bgp.router_id != self.bgp.get('router_id', None):
            return True
        
        if self.bgp.get('bgp_profile', None):
            # Only changed BGP Profile if specified, BGP Profile. Policy is cache
            bgp_profile = self.cache.get('bgp_profile', self.bgp['bgp_profile'])
            if not bgp.profile:
                return True
            elif bgp.profile.name != bgp_profile.name:
                return True
        
        if set(bgp.data.get('antispoofing_ne_ref', [])) ^ \
            set(self.antispoofing_format()):
            return True
        
        # Announced networks
        current = bgp.data.get('bgp', {}).get('announced_ne_setting', [])
        current_dict = {entry.get('announced_ne_ref'): entry.get('announced_rm_ref')
            for entry in current}
        
        # Put the specified dict into a format to compare
        new_dict = {entry.get('network'): entry.get('route_map')
            for entry in self.announced_network_format()}
        
        if cmp(current_dict, new_dict) != 0:
            return True
        return False
    
    def update_bgp_peering(self, engine, bgp_peering, peering_dict):
        """
        Update BGP Peering on the interface. Only update if the
        peering isn't already there.
        
        :param Engine engine: engine ref
        :param BGPPeering bgp_peering: peering ref
        :param dict peering_dict: list of interfaces to add to
        :rtype: bool
        """
        if 'external_bgp_peer' in peering_dict:
            extpeer = self.cache.get('external_bgp_peer', peering_dict.get('external_bgp_peer'))
        elif 'engine' in peering_dict:
            extpeer = self.cache.get('fw_cluster', peering_dict.get('engine'))
        
        changed = False
        interface_id = peering_dict.get('interface_id')
        network = peering_dict.get('network')
        routing = engine.routing.get(interface_id)
        
        interface_peerings = list(routing.bgp_peerings)
        needs_update = False
        if interface_peerings:
            for _, net, peering in interface_peerings:
                if network and net.ip == network:
                    if peering.name != bgp_peering.name:
                        needs_update = True
                elif peering.name == bgp_peering.name:
                    # Check for nested gateways under peering and add if the
                    # peering next hop (external_bgp_peer, engine) are not
                    # already there
                    if not any(p.name == extpeer.name for p in peering):
                        needs_update = True
                elif bgp_peering.name != peering.name:
                    needs_update = True
        else:
            needs_update = True
        
        if needs_update:
            modified = routing.add_bgp_peering(
                bgp_peering, extpeer, network)
            if modified:
                changed = True
       
        return changed
        
    def validate_antispoofing_network(self, s):
        """
        Validate the input antispoofing format:
        
        Expected format for antispoofing networks:
            {'network': [net1, net2],
             'host': [hosta, hostb}]}
        
        :return: None
        """
        valid = ('network', 'group', 'host')
        if not isinstance(s, dict):
            self.fail(msg='Antispoofing networks should be defined as a dict of '
            'element types with a list of values, received: %s' % s)
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
                for_cache.setdefault(typeof, []).append(
                    sub_dict['name'])
        return for_cache
        
    def antispoofing_format(self):
        """
        Get the antispoofing format
        
        :rtype: list of href
        """
        return [self.cache.get(typeof, value).href
            for typeof, v in self.bgp.get('antispoofing_network', {}).items()
            for value in v]
    
    def announced_network_format(self):
        """
        Get the announced network format
        
        :rtype: list(dict)
        """
        announced_ne_setting = []
        for entry in self.bgp.get('announced_network', []):
            for typeof, dict_value in entry.items():
                name = self.cache.get(typeof, dict_value.get('name'))
                route_map = self.cache.get('route_map', dict_value.get('route_map'))
                announced_ne_setting.append(
                    {'network': name.href, 'route_map': route_map if not route_map else route_map.href})
        return announced_ne_setting

    
def main():
    StonesoftCluster()
    
if __name__ == '__main__':
    main()

        