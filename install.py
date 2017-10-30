#!/usr/bin/python
# Base installer helper

import sys
import os.path
import shutil

    
def main():
    try:
        import ansible
    except ImportError:
        print('Ansible module is required for installation.')
        sys.exit(1)

    # Find the module paths
    ansible_path = os.path.dirname(os.path.abspath(os.path.realpath(ansible.__file__)))
    
    '''
    # Check to see if appropriate directories exist
    module_utils_path = os.path.join(ansible_path, 'module_utils')
    if not os.path.exists(module_utils_path):
        print('Module utils directory (%s) does not exist' % module_utils_path)
        sys.exit(1)
    if not os.path.isdir(module_utils_path):
        print('Module utils path (%s) is not a directory' % module_utils_path)
        sys.exit(1)
    '''
    # Where is this package located
    here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    
    # Copy the module document fragments to the module docs directory so the 
    # documentation fragments display properly for the modules
    module_doc_path = os.path.join(ansible_path, 'utils', 'module_docs_fragments')
    if not os.path.exists(module_doc_path):
        print('Could not find ansible document module path!')
        sys.exit(1)
    else:
        here_doc_fragments = os.path.join(here, 'doc_fragments')
        for filename in os.listdir(here_doc_fragments):
            print("Copying doc fragment: %s" % filename)
            shutil.copy(os.path.join(here_doc_fragments, filename),
                        os.path.join(module_doc_path, filename))


if __name__ == '__main__':
    main()