.. _bgp_element:


bgp_element - BGP Elements for BGP configuratons
++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* BGP elements are the building blocks to building a BGP configuration on a layer 3 engine. Use this module to obtain available elements and their values.



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
    <td>yes</td>
    <td></td>
    <td></td>
	<td>
        <p>List of device hashes/dictionaries with custom configurations based on the element type</p>
        <p>Valid elements include: ip_access_list, ip_prefix_list, ipv6_access_list, ipv6_prefix_list,  as_path_access_list, community_access_list, extended_community_access_list, external_bgp_peer, bgp_peering, autonomous_system. See the example bgp_element.yaml for a full list of supported parameters per item. Also see smc python documentation for routing elements  <a href='http://smc-python.readthedocs.io/en/latest/pages/reference.html#dynamic-routing-elements'>http://smc-python.readthedocs.io/en/latest/pages/reference.html#dynamic-routing-elements</a>
    </p>
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
    <td>overwrite_existing<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>yes</li><li>no</li></ul></td>
	<td>
        <p>Overwrite existing will replace the contents of the Access List type with the values provided in the element configuration. Otherwise operations will be update_or_create, where an update will add new entries if they do not exist or fully create and add entries if the acl doesnt exist. To replace entries you should fully define the access list and set overwrite_existing to true.</p>
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
        <p>Create or delete a BGP Element. If <em>state=absent</em>, the element dict must have at least the type of element and name field as a valid value.</p>
	</td>
	</tr>
    </td>
    </tr>

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Create all BGP element types
      register: result
      bgp_element:
        smc_logging:
          level: 10
          path: /Users/davidlepage/Downloads/ansible-smc.log
        elements:
          - ip_access_list: 
              name: myservice2
              comment: my ip acl without min and max prefix length
              entries: 
                - subnet: 1.1.3.0/24
                  action: permit
                - subnet: 2.2.2.0/24
                  action: deny
          - ip_prefix_list:
              name: aprefix
              comment: prefix lists without min and max prefix
              entries:
                - subnet: 10.0.0.0/8
                  action: deny
                - subnet: 192.16.2.0/24
                  action: permit
          - ipv6_access_list:
              name: myipv6acl
              comment: an ipv6 acl
              entries:
                - subnet: '2001:db8:1::1/128'
                  action: permit
          - ipv6_prefix_list:
              name: ipv6prefix
              entries:
                - subnet: 'ab00::/64'
                  min_prefix_length: 65
                  max_prefix_length: 128
                  action: deny
          - as_path_access_list:
              name: mytestaccesslist
              comment: an as path
              entries:
                - expression: '123-456'
                  action: permit
                - expression: '1234-567'
                  action: deny
          - community_access_list:
              name: cmtyacl
              type: standard
              comment: my community
              entries:
                - community: '123'
                  action: permit
                - community: '456'
                  action: deny
          - extended_community_access_list:
              name: extcommacl
              type: standard
              comment: Some acl
              entries:
                - community: '123'
                  action: permit
                  type: rt
                - community: '456'
                  action: deny
                  type: soo
          - bgp_peering:
              name: extpeer
              comment: my peering
          - external_bgp_peer:
              name: mypeer666
              neighbor_as: myas123
              neighbor_ip: 12.12.12.12
              #neighbor_port: 179
              comment: mypeer
          - autonomous_system:
              name: myas123
              as_number: '123.123'
              comment: foo comment
        #state: absent
        #overwrite_existing: true
        
    - name: Update an existing IP Access List and overwrite all entries
      register: result
      bgp_element:
        smc_logging:
          level: 10
          path: /Users/davidlepage/Downloads/ansible-smc.log
        elements:
          - ip_access_list: 
              name: myservice2
              comment: my ip acl
              entries: 
                - subnet: 1.1.4.0/24
                  action: permit
                - subnet: 2.2.2.0/24
                  action: deny
          overwrite_existing: true
          
    - name: Delete an IP Access List by name
      register: result
      bgp_element:
        smc_logging:
          level: 10
          path: /Users/davidlepage/Downloads/ansible-smc.log
        elements:
          - ip_access_list: 
              name: myservice2

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
    <td align=center>list</td>
    <td align=center>[{'action': 'created', 'type': 'ip_access_list', 'name': 'myservice2'}, {'action': 'modified', 'type': 'ip_access_list', 'name': 'myservice2'}, {'action': 'deleted', 'type': 'ip_access_list', 'name': 'myservice2'}]</td>
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
    - If a filter is not used in the query, this will return all results for the element type specified. The return data in this case will only contain the metadata for the element which will be name and type. To get detailed information about an element, use a filter. When using filters on network or service elements, the filter value will search the element fields, for example, you could use a filter of '1.1.1.1' when searching for hosts and all hosts with this IP will be returned. The same applies for services. If you are unsure of the service name but know the port you require, your filter can be by port.


Author
~~~~~~

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


