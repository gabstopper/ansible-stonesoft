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
    management = ('primary_mgt', 'backup_mgt', 'primary_heartbeat')
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
                        network_value=sub_interface.network_value)
                    if not 'type' in itf: # It's a physical interface
                        itf.update(macaddress=interface.macaddress)
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
                        
                        for role in management:
                            if getattr(sub_interface, role, None):
                                yaml_engine[role] = getattr(sub_interface, 'nicid')    
        
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

                            for role in management:
                                if getattr(sub_vlan, role, None):
                                    yaml_engine[role] = getattr(sub_vlan, 'nicid')
            
                        if vlan.zone_ref:
                            itf.update(zone_ref=zone_finder(
                                zone_cache, vlan.zone_ref))
                        
                        itf.setdefault('nodes', []).append(node)
                        
                    interfaces.append(itf)
                else:
                    # Empty VLAN, check for zone
                    if vlan.zone_ref:
                        itf.update(zone_ref=zone_finder(
                            zone_cache, vlan.zone_ref))
                    interfaces.append(itf)
        
        else: # Single interface, no addresses
            if getattr(interface, 'macaddress', None) is not None:
                itf.update(macaddress=interface.macaddress)
            if interface.zone_ref:
                itf.update(zone_ref=zone_finder(
                    zone_cache, interface.zone_ref))
            interfaces.append(itf)
    
    #sorted_id = sorted(interfaces, key=itemgetter('interface_id'))
    yaml_engine.update(
        interfaces=interfaces,
        default_nat=engine.default_nat.status,
        enable_antivirus=engine.antivirus.status,
        enable_file_reputation=engine.file_reputation.status,
        enable_sidewinder_proxy=engine.sidewinder_proxy.status,
        domain_server_address=[dns.value for dns in engine.dns
                               if dns.element is None])
    if engine.comment:
        yaml_engine.update(comment=engine.comment)

    # Only return the location if it is not the default (Not set) location
    location = engine.location
    if location:
        yaml_engine.update(location=location.name)

    # Show SNMP data if SNMP is enabled
    if engine.snmp.status:
        snmp = engine.snmp
        data = dict(snmp_agent=snmp.agent.name)
        if snmp.location:
            data.update(snmp_location=snmp.location)
        interfaces = snmp.interface
        if interfaces:
            data.update(snmp_interface=[itf.interface_id for itf in interfaces])
        yaml_engine.update(snmp=data)
    
    if getattr(engine, 'cluster_mode', None):
        yaml_engine.update(cluster_mode=engine.cluster_mode)
    
    # Lastly, get tags
    tags = [tag.name for tag in engine.categories]
    if tags:
        yaml_engine.update(tags=tags)
                
    return yaml_engine


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
                engines = [to_yaml(engine) for engine in result
                           if engine.name == self.filter]
                if engines:
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