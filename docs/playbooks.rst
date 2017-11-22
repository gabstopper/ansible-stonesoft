#########
Playbooks
#########

Playbooks can be run with the ansible-stonesoft package installed on a remote client machine, or directly from the SMC server.

When the ansible client is running the package locally (remote from the SMC), set up the inventory or use the `localhost` designation for the connection::

  - name: Retrieve all firewalls
    hosts: localhost
    gather_facts: no
    tasks:
    - name: get metadata for existing firewalls
      engine_facts:
        element: fw_clusters
  
If you want to run the playbooks remotely from the SMC but have the execution happen remotely, you will first need to ensure that the `smc-python` dependency library has been installed.

API Logging of playbook run
---------------------------

You can enable logging of smc-python API calls to file for a playbook run by adding the `smc_logging`
parameter to a playbook. The logging level is a valid int value per the standard python logging module:

.. code-block:: yaml

  - name: Get group to analyze members
    register: result
    network_element_facts:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      element: group
      filter: mygroup
      exact_match: yes
      expand:
        - group
 
This will provide additional visibility if an error should occur from the smc-python library to SMC.
