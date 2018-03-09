.. _bgp:


bgp - Create, modify or delete a BGP configuration on an engine.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* BGP is a supported dynamic protocol only on layer 3 FW engines. This module allows you to enable BGP and assign a specific BGP configuration to a specified engine. This module assumes the engine already exists. Set enabled to true or false to enable or disable BGP on the engine. If you switch from enabled to disabled, any BGP Peerings will be left on the interfaces. Remove all remnants of BGP Peerings by setting state=absent.




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
        <div>Networks to announce for this BGP configuration. These are typically internal directly connected or routed networks. Required if <em>state=present</em>. Announced networks can only be of type network, host or group of network and hosts. These elements are expected to exist in SMC.</div>
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
    <td rowspan="2">antispoofing_networks<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>List of advertised networks by name. These are expected to exist in SMC. They are automatically added to the antispoofing configuration.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object antispoofing_networks</b></caption>

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
    <td rowspan="2">autonomous_system<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>An AS represents a whole network or a series of networks. Required if creating new BGP configuration or changing existing AS. Required if <em>state=present</em>.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object autonomous_system</b></caption>

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
            <div>Optional description</div>
        </td>
        </tr>

        <tr>
        <td>as_number<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Autonomous System number for the AS. Can be in as_dot format.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name of the Autonomous System element. A get or create operation will be performed</div>
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
        <td>interfaces<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A list of dict with minimum of interface_id defined. Optionally provide network keyword and value to bind BGP Peering to a specific network on a given interface.</div>
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
    <td rowspan="2">external_bgp_peer<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>The external BGP peering element to place after the BGP Peering element on the routing interface. At minimum you can provide only name of an External BGP Peer. This will be used if it exists. Otherwise provide the additional fields to perform a get or create.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object external_bgp_peer</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>neighbor_ip<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The IP Address for the external BGP peer. Required if <em>neighbor_as</em></div>
        </td>
        </tr>

        <tr>
        <td>neighbor_as<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The autonomous system element representing the external BGP peer. Required if <em>neighbor_ip</em>. This is expected to exist in SMC if creating an element.</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The name of the external BGP peer. This will be a get or create operation</div>
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

    
    - name: Configure BGP on an engine
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Run BGP task on cluster FW named newcluster and enable logging
        register: result
        bgp:
          smc_logging:
            level: 10
            path: /Users/davidlepage/Downloads/ansible-smc.log
          name: newcluster
          enable: true
          autonomous_system:
            name: myas
            as_number: '65026.65013'
            comment: optional
          router_id: 1.1.1.1
          announced_networks:
            - network:
                name: network-172.18.1.0/24
                route_map: myroutemap
            - network:
                name: network-1.1.1.0/24
            - host:
                name: hosta
                route_map: myroutemap
            - host:
                name: hostb
            - group:
                name: group1
          antispoofing_networks:
            - network:
                - network-172.18.1.0/24
                - network-1.1.1.0/24
            - host:
                - hosta
            - group:
                - group1
                - group2
          #bgp_profile: MyCustomBGP
          bgp_peering:
            name: mypeering4
            interfaces:
              - interface_id: 0
                network: 1.1.1.0/24
              - interface_id: 1
          external_bgp_peer:
            name: AWS
            neighbor_ip: 10.10.10.10
            neighbor_as: as-200
            neighbor_port: 179

Return Values
-------------

Common return values are documented :ref:`here <common_return_values>`, the following are the fields unique to this {{plugin_type}}:

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
        <div>The json representation of the BGP configuration</div>
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



For help in developing, should you be so inclined, please read :doc:`../../community`,
:doc:`../../dev_guide/testing` and :doc:`../../dev_guide/developing_modules`.
