# sqAPI Tests

## Structure
The package structure of the test directory should be
equal to the source code structure.
This means that each package should be represented with one module
for each module in the source code.

#### Example
```bash
src
└── sqapi
    └── messaging
        └── util.py
test
└── sqapi
    └── messaging
        └── test_util.py
```

## Running tests
When standing in the project root directory,
all tests could be run by the following command.
```bash
PYTHONPATH=${PWD}/src python3 -m unittest discover
```
