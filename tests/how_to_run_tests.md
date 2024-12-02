# Tests

Testing will be/has been done sparsely in this project.
A small test is created whenever a logical error occurs (not small syntax errors).

## Prerequisites

Set your path variables in test_config.sh.

## Execution

**PLEASE MAKE SURE TO RUN THE SCRIPT FROM THE REPOSITORIES BASE DIRECTORY.**

### Bash tests

```bash
tests/run_tests.sh tests/test_pblock_config.sh
```

### Python tests

Run this command from the repositories base directory (xilinx-bram-evaluation)

```bash
python -m unittest discover tests
```
