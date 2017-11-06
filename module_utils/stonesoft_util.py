"""
Base spec for Stonesoft Management Center connections. This is a session
that will be re-used for multiple operations against the management
server.
"""
import inspect
import traceback
from ansible.module_utils.basic import AnsibleModule
from smc.elements.service import ICMPService, ICMPIPv6Service


try:
    from smc import session
    import smc.elements.network as network
    import smc.elements.group as group
    import smc.elements.service as service
    from smc.base.collection import Search
    from smc.elements.other import Category
    from smc.api.exceptions import ConfigLoadError, SMCException
    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def element_type_dict():
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
    
    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.create).args[1:]
    
    return types


def ro_element_type_dict():
    """
    Type dict of read-only network elements. These elements can be
    fetched but not created
    """
    types = dict(
        alias=dict(type=network.Alias),
        country=dict(type=network.Country),
        expression=dict(type=network.Expression))

    for t in types.keys():
        clazz = types.get(t)['type']
        types[t]['attr'] = inspect.getargspec(clazz.__init__).args[1:]
    
    return types


def service_type_dict():
    """
    Type dict for serviec elements and groups.
    """
    types = dict(
        tcp_service=dict(type=service.TCPService),
        udp_service=dict(type=service.UDPService),
        ip_service=dict(type=service.IPService),
        ethernet_service=dict(type=service.EthernetService),
        icmp_service=dict(type=ICMPService),
        icmp_ipv6_service=dict(type=ICMPIPv6Service),
        service_group=dict(type=group.ServiceGroup),
        tcp_service_group=dict(type=group.TCPServiceGroup),
        udp_service_group=dict(type=group.UDPServiceGroup),
        ip_service_group=dict(type=group.IPServiceGroup),
        icmp_service_group=dict(type=group.ICMPServiceGroup))
    
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

    
SEARCH_HINTS = dict(
    host='address',
    router='address',
    network='ipv4_network',
    address_range='ip_range')


def get_or_create_element(element, type_dict):
    """
    Create or get the element specified. The strategy is to look at the
    element type and check the default arguments. Some elements require
    only name and comment to create. Others require specific arguments.
    If only name and comment is provided and the constructor requires
    additional args, try to fetch the element, otherwise call
    get_or_create. If the constructor only requires name and comment,
    these will also call get_or_create.
    
    :param dict element: dict of the element with single key representing
        the typeof element, value is the optional arguments for create.
    :param dict type_dict: map of element type to class and attributes
    :raises CreateElementFailed: may fail due to duplicate name or other
    :raises ElementNotFound: if fetch and element doesn't exist
    :return: The result as type Element
    """
    for typeof, values in element.items():
        type_dict = type_dict.get(typeof)
        
        attr_names = type_dict.get('attr', []) # Constructor args
        provided_args = set(values)
        
        hint = SEARCH_HINTS.get(typeof)
        filter_key = {hint: values.get(hint)} if hint else None

        # Args satisfy a call to create
        if any(arg for arg in provided_args if arg not in ('name', 'comment')):
            result = type_dict['type'].get_or_create(filter_key=filter_key, **values)
        else:
            # Only name and/or comment was provided.
            if any(x for x in attr_names if x not in ('name', 'comment')):
                # Other arguments are required, so we can only try to get
                result = type_dict['type'].get(values.get('name'))
            else:
                # Constructor only requires name, comment so get or create
                result = type_dict['type'].get_or_create(filter_key=filter_key, **values)
             
        return result


def is_element_valid(element, type_dict, check_required=True):
    """
    Are all provided arguments valid for this element type.
    Name and comment are valid for all. Key of dict should be
    the typeof element. Value is the data for the element.
    
    :param dict element: dict of element
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
        # Key is type, values are dict of values
        if key not in type_dict:
            return 'Unsupported element type: {} provided. Valid options {}'\
                .format(key, type_dict.keys())
        
        valid_values = type_dict.get(key).get('attr', [])
        provided_values = values.keys() if isinstance(values, dict) else []
        if provided_values:
            # Name is always required
            if 'name' not in provided_values:
                return 'Entry: {}, missing required name field'.format(key)
        
            for value in provided_values:
                if value not in valid_values:
                    return 'Entry with name {} has an invalid field: {}. '\
                        'Valid values: {} '.format(values['name'], value, valid_values)
            
            if check_required:
                required_arg = [arg for arg in valid_values if arg not in ('name', 'comment')]
                if required_arg: #Something other than name and comment fields
                    if not any(arg for arg in required_arg if arg in provided_values):
                        return 'Missing a required argument for {} entry, Valid values: {}'\
                            .format(values['name'], valid_values)
            
            if 'group' in element and values.get('members', []):
                for element in values['members']:
                    invalid = is_element_valid(element, type_dict, check_required=False)
                    if invalid:
                        return 'Invalid group member. {}'.format(invalid)
        else:
            return 'Entry type: {} has no values. Valid values: {} '\
                .format(key, valid_values)


def element_dict_from_obj(element, type_dict):
    """
    Resolve the element to the type and return a dict
    with the values of defined attributes
    
    :param Element element
    :return dict representation of the element
    """
    known = type_dict.get(element.typeof)
    if known:
        elem = {}
        for attribute in known.get('attr', []):
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
        smc_extra_args=dict(type='dict')
    )


def fact_argument_spec():
    return dict(
        filter=dict(type='str'),
        limit=dict(default=0, type='int'),
        exact_match=dict(default=False, type='bool'),
        case_sensitive=dict(default=True, type='bool')
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
            if params.get('smc_address') and params.get('smc_api_key'):
                extra_args = params.get('smc_extra_args')
                # When connection parameters are defined, alt_filepath is ignored.
                session.login(
                    url=params.get('smc_address'),
                    api_key=params.get('smc_api_key'),
                    api_version=params.get('smc_api_version'),
                    timeout=params.get('smc_timeout'),
                    domain=params.get('smc_domain'),
                    **(extra_args or {}))
            elif params.get('smc_alt_filepath'):
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
        
        

