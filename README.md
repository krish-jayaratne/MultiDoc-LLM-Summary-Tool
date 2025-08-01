# MultiDoc-LLM-Summary-Tool

A Python project for analyzing and summarizing documents with extensible architecture for metadata extraction and LLM integration.

## Features

- Base document reader classes for extensible document processing (Text and PDF support)
- Comprehensive metadata extraction (names, dates, entities, people, descriptions)
- LLM integration with OpenAI support for document analysis and summarization
- Document cross-referencing and relationship analysis
- Comprehensive test suite with extensive coverage

## Project Structure

```
document_summarizer/
├── src/
│   └── document_summarizer/
│       ├── __init__.py
│       ├── base/
│       │   ├── __init__.py
│       │   ├── document_reader.py      # Base classes and TextDocumentReader
│       │   └── pdf_reader.py           # PDF document reader
│       ├── models/
│       │   ├── __init__.py
│       │   └── metadata.py             # DocumentMetadata model
│       └── interfaces/
│           ├── __init__.py
│           ├── llm_interface.py        # LLM integration interfaces
│           └── openai_llm.py           # OpenAI LLM implementation
├── tests/
│   ├── __init__.py
│   ├── test_document_reader.py         # Document reader tests
│   ├── test_metadata.py                # Metadata model tests
│   ├── test_llm_interface.py           # LLM interface tests
│   └── test_pdf_reader.py              # PDF reader tests
├── dev_tools/
│   ├── debug/                          # Debug utilities and examples
│   └── examples/                       # Example scripts and tests
├── data/
│   ├── output/                         # Analysis results and outputs
│   ├── sample_pdfs/                    # Sample PDF documents
│   └── sample_texts/                   # Sample text documents
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
cd document_summarizer

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install with LLM support (optional)
pip install -r requirements.txt
pip install ".[llm]"  # For OpenAI integration
```

## Usage

### Basic Usage

```python
from document_summarizer.base.document_reader import TextDocumentReader
from document_summarizer.base.pdf_reader import PDFDocumentReader
from document_summarizer.models.metadata import DocumentMetadata

# Create document reader instances
text_reader = TextDocumentReader()
pdf_reader = PDFDocumentReader()

# Extract metadata from a text document
metadata = text_reader.extract_metadata("path/to/document.txt")

# Extract metadata from a PDF document
pdf_metadata = pdf_reader.extract_metadata("path/to/document.pdf")

# Display results
print(f"Document: {metadata.name}")
print(f"Description: {metadata.description}")
print(metadata.to_summary())
```

### Advanced Usage with LLM Integration

```python
from document_summarizer.interfaces.llm_interface import DocumentAnalyzer
from document_summarizer.interfaces.openai_llm import OpenAILLM
from document_summarizer.base.document_reader import TextDocumentReader

# Initialize LLM interface
llm = OpenAILLM(api_key="your-openai-api-key")

# Initialize analyzer with LLM
analyzer = DocumentAnalyzer(llm_interface=llm)
reader = TextDocumentReader()

# Analyze a single document with LLM
result = analyzer.analyze_single_document("document.txt", reader, use_llm=True)

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
pytest --cov=src/document_summarizer --cov-report=html

# Run tests using VS Code tasks
# Use Ctrl+Shift+P -> "Tasks: Run Task" -> "Run Tests"
```

### Run Specific Tests
```bash
# Run tests for a specific module
pytest tests/test_document_reader.py

# Run PDF reader tests
pytest tests/test_pdf_reader.py

# Run LLM interface tests
pytest tests/test_llm_interface.py

# Run a specific test function
pytest tests/test_document_reader.py::TestTextDocumentReader::test_extract_metadata_complete
```

## Development

### Architecture Overview

The project follows a modular, extensible architecture:

- **Base Classes**: `DocumentReader` abstract base class for different document types
- **Document Readers**: `TextDocumentReader` for text files, `PDFDocumentReader` for PDF files
- **Metadata Model**: `DocumentMetadata` with comprehensive entity tracking
- **LLM Integration**: Interface-based design with OpenAI implementation
- **Document Analysis**: `DocumentAnalyzer` for single document analysis and cross-referencing
- **Testing**: Comprehensive test suite covering all functionality

### Adding New Document Types

1. Inherit from `DocumentReader`:
```python
class WordDocumentReader(DocumentReader):
    def __init__(self):
        super().__init__()
        self.supported_extensions = {'.docx', '.doc'}
    
    def read_content(self, file_path: str) -> str:
        # Implement Word document reading logic
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
- [x] PDF document processing
- [x] Entity extraction (organizations, people, dates, documents)
- [x] OpenAI LLM integration
- [x] Document analysis and summarization
- [x] Document cross-referencing
- [x] Complete test suite with extensive coverage

### Planned Features 🚧
- [ ] DOCX document reader implementation
- [ ] Azure OpenAI LLM integration
- [ ] Enhanced NER with spaCy/NLTK
- [ ] Document similarity analysis
- [ ] REST API interface
- [ ] Web interface for document upload and analysis
- [ ] Batch document processing

### Future Enhancements 🔮
- [ ] Support for images and OCR
- [ ] Document classification models
- [ ] Real-time document monitoring
- [ ] Integration with document management systems
- [ ] Advanced relationship mapping between documents