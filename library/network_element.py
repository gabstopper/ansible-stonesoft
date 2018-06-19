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
module: network_element
short_description: Create, modify or delete network elements
description:
  - Each element type currently supported in this module is documented in the example
    playbook. Each network element type will have a minimum number of arguments
    that is required to create the element if it does not exist. Network elements
    supported by this module have their `create` constructors documented at
    U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements). This
    module uses a 'update or create' logic, therefore it is not possible to create
    the same element twice. If the element exists and the attributes provided are 
    different, the element will be updated before returned. It also means this module can
    be run multiple times with only slight modifications to the playbook. This is useful
    when an error is seen with a duplicate name, etc and you must re-adjust the playbook
    and re-run. For groups, you can reference a member by name which will require it to
    exist, or you can also specify the required options and create the element if it
    doesn't exist.

version_added: '2.5'

options:
  elements:
    description:
      - A list of the elements to create, modify or remove
    type: list
    required: true
    suboptions:
      host:
        description:
          - A network element of type host
        type: dict
        suboptions:
          name:
            description:
              - Name of this host element
            type: str
            required: true
          address:
            description:
              - IPv4 address for this host, required if I(ipv6_address) is not defined.
            type: str
          ipv6_address:
            description:
              - IPv6 address for this host, required if I(address) is not defined.
          secondary:
            description:
              - Optional secondary IP addresses for this host
            type: list
          comment:
            description:
              - Optional comment for this host
      network:
        description:
          - A network element of type network
        type: dict
        suboptions:
          name: 
            description:
              - Name of this network element
            type: str
            required: true
          ipv4_network:
            description:
              - IPv4 network in cidr format, required if I(ipv6_network) is not defined.
            type: str
          ipv6_network:
            description:
              - IPv6 network in cidr format, required if I(ipv4_network) is not defined.
            type: str
          comment:
            description:
              - Optional comment for this network
      address_range:
        description:
          - A network element of type address range
        type: dict
        suboptions:
          name:
            description:
              - Name of this address range
            type: str
            required: true
          ip_range:
            description: 
              - The address range defintion, starting [dash] ending network
            type: str
            required: true
          comment:
            description:
              - Optional comment
            type: str
      interface_zone:
        description:
          - A zone tag optionally assigned to an interface
        type: dict
        suboptions:
          name:
            description:
              - Name of this zone
            type: str
            required: true
          comment:
            description:
              - Optional comment
            type: str
      domain_name:
        description:
          - Domain name element to be used in rule
        type: dict
        suboptions:
          name: 
            description:
              - Domain name value, i.e. google.com
            type: str
            required: true
          comment:
            description:
              - Optional comment
            type: str
      router:
        description:
          - A router element
        type: dict
        suboptions:
          name: 
            description:
              - Name of this router element
            type: str
            required: true
          address:
            description:
              - IPv4 address for this host, required if I(ipv6_address) is not defined.
            type: str
          ipv6_address:
            description:
              - IPv6 address for this host, required if I(address) is not defined.
            type: str
          secondary:
            description:
              - Optional secondary IP addresses for this host
            type: list
          comment:
            description:
              - Optional comment for this host
            type: str
      ip_list:
        description:
          - An IP list element containing individual addresses and networks
        type: dict
        suboptions:
          name: 
            description:
              - Name of this router element
            type: str
            required: true
          iplist:
            description:
              - A list of IPv4, IPv6 addresses or networks
            type: list
            required: true
      group:
        description:
          - A group of network elements
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of dict with the key being the type of element and the value is
                a list of members by name. Members for a group can be any one of the
                valid elements defined in this playbook. In addition, you can add
                read-only element types engine, alias, and expression
            type: list
          append_lists:
            description:
              - Append defined members to the existing list of group members. Setting this
                to false will overwrite the existing group with the defined members
            type: bool
            default: false
          remove_members:
            description:
              - Set to true to reverse the group logic by specifying the defined members
                be deleted from the group. This setting is mutually exclusive with I(append_lists)
            type: bool
            default: false
          comment:
            description:
              - Optional comment for the group
            type: str
      netlink:
        description:
          - Create a Static Netlink element
        type: dict
        suboptions:
          name:
            description:
              - Name of the netlink
            type: str
            required: true
          comment:
            description:
              - optional comment
            type: str
          gateway:
            description:
              - The gateway element used as the next hop for the netlink. This
                should be a dict with name and type defined. The element referenced
                in name and type should exist and be of type router or engine
            type: dict
            suboptions:
              name: 
                description:
                  - name of the gateway element
                type: str
              type:
                description:
                  - type of element
                choices:
                  - router
                  - engine
                type: dict
          network:
            description:
              - List of networks for this netlink. These are referenced by element
                name and expected to exist
            type: list
            required: true
          domain_server_address:
            description:
              - Optional list of DNS server elements by name
            type: list
          probe_address:
            description:
              - optional list of addresses to probe for status
            type: list
        comment:
          description:
            - optional comment
          type: str
  ignore_err_if_not_found:
    description:
      - When deleting elements, whether to ignore an error if the element is not found.
        This is only used when I(state=absent).
    default: True
  state:
    description:
      - Create or delete flag
    required: false
    default: present
    choices:
      - present
      - absent
 
extends_documentation_fragment:
  - stonesoft
 
requirements:
  - smc-python
author:
  - David LePage (@gabstopper)        
'''

EXAMPLES = '''
- name: Create a network element
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Example network element creation
    register: result
    network_element:
      smc_logging:
        level: 10
        path: ansible-smc.log
      elements:
        - host: 
            name: hostb
            address: 1.1.1.1
            ipv6_address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
            secondary:
              - 1.1.1.2
              - 1.1.1.3
        - network:
            name: networka
            ipv4_network: 3.3.3.0/24
            ipv6_network: fc00::/7
            comment: created by dlepage
        - address_range:
            name: myrange
            ip_range: 1.1.1.1-1.1.1.10
        - interface_zone:
            name: myzone
        - domain_name:
            name: mydomain.com
            comment: foo
        - router:
            name: myrouter
            address: 172.18.1.254
            secondary:
              - 172.18.1.253
            ipv6_address: 2003:dead:beef:4dad:23:46:bb:101
        - ip_list: 
            name: myiplist
            comment: testlist
            iplist:
              - 1.1.1.1
              - 1.1.1.2
              - 1.1.1.3
              - 1.1.1.4
        - group:
            name: foogroup
            #remove_members: true
            #append_lists: true
            members:
                host:
                - hosta
                - hostb
                network:
                - networka
                engine:
                - myfw
                - myfw2
        - group:
            name: emptyregulargrp
            members:
        - router:
            name: myrouter2
            address: 13.13.13.13
        - network:
            name: mynetwork2
            ipv4_network: 13.13.13.0/24
        - netlink:
            name: mynetlink2
            gateway:
                name: myrouter2
                type: router
            network:
            -   mynetwork2
            domain_server_address:
                -   8.8.8.8
                -   8.8.7.7
            probe_address:
                -   10.10.10.1
            comment: added by ansible


- name: Delete network elements. Use a list of elements by name
  network_element:
    smc_logging:
        level: 10
        path: ansible-smc.log
    state: absent
    elements:
      - group:
          - mygroup
          - newgroupa
      - host:
          - hosta
          - hostb
      - network:
          - networka
      - address_range:
          - myrange
      - interface_zone:
          - myzone
      - domain_name:
          - mydomain.com
      - router:
          - myrouter
      - ip_list:
          - myiplist
'''

RETURN = '''
state:
    description: Current state of elements
    returned: always
    type: list
    sample: [
        {
            "action": "created", 
            "name": "myservice", 
            "type": "tcp_service"
        }, 
        {
            "name": "newservice80", 
            "type": "tcp_service"
        }, 
        {
            "action": "created", 
            "name": "myudp", 
            "type": "udp_service"
        }, 
        {
            "name": "udp2000", 
            "type": "udp_service"
        }, 
        {
            "action": "created", 
            "name": "new service", 
            "type": "ip_service"
        }]
'''

import copy
import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache, element_type_dict,
    ro_element_type_dict, update_or_create, delete_element)


try:
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class NetworkElement(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            elements=dict(type='list', required=True),
            ignore_err_if_not_found=dict(type='bool', default=True),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
    
        self.elements = None
        self.ignore_err_if_not_found = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(NetworkElement, self).__init__(self.module_args, supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        ELEMENT_TYPES = element_type_dict()
        GROUP_MEMBER_TYPES = ro_element_type_dict(map_only=True)
        GROUP_MEMBER_TYPES.update(ELEMENT_TYPES)
        
        try:
            if state == 'present':
                deferred_elements = ('group', 'netlink')
                # Validate elements before proceeding.
                groups, netlinks = [], []
                for element in self.elements:
                    self.is_element_valid(element, ELEMENT_TYPES if 'group' not in\
                        element else GROUP_MEMBER_TYPES)
                    if 'group' in element:
                        groups.append(element)
                    elif 'netlink' in element:
                        netlinks.append(element)
                
                if groups or netlinks:
                    to_be_created = self.to_be_created_elements()
                    self.cache = Cache()
                
                if groups:
                    self.enum_group_members(groups, to_be_created)
                    if self.cache.missing:
                        self.fail(msg='Group members referenced are missing and are not being '
                            'created in this playbook: %s' % self.cache.missing)
                
                if netlinks:
                    self.enum_netlink_members(netlinks, to_be_created)
                    if self.cache.missing:
                        self.fail(msg='Netlink elements referenced are missing and are not being '
                            'created in this playbook: %s' % self.cache.missing)

                for element in self.elements:
                    for typeof, _ in element.items():
                        if typeof not in deferred_elements:
                            result = update_or_create(
                                element, ELEMENT_TYPES, check_mode=self.check_mode)
                            self.results['state'].append(result)

                for group in groups:
                    # Run through cache again, entries that exist will not be
                    # added twice but this captures elements that might have been
                    # added earlier by the playbook run
                    _group = copy.deepcopy(group)
                    members = _group.get('group', {}).get('members', {}) 
                    if members:
                        self.cache.add_many([members])
                        # Add to new members list
                        _members = [self.cache.get(typeof, value)
                            for typeof, member in members.items()
                            for value in member]
                    else: # No members defined
                        _members = []

                    _group.setdefault('group', {}).update(
                        members=_members)
                    
                    result = update_or_create(_group, ELEMENT_TYPES, check_mode=self.check_mode)
                    self.results['state'].append(result)
                
                for netlink in netlinks:
                    _netlink = copy.deepcopy(netlink)
                    gateway = _netlink.get('netlink', {}).get('gateway')
                    self.cache._add_entry(gateway.get('type'), gateway.get('name'))
                    _netlink.setdefault('netlink').update(
                        gateway=self.cache.get(
                            gateway.get('type'), gateway.get('name')))
                    
                    # Update networks
                    networks = _netlink.get('netlink').get('network')
                    for net in networks:
                        self.cache._add_entry('network', net)
                    _netlink.setdefault('netlink').update(
                        network=[self.cache.get('network', net)
                            for net in networks])
                    
                    result = update_or_create(
                        _netlink, ELEMENT_TYPES, check_mode=self.check_mode)
                    self.results['state'].append(result)
                    
                if self.check_mode:
                    return self.results
            
            else:        
                for element in self.elements:
                    for typeof in element:
                        if typeof not in ELEMENT_TYPES:
                            self.fail(msg='Element specified is not valid, got: {}, valid: {}'
                                .format(typeof, ELEMENT_TYPES.keys()))
                        else:
                            if not self.check_mode:
                                for elements in element[typeof]:
                                    result = delete_element(
                                        ELEMENT_TYPES.get(typeof)['type'](elements),
                                        self.ignore_err_if_not_found)
                                    self.results['state'].append(result)

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        for results in self.results['state']:
            if 'action' in results:
                self.results['changed'] = True
                break 
        return self.results
    
    def to_be_created_elements(self):
        """
        Get a dict of all elements that are to be created by this playbook.
        This is used when nested elements are being created that have
        requirements on other elements. This allows nested elements to be
        created alongside of their dependency.
        
        :return: dict of element by type: set([names]) to be created
        :rtype: dict
        """
        nested_element = ('netlink', 'group')
        to_be_created = {} # dict of element by type: set([names]) to be created.
        for element in self.elements:
            for typeof, values in element.items():
                if typeof not in nested_element:
                    to_be_created.setdefault(typeof, set()).add(
                        values.get('name'))
        return to_be_created
        
    def enum_group_members(self, groups, pending_elements):
        """
        Check group membership. Groups reference only the type of element and
        the names of those members. If the element is being created, skip the
        existence check. If the member is not being created, attempt to fetch
        the member and save to cache. Return the cache. Check cache.missing
        before continuing to ensure all required elements are found.
        
        :param list groups: list of groups extracted from elements
        :param dict pending_elements: elements waiting to be created
        :return: None
        """
        for group in groups:
            members = group.get('group', {}).get('members', {})
            members = {} if members is None else members
            for typeof, member in members.items():
                for name in member:
                    if name not in pending_elements.get(typeof, set()):
                        self.cache._add_entry(typeof, name)
    
    def enum_netlink_members(self, netlinks, pending_elements):
        """
        Netlinks reference nested elements gateway and networks. Attempt to
        locate these either in definitions to be created by this playbook or
        existing already in SMC. Populate cache with href and name map and
        catch any missing before continuing.
        
        :return: None
        """
        for netlink in netlinks:
            values = netlink.get('netlink', [])
            for req in ('gateway', 'network'):
                if req not in values:
                    self.fail(msg='Netlink requires a gateway and list of networks, '
                        'received: %s' % values)
            # Add requirements to cache
            gateway = values['gateway']
            if not isinstance(gateway, dict) or 'name' not in gateway or 'type' not in gateway:
                self.fail(msg='Netlink gateway must be a dict with a name and type key value: %s'
                    % gateway)
            
            if gateway.get('type') not in ('engine', 'router'):
                self.fail(msg='Netlink types can only be of type engine or router, got: %s' %
                    gateway.get('type'))
            
            networks = values['network']
            if not isinstance(networks, list):
                self.fail(msg='Netlink networks must be defined as a list, got: %s' % type(networks))
            
            if gateway.get('name') not in pending_elements.get(gateway.get('type'), set()):
                self.cache._add_entry(gateway.get('type'), gateway.get('name'))
            
            for network in networks:
                if network not in pending_elements.get('network', set()):
                    self.cache._add_entry('network', network)
            
            for attr in ('probe_address', 'domain_server_address'):
                if attr in values and not isinstance(values.get(attr), list):
                    self.fail(msg='%s must be in list format' % attr)


def main():
    NetworkElement()
    
if __name__ == '__main__':
    main()