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
  - Firewall clusters can be created with up to 16 nodes per cluster. For
    each cluster_node specified, this will define a unique cluster member.
    Modifications can be made to existing interfaces, interfaces can be
    added, VLANs can be added and removed. By default if the interface is
    not defined in the YAML, it will be deleted. VLANs can be removed or
    added however if a vlan ID needs to change, you must delete the old
    and recreate the new VLAN definition. In addition, it is not possible
    to modify interfaces that have multiple IP addresses defined.

version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall cluster to add or delete
    required: true
  cvi_mode:
    description:
      - How to perform clustering, either balancing or standby
    choices: ['balancing', 'standby']
    default: balancing
  primary_mgt:
    description:
      - Identify the interface to be specified as management
    type: int
    required: true
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
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW.
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
l3fw_cluster:
  smc_logging:
    level: 10
    path: /Users/davidlepage/Downloads/ansible-smc.log
  name: newcluster
  cvi_mode: standby
  primary_mgt: 0
  interfaces:
    - interface_id: 0
      cluster_virtual: 1.1.1.1
      network_value: 1.1.1.0/24
      macaddress: 02:02:02:02:02:02
      nodes:
        - address: 1.1.1.2
          network_value: 1.1.1.0/24
          nodeid: 1
        - address: 1.1.1.3
          network_value: 1.1.1.0/24
          nodeid: 2
        - address: 1.1.1.4
          network_value: 1.1.1.0/24
          nodeid: 3
    - interface_id: 1
      cluster_virtual: 2.2.2.1
      network_value: 2.2.2.0/24
      macaddress: 02:02:02:02:02:04
      nodes:
        - address: 2.2.2.2
          network_value: 2.2.2.0/24
          nodeid: 1
        - address: 2.2.2.3
          network_value: 2.2.2.0/24
          nodeid: 2
        - address: 2.2.2.4
          network_value: 2.2.2.0/24
          nodeid: 3
    - interface_id: 2
      nodes:
        - address: 3.3.3.2
          network_value: 3.3.3.0/24
          nodeid: 1
        - address: 3.3.3.3
          network_value: 3.3.3.0/24
          nodeid: 2
        - address: 3.3.3.4
          network_value: 3.3.3.0/24
          nodeid: 3
      vlan_id: 3
    - interface_id: 2
      nodes:
        - address: 4.4.4.2
          network_value: 4.4.4.0/24
          nodeid: 1
        - address: 4.4.4.3
          network_value: 4.4.4.0/24
          nodeid: 2
        - address: 4.4.4.4
          network_value: 4.4.4.0/24
          nodeid: 3
      vlan_id: 4
    - interface_id: 3
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
    
    def empty(self):
        return not any(v for k, v in self.__dict__.items()
            if k is not 'interface_id')
    
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
    
    # Tuple is defined as: (was_changed, network)
    # If the interface is changed, store the original
    # network in the second tuple position only if it
    # is in a different network than the original so it
    # can be removed from the routing table.
    changes = False, False
    
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
            cvi_mode=dict(type='str', default='standby', choices=['standby', 'balancing']),
            interfaces=dict(type='list', default=[]),
            domain_server_address=dict(default=[], type='list'),
            log_server=dict(type='str'),
            default_nat=dict(default=False, type='bool'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_sidewinder_proxy=dict(default=False, type='bool'),
            enable_gti=dict(default=False, type='bool'),
            primary_mgt=dict(type='str', default='0'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cvi_mode=None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.log_server = None
        self.default_nat = None
        self.enable_antivirus = None
        self.enable_sidewinder_proxy = None #: TODO implement in check
        self.enable_gti = None
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
                                    'fields are: %s' % list(node_req))
                        
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
                        log_server_ref=self.log_server,
                        domain_server_address=self.domain_server_address,
                        default_nat=self.default_nat,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        interfaces=interfaces)
                    
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
                    
                    if self.check_mode:
                        return self.results
                    

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
                                itf = Interfaces(interfaces).get(interface_id)
                                
                                # Create a VLAN interface.
                                # Note: If the interface already exists with a VLAN
                                # specified and no addresses, you cannot convert this to
                                # a non-VLAN interface. You must delete it and recreate.
                                if itf.vlan_id:
                                    engine.physical_interface.add_ipaddress_and_vlan_to_cluster(
                                        **itf.as_dict())
                                    changed = True
                                    continue
                                # Create a cluster interface only if a Cluster Virtual Address,
                                # network_value and macaddress, or nodes (NDI's) are specified.
                                elif (itf.cluster_virtual and itf.network_value and itf.macaddress) or len(itf.nodes):
                                    engine.physical_interface.add_cluster_virtual_interface(**itf.as_dict())
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
                                if interface.change_cluster_interface(
                                    cluster_virtual=yaml.cluster_virtual,
                                    network_value=yaml.network_value,
                                    macaddress=yaml.macaddress,
                                    nodes=yaml.nodes, vlan_id=None):
                                    
                                    changed = True
                            
                            elif interface.has_vlan:
                                # Collection of VLANs. It is not possible to change the VLAN
                                # ID and the interface address. You must change one or the
                                # other as it's not possible to represent the previous then
                                # new cleanly in the YAML
                                
                                routes_to_remove = []
                                vlan_interfaces = interface.vlan_interface
                                
                                for sub in vlan_interfaces:
                                    yaml = ifs.get_vlan(sub.vlan_id)
                                    # If the YAML definition for the interface exists, either
                                    # create interface addresses or update existing, otherwise
                                    # delete the interface.
                                    if yaml is not None:
                                        if not sub.has_interfaces:
                                            updated = create_cluster_vlan_interface(interface, yaml)
                                            network = False
                                        else:
                                            updated, network = update_cluster_vlan_interface(sub, yaml)
                                    else:
                                        # YAML does not define an existing interface, so
                                        # delete the VLAN interface
                                        updated, network = delete_vlan_interface(sub)
                                    
                                    # If the interface was updated, check to see if we need
                                    # to remove stale routes and add the interface ID so we
                                    # can get the routing for that specific interface_id
                                    if updated:
                                        needs_update = True
                                        if network:
                                            routes_to_remove.append(
                                                sub.interface_id)
                                
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
                                    engine.physical_interface.add_cluster_virtual_interface(**itf.as_dict())
                                
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

        