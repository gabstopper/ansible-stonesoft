"""
Base spec for Stonesoft Management Center connections. This is a session
that will be re-used for multiple operations against the management
server.
"""
import inspect
import traceback
from ansible.module_utils.basic import AnsibleModule


try:
    from smc import session
    import smc.elements.network as network
    import smc.elements.group as group
    import smc.elements.service as service
    from smc.core.engine import Engine
    from smc.base.collection import Search
    from smc.elements.other import Category
    from smc.api.exceptions import (
        ConfigLoadError,
        SMCException,
        ElementNotFound, DeleteElementFailed)
    HAS_LIB = True
except ImportError:
    HAS_LIB = False
    

class Cache(object):
    """
    Convenience cache object to reduce number of queries for a
    given playbook and store unfound elements in `missing`. This
    is not intended to have a `get_or_create` logic, therefore when
    validating the existence of elements, you should check missing
    before continuing the playbook run.
    """
    
    def __init__(self):
        self.missing = []
        self.cache = {}
        
    def add_many(self, list_of_entries):
        """
        Add many elements into cache. Format should be:
    
            element = [{'network': [network1,network2]},
                       {'host': [host1, host2]}
                       ...]
        Where the key is a valid 'typeof' (SMC entry point)
        and value is a list of names to search
        """
        for elements in list_of_entries:
            for typeof, values in elements.items():
                for name in values:
                    self._add_entry(typeof, name)
                
    def add(self, dict_of_entries):
        """
        Add entry as dict of list, format:
        
            element = {'network': [network1,network2]}
        """
        for typeof, values in dict_of_entries.items():
            for name in values:
                self._add_entry(typeof, name)
        
    def _add_entry(self, typeof, name):
        # Add entry if it doesn't already exist
        if self.get(typeof, name):
            return
        result = Search.objects.entry_point(typeof)\
            .filter(name, exact_match=True).first()
        if result:
            self.cache.setdefault(typeof, []).append(
                result)
        else:
            self.missing.append(
                dict(msg='Cannot find specified element',
                     name=name,type=typeof))
    
    def get(self, typeof, name):
        for value in self.cache.get(typeof, []):
            if value.name == name:
                return value


def element_type_dict(map_only=False):
    """ 
    Type dict constructed with valid `create` constructor arguments.
    This is used in modules that support get_or_create operations
    for an element.
    """
    types = dict(
        host=dict(type=network.Host),
        network=dict(type=network.Network),
        address_range=dict(type=network.AddressRange),
        router=dict(type=network.Router),
        ip_list=dict(type=network.IPList),
        group=dict(type=group.Group),
        interface_zone=dict(type=network.Zone),
        domain_name=dict(type=network.DomainName))
    
    if map_only:
        return types
    
    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.create).args[1:]
    
    return types


def ro_element_type_dict(map_only=False):
    """
    Type dict of read-only network elements. These elements can be
    fetched but not created
    """
    types = dict(
        alias=dict(type=network.Alias),
        country=dict(type=network.Country),
        expression=dict(type=network.Expression),
        engine=dict(type=Engine))

    if map_only:
        return types
    
    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.__init__).args[1:]
    
    return types


def service_type_dict(map_only=False):
    """
    Type dict for serviec elements and groups.
    """
    types = dict(
        tcp_service=dict(type=service.TCPService),
        udp_service=dict(type=service.UDPService),
        ip_service=dict(type=service.IPService),
        ethernet_service=dict(type=service.EthernetService),
        icmp_service=dict(type=service.ICMPService),
        icmp_ipv6_service=dict(type=service.ICMPIPv6Service),
        service_group=dict(type=group.ServiceGroup),
        tcp_service_group=dict(type=group.TCPServiceGroup),
        udp_service_group=dict(type=group.UDPServiceGroup),
        ip_service_group=dict(type=group.IPServiceGroup),
        icmp_service_group=dict(type=group.ICMPServiceGroup))
    
    if map_only:
        return types
    
    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.create).args[1:]
    
    return types


def ro_service_type_dict():
    """
    Type dict of read-only service elements. These elements can be
    fetched but not created
    """
    types = dict(
        url_category=dict(type=service.URLCategory),
        application_situation=dict(type=service.ApplicationSituation),
        protocol=dict(type=service.Protocol),
        rpc_service=dict(type=service.RPCService))
    
    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.__init__).args[1:]
    
    return types


def get_or_create(element, type_dict, hint=None, check_mode=False):
    """
    Create or get the element specified. Set check_mode to only
    perform a get against the element versus an actual action.
    
    :param dict element: element dict, key is typeof element and values
    :param dict type_dict: type dict mappings to get class mapping
    :param str hint: element attribute to use when finding the element
    :raises CreateElementFailed: may fail due to duplicate name or other
    :raises ElementNotFound: if fetch and element doesn't exist
    :return: The result as type Element
    """
    for typeof, values in element.items():
        type_dict = type_dict.get(typeof)
        
        # An optional filter key specifies a valid attribute of
        # the element that is used to refine the search so the
        # match is done on that exact attribute. This is generally
        # useful for networks and address ranges due to how the SMC
        # interprets / or - when searching attributes. This changes
        # the query to use the attribute for the top level search to
        # get matches, then gets the elements attributes for the exact
        # match. Without filter_key, only the name value is searched.
        filter_key = {hint: values.get(hint)} if hint in values else None
        
        if check_mode:
            result = type_dict['type'].get(values.get('name'), raise_exc=False)
            if result is None:
                return dict(
                    name=values.get('name'),
                    type=typeof,
                    msg='Specified element does not exist')
        else:
            result = type_dict['type'].get_or_create(filter_key=filter_key, **values)
            return result
                

def update_or_create(element, type_dict, check_mode=False):
    """
    Update or create the element specified. Set check_mode to only
    perform a get against the element versus an actual action.
    
    :param dict element: element dict, key is typeof element and values
    :param dict type_dict: type dict mappings to get class mapping
    :param str hint: element attribute to use when finding the element
    :raises CreateElementFailed: may fail due to duplicate name or other
    :raises ElementNotFound: if fetch and element doesn't exist
    :return: The result as type Element
    """
    for typeof, values in element.items():
        type_dict = type_dict.get(typeof)
        
        if check_mode:
            result = type_dict['type'].get(values.get('name'), raise_exc=False)
            if result is None:
                return dict(
                    name=values.get('name'),
                    type=typeof,
                    msg='Specified element does not exist')
        else:
            attr_names = type_dict.get('attr', []) # Constructor args
            provided_args = set(values)
                
            # Guard against calling create for elements that may not exist
            # and do not have valid `create` constructor arguments
            if set(attr_names) == set(['name', 'comment']) or \
                any(arg for arg in provided_args if arg not in ('name',)):
                
                result = type_dict['type'].update_or_create(**values)
            else:
                result = type_dict['type'].get(values.get('name'))
        
            return result


def delete_element(element, ignore_if_not_found=True):
    """
    Delete an element of any type.
    
    :param Element element: the smc api element
    :param bool ignore_if_not_found: ignore raising an exception when
        a specified element is not found. This will still be returned
        for the state result.
    :raises DeleteElementFailed: failed to delete an element. This is
        generally thrown when a another configuration area has a
        dependency on this element (i.e. used in policy, etc).
    :return: list or None
    """
    try:
        element.delete()
    except ElementNotFound:
        if ignore_if_not_found:
            return dict(
                name=element.name,
                type=element.typeof,
                msg='Element not found, skipping delete')
    except DeleteElementFailed as e:
        if ignore_if_not_found:
            return dict(
                name=element.name,
                type=element.typeof,
                msg=str(e))
    

def format_element(element):
    """
    Format a raw json element doc
    """
    for key in ('link', 'key', 'system_key'):
        element.data.pop(key, None)
    return element.data.data


def element_dict_from_obj(element, type_dict, expand=None):
    """
    Resolve the element to the type and return a dict
    with the values of defined attributes
    
    :param Element element
    :return dict representation of the element
    """
    expand = expand if expand else []
    known = type_dict.get(element.typeof)
    if known:
        elem = {'type': element.typeof}
        for attribute in known.get('attr', []):
            if 'group' in element.typeof and 'group' in expand:
                if attribute == 'members':
                    elem[attribute] = []
                    for member in element.obtain_members():
                        m_expand = ['group'] if 'group' in member.typeof else None
                        elem[attribute].append(
                            element_dict_from_obj(member, type_dict, m_expand))
                else:
                    elem[attribute] = getattr(element, attribute, None)
            else:        
                elem[attribute] = getattr(element, attribute, None)
        return elem
    else:
        return dict(name=element.name, type=element.typeof)


def smc_argument_spec():
    return dict(
        smc_address=dict(type='str'),
        smc_api_key=dict(type='str', no_log=True),
        smc_api_version=dict(type='str'),
        smc_timeout=dict(default=30, type='int'),
        smc_domain=dict(type='str'),
        smc_alt_filepath=dict(type='str'),
        smc_extra_args=dict(type='dict'),
        smc_logging=dict(type='dict')
    )


def fact_argument_spec():
    return dict(
        filter=dict(type='str'),
        limit=dict(default=0, type='int'),
        exact_match=dict(default=False, type='bool'),
        case_sensitive=dict(default=True, type='bool'),
        as_yaml=dict(default=False, type='bool')
    )


class StonesoftModuleBase(object):
    def __init__(self, module_args, required_if=None, bypass_checks=False,
                 no_log=False, check_invalid_arguments=True,
                 mutually_exclusive=None, required_together=None,
                 required_one_of=None, add_file_common_args=False,
                 supports_check_mode=False, is_fact=False):
        
        argument_spec = smc_argument_spec()
        if is_fact:
            argument_spec.update(fact_argument_spec())
        argument_spec.update(module_args)
        
        self.module = AnsibleModule(
            argument_spec=argument_spec,
            required_if=required_if,
            bypass_checks=bypass_checks,
            no_log=no_log,
            check_invalid_arguments=check_invalid_arguments,
            mutually_exclusive=mutually_exclusive,
            required_together=required_together,
            required_one_of=required_one_of,
            add_file_common_args=add_file_common_args,
            supports_check_mode=supports_check_mode)
        
        if not HAS_LIB:
            self.module.fail_json(msg='Could not import smc-python required by this module')
        
        self.check_mode = self.module.check_mode
        self.connect(self.module.params)
            
        result = self.exec_module(**self.module.params)
        self.success(**result)
    
    def connect(self, params):
        """
        Get the SMC connection. If the credentials are provided in the module,
        then use them. Otherwise credentials gathering falls back to using
        smc-python native methods. Session is maintained for ansible run.
        
        :param dict params: dict of the SMC credential information
        """
        try:
            if params.get('smc_logging') is not None:
                if 'path' not in params['smc_logging']:
                    self.fail(msg='You must specify a path for SMC logging.')
        
                session.set_file_logger(
                    log_level=params['smc_logging'].get('level', 10),
                    path=params['smc_logging']['path'])
            
            if 'smc_address' and 'smc_api_key' in params:    
                extra_args = params.get('smc_extra_args')
                # When connection parameters are defined, alt_filepath is ignored.
                session.login(
                    url=params.get('smc_address'),
                    api_key=params.get('smc_api_key'),
                    api_version=params.get('smc_api_version'),
                    timeout=params.get('smc_timeout'),
                    domain=params.get('smc_domain'),
                    **(extra_args or {}))
            elif 'smc_alt_filepath' in params:
                # User specified to look in file
                session.login(alt_filepath=params['smc_alt_filepath'])
            else:
                # From user ~.smcrc or environment
                session.login()
        
        except (ConfigLoadError, SMCException) as err:
            self.fail(msg=str(err), exception=traceback.format_exc())

    def disconnect(self):
        """
        Disconnect session from SMC after ansible run
        """
        try:
            session.logout()
        except SMCException:
            pass
    
    def exec_module(self):
        self.fail(msg='Override in sub-module. Called from: {}'.format(self.__class__.__name__))
    
    def search_by_context(self):
        """
        Only used by fact modules. Fact modules need to implement a single
        attribute `element` that identifies the SMC entry point used for
        the search. See engine_facts for an example.
        This is a generic iterator using SMC context_filters
        
        :return: list of metadata results
        :rtype: list
        """
        if self.filter:
            # Find specific
            iterator = Search.objects\
                .context_filter(self.element)\
                .filter(self.filter,
                        exact_match=self.exact_match,
                        case_sensitive=self.case_sensitive)            
        else:
            # Find all
            iterator = Search.objects.context_filter(self.element)
        
        if self.limit >= 1:
            iterator = iterator.limit(self.limit)
               
        return list(iterator)
    
    def search_by_type(self, typeof):
        """
        Only used by fact modules. Fact modules need to implement a single
        attribute `element` that identifies the SMC entry point used for
        the search. See engine_facts for an example.
        This is an iterator by the specific SMC element type.
        
        :param str typeof: SMC API entry point
        :return: list of metadata results
        :rtype: list
        """
        if self.filter:
            iterator = typeof.objects\
                .filter(self.filter,
                        exact_match=self.exact_match,
                        case_sensitive=self.case_sensitive)
        else:
            iterator = typeof.objects.all()
        
        if self.limit >= 1:
            iterator = iterator.limit(self.limit)
        
        return list(iterator)
    
    def fetch_element(self, cls):
        """
        Fetch an element by doing an exact match.
        Name should be set on self.
        
        :param Element cls: class of type Element
        :return: element or None
        """
        return cls.objects.filter(self.name, exact_match=True).first()
    
    def add_tags(self, element, tags):
        """    
        Add tag/s to an element.
        
        :param Element element: the element to add a tag.
        :param list tags: list of tags by name
        :return: boolean success or fail
        """
        changed = False
        current_tags = [tag.name for tag in element.categories]
        add_tags = set(tags) - set(current_tags)
        if add_tags:
            element.add_category(list(add_tags))
            changed = True
        return changed
    
    def remove_tags(self, element, tags):
        """
        Remove tag/s from an element
        
        :param Element element: the element to add a tag.
        :param list tags: list of tags by name
        :return: boolean success or fail
        """
        changed = False
        current_tags = [tag.name for tag in element.categories]
        for tag in tags:
            if tag in current_tags:
                category = Category(tag)
                category.remove_element(element)
                changed = True
        return changed
    
    def clear_tags(self, element):
        """
        Clear all tags from the element
        
        :param Element element: the element for which to remove tags
        :return: boolean success or fail
        """
        changed = False
        for category in element.categories:
            category.remove_element(element)
            changed = True
        return changed
        
    def is_element_valid(self, element, type_dict, check_required=True):
        """
        Used by modules that want to create an element (network and service).
        This will check that all provided arguments are valid for this element
        type. When creating an element, name and comment are valid for all.
        Key of dict should be the valid typeof element. Value is the data
        for the element.
        
        :param dict element: dict of element, key is typeof
        :param dict type_dict: provide a type dict to specify which elements
            are supported for the given context of the call. Default type
            dict examples are defined in stonesoft_util.
        :param bool check_required: check required validates that at least
            one of the required arguments are provided. Skip this when
            checking group members that may only provide the 'name' field
            to reference a member to be added to a group versus creating the
            member.
        :return: error message on fail, otherwise None
        """
        for key, values in element.items():
            if key not in type_dict:
                self.fail(msg='Unsupported element type: {} provided'.format(key))
    
            valid_values = type_dict.get(key).get('attr', [])
            # Verify that all attributes are supported for this element type
            provided_values = values.keys() if isinstance(values, dict) else []
            if provided_values:
                # Name is always required
                if 'name' not in provided_values:
                    self.fail(msg='Entry: {}, missing required name field'.format(key))
            
                for value in provided_values:
                    if value not in valid_values:
                        self.fail(msg='Entry type: {} with name {} has an invalid field: {}. '\
                            'Valid values: {} '.format(key, values['name'], value, valid_values))
                
                if check_required:
                    required_arg = [arg for arg in valid_values if arg not in ('name', 'comment')]
                    if required_arg: #Something other than name and comment fields
                        if not any(arg for arg in required_arg if arg in provided_values):
                            self.fail(msg='Missing a required argument for {} entry: {}, Valid values: {}'\
                                .format(key, values['name'], valid_values))
                
                if 'group' in element and values.get('members', []):
                    for element in values['members']:
                        if not isinstance(element, dict):
                            return 'Group {} has a member: {} with an invalid format. Members must be '\
                                'of type dict.'.format(values['name'], element)
                        return self.is_element_valid(element, type_dict, check_required=False)
            else:
                self.fail(msg='Entry type: {} has no values. Valid values: {} '\
                    .format(key, valid_values))
    
    def fail(self, msg, **kwargs):
        """
        Fail the request with message
        """
        self.disconnect()
        self.module.fail_json(msg=msg, **kwargs)
        
    def success(self, **result):
        """
        Success with result messages
        """
        self.disconnect()
        self.module.exit_json(**result)
        
        

