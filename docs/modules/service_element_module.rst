.. _service_element:


service_element - Create, modify or delete service elements
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Each service type currently supported in this module is documented in the example playbook. Each service element type will have a minimum number of arguments that is required to create the element if it does not exist. Service elements supported by this module have their `create` constructors documented at http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements. This module uses a 'get or create' logic, therefore it is not possible to create the same element twice, instead if it exists, it will be returned. It also means this module can be run multiple times with only slight modifications to the playbook. This is useful when an error is seen with a duplicate name, etc and you must re-adjust the playbook and re-run. For groups, you can reference a member by name which will require it to exist, or you can also specify the required options and create the element if it doesn't exist.



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
    <td rowspan="2">elements<br/><div style="font-size: small;"></div></td>
    <td>yes</td>
    <td></td>
    <td></td>
    <td>
        <div>A list of the elements to create, modify or remove</div>
    </tr>

    <tr>
    <td colspan="5">
        <table border=1 cellpadding=4>
        <caption><b>Dictionary object elements</b></caption>

        <tr>
        <th class="head">parameter</th>
        <th class="head">required</th>
        <th class="head">default</th>
        <th class="head">choices</th>
        <th class="head">comments</th>
        </tr>

        <tr>
        <td>service_group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A group of service elements of any service type</div>
        </td>
        </tr>

        <tr>
        <td>icmp_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>An ICMP related service</div>
        </td>
        </tr>

        <tr>
        <td>ip_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>An IP based related service</div>
        </td>
        </tr>

        <tr>
        <td>ip_service_group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A group of service elements of IP services</div>
        </td>
        </tr>

        <tr>
        <td>icmp_ipv6_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>An ICMP related service</div>
        </td>
        </tr>

        <tr>
        <td>icmp_service_group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A group of service elements of ICMP services</div>
        </td>
        </tr>

        <tr>
        <td>tcp_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A TCP related service</div>
        </td>
        </tr>

        <tr>
        <td>tcp_service_group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A group of TCP services</div>
        </td>
        </tr>

        <tr>
        <td>udp_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A UDP related service</div>
        </td>
        </tr>

        <tr>
        <td>udp_service_group<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>A group of service elements of UDP services</div>
        </td>
        </tr>

        <tr>
        <td>ethernet_service<br/><div style="font-size: small;"></div></td>
        <td>no</td>
        <td></td>
        <td></td>
        <td>
            <div>An Ethernet related service</div>
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

    </table>
    </br>

Examples
--------

.. code-block:: yaml

    
    - name: Create a service element. Check smc-python documentation for required fields.
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Example service element and service group creation
        service_element:
          elements:
            - tcp_service: 
                name: myservice
                min_dst_port: 8080
                max_dst_port: 8100
            - udp_service:
                name: myudp
                min_dst_port: 8090
                max_dst_port: 8091
                comment: created by dlepage
            - ip_service:
                name: new service
                protocol_number: 8
                comment: custom EGP service
            - ethernet_service:
                name: myethernet service
                frame_type: eth2
                ethertype: 32828
            - icmp_service:
                name: custom icmp
                icmp_type: 3
                icmp_code: 7
                comment: custom icmp services
            - icmp_ipv6_service:
                name: my v6 icmp
                icmp_type: 139
                comment: Neighbor Advertisement Message
            - tcp_service_group:
                name: mygroup
                members:
                  - tcp_service:
                      name: newservice80
                      min_dst_port: 80
            - service_group:
                name: mysvcgrp
                members:
                  - tcp_service:
                      name: newservice80
            - udp_service_group:
                name: myudp2000
                members:
                  - udp_service:
                      name: myudp
                  - udp_service:
                      name: udp2000
                      min_dst_port: 2000
            - icmp_service_group:
                name: myicmp
                members:
                  - icmp_service:
                      name: custom icmp
            - ip_service_group:
                name: myipservices
                members:
                  - ip_service:
                      name: new service

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
        <div>Return from all elements using filter of 10.</div>
    </td>
    <td align=center>always</td>
    <td align=center>list</td>
    <td align=center>[{'type': 'tcp_service', 'name': 'myservice'}, {'type': 'udp_service', 'name': 'myudp'}, {'type': 'ip_service', 'name': 'new service'}, {'type': 'ethernet_service', 'name': 'myethernet service'}, {'type': 'icmp_service', 'name': 'custom icmp'}, {'type': 'icmp_ipv6_service', 'name': 'my v6 icmp'}, {'type': 'tcp_service_group', 'name': 'mygroup'}, {'type': 'service_group', 'name': 'mysvcgrp'}, {'type': 'udp_service_group', 'name': 'myudp2000'}, {'type': 'icmp_service_group', 'name': 'myicmp'}, {'type': 'ip_service_group', 'name': 'myipservices'}]</td>
    </tr>
    </table>
    </br></br>


Author
~~~~~~

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


