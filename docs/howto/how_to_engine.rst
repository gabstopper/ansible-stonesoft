Engine
######

Engine represents the module responsible for modifying, creating and removing NGFW engines from the SMC. Engine is a generic term used to represent a managed device in the SMC whether it's a physical hardware, virtual or cloud instance.

Engines can be created as single layer 3 or clustered layer 3 configurations and provide many options to configure ancillary features such as antivirus, file reputation and default NAT, as well as core engine functionality such as OSPF, BGP, Netlinks and antispoofing.


Creating and modifying engines
==============================

Supported engine types are current layer 3 single FW's and layer 3 cluster firewall's.
The simplest way to create an engine is to observe a pre-existing engines configuration. If you retrieve and existing engine using
:ref:`Engine Facts <engine_facts>` and output as yaml, you can adjust the output to represent how you would like the new engine
created.

Once an engine is created, you can retrieve it's configuration using engine_facts and make adjustments to the configuration by adding
or removing within the configuration areas. 

It is important to note that all ansible runs will first run through a validation against any elements that are required by the
configuration and expected to pre-exist. A playbook run will always fail when the element referenced is not found. Take note of
specific configuration areas that require pre-existing elements and use the relevant playbooks to pre-create the dependencies.


Deleting engines
================

Deleting engines is as easy as providing the name of the engine and the `state=absent` attribute:

.. code-block:: yaml

  - name: delete firewall by name
    engine:
      name: myfirewall
      state: 'absent'


Engine actions (commands)
=========================

Engine actions allow you to 'command' a given node to perform some action. Common actions might be reboot, go_online, go_offline,
initial_contact, bind_license, etc.
All engine actions can be performed using the :ref:`Engine Actions <engine_action>` module.

Example of generating an initial contact configuration for an uninitialized node and showing the output:

.. code-block:: yaml

  - name: Firewall Actions
    hosts: localhost
    gather_facts: no
    tasks:
    - name: Generate initial config
      register: command_output
      engine_action:
        name: myfw3
        nodeid: 1
        action: initial_contact
        extra_args:
          enable_ssh: true
          as_base64: true
  
    - debug: msg="{{ command_output.msg }}"
 
Reboot a given node:
 
.. code-block:: yaml
 
  - name: Firewall Actions
 	 hosts: localhost
    gather_facts: no
    tasks:
    - name: Reboot node 1
      engine_action:
        name: myfw3
        nodeid: 1
        action: reboot
        extra_args:
          comment: my reboot comment


There are many more options available in the :ref:`Engine Actions <engine_action>` module.
Node actions and available arguments are also documented as part of
`smc-python <http://smc-python.readthedocs.io/en/latest/pages/reference.html#module-smc.core.node>`_.


Finding existing engines
========================

Finding an engine is done through the :ref:`Engine Facts <engine_facts>` module. Like all other fact modules, you can find top level results returning only metadata or
more detailed information. Often it's useful to retrieve an existing engine and output that into YAML format to show the current state,
then make modifications and replay the playbook.

An example of retrieving an existing firewall named 'myfw', outputting as yaml using the templates/engine_yaml jinja template and saving
to a new file named l3fw.yml.

.. code-block:: yaml

  - name: Get engine details for 'myfw'
    register: results
      engine_facts:
        filter: myfw
        as_yaml: true

  - name: Write the yaml using a jinja template
    template: src=templates/engine_yaml.j2 dest=./l3fw.yml


Retrieving engine appliance details
===================================

Finding information such as the engine status, interface information, and filesystem utilization can be done by using
the :ref:`Engine Appliance Facts <engine_appliance_facts>` module. Information can be returned for any engine of any type.
It is only required to specify the name of the engine when retrieving facts.

Provide a basic yaml configuration to request the information based on desired criteria.

Return information about all nodes of a specific engine:

.. code-block:: yaml

  - name: Retrieve all stats (hardware, interface, status)
    engine_appliance_facts:
      filter: sg_vm


You can also specify only certain items to be retrieved. This example is redundant as status, filesystem and
interfaces will be returned if `items` is not present, however it shows that you can control what is returned.
Example of retrieving this information only for node 1:

.. code-block:: yaml

  - name: Retrieve all stats (hardware, interface, status)
    engine_appliance_facts:
      filter: sg_vm
	  nodeid: 1
      items:
      - status
      - filesystem
      - interfaces


Adding engine routing components
================================

You can add routing elements to an engine such as BGP, OSPF, static routes, netlinks and antispoofing
configurations using the :ref:`Engine Routing <engine_routing>` module.

.. note:: Routing elements of type netlink, bgp peering and ospf can also be added directly on the engine
  itself using the `engine` playbook, however `engine_routing` provides the ability to add all routing element
  types.

Example of adding different routing elements to an engine:

.. code-block:: yaml

 - name: Engine routing elements
   hosts: localhost
   gather_facts: no
   tasks:
   - name: Add routing elements to engine sg_vm
     engine_routing:
       smc_logging:
         level: 10
         path: ansible-smc.log
       name: myfw4
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
 
See the playbooks directory for more examples.       


Retrieving engine routing
=========================

To retrieve routes, use the :ref:`Engine Routing Facts <engine_routing_facts>` module.
Simply provide the name of the engine and the existing engine level routes will be returned:

.. code-block:: yaml

  - name: Retrieve engine routes from sg_vm
    engine_routing_facts:
      filter: sg_vm

.. note:: Retrieving engine routes calls the engine from the SMC and asks for the routing table directly.
  The output of this is based on what you might see from the engine if running `netstat -nr`.

