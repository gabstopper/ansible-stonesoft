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
module: routing_facts
short_description: Facts about specific routes installed on an engine
description:
  - Show the current routing table for the given engine. This will show references
    to the dst_if for the route along with the gateway and route network. Use
    engine_facts to resolve interface ID's returned by this module.

version_added: '2.5'

options:
  element:
    description:
      - Specify the name of the engine in order to find the routing table
    required: true
      
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


RETURN = '''
routes: 
    description: Return all policy VPNs
    returned: always
    type: list
    sample: [{
        "dst_if": 1, 
        "route_gateway": "10.0.0.1", 
        "route_netmask": 0, 
        "route_network": "0.0.0.0", 
        "route_type": "Static", 
        "src_if": -1
        }, {
        "dst_if": 0, 
        "route_gateway": "172.18.1.240", 
        "route_netmask": 0, 
        "route_network": "0.0.0.0", 
        "route_type": "Static", 
        "src_if": -1
    }]
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engine import Engine
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def route_dict_from_obj(element):
    return dict(
        route_gateway=getattr(element, 'route_gateway', None),
        route_type=element.route_type,
        src_if=element.src_if,
        route_netmask=element.route_netmask,
        dst_if=element.dst_if,
        route_network=element.route_network)
    
    
class RoutingFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            element=dict(type='str', required=True)
        )
        
        self.element = None
        
        self.results = dict(
            ansible_facts=dict(
                routes=[]
            )
        )
        super(RoutingFacts, self).__init__(self.module_args)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        elements = []
        try:
            engine = Engine(self.element)
            elements = [route_dict_from_obj(element) for element in engine.routing_monitoring]
            
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['ansible_facts'] = {'routes': elements}
        return self.results

def main():
    RoutingFacts()
    
if __name__ == '__main__':
    main()
