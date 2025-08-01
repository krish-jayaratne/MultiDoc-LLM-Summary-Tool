# Debug Commands Reference

Quick reference for debugging test failures

## 1. Run specific failing test with maximum verbosity
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content -vv -s
```

## 2. Drop into debugger on failure
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --pdb
```

## 3. Show detailed traceback
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --tb=long
```

## 4. Run only failed tests from last run
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest --lf
```

## 5. Stop on first failure
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest -x
```

## 6. Run with coverage to see which lines are executed
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --cov=src/document_summarizer --cov-report=term-missing
```

## 7. Time the test execution
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --durations=10
```

## 8. Show all available fixtures
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest --fixtures
```

## 9. Dry run (collect tests without running)
```bash
"/home/krish/repos/document_summarizer/.venv/bin/python" -m pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --collect-only
```
