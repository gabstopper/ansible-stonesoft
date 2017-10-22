## ansible-stonesoft

This repository provides [Ansible](https://www.ansible.com)  modules for configuration and automation of [Stonesoft Next Generation Firewall](https://www.forcepoint.com/product/network-security/forcepoint-ngfw). It uses the [smc-python](https://github.com/gabstopper/smc-python) for all operations between the ansible client and the Stonesoft Management Center.

#### Prerequisites

* smc-python >= 0.5.6
* Stonesoft Management Center 6.x
* API client account with permissions

### Installation

#### Using `virtualenv` (recommended)
```
pip install ansible
git clone https://github.com/gabstopper/ansible-stonesoft.git
cd ansible-stonsoft
pip install -r requirements.txt
```

* Enable the SMC API within the management center

### Usage


Each ansible run will require a login event to the Stonesoft Management Center to perform it's operations. 
Since the ansible libraries use smc-python, the login process uses the same [session](http://smc-python.readthedocs.io/en/latest/pages/session.html) logic.


* You can provide url and api_key as task parameters
* You can provide the `smc_alt_filepath` parameter in the task run to specify where to find the .smcrc file with your stored credentials

If neither of the two above are used, then:
* Try to find ~.smcrc in users home directory
* Use environment variables (SMC_ADDRESS, SMC_API_KEY, ...)

If none of the above succeed, the run will fail. 

### Running playbooks

Before running plays, it's best to explain the architecture used to make the administrative changes. 


The Stonesoft Management Center is where modifications to all elements are performed. 

Installing the ansible modules can therefore either be done on a client host machine remote from the SMC, or on the SMC itself.

If the ansible modules are installed on a controller that is remote from the SMC, set your inventory to use localhost for the connection. 

For example, set your default inventory */etc/ansible/hosts*:
```
localhost ansible_connection=local
```
Note that the host running the ansible client will still need to connect to the SMC through the smc-python API over the default port 8082/tcp.

The other option is to install the ansible libraries on the SMC server itself and make your ansible runs from the controller client. In this case, the SMC connection can then be done using an SMC url of 127.0.0.1.

#### More information

All modules provide doc snippets when run from the ansible client:

```
ansible-doc -s stonesoft_l3fw
```

#### Contributions

If you have requests for additional configuration functionality, please submit an issue request.
