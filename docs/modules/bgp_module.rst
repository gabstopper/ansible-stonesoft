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
    <td>announced_networks<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Networks to announce for this BGP configuration. These are typically internal directly connected or routed networks.</p>
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
        <p>An AS represents a whole network or a series of networks. Required if creating new BGP configuration or changing existing AS.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>bgp_profile<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
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


