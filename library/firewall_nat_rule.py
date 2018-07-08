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
module: firewall_nat_rule
short_description: Create, modify or delete a firewall NAT rule
description:
  - Firewall NAT rules can be added or removed from either a top level policy
    or a sub-policy. Source, destination and service elements can be used and
    referenced by their type and name (they must be pre-created).
    This module requires SMC >= 6.4.3 or above to support changes to NAT rules

version_added: '2.5'

options:
  policy:
    description:
      - The policy which to operate on. Any rule modifications are done in the
        context of this policy
    required: true
    type: str
  sub_policy:
    description:
      - The sub policy which to operate on. This is mutually exclusive with the
        I(policy) parameter. You can operate on rules within a firewall policy or
        firewall sub policy.
    type: str
  rules:
    description:
      - Source elements to add to the rule. Elements need to specify the type of
        element to add. If source is not provided, the rule source cell will be
        set to none and the rule will effectively be disabled.
    type: list
    suboptions:
      comment:
        description:
          - Optional comment for this rule
        type: str
      name:
        description:
          - Name for this rule. Required if adding a new rule. Not required for
            modifications
        type: str
        required: true
      tag:
        description:
          - Tag retrieved from facts module. The tag identifies the rule uniquely and
            is a required field when making modifications. If tag is present, the operation
            becomes a modify. Otherwise it becomes a create and I(name) is required.
        type: str
      is_disabled:
        description:
          - Is this rule disabled. Set to true to disable rule, false otherwise.
        default: false
      sources:
        description:
          - Sources for use in this rule. You can use a shortcut for 'any' or 'none'
            in this field, by providing a simple dict with keys 'any' or 'none' and value
            of true. Otherwise this should be a dict with keys using valid element types
            and value should be a list of those element types by name. The choices represent
            valid keys for the dict. If no sources field is provided, 'any' is used
        type: dict
        choices:
         - domain_name
         - expression
         - group
         - host
         - ip_list
         - network
         - engine
         - router
         - netlink
         - interface_zone
      destinations:
        description:
          - Destinations for use in this rule. You can use a shortcut for 'any' or 'none'
            in this field, by providing a simple dict with keys 'any' or 'none' and value
            of true. Otherwise this should be a dict with keys using valid element types
            and value should be a list of those element types by name. The choices represent
            valid keys for the dict, If no destinations field is provided, 'any' is used
        type: dict
        choices:
         - domain_name
         - expression
         - group
         - host
         - ip_list
         - network
         - engine
         - router
         - netlink
         - interface_zone
      services:
        description:
          - Services for this rule. You can use a shortcut for 'any' or 'none'
            in this field, by providing a simple dict with keys 'any' or 'none' and value
            of true. Otherwise this should be a dict with keys using valid element types
            and value should be a list of those element types by name. The choices represent
            valid keys for the dict. If no services field is provided, 'any' is used
        type: dict
        choices:
        - service_group
        - tcp_service_group
        - udp_service_group
        - ip_service_group
        - icmp_service_group
        - tcp_service
        - udp_service
        - ip_service
        - ethernet_service
        - icmp_service
        - application_situation
        - url_category
      static_src_nat:
        description:
          - Static source NAT rule. A static source NAT rule uses the value of the
            rule source field and requires either an IP or element as the translated
            address. This is mutually exclusive with dynamic_src_nat.
      dynamic_src_nat:
        description:
          - Dynamic source NAT rule. A dynamic source NAT rule uses the value of the
            rule source field and requires either an IP or element as the translated
            address. You can also define ports to use for PAT. This NAT type is typically
            used for outbound NAT and PAT operations.
      static_dst_nat:
        description:
          - Static dest NAT rule. Typically used for inbound traffic. This rule uses the
            rule destination field and requires either an IP or element as the translated
            address. You can also specify source ports as single values or ranges to
            translate. This is useful if you want inbound traffic on port 80 and need to
            redirect to an internal host on 8080 for example
      add_after:
        description:
          - Provide a rule tag ID for which to add the rule after. This is only relevant for
            rules that are being created.
        type: str
      add_before:
        description:
          - Provide a rule tag ID for which to add the rule before. This is only relevant for
            rules that are being created.
        type: str
  state:
    description:
      - Create or delete a firewall cluster
    required: false
    default: present
    choices:
      - present
      - absent
    
'''


EXAMPLES = '''
- name: Firewall NAT rule examples
  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: added a comment
      destinations:
        any: true
      dynamic_src_nat:
        automatic_proxy: true
        translated_value:
          ip_descriptor: 1.1.1.1
          max_port: 60000
          min_port: 1024
      is_disabled: false
      name: dynamic source nat with ports and IP redirect
      services:
        any: true
      sources:
        any: true
    - comment: null
      destinations:
        any: true
      dynamic_src_nat:
        automatic_proxy: true
        translated_value:
          max_port: 65535
          min_port: 1024
          name: host-4.4.4.4
          type: host
      is_disabled: false
      name: dynamic source nat with element
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
    - comment: testcomment
      destinations:
        host:
        - host-3.3.3.3
      is_disabled: false
      name: static_dest_nat with IP redirect
      services:
        any: true
      sources:
        any: true
      static_dst_nat:
        automatic_proxy: true
        original_value:
          max_port: 90
          min_port: 90
        translated_value:
          ip_descriptor: 1.1.1.1
          max_port: 9999
          min_port: 9999
      used_on: ANY
    - comment: null
      destinations:
        any: true
      is_disabled: false
      name: static_src_nat with IP address
      services:
        any: true
      sources:
        host:
        - host-4.4.4.4
      static_src_nat:
        automatic_proxy: true
        translated_value:
          ip_descriptor: 1.1.1.1
      used_on: ANY
    - comment: null
      destinations:
        any: true
      dynamic_src_nat:
        automatic_proxy: true
        translated_value:
          max_port: 65535
          min_port: 1024
          name: host-4.4.4.4
          type: host
      is_disabled: false
      name: dynamic_source_nat with element
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
      used_on: ANY
'''


RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: The current state of the element
  return: always
  type: dict
'''

import traceback
from ansible.module_utils.six import string_types
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache)


try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.policy.layer3 import FirewallSubPolicy
    from smc.api.exceptions import SMCException
except ImportError:
    pass


rule_targets = ('address_range', 'country', 'domain_name', 'expression', 'group', 'host',
    'ip_list', 'network', 'engine', 'router', 'netlink', 'interface_zone', 'alias')

service_targets = ('service_group', 'tcp_service_group', 'udp_service_group', 'ip_service_group',
    'icmp_service_group', 'tcp_service', 'udp_service', 'ip_service', 'ethernet_service', 'icmp_service')

nat_type = ('dynamic_src_nat', 'static_src_nat', 'static_dst_nat')


def compare_rules(rule, rule_dict):
    """
    Compare two rules.
    
    :param IPv4Rule rule: rule fetched from policy
    :param dict rule_dict: rule dict from yaml, matching the create
        constructor args
    """
    changes = []
    if rule.is_disabled != rule_dict.get('is_disabled'):
        if rule_dict.get('is_disabled'):
            rule.disable()
        else:
            rule.enable()
        changes.append('is_disabled')
    
    if 'comment' in rule_dict and rule.comment != rule_dict['comment']:
        rule.comment = rule_dict['comment']
        changes.append('comment')
    
    # Rule sections do not have sources/dest/service fields
    if rule.is_rule_section: 
        return changes
    
    if rule.name != rule_dict.get('name'):
        rule.data.update(name=rule_dict.get('name'))
        changes.append('name')
        
    for field in ('sources', 'destinations', 'services'):
        # Quick comparison that should only match if field is any or None
        field_value = rule_dict.get(field)
        if not field_value and not getattr(rule, field).is_none:
            getattr(rule, field).set_none()
            changes.append(field)
        elif isinstance(field_value, string_types) and not getattr(rule, field).is_any:
            getattr(rule, field).set_any()
            changes.append(field)
        else: #List of entries
            if getattr(rule, field).update_field(field_value):
                changes.append(field)
    
    # NAT is modified if the YAML defines NAT and the rule being
    # compared does not have NAT defined. The second case is when
    # the YAML doesn't have NAT defined and the existing rule does,
    # in which case the NAT is removed.
    for nat in nat_type:
        if nat in rule_dict:
            start_port, end_port = rule_dict.get('%s_ports' % nat, (None, None))
            if getattr(rule, nat).update_field(
                rule_dict.get(nat), start_port, end_port):
                changes.append(nat)
        elif getattr(rule, nat).has_nat and nat not in rule_dict:
            getattr(rule, nat).set_none()
            changes.append(nat)
    
    return changes


def is_port_range(port):
    """
    If ports are specified and as a port range, then validate
    whether the ranges are the same length. This is only used
    when creating destination NAT rules.
    """
    if isinstance(port, str) and '-' in port:
        start_port, end_port = map(int, port.split('-'))
        return len(range(start_port, end_port))
             
 
def is_a_valid_port(min_port, max_port):
    """
    A valid port for NAT must be a positive integer between
    1-65535. In addition, dynamic destination NAT can be a
    port range in which case the port range for min and max
    ports must be equal in length.
     
    :return: whether ports are valid
    :rtype: bool
    """
    min_port_range, max_port_range = None, None
    try:
        min_port_range = is_port_range(min_port)
        max_port_range = is_port_range(max_port)
        
        if min_port_range is not None and max_port_range is not None:
            if min_port_range != max_port_range:
                return False
        else:
            for port in map(int, (min_port, max_port)):
                if port <= 0 or port > 65535:
                    return False
    except ValueError:
        return False
    return True


def get_tag(tag):
    """
    Get the rule tag. Used by the search function that needs
    the revision number stripped from the tag id.
    
    :return: string representation of tag
    :rtype: str
    """
    if tag:
        try:
            tag, _version = tag.split('.')
            return tag
        except ValueError:
            pass
    

class FirewallNATRule(StonesoftModuleBase):
    def __init__(self):
        self.module_args = dict(
            policy=dict(type='str'),
            sub_policy=dict(type='str'),
            rules=dict(type='list', default=[]),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.policy = None
        self.sub_policy = None
        self.rules = None
        
        mutually_exclusive = [
            ['policy', 'sub_policy'],
        ]
         
        required_one_of = [
            [ 'policy', 'sub_policy' ]
        ]
        
        self.results = dict(
            changed=False,
            state=[]
        )
        
        super(FirewallNATRule, self).__init__(self.module_args,
            mutually_exclusive=mutually_exclusive, required_one_of=required_one_of,
            supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:            
            # Now that we have valid option settings, we can hit the db
            if self.policy:
                policy = FirewallPolicy.get(self.policy)
            else:
                policy = FirewallSubPolicy.get(self.sub_policy)
            
            if state == 'present':
                
                self.cache = Cache()
                
                for rule in self.rules:
                    if 'tag' not in rule and 'name' not in rule:
                        self.fail(msg='A rule must have either a rule tag or a '
                            'name field: %s' % rule)
    
                    if 'used_on' in rule:
                        used_on = rule['used_on']
                        if not isinstance(used_on, string_types):
                            self.fail(msg='Used on field should be the name of an '
                                'engine or the value "ANY". Received: %s' % used_on)
                    
                    if all(ntype in rule for ntype in ('static_src_nat', 'dynamic_src_nat')):
                        self.fail(msg='You must specify either static or dynamic source '
                            'NAT, not both: %s' % rule)
                                
                    # Resolve elements if they exist, calls to SMC could happen here
                    if self.field_resolver(rule.get('sources', {'none': True}), rule_targets):
                        if 'static_src_nat' in rule:
                            self.fail(msg='You must specify a source value when configuring '
                                'static_src_nat. ANY and None are not valid: %s' % rule)
                    
                    if self.field_resolver(rule.get('destinations', {'none': True}), rule_targets):    
                        if 'static_dst_nat' in rule:
                            self.fail(msg='You must specify a destination value when configuring '
                                'static_dst_nat. ANY and None are not valid: %s' % rule)
                    
                    if 'services' in rule:
                        self.field_resolver(rule.get('services'), service_targets)
                    
                    # Evaluate the NAT definitions first as they might have embedded
                    # element references.
                    for nat in nat_type:
                        if nat not in rule:
                            continue
                        
                        if not isinstance(rule[nat], dict):
                            self.fail(msg='NAT definition must be type dict. Rule was: %s' % rule)
                        
                        nat_value_dict = rule.get(nat)
                        translated_value = nat_value_dict.get('translated_value')
                        if not translated_value or not isinstance(translated_value, dict):
                            self.fail(msg='NAT translated value must exist and be in dict '
                                'format. Rule was: %s' % rule)
                        
                        if all(port in translated_value for port in ('min_port', 'max_port')):
                            min_port = translated_value.get('min_port')
                            max_port = translated_value.get('max_port')
                            
                            # Port ranges are not valid for dynamic source NAT
                            if any('-' in port for port in map(str, (min_port, max_port))) and \
                                'dynamic_src_nat' in rule:
                                self.fail(msg='Dynamic source NAT port definitions must be in '
                                    'single port (str or int) format. Ranges are not valid: %s' % rule)
                                
                            if not is_a_valid_port(min_port, max_port):    
                                self.fail(msg='Ports specified for nat type: %r are not valid. '
                                    'Ports for dynamic_src_nat must be between 1-65535 and port '
                                    'ranges used for static_dst_nat must be of equal lengths. '
                                    'Min port: %s, max_port: %s' % (nat, min_port, max_port))
                    
                        if all(k in translated_value for k in ('name', 'type')):
                            # Add elements to cache if defined
                            self.cache._add_entry(
                                translated_value.get('type'),
                                translated_value.get('name'))
                                           
                if self.cache.missing:
                    self.fail(msg='Missing required elements that are referenced in this '
                        'configuration: %s' % self.cache.missing)
                
                if self.check_mode:
                    return self.results
                
                # If we've gotten here, cache is populated and we're not missing anything
                for rule in self.rules:
                    rule_dict = {}            
                    
                    rule_dict.update(
                        comment=rule.get('comment'),
                        is_disabled=rule.get('is_disabled', False),
                        name=rule.get('name'))
                    
                    for field in ('sources', 'destinations', 'services'):
                        rule_dict[field] = self.get_values(rule.get(field, None))
                    
                    for nat in nat_type:
                        if nat in rule:
                            rule_dict.update(self.nat_definition(nat, rule.get(nat)))
                                
                    if 'tag' not in rule:    
                        rule = policy.fw_ipv4_nat_rules.create(**rule_dict)
                        changed = True
                        self.results['state'].append({
                            'rule': rule.name,
                            'type': rule.typeof,
                            'action': 'created'})
                    else:
                        target_rule = self.rule_by_tag(policy, rule.get('tag'))
                        if not target_rule:
                            continue
                        
                        changes = compare_rules(target_rule, rule_dict)
                        if rule.get('add_after', None):
                            rule_at_pos = self.rule_by_tag(policy, rule.get('add_after'))
                            if rule_at_pos:
                                target_rule.move_rule_after(rule_at_pos)
                                changes.append('add_after')
                        elif rule.get('add_before', None):
                            rule_at_pos = self.rule_by_tag(policy, rule.get('add_before'))
                            if rule_at_pos:
                                target_rule.move_rule_before(rule_at_pos)
                                changes.append('add_before')
                        elif changes:
                            target_rule.save()
                        
                        if changes:
                            changed = True
                            self.results['state'].append({
                                'rule': target_rule.name,
                                'type': target_rule.typeof,
                                'action': 'modified',
                                'changes': changes})
            
            elif state == 'absent':
                for rule in self.rules:
                    if 'tag' in rule:
                        target_rule = self.rule_by_tag(policy, rule.get('tag'))
                        if target_rule:
                            target_rule.delete()
                            changed = True
                            self.results['state'].append({
                                'rule': target_rule.name,
                                'type': target_rule.typeof,
                                'action': 'deleted'})
                    
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def rule_by_tag(self, policy, tag):
        """
        Get the rule referenced by it's tag. Tag will be in format
        '1234566.0'. When doing a search_rule, you must omit the part
        after the dot(.) to find the rule.
        
        :param FirewallPolicy policy: policy reference
        :param str tag: tag
        :rtype: Rule or None
        """
        resolved_tag = get_tag(tag)
        if resolved_tag:
            rule = policy.search_rule('@{}'.format(resolved_tag))
            return rule[0] if rule else None
        
    def field_resolver(self, elements, types):

        """
        Field resolver, specific to retrieving network or service level
        elements in different formats. If elements are referencing existing
        elements, they will be loaded in the cache for retrieval.
        
        Format #1, as list (elements are expected to exist):
            - tcp_service:
                - service1
                - service2
        
        Format #2, as dict, only used for specifying any:
            any: true
        
        Format #3, if you have retrieved the rule and the sources, services,
        and destinations are in href format, pass through.
        
            - sources:
                - http://1.1.1.1/elements/host/1
                - http://1.1.1.1/elements/host/2
                ...
    
        .. note:: This is optimal if sources, destinations or services are
            not being changed as it will not result in queries to SMC. This
            is accomplished by not setting `expand` when running the facts
            module as_yaml.
        
        Return True if any or none are used. This is necessary to verify for
        NAT rules as source ANY/None or destinations ANY/None are not valid
        when doing static_src_nat or static_dst_nat.
            
        :param list elements: list of elements as parsed from YAML file
        :param dict type_dict: type dictionary for elements that should be
            supported for this run.
        :return: returns True if any or none are set on these fields. Otherwise
            None is returned and elements are added to cache or cache missing
        :rtype: bool or None
        """
        if isinstance(elements, dict):
            if 'any' in elements or 'none' in elements:
                return True
            
            for name, value in elements.items():
                if name not in types:
                    self.fail(msg='Invalid element type specified: %s. Valid '
                        'types are: %s' % (name, list(types)))
                if not isinstance(value, list):
                    self.fail(msg='Elements specified for type: %s should be in list '
                        'format, got: %s' % (name, type(value)))
            
            self.cache.add_many([elements])

        elif isinstance(elements, list):
            for entry in elements:
                if not isinstance(entry, string_types) or not entry.startswith('http'):
                    self.fail(msg='List entry is expected to be the raw href of '
                        'the element. Received: %s' % entry)
                    
    def get_values(self, elements):
        """
        Get the values for source, destination and service cells. If these
        are not provided, return 'any'.
        """
        if not elements:
            return 'any'
        
        if isinstance(elements, dict):
            if 'any' in elements:
                return 'any'
            elif 'none' in elements:
                return None
        
            # Resolve out of cache, return as Element
            return [self.cache.get(typeof, value)
                for typeof, values in elements.items()
                for value in values]

        elif isinstance(elements, list):
            return elements
    
    def nat_definition(self, nat_type, data_dict):
        """
        Return a dict for the rule create constructor.
        
        :param str nat_type: nat type retrieved from yaml
        :param dict data_dict: nat dict from yaml definition
        :rtype: dict
        """
        nat_dict = {}
        translated_value = data_dict.get('translated_value')
        if nat_type in ('dynamic_src_nat', 'static_src_nat'):
            # Validate ports first. Range of ports must have equal length
            if 'min_port' in translated_value and 'max_port' in translated_value:
                nat_dict['%s_ports' % nat_type] = (
                    translated_value.get('min_port'),
                    translated_value.get('max_port'))

        if 'name' in translated_value and 'type' in translated_value:
            nat_dict[nat_type] = self.cache.get(
                translated_value['type'], translated_value['name'])
        else:
            nat_dict[nat_type] = translated_value.get('ip_descriptor')
        return nat_dict
 
                    
def main():
    FirewallNATRule()
    
if __name__ == '__main__':
    main()

        
