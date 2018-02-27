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
      - Identify the interface to be specified as management
    type: int
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
      - Location identifier for the engine. Used when engine is behind NAT
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
            '2.3' syntax
        type: list
        required: false
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW. Required to enable
        Antivirus, GTI and URL Filtering on the NGFW.
  enable_antivirus:
    description:
      - Enable Anti-Virus engine on the FW
    type: bool
    default: false
  enable_file_reputation:
    description:
      - Enable file reputation
    type: bool
    default: false
  enable_sidewinder_proxy:
    description:
      - Enable Sidewinder proxy capabilities
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
  - name: Create a layer 3 FW cluster, 2 nodes
    l3fw_cluster:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      cluster_mode: balancing
      comment: my new firewall
      default_nat: false
      domain_server_address: []
      enable_antivirus: false
      enable_gti: false
      enable_sidewinder_proxy: false
      interfaces:
      -   interface_id: '1000'
          nodes:
          -   address: 100.100.100.1
              network_value: 100.100.100.0/24
              nodeid: 1
          -   address: 100.100.100.2
              network_value: 100.100.100.0/24
              nodeid: 2
          type: tunnel_interface
          zone_ref: AWSTunnel
      -   interface_id: '4'
          nodes:
          -   address: 5.5.5.3
              network_value: 5.5.5.0/24
              nodeid: 2
          -   address: 5.5.5.2
              network_value: 5.5.5.0/24
              nodeid: 1
          zone_ref: heartbeat
      -   interface_id: '3'
      -   interface_id: '2'
          nodes:
          -   address: 3.3.3.2
              network_value: 3.3.3.0/24
              nodeid: 1
          -   address: 3.3.3.3
              network_value: 3.3.3.0/24
              nodeid: 2
          vlan_id: '3'
      -   interface_id: '2'
          nodes:
          -   address: 4.4.4.2
              network_value: 4.4.4.0/24
              nodeid: 1
          -   address: 4.4.4.3
              network_value: 4.4.4.0/24
              nodeid: 2
          vlan_id: '4'
          zone_ref: somevlan
      -   cluster_virtual: 2.2.2.1
          interface_id: '1'
          macaddress: 02:02:02:02:02:04
          network_value: 2.2.2.0/24
          nodes:
          -   address: 2.2.2.2
              network_value: 2.2.2.0/24
              nodeid: 1
          -   address: 2.2.2.3
              network_value: 2.2.2.0/24
              nodeid: 2
          zone_ref: internal
      -   cluster_virtual: 1.1.1.1
          interface_id: '0'
          macaddress: 02:02:02:02:02:02
          network_value: 1.1.1.0/24
          nodes:
          -   address: 1.1.1.2
              network_value: 1.1.1.0/24
              nodeid: 1
          -   address: 1.1.1.3
              network_value: 1.1.1.0/24
              nodeid: 2
      location: mylocation
      name: newcluster
      primary_heartbeat: '4'
      primary_mgt: '0'
      backup_mgt: '2.3'
      snmp:
          snmp_agent: myagent
          snmp_interface:
          - '1'
          - '2.4'
          snmp_location: newcluster
      tags:
      - footag

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
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engines import FirewallCluster
    from smc.api.exceptions import SMCException, InterfaceNotFound
    from smc.elements.helpers import zone_helper
    from smc.elements.profiles import SNMPAgent
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class YamlInterface(object):
    def __init__(self, interfaces):
        self.cluster_virtual = None
        self.interface_id = None
        self.macaddress = None
        self.network_value = None
        self.vlan_id = None
        self.zone_ref = None
        self.nodes = []
        for name, value in interfaces.items():
            if name not in ('nodes',):
                setattr(self, name, str(value))
            else:
                setattr(self, name, value)
        self.cvi_mode = 'packetdispatch' if self.cluster_virtual else None
        
    def __iter__(self):
        for node in self.nodes:
            yield node
    
    def __len__(self):
        return len(self.nodes)
    
    @property
    def is_vlan(self):
        return bool(self.vlan_id)
    
    def get_nodeid(self, nodeid):
        for nodes in self:
            if nodes.get('nodeid') == nodeid:
                return nodes
    
    def as_dict(self):
        if not self.is_vlan:
            delattr(self, 'vlan_id')
        return vars(self)

    def __repr__(self):
        return 'Interface(interface_id={}, vlan_id={})'.format(
            self.interface_id, self.vlan_id)

    
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
    
    @property
    def vlan_ids(self):
        """
        Return all defined VLAN ids
        """
        return [itf.vlan_id for itf in self
                if itf.vlan_id]
    
    def get_vlan(self, vlan_id):
        """
        Get the VLAN by id
        """
        for interface in self:
            if interface.vlan_id == vlan_id:
                return interface
    
    def get(self, interface_id):
        """
        Get the interface by ID
        """
        for interface in self:
            if interface.interface_id == str(interface_id):
                return interface


def delete_vlan_interface(self):
    """
    Delete a VLAN interface. This mutates the
    interface definition directly.
    
    :param self PhysicalVlanInterface
    :param str vlan_id: vlan ID
    :return: tuple(was_changed, delete_network)
    """
    changes = False, False
    # If we have interfaces, we will need to delete the route
    if self.addresses:
        changes = True, True
    else:
        vlan_str = self.interface_id
        changes = True, False
    
    self._parent.data['vlanInterfaces'] = [
        vlan for vlan in self._parent.data['vlanInterfaces']
        if vlan.get('interface_id') != vlan_str]
    
    return changes


def create_cluster_vlan_interface(interface, yaml):
    """
    Create a new VLAN interface on the cluster. This mutates the
    interface definition directly.
    
    :param PhysicalInterface interface: the interface ref
    :param YamlInterface yaml: yaml interface
    :return: True if the create met the criteria and was added, false
        if there was no cluster address or nodes defined
    """
    if (yaml.cluster_virtual and yaml.network_value) or yaml.nodes:
        builder, interface = interface._get_builder()
        if yaml.cluster_virtual and yaml.network_value:   # Add CVI 
            builder.add_cvi_to_vlan(yaml.cluster_virtual, yaml.network_value, yaml.vlan_id) 
            if yaml.macaddress: 
                builder.macaddress = yaml.macaddress 
                builder.cvi_mode = yaml.cvi_mode 
            else: 
                builder.cvi_mode = None 
        else: # VLAN on an NDI 
            builder.add_vlan_only(yaml.vlan_id, zone_ref=yaml.zone_ref) 
        if yaml.nodes: 
            for node in yaml.nodes: 
                node.update(vlan_id=yaml.vlan_id) 
                builder.add_ndi_to_vlan(**node)
        return True
    return False
                
    
def update_cluster_vlan_interface(self, yaml):
    """
    Update the cluster VLAN interface. This mutates the
    interface definition directly.
    
    :param self PhysicalVlanInterface
    :param YamlInterface yaml: yaml serialized to interface
    :return: tuple(was_changed, delete_network)
    """
    cluster_virtual = yaml.cluster_virtual
    cluster_mask = yaml.network_value
    nodes = yaml.nodes
    
    # Tuple is defined as: (was_changed, network). If the interface
    # is changed, store the original network in the second tuple position only
    # if it is in a different network than the original so it can be removed
    # from the routing table.
    changes = False, False
    
    # Check the zone to see if we have a different value
    # If a zone exists and yaml defines a different zone,
    # change. If no interface zone exists and yaml zone
    # exists, set it. If yaml and interface zone exists,
    # compare and only change if they are not the same
    if self.zone_ref and not yaml.zone_ref:
        self.data.update(zone_ref=None)
        changes = True, False
    elif not self.zone_ref and yaml.zone_ref:
        self.zone_ref = yaml.zone_ref
        changes = True, False
    elif self.zone_ref and yaml.zone_ref:
        zone = zone_helper(yaml.zone_ref)
        if zone != self.zone_ref:
            self.zone_ref = zone
            changes = True, False
        
    # Delete all interfaces
    if not nodes and self.has_interfaces:
        self.data.update(interfaces=[])
        changes = True, True
    else:
        for interface in self.interfaces:
            if cluster_virtual and interface.nodeid is None: #CVI has no nodeid
                if cluster_virtual != interface.address:
                    interface.update(address=cluster_virtual)
                    changes = True, False
                if cluster_mask and cluster_mask != interface.network_value:
                    interface.update(network_value=cluster_mask)
                    changes = True, True
            elif nodes:
                for node in nodes:
                    if node.get('nodeid') == interface.nodeid:
                        if interface.address != node.get('address'):
                            interface.update(address=node.get('address'))
                            changes = True, False                  
                        if interface.network_value != node.get('network_value'):
                            interface.update(network_value=node.get('network_value'))
                            changes = True, True
    return changes
                            

class StonesoftCluster(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_mode=dict(type='str', default='standby', choices=['standby', 'balancing']),
            interfaces=dict(type='list', default=[]),
            domain_server_address=dict(default=[], type='list'),
            location=dict(type='str'),
            comment=dict(type='str'),
            log_server=dict(type='str'),
            snmp=dict(type='dict', default={}),
            default_nat=dict(default=False, type='bool'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_sidewinder_proxy=dict(default=False, type='bool'),
            enable_file_reputation=dict(default=False, type='bool'),
            primary_mgt=dict(type='str', default='0'),
            backup_mgt=dict(type='str'),
            primary_heartbeat=dict(type='str'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cluster_mode = None
        self.location = None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.log_server = None
        self.snmp = None
        self.comment = None
        self.default_nat = None
        self.enable_antivirus = None
        self.enable_sidewinder_proxy = None #: TODO implement in check
        self.enable_file_reputation = None
        self.tags = None
        
        self.results = dict(
            changed=False,
            state=dict()
        )
            
        super(StonesoftCluster, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(FirewallCluster)
        
        try:
            if state == 'present':        
                if not engine:
                    if not self.interfaces:
                        self.fail(msg='You must provide at least one interface '
                            'configuration to create a cluster.')
                    
                    node_req = ('address', 'network_value', 'nodeid')
                    
                    itf = Interfaces(self.interfaces)
                    for interface in itf:
                        if not interface.interface_id:
                            self.fail(msg='interface_id is required for all interface '
                                'definitions')
                        for node in interface.nodes:
                            if not all(k in node for k in node_req):
                                self.fail(msg='Node missing required field. Required '
                                    'fields are: %s, interface: %s' %
                                    (list(node_req), interface))
                        
                    # Management interface
                    mgmt_interface = itf.get(self.primary_mgt)
                    if not mgmt_interface:
                        self.fail(msg='Management interface is not defined. Management was '
                            'specified on interface: %s' % self.primary_mgt)
                    
                    if self.check_mode:
                        return self.results
                    
                    interfaces = [intf.as_dict() for intf in itf
                                  if intf.interface_id != self.primary_mgt]

                    cluster = mgmt_interface.as_dict()
                    
                    cluster.update(
                        name=self.name,
                        cluster_mode=self.cluster_mode,
                        backup_mgt=self.backup_mgt,
                        primary_heartbeat=self.primary_heartbeat,
                        log_server_ref=self.log_server,
                        domain_server_address=self.domain_server_address,
                        default_nat=self.default_nat,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        location_ref=self.location,
                        interfaces=interfaces,
                        snmp_agent=self.snmp.get('snmp_agent', None),
                        snmp_location=self.snmp.get('snmp_location', None),
                        snmp_interface=self.snmp.get('snmp_interface', []),
                        comment=self.comment)

                    engine = FirewallCluster.create(**cluster)
                    changed = True

                    if self.tags:
                        if self.add_tags(engine, self.tags):
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
                    
                    status = engine.file_reputation.status
                    if self.enable_file_reputation:
                        if not status:
                            engine.file_reputation.enable()
                            changed = True
                    else:
                        if status:
                            engine.file_reputation.disable()
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
                    
                    if engine.cluster_mode != self.cluster_mode:
                        engine.data.update(cluster_mode=self.cluster_mode)
                        changed = True
                    
                    snmp = engine.snmp
                    if snmp.status and not self.snmp:
                        snmp.disable()
                        changed = True
                    elif not snmp.status and 'snmp_agent' in self.snmp:
                        agent = SNMPAgent(self.snmp.pop('snmp_agent', None))
                        snmp.enable(snmp_agent=agent, **self.snmp)
                        changed = True
                    elif snmp.status and self.snmp:
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
                            agent = SNMPAgent(self.snmp.pop('snmp_agent', None))
                            snmp.enable(snmp_agent=agent, **self.snmp)
                            changed = True

                    if self.check_mode:
                        return self.results
                    
                    # Check engine location value
                    location = engine.location
                    
                    if not location and self.location:
                        engine.location = self.location
                        changed = True
                    elif location and not self.location:
                        engine.location = None
                        changed = True
                    elif location and self.location:
                        if location.name != self.location:
                            engine.location = self.location
                            changed = True

                    # Update top level engine items so they are not lost when
                    # interface updates clear engine level cache
                    if changed:
                        engine.update()
                    
                    playbook = {}  # {interface_id: [interface defs]}
                    
                    for interface in self.interfaces:
                        playbook.setdefault(str(interface.get('interface_id')), []).append(
                            interface)
                    
                    # Track interfaces defined and add new ones as they are
                    # created so undefined interfaces can be deleted at the end
                    playbook_interfaces = playbook.keys()
                    
                    # Iterate the YAML defintions
                    for interface_id, interfaces in playbook.items():
                        
                        try:
                            interface = engine.interface.get(interface_id)
                            needs_update = False
                            
                            # Use case #1: The engine interface is defined but has no
                            # interface addresses. Create as VLAN if vlan_id is defined
                            # otherwise it's a non-VLAN interface
                            if not interface.has_interfaces and not \
                                interface.has_vlan:
                                yaml = Interfaces(interfaces).get(interface_id)
                                
                                # Note: If the interface already exists with a VLAN
                                # specified and no addresses, you cannot convert this to
                                # a non-VLAN interface. You must delete it and recreate.
                                if yaml.vlan_id:
                                    engine.physical_interface.add_ipaddress_and_vlan_to_cluster(
                                        **yaml.as_dict())
                                    changed = True
                                    continue
                                # Create a cluster interface only if a Cluster Virtual Address,
                                # network_value and macaddress, or nodes (NDI's) are specified.
                                elif (yaml.cluster_virtual and yaml.network_value and \
                                      yaml.macaddress) or len(yaml.nodes):
                                    engine.physical_interface.add_cluster_virtual_interface(
                                        **yaml.as_dict())
                                    changed = True
                                    continue    
                            
                            ifs = Interfaces(interfaces)
                            yaml = ifs.get(interface_id)
                            
                            # If the engine has at least 0 interfaces but as many interfaces
                            # as there are nodes (i.e. not multiple interfaces), continue.
                            # It is currently not supported to modify interfaces that have
                            # multiple IP addresses
                            if not interface.has_vlan and  0 <= len(yaml) <= len(engine.nodes):
                                
                                #TODO: Add cvi_mode to change_cluster_interface
                                # To delete nodes, remove the interface and re-add
                                if len(yaml): # Nodes are defined
                                    if interface.change_cluster_interface(
                                        cluster_virtual=yaml.cluster_virtual,
                                        network_value=yaml.network_value,
                                        macaddress=yaml.macaddress,
                                        nodes=yaml.nodes, zone_ref=yaml.zone_ref,
                                        vlan_id=None):
                                        
                                        changed = True
                                elif interface.has_interfaces:
                                    # Yaml nodes are undefined, reset if addresses exist
                                    interface.reset_interface()
                                    changed = True
                            
                            elif interface.has_vlan:
                                # Collection of VLANs. It is not possible to change the VLAN
                                # ID and the interface address. You must change one or the
                                # other as it's not possible to represent the previous then
                                # new cleanly in the YAML
                                
                                routes_to_remove = []
                                vlan_interfaces = interface.vlan_interface
                                
                                for vlan in vlan_interfaces:
                                    yaml = ifs.get_vlan(vlan.vlan_id)
                                    # If the YAML definition for the interface exists, either
                                    # create interface addresses or update existing, otherwise
                                    # delete the interface.
                                    if yaml is not None:
                                        if not vlan.has_interfaces:
                                            updated = create_cluster_vlan_interface(interface, yaml)
                                            network = False
                                        else:
                                            updated, network = update_cluster_vlan_interface(vlan, yaml)
                                    else:
                                        # YAML does not define an existing interface, so
                                        # delete the VLAN interface
                                        updated, network = delete_vlan_interface(vlan)
                                    
                                    # If the interface was updated, check to see if we need
                                    # to remove stale routes and add the interface ID so we
                                    # can get the routing for that specific interface_id
                                    if updated:
                                        needs_update = True
                                        if network:
                                            routes_to_remove.append(
                                                vlan.interface_id)
                                
                                # Check YAML to see if VLANs are defined in YAML but not
                                # in the engine interface and create
                                interface_vlans = set(vlan_interfaces.vlan_ids)
                                missing_vlans = [x for x in ifs.vlan_ids if x not in interface_vlans]
                                for vlan in missing_vlans:
                                    create_cluster_vlan_interface(interface, ifs.get_vlan(vlan))
                                    needs_update = True
                                      
                                if needs_update:
                                    interface.update()
                                    changed = True
                                if routes_to_remove:
                                    routing = engine.routing
                                    for int_id in routes_to_remove:
                                        for route in routing:
                                            if route.name == 'VLAN {}'.format(int_id):
                                                # If this interface has multiple networks, only
                                                # delete the obsolete network, otherwise delete all
                                                if len(list(route)) > 1:
                                                    for vlan_network in route:
                                                        if vlan_network.invalid:
                                                            vlan_network.delete()
                                                else:
                                                    route.delete()
                          
                        except InterfaceNotFound:
                            # Create the missing interface. Verify if it's a VLAN interface
                            # versus standard
                            ifs = Interfaces(interfaces)
                            for itf in ifs:
                                if itf.is_vlan:
                                    #TODO: Make this constructor take multiple VLANs at once
                                    engine.physical_interface.add_vlan_to_cluster(
                                        **itf.as_dict())
                                else:
                                    engine.physical_interface.add_cluster_virtual_interface(
                                        **itf.as_dict())
                                
                                changed = True
                            
                            playbook_interfaces.append(interface_id)

                    # Before deleting old interfaces, check the primary management
                    # interface setting and reset if necessary. This is done last
                    # in case primary management is moved to a new interface that
                    # was just created
                    management = engine.interface.get(self.primary_mgt)
                    if not management.is_primary_mgt:
                        engine.interface_options.set_primary_mgt(self.primary_mgt)
                        changed = True
                    
                    if engine.interface_options.backup_mgt != self.backup_mgt:
                        engine.interface_options.set_backup_mgt(self.backup_mgt)
                        changed = True
                    
                    if engine.interface_options.primary_heartbeat != self.primary_heartbeat:
                        engine.interface_options.set_primary_heartbeat(self.primary_heartbeat)
                        changed = True
                    
                    # Lastly, delete top level interfaces that are not defined in 
                    # the YAML or added while looping
                    for interface in engine.interface:
                        if interface.interface_id not in playbook_interfaces:
                            interface.delete()
                            changed = True

                    if self.tags:
                        if self.add_tags(engine, self.tags):
                            changed = True
                    else:
                        if self.clear_tags(engine):
                            changed = True

                self.results['state'] = engine.data
                
            elif state == 'absent':
                if engine:
                    engine.delete()
                    changed = True
        
        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed        
        return self.results
    

def main():
    StonesoftCluster()
    
if __name__ == '__main__':
    main()

        