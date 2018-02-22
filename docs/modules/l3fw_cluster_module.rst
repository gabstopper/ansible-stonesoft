.. _l3fw_cluster:


l3fw_cluster - Create or delete Stonesoft FW clusters
+++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Firewall clusters can be created with up to 16 nodes per cluster. For each cluster_node specified, this will define a unique cluster member. Modifications can be made to existing interfaces, interfaces can be added, VLANs can be added and removed. By default if the interface is not defined in the YAML, it will be deleted. VLANs can be removed or added however if a vlan ID needs to change, you must delete the old and recreate the new VLAN definition. In addition, it is not possible to modify interfaces that have multiple IP addresses defined.



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
    <td>cvi_mode<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>balancing</td>
    <td><ul><li>balancing</li><li>standby</li></ul></td>
	<td>
        <p>How to perform clustering, either balancing or standby</p>
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
    <td>domain_server_address<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>A list of IP addresses to use as DNS resolvers for the FW.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>enable_antivirus<br/><div style="font-size: small;"></div></td>
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
    <td>enable_gti<br/><div style="font-size: small;"></div></td>
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
    <td>primary_mgt<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>Identify the interface to be specified as management</p>
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

    
    l3fw_cluster:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      name: newcluster
      cvi_mode: standby
      primary_mgt: 0
      interfaces:
        - interface_id: 0
          cluster_virtual: 1.1.1.1
          network_value: 1.1.1.0/24
          macaddress: 02:02:02:02:02:02
          nodes:
            - address: 1.1.1.2
              network_value: 1.1.1.0/24
              nodeid: 1
            - address: 1.1.1.3
              network_value: 1.1.1.0/24
              nodeid: 2
            - address: 1.1.1.4
              network_value: 1.1.1.0/24
              nodeid: 3
        - interface_id: 1
          cluster_virtual: 2.2.2.1
          network_value: 2.2.2.0/24
          macaddress: 02:02:02:02:02:04
          nodes:
            - address: 2.2.2.2
              network_value: 2.2.2.0/24
              nodeid: 1
            - address: 2.2.2.3
              network_value: 2.2.2.0/24
              nodeid: 2
            - address: 2.2.2.4
              network_value: 2.2.2.0/24
              nodeid: 3
        - interface_id: 2
          nodes:
            - address: 3.3.3.2
              network_value: 3.3.3.0/24
              nodeid: 1
            - address: 3.3.3.3
              network_value: 3.3.3.0/24
              nodeid: 2
            - address: 3.3.3.4
              network_value: 3.3.3.0/24
              nodeid: 3
          vlan_id: 3
        - interface_id: 2
          nodes:
            - address: 4.4.4.2
              network_value: 4.4.4.0/24
              nodeid: 1
            - address: 4.4.4.3
              network_value: 4.4.4.0/24
              nodeid: 2
            - address: 4.4.4.4
              network_value: 4.4.4.0/24
              nodeid: 3
          vlan_id: 4
        - interface_id: 3
      tags:
        - footag
    
    # Delete a cluster
    - name: layer 3 cluster with 3 members
      l3fw_cluster:
        name: mycluster
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
        <div>Full json definition of NGFW</div>
    </td>
    <td align=center>always</td>
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

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


