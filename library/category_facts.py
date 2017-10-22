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
module: category_facts
short_description: Facts about category tag elements in the SMC
description:
  - Category tags can be added to most elements in the SMC to identify elements
    and for grouping purposes.
version_added: '2.5'
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Return all categories
    category_facts:

- name: Return all categories and references for categories containing 'smc'
    category_facts:
      limit: 5
      filter: smc

- name: Return category information matching 'smc-python'.
    category_facts:
      limit: 1
      filter: smc-python
      exact_match: yes
      case_sensitive: yes
'''


RETURN = '''
categories:
    description: Return all categories
    returned: always
    type: list
    example: [{
        "name": "aws", 
        "type": "category_tag"}, 
        {
        "name": "foocategory", 
        "type": "category_tag"
    }]

categories:
    description: Return categories and references using 'smc' as filter
    returned: always
    type: list
    example: [{
        "comment": null, 
        "name": "smc-python", 
        "references": [{
            "name": "172.18.1.135", 
            "type": "host"
            }], 
            "type": "category_tag"
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.elements.other import Category
except ImportError:
    pass


def category_dict_from_obj(element):
    """
    Resolve the category to the supported types and return a dict
    with the values of defined attributes
    
    :param Element element
    """
    elem = {
        'name': element.name,
        'type': element.typeof,
        'references': [],
        'comment': getattr(element, 'comment', None)}
    
    for reference in element.search_elements():
        elem['references'].append(
            {'name': reference.name, 'type': reference.typeof})
    
    return elem


class CategoryFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.element = 'category'
        self.limit = None
        self.filter = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                categories=[]
            )
        )
        
        super(CategoryFacts, self).__init__({}, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = self.search_by_type(Category)
        # Search by specific element type
        if self.filter:    
            elements = [category_dict_from_obj(element) for element in result]
        else:
            elements = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts'] = {'categories': elements}
        return self.results

def main():
    CategoryFacts()
    
if __name__ == '__main__':
    main()