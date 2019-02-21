.. _firewall_nat_rule:


firewall_nat_rule - Create, modify or delete a firewall NAT rule
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Firewall NAT rules can be added or removed from either a top level policy or a sub-policy. Source, destination and service elements can be used and referenced by their type and name (they must be pre-created). This module requires SMC >= 6.4.3 or above to support changes to NAT rules




Options
-------

.. raw:: html

    <table border=1 cellpadding=4>

    <tr>
    <th class="head">parameter</th>
    <th class="head">required</th>
    <th class="head">default</th>
    <th class="head">choices</th>
    <th class="head">comments</th>
    </tr>

    <tr>
    <td>policy<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>The policy which to operate on. Any rule modifications are done in the context of this policy</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">rules<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Source elements to add to the rule. Elements need to specify the type of element to add. If source is not provided, the rule source cell will be set to none and the rule will effectively be disabled.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object rules</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>comment<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional comment for this rule</div>
        </td>
        </tr>

        <tr>
        <td>add_after<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Provide a rule tag ID for which to add the rule after. This is only relevant for rules that are being created.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name for this rule. Required if adding a new rule. Not required for modifications</div>
        </td>
        </tr>

        <tr>
        <td>is_disabled<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Is this rule disabled. Set to true to disable rule, false otherwise.</div>
        </td>
        </tr>

        <tr>
        <td>add_before<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Provide a rule tag ID for which to add the rule before. This is only relevant for rules that are being created.</div>
        </td>
        </tr>

        <tr>
        <td>sources<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>domain_name</li><li>expression</li><li>group</li><li>host</li><li>ip_list</li><li>network</li><li>engine</li><li>router</li><li>netlink</li><li>interface_zone</li></ul></td>
        <td>
            <div>Sources for use in this rule. You can use a shortcut for 'any' or 'none' in this field, by providing a simple dict with keys 'any' or 'none' and value of true. Otherwise this should be a dict with keys using valid element types and value should be a list of those element types by name. The choices represent valid keys for the dict. If no sources field is provided, 'any' is used</div>
        </td>
        </tr>

        <tr>
        <td>tag<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Tag retrieved from facts module. The tag identifies the rule uniquely and is a required field when making modifications. If tag is present, the operation becomes a modify. Otherwise it becomes a create and <em>name</em> is required.</div>
        </td>
        </tr>

        <tr>
        <td>static_src_nat<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Static source NAT rule. A static source NAT rule uses the value of the rule source field and requires either an IP or element as the translated address. This is mutually exclusive with dynamic_src_nat.</div>
        </td>
        </tr>

        <tr>
        <td>services<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>service_group</li><li>tcp_service_group</li><li>udp_service_group</li><li>ip_service_group</li><li>icmp_service_group</li><li>tcp_service</li><li>udp_service</li><li>ip_service</li><li>ethernet_service</li><li>icmp_service</li><li>application_situation</li><li>url_category</li></ul></td>
        <td>
            <div>Services for this rule. You can use a shortcut for 'any' or 'none' in this field, by providing a simple dict with keys 'any' or 'none' and value of true. Otherwise this should be a dict with keys using valid element types and value should be a list of those element types by name. The choices represent valid keys for the dict. If no services field is provided, 'any' is used</div>
        </td>
        </tr>

        <tr>
        <td>dynamic_src_nat<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Dynamic source NAT rule. A dynamic source NAT rule uses the value of the rule source field and requires either an IP or element as the translated address. You can also define ports to use for PAT. This NAT type is typically used for outbound NAT and PAT operations.</div>
        </td>
        </tr>

        <tr>
        <td>static_dst_nat<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Static dest NAT rule. Typically used for inbound traffic. This rule uses the rule destination field and requires either an IP or element as the translated address. You can also specify source ports as single values or ranges to translate. This is useful if you want inbound traffic on port 80 and need to redirect to an internal host on 8080 for example</div>
        </td>
        </tr>

        <tr>
        <td>destinations<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>domain_name</li><li>expression</li><li>group</li><li>host</li><li>ip_list</li><li>network</li><li>engine</li><li>router</li><li>netlink</li><li>interface_zone</li></ul></td>
        <td>
            <div>Destinations for use in this rule. You can use a shortcut for 'any' or 'none' in this field, by providing a simple dict with keys 'any' or 'none' and value of true. Otherwise this should be a dict with keys using valid element types and value should be a list of those element types by name. The choices represent valid keys for the dict, If no destinations field is provided, 'any' is used</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
	<td>
        <p>Create or delete a firewall cluster</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>sub_policy<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>The sub policy which to operate on. This is mutually exclusive with the <em>policy</em> parameter. You can operate on rules within a firewall policy or firewall sub policy.</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Firewall NAT rule examples
      firewall_nat_rule:
        policy: TestPolicy
        rules:
        - comment: added a comment
          destinations:
            any: true
          dynamic_src_nat:
            automatic_proxy: true
            translated_value:
              ip_descriptor: 1.1.1.1
              max_port: 60000
              min_port: 1024
          is_disabled: false
          name: dynamic source nat with ports and IP redirect
          services:
            any: true
          sources:
            any: true
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
          name: dynamic source nat with element
          services:
            any: true
          sources:
            host:
            - host-3.3.3.3
        - comment: testcomment
          destinations:
            host:
            - host-3.3.3.3
          is_disabled: false
          name: static_dest_nat with IP redirect
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
          used_on: ANY
        - comment: null
          destinations:
            any: true
          is_disabled: false
          name: static_src_nat with IP address
          services:
            any: true
          sources:
            host:
            - host-4.4.4.4
          static_src_nat:
            automatic_proxy: true
            translated_value:
              ip_descriptor: 1.1.1.1
          used_on: ANY
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
          name: dynamic_source_nat with element
          services:
            any: true
          sources:
            host:
            - host-3.3.3.3
          used_on: ANY


Return Values
-------------

Common return values are documented `Return Values <http://docs.ansible.com/ansible/latest/common_return_values.html>`_, the following are the fields unique to this module:

.. raw:: html

    <table border=1 cellpadding=4>

    <tr>
    <th class="head">name</th>
    <th class="head">description</th>
    <th class="head">returned</th>
    <th class="head">type</th>
    <th class="head">sample</th>
    </tr>

    <tr>
    <td>state</td>
    <td>
        <div>The current state of the element</div>
    </td>
    <td align=center></td>
    <td align=center>dict</td>
    <td align=center></td>
    </tr>

    <tr>
    <td>changed</td>
    <td>
        <div>Whether or not the change succeeded</div>
    </td>
    <td align=center>always</td>
    <td align=center>bool</td>
    <td align=center></td>
    </tr>
    </table>
    </br></br>


Author
~~~~~~

    * UNKNOWN




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


