# PyTest Debugging Guide

Complete guide to debugging with pytest and pdb

## 1. COMMAND LINE WITH PYTEST (Automatic on Failure)

```bash
# Drop into debugger automatically when a test fails
pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --pdb

# Drop into debugger automatically on FIRST failure and stop
pytest tests/test_document_reader.py --pdb -x

# Use ipdb as debugger (if installed: pip install ipdb)
pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --pdbcls=IPython.terminal.debugger:TerminalPdb
```

## 2. MANUAL BREAKPOINTS IN CODE

```python
# Add this line anywhere in your code to set a breakpoint:
import pdb; pdb.set_trace()

# Python 3.7+ has a built-in breakpoint() function:
breakpoint()
```

## 3. COMMAND LINE WITH PYTHON SCRIPT

```bash
# Run any Python script with debugger
python -m pdb your_script.py

# Run and break at first line
python -c "import pdb; pdb.run('exec(open(\"your_script.py\").read())')"
```

## 4. POST-MORTEM DEBUGGING

```python
# Debug after an exception occurs
python -c "
import pdb, traceback, sys
try:
    exec(open('your_script.py').read())
except:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
"
```

## PDB COMMANDS QUICK REFERENCE

When in pdb debugger, use these commands:

### Basic Navigation:
- `l` (list) - Show current code
- `ll` - Show full function
- `w` (where) - Show stack trace
- `u` (up) - Go up in stack
- `d` (down) - Go down in stack

### Execution Control:
- `n` (next) - Execute next line
- `s` (step) - Step into functions
- `c` (continue) - Continue execution
- `r` (return) - Continue until return
- `q` (quit) - Quit debugger

### Variables & Expressions:
- `p <var>` - Print variable
- `pp <var>` - Pretty print variable
- `a` (args) - Print function arguments
- `!<statement>` - Execute Python statement
- `<expression>` - Evaluate and print expression

### Breakpoints:
- `b` - List breakpoints
- `b <line>` - Set breakpoint at line
- `b <file:line>` - Set breakpoint at file:line
- `cl` - Clear all breakpoints
- `cl <bp_num>` - Clear specific breakpoint

## PYTEST SPECIFIC OPTIONS

Other useful pytest debugging options:
- `-s` - Show print statements (disable capture)
- `-vv` - Extra verbose output
- `--tb=long` - Show long traceback format
- `--tb=short` - Show short traceback format
- `--tb=line` - Show minimal traceback
- `--lf` - Run only failing tests from last run
- `-x` - Stop on first failure
- `--pdbcls` - Use custom debugger class
