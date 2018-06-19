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
module: engine_action
short_description: Node level actions on an engine

description:
  - Perform a node level action on the engine such as go_online, go_offline,
    generate initial_contact, reboot, etc

version_added: '2.5'

options:
  name:
    description:
      - Provide the name of the engine for which to perform a node operation
    type: str
    required: true
  nodeid:
    description:
      - Provide a nodeid for the engine node to perform the action. For single FWs this
        is not required and will default to nodeid 1. For clusters, each node has a nodeid
        to represent which node to operate on
    type: int
    default: 1
  actions:
    description:
      - Action to perform against the engine node. Some actions will optionally have additional
        arguments that can be provided
    type: str
    choices:
    - initial_contact
    - reboot
    - power_off
    - reset_to_factory
    - sginfo
    - ssh
    - change_ssh_pwd
    - time_sync
    - fetch_license
    - bind_license
    - unbind_license
    - cancel_unbind_license
    - go_offline
    - go_online
    - go_standby
    - lock_online
    - lock_offline
    - reset_user_db
  extra_args:
    description:
      - Extra arguments to provide to action constructor. Arguments documented only show
        action choices that have specific extra args that are useful when calling the action
        Constructor arguments are documented at
        U(http://smc-python.readthedocs.io/en/latest/pages/reference.html#module-smc.core.node)    
    type: dict

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
- name: Generate an initial contact configuration in base64 format
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Layer 3 FW template
    register: command_output
    engine_action:
      smc_logging:
        level: 10
        path: ansible-smc.log
      name: myfw3
      nodeid: 1
      action: initial_contact
      extra_args:
        enable_ssh: true
        as_base64: true
  
  - debug: msg="{{ command_output.msg }}"
  
- name: Reboot node 1
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Layer 3 FW template
    engine_action:
      name: myfw3
      nodeid: 1
      action: reboot
      extra_args:
        comment: reboot fw log entry

'''
RETURN = '''
state:
    description: appliance status after performing the action
    returned: always
    type: dict
    sample: {
        "configuration_status": "Declared", 
        "dyn_up": null, 
        "installed_policy": null, 
        "name": "myfw3 node 1", 
        "platform": "N/A", 
        "state": "NO_STATUS", 
        "status": "Not Monitored", 
        "version": "unknown"
    }
msg:
    description: message attribute will be empty except for initial contact
    returned: always
    type: str
'''


import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, allowed_args


try:
    from smc.core.engine import Engine
    from smc.api.exceptions import SMCException, NodeCommandFailed
except ImportError:
    pass

    
actions = ('initial_contact',
           'reboot', 'power_off', 'reset_to_factory',
           'sginfo','ssh', 'change_ssh_pwd', 'time_sync',
           'fetch_license', 'bind_license', 'unbind_license', 'cancel_unbind_license',
           'go_offline', 'go_online', 'go_standby',
           'lock_online', 'lock_offline',
           'reset_user_db')
                

class StonesoftEngineAction(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            nodeid=dict(type='int', default=1),
            action=dict(type='str', required=True, choices=actions),
            extra_args=dict(type='dict', default={}))
        
        self.extra_args = None
        self.nodeid = None
        
        self.results = dict(
            changed=False,
            state=[]
        )
        super(StonesoftEngineAction, self).__init__(self.module_args, supports_check_mode=False)
        
    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        result = ''
        try:
            engine = Engine(self.name)
            node = engine.nodes.get(self.nodeid)
            if not node:
                raise SMCException('Node specified for action %r was not found. This engine '
                    'has %s nodes (numbering starts at 1)' % (self.action, len(engine.nodes)))
            
            self.check_provided_args(node, self.action)
            
            # Run command
            result = getattr(node, self.action)(**self.extra_args)
            self.results['changed'] = True
#             if self.action == 'initial_contact':
#                 self.results['state'].append(
#                     node.initial_contact(**self.extra_args))
#                 #enable_ssh=True, time_zone=None, 
#                 #keyboard=None, 
#                 #filename=None, 
#                 #as_base64=False
#             elif self.action == 'change_ssh_pwd':
#                 pass 
#                 # pwd
#             elif self.action == 'sginfo':
#                 pass
#                 #include_core_files=False, 
#                 #include_slapcat_output=False, 
#                 #filename='sginfo.gz'
#             elif self.action == 'ssh':
#                 pass
#                 # enabled
#             elif self.action == 'bind_license':
#                 pass
#                 #license_item_id
            self.results['state'] = self.get_state_after_action(node)
        
        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['msg'] = result   
        return self.results
    
    def get_state_after_action(self, node):
        """
        Get the configuration status after the appliance
        action for the state attribute
        
        :rtype: dict
        """
        try:
            return node.health._asdict()
        except NodeCommandFailed:
            return {}
        
    def check_provided_args(self, node, operation):
        allowed = allowed_args(node, operation)
        for arg in self.extra_args:
            if arg not in allowed:
                self.fail(msg='Invalid argument provided to node action %r. Valid arguments '
                    'for this action are %s' % (arg, allowed))

    
def main():
    StonesoftEngineAction()
    
if __name__ == '__main__':
    main()

