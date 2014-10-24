import sys

# Type Checker
def raise_for_type(value, expected_type):
    if expected_type and type(value) is not expected_type:
        raise ValueError('{} is not of type: {}'.format(value, expected_type))

def unicode_to_str(uni):
    if sys.version_info[0] == 2:
        return uni.encode('utf-8') # python2's str = bytes
    else:
        return uni # python3's str = unicode

def compatible_input(prompt=''):
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    else:
        return input(prompt)
