.. _engine:


engine - Operations on single or cluster layer 3 firewalls
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Create or delete a Stonesoft Layer 3 Firewall on the Stonesoft Management Center.



Requirements (on host that executes module)
-------------------------------------------

  * smc-python


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
    <td>antispoofing_network<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>network</li><li>group</li><li>host</li></ul></td>
	<td>
        <p>Antispoofing networks are automatically added to the route antispoofing configuration. The dict should have a key specifying the element type from SMC. The dict key value should be a list of the element types by name.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>antivirus<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Enable Anti-Virus engine on the FW</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>backup_heartbeat<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Specify an interface by ID that will be the backup heartbeat. If the interface is a VLAN, specify in '2.4' format. If the interface cannot be used as this management type, operation is skipped.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>backup_mgt<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Specify an interface by ID that will be the backup management. If the interface is a VLAN, specify in '2.4' format (interface 2, vlan 4). If the interface cannot be used as this management type, operation is skipped.</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">bgp<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>If enabling BGP on the engine, provide BGP related settings</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object bgp</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>router_id<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional router ID to identify this BGP peer</div>
        </td>
        </tr>

        <tr>
        <td>bgp_peering<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>BGP Peerings to add to specified interfaces.</div>
        </td>
        </tr>

        <tr>
        <td>enabled<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Set to true or false to specify whether to configure BGP</div>
        </td>
        </tr>

        <tr>
        <td>autonomous_system<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The autonomous system for this engine. Provide additional arguments to allow for get or create logic</div>
        </td>
        </tr>

        <tr>
        <td>announced_network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>network</li><li>group</li><li>host</li></ul></td>
        <td>
            <div>Announced networks identify the network and optional route map for internal networks announced over BGP. The list should be a dict with the key identifying the announced network type from SMC. The key should have a dict with name and route_map (optional) if the element should have an associated route_map.</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>cluster_mode<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>standby</td>
    <td><ul><li>balancing</li><li>standby</li></ul></td>
	<td>
        <p>How to perform clustering, either balancing or standby</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>comment<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Optional comment tag for the engine</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>default_nat<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Whether to enable default NAT on the FW. Default NAT will identify internal networks and use the external interface IP for outgoing traffic</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>delete_undefined_interfaces<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Delete interfaces from engine cluster that are not defined in the YAML file. This can be used as a strategy to remove interfaces. One option is to retrieve the full engine json using engine_facts as yaml, then remove the interfaces from the yaml and set this to True.</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">domain_server_address<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>A list of IP addresses to use as DNS resolvers for the FW. Required to enable Antivirus, GTI and URL Filtering on the NGFW.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object domain_server_address</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>type<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Type of element. Valid entries are ipaddress, host, dns_server or dynamic_interface_alias. If using an element that is not ipaddress, it must pre-exist in the SMC</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the element, can be IP address or element</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>enable_vpn<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Provide a list of IP addresses for which to enable VPN endpoints on. This should be a list of string IP address identifiers. If enabling on a DHCP address, use the value specified in the SMC under VPN endpoints, i.e. First DHCP Interface ip.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>file_reputation<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Enable file reputation</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">interfaces<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>Define the interface settings for this cluster interface, such as address, network and node id.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object interfaces</b></caption>

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
            <div>Optional comment for this interface. If you want to unset the interface comment, set to an empty string or define with no value</div>
        </td>
        </tr>

        <tr>
        <td>macaddress<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The mac address to assign to the cluster virtual IP interface. This is required if <em>cluster_virtual</em></div>
        </td>
        </tr>

        <tr>
        <td>zone_ref<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional zone name for this interface</div>
        </td>
        </tr>

        <tr>
        <td>cluster_virtual<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The cluster virtual (shared) IP address for all cluster members. Not required if only creating NDI's</div>
        </td>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The cluster nic ID for this interface. Required.</div>
        </td>
        </tr>

        <tr>
        <td>network_value<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The cluster netmask for the cluster_vip. Required if <em>cluster_virtual</em></div>
        </td>
        </tr>

        <tr>
        <td>nodes<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>List of the nodes for this interface</div>
        </td>
        </tr>

        <tr>
        <td>type<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The type of interface. Default is physical_interface. This is only required if the interface type is tunnel_interface or switch_physical_interface</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>location<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Location identifier for the engine. Used when engine is behind NAT. If a location is set on the engine and you want to reset to unspecified, then use the keyword None.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>log_server<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Name of the log server to assign. If not provided, the default (primary) log server will be used</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>name<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>The name of the firewall cluster to add or delete</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">netlinks<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Netlinks are a list of dicts defining where to place netlinks and any destinations on a given routing interface. Suboptions define the dict structure for each list dict</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object netlinks</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>destination<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Destination elements specifying the networks, hosts, groups behind this netlink. Suboptions define the dict format for each list member</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
        </td>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface ID which to bind the netlink to. For VLAN, should be in dot syntax, i.e. 1.2, indicating interface 1, VLAN 2</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">policy_vpn<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Defines any policy based VPN membership for thie engine. You can specify multiple and whether the engine should be a central gateway or satellite gateway and whether it should be enabled for mobile gateway. Updating policy VPN on the engine directly requires SMC version &gt;= 6.3.x</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object policy_vpn</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>central_gateway<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Whether this engine should be a central gateway. Mutually exclusive with <em>satellite_gateway</em></div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The name of the policy VPN.</div>
        </td>
        </tr>

        <tr>
        <td>mobile_gateway<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Whether this engine should be enabled for remote VPN for mobile gateways (client VPN)</div>
        </td>
        </tr>

        <tr>
        <td>satellite_gateway<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Whether this engine should be a satellite gateway. Mutually exclusive with <em>central_gateway</em></div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>primary_heartbeat<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Specify an interface for the primary heartbeat interface. This will default to the same interface as primary_mgt if not specified. If the interface cannot be used as this management type, operation is skipped.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>primary_mgt<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>Identify the interface to be specified as management. When creating a new cluster, the primary mgt must be a non-VLAN interface. You can move it to a VLAN interface after creation. If the interface cannot be used as this management type, operation is skipped.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>skip_interfaces<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Optionally skip the analysis of interface changes. This is only relevant when running the playbook against an already created engine. This must be false if attempting to add interfaces.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>smc_address<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>FQDN with port of SMC. The default value is the environment variable <code>SMC_ADDRESS</code></p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>smc_alt_filepath<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Provide an alternate path location to read the credentials from. File is expected to be stored in ~.smcrc. If provided, url and api_key settings are not required and will be ignored.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>smc_api_key<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>API key for api client. The default value is the environment variable <code>SMC_API_KEY</code> Required if <em>url</em></p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>smc_api_version<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Optional API version to connect to. If none is provided, the latest SMC version API will be used based on the Management Center version. Can be set though the environment variable <code>SMC_API_VERSION</code></p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>smc_domain<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Optional domain to log in to. If no domain is provided, 'Shared Domain' is used. Can be set throuh the environment variable <code>SMC_DOMAIN</code></p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">smc_extra_args<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Extra arguments to pass to login constructor. These are generally only used if specifically requested by support personnel.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object smc_extra_args</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>verify<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>True</td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Is the connection to SMC is HTTPS, you can set this to True, or provide a path to a client certificate to verify the SMC SSL certificate. You can also explicitly set this to False.</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">smc_logging<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Optionally enable SMC API logging to a file</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object smc_logging</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>path<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Full path to the log file</div>
        </td>
        </tr>

        <tr>
        <td>level<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Log level as specified by the standard python logging library, in int format. Default setting is logging.DEBUG.</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>smc_timeout<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Optional timeout for connections to the SMC. Can be set through environment <code>SMC_TIMEOUT</code></p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">snmp<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>SNMP settings for the engine</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object snmp</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>snmp_agent<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The name of the SNMP agent from within the SMC</div>
        </td>
        </tr>

        <tr>
        <td>enabled<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>Set this to False if enabled on the engine and wanting to remove the configuration.</div>
        </td>
        </tr>

        <tr>
        <td>snmp_interface<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A list of interface IDs to enable SNMP. If enabling on a VLAN, use '2.3' syntax. If omitted, snmp is enabled on all interfaces</div>
        </td>
        </tr>

        <tr>
        <td>snmp_location<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional SNMP location string to add the SNMP configuration</div>
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
    <td>tags<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Optional tags to add to this engine</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Firewall Template
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Layer 3 FW template
        engine:
          smc_logging:
            level: 10
            path: ansible-smc.log
          antispoofing_network:
            group:
            - group1
            host:
            - 2.2.2.23
            network:
            - network-5.5.5.0/24
            - network-50.50.50.0/24
          antivirus: true
          bgp:
            announced_network:
            - network:
                name: network-1.1.1.0/24
                route_map: myroutemap
            autonomous_system:
              as_number: 200
              comment: null
              name: as-200
            bgp_peering:
            - external_bgp_peer: bgppeer
              interface_id: '1000'
              name: bgppeering
            bgp_profile: Default BGP Profile
            enabled: true
            router_id: 2.3.4.5
          default_nat: true
          domain_server_address:
          - name: 8.8.8.8
            type: ipaddress
          - name: Localhost
            type: host
          file_reputation: true
          interfaces:
          - interface_id: '1000'
            interfaces:
            - nodes:
              - address: 10.10.10.1
                network_value: 10.10.10.1/32
                nodeid: 1
            type: tunnel_interface
          - interface_id: '2'
            interfaces:
            - nodes:
              - address: 21.21.21.21
                network_value: 21.21.21.0/24
                nodeid: 1
              vlan_id: '1'
          - interface_id: '1'
            interfaces:
            - nodes:
              - address: 2.2.2.1
                network_value: 2.2.2.0/24
                nodeid: 1
          - interface_id: '0'
            interfaces:
            - nodes:
              - address: 1.1.1.1
                network_value: 1.1.1.0/24
                nodeid: 1
          - interface_id: SWP_0
            appliance_switch_module: 110
            type: switch_physical_interface
            port_group_interface:
            - interface_id: SWP_0.4
              switch_physical_interface_port:
              - switch_physical_interface_port_comment: port 2
                switch_physical_interface_port_number: 2
              - switch_physical_interface_port_comment: ''
                switch_physical_interface_port_number: 4
              - switch_physical_interface_port_comment: ''
                switch_physical_interface_port_number: 5
              - switch_physical_interface_port_comment: ''
                switch_physical_interface_port_number: 6
          name: myfw3
          log_server: my_custom_log_server
          netlinks:
          - destination:
            - name: host-3.3.3.3
              type: host
            interface_id: '2.1'
            name: netlink-21.21.21.0
          ospf:
            enabled: true
            ospf_areas:
            - interface_id: '2.1'
              name: myarea
              network: 21.21.21.0/24
            ospf_profile: Default OSPFv2 Profile
            router_id: 1.1.1.1
          policy_vpn:
          - central_gateway: true
            mobile_gateway: false
            name: new_policy_vpn
            satellite_gateway: false
          primary_mgt: '0'
          snmp:
            snmp_agent: fooagent
            snmp_interface:
            - '1'
            snmp_location: test
          type: single_fw


    # Delete a layer 3 firewall, using environment variables for credentials
    - name: delete firewall by name
      engine:
        name: myfirewall
        state: 'absent'


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


Notes
-----

.. note::
    - Login credential information is either obtained by providing them directly to the task/play, specifying an alt_filepath to read the credentials from to the play, or from environment variables (in that order). See http://smc-python.readthedocs.io/en/latest/pages/session.html for more information.


Author
~~~~~~

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


