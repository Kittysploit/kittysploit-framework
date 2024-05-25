import string
from kittysploit.core.base.exceptions import MaxLengthException, WasNotFoundException

MAX_PATTERN_LENGTH = 20280

def pattern_create(length: int):
	if int(length) >= MAX_PATTERN_LENGTH:
			raise MaxLengthException('ERROR: Pattern length exceeds ' 'maximum of {0}'.format(MAX_PATTERN_LENGTH))

	pattern = ''
	for upper in string.ascii_uppercase:
		for lower in string.ascii_lowercase:
			for digit in string.digits:
				if len(pattern) < int(length):
					pattern += upper+lower+digit
				else:
					out = pattern[:int(length)]
					return out

def pattern_offset(search_pattern):

    needle = search_pattern

    try:
        if needle.startswith('0x'):
            needle = needle[2:]
            needle = bytearray.fromhex(needle).decode('ascii')
            needle = needle[::-1]
    except (ValueError, TypeError) as e:
        raise

    haystack = ''
    for upper in string.ascii_uppercase:
        for lower in string.ascii_lowercase:
            for digit in string.digits:
                haystack += upper+lower+digit
                found_at = haystack.find(needle)
                if found_at > -1:
                    return found_at

    raise WasNotFoundException('Couldn`t find {0} ({1}) anywhere in the pattern.'.format(search_pattern,
                                                                 needle))