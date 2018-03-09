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
- name: Return all categories
    route_map:

- name: Return all route map and references containing 'my' in the name
    route_map:
      limit: 5
      filter: my

- name: Return detailed information on route map named myroutemap
    category_facts:
      limit: 1
      filter: myroutemap
      exact_match: yes
      case_sensitive: yes
'''


RETURN = '''
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
                elem = 'engine_clusters' if isinstance(condition.element, Engine) \
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