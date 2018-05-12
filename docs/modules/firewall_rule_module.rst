.. _firewall_rule:


firewall_rule - Create, modify or delete a firewall rule
++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Firewall rules can be added or removed from either a top level policy or a sub-policy. Source, destination and service elements can be used and referenced by their type and name (they must be pre-created). Many other rule settings are possible, including logging, inspection and connection tracking settings.




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
    <td>inspection_policy<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Read only view of the inspection policy for this policy</p>
	</td>
	</tr>
    </td>
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
        <td>authentication_options<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Set authentication options for this rule</div>
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
        <td>connection_tracking<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional settings to control connection tracking on the rule. Primary connection setting fields allow you to enforce MSS settings or modify the inspection mode to strict, loose, normal or off.</div>
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
        <td>log_options<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Log options for this rule</div>
        </td>
        </tr>

        <tr>
        <td>action<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>allow</td>
        <td><ul><li>allow</li><li>discard</li><li>refuse</li><li>continue</li><li>jump</li><li>apply_blacklist</li><li>apply_vpn</li><li>enforce_vpn</li><li>forward_vpn</li></ul></td>
        <td>
            <div>Required action for the rule</div>
        </td>
        </tr>

        <tr>
        <td>inspection_options<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Set inspection features on or off</div>
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

    <tr>
    <td>template<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Read only view of the policy or sub policies template. This is returned by the facts module when retrieving rules</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Example log all rule for top of rule set
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
    
    - name: Create a rule with specific sources and services
      firewall_rule:
        smc_logging:
          level: 10
          path: ansible-smc.log
        policy: TestPolicy
        rules:
        -   action: allow
            comment: my comment
            connection_tracking:
                mss_enforced: true
                mss_enforced_max: 1555
                mss_enforced_min: 0
                timeout: 11
            destinations:
                group:
                - foogroup
                host:
                - host-1.1.1.1
                ip_list:
                - Amazon S3
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
            name: ruletest2
            services:
                ip_service:
                - CHAOS
                tcp_service:
                - AOL
                udp_service:
                - Biff
            sources:
                country:
                - China
                interface_nic_x_ip_alias:
                - $$ Interface ID 0.ip
                single_fw:
                - myfw
        
    - name: Create a rule to use VPN, requires a vpn_policy or mobile_vpn set
      firewall_rule:
        smc_logging:
          level: 10
          path: ansible-smc.log
        inspection_policy: High-Security Inspection Template
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
                decrypting: null
                deep_inspection: null
                file_filtering: null
            is_disabled: false
            authentication_options:
                method:
                - LDAP Authentication
                require_auth: true
                users:
                - dc=lepages,dc=local,domain=myldapdomain
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
        template: Firewall Inspection Template
    
    - name: Add a deny rule after specified rule using add_after syntax
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
    
    - name: Delete a rule
      firewall_rule:
        policy: TestPolicy
        rules:
        -   tag: '2097203.0'
        state: absent



Author
~~~~~~

    * UNKNOWN




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


