.. _network_element_facts:


network_element_facts - Facts about networks elements in the SMC
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Network elements can be used as references in many areas of the configuration. This fact module provides the ability to retrieve information related to elements and their values.



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
    <td>element<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>*</td>
    <td><ul><li>host</li><li>network</li><li>router</li><li>address_range</li><li>interface_zone</li><li>domain_name</li><li>group</li><li>ip_list</li><li>country</li><li>alias</li><li>expression</li></ul></td>
	<td>
        <p>Type of network element to retrieve</p>
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
    <td>expand<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>group</li></ul></td>
	<td>
        <p>Optionally expand element attributes that contain only href</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>filter<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>*</td>
    <td></td>
	<td>
        <p>String value to match against when making query. Matches all if not specified. A filter will attempt to find a match in the name, primary key field or comment field of a given record.</p>
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

    
    - name: All network elements, limit result to 10
      network_element_facts:
        limit: 10

    - name: Find all hosts with an IP value of 1.1.1.1 
      network_element_facts:
        limit: 0
        element: host
        filter: 1.1.1.1

    - name: Find an address range including 1.1.1.1
      network_element_facts:
        limit: 10
        element: address_range
        filter: 1.1.1.1
        
    - name: Find a specific group and expand all members
      network_element_facts:
        element: group
        filter: mygroup
        expand:
          - group


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
    <td>elements</td>
    <td>
        <div>Return from all elements using filter of '10.'</div>
    </td>
    <td align=center>always</td>
    <td align=center>list</td>
    <td align=center>[{'comment': None, 'ipv6_network': '::/0', 'ipv4_network': '0.0.0.0/0', 'type': 'network', 'name': 'Any network'}, {'type': 'single_fw', 'name': 'myfirewall'}, {'comment': None, 'ipv6_network': None, 'ipv4_network': '10.0.0.0/8', 'type': 'network', 'name': 'private-10.0.0.0/8'}, {'comment': None, 'ipv6_network': None, 'ipv4_network': '10.10.10.0/24', 'type': 'network', 'name': 'network-10.10.10.0/24'}]</td>
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


