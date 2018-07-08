Firewall NAT Rule
#################

Firewall NAT rules in SMC can be created, modified or deleted. Rules can also be fetched in various ways outlined in the documentation below.
Logic for creating a NAT rule is similar to creating a firewall rule with some subtle differences.

.. note:: Specifying sources, destinations and services is identical to creating a normal firewall rule. See also: :ref:`Firewall Rule <firewall_rule>` module

.. warning:: Modifying a NAT rule is not supported by the SMC API until version >= 6.4.3. If using an earlier version of SMC, remove and recreate the
  rule to workaround modifications

Creating, Modifying or Deleting Firewall NAT Rules
==================================================

Firewall NAT policy rules can be created, modified or deleted based on the playbook configuration. See the sections below for details on each operation type.

Creating a NAT rule requires basic information as documented by the :ref:`Firewall NAT Rule <firewall_nat_rule>` module.

An operation will be considered a 'create' if the playbook definition does not provide the 'tag' attribute. The 'tag' attribute is a unique identifier for an existing rule that uniquely identifies the rule since rule names can be identical. Therefore, if a rule definition in a playbook has the tag attribute, it will be considered a 'modify' operation.

.. note:: The 'tag' field of an existing rule is 'read-only' and only uniquely identifies the rule. It does not specify the rule position in a rule set.

Setting 'present' on the playbook `state` attribute is required to create or modify a rule. If the state is `absent`, the operation will be considered a delete operation and will use the rule tag identifier to find the correct rule to delete.

NAT rule types
--------------

There are 3 NAT type rules that can be created:

* **dynamic_src_nat**: A dynamic source NAT translates the source field element to a value and allows port address translation (PAT) to be defined. This NAT type is commonly used to
  for outbound traffic
  
* **static_src_nat**: A static source NAT translates a defined source field element to a specific value (1-to-1 NAT). 

* **static_dst_nat**: A static destination NAT translates a defined destination field element to a specific value. You can also define ports that you want to translate from source to
  destination. This NAT type is commonly used to define inbound traffic, for example to DMZ web services.
  
  The port definitions can be either single ports for translation (i.e. translate
  port 80 to 8080) or a range of ports (translate ports 1-10 to 90-100). If using port range translation, the port range lengths must be equal.
  
It is also possible to create a NAT rule that does NOT define one of the NAT types specified above. If creating a NAT rule without a NAT type specified, the rule is an explicit "no NAT" rule.

The following examples will illustrate how to define each NAT type.


**Create a no NAT rule**

If it is required to create a rule to explicitly disable NAT, you can create a NAT rule that doesn't specify a NAT type:

.. code-block:: yaml

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: null
      destinations:
        any: true
      is_disabled: false
      name: My no nat rule
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
        
**Create a dynamic source NAT rule**

Create a dynamic source NAT rule that also defines a range of ports for PAT. In this example, the source `host` element 'host-3.3.3.3' to
any destination is translated to another `host` element 'host-4.4.4.4' and PAT is defined to use ports 1024-65535:

.. code-block:: yaml

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: null
      destinations:
        any: true
      dynamic_src_nat:
        automatic_proxy: true
        translated_value:
          max_port: 65535
          min_port: 1024
          name: host-4.4.4.4
          type: host
      is_disabled: false
      name: dynamic source nat rule
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
        
**Create a static source NAT rule**

Create a static source NAT rule that translates the `host` element 'host-4.4.4.4' to the IP address '1.1.1.1':

.. code-block:: yaml 
  
  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: null
      destinations:
        any: true
      is_disabled: false
      name: my static source nat rule
      services:
        any: true
      sources:
        host:
        - host-4.4.4.4
     static_src_nat:
       automatic_proxy: true
       translated_value:
         ip_descriptor: 1.1.1.1
  
**Create a static destination NAT rule**

Create a destination NAT rule that translates the destination `host` element 'host-3.3.3.3' to the IP address '1.1.1.1'. It also
translates the inbound port 90 to 9999:

.. code-block:: yaml

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: testcomment
      destinations:
        host:
        - host-3.3.3.3
      is_disabled: false
      name: my destination nat rule
      services:
        any: true
      sources:
        any: true
      static_dst_nat:
        automatic_proxy: true
        original_value:
          max_port: 90
          min_port: 90
        translated_value:
          ip_descriptor: 1.1.1.1
          max_port: 9999
          min_port: 9999
     
.. note:: If ports are omitted, the ports defined by the services are translated 1-to-1

**Create a source NAT and destination NAT rule**

It is possible to also create a NAT rule that defines both a source and destination NAT.
This example does a source NAT on the `host` element 'host-3.3.3.3' and translates it to '3.3.3.10'.
When the destination is the `host` element 'somehost', the destination is translated to '10.10.10.10'.
No port translation is defined:

.. code-block:: yaml

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: null
      destinations:
        host:
        - somehost
      is_disabled: false
      name: Rule @315.1
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
      static_dst_nat:
        automatic_proxy: true
        translated_value:
          ip_descriptor: 10.10.10.10
      static_src_nat:
        automatic_proxy: true
        translated_value:
          ip_descriptor: 3.3.3.10


**Inserting rules in a specific position**

It is also possible to add a rule after or before another specified rule using the target rules tag field. It is recommended that when you
want rules inserted in a specific position, you locate the rule to insert 'before' or 'after' and specify that in the rule yaml.
When rules are added, without a position they will be added in position #1 (top of the rule list).

Using that logic, if you have multiple rules that should all be inserted in a specific order somewhere in the rule list, one strategy is
to fetch the existing policy to locate the rule tag which will act as the insert point. 
Then list your rules in the yaml from lowest in the list to highest, with all using the same add_after rule tag.

This example shows inserting a deny all rule after rule with a specific tag:

.. note:: By default rules are always inserted at the top of the policy unless specified otherwise

.. code-block:: yaml         

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: null
      destinations:
        any: true
      is_disabled: false
      name: My no nat rule
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
      add_after: '2097193.0'
      
More examples can be found in the playbooks directory.

Modifying a rule
----------------

Modifying a rule consists of first retrieving the rule, making modifications, and re-running the playbook. Retrieving the rule can be done using the techniques describes below in :ref:`Finding Firewall Rules <finding_firewall_rule>`.

Once you have retrieved the rule, you will notice a 'tag' field. This is a unique identifier for each rule. Rule names are not unique and rules can have the same rule name. Hence when a playbook is run on a rule that has a 'tag' value, the operation will be considered a modify.

To modify rules, once the rule has been retrieved, the content will look similar to the following:

.. code-block:: yaml

  firewall_nat_rule:
    policy: TestPolicy
    rules:
    - comment: modified comment
      destinations:
        host:
        - somehost
      is_disabled: true
      name: myrule
      services:
        any: true
      sources:
        host:
        - host-3.3.3.3
      static_dst_nat:
        automatic_proxy: true
        translated_value:
          ip_descriptor: 10.10.10.10
      tag: '123456.0'

Make the modifications and resubmit the retrieved yaml.

.. note:: This will be a no-op if the rule could not be found based on the rule tag value provided. In addition, this will change the rule tag
 of the original rule so a refetch will be necessary to operate on the rule again.
 

Deleting a rule
---------------

Deleting a firewall rule can be done by setting *state=absent* on the playbook.
You must also pre-fetch the rule in order to validate deleting the correct rule. Rules are identified by the 'tag' attribute returned after fetching the rule since
rule names are not unique.

Example of deleting a rule by rule tag after fetching (and removing other unneeded attributes):

.. code-block:: yaml

 - name: Task output
   firewall_nat_rule:
     policy: TestPolicy
     rules:
     -   tag: '2097203.0'
     state: absent
    
Generally you might want to search for the particular rule of interest using firewall_rule_facts to narrow the search, return the results in yaml
and delete.


Finding Firewall NAT Rules
==========================

Finding NAT rules is the same as finding normal firewall rules: :ref:`Finding Firewall Rules <finding_firewall_rule>`.


