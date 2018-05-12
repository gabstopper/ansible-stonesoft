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
    or a sub-policy. Source, destination and service elements can be used and
    referenced by their type and name (they must be pre-created). Many other
    rule settings are possible, including logging, inspection and connection
    tracking settings. 

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
  template:
    description:
      - Read only view of the policy or sub policies template. This is returned
        by the facts module when retrieving rules
  inspection_policy:
    description:
      - Read only view of the inspection policy for this policy
  rules:
    description:
      - Source elements to add to the rule. Elements need to specify the type of
        element to add. If source is not provided, the rule source cell will be
        set to none and the rule will effectively be disabled.
    type: list
    default: 'none'
    suboptions:
      action:
        description:
          - Required action for the rule
        choices:
          - allow
          - discard
          - refuse
          - continue
          - jump
          - apply_blacklist
          - apply_vpn
          - enforce_vpn
          - forward_vpn
        type: str
        default: allow
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
      connection_tracking:
        description:
          - Optional settings to control connection tracking on the rule. Primary
            connection setting fields allow you to enforce MSS settings or modify
            the inspection mode to strict, loose, normal or off.
        type: dict
        required: false
        suboptions:
          mss_enforced:
            description:
              - Whether to enforce mss settings on this rule match.
            type: bool
            default: false
          mss_enforced_max:
            description:
              - Max value for MSS enforcement. This value must be larger than the
                value of I(mss_enforced_min). Required if I(mss_enforced). Set to '-1'
                to disable or set I(mss_enforced) to false
            type: int
            default: -1
          mss_enforced_min:
            description:
              - Min value for MSS enforcement. Used with I(mss_enforced_max). The value
                must be smaller than I(mss_enforced_max). Set to '-1' to disable or set
                I(mss_enforced) to false
            type: int
            default: -1
          timeout:
            description:
              - The timeout (in seconds) after which inactive connections are closed.
                This timeout only concerns idle connections. Set to '-1' to disable
            type: int
            default: -1
          state:
            description:
              - Set the connection tracking mode for the state engine. Connection tracking
                controls how state is tracked for this rule match. If set use null to unset
                back to the default state of inherit from continue rule
            type: str
            choices:
              - no
              - loose
              - normal
              - strict
              - null
      inspection_options:
        description:
          - Set inspection features on or off
        type: dict
        required: false
        suboptions:      
          decrypting:
            description:
              - Whether to allow or deny decryption on this rule match. Set to
                null to set back to inherit from continue rule
            type: bool
            choices:
              - true
              - false
              - null
          deep_inspection:
            description:
              - Whether to enable deep inspection on this rule match. Set to
                null to set back to inherit from continue rule
            type: bool
            choices:
              - true
              - false
              - null
          file_filtering:
            description:
              - Whether to enable file filtering on this rule match. Set to
                null to set back to inherit from continue rule
            type: bool
            choices:
              - true
              - false
              - null
      log_options:
        description:
          - Log options for this rule
        type: dict
        suboptions:
          application_logging:
            description:
              - Whether to enable application logging for the rule. Default sets
                it to inherit from continue rule
            type: str
            choices:
              - enforced
              - default
              - off
            default: default
          eia_executable_logging:
            description:
              - Whether to enable EIA logging for the rule. Default sets it to
                inherit from continue rule
            type: str
            default: default
            choices:
              - enforced
              - default
              - off
          user_logging:
            description:
              - Whether to enable user logging on the rule. Default sets it to
                inherit from continue rule
            type: str
            default: default
            choices:
              - enforced
              - default
              - off
          log_level:
            description:
              - Log level for this rule. Undefined sets it to inherit from continue rule
            type: str
            choices:
              - none
              - transient
              - stored
              - essential
              - alert
              - undefined
          log_accounting_info_mode:
            description:
              - Both connection opening and closing are logged and information on the volume of
                traffic is collected. This sets connection closing to 'log accounting information'.
            type: bool
            default: false
          log_closing_mode:
            description:
              - Whether to log an event when the connection closes. This is recommended to capture
                the application info which might only be written on a connection close event. This
                setting is only in effect when I(log_level) is not none. This sets connection closing
                to 'normal'.
            type: bool
            default: false
          log_payload_additionnal:
            description:
              - Log an additional payload with the log entry. By default excerpt logs 4K
            type: bool
            default: false
          log_payload_excerpt:
            description:
              - Whether to log an excerpt of 4K bytes for the log entries. Use I(log_payload_additionnal)
                to change from 4K to smaller or larger
            type: bool
            default: false
          log_payload_record:
            description:
              - Logs the payload up to the 4K specified number of bytes
            type: bool
            default: false
      authentication_options:
        description:
          - Set authentication options for this rule
        type: dict
        suboptions:
          method:
            description:
              - Authentication method/s supported for this rule. Default authentication methods
                are provided as choices. If you've created a custom authentication service
                reference it by name
            type: list
            choices:
              - IPsec Certificate
              - LDAP Authentication
              - Network Policy Server
              - User password
              - Pre-Shared Key Method
          require_auth:
            description:
              - Whether to require auth on this rule. If not set it is false. To require authentication
                set to true and specify I(method) and I(users)
            type: bool
            default: false
          users:
            description:
              - Users that are allowed to authenticate. If using an LDAP authentication resource
                specify users by their fully qualified DN and specify the system created External
                LDAP domain. Examples of LDAP configured users are
                'CN=myuser,CN=Users,DC=mydomain,DC=local,domain=myldapdomain'
                'OU=Domain Controllers,DC=mydomain,DC=local,domain=myldapdomain'
                'dc=mydomain,dc=local,domain=myldapdomain'
            type: list
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
- name: Example log all rule for top of rule set
  firewall_rule:
    policy: TestPolicy
    rules:
    -   action: continue
        comment: logging rule
        log_options:
          log_accounting_info_mode: true
          log_closing_mode: true
          log_level: stored
        is_disabled: false
        name: Log all continue rule

- name: Create a rule with specific sources and services
  firewall_rule:
    smc_logging:
      level: 10
      path: ansible-smc.log
    policy: TestPolicy
    rules:
    -   action: allow
        comment: my comment
        connection_tracking:
            mss_enforced: true
            mss_enforced_max: 1555
            mss_enforced_min: 0
            timeout: 11
        destinations:
            group:
            - foogroup
            host:
            - host-1.1.1.1
            ip_list:
            - Amazon S3
            network:
            - foonet
        inspection_options:
            decrypting: null
            deep_inspection: null
            file_filtering: null
        is_disabled: false
        log_options:
            application_logging: enforced
            eia_executable_logging: 'off'
            log_accounting_info_mode: false
            log_closing_mode: true
            log_compression: 'off'
            log_level: none
            log_payload_additionnal: true
            log_payload_excerpt: false
            log_payload_record: false
            log_severity: -1
            user_logging: enforced
        name: ruletest2
        services:
            ip_service:
            - CHAOS
            tcp_service:
            - AOL
            udp_service:
            - Biff
        sources:
            country:
            - China
            interface_nic_x_ip_alias:
            - $$ Interface ID 0.ip
            single_fw:
            - myfw
    
- name: Create a rule to use VPN, requires a vpn_policy or mobile_vpn set
  firewall_rule:
    smc_logging:
      level: 10
      path: ansible-smc.log
    inspection_policy: High-Security Inspection Template
    policy: TestPolicy
    rules:
    -   action: enforce_vpn
        comment: my comment
        connection_tracking:
            mss_enforced: false
            mss_enforced_max: -1
            mss_enforced_min: -1
            timeout: -1
        destinations:
            any: true
        inspection_options:
            decrypting: null
            deep_inspection: null
            file_filtering: null
        is_disabled: false
        authentication_options:
            method:
            - LDAP Authentication
            require_auth: true
            users:
            - dc=lepages,dc=local,domain=myldapdomain
        log_options:
            application_logging: default
            eia_executable_logging: default
            log_accounting_info_mode: true
            log_closing_mode: false
            log_compression: 'off'
            log_level: stored
            log_payload_additionnal: false
            log_payload_excerpt: false
            log_payload_record: false
            log_severity: -1
        name: ruletest2
        services:
            any: true
        sources:
            any: true
        vpn_policy: MOBILE CLIENT VPN
    template: Firewall Inspection Template

- name: Add a deny rule after specified rule using add_after syntax
  firewall_rule:
    smc_logging:
      level: 10
      path: ansible-smc.log
    policy: TestPolicy
    rules:
    -   action: discard
        comment: deny rule
        is_disabled: false
        name: my deny
        add_after: '2097193.0'

- name: Delete a rule
  firewall_rule:
    policy: TestPolicy
    rules:
    -   tag: '2097203.0'
    state: absent
'''
import traceback
from ansible.module_utils.six import integer_types
from ansible.module_utils.six import string_types

from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache)


try:
    from smc.policy.layer3 import FirewallPolicy
    from smc.policy.layer3 import FirewallSubPolicy
    from smc.api.exceptions import SMCException
    from smc.policy.rule_elements import LogOptions, ConnectionTracking, \
        Action, AuthenticationOptions
except ImportError:
    pass


action = ('allow', 'discard', 'refuse', 'continue', 'jump', 'apply_blacklist',
    'apply_vpn', 'enforce_vpn', 'forward_vpn')

log_levels = ('none', 'transient', 'stored', 'essential', 'alert', 'undefined')

log_override = ('default', 'enforced', 'off')

cxn_tracking = ('no', 'loose', 'normal', 'strict')

inspection_options = ('decrypting', 'deep_inspection', 'file_filtering')

rule_targets = ('adress_range', 'country', 'domain_name', 'expression', 'group', 'host',
    'ip_list', 'network', 'engine', 'router', 'netlink', 'interface_zone', 'alias')

service_targets = ('service_group', 'tcp_service_group', 'udp_service_group', 'ip_service_group',
    'icmp_service_group', 'tcp_service', 'udp_service', 'ip_service', 'ethernet_service', 'icmp_service',
    'application_situation', 'url_category')

sentinel = object()


def validate_rule(rule):
    """
    Validate the rule by checking fields that do not require a call
    to the SMC. Sources, Destinations and Services are not validated
    in this initial check.
    
    :param dict rule: firewall rule defined in yaml
    :return: None
    """
    if 'tag' not in rule and 'name' not in rule:
        raise Exception('A rule must have either a rule tag or a '
            'name field: %s' % rule)
    
    if 'action' in rule and rule['action'] not in action:
        raise Exception('Invalid action specified: %s, valid options: %s' %
            (rule['action'], action))
    
    if rule.get('action') in ('forward_vpn', 'enforce_vpn', 'apply_vpn'):
        if 'mobile_vpn' not in rule and 'vpn_policy' not in rule:
            raise Exception('You must provide a value for mobile_vpn or vpn_policy '
                'when using a VPN action: %s' % rule['action'])
    
    elif rule.get('action') == 'jump':
        if 'sub_policy' not in rule:
            raise Exception('Jump policy specified in rule: %s but no sub_policy '
                'parameter was specified' % rule.get('name'))
        
    if 'connection_tracking' in rule:
        ct = rule['connection_tracking']
        if ct.get('mss_enforced', False):
            for field in ('mss_enforced_max', 'mss_enforced_min', 'timeout'):
                if not isinstance(ct.get(field, 0), integer_types):
                    raise Exception('Connection tracking field: %s must be an '
                        'int value, received: %s' % (field, ct))
            # Timeout of -1 is disabled
            if ct.get('mss_enforced_max') < 0 or ct.get('mss_enforced_max') < \
                ct.get('mss_enforced_min'):
                raise Exception('MSS enforced max must be higher than the MSS '
                    'enforced min value in rule: %s' % rule)
    
        # Connection Tracking Mode
        if ct.get('state') and ct['state'] not in cxn_tracking:
            raise Exception('Connection tracking mode state provided invalid field: %s '
                'valid values: %s' % (ct['state'], cxn_tracking))
    
    if 'log_options' in rule:
        logging = rule['log_options']
        if 'log_level' in logging and logging.get('log_level') not in log_levels:
            raise Exception('Log level: %s invalid. Valid values are: %s' %
                (logging.get('log_level'), log_levels))
        
        for field in ('application_logging', 'eia_executable_logging', 'user_logging'):
            if field in logging and logging.get(field) not in log_override:
                raise Exception('Logging override setting: %s is invalid type. '
                    'value: %s, valid: %s' % (field, logging.get(field), log_override))
        
        for field in ('log_accounting_info_mode', 'log_closing_mode',
            'log_payload_record', 'log_payload_additionnal'):
            if field in logging and not isinstance(logging.get(field), bool):
                raise Exception('Log field: %s must be of type bool. Received: %s'
                    % (field, logging.get(field)))
    
    if 'inspection_options' in rule:
        inspection = rule['inspection_options']
        for field in inspection_options:
            if field in inspection and inspection.get(field, sentinel) not \
                in (None, True, False):
                raise Exception('Invalid setting for inspection field: %s. Value options '
                    'are None, True or False' % field)
                
    if 'authentication_options' in rule:
        auth_options = rule['authentication_options']
        if auth_options.get('require_auth'):
            if not auth_options.get('methods', []):
                raise Exception('You must specify authentication methods when requiring '
                    'authentication on a rule: %s' % rule.get('name'))
            if not auth_options.get('users') and not auth_options.get('groups'):
                raise Exception('You must specify users and/or groups when enabling '
                    'authentication on a rule: %s' % rule.get('name'))
            else: # Verify correct user format
                for field in ('users', 'groups'):
                    for value in auth_options.get(field, []):
                        if len(value.split(',domain=')) != 2:
                            raise Exception('When defining users you must use a fully '
                                'qualified syntax which should end with `domain=`. The '
                                'value of domain should map to the internal or external '
                                'user domain defined in SMC')


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
    
    yaml_action = rule_dict.get('action').action
    if rule.action.action != yaml_action:
        vpn_action = ('apply_vpn', 'enforce_vpn', 'forward_vpn')
        # Undo VPN setting
        if yaml_action == 'jump':
            rule.action.sub_policy = rule_dict.get('sub_policy')
        elif rule.action.action in vpn_action and yaml_action not in vpn_action:
            rule.action.vpn = None
            rule.action.mobile_vpn = False
        # YAML action switches to VPN or VPN type is changed
        elif yaml_action in vpn_action and rule.action.action not in vpn_action or \
            yaml_action in vpn_action and rule.action.action in vpn_action:
            if rule_dict.get('vpn_policy', None):
                rule.action.vpn = rule_dict.get('vpn_policy')
            else: #mobile VPN
                rule.action.mobile_vpn = True
        
        rule.action.action = yaml_action
        changes.append('action')
            
    if 'log_options' in rule_dict:
        for name, value in rule_dict['log_options'].items():
            if getattr(rule.options, name, None) != value:
                rule.options.update(**rule_dict['log_options'])
                changes.append('log_options')
                break
    
    if 'connection_tracking' in rule_dict:
        for name, value in rule_dict['connection_tracking'].items():
            if getattr(rule.action.connection_tracking_options, name, None) != value:
                rule.action.connection_tracking_options.update(**rule_dict['connection_tracking'])
                changes.append('connection_tracking')
                break
    
    if 'authentication_options' in rule_dict:
        auth = rule_dict['authentication_options'] #AuthenticationOptions
        if auth != rule.authentication_options:
            if auth.require_auth != rule.authentication_options.require_auth and \
                not auth.require_auth:
                rule.authentication_options.update(
                    require_auth=False, methods=[], users=[])
            else:
                rule.authentication_options.data.update(auth.data)
            changes.append('authentication_options')
        
    for field in inspection_options:
        if field in rule_dict.get('action'):
            if getattr(rule.action, field) != getattr(rule_dict.get('action'), field):
                rule.action[field] = getattr(rule_dict.get('action'), field)
                changes.append('inspection_options: %s' % field)
    
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

    return changes


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
        

class FirewallRule(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            policy=dict(type='str'),
            sub_policy=dict(type='str'),
            template=dict(type='str'),
            rules=dict(type='list', default=[]),
            inspection_policy=dict(type='str'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.policy = None
        self.sub_policy = None
        self.template = None
        self.rules = None
        self.inspection_policy = None
        self.use_search_hints = None
        
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
        
        super(FirewallRule, self).__init__(self.module_args,
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
                
                for rule in self.rules:
                    try:
                        validate_rule(rule)
                    except Exception as e:
                        self.fail(msg=str(e))
        
                self.cache = Cache()

                for rule in self.rules:
                    # Resolve elements if they exist, calls to SMC could happen here
                    if 'sources' in rule:
                        self.field_resolver(rule.get('sources'), rule_targets)
                    
                    if 'destinations' in rule:
                        self.field_resolver(rule.get('destinations'), rule_targets)
                    
                    if 'services' in rule:
                        self.field_resolver(rule.get('services'), service_targets)
                    
                    if 'vpn_policy' in rule:
                        self.cache._add_entry('vpn', rule.get('vpn_policy'))
                        
                    if 'sub_policy' in rule:
                        self.cache._add_entry('sub_ipv4_fw_policy', rule.get('sub_policy'))
                    
                    if 'authentication_options' in rule:
                        auth = rule['authentication_options']
                        if auth.get('require_auth'):
                            for method in auth.get('methods'):
                                self.cache._add_entry('authentication_service', method)
                            
                            for accounts in ('users', 'groups'):
                                self.cache._add_user_entries(accounts, auth.get(accounts, []))

                if self.cache.missing:
                    self.fail(msg='Missing required elements that are referenced in this '
                        'configuration: %s' % self.cache.missing)
                
                if self.check_mode:
                    return self.results
                
                for rule in self.rules:
                    rule_dict = {}
                
                    if 'log_options' in rule:
                        log_options = LogOptions()
                        _log = rule['log_options']
                        for name, value in log_options.items():
                            if name not in _log:
                                log_options.pop(name)
            
                        log_options.update(rule.get('log_options', {}))
                        rule_dict.update(log_options=log_options)

                    if 'connection_tracking' in rule:
                        connection_tracking = ConnectionTracking()
                        _ct = rule['connection_tracking']
                        for name, value in connection_tracking.items():
                            if name not in _ct:
                                connection_tracking.pop(name)
            
                        connection_tracking.update(rule.get('connection_tracking',{}))
                        rule_dict.update(connection_tracking=connection_tracking)
                    
                    action = Action()
                    action.action = rule.get('action', 'allow')
                    
                    if 'inspection_options' in rule:
                        _inspection = rule['inspection_options']
                        for option in inspection_options:
                            if option in _inspection:
                                action[option] = _inspection.get(option)
                    
                    if 'authentication_options' in rule:
                        _auth_options = rule['authentication_options']
                        auth_options = AuthenticationOptions()
                        
                        if _auth_options.get('require_auth'):
                            auth_options.update(methods=[
                                self.get_value('authentication_service', m).href
                                for m in _auth_options.get('methods', [])],
                            require_auth=True)
                            
                            auth_options.update(users=[entry.href
                                for entry in self.cache.get_type('user_element')])

                        rule_dict.update(authentication_options=auth_options)
                    
                    rule_dict.update(action=action)
                    
                    for field in ('sources', 'destinations', 'services'):
                        rule_dict[field] = self.get_values(rule.get(field, None))

                    rule_dict.update(
                        vpn_policy=self.get_value('vpn', rule.get('vpn_policy')),
                        sub_policy=self.get_value('sub_ipv4_fw_policy', rule.get('sub_policy')),
                        mobile_vpn=rule.get('mobile_vpn', False))
                    
                    if 'comment' in rule:
                        rule_dict.update(comment=rule.get('comment'))
                    
                    rule_dict.update(
                        name=rule.get('name'),
                        is_disabled=rule.get('is_disabled', False))
                    
                    if 'tag' not in rule:
                        # If no tag is present, this is a create
                        rule_dict.update(
                            before=rule.get('add_before'),
                            after=rule.get('add_after'))
                        
                        rule = policy.fw_ipv4_access_rules.create(**rule_dict)
                        changed = True
                        self.results['state'].append({
                            'rule': rule.name,
                            'type': rule.typeof,
                            'action': 'created'})
                    
                    else:
                        # Modify as rule has 'tag' defined. Fetch the rule first
                        # by it's tag reference, skip if tag not found
                        target_rule = self.rule_by_tag(policy, rule.get('tag'))
                        if not target_rule:
                            continue

                        changes = compare_rules(target_rule, rule_dict)
                        # Changes have already been merged if any
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
        rule = policy.search_rule('@{}'.format(resolved_tag))
        if rule:
            return rule[0]
        
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
            
        :param list elements: list of elements as parsed from YAML file
        :param dict type_dict: type dictionary for elements that should be
            supported for this run.
        """
        if isinstance(elements, dict):
            if 'any' in elements or 'none' in elements:
                return
            
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
                if not entry.startswith('http'):
                    self.fail(msg='List entry is expected to be the raw href of '
                        'the element. Received: %s' % entry)
    
    def get_value(self, typeof, element):
        """
        Get single value from cache
        
        :param str typeof: typeof element by key
        :param str element to fetch
        """
        return self.cache.get(typeof, element)
        
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
        
def main():
    FirewallRule()
    
if __name__ == '__main__':
    main()
    