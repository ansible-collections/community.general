# interfaces_file unit tests

## Tests structure

- `input` directory contains interfaces configuration files
- `test_interfaces_file.py` runs each hardcoded test agains all configurations in `input` directory and compares results with golden outputs in `golden_output`

## Running unit tests with docker

1. Clone project to `ansible_collections/community/general`
2. Change directory to the project one `cd ansible_collections/community/general`
3. Run `ansible-test units --docker -v --python 3.6 tests/unit/plugins/modules/system/interfaces_file/test_interfaces_file.py`

## Adding tests

1. New configurations should added to `input` directory
2. New test cases should be defined in `test_interfaces_file.py`. Same for new test functions if needed
3. On first test run for a new combination of a test case and an interface configuration new set of golden files will be generated. In case of docker-based test approach that's going to fail due to RO mount option. The workaround is to run tests locally with Python 3 (3.7 in this example):
    1. Install required modules with `pip3.7 install pytest-xdist pytest-mock mock`
    3. Run tests with `ansible-test units --python 3.7 tests/unit/plugins/modules/system/interfaces_file/test_interfaces_file.py`
4. Carefully verify newly created golden output files!
