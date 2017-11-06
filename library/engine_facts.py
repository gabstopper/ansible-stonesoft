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
- name: Find an engine named exactly 've-1' and display details
  engine_facts:
    filter: ve-1
    exact_match: yes

- name: Find firewall disabling case sensitivity (exact_match=no)
  engine_facts:
    filter: MyFirewall
    case_sensitive: no

- name: Find firewalls starting with 've', limit to 5 results
  engine_facts:
    filter: ve
    limit: 5
    case_sensitive: no

- name: Retrieve all layer 2 firewalls only
  engine_facts:
    element: ips_clusters
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


try:
    from smc.api.exceptions import UnsupportedEngineFeature
    from smc.core.interfaces import InterfaceModifier
except ImportError:
    pass


ENGINE_TYPES = frozenset(['fw_clusters', 'engine_clusters', 'ips_clusters',
                          'layer2_clusters'])


def interface_spec():
    return dict(
        interface_id=None,
        name=None,
        type=None,
        interfaces=[],
        vlans=[]
    )

   
def address_spec():
    return dict(
        address=None,
        network_value=None,
        type=None,
        nodeid=None
    )


def interface_map(engine):
    """
    Return an interface dict for specified engine.
    
    :param engine: :class:`smc.core.engine.Engine`
    :rtype: dict
    """
    nodes = InterfaceModifier.byEngine(engine)
    interfaces = []
    for node in nodes:
        spec = interface_spec()
        spec.update(interface_id=node.interface_id,
                    name=node.name,
                    type=node.typeof)
        
        # IF a node has a VLAN, there should not be interfaces, with the
        # exception that an inline interface still stores a single ref
        if node.has_vlan:
            vlan_interfaces = node.vlan_interfaces()
            # A VLAN is a type of PhysicalInterface
            for vlan in vlan_interfaces:
                sub_interfaces = vlan.sub_interfaces()
                
                # VLANs can't have VLANs
                for sub_if in sub_interfaces:
                    address = address_spec()
                    address.update(
                        address=getattr(sub_if, 'address', None),
                        network_value=getattr(sub_if, 'network_value', None),
                        type=sub_if.typeof,
                        nodeid=getattr(sub_if, 'nodeid', None),
                        vlan_id=getattr(sub_if, 'vlan_id', None))
                    
                spec['vlans'].append(address)
        
        elif node.has_interfaces:
            sub_interfaces = node.sub_interfaces()
            for sub_if in sub_interfaces:
                address = address_spec()
                address.update(
                    address=getattr(sub_if, 'address', None),
                    network_value=getattr(sub_if, 'network_value', None),
                    type=sub_if.typeof,
                    nodeid=getattr(sub_if, 'nodeid', None))
                spec['interfaces'].append(address)

        interfaces.append(spec)
    return interfaces


def _unsupported_exc(engine, prop):
    # Some features can not be enabled based on the
    # engine type.
    try:
        return getattr(engine, prop)
    except UnsupportedEngineFeature:
        return False


def engine_dict_from_obj(engine):
    engine_dict = dict(
        name=engine.name,
        type=engine.type,
        engine_version=engine.data.get('engine_version'),
        cluster_mode=engine.data.get('cluster_mode'),
        interfaces=interface_map(engine),
        antivirus=_unsupported_exc(engine, 'is_antivirus_enabled'),
        gti=_unsupported_exc(engine, 'is_gti_enabled'),
        sidewinder_proxy=_unsupported_exc(engine, 'is_sidewinder_proxy_enabled'),
        default_nat=_unsupported_exc(engine, 'is_default_nat_enabled'),
        tags=[]
    )
    for tag in engine.categories:
        engine_dict['tags'].append(tag.name)
    
    try:
        engine_dict['pending_changes'] = engine.pending_changes.has_changes
    except UnsupportedEngineFeature:
        engine_dict['pending_changes'] = False
    
    if _unsupported_exc(engine, 'ospf'):
        ospf = engine.ospf
        if ospf.is_enabled:
            ospf_dict = dict(
                enabled=True,
                profile=ospf.profile.name,
                router_id=ospf.router_id)
            engine_dict['ospf'] = ospf_dict
        else:
            engine_dict['ospf'] = {'enabled': False} 
    
    if _unsupported_exc(engine, 'bgp'):
        bgp = engine.bgp
        if bgp.is_enabled:
            as_element = bgp.autonomous_system
            bgp_dict = dict(
                enabled=True,
                router_id=getattr(bgp, 'router_id'),
                autonomous_system=as_element.name,
                as_number=as_element.as_number,
                profile=bgp.profile.name,
                advertisements=[])
        
            advertisements = getattr(bgp, 'advertisements', None)
            if advertisements:
                for ads in advertisements:
                    net, routemap = ads
                    bgp_dict['advertisements'].append({
                        net.typeof: net.name, 'route_map': routemap.name if routemap else None})
            engine_dict['bgp'] = bgp_dict
        else:
            engine_dict['bgp'] = {'enabled': False}

    return engine_dict

              
class EngineFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(default='engine_clusters', type='str', choices=list(ENGINE_TYPES))
        )
    
        self.element = None
        self.limit = None
        self.filter = None
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
        
        result = self.search_by_context()
        if self.filter:
            engines = [engine_dict_from_obj(engine) for engine in result]
        else:
            engines = [{'name': engine.name, 'type': engine.type} for engine in result]
        
        self.results['ansible_facts'] = {'engines': engines}
        return self.results

def main():
    EngineFacts()
    
if __name__ == '__main__':
    main()