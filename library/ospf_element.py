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
module: ospf_element
short_description: OSPF Elements used in engine configurations
description:
  - OSPF elements are the building blocks to building an OSPF configuration on
    a layer 3 engine. Use this module to obtain available elements and their
    values.

version_added: '2.5'

options:
  elements:
    description:
      - List of OSPF related elements to create within the SMC. The list contain dicts representing
        valid OSPF element types as the key, and nested dict should be valid attributes of that
        OSPF element type.
      - >
        Valid elements include: ospfv2_area, ospf_profile 
        U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#module-smc.routing.ospf)
    required: true
    type: list
    suboptions:
      ospvfv2_area:
        description:
          - Create an OSPFv2 area element to be used on an routing interface to advertise OSPF.
            Suboptions describe key value pairs for area dict
        type: dict
        suboptions:
          name:
            description:
              - Name of the OSPF Area
            type: str
            required: true
          area_type:
            description:
              - OSPF area type for this element
            type: str
            default: normal
          comment:
            description:
              - Optional description
            type: str
          inbound_filters:
            description:
              - Inbound IP access list and or IP Prefix List to apply to this OSPF area.
                Key should be a valid choice and value is name of IP access list or IP prefix
                list
            type: dict
            choices:
            - ip_access_list
            - ip_prefix_list
          outbound_filters:
            description:
              - Outbound IP access list and or IP prefix list to apply to this OSPF area.
                Key should be a valid choice and value is name of IP access list or IP prefix
                list
            type: dict
            choices:
            - ip_access_list
            - ip_prefix_list  
          interface_settings_ref:
            description:
              - Name of the interface settings element for this OSPF area
            type: str
            default: Default OSPFv2 Interface Settings
      ospfv2_profile:
        description:
          - An OSPF profile defines how an OSPF area should behave with respects to redistributing
            routes between adjacent areas
        type: dict
        suboptions:
          name:
            description:
              - Name of OSPF profile
            type: str
            required: true   
          comment:
            description:
              - optional comment
            type: str
          default_metric:
            description:
              - Default metric to use for redistributed routes
            type: int   
          domain_settings_ref:
            description:
              - The default OSPF domain settings element referenced by this OSPF profile
            type: str
            default: Default OSPFv2 Domain Settings
          external_distance:
            description: 
              - External distance metric used by this OSPF profile
            type: int
            default: 110
          inter_distance:
            description:
              - inter distance metric used by this OSPF profile
            type: int
            default: 110
          intra_distance:
            description:
              - intra distance metric used by this OSPF profile
            default: 110
          redistribution_entry:
            description:
              - List of dicts describing how routes should be redistributed through OSPF
                Each redistribution type can have an optional filter which is either a
                route map or IP access list
            type: list
            suboptions:
              enabled:
                description:
                  - Enable route redistribution for this route type
                type: bool
              metric_type:
                description:
                  - Metric type for this route type
                choices:
                - external_1
                - external_2
              type:
                description:
                  - Area of which to redistrbute routes from
                type: str
                choices:
                - bgp
                - static
                - connected
                - kernel
                - default_originate
              filter:
                description:
                  - Optional IP Access List or Route Map to apply to redistribution. Key for
                    must be either ip_access_list or route_map. Value is list of name value for
                    pre-existing element. You can provide empty dict brackets to unset an existing
                    IP access list or route map
                type: dict
  state:
    description:
      - Create or delete an OSPF Element. If I(state=absent), the element dict must have at least the
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
- name: OSPF Elements
  register: result
  ospf_element:
    elements:
    - ospfv2_area:
        area_type: normal
        comment: null
        inbound_filters:
          ip_access_list:
          - myacl22
          ip_prefix_list:
          - mylist2
        interface_settings_ref: Default OSPFv2 Interface Settings
        name: myarea2
        outbound_filters:
          ip_access_list:
          - myservice
    - ospfv2_profile:
        comment: added by ansible
        default_metric: 123
        domain_settings_ref: Default OSPFv2 Domain Settings
        external_distance: 110
        inter_distance: 130
        intra_distance: 110
        name: myprofile
        redistribution_entry:
        - enabled: true
          metric_type: external_1
          type: bgp
        - enabled: true
          filter:
            route_map:
            - myroutemap
          metric: 2
          metric_type: external_1
          type: static
        - enabled: true
          filter:
            ip_access_list:
            - myacl
          metric_type: external_2
          type: connected
        - enabled: false
          metric_type: external_1
          type: kernel
        - enabled: false
          metric_type: external_1
          type: default_originate
    #state: absent
 
- name: Unset an existing redistributed route ip access list or route map
  register: result
  ospf_element:
    elements:   
    - ospfv2_profile:
      name: myprofile
      redistribution_entry:
      - enabled: true
        metric_type: external_1
        type: bgp
      - enabled: true
        filter: {}
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
        "name": "myarea2", 
        "type": "ospfv2_area"
        }, 
        {
        "action": "created", 
        "name": "myprofile", 
        "type": "ospfv2_profile"
        },
        {
        "action": "deleted", 
        "name": "myarea2", 
        "type": "ospfv2_area"
        }, 
        {
        "action": "failed to delete with reason: Cannot find specified element: myprofile, type: ospfv2_profile", 
        "name": "myprofile", 
        "type": "ospfv2_profile"
        }
    ]        
'''

import copy
import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, allowed_args, Cache


try:
    from smc.base.model import lookup_class
    from smc.api.exceptions import SMCException
except ImportError:
    pass


ospf_elements = ('ospfv2_area', 'ospfv2_interface_settings', 'ospfv2_key_chain',
    'ospfv2_profile', 'ospfv2_domain_settings')


class StonesoftOSPFElement(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            elements=dict(type='list', required=True),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        self.elements = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftOSPFElement, self).__init__(self.module_args, supports_check_mode=True)
        
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:
            if state == 'present':
                
                self.cache = Cache()
                self.check_elements()
                
                # Any missing dependencies..
                if self.cache.missing:
                    self.fail(msg='Missing dependent elements that are not created within this '
                        'playbook: %s' % self.cache.missing)
                
                deferrals, elements = self.resolve_references(self.elements)
                if self.cache.missing:
                    self.fail(msg='Missing elements that have a dependency, cannot continue: %s'
                        % self.cache.missing)
                 
                if self.check_mode:
                    return self.results
                
                for element in elements:
                    if self.create_or_update_element(element):
                        changed = True

                if deferrals:
                    _, ospf_elements = self.resolve_references(deferrals)
                    for element in ospf_elements:
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
                                result = {'name': name, 'type': klazz.typeof, 'action': 'deleted'}
                                changed = True
                            except SMCException as e:
                                result = {'name': name, 'type': klazz.typeof, 'action': 'failed to delete '
                                    'with reason: %s' % str(e)}
                            finally:
                                self.results['state'].append(result)
    
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results 
    
    def serialize_fields(self, typeof, element_values):
        """
        Serialize fields to fit into the update_or_create constructors
        for the relevant types.
        
        :param str typeof: ospf element type
        :param dict element_values: values for dict from yaml
        :return: serialized dict for update_or_create
        """
        new_values = copy.deepcopy(element_values)
        if 'ospfv2_profile' in typeof:
            for entry in new_values.get('redistribution_entry', []):
                if 'filter' in entry:
                    if not entry.get('filter'): # Empty, clear existing
                        entry.update(filter=[])
                    else:
                        for typeof, value in entry.pop('filter', {}).items():
                            # Get element from cache
                            entry.update(filter=
                                self.cache.get(typeof, value[0]))
            
            if 'domain_settings_ref' in element_values:
                new_values.update(domain_settings_ref=
                    self.cache.get_href('ospfv2_domain_settings', element_values.get(
                        'domain_settings_ref')))
                
        elif 'ospfv2_area' in typeof:
            if 'interface_settings_ref' in new_values:
                new_values.update(
                    interface_settings_ref=self.cache.get_href('ospfv2_interface_settings',
                    new_values.pop('interface_settings_ref')))
    
            for _filter in ('inbound_filters', 'outbound_filters'):
                if _filter in new_values:
                    if not new_values.get(_filter): # Empty, clear existing
                        new_values[_filter] = []
                    else:
                        for k, value in new_values.pop(_filter, {}).items():
                            new_values.setdefault(_filter, []).append(
                                self.cache.get_href(k, value[0]))
        return new_values
        
    def create_or_update_element(self, element):
        """
        Create the element. 
        
        :param dict element: the element dict from elements
        """
        changed = False
        for typeof, values in element.items():
            klazz = lookup_class(typeof)
            
            s_values = self.serialize_fields(typeof, values)
            obj, modified, created = klazz.update_or_create(
                with_status=True, **s_values)
            
            if created or modified:
                self.results['state'].append(
                    {'name': obj.name, 'type': obj.typeof, 'action': 'created'
                        if created else 'modified'})
            
            changed = created or modified
        return changed    
        
    def resolve_references(self, elementlist):
        """
        Some elements have a dependency on another element being
        created. Check for those elements here and defer their
        creation until the end if the dependency is also being created.
        
        :rtype: tuple(list, list)
        """
        deferrals, elements = [], []
        for element in elementlist:
            if 'ospfv2_area' in element:
                area = element['ospfv2_area']
                if area.get('interface_settings_ref'):
                    if not self.dependency_being_created(
                        elementlist, 'ospfv2_interface_settings', area['interface_settings_ref']):
                        self.cache._add_entry('ospfv2_interface_settings', area['interface_settings_ref'])
                    else:
                        deferrals.append(element)
                        continue
        
            elif 'ospfv2_profile' in element:
                profile = element['ospfv2_profile']
                if profile.get('domain_settings_ref'):
                    if not self.dependency_being_created(
                        elementlist, 'ospfv2_domain_settings', profile['domain_settings_ref']):
                        self.cache._add_entry('ospfv2_domain_settings', profile['domain_settings_ref'])
                    else:
                        deferrals.append(element)

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
                self.fail('OSPF element type must be defined as a dict, received: '
                    '%s, type: %s' % (element, type(element)))

            for ospf_element, values in element.items():
                if ospf_element not in ospf_elements:
                    self.fail(msg='OSPF element type specified is not a supported '
                        'element type, provided: %s. Valid values: %s' %
                        (ospf_element, list(ospf_elements)))
                if not isinstance(values, dict):
                    self.fail(msg='Element values must be of type dict. Received '
                        'values: %s of type: %s' % (values, type(values)))
                
                if 'name' not in values:
                    self.fail(msg='Name is a required field when creating or '
                        'modifying an element. Missing on definition: %s' % ospf_element)
                
                # Check each value against what the constructor requires
                allowed = allowed_args(ospf_element)
                for value in values:
                    if value not in allowed:
                        self.fail(msg='Provided an argument that is not valid for this '
                            'element type. Argument: %s, element type: %s, valid args: %s'
                             % (value, ospf_element, allowed))
                
                # Redistribution entries must exist as they are not created in this module
                if ospf_element == 'ospfv2_profile':
                    for redist in values.get('redistribution_entry', []):
                        for _type, _val in redist.get('filter', {}).items():
                            if _type not in ('ip_access_list', 'route_map'):
                                self.fail(msg='Redistribution entry filters must be either '
                                    'ip_access_list or route_map, received: %s' % _type)
                            self.cache.add(redist['filter'])
                
                elif ospf_element == 'ospfv2_area':
                    for _filter in ('inbound_filters', 'outbound_filters'):
                        if _filter in values:
                            for k, v in values.get(_filter).items():
                                if k not in ('ip_access_list', 'ip_prefix_list'):
                                    self.fail(msg='%s type invalid. Supported filters must '
                                        'be of type ip_access_list or ip_prefix_list. Received '
                                        '%s' % (_filter, k))
                                self.cache.add({k: v})

    
def main():
    StonesoftOSPFElement()
    
if __name__ == '__main__':
    main()
