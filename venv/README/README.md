[![Build Status](https://travis-ci.com/daveoncode/python-string-utils.svg?branch=develop)](https://travis-ci.com/daveoncode/python-string-utils)
[![codecov](https://codecov.io/gh/daveoncode/python-string-utils/branch/develop/graph/badge.svg)](https://codecov.io/gh/daveoncode/python-string-utils)
[![Documentation Status](https://readthedocs.org/projects/python-string-utils/badge/?version=develop)](https://python-string-utils.readthedocs.io/en/develop)
[![Python 3.5](https://img.shields.io/badge/python-3.5-blue.svg)](https://www.python.org/downloads/release/python-350/)
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# Python String Utils
##### Latest version: [1.0.0](https://github.com/daveoncode/python-string-utils/blob/master/CHANGELOG.md) (March 2020)

A handy library to validate, manipulate and generate strings, which is:

- Simple and "pythonic"
- Fully documented and with examples! (html version on [readthedocs.io](https://python-string-utils.readthedocs.io/en/develop))
- 100% code coverage! (see it with your own eyes on [codecov.io](https://codecov.io/gh/daveoncode/python-string-utils/branch/develop))
- Tested (automatically on each push thanks to Travis CI) against all officially supported Python versions
- Fast (mostly based on compiled regex)
- Free from external dependencies
- PEP8 compliant


## What's inside...

### Library structure

The library basically consists in the python package `string_utils`, containing the following modules:

- `validation.py` (contains string check api)
- `manipulation.py` (contains string transformation api)
- `generation.py` (contains string generation api)
- `errors.py` (contains library-specific errors)
- `_regex.py` (contains compiled regex **FOR INTERNAL USAGE ONLY**)

Plus a secondary package `tests` which includes several submodules.\
Specifically one for each test suite and named according to the api to test (eg. tests for `is_ip()` 
will be in `test_is_ip.py` and so on).

All the public API are importable directly from the main package `string_utils`, so this:

`from string_utils.validation import is_ip`

can be simplified as:
 
 `from string_utils import is_ip`

### Api overview

***Bear in mind**: this is just an overview, 
for the full API documentation see:* [readthedocs.io](https://python-string-utils.readthedocs.io/en/develop)

#### String validation functions:


**is_string**: checks if the given object is a string
~~~~
is_string('hello') # returns true
is_string(b'hello') # returns false
~~~~

**is_full_string**: checks if the given object is non empty string
~~~~
is_full_string(None) # returns false
is_full_string('') # returns false
is_full_string(' ') # returns false
is_full_string('foo') # returns true
~~~~

**is_number**: checks if the given string represents a valid number
~~~~
is_number('42') # returns true
is_number('-25.99') # returns true
is_number('1e3') # returns true
is_number(' 1 2 3 ') # returns false
~~~~

**is_integer**: checks if the given string represents a valid integer
~~~~
is_integer('42') # returns true
is_integer('42.0') # returns false
~~~~

**is_decimal**: checks if the given string represents a valid decimal number
~~~~
is_decimal('42.0') # returns true
is_decimal('42') # returns false
~~~~

**is_url**: checks if the given string is an url
~~~~
is_url('foo.com') # returns false
is_url('http://www.foo.com') # returns true
is_url('https://foo.com') # returns true
~~~~

**is_email**: Checks if the given string is an email
~~~~
is_email('my.email@some.provider.com') # returns true
is_eamil('@gmail.com') # retruns false
~~~~

**is_credit_card**: Checks if the given string is a credit card
~~~~
is_credit_card(value)

# returns true if `value` represents a valid card number for one of these:
# VISA, MASTERCARD, AMERICAN EXPRESS, DINERS CLUB, DISCOVER or JCB
~~~~

**is_camel_case**: Checks if the given string is formatted as camel case
~~~~
is_camel_case('MyCamelCase') # returns true
is_camel_case('hello') # returns false
~~~~

**is_snake_case**: Checks if the given string is formatted as snake case
~~~~
is_snake_case('snake_bites') # returns true
is_snake_case('nope') # returns false
~~~~

**is_json**: Checks if the given string is a valid json
~~~~
is_json('{"first_name": "Peter", "last_name": "Parker"}') # returns true
is_json('[1, 2, 3]') # returns true
is_json('{nope}') # returns false
~~~~

**is_uuid**: Checks if the given string is a valid UUID
~~~~
is_uuid('ce2cd4ee-83de-46f6-a054-5ee4ddae1582') # returns true
~~~~

**is_ip_v4**: Checks if the given string is a valid ip v4 address
~~~~
is_ip_v4('255.200.100.75') # returns true
is_ip_v4('255.200.100.999') # returns false (999 is out of range)
~~~~

**is_ip_v6**: Checks if the given string is a valid ip v6 address
~~~~
is_ip_v6('2001:db8:85a3:0000:0000:8a2e:370:7334') # returns true
is_ip_v6('123:db8:85a3:0000:0000:8a2e:370,1') # returns false
~~~~

**is_ip**: Checks if the given string is a valid ip (any version)
~~~~
is_ip('255.200.100.75') # returns true
is_ip('2001:db8:85a3:0000:0000:8a2e:370:7334') # returns true
is_ip('255.200.100.999') # returns false
is_ip('123:db8:85a3:0000:0000:8a2e:370,1') # returns false
~~~~

**is_isnb_13**: Checks if the given string is a valid ISBN 13
~~~~
is_isbn_13('9780312498580') # returns true
is_isbn_13('978-0312498580') # returns true
is_isbn_13('978-0312498580', normalize=False) # returns false
~~~~

**is_isbn_10**: Checks if the given string is a valid ISBN 10
~~~~
is_isbn_10('1506715214') # returns true
is_isbn_10('150-6715214') # returns true
is_isbn_10('150-6715214', normalize=False) # returns false
~~~~

**is_isbn**: Checks if the given string is a valid ISBN (any version)
~~~~
is_isbn('9780312498580') # returns true
is_isbn('1506715214') # returns true
~~~~

**is_slug**: Checks if the string is a slug (as created by `slugify()`)
~~~~
is_slug('my-blog-post-title') # returns true
is_slug('My blog post title') # returns false
~~~~

**contains_html**: Checks if the strings contains one ore more HTML/XML tag
~~~~
contains_html('my string is <strong>bold</strong>') # returns true
contains_html('my string is not bold') # returns false
~~~~

**words_count**: Returns the number of words contained in the string
~~~~
words_count('hello world') # returns 2
words_count('one,two,three') # returns 3 (no need for spaces, punctuation is recognized!)
~~~~

**is_palindrome**: Checks if the string is a palindrome
~~~~
is_palindrome('LOL') # returns true
is_palindrome('ROTFL') # returns false
~~~~

**is_pangram**: Checks if the string is a pangram
~~~~
is_pangram('The quick brown fox jumps over the lazy dog') # returns true
is_pangram('hello world') # returns false
~~~~

**is_isogram**: Checks if the string is an isogram
~~~~
is_isogram('dermatoglyphics') # returns true
is_isogram('hello') # returns false
~~~~

#### String manipulation:

**camel_case_to_snake**:  Converts a camel case formatted string into a snake case one
~~~~
camel_case_to_snake('ThisIsACamelStringTest') # returns 'this_is_a_camel_case_string_test'
~~~~

**snake_case_to_camel**: Converts a snake case formatted string into a camel case one
~~~~
snake_case_to_camel('the_snake_is_green') # returns 'TheSnakeIsGreen'
~~~~

**reverse**: Returns the string in a reversed order
~~~
reverse('hello') # returns 'olleh'
~~~

**shuffle**: Returns the string with its original chars but at randomized positions
~~~~
shuffle('hello world') # possible output: 'l wodheorll'
~~~~

**strip_html**: Removes all the HTML/XML tags found in a string
~~~~
strip_html('test: <a href="foo/bar">click here</a>') # returns 'test: '
strip_html('test: <a href="foo/bar">click here</a>', keep_tag_content=True) # returns 'test: click here'
~~~~

**prettify**: Reformat a string by applying basic grammar and formatting rules
~~~~
prettify(' unprettified string ,, like this one,will be"prettified" .it\' s awesome! ')
# the ouput will be: 'Unprettified string, like this one, will be "prettified". It\'s awesome!'
~~~~

**asciify**: Converts all non-ascii chars contained in a string into the closest possible ascii representation
~~~~
asciify('èéùúòóäåëýñÅÀÁÇÌÍÑÓË') 
# returns 'eeuuooaaeynAAACIINOE' (string is deliberately dumb in order to show char conversion)
~~~~

**slugify**: Convert a string into a formatted "slug"
~~~~
slugify('Top 10 Reasons To Love Dogs!!!') # returns: 'top-10-reasons-to-love-dogs'
~~~~

**booleanize**: Convert a string into a boolean based on its content
~~~~
booleanize('true') # returns true
booleanize('YES') # returns true
booleanize('y') # returns true
booleanize('1') # returns true
booelanize('something else') # returns false
~~~~

**strip_margin**: Removes left indentation from multi-line strings (inspired by Scala)
~~~~
strip_margin('''
        line 1
        line 2
        line 3
''')

#returns:
'''
line 1
line 2
line 3
'''
~~~~

**compress/decompress**: Compress strings into shorted ones that can be restored back to the original one later on
~~~~
compressed = compress(my_long_string) # shorter string (URL safe base64 encoded)

decompressed = decompress(compressed) # string restored

assert(my_long_string == decompressed) # yep
~~~~

**roman_encode**: Encode integers/string into roman numbers
~~~
roman_encode(37) # returns 'XXXVII'
~~~~

**roman_decode**: Decode roman number into an integer
~~~~
roman_decode('XXXVII') # returns 37
~~~~

**roman_range**: Generator which returns roman numbers on each iteration
~~~~
for n in roman_range(10): print(n) # prints: I, II, III, IV, V, VI, VII, VIII, IX, X
for n in roman_range(start=7, stop=1, step=-1): print(n) # prints: VII, VI, V, IV, III, II, I
~~~~

#### String generations:

**uuid**: Returns the string representation of a newly created UUID object
~~~~
uuid() # possible output: 'ce2cd4ee-83de-46f6-a054-5ee4ddae1582'
uuid(as_hex=True) # possible output: 'ce2cd4ee83de46f6a0545ee4ddae1582'
~~~~

**random_string**: Creates a string of the specified size with random chars
~~~~
random_string(9) # possible output: 'K1URtlTu5'
~~~~

**secure_random_hex**: Creates an hexadecimal string using a secure strong random generator
~~~~
secure_random_hex(12) 
# possible ouput: 'd1eedff4033a2e9867c37ded' 
# (len is 24, because 12 represents the number of random bytes generated, which are then converted to hexadecimal value)
~~~~


## Installation

    pip install python-string-utils


## Checking installed version

~~~
import string_utils
string_utils.__version__
'1.0.0' # (if '1.0.0' is the installed version)
~~~

## Documentation

Full API documentation available on [readthedocs.io](https://python-string-utils.readthedocs.io/en/develop)


## Support the project!

Do you like this project? Would you like to see it updated more often with new features and improvements?
If so, you can make a small donation by clicking the button down below, it would be really appreciated! :)

<a href="https://www.buymeacoffee.com/c4yYUvp" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217" height="51" />
</a>
