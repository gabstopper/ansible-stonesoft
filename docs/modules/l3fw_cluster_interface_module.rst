.. _l3fw_cluster_interface:


l3fw_cluster_interface - Create or delete Stonesoft FW cluster interfaces
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Add or remove cluster CVI's, NDI's or CVI and NDI interfaces to a cluster



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
    <td>cluster_macaddress<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>The mac address to assign to the cluster virtual IP interface. Required if <em>cluster_vip_mask</em> and <em>cluster_vip</em></p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>cluster_nic_id<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>The interface ID to use for the cluster vip</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">cluster_nodes<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>Define the address, network and node id for each cluster member. Each cluster_node is a dictionary. Required if creating NDIs</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object cluster_nodes</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>address<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The IP address for this cluster node member</div>
        </td>
        </tr>

        <tr>
        <td>nodeid<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The node ID for the cluster node</div>
        </td>
        </tr>

        <tr>
        <td>network_value<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>The netmask for this cluster node address</div>
        </td>
        </tr>

        </table>

    </td>
    </tr>
    </td>
    </tr>

    <tr>
    <td>cluster_vip<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>The cluster virtual (shared) IP address for all cluster members. Required when creating a CVI</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>cluster_vip_mask<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>The cluster netmask for the cluster_vip. Required if <em>cluster_vip</em></p>
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
        <p>The name of the firewall cluster to modify</p>
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
        <td></td>
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
        <p>Create or delete a firewall cluster</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>zone_ref<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>A zone name for the FW management interface.</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Add a cluster address with a CVI and NDIs to a 2 node cluster
      l3fw_cluster_interface:
        name: mycluster
        cluster_vip: 3.3.3.1
        cluster_vip_mask: 3.3.3.0/24
        cluster_macaddress: 02:02:02:02:02:04
        cluster_nic_id: 3
        cluster_nodes:
          - address: 3.3.3.2
            network_value: 3.3.3.0/24
            nodeid: 1
          - address: 3.3.3.3
            network_value: 3.3.3.0/24
            nodeid: 2
    
    - name: Add only a CVI to a cluster
      l3fw_cluster_interface:
        name: mycluster
        cluster_vip: 4.4.4.1
        cluster_vip_mask: 4.4.4.0/24
        cluster_macaddress: 02:02:02:02:02:06
        cluster_nic_id: 4
    
    - name: Add only NDI's to a cluster FW
      l3fw_cluster_interface:
        name: mycluster
        cluster_nic_id: 3
        cluster_nodes:
          - address: 3.3.3.2
            network_value: 3.3.3.0/24
            nodeid: 1
          - address: 3.3.3.3
            network_value: 3.3.3.0/24
            nodeid: 2  

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

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


