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
module: route_map_facts
short_description: Facts about Route Map policies in SMC
description:
  - Route Maps can be applied to dynamic routing configurations to provide
    granularity for filtering based on specific networks and parameters. This
    module provides the ability to view available route map configurations as
    well as dump a route map configuration into a dict or YAML for easy
    modification.

version_added: '2.5'
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Return all route map policies
    route_map_facts:

- name: Return 5 route map policies containing 'my' in the name
    route_map_facts:
      limit: 5
      filter: my

- name: Return detailed information on route map named myroutemap
    route_map_facts:
      filter: myroutemap
      exact_match: yes
      case_sensitive: yes
      
- name: Get route map details for myroutemap and save to yaml
    register: results
    route_map_facts:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      filter: newroutemap
      as_yaml: true

  - name: Write the yaml using a jinja template
    template: src=templates/facts_yaml.j2 dest=./foo.yml
    vars:
      playbook: route_map
'''


RETURN = '''
route_map:
  description: Return all route maps
  returned: always
  type: list
  sample: [
    {
        "name": "routemap_for_aws", 
        "type": "route_map"
    }, 
    {
        "name": "myroutemap", 
        "type": "route_map"
    }, 
    {
        "name": "newroutemap", 
        "type": "route_map"
    }, 
    {
        "name": "anewmap", 
        "type": "route_map"
    }]

route_map: 
  description: Return a specific route map by name
  returned: always
  type: list
  sample: [
    {
        "comment": "foo", 
        "name": "anewmap", 
        "rules": [
            {
                "action": "permit", 
                "comment": null, 
                "match_condition": [
                    {
                        "element": "external_bgp_peer", 
                        "name": "bgppeer", 
                        "type": "peer_address"
                    }, 
                    {
                        "element": "ip_access_list", 
                        "name": "myacl", 
                        "type": "access_list"
                    }, 
                    {
                        "type": "metric", 
                        "value": 20
                    }
                ], 
                "name": "Rule @141.0", 
                "tag": "141.0"
            }
        ]
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.routing.route_map import RouteMap
    from smc.core.engine import Engine
except ImportError:
    pass


def to_yaml(rm):
    routemap = dict(
        name=rm.name,
        comment=rm.comment)
    
    for rule in rm.route_map_rules:
        r = dict(name=rule.name,
                 tag=rule.tag,
                 action=rule.action,
                 comment=rule.comment)
        
        for condition in rule.match_condition:
            if condition.type == 'metric':
                r.setdefault('match_condition', []).append(
                    dict(type=condition.type,
                         value=condition.element.value))
            else:
                elem = 'engine' if isinstance(condition.element, Engine) \
                    else condition.element.typeof 
                r.setdefault('match_condition', []).append(
                    dict(name=condition.element.name,
                         element=elem,
                         type=condition.type))
        
        routemap.setdefault('rules', []).append(
            r)
    return routemap

    
class RouteMapFacts(StonesoftModuleBase):
    def __init__(self):
    
        self.element = 'route_map'
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                route_map=[]
            )
        )
        super(RouteMapFacts, self).__init__({}, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if self.as_yaml and not self.filter:
            self.fail(msg='You must provide a filter to use the as_yaml '
                'parameter')
        
        result = self.search_by_type(RouteMap)
        if self.filter:
            if self.as_yaml:
                route_maps = [to_yaml(rm) for rm in result
                              if rm.name == self.filter]
            else:
                route_maps = [to_yaml(rm) for rm in result]
        else:
            route_maps = [{'name': rm.name, 'type': rm.typeof} for rm in result]
        
        self.results['ansible_facts']['route_map'] = route_maps
        return self.results

def main():
    RouteMapFacts()
    
if __name__ == '__main__':
    main()