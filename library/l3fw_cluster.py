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
    default: balancing
  mgmt_interface:
    description:
      - Identify the interface to be specified as management
    type: int
  interfaces:
    description:
        - Define the interface settings for this cluster interface, such as 
          address, network and node id.
    suboptions:
      cluster_nic:
        description:
          - The cluster nic ID for this interface. Required.
        type: int
      cluster_virtual:
        description:
          - The cluster virtual (shared) IP address for all cluster members. Not
            required if only creating NDI's
        type: str
      cluster_mask:
        description:
          - The cluster netmask for the cluster_vip. Required if I(cluster_virtual)
        type: str
      cluster_macaddress:
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
  zone_ref:
    description:
      - A zone name for the FW management interface.
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
- name: Create a layer 3 FW cluster with 3 members
  l3fw_cluster:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    name: mycluster
    cluster_mode: standby
    mgmt_interface: 0
    interfaces:
      - cluster_nic: 0
        cluster_virtual: 1.1.1.1
        cluster_mask: 1.1.1.0/24
        macaddress: 02:02:02:02:02:02
        zone_ref: management
        nodes:
          - address: 1.1.1.2
            network_value: 1.1.1.0/24
            nodeid: 1
          - address: 1.1.1.3
            network_value: 1.1.1.0/24
            nodeid: 2
      - cluster_nic: 1
        cluster_virtual: 2.2.2.1
        cluster_mask: 2.2.2.0/24
        macaddress: 02:02:02:02:02:03
        nodes:
          - address: 2.2.2.2
            network_value: 2.2.2.0/24
            nodeid: 1
          - address: 2.2.2.3
            network_value: 2.2.2.0/24
            nodeid: 2
      - cluster_nic: 2
        nodes:
          - address: 3.3.3.1
            network_value: 3.3.3.0/24
            nodeid: 1
          - address: 3.3.3.2
            network_value: 3.3.3.0/24
            nodeid: 2
    default_nat: yes
    domain_server_address:
      - 10.0.0.1
      - 10.0.0.3
    enable_antivirus: yes
    enable_gti: yes
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
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engines import FirewallCluster
    from smc.api.exceptions import SMCException, InterfaceNotFound
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class StonesoftCluster(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_mode=dict(type='str', default='standby'),
            mgmt_interface=dict(type='int', default=0),
            interfaces=dict(type='list'),
            domain_server_address=dict(default=[], type='list'),
            log_server=dict(type='str'),
            default_nat=dict(default=False, type='bool'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_gti=dict(default=False, type='bool'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cluster_mode=None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.log_server = None
        self.default_nat = None
        self.enable_antivirus = None
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
                            'configuration to create a cluster')
                    
                    req = ('cluster_nic', 'nodes')
                    node_req = ('address', 'network_value', 'nodeid')
                    mgmt_index = None
                    for num, value in enumerate(self.interfaces):
                        if not all(k in value for k in req):
                            self.fail(msg='Missing interface field. Required fields '
                                'are: %s' % list(req))
                            
                        # Validate nodes
                        for node in value.get('nodes'):
                            if not all(k in node for k in node_req):
                                self.fail(msg='Node missing required field. Required '
                                    'fields are: %s' % list(node_req))
                        
                        # Management interface
                        if value.get('cluster_nic') == self.mgmt_interface:
                            mgt = ('cluster_virtual', 'cluster_mask', 'macaddress')
                            if not all(k in value for k in mgt):
                                self.fail(msg='Management interface requires the following '
                                    'fields: %s' % list(mgt))
                            mgmt_index = num
                    
                    if mgmt_index is None:
                        self.fail(msg='Management interface is not defined. Management was '
                            'specified on interface: %s' % self.mgmt_interface)
                    
                    if self.check_mode:
                        return self.results
                    
                    management = self.interfaces.pop(mgmt_index)
                    management.update(
                        name=self.name,
                        cluster_mode=self.cluster_mode,
                        log_server=self.log_server,
                        domain_server_address=self.domain_server_address,
                        default_nat=self.default_nat,
                        enable_antivirus=self.enable_antivirus,
                        enable_gti=self.enable_gti,
                        interfaces=self.interfaces)
                    
                    engine = FirewallCluster.create(**management)
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
                    
                    # Check management interface setting
                    mgt_intf = engine.interface_options.primary_mgt
                    if mgt_intf.interface_id != str(self.mgmt_interface):
                        engine.interface_options.set_primary_mgt(str(self.mgmt_interface))
                        changed = True
                    
                    # Check and change cluster mode
                    if self.cluster_mode != engine.cluster_mode and \
                        self.cluster_mode in ('standby', 'balancing'):
                        engine.data.update(cluster_mode=self.cluster_mode)
                        changed = True 
                    
                    # Verify interfaces. Validate that we have the settings that
                    # we need along the way. If the intent is to add a CVI to an
                    # interface that already exists but has NDIs only, you should
                    # first delete the interface and recreate.
                    
                    # Track defined so we can delete undefined
                    defined = []
                    for interface in self.interfaces:
                        cluster_nic = str(interface.pop('cluster_nic'))
                        try:
                            intf = engine.interface.get(cluster_nic)
                            needs_update = False
                            for sub in intf.interfaces:
                                #if not needs_update:
                                if sub.nodeid is None:
                                    if sub.address != interface.get('cluster_virtual'):
                                        needs_update = True
                                        break
                                else: # NDI
                                    for node in interface.get('nodes'):
                                        if node.get('nodeid') == sub.nodeid:
                                            if sub.address != node.get('address'):
                                                needs_update = True
                                                break
                            
                            if needs_update:
                                intf.change_cluster_ipaddress(
                                    cvi=interface.get('cluster_virtual'),
                                    cvi_network_value=interface.get('cluster_mask'),
                                    nodes=interface.get('nodes'))
                                changed = True

                        except InterfaceNotFound:
                            # Create the missing interface
                            interface.update(interface_id=cluster_nic)
                            engine.physical_interface.add_cluster_virtual_interface(
                                **interface)
                            changed = True
                    
                        defined.append(cluster_nic)
                    
                    for interface in engine.interface:
                        if interface.interface_id not in defined:
                            interface.delete()
                            # Don't set local changed as delete will update
                            # the engine already. Set this on the result so
                            # it's reported property
                            self.results['changed'] = True
                    
                    if self.tags:
                        if self.add_tags(engine, self.tags):
                            changed = True
                    else:
                        if self.clear_tags(engine):
                            changed = True
                           
                    if changed:
                        engine.update()
                        
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

        