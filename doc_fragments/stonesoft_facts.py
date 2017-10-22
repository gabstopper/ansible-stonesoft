#
# (c) 2017, David LePage (@gabstopper)
# Stonesoft Documentation fragment. This fragment specifies the top level
# requirements for obtaining a valid session to the Stonesoft Management
# Center. 

class ModuleDocFragment(object):
    # Standard Stonesoft documentation fragment
    DOCUMENTATION = '''
options:
  filter:
    description:
      - String value to match against when making query. Matches all if not specified.
        A filter will attempt to find a match in the name, primary key field or comment
        field of a given record.
    required: false
    default: '*'
    type: str
  limit:
    description:
      - Limit the number of results. Set to 0 to remove limit.
    required: false
    default: 10
    type: int
  exact_match:
    description:
      - Whether to do an exact match on the filter specified
    required: false
    default: false
  case_sensitive:
    description:
      - Whether to do a case sensitive match on the filter specified
    required: false
    default: true

notes:
  - If a filter is not used in the query, this will return all results for the
    element type. The return data in this case will only contain the meta data
    for the element which will be name and type.
'''
