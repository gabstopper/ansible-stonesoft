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
module: bgp_element
short_description: BGP Elements for BGP configuratons
description:
  - BGP elements are the building blocks to building a BGP configuration on
    a layer 3 engine. Use this module to obtain available elements and their
    values.

version_added: '2.5'

options:
  elements:
    description:
      - List of device hashes/dictionaries with custom configurations based on the element type
      - >
        Valid elements include: ip_access_list, ip_prefix_list, ipv6_access_list, ipv6_prefix_list, 
        as_path_access_list, community_access_list, extended_community_access_list, external_bgp_peer,
        bgp_peering, autonomous_system. See the example bgp_element.yaml for a full list of
        supported parameters per item. Also see smc python documentation for routing elements 
        U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#dynamic-routing-elements)
    required: true
    type: list
  overwrite_existing:
    description:
      - Overwrite existing will replace the contents of the Access List type with the values provided
        in the element configuration. Otherwise operations will be update_or_create, where an update
        will add new entries if they do not exist or fully create and add entries if the acl doesnt
        exist. To replace entries you should fully define the access list and set overwrite_existing
        to true.
    type: bool
    default: false
  state:
    description:
      - Create or delete a BGP Element. If I(state=absent), the element dict must have at least the
        type of element and name field as a valid value.
    required: false
    default: present
    choices:
      - present
      - absent


extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Create all BGP element types
  register: result
  bgp_element:
    smc_logging:
      level: 10
      path: ansible-smc.log
    elements:
      - ip_access_list: 
          name: myservice2
          comment: my ip acl without min and max prefix length
          entries: 
            - subnet: 1.1.3.0/24
              action: permit
            - subnet: 2.2.2.0/24
              action: deny
      - ip_prefix_list:
          name: aprefix
          comment: prefix lists without min and max prefix
          entries:
            - subnet: 10.0.0.0/8
              action: deny
            - subnet: 192.16.2.0/24
              action: permit
      - ipv6_access_list:
          name: myipv6acl
          comment: an ipv6 acl
          entries:
            - subnet: '2001:db8:1::1/128'
              action: permit
      - ipv6_prefix_list:
          name: ipv6prefix
          entries:
            - subnet: 'ab00::/64'
              min_prefix_length: 65
              max_prefix_length: 128
              action: deny
      - as_path_access_list:
          name: mytestaccesslist
          comment: an as path
          entries:
            - expression: '123-456'
              action: permit
            - expression: '1234-567'
              action: deny
      - community_access_list:
          name: cmtyacl
          type: standard
          comment: my community
          entries:
            - community: '123'
              action: permit
            - community: '456'
              action: deny
      - extended_community_access_list:
          name: extcommacl
          type: standard
          comment: Some acl
          entries:
            - community: '123'
              action: permit
              type: rt
            - community: '456'
              action: deny
              type: soo
      - bgp_peering:
          name: extpeer
          comment: my peering
      - external_bgp_peer:
          name: mypeer666
          neighbor_as: myas123
          neighbor_ip: 12.12.12.12
          #neighbor_port: 179
          comment: mypeer
      - autonomous_system:
          name: myas123
          as_number: '123.123'
          comment: foo comment
    #state: absent
    #overwrite_existing: true
    
- name: Update an existing IP Access List and overwrite all entries
  register: result
  bgp_element:
    smc_logging:
      level: 10
      path: ansible-smc.log
    elements:
      - ip_access_list: 
          name: myservice2
          comment: my ip acl
          entries: 
            - subnet: 1.1.4.0/24
              action: permit
            - subnet: 2.2.2.0/24
              action: deny
      overwrite_existing: true
      
- name: Delete an IP Access List by name
  register: result
  bgp_element:
    smc_logging:
      level: 10
      path: ansible-smc.log
    elements:
      - ip_access_list: 
          name: myservice2
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: Full json definition of NGFW
  returned: always
  type: list
  sample: [
      {
        "action": "created", 
        "name": "myservice2", 
        "type": "ip_access_list"},
      {
        "action": "modified", 
        "name": "myservice2", 
        "type": "ip_access_list"},
      {
        "action": "deleted", 
        "name": "myservice2", 
        "type": "ip_access_list"
      }
    ]        
'''


import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase
from smc.routing.bgp import AutonomousSystem


try:
    from smc.base.model import lookup_class
    from smc.api.exceptions import SMCException
except ImportError:
    pass


"""
Access Lists require the entries parameter and specific attributes depending on
the access list type. These are used to validate the input prior to using for
creating.
"""
access_lists = {
    'ip_prefix_list': ['subnet', 'action'],
    'ipv6_prefix_list': ['subnet', 'action'],
    'ip_access_list': ['subnet', 'action'],
    'ipv6_access_list': ['subnet', 'action'],
    'as_path_access_list': ['expression', 'action'],
    'community_access_list': ['community', 'action'],
    'extended_community_access_list': ['community', 'action', 'type']
}
    
    
bgp_elements = (
    'ip_access_list', 'ip_prefix_list', 'ipv6_access_list',
    'ipv6_prefix_list', 'as_path_access_list', 'community_access_list',
    'extended_community_access_list', 'external_bgp_peer', 'bgp_peering',
    'autonomous_system'
)



class StonesoftBGPElement(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            elements=dict(type='list', required=True),
            overwrite_existing=dict(type='bool', default=False),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        self.elements = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftBGPElement, self).__init__(self.module_args, supports_check_mode=True)
        
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:
            if state == 'present':
                
                self.check_elements()
                
                # Defer ExternalBGPPeer as it's dependent on having a valid
                # AutonomousSystem element, but only if the AS doesn't already exist
                deferrals, elements = self.resolve_references(self.elements)
                
                if self.check_mode:
                    return self.results
                
                for element in elements:
                    if self.create_or_update_element(element):
                        changed = True
                
                if deferrals:
                    _, bgp_peers = self.resolve_references(deferrals)
                    for element in bgp_peers:
                        if self.create_or_update_element(element):
                            changed = True
                
            else:
                # No need to validate elements beyond type and name
                for element in self.elements:
                    for typeof, values in element.items():
                        klazz = lookup_class(typeof)
                        name = values.get('name')
                        if name:
                            try:
                                klazz(name).delete()
                                self.results['state'].append(
                                    {'name': name, 'type': klazz.typeof, 'action': 'deleted'})
                                changed = True
                            except SMCException as e:
                                self.results['state'].append(
                                    {'name': name, 'type': klazz.typeof, 'action': 'failed to delete '
                                     'with reason: %s' % str(e)})
            
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results 
    
    def create_or_update_element(self, element):
        """
        Create the element. 
        
        :param dict element: the element dict from elements
        """
        changed = False
        for typeof, values in element.items():
            klazz = lookup_class(typeof)
            
            if ('access_list' in klazz.typeof or 'prefix_list' in klazz.typeof)\
                and self.overwrite_existing:
            
                obj, modified, created = klazz.update_or_create(
                    with_status=True, overwrite_existing=True, **values)
            else:
                obj, modified, created = klazz.update_or_create(
                    with_status=True, **values)
            
            if created:
                self.results['state'].append(
                    {'name': obj.name, 'type': obj.typeof, 'action': 'created'})
            elif modified:
                self.results['state'].append(
                    {'name': obj.name, 'type': obj.typeof, 'action': 'modified'})
            changed = created or modified
        return changed    
        
    def resolve_references(self, elementlist):
        """
        Some elements have a dependency on another element being
        created. Check for those elements here and defer their
        creation until the end if the dependency is also being created.
        
        :rtype: tuple(list, list)
        """
        deferrals, elements = ([] for i in range(2))
        for element in elementlist:
            if 'external_bgp_peer' in element:
                value = element.get('external_bgp_peer')
                neighbor = value.get('neighbor_as')
                if not self.dependency_being_created(elementlist, 'autonomous_system', neighbor):
                    as_system = AutonomousSystem.get(neighbor, raise_exc=False)
                    if not as_system:
                        self.fail(msg='Autonomous System: %r referenced in external_bgp_peer: '
                            'cannot be found and is not being created by this task: %s' %
                            (neighbor, value))
                    else:
                        value.update(neighbor_as=as_system.href)
                else:
                    deferrals.append(element)
                    continue
            elements.append(element)
        return deferrals, elements

    def dependency_being_created(self, elementlist, typeof, name):
        """
        Check whether the specified dependency element type is in the
        list to be created or not. If this returns False, the dependency
        should be fetched to verify it exists before creating the element
        that requires it. Element list is the supported element format.
        
        :param list elementlist: list of elements to check for dependency
        :param str typeof: valid bgp element typeof
        :param str name: name to find
        :rtype: bool
        """
        for element in elementlist:
            if typeof in element:
                value = element.get(typeof)
                if value.get('name') == name:
                    return True
        return False

    def check_elements(self):
        """
        Check the elements for validity before continuing. 
        Only return elements that can be processed without being
        deferred due to references.
        
        :rtype: list
        """
        for element in self.elements:
            if not isinstance(element, dict):
                self.fail('BGP element type must be defined as a dict, received: '
                    '%s, type: %s' % (element, type(element)))
            for bgp_element, values in element.items():
                if bgp_element not in bgp_elements:
                    self.fail(msg='BGP element type specified is not a supported '
                        'element type, provided: %s. Valid values: %s' %
                        (bgp_element, list(bgp_elements)))
                if not isinstance(values, dict):
                    self.fail(msg='Element values must be of type dict. Received '
                        'values: %s of type: %s' % (values, type(values)))
                
                if 'name' not in values:
                    self.fail(msg='Name is a required field when creating or '
                        'modifying an element. Missing on defintion: %s' % bgp_element)
                
                if 'access_list' in bgp_element:
                    # Check that all entry values are valid
                    entries = values.get('entries')
                    if not entries:
                        self.fail(msg='You must specify at least one value in entries '
                            'to create an access list of any type: %s' % bgp_element)
        
                    required = set(access_lists.get(bgp_element))
                    for specified in entries:
                        if set(specified.keys()) ^ required:
                            self.fail(msg='Missing required fields for the access list: %s. '
                                'Received: %s, required values: %s' % (bgp_element, specified,
                                list(required)))
                    
                    # Use a standard vs. expanded ACL if not specified        
                    if 'community' in bgp_element and 'type' not in values:
                        values.update(type='standard')

                elif 'external_bgp_peer' in bgp_element:
                    for required in ('neighbor_as', 'neighbor_ip'):
                        if required not in values or not values.get(required):
                            self.fail(msg='External BGP definition is missing neighbor_as '
                                'or neighbor_ip value, received: %s' % values)

                elif 'autonomous_system' in bgp_element:
                    if 'as_number' not in values or not values.get('as_number'):
                        self.fail(msg='Autonomous system requires an as_number be set: %s'
                            % values)

    
def main():
    StonesoftBGPElement()
    
if __name__ == '__main__':
    main()

        
        