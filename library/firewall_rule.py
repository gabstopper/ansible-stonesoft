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
module: firewall_rule
short_description: Create, modify or delete a firewall rule
description:
  - Firewall rules can be added or removed from either a top level policy
    or a sub-policy. Source/destination and service elements can optionally
    be created or provided individually or as a list. See examples below. In
    addition, this module supports check mode. It will still perform get requests
    to the SMC but will not perform an actual create.

version_added: '2.5'

options:
  name:
    description:
      - A unique name for the rule. Rules are searchable by name so this should
        be something that represents the purpose of the rule.
    required: true
    type: str
  policy:
    description:
      - Name of the policy for the rule. This is required if I(sub_policy)
        is not set.
    type: str
  sub_policy:
    description:
      - Name of the sub policy for the rule. This is required if I(policy) is
        not set.
    type: str
  source:
    description:
      - Source elements to add to the rule. Elements need to specify the type of
        element to add. If source is not provided, the rule source cell will be
        set to none and the rule will effectively be disabled.
    type: list
    default: 'none'
    suboptions:
    
'''

import traceback
from ansible.module_utils.six import string_types
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    element_type_dict,
    ro_element_type_dict,
    service_type_dict,
    ro_service_type_dict,
    get_or_create_element)


try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.policy.layer3 import FirewallSubPolicy
    from smc.policy.rule_elements import LogOptions, Action
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def is_allow_action(action):
    """
    Determine the rule action type. Allow type actions allow additional
    settings that can be enabled such as file filtering, inspection and
    connection settings.
    
    :rtype: bool
    """
    if action in ('allow', 'continue', 'apply_vpn', 'enforce_vpn', 'forward_vpn'):
        return True
    return False


def check_on_off(value):
    """
    Check the on/off/default value to ensure it's valid. This is
    used for action fields that provide 3 states, on/off or
    inherit the configuration from a continue rule (default).
    
    :rtype: bool
    """
    if isinstance(value, bool):
        return True
    elif value in ('default',):
        return True
    return False
    

def connection_tracking_opt():
    """
    Supported connection tracking options
    """
    return ('default', 'on', 'off', 'normal', 'strict', 'loose')


def log_levels():
    """
    Supported log levels
    """
    return ('none', 'transient', 'stored', 'essential', 'alert', 'undefined')


def std_opt():
    """
    Common options for enabling and disabling features.
    """
    return ('default', 'on', 'off')


def is_valid_int(field):
    """
    Is the field a valid int
    
    :rtype: bool
    """
    try:
        i = int(field)
        return i > 0
    except ValueError:
        return False


def _log_fmt(field):
    """
    Turning on log enforcement by types (users, applications) uses
    'on', 'off' and 'enforced' in the SMC API. Convert the common
    on/off/default settings into the proper format:
    
        True = 'enforced'
        False = 'off'
        default = 'default' (override by Continue rule)
    
    :rtype: str
    """
    if isinstance(field, bool):
        if field:
            return 'enforced'
        else:
            return 'off'

        return 'default'


def _bool_none(field):
    """
    Enabling, disabling and setting inspection options use 
    True/False/None. This returns None if setting was set
    to use 'default', otherwise the boolean is valid
    """
    if isinstance(field, bool):
        return field
    #return None
            

class FirewallRule(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            policy=dict(type='str'),
            sub_policy=dict(type='str'),
            source=dict(type='list'),
            destination=dict(type='list'),
            action=dict(type='str', choices=['allow', 'discard', 'refuse', 'continue',
                'jump', 'apply_blacklist', 'apply_vpn', 'enforce_vpn', 'forward_vpn']),
            service=dict(type='list'),
            jump_policy=dict(type='str'),
            vpn_policy=dict(type='str'),
            blacklist_target=dict(type='str'),
            logging=dict(type='dict'),
            inspection_options=dict(type='dict'),
            connection_options=dict(type='dict'),
            position=dict(type='str'),
            use_search_hints=dict(default=True, type='bool'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.policy = None
        self.sub_policy = None
        self.action = None
        self.source = None
        self.destination = None
        self.service = None
        self.logging = None
        self.jump_policy = None
        self.vpn_policy = None
        self.blacklist_target = None
        self.inspection_options = None
        self.connection_options = None
        self.position = None
        self.use_search_hints = None
        
        mutually_exclusive = [
            ['policy', 'sub_policy'],
        ]
        
        required_one_of = [
            [ 'policy', 'sub_policy' ]
        ]
        
        required_if=([
            ('action', 'jump', ['jump_policy']),
            ('action', 'apply_vpn', ['vpn_policy']),
            ('action', 'forward_vpn', ['vpn_policy']),
            ('action', 'enforce_vpn', ['vpn_policy']),
            ('action', 'apply_blacklist', ['blacklist_target'])
        ])
        self.results = dict(
            changed=False,
            state=[]
        )
        super(FirewallRule, self).__init__(self.module_args,
            mutually_exclusive=mutually_exclusive, required_one_of=required_one_of,
            required_if=required_if, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:    
            if (self.inspection_options or self.connection_options) and \
                not is_allow_action(self.action):
                self.fail(msg='Inspection and connection options are not allowed '
                    'with the following action: {}'.format(self.action))
            
            if self.logging:
                log = self.logging
                if 'log_level' in log and log['log_level'] not in log_levels():
                    self.fail(msg='Valid log levels: {}, got: {}'.format(log_levels(), log['log_level']))
                
                for opt, value in log.items():
                    if opt != 'log_level':
                        if not check_on_off(value):
                            self.fail(msg='Value of {} must be {}, got: {} '
                                .format(opt, std_opt(), value))
                    
            if self.inspection_options:
                for opt, value in self.inspection_options.items():
                    if not check_on_off(value):
                        self.fail(msg='Value of {} must be {}, got: {}'
                            .format(opt, std_opt(), value))
                            
            if self.connection_options:
                if 'connection_tracking' in self.connection_options and \
                    self.connection_options['connection_tracking'] not in connection_tracking_opt():
                    self.fail(msg='Value of connection_tracking must be: {}, got: {}'.format(
                        connection_tracking_opt(), self.connection_options['connection_tracking']))
            
                if 'synchronize' in self.connection_options and not check_on_off(
                    self.connection_options['synchronize']):
                    self.fail(msg='Value of synchronize must be: {}, got: {}'
                        .format(std_opt(), self.connection_options['synchronize']))
                    
                if 'idle_timeout' in self.connection_options and not \
                    is_valid_int(self.connection_options['idle_timeout']):
                        self.fail(msg='Invalid idle timeout value: {}, must be a positive int '
                            'value'.format(self.connection_options['idle_timeout']))
                        
                if 'enforce_tcp_mss' in self.connection_options:
                    opts = self.connection_options['enforce_tcp_mss']
                    for k, v in opts.items():
                        if k not in ('min', 'max'):
                            self.fail(msg='Invalid mss setting. Valid option settings: {}'
                                .format(('min','max')))
                        else:
                            if not is_valid_int(v):
                                self.fail(msg='MSS value invalid: {}, got: {}'
                                    .format(k, v))
                    
            # Now that we have valid option settings, we can hit the db
            if self.policy:
                policy = FirewallPolicy.get(self.policy)
            else:
                policy = FirewallSubPolicy.get(self.sub_policy)
            
            if state == 'present':

                NETWORK_ELEMENTS = element_type_dict()
                NETWORK_ELEMENTS.update(ro_element_type_dict())
                
                # Check network elements first
                if self.source:
                    sources = self.field_resolver(self.source, NETWORK_ELEMENTS)
                    #self.fail(msg=[x.href for x in sources])
                    
                if self.destination:
                    destinations = self.field_resolver(self.destination, NETWORK_ELEMENTS)
                    #self.fail(msg=destinations)
                
                SERVICE_ELEMENTS = service_type_dict()
                SERVICE_ELEMENTS.update(ro_service_type_dict())
                
                if self.service:
                    services = self.field_resolver(self.service, SERVICE_ELEMENTS)
                    
                if self.check_mode:
                    return self.results
                
                log_options = None if not self.logging else self.logging_options()
                action = self.action if not (self.inspection_options and self.connection_options) \
                    else self.action_options()
                    
                rule = policy.fw_ipv4_access_rules.create(
                    name=self.name,
                    sources=sources,
                    destinations=destinations,
                    services=services,
                    action=action,
                    log_options=log_options,
                    vpn_policy=self.vpn_policy,
                    sub_policy=self.jump_policy)
                
                self.results['state'] = rule.data
                self.results['changed'] = True

            elif state == 'absent':
                pass

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def logging_options(self):
        """
        Set logging options on this rule
        
        :return LogOptions
        """
        options = LogOptions()
        if 'log_level' in self.logging:
            options.log_level = self.logging['log_level']
        if 'log_accounting' in self.logging:
            options.log_accounting_info_mode = _bool_none(self.logging['log_accounting'])
        if 'application_logging' in self.logging:
            options.application_logging = _log_fmt(self.logging['application_logging'])
        if 'user_logging' in self.logging:
            options.user_logging = _log_fmt(self.logging['user_logging'])
        return options 
    
    def action_options(self):
        """                
        Set inspection options on the action of this rule
        
        :return Action
        """
        action = Action()
        action.action = self.action
        if self.connection_options:
            conn = action.connection_tracking_options
            if 'connection_tracking' in self.connection_options:
                conn.state = self.connection_options['connection_tracking']
            if 'idle_timeout' in self.connection_options:
                conn.timeout = self.connection_options['idle_timeout']
            if 'synchronize' in self.connection_options:
                conn.sync_connections = _bool_none(self.connection_options['synchronize'])
            if 'enforce_tcp_mss' in self.connection_options:
                conn.mss_enforced = True
                conn.mss_enforced_min_max = (
                    self.connection_options['enforce_tcp_mss']['min'],
                    self.connection_options['enforce_tcp_mss']['max'])
            
        if self.inspection_options:
            if 'deep_inspection' in self.inspection_options:
                action.deep_inspection = _bool_none(self.inspection_options['deep_inspection'])
            if 'file_filtering' in self.inspection_options:
                action.file_filtering = _bool_none(self.inspection_options['file_filtering'])
                
        return action
            
    def field_resolver(self, elements, type_dict, search_hints=None):
        """
        Field resolver, specific to retrieving network or service level
        elements in different formats.
        
        YAML format #1:
            - tcp_service: service_name
                
        Format #2, as list (elements are expected to exist):
            - tcp_service:
                - service1
                - service2
        
        Format #1 can also be used to get_or_create if the element types
        attributes are provided:
        
            - host: myhost
              address: 1.1.1.1
        
        :param list elements: list of elements as parsed from YAML file
        :param dict type_dict: type dictionary for elements that should be
            supported for this run.
        """
        values = []
        for element in elements:
            if isinstance(element, dict):
                filter_key = element.pop('filter_key', None)
                
                key = [key for key in set(element) if key in type_dict]
                if key and len(key) == 1:
                    typeof = key.pop()
                    element['name'] = element.pop(typeof)
                    
                    # Is format #1
                    if isinstance(element['name'], list):
                        # Add each element to the collection
                        clazz = type_dict.get(typeof)['type']
                        for e in element['name']:
                            if not (isinstance(e, string_types)):
                                self.fail(msg='List items must be string type, got: {}'
                                    .format(e))
                                
                            found = clazz.objects.filter(e, exact_match=True).first()
                            if not found:
                                if self.check_mode:
                                    self.results['state'].append(
                                        dict(name=e,
                                             type=typeof,
                                             msg='Specified list element is missing'))
                                else:
                                    self.fail(msg='{} type element was not found, got: {}'.format(typeof, e))
                            
                            values.append(found)
                
                    elif typeof == 'network' and element['name'].upper() == 'ANY':
                        return 'any'
                
                    else:
                        element_dict = {typeof: element}
                        self.is_element_valid(element_dict, type_dict, check_required=False)
                        
                        if not filter_key and search_hints:
                            filter_key = search_hints.get(typeof)
                        
                        result = get_or_create_element(element_dict, type_dict, filter_key, self.check_mode)
                        if self.check_mode:
                            if result is not None:
                                self.results['state'].append(result)
                        else:
                            values.append(result)
                          
                else:
                    self.fail(msg='Element not found: {}'.format(element))
            else:
                self.fail(msg='Invalid format provided for element: {}'.format(element))
        
        return values
    

def main():
    FirewallRule()
    
if __name__ == '__main__':
    main()
    