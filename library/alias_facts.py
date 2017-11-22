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
short_description: Resolve and engine alias to value
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
  - smc-python >= 0.5.7
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Retrieve all NAT entries
  alias_facts:
    limit: 0

- name: resolve all NAT aliases for engine myfirewall
  alias_facts:
    limit: 0
    engine: myfirewall
    exact_match: no
    case_sensitive: no

- name: Resolve any aliases with keyword nat for engine sg_vm
  alias_facts:
    limit: 0
    filter: nat
    engine: sg_vm
    exact_match: no
    case_sensitive: no
'''


RETURN = '''
aliases: 
    description: Resolve NAT alias to firewall engine sg_vm
    returned: always
    type: list
    sample: [
        {
            "name": "$$ Interface ID 0.ip", 
            "resolved_value": [
                "10.10.0.1"
            ], 
            "type": "interface_nic_x_ip_alias"
        }, 
        {
            "name": "$$ Interface ID 0.net", 
            "resolved_value": [
                "10.10.0.0/24"
            ], 
            "type": "interface_nic_x_net_alias"
        }
    ]
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
        elem.update(resolved_value=alias.resolve(engine))
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
                fw = Engine.get(self.engine)
            except ElementNotFound:
                self.fail(
                    msg='Specified engine was not found: {}. Called from: {}'
                    .format(self.engine, self.__class__.__name__))
        
        if self.engine and not self.filter:
            result = list(fw.alias_resolving())
            aliases = [{'name': alias.name, 'type': alias.typeof, 'resolved_value': alias.resolved_value}
                       for alias in result]
    
        else:
                    
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