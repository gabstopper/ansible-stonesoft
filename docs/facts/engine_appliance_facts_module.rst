.. _engine_appliance_facts:


engine_appliance_facts - Facts about engine appliances such as hardware and interface status
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Retrieve specific information about a particular engine node or all nodes of an engine. Information that can be obtained is general information about the node itself as well as general information such as filesystem utilization, interfaces and statuses and current routing table.



Requirements (on host that executes module)
-------------------------------------------

  * smc-python >= 0.6.0


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
    <td>case_sensitive<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>True</td>
    <td></td>
	<td>
        <p>Whether to do a case sensitive match on the filter specified</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>exact_match<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Whether to do an exact match on the filter specified</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>filter<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>Provide the name of the engine as a filter</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>items<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>status</li><li>interfaces</li><li>filesystem</li></ul></td>
	<td>
        <p>If it is preferable to view only specific node level items you can provide a list of those individually. If items is omitted all items will be returned</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>limit<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>10</td>
    <td></td>
	<td>
        <p>Limit the number of results. Set to 0 to remove limit.</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>nodeid<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Only return the details of a specific node by ID. If not provided, all node info is returned</p>
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

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Retrieve all stats (hardware, interface, info) for engine sg_vm
      engine_appliance_facts:
        filter: sg_vm

    - name: Retrieve all stats (hardware, interface, info) on for node 1
      engine_appliance_facts:
        filter: sg_vm
        nodeid: 1

    - name: Retrieve all stats (hardware, interface, info) for node 1 using items
      engine_appliance_facts:
        filter: sg_vm
        nodeid: 1
        items:
        - status
        - filesystem
        - interfaces

    - name: Only retrieve engine status facts
      engine_appliance_facts:
        filter: sg_vm
        nodeid: 1
        items:
        - status


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
    <td>engines</td>
    <td>
        <div>List of nodes and statuses</div>
    </td>
    <td align=center>always</td>
    <td align=center>list</td>
    <td align=center>[{'status': {'status': 'Online', 'initial_license_remaining_days': 0, 'software_version': '5.7', 'cloud_id': 'N/A', 'installed_policy': 'Standard Firewall Policy with Inspection', 'first_upload_time': 0, 'proof_of_serial': 'xxxxxxxx-xxxxxxxxxx', 'name': 'ngf-1035', 'software_features': 'SECNODE+ALLOWX64=YES+ANTISPAM=YES+ANTIVIRUS=YES+DYNAMIC_ROUTING=YES+USERS=YES+URL_SERVICE2=YES+DEVICECLASS=100+VPN=YES', 'cloud_type': 'NONE', 'dyn_up': '1070', 'hardware_version': '79.1', 'configuration_status': 'Installed', 'platform': 'x86-64-small', 'state': 'READY', 'version': 'version 6.4.1 #20056', 'product_name': '1035-1-C1', 'initial_contact_time': '2016-03-08T21:28:02.263000'}, 'interfaces': [{'status': 'Up', 'name': 'eth0_0', 'mtu': 1500, 'capability': 'Normal Interface', 'flow_control': 'AutoNeg: off Rx: off Tx: off', 'aggregate_is_active': False, 'interface_id': 0, 'port': 'Copper', 'speed_duplex': '1000 Mb/s / Full / Automatic'}, {'status': 'Up', 'name': 'eth0_1', 'mtu': 1500, 'capability': 'Normal Interface', 'flow_control': 'AutoNeg: off Rx: off Tx: off', 'aggregate_is_active': False, 'interface_id': 1, 'port': 'Copper', 'speed_duplex': '1000 Mb/s / Full / Automatic'}, {'status': 'Up', 'name': 'eth0_2', 'mtu': 1500, 'capability': 'Normal Interface', 'flow_control': 'AutoNeg: off Rx: off Tx: off', 'aggregate_is_active': False, 'interface_id': 2, 'port': 'Copper', 'speed_duplex': '1000 Mb/s / Full / Automatic'}, {'status': 'Down', 'name': 'eth0_3', 'mtu': 1500, 'capability': 'Normal Interface', 'flow_control': 'AutoNeg: off Rx: off Tx: off', 'aggregate_is_active': False, 'interface_id': 3, 'port': 'Copper', 'speed_duplex': 'Half / Automatic'}], 'filesystem': [{'status': -1, 'sub_system': 'File Systems', 'param': 'Partition Size', 'value': '600 MB', 'label': 'Root'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Usage', 'value': '9.8%', 'label': 'Data'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Size', 'value': '1937 MB', 'label': 'Data'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Usage', 'value': '14.2%', 'label': 'Spool'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Size', 'value': '3288 MB', 'label': 'Spool'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Usage', 'value': '0.0%', 'label': 'Tmp'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Size', 'value': '1926 MB', 'label': 'Tmp'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Usage', 'value': '7.4%', 'label': 'Swap'}, {'status': -1, 'sub_system': 'File Systems', 'param': 'Size', 'value': '943 MB', 'label': 'Swap'}, {'status': -1, 'sub_system': 'Logging subsystem', 'param': 'Sending (entries / s)', 'value': '21', 'label': 'Log rates (average over 30 s)'}], 'nodeid': 2, 'name': 'ngf-1035'}]</td>
    </tr>
    </table>
    </br></br>


Notes
-----

.. note::
    - If a filter is not used in the query, this will return all results for the element type specified. The return data in this case will only contain the metadata for the element which will be name and type. To get detailed information about an element, use a filter. When using filters on network or service elements, the filter value will search the element fields, for example, you could use a filter of '1.1.1.1' when searching for hosts and all hosts with this IP will be returned. The same applies for services. If you are unsure of the service name but know the port you require, your filter can be by port.


Author
~~~~~~

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


