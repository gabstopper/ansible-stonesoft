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


