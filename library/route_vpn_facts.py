#!/usr/bin/python
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: route_vpn_facts
short_description: Facts about route VPNs
description:
  - Route VPN definitions in the SMC. Route VPN supports element
    expansion by providing the expand parameter with a valid choice.
    You can provide any or all of the supported expandable fields in
    any given run.

version_added: '2.5'

options:
  element:
    description:
      - Type of network element to retrieve
    required: false
    default: '*'
    choices:
      - host
      - network
      - router
      - address_range
      - interface_zone
      - domain_name
      - group
      - ip_list
      - country
      - alias
      - expression
    type: str
  expand:
    description:
      - Optionally expand element attributes that contain only href
    type: list
    choices:
      - rbvpn_tunnel_side_a
      - rbvpn_tunnel_side_b
      - vpn_profile_ref
      - monitoring_group_ref
  
extends_documentation_fragment:
  - stonesoft
  - stonesoft_facts

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''

RETURN = '''
# Find all route VPNs
"ansible_facts": {
    "route_vpn": [
        {
            "name": "myrbvpn", 
            "type": "rbvpn_tunnel"
        }
    ]
}
# Find route VPN based on filter
"ansible_facts": {
    "route_vpn": [
        {
            "enabled": true, 
            "monitoring_group_ref": "http://172.18.1.151:8082/6.4/elements/rbvpn_tunnel_monitoring_group/1", 
            "mtu": 0, 
            "name": "myrbvpn", 
            "pmtu_discovery": true, 
            "preshared_key": "*****", 
            "rbvpn_tunnel_side_a": {
                "gateway_ref": "http://172.18.1.151:8082/6.4/elements/single_fw/746/internal_gateway/12", 
                "tunnel_interface_ref": "http://172.18.1.151:8082/6.4/elements/single_fw/746/tunnel_interface/52"
            }, 
            "rbvpn_tunnel_side_b": {
                "gateway_ref": "http://172.18.1.151:8082/6.4/elements/external_gateway/19"
            }, 
            "read_only": false, 
            "system": false, 
            "ttl": 0, 
            "tunnel_mode": "vpn", 
            "vpn_profile_ref": "http://172.18.1.151:8082/6.4/elements/vpn_profile/4"
        }
    ]
}
# Find Route VPN by filter, expanding all fields
"ansible_facts": {
    "route_vpn": [
        {
            "enabled": true, 
            "monitoring_group_ref": {
                "name": "Uncategorized", 
                "read_only": true, 
                "system": true
            }, 
            "mtu": 0, 
            "name": "myrbvpn", 
            "pmtu_discovery": true, 
            "preshared_key": "*****", 
            "rbvpn_tunnel_side_a": {
                "antivirus": false, 
                "auto_certificate": true, 
                "dhcp_relay": {
                    "dhcp_add_info": 0, 
                    "dhcp_client_interface": "0", 
                    "dhcp_client_mode": 0, 
                    "dhcp_server_ref": [], 
                    "proxy_arp_address_list": "", 
                    "restricted_address_enabled": false, 
                    "restricted_address_list": "", 
                    "use_arp_proxy_enabled": false
                }, 
                "firewall": false, 
                "gateway_profile": "http://172.18.1.151:8082/6.4/elements/gateway_profile/3", 
                "name": "myfw - Primary", 
                "read_only": false, 
                "ssl_vpn_portal_setting": [], 
                "system": false, 
                "trust_all_cas": true, 
                "trusted_certificate_authorities": [], 
                "vpn_client_mode": "ipsec", 
                "windows-update": false
            }, 
            "rbvpn_tunnel_side_b": {
                "gateway_profile": "http://172.18.1.151:8082/6.4/elements/gateway_profile/1", 
                "name": "extgw3", 
                "read_only": false, 
                "system": false, 
                "trust_all_cas": true, 
                "trusted_certificate_authorities": []
            }, 
            "read_only": false, 
            "system": false, 
            "ttl": 0, 
            "tunnel_mode": "vpn", 
            "vpn_profile_ref": {
                "capabilities": {
                    "aes128_for_ike": false, 
                    "aes128_for_ipsec": false, 
                    "aes256_for_ike": false, 
                    "aes256_for_ipsec": false, 
                    "aes_gcm_256_for_ipsec": false, 
                    "aes_gcm_for_ipsec": false, 
                    "aes_xcbc_for_ipsec": false, 
                    "aggressive_mode": false, 
                    "ah_for_ipsec": false, 
                    "blowfish_for_ike": false, 
                    "blowfish_for_ipsec": false, 
                    "des_for_ike": false, 
                    "des_for_ipsec": false, 
                    "dh_group_14_for_ike": false, 
                    "dh_group_15_for_ike": false, 
                    "dh_group_16_for_ike": false, 
                    "dh_group_17_for_ike": false, 
                    "dh_group_18_for_ike": false, 
                    "dh_group_19_for_ike": false, 
                    "dh_group_1_for_ike": false, 
                    "dh_group_20_for_ike": false, 
                    "dh_group_21_for_ike": false, 
                    "dh_group_2_for_ike": true, 
                    "dh_group_50_for_ike": false, 
                    "dh_group_51_for_ike": false, 
                    "dh_group_5_for_ike": false, 
                    "dss_signature_for_ike": false, 
                    "ecdsa_signature_for_ike": false, 
                    "esp_for_ipsec": true, 
                    "external_for_ipsec": false, 
                    "forward_client_vpn": false, 
                    "forward_gw_to_gw_vpn": false, 
                    "gost_cfb_for_ike": false, 
                    "gost_cnt_1k_for_ipsec": false, 
                    "gost_cnt_4m_for_ipsec": false, 
                    "gost_for_ike": false, 
                    "gost_for_ipsec": false, 
                    "gost_g28147_imit_for_ipsec": false, 
                    "gost_g3411_for_ike": false, 
                    "gost_g3411_for_ipsec": false, 
                    "gost_signature_for_ike": false, 
                    "ike_v1": true, 
                    "ike_v2": true, 
                    "ipcomp_deflate_for_ipsec": false, 
                    "main_mode": true, 
                    "md5_for_ike": false, 
                    "md5_for_ipsec": false, 
                    "null_for_ipsec": false, 
                    "pfs_dh_group_14_for_ipsec": false, 
                    "pfs_dh_group_15_for_ipsec": false, 
                    "pfs_dh_group_16_for_ipsec": false, 
                    "pfs_dh_group_17_for_ipsec": false, 
                    "pfs_dh_group_18_for_ipsec": false, 
                    "pfs_dh_group_19_for_ipsec": false, 
                    "pfs_dh_group_1_for_ipsec": false, 
                    "pfs_dh_group_20_for_ipsec": false, 
                    "pfs_dh_group_21_for_ipsec": false, 
                    "pfs_dh_group_2_for_ipsec": false, 
                    "pfs_dh_group_50_for_ipsec": false, 
                    "pfs_dh_group_51_for_ipsec": false, 
                    "pfs_dh_group_5_for_ipsec": false, 
                    "pre_shared_key_for_ike": true, 
                    "rsa_signature_for_ike": false, 
                    "sa_per_host": false, 
                    "sa_per_net": true, 
                    "sha1_for_ike": true, 
                    "sha1_for_ipsec": true, 
                    "sha2_for_ike": false, 
                    "sha2_for_ipsec": false, 
                    "sha2_ike_hash_length": 256, 
                    "sha2_ipsec_hash_length": 256, 
                    "triple_des_for_ike": true, 
                    "triple_des_for_ipsec": true, 
                    "vpn_client_dss_signature_for_ike": false, 
                    "vpn_client_ecdsa_signature_for_ike": false, 
                    "vpn_client_gost_signature_for_ike": false, 
                    "vpn_client_rsa_signature_for_ike": true, 
                    "vpn_client_sa_per_host": false, 
                    "vpn_client_sa_per_net": true
                }, 
                "cn_authentication_for_mobile_vpn": false, 
                "comment": "VPN-A Cryptographic Suite", 
                "disable_anti_replay": false, 
                "disable_path_discovery": false, 
                "hybrid_authentication_for_mobile_vpn": false, 
                "name": "VPN-A Suite", 
                "preshared_key_authentication_for_mobile_vpn": false, 
                "read_only": false, 
                "sa_life_time": 86400, 
                "sa_to_any_network_allowed": false, 
                "system": true, 
                "trust_all_cas": true, 
                "trusted_certificate_authority": [], 
                "tunnel_life_time_kbytes": 0, 
                "tunnel_life_time_seconds": 28800
            }
        }
    ]
}
'''

from ansible.module_utils.stonesoft_util import StonesoftModuleBase, format_element


try:
    from smc.vpn.route import RouteVPN
except ImportError:
    pass
    

def valid_attr():
    return ('rbvpn_tunnel_side_a', 'rbvpn_tunnel_side_b',
        'vpn_profile_ref', 'monitoring_group_ref')


def to_yaml(vpn):
    rbvpn = {'name': vpn.name,
             'enabled': vpn.enabled}
    local_gw = vpn.local_endpoint
    gateway = local_gw.gateway
    rbvpn.update(local_gw=
        {'name': gateway.name.replace(' - Primary', ''),
         'tunnel_interface': local_gw.tunnel_interface.interface_id})
    
    for endpoint in gateway.internal_endpoint:
        if endpoint.enabled:
            rbvpn.setdefault('local_gw').update(address=endpoint.name)
            break
    
    remote_gw = vpn.remote_endpoint
    gateway = remote_gw.gateway
    if gateway.typeof == 'internal_gateway':
        rbvpn.update(remote_gw=
            {'name': gateway.name.replace(' - Primary', ''),
             'tunnel_interface': remote_gw.tunnel_interface.interface_id})
        
        for endpoint in gateway.internal_endpoint:
            if endpoint.enabled:
                rbvpn.setdefault('remote_gw').update(address=endpoint.name)
                break
    else: #External GW
        remote_gw = {'name': gateway.name,
                     'type': gateway.typeof,
                     'preshared_key': '********'}
        endpoints = []
        for endpoint in gateway.external_endpoint:
            endpoints.append({
                'name': endpoint.name,
                'address': endpoint.address,
                'enabled': endpoint.enabled})
        remote_gw.update(external_endpoint=endpoints)
        # Obtain VPN sites
        vpn_site = {}
        site_elements = {} # Dict of typeof: [element names]
        for site in gateway.vpn_site:
            vpn_site.update(name=site.name)
            for element in site.site_element:
                vpn_site.setdefault(element.typeof, []).append(
                    element.name)
            break
        vpn_site.update(site_elements)
        remote_gw.update(vpn_site=vpn_site)
        rbvpn.update(remote_gw=remote_gw)
        return rbvpn
    
    
def to_dict(vpn, expand=None):
    """
    Flatten the route VPN
    
    :param policy_vpn PolicyVPN
    :return dict
    """
    expand = expand if expand else []
    if not expand:
        return format_element(vpn)
    else:
        if 'vpn_profile_ref' in expand:
            vpn.data['vpn_profile_ref'] = format_element(vpn.vpn_profile)
        if 'monitoring_group_ref' in expand:
            vpn.data['monitoring_group_ref'] = format_element(vpn.monitoring_group)
        if 'rbvpn_tunnel_side_a' in expand:
            vpn.data['rbvpn_tunnel_side_a'] = format_element(vpn.local_endpoint.gateway)
        if 'rbvpn_tunnel_side_b' in expand:
            vpn.data['rbvpn_tunnel_side_b'] = format_element(vpn.remote_endpoint.gateway)
        return format_element(vpn)

    
class RouteVPNFacts(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            expand=dict(default=[], type='list')
        )
        self.element = 'rbvpn_tunnel'
        self.limit = None
        self.filter = None
        self.as_yaml = None
        self.expand = None
        self.exact_match = None
        self.case_sensitive = None
        
        self.results = dict(
            ansible_facts=dict(
                route_vpn=[]
            )
        )
        super(RouteVPNFacts, self).__init__(self.module_args, is_fact=True)

    def exec_module(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        if self.as_yaml and not self.filter:
            self.fail(msg='You must provide a filter to use the as_yaml '
                'parameter')
        
        valid = valid_attr()
        for attr in self.expand:
            if attr not in valid:
                self.fail(msg='Invalid expandable attribute provided: {}. Valid options '
                    'are {}'.format(attr, list(valid)))
            
        result = self.search_by_type(RouteVPN)
        # Search by specific element type
        if self.filter:
            if self.as_yaml:
                route_vpn = [to_yaml(rbvpn) for rbvpn in result
                             if rbvpn.name == self.filter]
            else:
                route_vpn = [to_dict(element, self.expand) for element in result]
        else:
            route_vpn = [{'name': element.name, 'type': element.typeof} for element in result]
        
        self.results['ansible_facts']['route_vpn'] = route_vpn
        return self.results

def main():
    RouteVPNFacts()
    
if __name__ == '__main__':
    main()
