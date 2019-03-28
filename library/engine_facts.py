#!/usr/bin/python
#
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from smc.core.interfaces import SwitchPhysicalInterface


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
        path: ansible-smc.log
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
        "antivirus": true,
        "antispoofing_network": {
            "network": [
                "network-1.1.1.0/24"
            ]
        },
        "bgp": {
            "announced_network": [
                {
                    "network": {
                        "name": "network-1.1.1.0/24", 
                        "route_map": "myroutemap"
                    }
                }
            ], 
            "autonomous_system": {
                "as_number": 200, 
                "comment": null, 
                "name": "as-200"
            }, 
            "bgp_peering": [
                {
                    "interface_id": "1000", 
                    "name": "bgppeering"
                }
            ], 
            "bgp_profile": "Default BGP Profile", 
            "enabled": true, 
            "router_id": "1.1.1.1"
        }, 
        "default_nat": true, 
        "domain_server_address": [
            "8.8.8.8"
        ], 
        "file_reputation": true, 
        "interfaces": [
            {
                "interface_id": "0", 
                "interfaces": [
                    {
                        "nodes": [
                            {
                                "address": "1.1.1.1", 
                                "network_value": "1.1.1.0/24", 
                                "nodeid": 1
                            }
                        ]
                    }
                ]
            }, 
            {
                "interface_id": "1000", 
                "interfaces": [
                    {
                        "nodes": [
                            {
                                "address": "10.10.10.1", 
                                "network_value": "10.10.10.1/32", 
                                "nodeid": 1
                            }
                        ]
                    }
                ], 
                "type": "tunnel_interface"
            }, 
            {
                "interface_id": "1", 
                "interfaces": [
                    {
                        "nodes": [
                            {
                                "address": "2.2.2.1", 
                                "network_value": "2.2.2.0/24", 
                                "nodeid": 1
                            }
                        ]
                    }
                ]
            }
        ], 
        "name": "myfw3", 
        "policy_vpn": [
            {
                "central_node": true, 
                "mobile_gateway": false, 
                "name": "ttesst", 
                "satellite_node": false
            }
        ], 
        "primary_mgt": "0", 
        "snmp": {
            "snmp_agent": "fooagent", 
            "snmp_interface": [
                "1"
            ], 
            "snmp_location": "test"
        }, 
        "type": "single_fw"
    }]
'''
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


ENGINE_TYPES = frozenset(['fw_clusters', 'engine_clusters', 'ips_clusters',
                          'layer2_clusters'])


try:
    from smc.elements.network import Zone
    from smc.vpn.policy import PolicyVPN
    from smc.core.sub_interfaces import ClusterVirtualInterface
    from smc.api.exceptions import UnsupportedEngineFeature
    from smc.core.interfaces import Layer3PhysicalInterface, TunnelInterface, \
        ClusterPhysicalInterface
except ImportError:
    pass


def zone_finder(zones, zone):
    for z in zones:
        if z.href == zone:
            return z.name


def yaml_cluster(engine):
    """
    Example interface dict created from cluster engine:
        
        {'cluster_virtual': u'2.2.2.1',
         'interface_id': u'1',
         'macaddress': u'02:02:02:02:02:03',
         'network_value': u'2.2.2.0/24',
         'nodes': [{'address': u'2.2.2.2',
                    'network_value': u'2.2.2.0/24',
                    'nodeid': 1,
                    'primary_mgt': True},
                   {'address': u'2.2.2.3',
                    'network_value': u'2.2.2.0/24',
                    'nodeid': 2,
                    'primary_mgt': True}]}
    
    Nodes dict key will always have at least `address`,
    `network_value` and `nodeid` if the interface definition
    has interface addresses assigned.
    """
    # Prefetch all zones to reduce queries
    zone_cache = list(Zone.objects.all())
    management = ('primary_mgt', 'backup_mgt', 'primary_heartbeat', 'backup_heartbeat')
    yaml_engine = {'name': engine.name, 'type': engine.type}
    interfaces = []
    
    for interface in engine.interface:
        if not isinstance(interface,
            (ClusterPhysicalInterface, Layer3PhysicalInterface, TunnelInterface,
                SwitchPhysicalInterface)):
            continue
        top_itf = {}
        
        # Interface common settings
        top_itf.update(interface_id=interface.interface_id)
        
        if getattr(interface, 'macaddress', None) is not None:
            top_itf.update(macaddress=interface.macaddress)
        if getattr(interface, 'comment', None):
            top_itf.update(comment=interface.comment)
        if interface.zone_ref:
            top_itf.update(zone_ref=zone_finder(
                zone_cache, interface.zone_ref))
        
        cvi_mode = getattr(interface, 'cvi_mode', None)
        if cvi_mode is not None and cvi_mode != 'none':
            top_itf.update(cvi_mode=interface.cvi_mode)
            
        if 'physical_interface' not in interface.typeof:
            top_itf.update(type=interface.typeof)
        
        if 'switch_physical_interface' in interface.typeof:
            top_itf.update(type='switch_physical_interface',
                appliance_switch_module=getattr(interface.appliance_switch_module, 'conf_value', None))
            
            for port_group in interface.port_group_interface:
                _port_group = {'switch_physical_interface_port': port_group.data.get(
                    'switch_physical_interface_port'),'interface_id': port_group.interface_id}
                if port_group.zone_ref:
                    _port_group.update(zone_ref=zone_finder(
                        zone_cache, port_group.zone_ref))
                                          
                if port_group.has_interfaces: # Port group has an assigned IP
                    _interfaces = []    
                    nodes = {}
                     
                    for sub_intf in port_group.all_interfaces:
                        node = {}
                        if getattr(sub_intf, 'dynamic', None):
                            node.update(dynamic=True, dynamic_index=
                               getattr(sub_intf, 'dynamic_index', 0))
                        else:
                            node.update(
                               address=sub_intf.address,
                               network_value=sub_intf.network_value,
                               nodeid=sub_intf.nodeid)
                        
                        for role in management:
                            if getattr(sub_intf, role, None):
                                yaml_engine[role] = getattr(sub_intf, 'nicid')
                            
                        nodes.setdefault('nodes', []).append(node)
                     
                    if nodes:
                        _interfaces.append(nodes)
                    if _interfaces:
                        _port_group.update(interfaces=_interfaces)
                 
                top_itf.setdefault('port_group_interface', []).append(_port_group)
             
            interfaces.append(top_itf)
            continue
         
        if interface.has_interfaces:
            _interfaces = []    
            nodes = {}
            for sub_interface in interface.all_interfaces:
                node = {}
                if isinstance(sub_interface, ClusterVirtualInterface):
                    nodes.update(
                        cluster_virtual=sub_interface.address,
                        network_value=sub_interface.network_value)

                    # Skip remaining to get nodes
                    continue
                else: # NDI
                    # Dynamic address
                    if getattr(sub_interface, 'dynamic', None):
                        node.update(dynamic=True, dynamic_index=
                            getattr(sub_interface, 'dynamic_index', 0))
                    else:
                        node.update(
                            address=sub_interface.address,
                            network_value=sub_interface.network_value,
                            nodeid=sub_interface.nodeid)
                     
                    for role in management:
                        if getattr(sub_interface, role, None):
                            yaml_engine[role] = getattr(sub_interface, 'nicid')    

#                         for role in management:
#                             if getattr(sub_interface, role, None):
#                                 yaml_engine[role] = getattr(sub_interface, 'nicid')    

                nodes.setdefault('nodes', []).append(node)
            
            if nodes:
                _interfaces.append(nodes)
            if _interfaces:
                top_itf.update(interfaces=_interfaces)
        
        elif interface.has_vlan:

            for vlan in interface.vlan_interface:
                
                itf = {'vlan_id': vlan.vlan_id}
                if getattr(vlan, 'comment', None):
                    itf.update(comment=vlan.comment)

                _interfaces = []    
                nodes = {}
                if vlan.has_interfaces:
                    for sub_vlan in vlan.all_interfaces:
                        node = {}

                        if isinstance(sub_vlan, ClusterVirtualInterface):
                            itf.update(
                                cluster_virtual=sub_vlan.address,
                                network_value=sub_vlan.network_value)
                            continue
                        else: # NDI
                            # Dynamic address
                            if getattr(sub_vlan, 'dynamic', None):
                                node.update(dynamic=True, dynamic_index=
                                    getattr(sub_vlan, 'dynamic_index', 0))
                            else:
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
                        
                        nodes.setdefault('nodes', []).append(node)
                        
                    if nodes:
                        _interfaces.append(nodes)
                    if _interfaces:
                        itf.update(nodes)
                    
                    top_itf.setdefault('interfaces', []).append(itf)
            
                else:
                    # Empty VLAN, check for zone
                    if vlan.zone_ref:
                        itf.update(zone_ref=zone_finder(
                            zone_cache, vlan.zone_ref))
                    
                    top_itf.setdefault('interfaces', []).append(itf)    
                    
        interfaces.append(top_itf)
        
    yaml_engine.update(
        interfaces=interfaces,
        default_nat=engine.default_nat.status,
        antivirus=engine.antivirus.status,
        file_reputation=engine.file_reputation.status)
    
    for vpn_endpoint in engine.vpn_endpoint:
        if vpn_endpoint.enabled:
            yaml_engine.setdefault('enable_vpn', []).append(
                vpn_endpoint.name)
    
    if engine.dns:
        yaml_engine.update(
            domain_server_address=get_engine_dns(engine))
    
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
    yaml_engine.update(bgp=get_bgp(engine))
    
    # OSPF Data
    yaml_engine.update(ospf=get_ospf(engine))
    
    # Antispoofing, only if dynamic routing is enabled
    antispoofing = get_antispoofing(engine)
    if antispoofing:
        yaml_engine.update(antispoofing_network=antispoofing)
    
    # Netlinks
    netlinks = []
    for netlink in engine.routing.netlinks:
        interface, _network, link = netlink
        netlink = {'interface_id': interface.nicid,
                   'name': link.name}
            
        for gw in link:
            gateway = gw.routing_node_element
            netlink.setdefault('destination', []).append(
                {'name': gateway.name, 'type': gateway.typeof})
        
        netlinks.append(netlink)
    if netlinks:
        yaml_engine.update(netlinks=netlinks)
    
    # Policy VPN
    policy_vpn = get_policy_vpn(engine)
    if policy_vpn:
        yaml_engine.update(policy_vpn=policy_vpn)
     
    # Lastly, get tags
    tags = [tag.name for tag in engine.categories]
    if tags:
        yaml_engine.update(tags=tags)
    return yaml_engine
                    

def get_engine_dns(engine):
    """
    Engine DNS entries
    
    :rtype: list
    """
    entries = []
    for val in engine.dns:
        if val.value:
            entries.append({'name': val.value, 'type': 'ipaddress'})
        else:
            ne_ref = val.element
            entries.append({'name': ne_ref.name, 'type': ne_ref.typeof})
    return entries


def get_antispoofing(engine):
    """
    Get antispoofing networks for configuration where BGP or
    OSPF are enabled
    
    :rtype: dict
    """
    dyn_routing = engine.dynamic_routing
    antispoofing_map = {}
    if dyn_routing.bgp.status or dyn_routing.ospf.status: 
        for net in dyn_routing.antispoofing_networks:
            antispoofing_map.setdefault(net.typeof, []).append(
                net.name)
    return antispoofing_map
    
    
def get_bgp(engine):
    """
    Get BGP settings for the engine if any
    
    :return: dict of BGP settings
    """
    bgp = engine.dynamic_routing.bgp
    data = dict(enabled=bgp.status,
                router_id=bgp.router_id)
    
    if bgp.status:    
        as_element = bgp.autonomous_system
        autonomous_system=dict(name=as_element.name,
                               as_number=as_element.as_number,
                               comment=as_element.comment)
        data.update(autonomous_system=autonomous_system)
        
        bgp_profile = bgp.profile
        if bgp_profile:
            data.update(bgp_profile=bgp_profile.name)
            
        announced_network = []
        for announced in bgp.announced_networks:
            element, route_map = announced
            d = {element.typeof: {'name': element.name}}
            if route_map:
                d[element.typeof].update(route_map=route_map.name)
            announced_network.append(d)
        data.update(announced_network=announced_network)
        
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
    return data
    
    
def get_ospf(engine):
    """
    Get OSPF settings for the engine
    
    :return: dict of entries only if OSPF is enabled
    """
    ospf = engine.dynamic_routing.ospf
    data = dict(
        enabled=ospf.status,
        router_id=ospf.router_id)
    if ospf.status:
        data.update(ospf_profile=ospf.profile.name)

    ospf_areas = []
    for interface, network, peering in engine.routing.ospf_areas:
        area_data = {}
        area_data.update(interface_id=interface.nicid,
                         name=peering.name)
        if network:
            area_data.update(network=network.ip)
        ospf_areas.append(area_data)
    if ospf_areas:
        data.update(ospf_areas=ospf_areas)
    return data
    

def get_policy_vpn(engine):
    """
    Policy VPN settings for the engine. This should be modified to leverage
    SMC 6.3.4 optimizations under engine.vpn_mappings.
    
    :return: dict of policy VPN settings
    """
    try:
        vpn_mappings = engine.vpn_mappings
    except UnsupportedEngineFeature:
        return
    engine_internal_gw = engine.vpn.internal_gateway.name
    policy_vpn = []
    _seen = []
    if vpn_mappings:
        for mapping in vpn_mappings:
            mapped_vpn = mapping.vpn
            if mapped_vpn.name not in _seen:
                _vpn = {'name': mapped_vpn.name}
                vpn = PolicyVPN(mapped_vpn.name)
                vpn.open()
                nodes = vpn.central_gateway_node
                node_central = nodes.get_contains(engine_internal_gw)
                _vpn.update(central_gateway=True if node_central else False)
                if not node_central: # If it's a central node it can't be a satellite node
                    nodes = vpn.satellite_gateway_node
                    _vpn.update(satellite_gateway=True if nodes.get_contains(engine_internal_gw) else False)
                else:
                    _vpn.update(satellite_node=False)
                if vpn.mobile_vpn_topology != 'None':
                    mobile_node = vpn.mobile_gateway_node
                    _vpn.update(mobile_gateway=True if mobile_node.get_contains(engine_internal_gw) else False)
                
                policy_vpn.append(_vpn)
                vpn.close()
                _seen.append(mapped_vpn.name)
    return policy_vpn

    
def to_yaml(engine):
    if 'single_fw' in engine.type or 'cluster' in engine.type:
        #return yaml_firewall(engine)
        return yaml_cluster(engine)
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
        
        required_if=([
            ('as_yaml', True, ['filter'])])
        
        self.results = dict(
            ansible_facts=dict(
                engines=[]
            )
        )
        super(EngineFacts, self).__init__(self.module_args, required_if=required_if,
                                          is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_context()
        engines = []
        if self.filter:
            if self.as_yaml:
                engines = [to_yaml(engine) for engine in result
                           if engine.name == self.filter]
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