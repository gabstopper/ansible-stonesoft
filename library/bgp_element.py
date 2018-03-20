

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase
from smc.routing.bgp import AutonomousSystem


try:
    from smc.base.model import lookup_class
    from smc.api.exceptions import SMCException
except ImportError:
    pass


"""
Access Lists require the entries parameter and specific attributes depending on
the access list type. These are used to validate the input prior to using for
creating.
"""
access_lists = {
    'ip_prefix_list': ['subnet', 'min_prefix_length', 'max_prefix_length', 'action'],
    'ipv6_prefix_list': ['subnet', 'min_prefix_length', 'max_prefix_length', 'action'],
    'ip_access_list': ['subnet', 'action'],
    'ipv6_access_list': ['subnet', 'action'],
    'as_path_access_list': ['expression', 'action'],
    'community_access_list': ['community', 'action'],
    'extended_community_access_list': ['community', 'action', 'type']
}
    
    
bgp_elements = (
    'ip_access_list', 'ip_prefix_list', 'ipv6_access_list',
    'ipv6_prefix_list', 'as_path_access_list', 'community_access_list',
    'extended_community_access_list', 'external_bgp_peer', 'bgp_peering',
    'autonomous_system'
)



class StonesoftBGPElement(StonesoftModuleBase):
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
        super(StonesoftBGPElement, self).__init__(self.module_args, supports_check_mode=True)
        
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        
        try:
            if state == 'present':
                
                self.check_elements()
                
                # Defer ExternalBGPPeer as it's dependent on having a valid
                # AutonomousSystem element, but only if the AS doesn't already exist
                deferrals, elements = self.resolve_references(self.elements)
                
                for element in elements:
                    if self.create_or_update_element(element):
                        changed = True
                
                if deferrals:
                    empty, bgp_peers = self.resolve_references(deferrals)
                    for element in bgp_peers:
                        if self.create_or_update_element(element):
                            changed = True
                
            else:
                # No need to validate elements beyond type and name
                for element in self.elements:
                    for typeof, values in element.items():
                        klazz = lookup_class(typeof)
                        name = values.get('name')
                        try:
                            klazz(name).delete()
                            self.results['state'].append(
                                {'name': name, 'type': klazz.typeof, 'action': 'deleted'})
                        except SMCException as e:
                            self.results['state'].append(
                                {'name': name, 'type': klazz.typeof, 'action': 'failed to delete '
                                 'with reason: %s' % str(e)})
            
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed
        return self.results 
    
    def create_or_update_element(self, element):
        """
        Create the element. 
        
        :param dict element: the element dict from elements
        """
        changed = False
        for typeof, values in element.items():
            klazz = lookup_class(typeof)
            
            obj, modified, created = klazz.update_or_create(
                with_status=True, **values)
            if created:
                self.results['state'].append(
                    {'name': obj.name, 'type': obj.typeof, 'action': 'created'})
            elif modified:
                self.results['state'].append(
                    {'name': obj.name, 'type': obj.typeof, 'action': 'modified'})
            changed = created or modified
        return changed    
        
    def resolve_references(self, elementlist):
        """
        Some elements have a dependency on another element being
        created. Check for those elements here and defer their
        creation until the end if the dependency is also being created.
        
        :rtype: tuple(list, list)
        """
        deferrals, elements = ([] for i in range(2))
        for element in elementlist:
            if 'external_bgp_peer' in element:
                value = element.get('external_bgp_peer')
                neighbor = value.get('neighbor_as')
                if not self.dependency_being_created(elementlist, 'autonomous_system', neighbor):
                    as_system = AutonomousSystem.get(neighbor, raise_exc=False)
                    if not as_system:
                        self.fail(msg='Autonomous System: %r referenced in external_bgp_peer: '
                            'cannot be found and is not being created by this task: %s' %
                            (neighbor, value))
                    else:
                        value.update(neighbor_as=as_system.href)
                else:
                    deferrals.append(element)
                    continue
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
                self.fail('BGP element type must be defined as a dict, received: '
                    '%s, type: %s' % (element, type(element)))
            for bgp_element, values in element.items():
                if bgp_element not in bgp_elements:
                    self.fail(msg='BGP element type specified is not a supported '
                        'element type, provided: %s. Valid values: %s' %
                        (bgp_element, list(bgp_elements)))
                if not isinstance(values, dict):
                    self.fail(msg='Element values must be of type dict. Received '
                        'values: %s of type: %s' % (values, type(values)))
                
                if 'name' not in values:
                    self.fail(msg='Name is a required field when creating or '
                        'modifying an element. Missing on defintion: %s' % bgp_element)
                
                if 'access_list' in bgp_element:
                    # Check that all entry values are valid
                    entries = values.get('entries')
                    if not entries:
                        self.fail(msg='You must specify at least one value in entries '
                            'to create an access list of any type: %s' % bgp_element)
        
                    required = set(access_lists.get(bgp_element))
                    for specified in entries:
                        if set(specified.keys()) ^ required:
                            self.fail(msg='Missing required fields for the access list: %s. '
                                'Received: %s, required values: %s' % (bgp_element, specified,
                                list(required)))
                    
                    # Use a standard vs. expanded ACL if not specified        
                    if 'community' in bgp_element and 'type' not in values:
                        values.update(type='standard')

                elif 'external_bgp_peer' in bgp_element:
                    for required in ('neighbor_as', 'neighbor_ip'):
                        if required not in values or not values.get(required):
                            self.fail(msg='External BGP definition is missing neighbor_as '
                                'or neighbor_ip value, received: %s' % values)

                elif 'autonomous_system' in bgp_element:
                    if 'as_number' not in values or not values.get('as_number'):
                        self.fail(msg='Autonomous system requires an as_number be set: %s'
                            % values)

    
def main():
    StonesoftBGPElement()
    
if __name__ == '__main__':
    main()

        
        