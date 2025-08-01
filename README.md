# Document Analyzer

A Python project for analyzing documents with extensible architecture for metadata extraction and future LLM integration.

## Features

- Base document reader class for extensible document processing
- Comprehensive metadata extraction (names, dates, entities, people, descriptions)
- Extensible architecture ready for LLM integration
- Comprehensive test suite with 48 passing tests

## Project Structure

```
document-analyzer/
├── src/
│   └── document_analyzer/
│       ├── __init__.py
│       ├── base/
│       │   ├── __init__.py
│       │   └── document_reader.py      # Base classes and TextDocumentReader
│       ├── models/
│       │   ├── __init__.py
│       │   └── metadata.py             # DocumentMetadata model
│       └── interfaces/
│           ├── __init__.py
│           └── llm_interface.py        # LLM integration interfaces
├── tests/
│   ├── __init__.py
│   ├── test_document_reader.py         # Document reader tests
│   ├── test_metadata.py                # Metadata model tests
│   └── test_llm_interface.py           # LLM interface tests
├── .github/
│   └── copilot-instructions.md         # Development guidelines
├── requirements.txt                    # Project dependencies
├── pyproject.toml                      # Modern Python packaging config
└── example_usage.py                    # Usage demonstration
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd document-analyzer

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from document_analyzer.base.document_reader import TextDocumentReader
from document_analyzer.models.metadata import DocumentMetadata

# Create a document reader instance
reader = TextDocumentReader()

# Extract metadata from a document
metadata = reader.extract_metadata("path/to/document.txt")

# Display results
print(f"Document: {metadata.name}")
print(f"Description: {metadata.description}")
print(metadata.to_summary())
```

### Advanced Usage with Document Analyzer

```python
from document_analyzer.interfaces.llm_interface import DocumentAnalyzer
from document_analyzer.base.document_reader import TextDocumentReader

# Initialize analyzer (without LLM for now)
analyzer = DocumentAnalyzer()
reader = TextDocumentReader()

# Analyze a single document
result = analyzer.analyze_single_document("document.txt", reader)

# Cross-reference multiple documents
results = analyzer.cross_reference_documents([
    "doc1.txt", "doc2.txt", "doc3.txt"
], reader)
```

### Running the Example

```bash
python example_usage.py
```

## Testing

### Run All Tests
```bash
# Basic test run
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=src/document_analyzer --cov-report=html
```

### Run Specific Tests
```bash
# Run tests for a specific module
pytest tests/test_document_reader.py

# Run a specific test function
pytest tests/test_document_reader.py::TestTextDocumentReader::test_extract_metadata_complete
```

## Development

### Architecture Overview

The project follows a modular, extensible architecture:

- **Base Classes**: `DocumentReader` abstract base class for different document types
- **Metadata Model**: `DocumentMetadata` with comprehensive entity tracking
- **LLM Integration**: Interface-based design ready for multiple LLM providers
- **Testing**: Comprehensive test suite with 48 tests covering all functionality

### Adding New Document Types

1. Inherit from `DocumentReader`:
```python
class PDFDocumentReader(DocumentReader):
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.pdf'}
    
    def read_content(self, file_path: str) -> str:
        # Implement PDF reading logic
        pass
```

2. Override entity extraction methods if needed for document-specific patterns

### Debugging Tests

When tests fail, use these debugging techniques:

#### 1. Command Line Debugging with pytest

```bash
# Drop into debugger automatically when a test fails
pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --pdb

# Drop into debugger on FIRST failure and stop
pytest tests/test_document_reader.py --pdb -x

# Show all print statements and detailed output
pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content -vv -s

# Show detailed traceback
pytest tests/test_document_reader.py::TestTextDocumentReader::test_generate_description_short_content --tb=long
```

#### 2. Manual Breakpoints in Code

Add debugging breakpoints directly in your code:

```python
# Classic pdb breakpoint
import pdb; pdb.set_trace()

# Python 3.7+ breakpoint function
breakpoint()

# Conditional breakpoint
if some_condition:
    import pdb; pdb.set_trace()
```

#### 3. PDB Commands Reference

When in the debugger, use these commands:

**Navigation:**
- `l` (list) - Show current code
- `ll` - Show full function
- `w` (where) - Show stack trace
- `u` (up) / `d` (down) - Navigate call stack

**Execution Control:**
- `n` (next) - Execute next line
- `s` (step) - Step into functions
- `c` (continue) - Continue execution
- `r` (return) - Continue until return
- `q` (quit) - Quit debugger

**Variables & Inspection:**
- `p <var>` - Print variable
- `pp <var>` - Pretty print variable
- `a` (args) - Print function arguments
- `!<statement>` - Execute Python statement

**Breakpoints:**
- `b` - List breakpoints
- `b <line>` - Set breakpoint at line
- `cl` - Clear all breakpoints

#### 4. Other Useful pytest Options

- `--lf` - Run only failing tests from last run
- `-x` - Stop on first failure
- `--tb=short` - Short traceback format
- `--tb=line` - Minimal traceback
- `-s` - Show print statements (disable capture)

### Code Style Guidelines

- Use descriptive method names like `extract_metadata`, `add_organization`
- Entity types should be plural in lists: `organizations`, `people_mentioned`
- Use snake_case for Python methods and variables
- Always validate file existence before processing
- Use appropriate exceptions (FileNotFoundError, IOError, etc.)
- Write comprehensive tests for all entity extraction methods

### Extension Points

#### Adding New Entity Types
1. Add new fields to `DocumentMetadata` dataclass
2. Add corresponding `add_*` methods with duplicate checking
3. Update the `to_summary()` method to include new entities
4. Add extraction logic in document readers

#### LLM Integration (Future)
1. Implement concrete LLM interface classes (OpenAI, Azure, etc.)
2. Add error handling for API failures
3. Implement caching for LLM responses
4. Add configuration for different models and parameters

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Dependencies

### Core Dependencies
- `dataclasses-json>=0.6.0` - JSON serialization for dataclasses
- `python-dateutil>=2.8.0` - Enhanced date parsing
- `typing-extensions>=4.0.0` - Extended type hints

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting

### Future Dependencies (for LLM integration)
- `openai>=1.0.0` - OpenAI API client
- `azure-openai>=1.0.0` - Azure OpenAI client

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

### Current Status ✅
- [x] Base document reader architecture
- [x] Comprehensive metadata model
- [x] Text document processing
- [x] Entity extraction (organizations, people, dates, documents)
- [x] Complete test suite (48 tests)
- [x] Extensible LLM interface design

### Planned Features 🚧
- [ ] PDF document reader implementation
- [ ] DOCX document reader implementation
- [ ] OpenAI LLM integration
- [ ] Azure OpenAI LLM integration
- [ ] Enhanced NER with spaCy/NLTK
- [ ] Document similarity analysis
- [ ] REST API interface
- [ ] Web interface for document upload and analysis

### Future Enhancements 🔮
- [ ] Support for images and OCR
- [ ] Document classification models
- [ ] Real-time document monitoring
- [ ] Integration with document management systems
- [ ] Advanced relationship mapping between documents