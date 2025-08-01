# Data Directory

This directory contains sample documents and output files for the Document Analyzer project.

## Directory Structure

```
data/
├── sample_pdfs/     # Sample PDF documents for testing
├── sample_texts/    # Sample text documents for testing  
├── output/          # Generated analysis results and reports
└── README.md        # This file
```

## Usage

### Sample Documents
- Place your PDF files in `sample_pdfs/`
- Place text files (.txt, .md, etc.) in `sample_texts/`
- These files are used for testing and demonstrating the document analyzer

### Output Files
- Generated metadata files (JSON, CSV)
- Analysis reports
- Extracted content files

## File Naming Conventions

For consistency, please follow these naming conventions:

### Sample Files
- `sample_contract.pdf` - Legal contracts
- `sample_report.pdf` - Technical reports
- `sample_invoice.pdf` - Business invoices
- `sample_meeting_minutes.txt` - Meeting records

### Output Files
- `{document_name}_metadata.json` - Extracted metadata
- `{document_name}_analysis.txt` - Analysis summary
- `batch_analysis_{timestamp}.csv` - Batch processing results

## Git Tracking

Note: The actual document files are excluded from git tracking via `.gitignore` to:
- Avoid committing potentially sensitive documents
- Keep the repository size manageable
- Prevent copyright issues

Only the directory structure and this README are tracked in version control.
