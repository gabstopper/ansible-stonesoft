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
module: route_map
short_description: Create or delete Route Map and rule configurations
description:
  - Route Maps are used by the BGP configuration to allow refined BGP based
    policies for the NGFW. Route maps can be applied to announced networks
    on the engine BGP configuration or to BGPPeering elements. This module
    provides the ability to create a route map policy and route map rules.
    To view an existing route map, use route_map_facts.

version_added: '2.5'

options:
  name:
    description:
      - The name of the route map policy
    required: true
  comment:
    description:
      - Optional comment on the Route Map policy
    type: str
  rules:
    description:
      - A list of rules to optionally add to the route map policy
    type: list
    suboptions:
      action:
        description:
          - Action for the rule
        choices:
          - permit
          - deny
        type: str
        default: permit
      comment:
        description:
          - Optional comment for the rule
        type: str
      match_condition:
        description:
          - List of match conditions that will be the subject of this rule
        type: list
        suboptions:
          element:
            description:
              - The element parameter defines the SMC based element type to
                use for this element. An engine or external_bgp_peer can only
                be used with type peer_address
            choices:
              - ip_access_list
              - ip_prefix_list
              - ipv6_access_list
              - ipv6_prefix_list
              - as_path_access_list
              - community_access_list
              - extended_community_access_list
              - engine
              - external_bgp_peer
            type: str
            required: true
          name:
            description:
              - The name of the element based on type. This element is expected
                to exist.
            type: str
            required: true
          type:
            description:
              - The type of route map entry for this element. Route map entries
                define how the rule type is used in the policy. When defining a
                peer address, the element value must be engine or external_bgp_peer.
                When defining a next_hop, the element value must be of an ip_access_list
                or ip_prefix_list. A metric type will only have a value parameter with
                the metric value.
            choices:
              - access_list
              - peer_address
              - metric
              - next_hop
            type: str
            required: true
  delete_undefined_rules:
    description:
      - Delete rules from the route map policy that are not defined in the yaml
        configuration. A strategy to remove rules effectively would be to fetch
        the route map rules using route_map_facts, remove the unwanted rules and
        rerun the route_map task. The rule name is used as the primary key for
        identifying a rule to delete.
    type: bool
    default: false
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

EXAMPLES = '''
- name: Rule map configuration
  register: result
  route_map:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    comment: created by ansible
    name: routemap_for_aws
    rules:
    -   action: permit
        comment: some interesting comment
        match_condition:
        -   element: as_path_access_list
            name: aspath
            type: access_list
        -   element: community_access_list
            name: mycommunityacl
            type: access_list
        -   element: extended_community_access_list
            name: extended
            type: access_list
        -   element: ip_access_list
            name: myacl
            type: access_list
        -   element: ip_prefix_list
            name: myprefixlist
            type: access_list
        -   type: metric
            value: 20
        -   element: engine
            name: myfw
            type: peer_address
        -   element: ip_access_list
            name: myacl
            type: next_hop
        #-   element: external_bgp_peer
        #    name: mypeer
        #    type: peer_address
        name: myrule3
    #delete_undefined_rules: false

- name: Delete an existing route map policy
    register: result
    route_map:
      name: routemap_for_aws
      state: absent
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: Full json definition of route map policy
  returned: always
  type: dict
'''



import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, Cache


try:
    from smc.routing.route_map import RouteMap, MatchCondition
    from smc.api.exceptions import SMCException
except ImportError:
    pass


match_conditions = ('access_list', 'peer_address', 'metric', 'next_hop')
access_list = ('ip_access_list', 'ip_prefix_list', 'ipv6_access_list',
    'ipv6_prefix_list', 'as_path_access_list', 'community_access_list',
    'extended_community_access_list', 'engine', 'external_bgp_peer')


class StonesoftRouteMap(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            comment=dict(type='str'),
            rules=dict(type='list', default=[]),
            delete_undefined_rules=dict(type='bool', default=False),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
            
        self.name = None
        self.comment = None
        self.rules = None
        self.delete_undefined_rules = False
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftRouteMap, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        route_map = self.fetch_element(RouteMap)
        
        if state == 'present':
            cache = Cache()
            # Validate rule structure
            cache_ready = self.check_rules()
            cache.add_many(cache_ready)
            if cache.missing:
                self.fail(msg='Missing specified match condition elements',
                    results=cache.missing)   
            
            self.cache = cache
        
        try:
            
            if state == 'present':  
                if not route_map:
                    route_map = RouteMap.create(
                        self.name, comment=self.comment)

                rules = []
                for rule in self.rules:
                    
                    rule.pop('tag', None)
                    compiled_rule = dict(**rule)
                    
                    if 'match_condition' in rule:                
                        compiled_rule.update(match_condition=
                            self.serialize_match_condition(rule.get('match_condition', [])))
                    
                    rules.append(compiled_rule)
                
                if self.delete_undefined_rules:
                    names = [rule.get('name') for rule in rules]
                    for rule in route_map.route_map_rules:
                        if rule.name not in names:
                            rule.delete()
            
                for rule in rules:
                    route_map.route_map_rules.create(**rule)
                    changed = True
        
            elif state == 'absent':
                if route_map:
                    route_map.delete()
                    changed = True
    
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def check_rules(self):
        """
        Check the rules for validity, including any nested match 
        condition definitions. The return of this function will be
        a cache ready structure which can be quickly fed to
        add_many when names need to be resolved to href:
        
            [{typeof: [name1, name2], typeof: [name1, name2]]
        
        :rtype: list
        """
        conditions = ('element', 'name', 'type')
        metric = set(['type', 'value'])
        
        elements = {}
        for rule in self.rules:
            if not isinstance(rule, dict):
                self.fail(msg='Rule format is not type dict: %s, type: %s'
                    % (rule, type(rule)))
            if 'name' not in rule:
                self.fail(msg='Name is a required field for all rules')
            if 'match_condition' in rule:
                if not isinstance(rule['match_condition'], list):
                    self.fail(msg='Match condition is expected to be a list')

                for match in rule['match_condition']:
                    if match.get('type') == 'metric':
                        if set(match.keys()) ^ metric:
                            self.fail(msg='Metric definition can only have '
                                'values: %s, given: %s' % (list(metric), match))
                        continue
                    # Validate fields in condition
                    for field in conditions:
                        if field not in match:
                            self.fail(msg='Match condition is missing a required '
                                'key: %r ,required: %s' % (match, list(conditions)))
                        if field == 'element' and match.get(field) not in access_list:
                            self.fail(msg='Match condition element is not valid: %s, '
                                'valid types: %s' % (match.get(field), list(access_list)))
                        elif field == 'type' and match[field] not in match_conditions:
                            self.fail(msg='Match condition type is not valid: %s, '
                                'valid types: %s' % (match[field], list(match_conditions)))
                    
                    element = match.get('element')
                    # peer_address can only be type engine or external_bgp_peer
                    if match['type'] == 'peer_address' and element not \
                        in ('engine', 'external_bgp_peer'):
                        self.fail(msg='A peer address element can only be of type '
                            'engine or external_bgp_peer, provided definition: %s' % match)
                    elif match['type'] == 'next_hop' and ('prefix_list' not in \
                        element and 'access_list' not in element):
                        self.fail(msg='A next hop definition must be either an access '
                            'list or prefix list type, provided defintion: %s' % match)
                        
                    if 'engine' in element:
                        element = 'single_fw,fw_cluster,virtual_fw'
                    elements.setdefault(
                        element, set([])).add(match.get('name'))
        
        return [elements] if elements else []

    def serialize_match_condition(self, condition):
        """
        Return a MatchCondition element for the rule element
        
        :param dict condition: dict definition of condition
        :rtype: MatchCondition
        """
        mc = MatchCondition()
            
        for condition in condition:
            cond_type = condition.get('type')
            if cond_type == 'access_list':
                mc.add_access_list(
                    self.cache.get(condition.get('element'), condition.get('name')))
            if cond_type == 'peer_address':
                if condition['element'] == 'engine':
                    element = 'single_fw,fw_cluster,virtual_fw'
                else:
                    element = condition.get('element') 
                mc.add_peer_address(
                    self.cache.get(element, condition.get('name')))
            elif cond_type == 'next_hop':
                mc.add_next_hop(
                    self.cache.get(condition.get('element'), condition.get('name')))
            elif cond_type == 'metric':
                mc.add_metric(condition.get('value'))
        return mc
        
def main():
    StonesoftRouteMap()
    
if __name__ == '__main__':
    main()