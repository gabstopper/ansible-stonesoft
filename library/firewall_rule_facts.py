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
module: firewall_rule_facts
short_description: Facts about firewall rules based on specified policy
description:
  - Retrieve rule specific information based on the policy specified in the
    facts module run. Specifying the policy is a required field. In addition,
    you can choose to expand fields like source, destination and services from
    href to their native element type and name by using the expand list with
    specified fields to expand. There are other search capabilities such as
    finding a rule based on partial match and rules within specific ranges.

version_added: '2.5'

options:
  filter:
    description:
      - The name of the FW Policy for which to retrieve rules
    required: true
  search:
    description:
      - Provide a search string for which to use as a match against a rule/s
        name or comments field. Mutually exclusive with I(rule_range)
    type: str
  rule_range:
    description:
      - Provide a rule range to retrieve. Firewall rules will be displayed based
        on the ranges provided in a top down fashion.
    type: str
  expand:
    description:
      - Specifying fields which should be expanded from href into their
        native elements. Expanded fields will be returned as a dict of lists
        with the key being the element type and list being the name values for
        that element type
    choices:
      - source
      - destination
      - services
    type: list
  as_yaml:
    description:
      - Set this boolean to true if the output should be exported into yaml format. By
        default the output format is actually dict, but using this field allows you to
        also use the provided jinja templates to format into yaml and reuse for playbook
        runs.
    type: bool
  
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
  - name: Show rules for policy 'TestPolicy' (only shows name, type)
    firewall_rule_facts:
      filter: TestPolicy

  - name: Search for specific rule/s using search value (partial searching supported)
    firewall_rule_facts:
      filter: TestPolicy
      search: rulet

  - name: Dump the results in yaml format, showing details of rule
    firewall_rule_facts:
      filter: TestPolicy
      search: rulet
      as_yaml: true

  - name: Resolve the source, destination and services fields
    firewall_rule_facts:
      filter: TestPolicy
      search: rulet
      as_yaml: true
      expand:
      - sources
      - destinations
      - services

  - name: Get specific rules based on range order (rules 1-10)
    firewall_rule_facts:
      filter: TestPolicy
      rule_range: 1-3
      as_yaml: true
  
  - name: Get firewall rule as yaml
    register: results
    firewall_rule_facts:
      smc_logging:
       level: 10
       path: ansible-smc.log
      filter: TestPolicy
      search: rulet
      #rule_range: 1-3
      as_yaml: true
      expand:
      - services
      - destinations
      - sources
  
  - name: Write the yaml using a jinja template
    template: src=templates/facts_yaml.j2 dest=./firewall_rules_test.yml
    vars:
      playbook: firewall_rule
'''


RETURN = '''
firewall_rule: 
    description: Obtain metadata through a simple rule search
    returned: always
    type: list
    sample: [
    {
        "comment": null, 
        "policy": "TestPolicy", 
        "rules": [
            {
                "name": "Rule @2097166.2", 
                "pos": 1, 
                "type": "fw_ipv4_access_rule"
            }, 
            {
                "name": "ruletest", 
                "pos": 2, 
                "type": "fw_ipv4_access_rule"
            }, 
            {
                "name": "Rule @2097168.0", 
                "pos": 3, 
                "type": "fw_ipv4_access_rule"
            }, 
            {
                "name": "nested", 
                "pos": 4, 
                "type": "fw_ipv4_access_rule"
            }
        ],
    }]
'''
import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.api.exceptions import SMCException
    from smc.policy.layer3 import FirewallPolicy
except ImportError:
    pass


engine_type = ('single_fw', 'single_layer2', 'single_ips', 'virtual_fw',
    'fw_cluster', 'master_engine')


def to_yaml(rule, expand=None):
    _rule = {
        'name': rule.name, 'tag': rule.tag,
        'is_disabled': rule.is_disabled,
        'comment': rule.comment}
        
    if rule.is_rule_section:
        return _rule 
    
    for field in ('sources', 'destinations', 'services'):
        if getattr(rule, field).is_any:
            _rule[field] = {'any': True}
        elif getattr(rule, field).is_none:
            _rule[field] = {'none': True}
        else:
            if expand and field in expand:
                tmp = {}
                for entry in getattr(rule, field).all():
                    element_type = entry.typeof
                    if entry.typeof in engine_type:
                        element_type = 'engine'
                    elif 'alias' in entry.typeof:
                        element_type = 'alias'
                    tmp.setdefault(element_type, []).append(
                        entry.name)
            else:
                tmp = getattr(rule, field).all_as_href()
            _rule[field] = tmp

    inspection_options = {
        'decrypting': rule.action.decrypting,
        'deep_inspection': rule.action.deep_inspection,
        'file_filtering': rule.action.file_filtering}

    _rule.update(inspection_options=inspection_options)
    _rule.update(log_options=rule.data.get('options'),
                 action=rule.action.action)
    
    auth_options = {
        'require_auth': rule.authentication_options.require_auth,
        'methods': [m.name for m in rule.authentication_options.methods]}
    for user in rule.authentication_options.users:
        if 'user_group' in user.typeof:
            auth_options.setdefault('groups', []).append(user.unique_id)
        else:
            auth_options.setdefault('users', []).append(user.unique_id)
    
    _rule.update(authentication_options=auth_options)
    
    if rule.action.action in ('enforce_vpn', 'forward_vpn', 'apply_vpn'):
        if rule.action.vpn:
            _rule.update(vpn_policy=rule.action.vpn.name)
        else:
            _rule.update(mobile_vpn=rule.action.mobile_vpn)
    elif rule.action.action == 'jump':
        _rule.update(sub_policy=rule.action.sub_policy.name)
    _rule.update(connection_tracking=rule.action.connection_tracking_options.data)
    return _rule


expands = ('sources', 'destinations', 'services')

        
class FirewallRuleFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            filter=dict(type='str', required=True),
            expand=dict(type='list', default=[]),
            search=dict(type='str'),
            rule_range=dict(type='str')
        )
    
        self.expand = None
        self.search = None
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.exact_match = None
        self.case_sensitive = None
        
        mutually_exclusive = [
            ['search', 'rule_range'],
        ]
        
        self.results = dict(
            ansible_facts=dict(
                firewall_rule=[]
            )
        )
        super(FirewallRuleFacts, self).__init__(self.module_args, is_fact=True,
            mutually_exclusive=mutually_exclusive)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        for attr in self.expand:
            if attr not in expands:
                self.fail(msg='Invalid expandable attribute: %s provided. Valid '
                    'options are: %s'  % (attr, expands))
        
        rules = []
        try:
            policy = self.search_by_type(FirewallPolicy)
            if not policy:
                self.fail(msg='Policy specified could not be found: %s' % self.filter)
            elif len(policy) > 1:
                self.fail(msg='Multiple policies found with the given search filter: %s '
                    'Use exact_match or case_sensitive to narrow the search' % 
                    [p.name for p in policy])
    
            policy = policy.pop()
            
            if self.search:
                result = policy.search_rule(self.search)
            elif self.rule_range:
                try:
                    start, end = map(int, self.rule_range.split('-'))
                    result= [x for x in policy.fw_ipv4_access_rules][start-1:end]
                except ValueError:
                    raise SMCException('Value of rule range was invalid. Rule ranges '
                        'must be a string with numeric only values, got: %s' %
                        self.rule_range)
            else:
                result = policy.fw_ipv4_access_rules
            
            if self.as_yaml:
                rules = [to_yaml(rule, self.expand) for rule in result
                         if rule.typeof == 'fw_ipv4_access_rule']
            else:
                # No order for since rules could be sliced or searched
                if self.search or self.rule_range:
                    rules = [{'name': rule.name, 'type': rule.typeof} for rule in result]
                else:
                    rules = [{'name': rule.name, 'type': rule.typeof, 'pos': num}
                              for num, rule in enumerate(result, 1)]
        
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        firewall_rule = {
            'policy': policy.name,
            'rules': rules}
    
        self.results['ansible_facts']['firewall_rule'].append(firewall_rule)
        return self.results
        
        
def main():
    FirewallRuleFacts()
    
if __name__ == '__main__':
    main()