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
module: engine_routing
short_description: Routing configurations on NGFW
description:
  - Use this module to add or remove static routes, antispoofing, BGP, OSPF or netlink
    elements to routing nodes on an engine. You can use engine_facts to dump the engine
    configuration or use engine_routing_facts to specifically dump only the routing table

version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall cluster to access routing table
    required: true
  bgp_peering:
    description:
      - List of dict describing the BGP peering to add
    type: list
    suboptions:
      interface_id:
        description:
          - The interface id to add the peering. Can be VLAN id if specified 1.23
        type: str
        required: true
      name:
        description:
          - Name of the BGP peering element in SMC
        required: true
      network:
        description:
          - Optional network to bind the BGP Peer to. Only relevant if multiple IP addresses
            are assigned to the given interface and you only want to bind to one.
        type: str
      destination:
        description:
          - Destination is the BGP peer associated with this BGP Peering. This can be either
            another NGFW engine or an external_bgp_peer element. Both element types must
            preexist in the SMC.
        type: list
        suboptions:
          name:
            description:
              - Name of element existing in SMC
            type: str
          type:
            description:
              - Type of element from SMC. Valid types for BGP peering are engine and
                external_bgp_peer. Required if I(name)
            choices:
            - engine
            - external_bgp_peer
  ospfv2_area:
    description:
      - List of dict describing the OSPF areas to add
    type: list
    suboptions:
      interface_id:
        description:
          - The interface id to add the OSPF area. Can be VLAN id if specified 1.23
        type: str
        required: true
      name:
        description:
          - Name of the OSPF area element in SMC
        required: true
      network:
        description:
          - Optional network to bind the OSPF area to. Only relevant if multiple IP
            addresses are assigned to the given interface and you only want to bind to one.
        type: str
      destination:
        description:
          - Destination is the element referenced can be an OSPF Area interface setting
            element from SMC. This can be used to override the default interface settings
            for OSPF. This is optional.
        type: list
        suboptions:
          name:
            description:
              - Name of OSPF Area Interface settings
            type: str
          type:
            description:
              - Type of element from SMC. Only valid element type for OSPF is 
                ospfv2_interface_settings. Required if I(name)
            choices:
            - ospfv2_interface_settings
  netlink:
    description:
      - List of dict describing the netlinks
    type: list
    suboptions:
      interface_id:
        description:
          - The interface id to add the netlink. Can be VLAN id if specified 1.23
        type: str
        required: true
      name:
        description:
          - Name of the netlink element in SMC
        required: true
      network:
        description:
          - Optional network to bind the netlink. Only relevant if multiple IP
            addresses are assigned to the given interface and you only want to bind to one.
        type: str
      destination:
        description:
          - Destinations associated with this netlink. Multiple element types can be used
            as a destination
        type: list
        suboptions:
          name:
            description:
              - Name of element
            type: str
          type:
            description:
              - Type of element from SMC. Required if I(name)
            choices:
            - host
            - router
            - engine
            - network
            - group
  static_route:
    description:
      - List of static routes
    type: list
    suboptions:
      interface_id:
        description:
          - The interface id to add the static route. Can be VLAN id if specified 1.23
        type: str
        required: true
      name:
        description:
          - Name of the router element to use as the next hop for the static route.
            Note that this MUST be a router type element from SMC.
        required: true
      network:
        description:
          - Optional network to bind the route. Only relevant if multiple IP
            addresses are assigned to the given interface and you only want to bind to one.
        type: str
      destination:
        description:
          - Destinations associated with this static route. Multiple element types can be used
            as a destination
        type: list
        suboptions:
          name:
            description:
              - Name of element
            type: str
          type:
            description:
              - Type of element from SMC. Required if I(name)
            choices:
            - host
            - router
            - engine
            - network
            - group
  antispoofing_network:
    description:
      - List of static routes
    type: list
    suboptions:
      interface_id:
        description:
          - The interface id to add the antispoofing network. Can be VLAN id if specified 1.23
        type: str
        required: true
      destination:
        description:
          - Destinations associated with this antispoofing entry. Multiple element types can be used
            as a destination
        type: list
        suboptions:
          name:
            description:
              - Name of element
            type: str
          type:
            description:
              - Type of element from SMC. Required if I(name)
            choices:
            - host
            - router
            - engine
            - network
            - group
            - netlink
  state:
    description:
      - Add or remove the routing entry. If I(state=absent) any defined routing
        configurations are considered a removal action
    required: false
    default: present
    choices:
      - present
      - absent

extends_documentation_fragment: stonesoft

notes:
  - Login credential information is either obtained by providing them directly
    to the task/play, specifying an alt_filepath to read the credentials from to
    the play, or from environment variables (in that order). See
    U(http://smc-python.readthedocs.io/en/latest/pages/session.html) for more
    information.

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)

'''

EXAMPLES = '''
- name: Engine routing configuration
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Add routing elements to engine sg_vm
    engine_routing:
      smc_logging:
        level: 10
        path: ansible-smc.log
      name: sg_vm
      bgp_peering:
      - destination:
        - name: bgppeer
          type: external_bgp_peer
        interface_id: '1000'
        name: bgppeering
      ospfv2_area:
      - interface_id: '2.1'
        name: myarea
        network: 21.21.21.0/24
        destination:
        - name: myinterface
          type: ospfv2_interface_settings
      - name: myarea2
        interface_id: 1
      netlink:
      - destination:
        - name: IP_10.3.3.1
          type: host
        interface_id: '2.1'
        name: netlink-21.21.21.0
      static_route:
      - destination:
        - name: Any network
          type: network
        interface_id: 0
        network: '1.1.1.0/24'
        name: myrouter # Must be element of type Router
      antispoofing_network:
      - destination:
        - name: foonet
          type: network
        interface_id: 0

- name: Engine routing configuration
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Remove specific antispoofing network from engine sg_vm
    engine_routing:
      smc_logging:
        level: 10
        path: ansible-smc.log
      name: sg_vm
      antispoofing_network:
      - destination:
        - name: foonet
          type: network
        interface_id: 0
      state: absent
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

from ansible.module_utils.stonesoft_util import StonesoftModuleBase, Cache

try:
    from smc.base.model import lookup_class
    from smc.core.engine import Engine
    from smc.api.exceptions import InterfaceNotFound, SMCException
except ImportError:
    pass


route_element = ('bgp_peering', 'ospfv2_area', 'netlink', 'static_route', 'antispoofing_network')


# Valid destination element types for static route and netlinks
srt_or_netlink_elem = ('host','router','group','engine','network')

# Valid antispoofing destination element types
antispoofing_elem = srt_or_netlink_elem + ('netlink',)


class StonesoftEngineRouting(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            bgp_peering=dict(type='list', default=[]),
            ospfv2_area=dict(type='list', default=[]),
            netlink=dict(type='list', default=[]),
            static_route=dict(type='list', default=[]),
            antispoofing_network=dict(type='list', default=[]),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftEngineRouting, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
            
        changed = False
        engine = self.fetch_element(Engine)
        if not engine:
            self.fail(msg='Engine specified cannot be found: %s' % self.name)
        
        self.cache = Cache()
        
        try:
            if state == 'present':
                
                self.validate_elements(engine)
                
                if self.cache.missing:
                    self.fail(msg='Missing element dependencies, cannot continue: %s' % 
                        self.cache.missing)
                
                if self.check_mode:
                    return self.results
                
                if self.update_routing(engine):
                    changed = True
                
                if self.update_antispoofing(engine):
                    changed = True
        
            else:
                # No need to validate an elements type, instead just check for the
                # type and name of the element to remove from the interface routing
                if self.delete_routing(engine):
                    changed = True
        
        except SMCException as e:
            self.fail(msg=str(e))
            
        self.results['changed'] = changed    
        return self.results
    
    def delete_routing(self, engine):
        """
        Iterate through specified routes and remove and log the state.
        Catch exceptions so overall state can be reported after run.
        
        :rtype: bool
        """
        changed = False
        for element in route_element:
            for it in getattr(self, element):
                if 'interface_id' not in it:
                    break
                try:
                    if 'antispoofing_network' in element:
                        iface = engine.antispoofing.get(it.get('interface_id'))
                        for dest in it.get('destination', []):
                            klazz = lookup_class(dest.get('type'))
                            modified = iface.remove(klazz(dest.get('name')))
                            if modified:
                                self.results['state'].append(
                                    dict(action='deleted',
                                         name=dest.get('name'),
                                         type='antispoofing'))
                                changed = True
                    else:
                        if 'name' not in it:
                            break
                        iface = engine.routing.get(it.get('interface_id'))
                        klazz = lookup_class(element) if element != 'static_route'\
                            else lookup_class('router')    
                        modified = iface.remove_route_gateway(klazz(it.get('name')))
                    
                        if modified:
                            self.results['state'].append(
                                dict(action='deleted',
                                     name=it.get('name'),
                                     type=klazz.typeof))
                            changed = True

                except InterfaceNotFound:
                    self.results['state'].append(
                        dict(action='Cannot find specified interface',
                             name=it.get('interface_id'),
                             type='interface'))
            
                except SMCException as e:
                    self.results['state'].append(
                        dict(action='Failed to delete with reason: %s' % str(e),
                             name=it.get('name'),
                             type=klazz.typeof))
    
        return changed
    
    def update_antispoofing(self, engine):
        """
        Update antispoofing on the engine
        
        :param Engine engine: engine ref
        :return: Whether routing was changed or not
        :rtype: bool
        """
        changed = False
        for it in self.antispoofing_network:
            routing_node = engine.antispoofing.get(it.get('interface_id'))
            for destination in it.get('destination', []):
                element = self.cache.get(
                    destination.get('type'), destination.get('name'))
                modified = routing_node.add(element)
                if modified:
                    self.results['state'].append(
                        {'name': 'interface %s' % it.get('interface_id'),
                         'type': 'antispoofing', 'action': 'updated'})
                    changed = True
        return changed

    def update_routing(self, engine):
        """
        Generic update for each routing element type.
        
        :param Engine engine: engine ref
        :return: Whether routing was changed or not
        :rtype: bool
        """
        mapper = {'bgp_peering': 'add_bgp_peering', 'ospfv2_area': 'add_ospf_area',
                  'netlink': 'add_traffic_handler', 'static_route': 'add_static_route'}
        
        changed = False
        for routing in mapper.keys():
            for it in getattr(self, routing):
                routing_node = engine.routing.get(it.get('interface_id'))
                # Static Routes are expected to have Router elements
                element = self.cache.get(routing, it.get('name')) if 'static_route' \
                    not in routing else self.cache.get('router', it.get('name'))
                
                destinations = []
                if 'destination' in it:
                    destinations = [self.cache.get(dest.get('type'), dest.get('name'))
                        for dest in it.get('destination', [])]
                    # BGP Peering and OSPF areas are non-list destinations
                    if routing in ('ospfv2_area', 'bgp_peering'):
                        destinations = destinations[0]
                        # TODO: Implement unicast ref for OSPF
                        #if 'communication_mode' in it:
                        #    kwargs = {'unicast_ref': self.cache.get(
                        #        dest.get('host'), dest.get('unicast_ref'))}
                    
                # Order of args: element, destination, network
                # destination and network can be None or []
                modified = getattr(routing_node, mapper.get(routing))(
                    element, destinations, it.get('network'))
                
                if modified:
                    self.results['state'].append(
                        {'name': 'interface %s' % it.get('interface_id'),
                         'type': routing, 'action': 'updated'})
                    changed = True
        return changed
    
    def validate_elements(self, engine):
        """
        Validate each of the routing element types. The `add` API for each type
        is essentially the same but the required element types may differ slightly.
        For example, static route 'next hop' elements should be of type Router.
        Populate cache and set missing if elements are not found.
        
        :param Engine engine: engine ref
        :return: None
        """
        for element in route_element:
            if 'antispoofing_network' in element:
                self.validate_antispoofing(engine)
                continue
            for it in getattr(self, element):
                if 'interface_id' not in it or 'name' not in it:
                    self.fail(msg='All routing elements require the name and interface_id '
                              'parameters. Invalid: %s, %s' % (element, it))

                if element == 'static_route':
                    self.cache._add_entry('router', it.get('name'))
                else:
                    self.cache._add_entry(element, it.get('name'))
        
                if 'destination' in it and isinstance(it['destination'], list):
                    for destinations in it['destination']:
                        if 'name' not in destinations or 'type' not in destinations:
                            self.fail(msg='Destination routing element must have the name '
                                'and type attribute. Invalid: %s, %s' % (element, it))
                        if 'bgp_peering' in element:
                            if destinations.get('type') not in ('external_bgp_peer', 'engine'):
                                self.fail(msg='A BGP peering destination element can only be of type '
                                    'external_bgp_peer or engine. Invalid: %s' % element)
                        elif 'ospfv2_area' in element:
                            if destinations.get('type') != 'ospfv2_interface_settings':
                                self.fail(msg='A OSPF destination element can only be of type '
                                    'ospfv2_interface_settings. Invalid: %s' % element)
                        elif 'netlink' or 'static_route' in element:
                            if destinations.get('type') not in srt_or_netlink_elem:
                                self.fail(msg='A Netlink or static route destination element can '
                                    'only be of type: %s. Invalid: %s' % (
                                        list(srt_or_netlink_elem), element))
                        # Add to cache for later check
                        self.cache._add_entry(
                            typeof=destinations.get('type'),
                            name=destinations.get('name'))
                
                self.have_interface(
                    engine,
                    interface=it.get('interface_id'),
                    network=it.get('network', None))
    
    def validate_antispoofing(self, engine):
        """
        Validate any antispoofing networks being added to the specified
        engine.
        
        :param Engine engine: engine ref
        """
        for it in self.antispoofing_network:
            if 'interface_id' not in it:
                self.fail(msg='Interface ID is required when defining antispoofing: %s' % it)
            if 'destination' in it and isinstance(it['destination'], list):
                for destination in it['destination']:
                    if 'name' not in destination or 'type' not in destination:
                        self.fail(msg='Name and type is required when defining an '
                            'antispoofing network: %s' % destination)
                    if destination.get('type') not in antispoofing_elem:
                        self.fail(msg='An Antispoofing destination element can only be of type: %s'
                            % list(srt_or_netlink_elem))
                    self.cache._add_entry(destination['type'], destination['name'])

            self.have_interface(
                engine,
                interface=it.get('interface_id'))
                
    def have_interface(self, engine, interface, network=None):
        """
        Check that we have the interface referenced in the element
        
        :param Engine engine: engine ref
        :param str interface: interface ID provided in yaml
        :param str network: optional network if specified. Allows to bind
            to a specified network on an interface with multiple networks
        :return: None
        """
        try:
            iface = engine.routing.get(interface)
            if network:
                if not any(net.ip == network for net in iface):
                    self.cache.missing.append(
                        dict(msg='Cannot find specified network on interface',
                             name=network,
                             type='interface_network'))
                    
        except InterfaceNotFound:
            self.cache.missing.append(
                dict(msg='Cannot find specified interface',
                     name=interface,
                     type='interface'))

def main():
    StonesoftEngineRouting()
    
if __name__ == '__main__':
    main()
    