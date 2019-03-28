#!/usr/bin/python
#
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: engine_appliance_facts
short_description: Facts about engine appliances such as hardware and interface status
description:
  - Retrieve specific information about a particular engine node or all nodes of an engine.
    Information that can be obtained is general information about the node itself as well
    as general information such as filesystem utilization, interfaces and statuses and
    current routing table.

version_added: '2.5'

options:
  filter:
    description:
      - Provide the name of the engine as a filter
    type: str
    required: true
  nodeid:
    description:
      - Only return the details of a specific node by ID. If not provided, all node info
        is returned
    type: int
  items:
    description:
      - If it is preferable to view only specific node level items you can provide a list
        of those individually. If items is omitted all items will be returned
    type: list
    choices:
    - status
    - interfaces
    - filesystem

extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python >= 0.6.0
author:
  - David LePage (@gabstopper)
'''
        

EXAMPLES = '''
- name: Retrieve all stats (hardware, interface, info) for engine sg_vm
  engine_appliance_facts:
    filter: sg_vm

- name: Retrieve all stats (hardware, interface, info) on for node 1
  engine_appliance_facts:
    filter: sg_vm
    nodeid: 1

- name: Retrieve all stats (hardware, interface, info) for node 1 using items
  engine_appliance_facts:
    filter: sg_vm
    nodeid: 1
    items:
    - status
    - filesystem
    - interfaces

- name: Only retrieve engine status facts
  engine_appliance_facts:
    filter: sg_vm
    nodeid: 1
    items:
    - status
'''


RETURN = '''
engines:
    description: List of nodes and statuses
    returned: always
    type: list    
    sample: [{
        "filesystem": [
            {
                "label": "Root", 
                "param": "Partition Size", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "600 MB"
            }, 
            {
                "label": "Data", 
                "param": "Usage", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "9.8%"
            }, 
            {
                "label": "Data", 
                "param": "Size", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "1937 MB"
            }, 
            {
                "label": "Spool", 
                "param": "Usage", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "14.2%"
            }, 
            {
                "label": "Spool", 
                "param": "Size", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "3288 MB"
            }, 
            {
                "label": "Tmp", 
                "param": "Usage", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "0.0%"
            }, 
            {
                "label": "Tmp", 
                "param": "Size", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "1926 MB"
            }, 
            {
                "label": "Swap", 
                "param": "Usage", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "7.4%"
            }, 
            {
                "label": "Swap", 
                "param": "Size", 
                "status": -1, 
                "sub_system": "File Systems", 
                "value": "943 MB"
            }, 
            {
                "label": "Log rates (average over 30 s)", 
                "param": "Sending (entries / s)", 
                "status": -1, 
                "sub_system": "Logging subsystem", 
                "value": "21"
            }
        ], 
        "interfaces": [
            {
                "aggregate_is_active": false, 
                "capability": "Normal Interface", 
                "flow_control": "AutoNeg: off Rx: off Tx: off", 
                "interface_id": 0, 
                "mtu": 1500, 
                "name": "eth0_0", 
                "port": "Copper", 
                "speed_duplex": "1000 Mb/s / Full / Automatic", 
                "status": "Up"
            }, 
            {
                "aggregate_is_active": false, 
                "capability": "Normal Interface", 
                "flow_control": "AutoNeg: off Rx: off Tx: off", 
                "interface_id": 1, 
                "mtu": 1500, 
                "name": "eth0_1", 
                "port": "Copper", 
                "speed_duplex": "1000 Mb/s / Full / Automatic", 
                "status": "Up"
            }, 
            {
                "aggregate_is_active": false, 
                "capability": "Normal Interface", 
                "flow_control": "AutoNeg: off Rx: off Tx: off", 
                "interface_id": 2, 
                "mtu": 1500, 
                "name": "eth0_2", 
                "port": "Copper", 
                "speed_duplex": "1000 Mb/s / Full / Automatic", 
                "status": "Up"
            }, 
            {
                "aggregate_is_active": false, 
                "capability": "Normal Interface", 
                "flow_control": "AutoNeg: off Rx: off Tx: off", 
                "interface_id": 3, 
                "mtu": 1500, 
                "name": "eth0_3", 
                "port": "Copper", 
                "speed_duplex": "Half / Automatic", 
                "status": "Down"
            }
        ], 
        "name": "ngf-1035", 
        "nodeid": 2, 
        "status": {
            "cloud_id": "N/A", 
            "cloud_type": "NONE", 
            "configuration_status": "Installed", 
            "dyn_up": "1070", 
            "first_upload_time": 0, 
            "hardware_version": "79.1", 
            "initial_contact_time": "2016-03-08T21:28:02.263000", 
            "initial_license_remaining_days": 0, 
            "installed_policy": "Standard Firewall Policy with Inspection", 
            "name": "ngf-1035", 
            "platform": "x86-64-small", 
            "product_name": "1035-1-C1", 
            "proof_of_serial": "xxxxxxxx-xxxxxxxxxx", 
            "software_features": "SECNODE+ALLOWX64=YES+ANTISPAM=YES+ANTIVIRUS=YES+DYNAMIC_ROUTING=YES+USERS=YES+URL_SERVICE2=YES+DEVICECLASS=100+VPN=YES", 
            "software_version": "5.7", 
            "state": "READY", 
            "status": "Online", 
            "version": "version 6.4.1 #20056"
        }
    }]
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.base.util import datetime_from_ms
    from smc.api.exceptions import NodeCommandFailed, EngineCommandFailed
except ImportError:
    pass


def get_status(node):
    """
    Get the appliance info for the given node
    
    :param Node node: node from engine
    :rtype: dict
    """
    info = node.appliance_info()._asdict()
    info.update(
        initial_contact_time=datetime_from_ms(
            info.pop('initial_contact_time')))
    info.update(node.health._asdict())
    return info


def get_filesystem(node):
    """
    Get the file system information about this node
    
    :param Node node: engine node
    :rtype: dict
    """
    hw = node.hardware_status
    all_status = []
    for fs in hw.filesystem:
        all_status.append(fs._asdict())
    for lg in hw.logging_subsystem:
        all_status.append(lg._asdict())
    return all_status
    

def get_interfaces(node):
    """
    Get interface information about this node
    
    :param Node node: node from engine
    :rtype: dict
    """
    ifaces = node.interface_status
    return [iface._asdict() for iface in ifaces]

    
def get_all_stats(node):
    _node = {}
    _node.update(status=get_status(node))
    _node.update(interfaces=get_interfaces(node))
    _node.update(filesystem=get_filesystem(node))
    return _node


def get_by_items(node, items):
    """
    Prefilter to get based on items.
    
    :param Node node: node reference
    :param list items: items to filter on if any
    :rtype: dict
    """
    _node = {}
    _node.update(name=node.name, nodeid=node.nodeid)
    if not items:
        _node.update(get_all_stats(node))
        return _node
    for item in items:
        _node[item] = globals()['get_%s' % item](node)
    return _node
    

items = ('status', 'interfaces', 'filesystem')
                    
 
class EngineApplianceFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            filter=dict(type='str', required=True),
            nodeid=dict(type='int'), # All nodes if not specified
            items=dict(type='list', default=[])
        )
    
        self.element = 'engine_clusters'
        self.nodeid = None
        self.items = None # Filters to only obtain specific details
        self.limit = None
        self.filter = None # Engine name
        self.as_yaml = None # Ignored for this fact type
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                engines=[]
            )
        )
        super(EngineApplianceFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        for _item in self.items:
            if _item not in items:
                self.fail(msg='Invalid appliance item specified: %s. Valid item '
                    'types are %s.' % (_item, list(items)))
        
        engine = self.search_by_context()
        if not engine:
            self.fail(msg='Specified engine does not exist: %s' % self.filter)
        
        nodes = []
        try:
            if self.nodeid:
                node = engine[0].nodes.get(self.nodeid)
                if not node:
                    self.fail(msg='Nodeid %s specified does not exist on this engine: %s'
                        % (self.nodeid, engine[0].name))
                nodes.append(get_by_items(node, self.items))
                
            else:
                for node in engine[0].nodes:
                    nodes.append(get_by_items(node, self.items))
        
        except NodeCommandFailed as e:
            self.fail(msg='%s. This can occur if the engine has not yet been '
                'initialized. Try using the %r item to retrieve the SMC state of '
                'the node' % (str(e), 'status'))
        except EngineCommandFailed as e:
            self.fail(msg=str(e))

        self.results['ansible_facts']['engines'] = nodes
        return self.results

def main():
    EngineApplianceFacts()
    
if __name__ == '__main__':
    main()