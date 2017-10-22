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
module: alias_facts
short_description: Facts about aliases mapped to engines
description:
  - Aliases are dynamic elements that have different values based on the
    engine the alias is applied on. This module allows you to retrieve
    aliases and retrieve their mappings.
version_added: '2.5'

options:
  engine:
    description:
      - Engine to retrieve for alias mapping
    required: false
    type: str
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Retrieve all NAT entries
  alias_facts:
    limit: 0

- name: Resolve any NAT aliases to firewall sg_vm
  alias_facts:
    limit: 0
    filter: nat
    engine: sg_vm
    exact_match: no
    case_sensitive: no
'''


RETURN = '''
aliases:
    description: List of all aliases, no filter
    returned: always
    type: list
    example: [
        {
        "name": "$$ Interface ID 46.net", 
        "type": "interface_nic_x_net_alias"
        }, 
        {
        "name": "$$ Interface ID 45.net", 
        "type": "interface_nic_x_net_alias"
    }]

aliases: 
    description: Resolve NAT alias to firewall engine sg_vm
    returned: always
    type: list
    example: [
        {
        "comment": "Default NAT Address depends on Routing View.", 
        "name": "$$ Default NAT Address", 
        "type": "default_nat_address_alias", 
        "values": [
            "10.0.0.254"
            ]
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.elements.network import Alias
    from smc.core.engine import Engine
    from smc.api.exceptions import ElementNotFound
except ImportError:
    pass


def alias_dict_from_obj(alias, engine):
    """
    Return dict of alias data. If engine is provided, resolve
    the values for the dict.
    
    :param Alias alias
    :param Engine engine
    """
    elem = {
        'name': alias.name,
        'type': alias.typeof,
        'comment': getattr(alias, 'comment', None)}
    
    if engine:
        elem.update(values=alias.resolve(engine))
    return elem
    

class AliasFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            engine=dict(type='str')
        )

        self.engine = None
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                aliases=[]
            )
        )
        
        super(AliasFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        # Verify the engine specified
        if self.engine:
            try:
                Engine.get(self.engine)
            except ElementNotFound:
                self.fail(
                    msg='Specified engine was not found: {}. Called from: {}'
                    .format(self.engine, self.__class__.__name__))
                
        result = self.search_by_type(Alias)
        
        if self.filter:
            aliases = [alias_dict_from_obj(alias, self.engine) for alias in result]
        else:
            aliases = [{'name': alias.name, 'type': alias.typeof} for alias in result]
        
        self.results['ansible_facts'] = {'aliases': aliases}
        return self.results

def main():
    AliasFacts()
    
if __name__ == '__main__':
    main()