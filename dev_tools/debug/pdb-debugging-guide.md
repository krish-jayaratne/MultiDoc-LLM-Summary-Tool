# PDB Complete Debugging Guide

🐛 **COMPLETE PDB DEBUGGING GUIDE**

## METHOD 1: pytest --pdb (MOST COMMON for test debugging)

This automatically drops into debugger when a test FAILS

```bash
# Run specific failing test with debugger
pytest demo_failing_test.py::test_that_will_fail_for_demo --pdb

# Run with extra verbosity
pytest demo_failing_test.py::test_that_will_fail_for_demo --pdb -v

# Stop on first failure and debug
pytest demo_failing_test.py --pdb -x
```

## METHOD 2: Manual breakpoints in code

Add these lines directly in your Python code:

```python
# Classic pdb breakpoint
import pdb; pdb.set_trace()

# Python 3.7+ breakpoint function
breakpoint()

# Conditional breakpoint
if some_condition:
    import pdb; pdb.set_trace()
```

## METHOD 3: Command line with Python scripts

```bash
# Run any Python script with debugger
python -m pdb your_script.py

# Debug a specific function
python -c "import pdb; import your_module; pdb.run(\"your_module.your_function()\")"
```

## METHOD 4: Post-mortem debugging

Debug after an exception has already occurred:

```python
import pdb, traceback, sys
try:
    exec(open("your_script.py").read())
except:
    extype, value, tb = sys.exc_info()
    traceback.print_exc()
    pdb.post_mortem(tb)
```

## PDB COMMANDS (when in debugger)

### Navigation:
- `l, ll` - List code around current line / full function
- `w` - Show current stack trace
- `u, d` - Move up/down the call stack

### Execution:
- `n` - Execute next line (don't step into functions)
- `s` - Step into functions
- `c` - Continue execution
- `r` - Continue until current function returns
- `q` - Quit debugger

### Variables:
- `p <var>` - Print variable value
- `pp <var>` - Pretty print variable
- `a` - Print function arguments
- `!<code>` - Execute Python code

### Breakpoints:
- `b` - List all breakpoints
- `b <line>` - Set breakpoint at line number
- `b <func>` - Set breakpoint at function
- `cl` - Clear all breakpoints

## PRACTICAL EXAMPLES

### Example 1: Debug failing test
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest demo_failing_test.py::test_that_will_fail_for_demo --pdb
```

### Example 2: Debug with manual breakpoint
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" demo_failing_test.py
```

### Example 3: Debug specific function interactively
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -c "
import pdb
from src.document_summarizer.base.document_reader import TextDocumentReader
reader = TextDocumentReader()
pdb.run(\"result = reader._generate_description(\\\"test content\\\")\")
"
```

## TIPS FOR EFFECTIVE DEBUGGING

1. Use `l` frequently to see where you are in the code
2. Use `pp variable_name` to inspect complex objects
3. Use `!variable_name = new_value` to modify variables during debugging
4. Use `a` to see what arguments were passed to the current function
5. Use `w` to understand the call stack when you're deep in nested calls
6. Use `c` to continue to the next breakpoint or error
7. Use `q` to exit when you're done debugging
