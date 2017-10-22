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
  cluster_vip:
    description:
      - The cluster virtual (shared) IP address for all cluster members.
        Required if I(state=present).
    type: str
  cluster_vip_mask:
    description:
      - The cluster netmask for the cluster_vip. Required if I(state=present)
    type: str
  cluster_macaddress:
    description:
      - The mac address to assign to the cluster virtual IP interface. This is
        required if I(state=present)
    type: str
  cluster_nic_id:
    description:
      - The interface ID to use for the cluster vip
    default: 0
  cluster_mode:
    description:
      - How to perform clustering, either balancing or standby
    choices: ['balancing', 'standby']
    default: balancing
  cluster_nodes:
    description:
        - Define the address, network and node id for each cluster member.
          Each cluster_node is a dictionary. Required if I(state=present)
    suboptions:
      address:
        description:
          - The IP address for this cluster node member
        type: str
        required: true
      network_value:
        description:
          - The netmask for this cluster node address
        type: str
        required: true
      nodeid:
        description:
          - The node ID for the cluster node
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
# Create a new cluster
- name: creating and deleting layer 3 firewalls
  gather_facts: no
  tasks:
  - name: layer 3 cluster with 3 members
    l3fw_cluster:
      name: mycluster
      cluster_vip: 1.1.1.1
      cluster_vip_mask: 1.1.1.0/24
      cluster_macaddress: 02:02:02:02:02:02
      cluster_nic_id: 0
      cluster_mode: standby
      cluster_nodes:
        - address: 1.1.1.2
          network_value: 1.1.1.0/24
          nodeid: 1
        - address: 1.1.1.3
          network_value: 1.1.1.0/24
          nodeid: 2
        - address: 1.1.1.4
          network_value: 1.1.1.0/24
          nodeid: 3
      default_nat: yes
      domain_server_address:
          - 10.0.0.1
          - 10.0.0.2
      enable_antivirus: yes
      enable_gti: yes

# Delete a cluster
- name: Deleting layer 3 firewalls
  gather_facts: no
  tasks:
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
msg:
  description: Simple description message
  returned: always
  type: string
  sample: Successfully created engine
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engines import FirewallCluster
    from smc.api.exceptions import SMCException
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class StonesoftCluster(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_vip=dict(type='str'),
            cluster_vip_mask=dict(type='str'),
            cluster_macaddress=dict(type='str'),
            cluster_nic_id=dict(default=0, type='int'),
            cluster_nodes=dict(type='list'),
            cluster_mode=dict(type='str', default='balancing'),
            domain_server_address=dict(default=[], type='list'),
            zone_ref=dict(type='str'),
            default_nat=dict(default=False, type='bool'),
            enable_antivirus=dict(default=False, type='bool'),
            enable_gti=dict(default=False, type='bool'),
            tags=dict(type='list'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.tags = None
        self.name = None
        self.cluster_vip = None
        self.cluster_vip_mask = None
        self.cluster_macaddress = None
        self.cluster_nic_id = None
        self.cluster_nodes = None
        self.cluster_mode = None
        self.log_server = None
        self.domain_server_address = None
        self.zone_ref = None
        self.default_nat = False
        self.enable_antivirus = False
        self.enable_gti = False
        
        required_if=([
            ('state', 'present', ['name', 'cluster_vip', 'cluster_vip_mask',
                                  'cluster_macaddress', 'cluster_nic_id',
                                  'cluster_nodes'])
        ])
        
        self.results = dict(
            changed=False,
            msg=''
        )
        super(StonesoftCluster, self).__init__(self.module_args, required_if=required_if)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if state == 'present':
            if not self.cluster_nodes:
                self.fail_json(msg='You must specify cluster nodes to create a cluster')   
    
            try:
                engine = FirewallCluster.create(
                    name=self.name,
                    cluster_virtual=self.cluster_vip,
                    cluster_mask=self.cluster_vip_mask,
                    macaddress=self.cluster_macaddress,
                    cluster_nic=self.cluster_nic_id,
                    nodes=self.cluster_nodes,
                    cluster_mode=self.cluster_mode,
                    log_server_ref=self.log_server,
                    domain_server_address=self.domain_server_address,
                    zone_ref=self.zone_ref,
                    default_nat=self.default_nat,
                    enable_antivirus=self.enable_antivirus,
                    enable_gti=self.enable_gti)
                
                if self.tags:
                    engine.add_category(self.tags)

            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successfully created engine', changed=True)
            
        elif state == 'absent':
            try:
                FirewallCluster(self.name).delete()
            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
            else:
                self.results.update(msg='Successfully deleted engine', changed=True)

        return self.results


def main():
    StonesoftCluster()
    
if __name__ == '__main__':
    main()

        