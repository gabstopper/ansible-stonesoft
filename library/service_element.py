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
    - Each service type currently supported in this module is documented in the example
      playbook. Each service element type will have a minimum number of arguments
      that is required to create the element if it does not exist. Service elements
      supported by this module have their `create` constructors documented at
      U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements).
      This module uses a 'update or create' logic, therefore it is not possible to create
      the same element twice. If the element exists and the attributes provided are 
      different, the element will be updated before returned. It also means this module can
      be run multiple times with only slight modifications to the playbook. This is useful
      when an error is seen with a duplicate name, etc and you must re-adjust the playbook
      and re-run. For groups, you can reference a member by name which will require it to
      exist, or you can also specify the required options and create the element if it doesn't
      exist. If running in check_mode, only fetches will be performed and the state attribute
      will indicate if an element is not found (i.e. would need to be created).

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
- name: Create a service element. Check smc-python documentation for required fields.
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Example service element and service group creation
    service_element:
      elements:
        - tcp_service: 
            name: myservice
            min_dst_port: 8080
            max_dst_port: 8100
        - udp_service:
            name: myudp
            min_dst_port: 8090
            max_dst_port: 8091
            comment: created by dlepage
        - ip_service:
            name: new service
            protocol_number: 8
            comment: custom EGP service
        - ethernet_service:
            name: myethernet service
            frame_type: eth2
            value1: 32828
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
              - tcp_service:
                  name: newservice80
                  min_dst_port: 80
        - service_group:
            name: mysvcgrp
            members:
              - tcp_service:
                  name: newservice80
        - udp_service_group:
            name: myudp2000
            members:
              - udp_service:
                  name: myudp
              - udp_service:
                  name: udp2000
                  min_dst_port: 2000
        - icmp_service_group:
            name: myicmp
            members:
              - icmp_service:
                  name: custom icmp
        - ip_service_group:
            name: myipservices
            members:
              - ip_service:
                  name: new service

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
            "comment": null, 
            "max_dst_port": null, 
            "min_dst_port": 8080, 
            "name": "myservice", 
            "type": "tcp_service"
        }, 
        {
            "comment": null, 
            "max_dst_port": 8091, 
            "min_dst_port": 8090, 
            "name": "myudp", 
            "type": "udp_service"
        }, 
        {
            "comment": "custom EGP service", 
            "name": "new service", 
            "protocol_number": "8", 
            "type": "ip_service"
        }, 
        {
            "comment": null, 
            "value1": null, 
            "frame_type": "eth2", 
            "name": "myethernet service", 
            "type": "ethernet_service"
        }, 
        {
            "comment": "custom icmp services", 
            "icmp_code": 7, 
            "icmp_type": 3, 
            "name": "custom icmp", 
            "type": "icmp_service"
        }, 
        {
            "comment": "Neighbor Advertisement Message", 
            "icmp_type": 139, 
            "name": "my v6 icmp", 
            "type": "icmp_ipv6_service"
        }, 
        {
            "comment": null, 
            "members": [
                "http://172.18.1.151:8082/6.4/elements/tcp_service/611"
            ], 
            "name": "mygroup", 
            "type": "tcp_service_group"
        }
    ]
'''

import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    service_type_dict,
    element_dict_from_obj,
    update_or_create,
    delete_element)


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
        
        if state == 'absent':
            for element in self.elements:
                for typeof in element:
                    if typeof not in ELEMENT_TYPES:
                        self.fail(msg='Element specified is not valid, got: {}, valid: {}'
                            .format(typeof, ELEMENT_TYPES.keys()))
                    else:
                        if not self.check_mode:
                            for elements in element[typeof]:
                                result = delete_element(
                                    ELEMENT_TYPES.get(typeof)['type'](elements), self.ignore_err_if_not_found)
                                if result:
                                    self.results['state'].append(result)
                                else:
                                    changed = True
        else:
            # Validate elements before proceeding
            for element in self.elements:
                self.is_element_valid(element, ELEMENT_TYPES)
        
            try:
                if state == 'present':
                    for element in self.elements:
                        for typeof, _ in element.items():
                            if 'group' in typeof:
                                result = self.update_group(element, ELEMENT_TYPES)
                            else:
                                result = update_or_create(
                                    element, ELEMENT_TYPES, check_mode=self.check_mode)
                        
                            if self.check_mode:
                                if result is not None:
                                    self.results['state'].append(result)
                            else:            
                                changed = True
        
                                self.results['state'].append(
                                    element_dict_from_obj(result, ELEMENT_TYPES))

            except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def update_group(self, group_dict, type_dict):
        """
        Process a group and it's members (if any). Each group member can
        be referenced by name only, or they can be created like a normal
        element nested in the group.
        
        :param dict group_dict: dict of group info
        :param dict type_dict: dict of all supported elements
        """
        members = []
        group_key = group_dict.keys().pop()
        g = group_dict.get(group_key)
        if g.get('members'):
            for member in g['members']:
                m = update_or_create(member, type_dict, check_mode=self.check_mode)
                if self.check_mode:
                    if m is not None:
                        members.append(m)
                else:
                    members.append(m.href)
    
        group_dict[group_key]['members'] = members
        result = update_or_create(group_dict, type_dict, check_mode=self.check_mode)
        if self.check_mode:
            if result is None and members:
                return group_dict
        return result

def main():
    ServiceElement()
    
if __name__ == '__main__':
    main()

