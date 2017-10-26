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
module: l3fw_cluster_interface
short_description: Create or delete Stonesoft FW cluster interfaces
description:
  - Add or remove cluster CVI's, NDI's or CVI and NDI interfaces to a cluster
version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall cluster to modify
    required: true
  cluster_vip:
    description:
      - The cluster virtual (shared) IP address for all cluster members.
        Required when creating a CVI
    type: str
  cluster_vip_mask:
    description:
      - The cluster netmask for the cluster_vip. Required if I(cluster_vip)
    type: str
  cluster_macaddress:
    description:
      - The mac address to assign to the cluster virtual IP interface. Required if
        I(cluster_vip_mask) and I(cluster_vip)
    type: str
  cluster_nic_id:
    description:
      - The interface ID to use for the cluster vip
    required: true
  cluster_nodes:
    description:
        - Define the address, network and node id for each cluster member.
          Each cluster_node is a dictionary. Required if creating NDIs
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
  zone_ref:
    description:
      - A zone name for the FW management interface.
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

EXAMPLES = '''
- name: Add a cluster address with a CVI and NDIs to a 2 node cluster
  l3fw_cluster_interface:
    name: mycluster
    cluster_vip: 3.3.3.1
    cluster_vip_mask: 3.3.3.0/24
    cluster_macaddress: 02:02:02:02:02:04
    cluster_nic_id: 3
    cluster_nodes:
      - address: 3.3.3.2
        network_value: 3.3.3.0/24
        nodeid: 1
      - address: 3.3.3.3
        network_value: 3.3.3.0/24
        nodeid: 2

- name: Add only a CVI to a cluster
  l3fw_cluster_interface:
    name: mycluster
    cluster_vip: 4.4.4.1
    cluster_vip_mask: 4.4.4.0/24
    cluster_macaddress: 02:02:02:02:02:06
    cluster_nic_id: 4

- name: Add only NDI's to a cluster FW
  l3fw_cluster_interface:
    name: mycluster
    cluster_nic_id: 3
    cluster_nodes:
      - address: 3.3.3.2
        network_value: 3.3.3.0/24
        nodeid: 1
      - address: 3.3.3.3
        network_value: 3.3.3.0/24
        nodeid: 2  
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engines import FirewallCluster
    from smc.api.exceptions import SMCException
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class StonesoftClusterInterface(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_vip=dict(type='str'),
            cluster_vip_mask=dict(type='str'),
            cluster_macaddress=dict(type='str'),
            cluster_nic_id=dict(type='int', required=True),
            cluster_nodes=dict(type='list'),
            cluster_mode=dict(type='str', default='packetdispatch'),
            zone_ref=dict(type='str'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cluster_vip = None
        self.cluster_vip_mask = None
        self.cluster_macaddress = None
        self.cluster_nic_id = None
        self.cluster_nodes = None
        self.zone_ref = None
        
        required_together = [
            ['cluster_vip', 'cluster_vip_mask', 'cluster_macaddress']
        ]
        
        self.results = dict(
            changed=False
        )
        super(StonesoftClusterInterface, self).__init__(self.module_args,
                                                        required_together=required_together)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(FirewallCluster)
    
        try:
            if state == 'present':
                if engine:
                    engine = FirewallCluster(self.name)
                    engine.physical_interface.add_cluster_virtual_interface(
                        interface_id=self.cluster_nic_id,
                        cluster_virtual=self.cluster_vip,
                        cluster_mask=self.cluster_vip_mask,
                        macaddress=self.cluster_macaddress,
                        nodes=self.cluster_nodes,
                        cvi_mode=self.cluster_mode,
                        zone_ref=self.zone_ref)
                    self.fail(msg='Finish')
                    changed = True

            elif state == 'absent':
                if engine:
                    interface = engine.physical_interface.get(self.cluster_nic_id)
                    interface.delete()
                    changed = True
                
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['results'] = changed    
        return self.results


def main():
    StonesoftClusterInterface()

if __name__ == '__main__':
    main()