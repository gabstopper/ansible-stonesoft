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
    U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements). This module
    uses a 'get or create' logic, therefore it is not possible to create the same element
    twice, instead if it exists, it will be returned. It also means this module can be run
    multiple times with only slight modifications to the playbook. This is useful when an
    error is seen with a duplicate name, etc and you must re-adjust the playbook and re-run.
    For groups, you can reference a member by name which will require it to exist, or you
    can also specify the required options and create the element if it doesn't exist.

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
          secondary:
            description:
              - Optional secondary IP addresses for this host
            type: list
          comment:
            description:
              - Optional comment for this host
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
              - A list of members by network element, either the name field must be
                defined or the name and optional parts to create the element
            type: list

extends_documentation_fragment:
  - stonesoft
 
requirements:
  - smc-python
author:
  - David LePage (@gabstopper)        
'''

EXAMPLES = '''
- name: Create network elements. Check smc-python documentation for required fields.
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Example network element creation
    network_element:
      elements:
        - host: 
            name: myhost
            address: 1.1.1.1
            ipv6_address: 2001:0db8:85a3:0000:0000:8a2e:0370:7334
            secondary:
              - 1.1.1.2
              - 1.1.1.3
        - network:
            name: mynetwork
            ipv4_network: 1.1.1.0/24
            ipv6_network: fc00::/7
            comment: created by dlepage
        - address_range:
            name: myrange
            ip_range: 1.1.1.1-1.1.1.10
        - interface_zone:
            name: myzone
        - domain_name:
            name: google.com
        - router:
            name: myrouter
            address: 172.18.1.254
            secondary:
              - 172.18.1.253
            ipv6_address: 2003:dead:beef:4dad:23:46:bb:101
        - ip_list: 
            name: mylist
            iplist:
              - 1.1.1.1
              - 1.1.1.2
              - 1.1.1.3
              - 1.1.1.4
        - group: 
            name: group_referencing_existing_elements
            members:
              - host: 
                  name: grace
        - group:
            name: group_and_create_elements_that_dont_exist
            members:
              - host:
                  name: newhost
                  address: 1.1.1.1
'''

RETURN = '''
elements:
    description: All elements, no filter
    returned: always
    type: list
    sample: [
        {
            "address": "3.3.3.3", 
            "comment": null, 
            "ipv6_address": null, 
            "name": "myhost", 
            "secondary": [], 
            "type": "host"
        }, 
        {
            "comment": "created by dlepage", 
            "ipv4_network": "3.3.3.0/24", 
            "ipv6_network": "fc00::/7", 
            "name": "mynetwork_ipv6", 
            "type": "network"
        }, 
        {
            "comment": null, 
            "ip_range": "1.1.1.1-1.1.1.10", 
            "name": "myrange", 
            "type": "address_range"
        }, 
        {
            "comment": null, 
            "name": "myzone", 
            "type": "interface_zone"
        }, 
        {
            "comment": null, 
            "name": "google.com", 
            "type": "domain_name"
        }, 
        {
            "address": "172.18.1.254", 
            "comment": null, 
            "ipv6_address": "2003:dead:beef:4dad:23:46:bb:101", 
            "name": "myrouter", 
            "secondary": [
                "172.18.1.253"
            ], 
            "type": "router"
        }, 
        {
            "comment": null, 
            "iplist": null, 
            "name": "mylist2", 
            "type": "ip_list"
        },
        {
            "comment": null, 
            "members": [
                "http://172.18.1.151:8082/6.4/elements/host/672"
            ], 
            "name": "group_referencing_existing_elements", 
            "type": "group"
        }, 
        {
            "comment": null, 
            "members": [
                "http://172.18.1.151:8082/6.4/elements/host/705"
            ], 
            "name": "group_and_create_elements", 
            "type": "group"
        }
    ]
'''

import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    element_type_dict,
    element_dict_from_obj,
    get_or_create_element)


try:
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class NetworkElement(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            elements=dict(type='list', required=True),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
    
        self.elements = None
        
        self.results = dict(
            changed=False,
            state=[],
            elements=[]
        )
        super(NetworkElement, self).__init__(self.module_args, supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        ELEMENT_TYPES = element_type_dict()
        
        # Validate elements before proceeding
        for element in self.elements:
            self.is_element_valid(element, ELEMENT_TYPES)
        
        changed = False
        try:
            if state == 'present':
                for element in self.elements:
                    for typeof, _ in element.items():
                        if 'group' in typeof:
                            result = self.update_group(element, ELEMENT_TYPES)
                        else:
                            result = get_or_create_element(
                                element, ELEMENT_TYPES, check_mode=self.check_mode)
                        
                        if self.check_mode:
                            if result is not None:
                                self.results['state'].append(result)
                        else:            
                            changed = True
    
                            self.results['elements'].append(
                                element_dict_from_obj(result, ELEMENT_TYPES))
                    
            elif state == 'absent':
                pass

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
        g = group_dict.get('group')
        if g.get('members'):
            for member in g['members']:
                m = get_or_create_element(member, type_dict, check_mode=self.check_mode)
                if self.check_mode:
                    if m is not None:
                        members.append(m)
                else:
                    members.append(m.href)
                
        group_dict['group']['members'] = members
        result = get_or_create_element(group_dict, type_dict, check_mode=self.check_mode)
        if self.check_mode:
            if result is None and members:
                return group_dict
        return result


def main():
    NetworkElement()
    
if __name__ == '__main__':
    main()