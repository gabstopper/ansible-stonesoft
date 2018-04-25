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
module: service_element
short_description: Create, modify or delete service elements
description:
    - Each service type currently supported in this module is documented as a suboption.
      Each service element type will have a minimum number of arguments
      that are required to create the element if it does not exist. Service elements
      supported by this module have their `create` constructors documented at
      U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements).
      This module uses a 'update or create' logic, therefore it is not possible to create
      the same element twice. If the element exists and the attributes provided are 
      different, the element will be updated before returned. It also means this module can
      be run multiple times with only slight modifications to the playbook. This is useful
      when an error is seen with a duplicate name, etc and you must re-adjust the playbook
      and re-run. For groups, members must be referenced by type and name. Members can be
      services that are also being created by the same playbook. If running in check_mode,'
      only fetches will be performed and the state attribute will indicate if an element is
      not found (i.e. would need to be created).

version_added: '2.5'

options:
  elements:
    description:
      - A list of the elements to create, modify or remove
    type: list
    required: true
    suboptions:
      tcp_service:
        description:
          - A TCP related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          min_dst_port:
            description:
              - Starting port for this service. Required.
            type: str
            required: true
          max_dst_port:
            description:
              - Top level port for this service. Required for defining a port range.
            type: str
      udp_service:
        description:
          - A UDP related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          min_dst_port:
            description:
              - Starting port for this service. Required.
            type: str
            required: true
          max_dst_port:
            description:
              - Top level port for this service. Required for defining a port range.
            type: str
      ip_service:
        description:
          - An IP based related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          protocol_number:
            description:
              - IP protocol number for the service
            type: str
            required: true
      ethernet_service:
        description:
          - An Ethernet related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          frame_type:
            description:
              - Frame type for this service
            type: str
            choices:
              - eth2
              - llc
              - snap
            required: true
          value1:
            description:
              - The hex string code for protocol 
            type: str
            required: true
      icmp_service:
        description:
          - An ICMP related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          icmp_type:
            description:
              - ICMP type field
            type: str
            required: true
          icmp_code:
            description:
              - ICMP type code
            type: str
            required: true
      icmp_ipv6_service:
        description:
          - An ICMP related service
        type: dict
        suboptions:
          name:
            description:
              - Name of this service element
            type: str
            required: true
          icmp_type:
            description:
              - ICMPv6 type field
            type: str
            required: true
      tcp_service_group:
        description:
          - A group of TCP services
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of members by service element, either the name field must be
                defined or the name and optional parts to create the element
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
      service_group:
        description:
          - A group of service elements of any service type
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of members by service element, either the name field must be
                defined or the name and optional parts to create the element
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
      udp_service_group:
        description:
          - A group of service elements of UDP services
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of members by service element, either the name field must be
                defined or the name and optional parts to create the element
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
      icmp_service_group:
        description:
          - A group of service elements of ICMP services
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of members by service element, either the name field must be
                defined or the name and optional parts to create the element
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
      ip_service_group:
        description:
          - A group of service elements of IP services
        type: dict
        suboptions:
          name: 
            description:
              - Name of this group element
            type: str
            required: true
          members:
            description:
              - A list of members by service element, either the name field must be
                defined or the name and optional parts to create the element
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
- name: Example service element creation
  register: result
  service_element:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    elements:
      - tcp_service: 
          name: myservice
          min_dst_port: 8080
          max_dst_port: 8100
      - tcp_service:
          name: newservice80
          min_dst_port: 80
      - udp_service:
          name: myudp
          min_dst_port: 8090
          max_dst_port: 8091
          comment: created by dlepage
      - udp_service:
          name: udp2000
          min_dst_port: 2000
      - ip_service:
          name: new service
          protocol_number: 8
          comment: custom EGP service
      - ethernet_service:
          name: 8021q frame
          frame_type: eth2
          value1: "0x8100"
      - icmp_service:
          name: custom icmp
          icmp_type: 3
          icmp_code: 7
          comment: custom icmp services
      - icmp_ipv6_service:
          name: my v6 icmp
          icmp_type: 139
          comment: Neighbor Advertisement Message
      - tcp_service_group:
          name: mygroup
          members:
              tcp_service:
              - newservice80
      - service_group:
          name: mysvcgrp
          members:
              tcp_service:
              - newservice80
              udp_service:
              - myudp
              - udp2000
              icmp_service:
              - custom icmp
      - udp_service_group:
          name: myudpservices
          members:
              udp_service:
              - myudp
              - udp2000
      - icmp_service_group:
          name: myicmp
          members:
              icmp_service:
              - custom icmp
      - icmp_service_group:
          name: myemptygroup
          members:
      - ip_service_group:
          name: myipservices
          members:
              ip_service:
              - new service

- name: Delete all service elements
  register: result
  service_element:
    smc_logging:
      level: 10
      path: /Users/davidlepage/Downloads/ansible-smc.log
    state: absent
    elements:
      - tcp_service_group:
          - mygroup
      - service_group:
          - mysvcgrp
      - udp_service_group:
          - myudp2000
      - icmp_service_group:
          - myicmp
      - ip_service_group:
          - myipservices
      - tcp_service: 
          - myservice
      - udp_service:
          - myudp
      - ip_service:
          - new service
      - ethernet_service:
          - 8021q frame
      - icmp_service:
          - custom icmp
      - icmp_ipv6_service:
          - my v6 icmp
'''

RETURN = '''
state:
    description: Current state of service elements
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
        }]
'''

import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase, Cache, service_type_dict,
    update_or_create, delete_element)


try:
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class ServiceElement(StonesoftModuleBase):
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
        super(ServiceElement, self).__init__(self.module_args, supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        ELEMENT_TYPES = service_type_dict()
        
        try:
            if state == 'present':
                # Retrieve naes of service groups
                group_types = [grp for grp in ELEMENT_TYPES.keys() if 'group' in grp]
                
                # Validate elements before proceeding.
                groups = []
                for element in self.elements:
                    self.is_element_valid(element, ELEMENT_TYPES)
                    for typeof in element:
                        if typeof in group_types:
                            groups.append(element)
                
                if groups:
                    cache = self.enum_group_members(groups, group_types)
                    if cache.missing:
                        self.fail(msg='Group members referenced are missing and are not being '
                            'created in this playbook: %s' % cache.missing)
                
                # Call update_or_create for elements that are NOT groups first
                for element in self.elements:
                    for typeof, _ in element.items():
                        if typeof not in group_types: # Groups are deferred
                            result = update_or_create(
                                element, ELEMENT_TYPES, check_mode=self.check_mode)
                            self.results['state'].append(result)
                        
                # Process groups now         
                for group in groups:
    
                    if self.check_mode:
                        result = update_or_create(group, ELEMENT_TYPES, check_mode=True)
                        self.results['state'].append(result)
                    
                    else:
                        # Run through cache again, entries that exist will not be
                        # added twice but this captures elements that might have been
                        # added earlier by the playbook run if they are not found
                        grouptype = group.keys()[0]
                        members = group.get(grouptype, {}).get('members', {})
                        if members:
                            cache.add_many([members])
                    
                            # Add to new members list
                            _members = [cache.get(typeof, value).href
                                for typeof, member in members.items()
                                for value in member]
                        else: # No members defined
                            _members = []

                        group.setdefault(grouptype, {}).update(
                            members=_members)
                        
                        result = update_or_create(group, ELEMENT_TYPES, check_mode=False)
                        if 'action' in result:
                            changed = True
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
                                    if 'action' in result:
                                        changed = True
                                    self.results['state'].append(result)
                                    
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def enum_group_members(self, groups, group_types):
        """
        Check group membership. Groups reference only the type of element and
        the names of those members. If the element is being created, skip the
        existence check. If the member is not being created, attempt to fetch
        the member and save to cache. Return the cache. Check cache.missing
        before continuing to ensure all required elements are found.
        
        :param list groups: list of groups extracted from elements
        :param list group_types: all supported group types by name
        :rtype: Cache
        """
        to_be_created = {} # dict of element by type: set([names]) to be created.
        
        # If groups reference elements that are to be created, skip validating.
        # Otherwise check for existence
        for element in self.elements:
            for typeof, values in element.items():
                if typeof not in group_types:
                    to_be_created.setdefault(typeof, set()).add(
                        values.get('name'))

        cache = Cache()
        for group in groups:
            for _, values in group.items():
                members = {} if values.get('members') is None else values['members']
                for typeof, member in members.items():
                    for name in member:
                        if name not in to_be_created.get(typeof, set()):
                            cache._add_entry(typeof, name)
        return cache
   

def main():
    ServiceElement()
    
if __name__ == '__main__':
    main()

