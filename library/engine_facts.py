#!/usr/bin/python
#
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


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
  - smc-python >= 0.6.0
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
  
  - name: Find a cluster FW named mycluster
    engine_facts:
      element: fw_clusters
      filter: mycluster
  
  - name: Find only Layer 2 FW's
    engine_facts:
      element: layer2_clusters

  - name: Find only IPS engines
    engine_facts:
      element: ips_clusters
  
  - name: Get engine details for 'myfirewall'
    engine_facts:
      filter: myfirewall

  - name: Get engine details for 'myfw' and save in editable YAML format
    register: results
    engine_facts:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      filter: newcluster
      as_yaml: true

  - name: Write the yaml using a jinja template
    template: src=templates/engine_yaml.j2 dest=./l3fw_cluster.yml
'''


RETURN = '''
engines: 
    description: When filtering by element, only top level meta is returned
    returned: always
    type: list
    sample: [
        {
            "name": "newcluster2", 
            "type": "fw_cluster"
        }, 
        {
            "name": "myips", 
            "type": "single_ips"
        }, 
        {
            "name": "jackson", 
            "type": "fw_cluster"
        }, 
        {
            "name": "newcluster", 
            "type": "fw_cluster"
        }, 
        {
            "name": "myfw", 
            "type": "single_fw"
        }]

engines:
    description: When using a filter match, full engine json is returned
    returned: always
    type: list
    sample: [
        {
        "alias_value": [], 
        "allow_email_upn_lookup": false, 
        "antivirus": {
            "antivirus_enabled": false, 
            "antivirus_http_proxy_enabled": false, 
            "antivirus_proxy_password": "*****", 
            "antivirus_proxy_port": 0, 
            "antivirus_update": "never", 
            "antivirus_update_day": "mo", 
            "antivirus_update_time": 0, 
            "virus_log_level": "undefined"
        }, 
        "auto_reboot_timeout": 10,
        ...
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
            if getattr(interface, 'comment', None):
                itf.update(comment=interface.comment)
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
                if getattr(vlan, 'comment', None):
                    itf.update(comment=vlan.comment)
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
            if getattr(interface, 'comment', None):
                itf.update(comment=interface.comment)
            if interface.zone_ref:
                itf.update(zone_ref=zone_finder(
                    zone_cache, interface.zone_ref))
            interfaces.append(itf)
    
    yaml_engine.update(
        interfaces=interfaces,
        default_nat=engine.default_nat.status,
        antivirus=engine.antivirus.status,
        file_reputation=engine.file_reputation.status,
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
    
    # BGP Data
    bgp = engine.bgp
    data = dict(enabled=bgp.status,
                router_id=bgp.router_id)
    
    if bgp.status:    
        as_element = bgp.autonomous_system
        autonomous_system=dict(name=as_element.name,
                               as_number=as_element.as_number,
                               comment=as_element.comment)
        data.update(autonomous_system=autonomous_system)
        
        if bgp.profile:
            data.update(bgp_profile=bgp.profile.name)
        
        antispoofing_map = {}
        for net in bgp.antispoofing_networks:
            antispoofing_map.setdefault(net.typeof, []).append(
                net.name)
        antispoofing_network = antispoofing_map if antispoofing_map else {}
        data.update(antispoofing_network=antispoofing_network)
            
        announced_network = []
        for announced in bgp.advertisements:
            element, route_map = announced
            d = {element.typeof: {'name': element.name}}
            if route_map:
                d[element.typeof].update(route_map=route_map.name)
            announced_network.append(d)
        data.update(announced_network=announced_network)
        
    yaml_engine.update(bgp=data)
    bgp_peering = []
    for interface, network, peering in engine.routing.bgp_peerings:
        peer_data = {}
        peer_data.update(interface_id=interface.nicid,
                         name=peering.name)
        if network:
            peer_data.update(network=network.ip)
        for gateway in peering:
            if gateway.routing_node_element.typeof == 'external_bgp_peer':
                peer_data.update(external_bgp_peer=gateway.name)
            else:
                peer_data.update(engine=gateway.name)
        bgp_peering.append(peer_data)
    if bgp_peering:
        data.update(bgp_peering=bgp_peering)
    
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
                engines = [engine.data.data for engine in result]
        else:
            engines = [{'name': engine.name, 'type': engine.type} for engine in result]
        
        self.results['ansible_facts']['engines'] = engines
        return self.results

def main():
    EngineFacts()
    
if __name__ == '__main__':
    main()