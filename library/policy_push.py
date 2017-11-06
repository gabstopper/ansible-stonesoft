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
module: policy_push
short_description: Deploy a policy to an engine
description:
  - Each NGFW engine requires that an existing policy be deployed. In addition,
    when making changes, policy will need to be refreshed. When retrieving engine
    facts, you can determine from the pending_changes key whether a policy refresh
    if required. In addition, specifying the policy in the playbook forces the
    specified policy to be deployed.

version_added: '2.5'

options:
  name:
    description:
      - Name of the engine to deploy policy on
  policy:
    description:
      - A policy to deploy. If the engine does not have an existing policy
        then specifying a policy is required. If an engine has an existing
        policy, a refresh of that existing policy is done.
    type: str
  sleep:
    description:
      - Amount of time to sleep between checking the task status
    type: int
    default: 3 sec
  max_tries:
    description:
      - Max number of times to loop through status checks. In case the policy
        is in 'wait' status (i.e. no connectivity to engine), this will only
        block for max_tries * sleep
    type: int
    default: 36
  wait_for_finish:
    description:
      - Whether to wait for the task to finish before returning
    type: bool
    default: true

extends_documentation_fragment: stonesoft

requirements:
  - smc-python

author:
  - David LePage (@gabstopper)
'''


EXAMPLES = '''
- name: Refresh policy and wait for task to complete
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Refresh policy
    policy_push:
      name: master-eng
      wait_for_finish: yes
      max_tries: 10
      sleep: 3
      
- name: Upload a policy to an engine and wait for task
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Upload policy specified to engine
    policy_push:
      name: fw
      policy: fwpolicy
      wait_for_finish: yes
      max_tries: 10
      sleep: 3
'''

RETURN = '''
failed:
  description: Whether or not the task failed or not
  returned: always
  type: bool
msg:
  description: Message returned when policy task returns
  return: always
  type: str
'''


import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase


try:
    from smc.core.engine import Engine
    from smc.api.exceptions import SMCException
except ImportError:
    pass


class PolicyDeploy(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            policy=dict(type='str'),
            sleep=dict(default=3, type='int'),
            max_tries=dict(default=36, type='int'),
            wait_for_finish=dict(type='bool', default=True),
        )
        
        self.name = None
        self.policy= None
        self.sleep = None
        self.max_tries = None
        self.wait_for_finish= None
        
        self.results = dict(
            failed=False,
            msg=''
        )
        super(PolicyDeploy, self).__init__(self.module_args)
    
    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        failed = False
        
        try:
            engine = Engine.get(self.name)
            msg = ''
            # If policy is defined, run an upload on the policy
            # TODO: Address situation where policy is queued for
            # uninitialized engine and attempted twice. This will
            # succeed but SMC 6.3 will return ''
            if self.policy:
                if self.wait_for_finish:
                    task = engine.upload(
                        self.policy,
                        timeout=self.sleep,
                        wait_for_finish=True,
                        max_tries=self.max_tries)
                    
                    while not task.done():
                        task.wait(self.sleep)
                    
                    msg = task.last_message()
                
                else:
                    task = engine.upload(self.policy)
                    
                    if task.task.in_progress:
                        msg = 'Task upload currently in progress. Check the engine ' \
                            'facts to determine if any pending changes remain.'
                    else:
                        msg ='Task did not report positive status when starting. ' \
                            'Returned status was %s' % task.last_message()
                        failed = True

            else: # A refresh of already installed policy
                if engine.installed_policy:
                    if self.wait_for_finish:
                        task = engine.refresh(
                            timeout=self.sleep,
                            wait_for_finish=True,
                            max_tries=self.max_tries)
                        
                        while not task.done():
                            task.wait(self.sleep)
                    
                        msg = task.last_message()
                    else:
                        if engine.installed_policy:
                            task = engine.refresh()
                            
                            if task.task.in_progress:
                                msg = 'Task refresh currently in progress. Check the engine ' \
                                    'facts to determine if any pending changes remain.'
                            else:
                                msg ='Task did not report positive status when starting. ' \
                                    'Returned status was %s' % task.last_message()
                                failed = True
                else:
                    msg = 'Engine does not currently have a policy assigned, you must ' \
                        'specify a policy to upload before refreshing policy.'
                    failed = True
                        

            self.results['msg'] = msg

        except SMCException as err:
            self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['failed'] = failed
        return self.results
    

def main():
    PolicyDeploy()
    
if __name__ == '__main__':
    main()


