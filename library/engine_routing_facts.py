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
module: engine_routing_facts
short_description: Facts about specific routes installed on an engine
description:
  - Show the current routing table for the given engine. This will show references
    to the dst_if for the route along with the gateway and route network. Use
    engine_facts to resolve interface ID's returned by this module.

version_added: '2.5'

options:
  filter:
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
    description: Return all engine routes
    returned: always
    type: list
    sample: [{
        "dst_if": 1, 
        "route_gateway": "10.0.0.1", 
        "route_netmask": 0, 
        "route_network": "0.0.0.0", 
        "route_type": "Static", 
        "src_if": -1
        }, 
        {
        "dst_if": 0, 
        "route_gateway": "172.18.1.240", 
        "route_netmask": 0, 
        "route_network": "0.0.0.0", 
        "route_type": "Static", 
        "src_if": -1
        },
        {
        "dst_if": 1, 
        "route_gateway": null, 
        "route_netmask": 24, 
        "route_network": "10.0.0.0", 
        "route_type": "Connected", 
        "src_if": -1
        }
    ]
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.api.exceptions import SMCException
except ImportError:
    pass
    
    
class EngineRoutingFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            filter=dict(type='str', required=True)
        )
        
        self.element = 'engine_clusters'
        self.filter = None
        
        self.results = dict(
            ansible_facts=dict(
                engines=[]
            )
        )
        super(EngineRoutingFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        engine = self.search_by_context()
        if not engine:
            self.fail(msg='Specified engine does not exist: %s' % self.filter)
        
        try:
            self.results['ansible_facts']['engines'] = [rt._asdict()
                for rt in engine[0].routing_monitoring]
            
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        return self.results

def main():
    EngineRoutingFacts()
    
if __name__ == '__main__':
    main()
