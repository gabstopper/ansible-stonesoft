#
# (c) 2017, David LePage (@gabstopper)
# Stonesoft Documentation fragment. This fragment specifies the top level
# requirements for obtaining a valid session to the Stonesoft Management
# Center. 

class ModuleDocFragment(object):
    # Standard Stonesoft documentation fragment
    DOCUMENTATION = '''
options:
  smc_address:
    description:
      - FQDN with port of SMC. The default value is the environment variable C(SMC_ADDRESS)
    required: false
  smc_api_key:
    description:
       - API key for api client. The default value is the environment variable C(SMC_API_KEY)
         Required if I(url)
    required: false
  smc_api_version:
    description:
      - Optional API version to connect to. If none is provided, the latest
        SMC version API will be used based on the Management Center version.
        Can be set though the environment variable C(SMC_API_VERSION)
    required: false
  smc_timeout:
    description:
      - Optional timeout for connections to the SMC. Can be set through environment C(SMC_TIMEOUT)
    required: false
  smc_domain:
    description:
      - Optional domain to log in to. If no domain is provided, 'Shared Domain' is used. Can be
        set throuh the environment variable C(SMC_DOMAIN)
    required: false
  smc_alt_filepath:
    description:
      - Provide an alternate path location to read the credentials from. File is expected to
        be stored in ~.smcrc. If provided, url and api_key settings are not required and will be ignored.
    required: false
  smc_logging:
    description:
      - Optionally enable SMC API logging to a file
    required: false
    type: dict
    suboptions:
      level:
        description:
          - Log level as specified by the standard python logging library, in int format. Default
            setting is logging.DEBUG.
        type: int
      path:
        description:
          - Full path to the log file
        type: str
        required: true
  smc_extra_args:
    description: 
      - Extra arguments to pass to login constructor. These are generally only used if
        specifically requested by support personnel.
    required: false
    suboptions:
      verify:
        description: 
          - Is the connection to SMC is HTTPS, you can set this to True, or provide a path
            to a client certificate to verify the SMC SSL certificate. You can also explicitly
            set this to False.
        default: true
        type: bool
'''
