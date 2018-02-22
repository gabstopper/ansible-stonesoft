#!/usr/bin/python
#
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: engine_facts
short_description: Facts about engines deployed in SMC
description:
  - Engines refers to any device that is deployed and managed by the Stonesoft
    Management Center. More specifically, an engine can be physical or virtual,
    an IPS, layer 2 firewall, layer 3 or clusters of these types.

version_added: '2.5'

options:
  element:
    description:
      - Type of engine to search for
    required: false
    default: engine_clusters
    choices:
      - engine_clusters
      - layer2_clusters
      - ips_clusters
      - fw_clusters
    type: str
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python >= 0.5.7
author:
  - David LePage (@gabstopper)
'''
        

EXAMPLES = '''
- name: Facts about all engines within SMC
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Find all managed engines (IPS, Layer 2, L3FW)
    engine_facts:
  
  - name: Find only Layer 3 FW's
    engine_facts:
      element: fw_clusters
  
  - name: Find only Layer 2 FW's
    engine_facts:
      element: layer2_clusters

  - name: Find only IPS engines
    engine_facts:
      element: ips_clusters
  
  - name: Get engine details for 'myfirewall'
    engine_facts:
      filter: myfirewall
'''


RETURN = '''
engines:
    description: List of engines from match query
    returned: always
    type: list
    sample: [{
        'antivirus': false,
        'cluster_mode': null,
        'default_nat': false,
        'engine_version': 'version 6.3 #19032',
        'gti': false,
        'interfaces': [{
            'interface_id': '2',
            'interfaces': [{
                'address': '10.29.248.49',
                'network_value': '10.29.248.49/30',
                'nodeid': 1,
                'type': 'single_node_interface',
                }],
            'name': 'Interface 2',
            'type': 'virtual_physical_interface',
            'vlans': [],
            }, {
            'interface_id': '0',
            'interfaces': [{
                'address': '10.29.248.53',
                'network_value': '10.29.248.53/30',
                'nodeid': 1,
                'type': 'single_node_interface',
                }],
            'name': 'Interface 0',
            'type': 'virtual_physical_interface',
            'vlans': [],
            }, {
            'interface_id': '1',
            'interfaces': [{
                'address': '10.29.248.57',
                'network_value': '10.29.248.57/30',
                'nodeid': 1,
                'type': 'single_node_interface',
                }],
            'name': 'Interface 1',
            'type': 'virtual_physical_interface',
            'vlans': [],
            }],
        'name': 've-5',
        'ospf': false,
        'sidewinder_proxy': false,
        'tags': ['footag']
}]
'''
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


ENGINE_TYPES = frozenset(['fw_clusters', 'engine_clusters', 'ips_clusters',
                          'layer2_clusters'])


try:
    from smc.elements.network import Zone
    from smc.core.sub_interfaces import ClusterVirtualInterface
except ImportError:
    pass


def zone_finder(zones, zone):
    for z in zones:
        if z.href == zone:
            return z.name


def yaml_firewall(engine):
        
    # Prefetch all zones to reduce queries
    zone_cache = list(Zone.objects.all())
    yaml_engine = {'name': engine.name}
    interfaces = []
    
    for interface in engine.interface:
        itf = {}
        itf.update(interface_id=interface.interface_id)
        if 'physical_interface' not in interface.typeof:
            itf.update(type=interface.typeof)
        if interface.has_interfaces:
            for sub_interface in interface.all_interfaces:
                node = {}
            
                if isinstance(sub_interface, ClusterVirtualInterface):
                    itf.update(
                        cluster_virtual=sub_interface.address,
                        macaddress=interface.macaddress,
                        network_value=sub_interface.network_value)
                    # Skip remaining to get nodes
                    continue
                else: # NDI
                    if sub_interface.dynamic:
                        node.update(dynamic=True)
                    else:
                        node.update(
                            address=sub_interface.address,
                            network_value=sub_interface.network_value,
                            nodeid=sub_interface.nodeid)
                        
                        if sub_interface.primary_mgt:
                            yaml_engine.update(primary_mgt='{}'.format(
                                interface.interface_id))
        
                if interface.zone_ref:
                    itf.update(zone_ref=
                        zone_finder(zone_cache, interface.zone_ref))
                
                itf.setdefault('nodes', []).append(node)

            interfaces.append(itf)
        
        elif interface.has_vlan:
            for vlan in interface.vlan_interface:
                itf = {}
                itf.update(interface_id=interface.interface_id,
                           vlan_id=vlan.vlan_id)
                if vlan.has_interfaces:
                    for sub_vlan in vlan.all_interfaces:
                        node = {}

                        if isinstance(sub_vlan, ClusterVirtualInterface):
                            itf.update(
                                cluster_virtual=sub_vlan.address,
                                macaddress=interface.macaddress,
                                network_value=sub_vlan.network_value)
                            continue
                        else: # NDI
                            node.update(
                                address=sub_vlan.address,
                                network_value=sub_vlan.network_value,
                                nodeid=sub_vlan.nodeid)

                            if sub_vlan.primary_mgt:
                                node.update(primary_mgt=True)
                                yaml_engine.update(primary_mgt='{}.{}'.format(
                                    interface.interface_id, sub_vlan.vlan_id))
            
                        if vlan.zone_ref:
                            itf.update(zone_ref=zone_finder(
                                zone_cache, vlan.zone_ref))
                        
                        itf.setdefault('nodes', []).append(node)
                        
                    interfaces.append(itf)
                else:
                    interfaces.append(itf)
        
        else: # Single interface, no addresses
            if getattr(interface, 'macaddress', None) is not None:
                itf.update(macaddress=interface.macaddress)
            interfaces.append(itf)

    yaml_engine.update(
        interfaces=interfaces,
        default_nat=engine.default_nat.status,
        enable_antivirus=engine.antivirus.status,
        enable_gti=engine.file_reputation.status,
        enable_sidewinder_proxy=engine.sidewinder_proxy.status,
        domain_server_address=[dns.value for dns in engine.dns
                               if dns.element is None])
    return yaml_engine

''' 
def yaml_firewall(engine):
        
    # Reduce number of zone query lookup cache
    zone_cache = list(Zone.objects.all())
    yaml_engine = {'name': engine.name}
    interfaces = []
    
    for interface in engine.interface:
        itf = {}
        itf.update(interface_id=interface.interface_id)
        if 'physical_interface' not in interface.typeof:
            itf.update(type=interface.typeof)
        if interface.has_interfaces:
            for sub_interface in interface.all_interfaces:
                if isinstance(sub_interface, ClusterVirtualInterface):
                    itf.update(
                        cluster_virtual=sub_interface.address,
                        macaddress=interface.macaddress,
                        address=sub_interface.address,
                        network_value=sub_interface.network_value)
                else: # NDI
                    if sub_interface.dynamic:
                        itf.update(dynamic=True)
                    else:
                        ndi = {'address': sub_interface.address,
                               'network_value': sub_interface.network_value,
                               'nodeid': sub_interface.nodeid}
                        if sub_interface.primary_mgt:
                            ndi.update(primary_mgt=True)
                        itf.setdefault('nodes', []).append(ndi)
        
                if interface.zone_ref:
                    itf.update(zone_ref=zone_finder(
                        zone_cache, interface.zone_ref))
            
            interfaces.append(itf)
        
        elif interface.has_vlan:
            vlan_interfaces = []
            for vlan in interface.vlan_interface:
                vlan_def = {}
                if vlan.has_interfaces:
                    for sub_vlan in vlan.all_interfaces:
                        vlan_def.update(vlan_id=sub_vlan.vlan_id)
                        if isinstance(sub_vlan, ClusterVirtualInterface):
                            itf.update(
                                cluster_virtual=sub_vlan.address,
                                macaddress=interface.macaddress,
                                address=sub_vlan.address,
                                network_value=sub_vlan.network_value)
                        else: # NDI
                            ndi = {'address': sub_vlan.address,
                                   'network_value': sub_vlan.network_value,
                                   'nodeid': sub_vlan.nodeid}
                            if sub_vlan.primary_mgt:
                                ndi.update(primary_mgt=True)
                            vlan_def.setdefault('nodes', []).append(ndi)
                    
                        if vlan.zone_ref:
                            vlan_def.update(zone_ref=zone_finder(
                                zone_cache, vlan.zone_ref))
                
                else:
                    vlan_def.update({'vlan_id': vlan.vlan_id})
                
                vlan_interfaces.append(vlan_def)
                itf.update(vlan_interfaces=vlan_interfaces)
        
            interfaces.append(itf)
        
        else: # Single interface, no addresses
            if getattr(interface, 'macaddress', None) is not None:
                itf.update(macaddress=interface.macaddress)
            interfaces.append(itf)

    yaml_engine.update(
        interfaces=interfaces,
        default_nat=engine.default_nat.status,
        enable_antivirus=engine.antivirus.status,
        enable_gti=engine.file_reputation.status,
        enable_sidewinder_proxy=engine.sidewinder_proxy.status,
        domain_server_address=[dns.value for dns in engine.dns
                               if dns.element is None])
    return yaml_engine
'''    
    

def to_yaml(engine):
    if 'single_fw' in engine.type or 'cluster' in engine.type:
        return yaml_firewall(engine)
    else:
        raise ValueError('Only single FW and cluster FW types are '
            'currently supported.')

     
class EngineFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(default='engine_clusters', type='str', choices=list(ENGINE_TYPES))
        )
    
        self.element = None
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                engines=[]
            )
        )
        super(EngineFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if self.as_yaml and not self.filter:
            self.fail(msg='You must provide a filter to use the as_yaml '
                'parameter')
        
        result = self.search_by_context()
        if self.filter:
            if self.as_yaml:
                for engine in result:
                    engines = [to_yaml(engine)]
                    self.results['engine_type'] = engine.type
            else:
                engines = [engine.data for engine in result]
        else:
            engines = [{'name': engine.name, 'type': engine.type} for engine in result]
        
        self.results['ansible_facts']['engines'] = engines
        return self.results

def main():
    EngineFacts()
    
if __name__ == '__main__':
    main()