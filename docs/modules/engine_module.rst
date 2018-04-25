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
    <td>backup_mgt<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Specify an interface by ID that will be the backup management. If the interface is a VLAN, specify in '2.4' format (interface 2, vlan 4).</p>
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
        <td>announced_network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>network</li><li>group</li><li>host</li></ul></td>
        <td>
            <div>Announced networks identify the network and optional route map for internal networks announced over BGP. The list should be a dict with the key identifying the announced network type from SMC. The key should have a dict with name and route_map (optional) if the element should have an associated route_map.</div>
        </td>
        </tr>

        <tr>
        <td>antispoofing_network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>network</li><li>group</li><li>host</li></ul></td>
        <td>
            <div>Antispoofing networks are automatically added to the route antispoofing configuration. The dict should have a key specifying the element type from SMC. The dict key value should be a list of the element types by name.</div>
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
    <td>domain_server_address<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>A list of IP addresses to use as DNS resolvers for the FW. Required to enable Antivirus, GTI and URL Filtering on the NGFW.</p>
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
        <td>network_value<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The cluster netmask for the cluster_vip. Required if <em>cluster_virtual</em></div>
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
        <td>nodes<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>List of the nodes for this interface</div>
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
    <td>primary_heartbeat<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Specify an interface for the primary heartbeat interface. This will default to the same interface as primary_mgt if not specified.</p>
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
        <p>Identify the interface to be specified as management. When creating a new cluster, the primary mgt must be a non-VLAN interface. You can move it to a VLAN interface after creation.</p>
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

    
    - name: Create a single layer 3 firewall
      register: result
      l3fw:
        smc_logging:
          level: 10
          path: /Users/davidlepage/Downloads/ansible-smc.log
        name: myfw
        mgmt_interface: 10
        interfaces:
          - interface_id: 0
            address: 1.1.1.2
            network_value: 1.1.1.0/16
            zone_ref: management
          - interface_id: 10
            address: 10.10.10.1
            network_value: 10.10.10.0/24
            zone_ref: external
            enable_vpn: yes
          - interface_id: 11
          - interface_id: 1000
            address: 11.11.11.1
            network_value: 11.11.11.0/24
            zone_ref: awsvpn
            type: tunnel_interface 
        domain_server_address:
          - 10.0.0.1
          - 10.0.0.2
        default_nat: yes
        enable_antivirus: yes
        enable_gti: yes
        enable_sidewinder_proxy: yes
        tags: 
          - footag
    
    # Delete a layer 3 firewall, using environment variables for credentials
    - name: delete firewall by name
      l3fw:
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


