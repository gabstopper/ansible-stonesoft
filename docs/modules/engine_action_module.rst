.. _engine_action:


engine_action - Node level actions on an engine
+++++++++++++++++++++++++++++++++++++++++++++++

.. versionadded:: 2.5




.. contents::
   :local:
   :depth: 2


Synopsis
--------


* Perform a node level action on the engine such as go_online, go_offline, generate initial_contact, reboot, etc



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
    <td>actions<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td><ul><li>initial_contact</li><li>reboot</li><li>power_off</li><li>reset_to_factory</li><li>sginfo</li><li>ssh</li><li>change_ssh_pwd</li><li>time_sync</li><li>fetch_license</li><li>bind_license</li><li>unbind_license</li><li>cancel_unbind_license</li><li>go_offline</li><li>go_online</li><li>go_standby</li><li>lock_online</li><li>lock_offline</li><li>reset_user_db</li></ul></td>
	<td>
        <p>Action to perform against the engine node. Some actions will optionally have additional arguments that can be provided</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>extra_args<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td></td>
    <td></td>
	<td>
        <p>Extra arguments to provide to action constructor. Arguments documented only show action choices that have specific extra args that are useful when calling the action Constructor arguments are documented at <a href='http://smc-python.readthedocs.io/en/latest/pages/reference.html#module-smc.core.node'>http://smc-python.readthedocs.io/en/latest/pages/reference.html#module-smc.core.node</a></p>
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
        <p>Provide the name of the engine for which to perform a node operation</p>
	</td>
	</tr>
    </td>
    </tr>

    <tr>
    <td>nodeid<br/><div style="font-size: small;"></div></td>
    <td>no</td>
    <td>1</td>
    <td></td>
	<td>
        <p>Provide a nodeid for the engine node to perform the action. For single FWs this is not required and will default to nodeid 1. For clusters, each node has a nodeid to represent which node to operate on</p>
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

    
    - name: Generate an initial contact configuration in base64 format
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Layer 3 FW template
        register: command_output
        engine_action:
          smc_logging:
            level: 10
            path: ansible-smc.log
          name: myfw3
          nodeid: 1
          action: initial_contact
          extra_args:
            enable_ssh: true
            as_base64: true
      
      - debug: msg="{{ command_output.msg }}"
      
    - name: Reboot node 1
      hosts: localhost
      gather_facts: no
      tasks:
      - name: Layer 3 FW template
        engine_action:
          name: myfw3
          nodeid: 1
          action: reboot
          extra_args:
            comment: reboot fw log entry



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
    <td>msg</td>
    <td>
        <div>message attribute will be empty except for initial contact</div>
    </td>
    <td align=center>always</td>
    <td align=center>str</td>
    <td align=center></td>
    </tr>

    <tr>
    <td>state</td>
    <td>
        <div>appliance status after performing the action</div>
    </td>
    <td align=center>always</td>
    <td align=center>dict</td>
    <td align=center>{'status': 'Not Monitored', 'dyn_up': None, 'configuration_status': 'Declared', 'platform': 'N/A', 'state': 'NO_STATUS', 'installed_policy': None, 'version': 'unknown', 'name': 'myfw3 node 1'}</td>
    </tr>
    </table>
    </br></br>


Notes
-----

.. note::
    - Login credential information is either obtained by providing them directly to the task/play, specifying an alt_filepath to read the credentials from to the play, or from environment variables (in that order). See http://smc-python.readthedocs.io/en/latest/pages/session.html for more information.


Author
~~~~~~

    * David LePage (@gabstopper)




Status
~~~~~~

This module is flagged as **preview** which means that it is not guaranteed to have a backwards compatible interface.


