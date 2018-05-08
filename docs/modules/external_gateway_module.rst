.. _external_gateway:


external_gateway - Represents a 3rd party gateway used for a VPN configuration
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* An external gateway is a non-SMC managed VPN endpoint used in either policy or route based VPN.



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
    <td rowspan="2">external_endpoint<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>An endpoint represents an external VPN gateway and it's remote site settings such as IP address, remote site networks, etc.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object external_endpoint</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>force_nat_t<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Whether to force NAT_T on the VPN</div>
        </td>
        </tr>

        <tr>
        <td>name<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>Name for the endpoint, unique identifier</div>
        </td>
        </tr>

        <tr>
        <td>dynamic<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>yes</li><li>no</li></ul></td>
        <td>
            <div>If the VPN gateway is dynamic (dhcp) then set this value. This is mutually exclusive with <em>endpoint_ip</em>.</div>
        </td>
        </tr>

        <tr>
        <td>address<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>The endpoint IP of the VPN gateway. This is mutually exclusive with <em>endpoint_dynamic</em></div>
        </td>
        </tr>

        <tr>
        <td>enabled<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>True</td>
        <td></td>
        <td>
            <div>Whether to enable the VPN endpoint</div>
        </td>
        </tr>

        <tr>
        <td>ike_phase1_id_value<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>Value of ika_phase1_id_type. This should conform to the type selected. For example, if email address is used, format should be a@a.com. Required if <em>dynamic=yes</em></div>
        </td>
        </tr>

        <tr>
        <td>nat_t<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>True</td>
        <td></td>
        <td>
            <div>Whether to enable nat-t on this VPN.</div>
        </td>
        </tr>

        <tr>
        <td>balancing_mode<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td>active</td>
        <td><ul><li>active</li><li>standby</li><li>aggregate</li></ul></td>
        <td>
            <div>The role for this VPN gateway.</div>
        </td>
        </tr>

        <tr>
        <td>ike_phase1_id_type<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td><ul><li>0 (DNS)</li><li>1 (Email address)</li><li>2 (Distinguished name)</li><li>3 (IP address)</li></ul></td>
        <td>
            <div>An IKE phase1 id is required if <em>dynamic=yes</em>. This specifies the type of selector to use to identify the dynamic endpoint</div>
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
        <p>The name of the external gateway</p>
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
        <p>Create or delete flag</p>
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
        <p>Any tags for this gateway</p>
	</td>
	</tr>
    </td>
    </tr>
    <tr>
    <td rowspan="2">vpn_site<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
    <td>
        <div>VPN sites defined the networks for this VPN. A site entry should be a network CIDR address. If the network does not exist, the element will be created.</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object vpn_site</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>element type<br/><div style="font-size: small;"></div></td>
        <td>yes</td>
        <td></td>
        <td></td>
        <td>
            <div>This is the type of element that is referenced in the SMC. For example, network, host, group, etc. This should be a dict of lists, where the dict key is the element type and the list value is the name of each element.</div>
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

    
    - name: Create a static IP based external gateway
      register: result
      external_gateway:
        smc_logging:
          level: 10
          path: ansible-smc.log
        external_endpoint:
        -   address: 33.33.33.41
            enabled: true
            name: extgw3 (33.33.33.41)
        -   address: 34.34.34.34
            enabled: true
            name: endpoint2 (34.34.34.34)
        -   address: 44.44.44.44
            enabled: true
            name: extgw4 (44.44.44.44)
        -   address: 33.33.33.50
            enabled: true
            name: endpoint1 (33.33.33.50)
        name: extgw3555
        vpn_site:
            group:
            - hostgroup
            host:
            - hosta
            name: site12a
            network:
            - network-172.18.1.0/24
            - network-172.18.2.0/24
    
    
    - name: Delete an external gateway
      external_vpn_gw:
        name: myextgw
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
        <div>Output of operations performed on gateway</div>
    </td>
    <td align=center>always</td>
    <td align=center>list</td>
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


