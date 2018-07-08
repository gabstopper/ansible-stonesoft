Firewall Rule
#############

Firewall rules in SMC can be created, modified or deleted. Rules can also be fetched in various ways outlined in the documentation below.

Creating, Modifying or Deleting Firewall Rules
==============================================

Firewall policy rules can be created, modified or deleted based on the playbook configuration. See the sections below for details on each operation type.

Creating a rule
---------------

Creating a rule requires basic information as documented by the :ref:`Firewall Rule <firewall_rule>` module.

An operation will be considered a 'create' if the playbook definition does not provide the 'tag' attribute. The 'tag' attribute is a unique identifier for an existing rule that uniquely identifies the rule since rule names can be identical. Therefore, if a rule definition in a playbook has the tag attribute, it will be considered a 'modify' operation.

.. note:: The 'tag' field of an existing rule is 'read-only' and only uniquely identifies the rule. It does not specify the rule position in a rule set.

Setting 'present' on the playbook `state` attribute is required to create or modify a rule. If the state is `absent`, the operation will be considered a delete operation and will use the rule tag identifier to find the correct rule.

**Basic rule creation**

The minimalist example of creating a rule is providing only the `name` field. If sources, destinations or services are not provided, the default
value is 'any'. If action is not provided, the default setting is 'allow'::

 - name: 
   hosts: localhost
   gather_facts: no
   tasks:
   - name: Task output
     firewall_rule:
       policy: TestPolicy
       rules:
       -   name: foo

You can create much more detailed rules by using other options within the firewall rule module.

**Creating more detailed rules**

An example of creating a basic continue rules that allows all logging at the beginning of a ruleset:

.. code-block:: yaml

 - name: Task output
   register: result
   firewall_rule:
     policy: TestPolicy
     rules:
     -   action: continue
         comment: logging rule
         log_options:
           log_accounting_info_mode: true
           log_closing_mode: true
           log_level: stored
         is_disabled: false
         name: Log all continue rule
   
However, there are many more options available to create a rule, including setting connection tracking settings, inspection features, mss settings, and additional log settings. It is also possible to specify elaborate rules based on sources, destinations and services. Rule actions such as use_vpn, forward_vpn and apply_vpn, and jump_rules are supported.

Generally it is easier to retrieve an existing rule using and dumping to yaml, then making modifications to suit your requirements. See :ref:`Finding Firewall Rules <finding_firewall_rule>` for more information on retrieving existing rules.

**Customize all rule fields**

Example of creating a rule with specific destinations and service elements. All source, destination and service elements are documented in the
firewall_rule module. Elements can also be retrieved or created using the :ref:`Network Elements <network_element>` module.

.. note:: Source, destination and service elements are validated before any only operations are performed to 
 modify or create an element. The playbook run will fail on missing elements.
 
.. code-block:: yaml

 - name: 
   hosts: localhost
   gather_facts: no
   tasks:
   - name: Task output
     firewall_rule:
       policy: TestPolicy
       rules:
       -   action: allow
           comment: my comment
           connection_tracking:
               mss_enforced: true
               mss_enforced_max: 1555
               mss_enforced_min: 0
               timeout: 10
               state: normal
           destinations:
               group:
               - foogroup
               ip_list:
               - Amazon S3
               host:
               - host-1.1.1.1
               network:
               - foonet
           inspection_options:
               decrypting: null
               deep_inspection: null
               file_filtering: null
           is_disabled: false
           log_options:
               application_logging: enforced
               eia_executable_logging: 'off'
               log_accounting_info_mode: false
               log_closing_mode: true
               log_compression: 'off'
               log_level: none
               log_payload_additionnal: true
               log_payload_excerpt: false
               log_payload_record: false
               log_severity: -1
               user_logging: enforced
           authentication_options:
              methods: []
              require_auth: false
           name: ruletest2
           services:
               tcp_service:
               - AOL
               udp_service:
               - Biff
               ip_service:
               - CHAOS
           sources:
               engine:
               - myfw
               alias:
               - $$ Interface ID 0.ip
               country:
               - China

**Creating rules with authentication**

Rules can be created that specify authentication by setting the `authentication_options` dict on the rule.
When enabling authentication, you must provide the authentication method along with at least one reference to a user or group from an internal
user domain or an external ldap domain.

When specifying the user or group information, it is required to specify in full DN syntax as this is how users and groups are identified within
the SMC.

An simple example YAML for authentication might look like::

 authentication_options:
    groups:
    - dc=lepages,dc=local,domain=myldapdomain
    methods:
    - LDAP Authentication
    - Network Policy Server
    - User password
    require_auth: true
    users:
    - cn=test,dc=stonegate,domain=InternalDomain
    - cn=test2,dc=stonegate,domain=InternalDomain

This specifies that auth is required and several authentication methods are supported. In addition, two internal users and one external ldap
domain is allowed to authenticate (using the LDAP domains base DN).

   
**Creating VPN rules**
        
An example of creating a 'enforce_vpn' rule requires the use of the parameter `vpn_policy` along with one of the valid vpn actions.
In addition, the rule specifies a valid authentication service, sets `require_auth` to true and defines the base DN of the domain
to allow authentication:

.. code-block:: yaml

 - name: Task output
   register: result
   firewall_rule:
     smc_logging:
       level: 10
       path: ansible-smc.log
     policy: TestPolicy
     rules:
     -   action: enforce_vpn
         comment: my comment
         connection_tracking:
             mss_enforced: false
             mss_enforced_max: -1
             mss_enforced_min: -1
             timeout: -1
         destinations:
             any: true
         inspection_options:
             decrypting: true
             deep_inspection: true
             file_filtering: null
         is_disabled: false
         authentication_options:
             methods:
             - LDAP Authentication
             require_auth: true
             groups:
             - dc=lepages,dc=local,domain=myldapdomain
             users:
             - cn=myuser,dc=stonegate,domain=InternalDomain
         log_options:
             application_logging: default
             eia_executable_logging: default
             log_accounting_info_mode: true
             log_closing_mode: false
             log_compression: 'off'
             log_level: stored
             log_payload_additionnal: false
             log_payload_excerpt: false
             log_payload_record: false
             log_severity: -1
         name: ruletest2
         services:
             any: true
         sources:
             any: true
         vpn_policy: MOBILE CLIENT VPN

**Creating jump rules**

An example of creating a 'jump' rule requires the use of the parameter `sub_policy` along with the action of `jump`:

.. code-block:: yaml

 - name: Task output
   register: result
   firewall_rule:
     smc_logging:
       level: 10
       path: ansible-smc.log
     policy: TestPolicy
     rules:
     -   action: jump
         comment: my comment
         connection_tracking:
             mss_enforced: false
             mss_enforced_max: -1
             mss_enforced_min: -1
             timeout: -1
         destinations:
             any: true
         inspection_options:
             decrypting: null
             deep_inspection: null
             file_filtering: null
         is_disabled: false
         authentication_options:
              methods: []
              require_auth: false
              users: []
         log_options:
             application_logging: enforced
             eia_executable_logging: default
             log_accounting_info_mode: true
             log_closing_mode: false
             log_compression: 'off'
             log_level: stored
             log_payload_additionnal: false
             log_payload_excerpt: true
             log_payload_record: false
             log_severity: -1
             user_logging: 'true'
         name: ruletest2
         services:
             any: true
         sources:
             any: true
         sub_policy: mysubpolicy

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

 - name: Add a deny rule after specified rule using add_after syntax
  register: result
  firewall_rule:
    smc_logging:
      level: 10
      path: ansible-smc.log
    policy: TestPolicy
    rules:
    -   action: discard
        comment: deny rule
        is_disabled: false
        name: my deny
        add_after: '2097193.0'

.. note:: You can leave fields like log_options, inspection_options and connection_tracking out of the playbook run if there is no need to customize those settings.

More examples can be found in the playbooks directory.

Modifying a rule
----------------

Modifying a rule consists of first retrieving the rule, making modifications, and re-running the playbook. Retrieving the rule can be done using the techniques describes below in :ref:`Finding Firewall Rules <finding_firewall_rule>`.

Once you have retrieved the rule, you will notice a 'tag' field. This is a unique identifier for each rule. Rule names are not unique and rules can have the same rule name. Hence when a playbook is run on a rule that has a 'tag' value, the operation will be considered a modify.

To modify rules, once the rule has been retrieved, the content will look similar to the following:

.. code-block:: yaml

 - name: Task output
   register: result
   firewall_rule:
     smc_logging:
       level: 10
       path: ansible-smc.log
     policy: TestPolicy
     rules:
     -   action: continue
         comment: null
         connection_tracking:
             mss_enforced: false
             mss_enforced_max: 0
             mss_enforced_min: 0
             timeout: -1
         destinations:
             any: true
         inspection_options:
             decrypting: null
             deep_inspection: null
             file_filtering: null
         is_disabled: false
         log_options:
             log_accounting_info_mode: false
             log_closing_mode: true
             log_level: undefined
             log_payload_additionnal: false
             log_payload_excerpt: false
             log_payload_record: false
             log_severity: -1
         name: Rule @2097166.2
         services:
             any: true
         sources:
             any: true
         tag: '2097166.2'

When modifying rules you can also move a rule by using the `add_after` or `add_before` fields. For these fields to work, you must provide the 'tag' for
the rule you want to move the rule 'before' or 'after'. This will result in the rule being duplicated into the correct position and the original rule
removed. 

.. note:: This will be a no-op if the rule could not be found based on the rule tag value provided. In addition, this will change the rule tag
 of the original rule so a refetch will be necessary to operate on the rule again.

An example of modifying a rule and moving it into a new position:

.. code-block:: yaml

 - name: 
   hosts: localhost
   gather_facts: no
   tasks:
   - name: Task output
     register: result
     firewall_rule:
       policy: TestPolicy
       rules:
       -   action: allow
           destinations:
               host:
               - host-2.2.2.5
               network:
               - gateway_170.27.126.0/24
           is_disabled: false
           name: newruleinpos
           services:
               any: true
           sources:
               any: true
           tag: '2097164.19'
           add_after: '2097260.0'

See :ref:`Exporting a Firewall Rule into YAML <export_firewall_rule>` for more information on retrieving existing rules.


Deleting a rule
---------------

Deleting a firewall rule can be done by setting *state=absent* on the playbook.
You must also pre-fetch the rule in order to validate deleting the correct rule. Rules are identified by the 'tag' attribute returned after fetching the rule since
rule names are not unique.

Example of deleting a rule by rule tag after fetching (and removing other unneeded attributes):

.. code-block:: yaml

 - name: Task output
   firewall_rule:
     policy: TestPolicy
     rules:
     -   tag: '2097203.0'
     state: absent
    
Generally you might want to search for the particular rule of interest using firewall_rule_facts to narrow the search, return the results in yaml
and delete.

.. _finding_firewall_rule:

Finding Firewall Rules
======================

Layer 3 Firewall rule facts can be obtained by providing various filters for retrieving data.

The `filter` parameter is always required when obtaining rules, with `filter` specifying the Firewall Policy for which to retrieve the rules from.

There are varying details and options for retrieving rules. These are outlined in the next section.

**Retrieving only name and rule position (metadata):**

This is done by providing only a `filter` for to specify the rule policy. All rules are returned with only metadata.

.. code-block:: yaml

  - name: Rule tasks
    hosts: localhost
    gather_facts: no
    tasks:
    - name: Show rules for policy 'TestPolicy' (only shows name, type)
      firewall_rule_facts:
        filter: TestPolicy

This results in the following output::

 ok: [localhost] => {
    "ansible_facts": {
        "firewall_rule": [
            {
                "comment": null, 
                "policy": "TestPolicy", 
                "rules": [
                    {
                        "name": "Rule @2097166.2", 
                        "pos": 1, 
                        "type": "fw_ipv4_access_rule"
                    }, 
                    {
                        "name": "my@rule", 
                        "pos": 2, 
                        "type": "fw_ipv4_access_rule"
                    }, 

You can also obtain rules based a specific range of rules using the `rule_range` field. For example, you might want to grab the first 5 rules, or rules 10-15 to limit the search.

**Retrieving rule based on rule range:**

.. code-block:: yaml

 - name: Get specific rules based on range order (rules 1-3)
   firewall_rule_facts:
     filter: TestPolicy
     rule_range: 1-3

Resulting in the following output::

 ok: [localhost] => {
    "ansible_facts": {
        "firewall_rule": [
            {
                "comment": null, 
                "policy": "TestPolicy", 
                "rules": [
                    {
                        "name": "Rule @2097166.2", 
                        "type": "fw_ipv4_access_rule"
                    }, 
                    {
                        "name": "ruletest", 
                        "type": "fw_ipv4_access_rule"
                    }, 
                    {
                        "name": "Rule @2097168.0", 
                        "type": "fw_ipv4_access_rule"
                    }
                ]
            }
        ]
    }

.. note:: `rule_range` and `search` are mutually exclusive operations


Many times it is necessary to get more details about the rule configuration itself and you may even know the name of the rule you are looking for.
If the rule name is known, you can provide the parameter `search` with a keyword that will be used as a wildcard to find any rules with this content in the name or comment field of a rule.

**Retrieving rule based on search string:**

.. code-block:: yaml

  - name: Search for specific rule/s using search value (partial searching supported)
    firewall_rule_facts:
      filter: TestPolicy
      search: rulet

.. note:: Searching may return multiple results

This results in the following output::

 ok: [localhost] => {
    "ansible_facts": {
        "firewall_rule": [
            {
                "comment": null, 
                "policy": "TestPolicy", 
                "rules": [
                    {
                        "name": "ruletest", 
                        "type": "fw_ipv4_access_rule"
                    }
                ]
            }
        ]
    }

This still only tells us that the a rule was found but no details about the contents of the rule.

The `as_yaml` parameter is available that provides the ability to 'dump' the contents of the rule into a format that can be re-used in a playbook or alternatively just dumped into a result register. 

**Retrieving more details about the rule:**

Adding the `as_yaml` parameter to obtain more detail about a rule:

.. code-block:: yaml

 - name: Dump the results in yaml format, showing details of rule
   firewall_rule_facts:
     filter: TestPolicy
     search: rulet
     as_yaml: true

The output from the run now contains must more data and the specifics about the rule itself::

 ok: [localhost] => {
    "ansible_facts": {
        "firewall_rule": [
            {
                "comment": null, 
                "policy": "TestPolicy", 
                "rules": [
                    {
                        "action": "allow", 
                        "comment": null, 
                        "connection_tracking": {
                            "mss_enforced": false, 
                            "mss_enforced_max": 0, 
                            "mss_enforced_min": 0, 
                            "state": "no", 
                            "timeout": -1
                        }, 
                        "destinations": [
                            "https://1.1.1.1:8082/6.4/elements/host/942", 
                            "https://1.1.1.1:8082/6.4/elements/host/944", 
                            "https://1.1.1.1:8082/6.4/elements/host/948", 
                            "https://1.1.1.1:8082/6.4/elements/network/3969"
                        ], 
                        "inspection_options": {
                            "decryption": false, 
                            "deep_inspection": false, 
                            "file_filtering": false
                        }, 
                        "is_disabled": false, 
                        "logging": {
                            "application_logging": "enforced", 
                            "eia_executable_logging": "off", 
                            "log_accounting_info_mode": true, 
                            "log_closing_mode": false, 
                            "log_compression": "off", 
                            "log_level": "stored", 
                            "log_payload_additionnal": false, 
                            "log_payload_excerpt": false, 
                            "log_payload_record": false, 
                            "log_severity": -1, 
                            "user_logging": "enforced"
                        }, 
                        "name": "ruletest", 
                        "services": [
                            "https://1.1.1.1:8082/6.4/elements/ip_service/58", 
                            "https://1.1.1.1:8082/6.4/elements/icmp_service/312", 
                            "https://1.1.1.1:8082/6.4/elements/tcp_service/358", 
                            "https://1.1.1.1:8082/6.4/elements/tcp_service/468", 
                            "https://1.1.1.1:8082/6.4/elements/udp_service/541", 
                            "https://1.1.1.1:8082/6.4/elements/udp_service/551"
                        ], 
                        "sources": {
                            "any": true
                        }, 
                        "tag": "2097164.14"
                    }
                ]
            }
        ]
    }

However, you will notice that certain fields, `sources`, `destinations` and `services` will contain href's that specify the location of the element but not the actual element itself by type or name. 
To obtain the resolved information for the elements, you can alternatively provide a parameter `expand` which is a list of fields to resolve into element and types.

.. note:: Expanding HREFs will result in a single SMC query per element href and is therefore only recommended in a limited fashion. For example, expanding all rules in a rule list of 100 rules will likely result in hundreds of queries against the SMC. It is recommended to narrow your search before expanding fields.

**Expanding href fields in a facts run:**

Add the `expand` field list to the existing playbook to provide resolution for the fields `source`, `destination` and `services`:

.. code-block:: yaml

 - name: Resolve the source, destination and services fields
   firewall_rule_facts:
     filter: TestPolicy
     search: rulet
     as_yaml: true
     expand:
     - sources
     - destinations
     - services

Running this task results in the following::

 ok: [localhost] => {
    "ansible_facts": {
        "firewall_rule": [
            {
                "comment": null, 
                "policy": "TestPolicy", 
                "rules": [
                    {
                        "action": "allow", 
                        "comment": null, 
                        "connection_tracking": {
                            "mss_enforced": false, 
                            "mss_enforced_max": 0, 
                            "mss_enforced_min": 0, 
                            "state": "no", 
                            "timeout": -1
                        }, 
                        "destinations": {
                            "host": [
                                "2.2.2.5", 
                                "2.2.2.6", 
                                "2.2.2.23"
                            ], 
                            "network": [
                                "gateway_170.27.126.0/24"
                            ]
                        }, 
                        "inspection_options": {
                            "decryption": false, 
                            "deep_inspection": false, 
                            "file_filtering": false
                        }, 
                        "is_disabled": false, 
                        "logging": {
                            "application_logging": "enforced", 
                            "eia_executable_logging": "off", 
                            "log_accounting_info_mode": true, 
                            "log_closing_mode": false, 
                            "log_compression": "off", 
                            "log_level": "stored", 
                            "log_payload_additionnal": false, 
                            "log_payload_excerpt": false, 
                            "log_payload_record": false, 
                            "log_severity": -1, 
                            "user_logging": "enforced"
                        }, 
                        "name": "ruletest", 
                        "services": {
                            "icmp_service": [
                                "Alternate Host Address (Any Code)"
                            ], 
                            "ip_service": [
                                "ARIS"
                            ], 
                            "tcp_service": [
                                "CreativePartnr", 
                                "CreativeServer"
                            ], 
                            "udp_service": [
                                "CMIP-Manager (UDP)", 
                                "CMIP Agent (UDP)"
                            ]
                        }, 
                        "sources": {
                            "any": true
                        }, 
                        "tag": "2097164.14"
                    }
                ]
            }
        ]
    }

Looking at the output, you may notice that the format of the output matches the input format that can be used to create a firewall rule. This is a useful way to also provide modifications to an existing rule. 
One technique for modifying an existing rule is to fetch the rule, make modifications and re-run the playbook.
To do this, there are helper jinja templates that will write the output to a specified filename and can also be added to the task.

.. _export_firewall_rule:

**Exporting a firewall rule into YAML using templates:**

Below is a full example that builds on the previous where you can optionally export the content into valid YML format, modify as necessary and re-run the playbook.

Templates are provided in the playbooks/templates directory.

.. code-block:: yaml

 - name: Get firewall rule as yaml
   register: results
   firewall_rule_facts:
     smc_logging:
      level: 10
      path: ansible-smc.log
     filter: TestPolicy
     search: rulet
     as_yaml: true
     expand:
     - services
     - destinations
     - sources
  
 - name: Write the yaml using a jinja template
   template: src=templates/facts_yaml.j2 dest=./firewall_rules_test.yml
   vars:
     playbook: firewall_rule
     

For details on supported options for playbook runs, see the Fact and Module documentation.
 
