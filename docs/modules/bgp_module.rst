.. _bgp:


bgp - Create, modify or delete a BGP configuration on an engine.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* BGP is a supported dynamic protocol only on layer 3 FW engines. This module allows you to enable BGP and assign a specific BGP configuration to a specified engine. This module assumes the engine already exists.




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
    <td rowspan="2">announced_networks<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Networks to announce for this BGP configuration. These are typically internal directly connected or routed networks. Required if <em>state=present</em>.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object announced_networks</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>host<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Host IP for the announced network. Host will be created if it doesn't exist. Created host will be named in format host-1.1.1.1</div>
        </td>
        </tr>

        <tr>
        <td>group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of group, this should exist or an empty group will be created</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Network cidr for the announced network in format 1.1.1.0/24. Network will be created if it doesn't exist with name network-1.1.1.0/24</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>autonomous_system<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>An AS represents a whole network or a series of networks. Required if creating new BGP configuration or changing existing AS. Required if <em>state=present</em>.</p>
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
        <div>Configure an interface on this engine with a BGP Peering and an external peer.</div>
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
        <td>neighbor_as<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The external AS number. The element will be created if one doesn't already exist</div>
        </td>
        </tr>

        <tr>
        <td>network<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The network cidr to add BGP peering when an interface has multiple network routes</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The name of the BGPPeering within SMC. If this does not exist, it will be automatically created</div>
        </td>
        </tr>

        <tr>
        <td>neighbor_ip<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The IP Address for the external BGP peer. Required if <em>bgp_peering</em></div>
        </td>
        </tr>

        <tr>
        <td>neighbor_port<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>179</td>
        <td></td>
        <td>
            <div>The external BGP port.</div>
        </td>
        </tr>

        <tr>
        <td>interface_id<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The interface ID for which to add the peering. You can also optionally provide a value for <em>network</em> to specify an exact network. Otherwise the peering is added to add networks if multiple are assigned to the specified interface</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>bgp_profile<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>Default BGP Profile</td>
    <td></td>
	<td>
        <p>Specify a unique BGP Profile for this configuration. The element contains distance, redistribution, and aggregation settings. Default profile is used if not provided.</p>
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
        <p>Name of the engine to enable BGP</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>router_id<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Router ID for this BGP configuration. The ID must be unique. Often, the global IPv4 address is the ID. By default, the Router ID is automatically the loopback CVI address or the highest CVI address available on the Firewall Cluster</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Run the BGP task on myfw with logging
        register: result
        bgp:
          smc_logging:
            level: 10
            path: /Users/davidlepage/Downloads/ansible-smc.log
          name: myfw
          autonomous_system: 250
          router_id: none
          announced_networks:
            network:
              - 172.18.1.0/24
              - 172.18.2.0/24
              - 172.18.18.0/24
            host:
              - 1.1.1.1
            group:
              - mygroup
          #bgp_profile: foo
          bgp_peering:
            name: mypeering
            interface_id: 0
            network: 1.1.1.0/24
            neighbor_ip: 10.10.10.10
            neighbor_as: 200
            neighbor_port: 179
    

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


