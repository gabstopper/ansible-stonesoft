############
Introduction
############

This project provides Ansible modules for management of Stonesoft Next Generation Firewall. The modules are dependent on the `smc-python <http://smc-python.readthedocs.io/en/latest/pages/reference.html#elements>`_ library which is used for all operations interacting with the Stonesoft Management Center.

Ansible playbooks can be run remotely from the Stonesoft Management Center, or optionally directly on the SMC itself.

Requirements
++++++++++++

Stonesoft Ansible modules are dependent on the following library:

- smc-python >= 0.6.0

They have also been tested on both python 2.x and 3.x versions.

This dependency will automatically be installed if you install directly from the ansible-stonesoft package.

Download this ansible package from github and optionally install in a virtualenv::

  pip install ansible
  git clone https://github.com/gabstopper/ansible-stonesoft.git
  cd ansible-stonesoft
  pip install -r requirements.txt

The package by default comes with an ansible.cfg in the base directory where this package is extracted. You will want to note the minimal settings, this is used to set two paths (library and module_utils) to resolve the custom modules. If you use your own ansible.cfg, you can insert these two lines or ensure your path can resolve these locations.

Getting Started
+++++++++++++++

To successfully use the modules you must ensure that you have enabled the SMC API on the management server and have created an administrative account that has privilege to the required elements.

In addition, note the credentials as they will be required on the ansible client to create the sessions to the SMC.

If your SMC is using the `Domain` feature, ensure your account has proper privilege within the domain.

Once you have your API client account, you can move on to configuring the ansible client side to use these credentials.

Credentials
+++++++++++

Credentials for an ansible run can be provided multiple ways. 

- They can be provided in an ansible playbook directly. This is the least flexible option as you would have to add the entries for each run.

- They can be set as environment variables on the host system

- They can be provided in a configuration file. For the configuration file, the default location is ~.smcrc. It is possible to override this single entry in an ansible playbook to specify an alternative file.

Credentials in playbook
-----------------------

An example of providing credentials in a playbook:

.. code::

  - name: Search for host elements with IP 1.1.1.1
    network_element_facts:
      element: host
      filter: 1.1.1.1
      smc_address: http://1.1.1.1:8082
      smc_api_key: xxxxxxxxxxxxxxxxxxx
      smc_timeout: 30

.. note:: You can also specify a domain of which to log in, an SMC API version as well as a certificate bundle to specify for HTTPS validation.

Module documentation also defines these parameters in the ansible standard format.

Credentials as environment variables
------------------------------------

The following ENV variables are supported for credentials:

.. code::

  SMC_ADDRESS=http://1.1.1.1:8082
  SMC_API_KEY=123abc
  SMC_CLIENT_CERT=path/to/cert
  SMC_TIMEOUT = 30 (seconds)
  SMC_API_VERSION = 6.1 (optional - uses latest by default)
  SMC_DOMAIN = name of domain, Shared is default 

The minimum variables that are required are SMC_ADDRESS and SMC_API_KEY.

Credentials in configuration file
---------------------------------

By default, smc-python will try to obtain credentials from the users home directory in a file `~.smcrc` (unless provided by one of the two methods above).

See `Creating the session <http://smc-python.readthedocs.io/en/latest/pages/session.html>`_ on specific syntax for the configuration file.

Lastly, if you want to override the location of the configuration file, you can provide the `smc_alt_filepath` and location (including filename) in the playbook:

.. code::

  - name: Search for host elements with IP 1.1.1.1
    network_element_facts:
      element: host
      filter: 1.1.1.1
      smc_alt_filepath: /path/to/my/file
 
Once you have your credential strategy decided on, you are ready to run playbooks.
