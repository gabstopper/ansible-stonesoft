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
module: generic_element
short_description: Create, modify or delete elements inheriting from Element
description:
  - This module allows elements that inherit from smc.base.model.Element to be
    created, deleted or modified. Any valid smc-python element is one that has a
    direct entry point in the SMC API. In order to create an element, you must
    provide any attributes required by the elements create signature.
    This module uses an 'update or create' logic, therefore it is not possible to create
    the same element twice. If the element exists and the attributes provided are 
    different, the element will be updated before returned.

version_added: '2.5'

options:
  elements:
    description:
      - A list of the elements to create, modify or remove
    type: list
    required: true
    suboptions:
      element:
        description:
          - Specify the typeof attribute for the given element. This value is the API
            entry point that correlates to the given smc-python object instance
        type: dict
        suboptions:
          name:
            description:
              - Name of this host element
            type: str
            required: true
          kwargs:
            description:
              - Free flowing keyword arguments used to modify or create the element.
                Arg type values must conform to the create or update_or_create
                constructor for the element type
            type: complex
            required: false

extends_documentation_fragment:
  - stonesoft
 
requirements:
  - smc-python
author:
  - David LePage (@gabstopper)        
'''

EXAMPLES = '''
- name: Create a VPN Profile
  generic_element:
    smc_logging:
      level: 10
      path: ansible-smc.log
    elements:
    - vpn_profile: 
        name: MyVPNProfile
        comment: mycomment
        capabilities:
          aes256_for_ike: True
          aes256_for_ipsec: True
          dh_group_2_for_ike: True
          esp_for_ipsec: True
          ike_v2: True
          main_mode: True
          pre_shared_key_for_ike: True
          sa_per_net: True
          sha1_for_ike: True
          sha1_for_ipsec: True
          sha2_ike_hash_length: 256
          sha2_ipsec_hash_length: 256
          vpn_client_rsa_signature_for_ike: True
          vpn_client_sa_per_net: True
'''

RETURN = '''
changed:
  description: Whether or not an element was changed
  returned: always
  type: bool
state:
  description: Full json definition of NGFW
  returned: always
  type: list
  sample: [
    {
        "action": "none", 
        "name": "MyVPNProfile", 
        "typeof": "vpn_profile"
    }
]
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.api.exceptions import SMCException
    from smc.base.collection import Search
    from smc.base.model import lookup_class
except ImportError:
    pass


class GenericElement(StonesoftModuleBase):
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
        super(GenericElement, self).__init__(self.module_args, supports_check_mode=True)

    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)

        # Validate whether the element type is valid
        entry_points = Search.object_types()

        for element in self.elements:
            for typeof, element_data in element.items():
                if typeof not in entry_points:
                    self.fail(msg='The specified element type: %s is not valid. '
                        'Data provided: %s' % (typeof, element))
                if 'name' not in element_data:
                    self.fail(msg='The name field is required to operate on all '
                        'elements. Data provided: %s' % element)

        try:
            if self.check_mode:
                return self.results

            for element in self.elements:
                for typeof, data in element.items():
                    try:
                        instance, updated, created = lookup_class(typeof).update_or_create(
                            with_status=True, **data)

                        action = 'none'

                        if updated:
                            action = 'updated'
                        elif created:
                            action = 'created'

                        if updated or created:
                            self.results['changed'] = True

                        self.results['state'].append(dict(name=instance.name,
                            typeof=instance.typeof, action=action))

                    except SMCException as e:
                        self.results['state'].append(dict(name=data.get('name'),
                            typeof=typeof, action='error', reason=str(e)))

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())

        return self.results

def main():
    GenericElement()
    
if __name__ == '__main__':
    main()
