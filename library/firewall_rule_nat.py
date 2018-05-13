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
module: firewall_rule
short_description: Create, modify or delete a firewall rule
description:
  - Firewall rules can be added or removed from either a top level policy
    or a sub-policy. Source, destination and service elements can be used and
    referenced by their type and name (they must be pre-created). Many other
    rule settings are possible, including logging, inspection and connection
    tracking settings. 

version_added: '2.5'
'''
