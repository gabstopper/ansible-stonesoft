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
module: bgp
short_description: Create, modify or delete a BGP configuration on an engine.
description:
  - BGP is a supported dynamic protocol only on layer 3 FW engines. This module
    allows you to enable BGP and assign a specific BGP configuration to a specified
    engine. This module assumes the engine already exists.

version_added: '2.5'

options:
  name:
    description:
      - Name of the engine to enable BGP
    required: true
    type: str
  router_id:
    description:
      - Router ID for this BGP configuration. The ID must be unique.
        Often, the global IPv4 address is the ID. By default, the Router
        ID is automatically the loopback CVI address or the highest
        CVI address available on the Firewall Cluster
    type: str
  autonomous_system:
    description:
      - An AS represents a whole network or a series of networks. Required
        if creating new BGP configuration or changing existing AS.
    type: str
  bgp_profile:
    description:
      - Specify a unique BGP Profile for this configuration. The element
        contains distance, redistribution, and aggregation settings. Default
        profile is used if not provided.
    type: str
  announced_networks:
    description:
      - Networks to announce for this BGP configuration. These are typically
        internal directly connected or routed networks.
    type: list
    
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
'''


import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase

try:
    from smc.core.engine import Engine
    from smc.routing.bgp import AutonomousSystem, BGPProfile
    from smc.elements.network import Network, Host
    from smc.elements.group import Group
    from smc.api.exceptions import SMCException
except ImportError:
    pass


ELEMENT_TYPES = dict(
    network=Network,
    host=Host,
    group=Group)


def as_number_to_element(as_number):
    """
    Given just the as_number, return an element. If the
    element doesn't exist, it will be created.
    
    :rtype: AutonomousSystem
    """
    as_element = AutonomousSystem.objects.filter(
        as_number=as_number).first()
    if not as_element:
        as_element = AutonomousSystem.create(
            'as-%s' % as_number, as_number)
    return as_element


def announced_to_element(list_of):
    """
    Return a list of references for each element provided.
    
    :return: list of the announced network element href's
    """
    return [ELEMENT_TYPES.get(typeof)(value)
            for e in list_of
            for typeof, value in e.items()]
    

class StonesoftBGP(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            router_id=dict(type='str'),
            autonomous_system=dict(type='str'),
            announced_networks=dict(type='list'),
            bgp_profile=dict(type='str'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.router_id = None
        self.bgp_profile = None
        self.autonomous_system = None
        self.announced_networks = None
        
        self.results = dict(
            changed=False
        )
        super(StonesoftBGP, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:
            engine = Engine.get(self.name)
            if state == 'present':
                if engine.bgp.is_enabled:
                    bgp = engine.bgp # BGP reference
                    update = False
                    # Change router ID
                    if self.router_id and self.router_id != bgp.router_id:
                        bgp.reset_router_id(self.router_id)
                        update = True
                    
                    # Change autonomous system
                    if self.autonomous_system and self.autonomous_system != \
                        bgp.autonomous_system.name:
                        bgp.reset_autonomous_system(
                            AutonomousSystem(self.autonomous_system))
                        update = True
                    
                    if self.bgp_profile and self.bgp_profile != bgp.profile.name:
                        bgp.reset_profile(
                            BGPProfile(self.bgp_profile))
                        update = True
                    
                    if self.announced_networks:
                        pass
                    
                    if update:
                        engine.update()
                        changed = True
                    
                else:
                    if not self.autonomous_system:
                        self.fail(msg='Missing AS for BGP config')
                    
                    if not self.announced_networks:
                        self.fail(msg='Missing BGP announced networks')
                    
                    self._validate_announced(self.announced_networks)
                    
                    engine.enable_bgp(
                        autonomous_system=as_number_to_element(
                            self.autonomous_system),
                        announced_networks=announced_to_element(
                            self.announced_networks),
                        router_id=self.router_id,
                        bgp_profile=self.bgp_profile)
                    
                    engine.update()
                    changed = True

            elif state == 'absent':
                pass

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results
    
    def _validate_announced(self, list_of):
        valid = ['host', 'network', 'group']
        keys = {z for y in (x.keys() for x in list_of) for z in y}
        if not all(key in valid for key in keys):
            self.fail(msg='Announced network types supported: %s' % valid)
            

def main():
    StonesoftBGP()
    
if __name__ == '__main__':
    main()