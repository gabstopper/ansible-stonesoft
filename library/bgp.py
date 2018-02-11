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
        if creating new BGP configuration or changing existing AS. Required if I(state=present).
    type: str
  bgp_profile:
    description:
      - Specify a unique BGP Profile for this configuration. The element
        contains distance, redistribution, and aggregation settings. Default
        profile is used if not provided.
    type: str
    default: Default BGP Profile
  announced_networks:
    description:
      - Networks to announce for this BGP configuration. These are typically
        internal directly connected or routed networks. Required if I(state=present).
    type: dict
    suboptions:
      network:
        description:
          - Network cidr for the announced network in format 1.1.1.0/24. Network will be
            created if it doesn't exist with name network-1.1.1.0/24
        type: list
      host:
        description:
          - Host IP for the announced network. Host will be created if it doesn't exist.
            Created host will be named in format host-1.1.1.1
        type: list
      group:
        description:
          - Name of group, this should exist or an empty group will be created
        type: list
  bgp_peering:
    description:
      - Configure an interface on this engine with a BGP Peering and an external peer.
    type: dict
    suboptions:
      name:
        description:
          - The name of the BGPPeering within SMC. If this does not exist, it will be
            automatically created
        type: str
        required: true
      interface_id:
        description:
          - The interface ID for which to add the peering. You can also optionally provide
            a value for I(network) to specify an exact network. Otherwise the peering is added
            to add networks if multiple are assigned to the specified interface
        type: str
        required: true
      network:
        description:
          - The network cidr to add BGP peering when an interface has multiple network routes
        type: str
      neighbor_ip:
        description:
          - The IP Address for the external BGP peer. Required if I(bgp_peering)
        type: str
      neighbor_as:
        description:
          - The external AS number. The element will be created if one doesn't already exist
        type: str
      neighbor_port:
        description:
          - The external BGP port.
        type: int
        default: 179

'''

EXAMPLES = '''
- name: Run the BGP task on myfw with logging
    register: result
    bgp:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      name: myfw
      autonomous_system: 250
      router_id: none
      announced_networks:
        network:
          - 172.18.1.0/24
          - 172.18.2.0/24
          - 172.18.18.0/24
        host:
          - 1.1.1.1
        group:
          - mygroup
      #bgp_profile: foo
      bgp_peering:
        name: mypeering
        interface_id: 0
        network: 1.1.1.0/24
        neighbor_ip: 10.10.10.10
        neighbor_as: 200
        neighbor_port: 179

'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: The current state of the element
  return: always
  type: dict
'''


import traceback
from ansible.module_utils.stonesoft_util import (
    StonesoftModuleBase,
    get_or_create,
    format_element,
    element_type_dict)


try:
    from smc.core.engine import Engine
    from smc.routing.bgp import AutonomousSystem, BGPProfile, BGPPeering, ExternalBGPPeer
    from smc.api.exceptions import SMCException
except ImportError:
    pass


def remove_bgp(engine, name=None, interface_id=None):
    """
    Remove BGP Peering from the engine. Optionally only
    remove BGP Peering by name and/or interface_id
    
    :param str name: name of BGPPeering element
    :param str,int interface_id: interface id
    """
    root = engine.routing
    if interface_id is not None:
        root = root.get(interface_id)
    for tree_tup in root.bgp_peerings:
        _, _, bgp = tree_tup
        if name:
            if bgp.name == name:
                bgp.delete()
        else:
            bgp.delete()
            

def as_number_to_element(as_number):
    """
    Given just the as_number, return an element. If the
    element doesn't exist, it will be created.
    
    :rtype: AutonomousSystem
    """
    as_element = AutonomousSystem.objects.filter(
        as_number=str(as_number)).first()
    if not as_element:
        as_element = AutonomousSystem.create(
            'as-%s' % as_number, as_number)
    return as_element


class StonesoftBGP(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            router_id=dict(type='str'),
            autonomous_system=dict(type='str'),
            announced_networks=dict(type='dict'),
            bgp_profile=dict(type='str', default='Default BGP'),
            bgp_peering=dict(type='dict'),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        required_if=([
            ('state', 'present', ['autonomous_system', 'announced_networks'])
        ])
            
        self.name = None
        self.router_id = None
        self.bgp_profile = None
        self.autonomous_system = None
        self.announced_networks = None
        self.bgp_peering = None
        
        self.results = dict(
            changed=False,
            state={}
        )
        super(StonesoftBGP, self).__init__(self.module_args, required_if=required_if,
            supports_check_mode=True)
    
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
                    
                    announced = self.get_announced_networks()
                    if self.check_mode:
                        self.results['state'] = [adv for adv in announced if adv is not None]

                        return self.results
                    
                    existing = [ne.get('announced_ne_ref')
                                for ne in bgp.data.get('announced_ne_setting', [])]
                    
                    announced_ref = [an.href for an in announced]
                    
                    ne = bgp.data['announced_ne_setting'] = []
                    
                    # Add any new advertised networks   
                    for element in announced_ref:
                        if element not in existing:
                            update = True
                        ne.append({'announced_ne_ref': element})
                    
                    # Remove any that are not defined
                    for href in existing:
                        if href not in announced_ref:
                            update = True

                    # Change router ID
                    if self.router_id and self.router_id != bgp.router_id:
                        bgp.reset_router_id(self.router_id)
                        update = True
                    
                    # Change autonomous system
                    if self.autonomous_system != str(bgp.autonomous_system.as_number):
                        bgp.reset_autonomous_system(
                            as_number_to_element(self.autonomous_system))
                        update = True
                    
                    # Modify BGP Profile
                    if self.bgp_profile:
                        if self.bgp_profile != bgp.profile.name:
                            try:
                                bgp.reset_profile(
                                    BGPProfile(self.bgp_profile))
                                update = True
                            except SMCException:
                                pass
                    
                    if update:
                        engine.update()
                        changed = True
                    
                else:
                    
                    self._validate_announced(self.announced_networks)
                    if self.bgp_peering:
                        if not all(k in self.bgp_peering for k in ('interface_id', 'name')):
                            self.fail(msg='You must specify a BGP peering name and an '
                                'interface_id for which to apply the BGP Peering.')
                        
                        if not all(k in self.bgp_peering for k in ('neighbor_ip', 'neighbor_as')):
                            self.fail(msg='You must specify neighbor_ip and neighbor_as '
                                'when defining BGP peering.')
                        # Get the interface, raises InterfaceNotFound
                        interface = engine.routing.get(self.bgp_peering['interface_id'])
                        if 'network' in self.bgp_peering:
                            if not any(net for net in interface if net.ip == self.bgp_peering['network']):
                                self.fail(msg='Network specified: {} does not exist on the interface '
                                    'id specified: {}'.format(
                                        self.bgp_peering['network'], self.bgp_peering['interface_id']))

                    announced = self.get_announced_networks()
                    
                    if self.check_mode:
                        self.results['state'] = [adv for adv in announced if adv is not None]
                        
                        return self.results
                
                    engine.bgp.enable(
                        autonomous_system=as_number_to_element(
                            self.autonomous_system),
                        announced_networks=announced,
                        router_id=self.router_id,
                        bgp_profile=BGPProfile.objects.filter(self.bgp_profile).first())
                    
                    # Update engine with BGP
                    engine.update()
                    changed = True
                    
                    # Create the External BGP Peer
                    if self.bgp_peering:
                        neighbor_as = as_number_to_element(self.bgp_peering['neighbor_as'])
                        neighbor_ip = self.bgp_peering['neighbor_ip']
                        neighbor_port = self.bgp_peering.get('neighbor_port', 179)
                        external_bgp_peer = ExternalBGPPeer.get_or_create(
                            filter_key={'neighbor_ip': neighbor_ip},
                            name='external-bgp-{}'.format(neighbor_ip),
                            neighbor_as_ref=neighbor_as,
                            neighbor_ip=neighbor_ip,
                            neighbor_port=neighbor_port)
                        
                        # Add this to the route table and interface. This operation does not
                        # require callin update as route table changes are automatic
                        bgp_peering = BGPPeering.get_or_create(name=self.bgp_peering['name'])
                        interface.add_bgp_peering(bgp_peering, external_bgp_peer,
                            network=self.bgp_peering.get('network', None))
                        changed=True
    
            elif state == 'absent':
                # Disable BGP from the engine. If bgp_peering is provided, then
                # only peering will be removed. When removing bgp_peering, you
                # can specify a bgp peering name and/or interface_id for which
                # to remove. If provided by name only, it will be removed from
                # all interfaces. If interface_id is provided, all peering on
                # that interface will be removed.
                if self.bgp_peering:
                    remove_bgp(engine, self.bgp_peering.get('name'),
                        self.bgp_peering.get('interface_id'))
                    
                else:
                    if engine.bgp.is_enabled:
                        engine.bgp.disable()
                        engine.update()
                        changed = True

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['state'] = format_element(engine.bgp)
        self.results['changed'] = changed
        return self.results
                
    def get_announced_networks(self):
        announced = []
        if 'network' in self.announced_networks:
            for network in self.announced_networks['network']:
                announced.append(get_or_create(
                    dict(network={'name': 'network-{}'.format(network),
                                  'ipv4_network': network}),
                    element_type_dict(), hint=network, check_mode=self.check_mode))
        
        if 'host' in self.announced_networks:
            for host in self.announced_networks['host']:
                announced.append(get_or_create(
                    dict(host={'name': 'host-{}'.format(host),
                               'address': host}),
                    element_type_dict(), check_mode=self.check_mode))
        
        if 'group' in self.announced_networks:
            for group in self.announced_networks['group']:
                announced.append(get_or_create(
                    dict(group={'name': 'group-{}'.format(group)}),
                         element_type_dict(), check_mode=self.check_mode))
        
        if self.check_mode:
            for advertised in announced:
                if advertised:
                    self.results['state'].append(advertised)
        return announced
                                
    def _validate_announced(self, announced):
        valid = ['host', 'network', 'group']
        if any(key not in valid for key in announced.keys()):
            self.fail(msg='Announced network types supported: %s' % valid)
            

def main():
    StonesoftBGP()
    
if __name__ == '__main__':
    main()