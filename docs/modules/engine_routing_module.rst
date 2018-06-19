.. _engine_routing:


engine_routing - Routing configurations on NGFW
+++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Use this module to add or remove static routes, antispoofing, BGP, OSPF or netlink elements to routing nodes on an engine. You can use engine_facts to dump the engine configuration or use engine_routing_facts to specifically dump only the routing table



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
    <td rowspan="2">antispoofing_network<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of static routes</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object antispoofing_network</b></caption>

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
            <div>Destinations associated with this antispoofing entry. Multiple element types can be used as a destination</div>
        </td>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface id to add the antispoofing network. Can be VLAN id if specified 1.23</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">bgp_peering<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of dict describing the BGP peering to add</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object bgp_peering</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface id to add the peering. Can be VLAN id if specified 1.23</div>
        </td>
        </tr>

        <tr>
        <td>destination<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Destination is the BGP peer associated with this BGP Peering. This can be either another NGFW engine or an external_bgp_peer element. Both element types must preexist in the SMC.</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional network to bind the BGP Peer to. Only relevant if multiple IP addresses are assigned to the given interface and you only want to bind to one.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the BGP peering element in SMC</div>
        </td>
        </tr>

        </table>

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
        <p>The name of the firewall cluster to access routing table</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">netlink<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of dict describing the netlinks</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object netlink</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface id to add the netlink. Can be VLAN id if specified 1.23</div>
        </td>
        </tr>

        <tr>
        <td>destination<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Destinations associated with this netlink. Multiple element types can be used as a destination</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional network to bind the netlink. Only relevant if multiple IP addresses are assigned to the given interface and you only want to bind to one.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the netlink element in SMC</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">ospfv2_area<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of dict describing the OSPF areas to add</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object ospfv2_area</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface id to add the OSPF area. Can be VLAN id if specified 1.23</div>
        </td>
        </tr>

        <tr>
        <td>destination<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Destination is the element referenced can be an OSPF Area interface setting element from SMC. This can be used to override the default interface settings for OSPF. This is optional.</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional network to bind the OSPF area to. Only relevant if multiple IP addresses are assigned to the given interface and you only want to bind to one.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the OSPF area element in SMC</div>
        </td>
        </tr>

        </table>

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
    <td>state<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>present</td>
    <td><ul><li>present</li><li>absent</li></ul></td>
	<td>
        <p>Add or remove the routing entry. If <em>state=absent</em> any defined routing configurations are considered a removal action</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">static_route<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of static routes</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object static_route</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface id to add the static route. Can be VLAN id if specified 1.23</div>
        </td>
        </tr>

        <tr>
        <td>destination<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Destinations associated with this static route. Multiple element types can be used as a destination</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Optional network to bind the route. Only relevant if multiple IP addresses are assigned to the given interface and you only want to bind to one.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the router element to use as the next hop for the static route. Note that this MUST be a router type element from SMC.</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Engine routing configuration
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Add routing elements to engine sg_vm
        engine_routing:
          smc_logging:
            level: 10
            path: ansible-smc.log
          name: sg_vm
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
    
    - name: Engine routing configuration
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Remove specific antispoofing network from engine sg_vm
        engine_routing:
          smc_logging:
            level: 10
            path: ansible-smc.log
          name: sg_vm
          antispoofing_network:
          - destination:
            - name: foonet
              type: network
            interface_id: 0
          state: absent

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


