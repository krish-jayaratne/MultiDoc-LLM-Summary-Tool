#!/usr/bin/env python3
"""
OpenAI LLM Example - Real Document Analysis

This example demonstrates how to use the OpenAI LLM integration to analyze a PDF document
and extract structured information using GPT-4o.

Prerequisites:
1. Set your OpenAI API key: export OPENAI_KEY="your-api-key-here"
2. Install dependencies: pip install -r requirements.txt
3. Ensure you have a PDF file to analyze

The simplified LLM architecture means you get all the information you need from a single
API call to analyze_document(), which returns:
- Document classification (type, category)
- Summary (concise overview)
- Entity extraction (people, organizations, dates, locations, etc.)
- Key information and financial amounts
- Referenced documents and properties

This replaces the old approach of making separate API calls for extraction, summarization,
and classification - saving both time and API costs!
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime

from src.document_summarizer.interfaces.openai_llm import OpenAILLM
from src.document_summarizer.interfaces.llm_interface import DocumentAnalyzer
from src.document_summarizer.base.pdf_reader import PDFDocumentReader


def create_master_csv_file():
    """Create a unique master CSV file for all analysis results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("data/output")
    output_dir.mkdir(exist_ok=True)
    
    csv_file = output_dir / f"llm_analysis_batch_{timestamp}.csv"
    return csv_file


def append_to_csv(llm_data, metadata, csv_file, write_header=False):
    """Append analysis results to the master CSV file."""
    
    # Prepare CSV row data
    csv_row = {
        'filename': metadata.name,
        'file_path': metadata.file_path,
        'file_type': metadata.file_type,
        'file_size_kb': round((metadata.file_size or 0) / 1024, 2) if metadata.file_size else 0,
        'document_type': llm_data.get('document_type', ''),
        'document_date': llm_data.get('document_date', ''),
        'summary': llm_data.get('summary', ''),
        'organizations': ', '.join(llm_data.get('organizations', [])),
        'people': ', '.join(llm_data.get('people', [])),
        'dates': ', '.join(llm_data.get('dates', [])),
        'locations': ', '.join(llm_data.get('locations', [])),
        'referenced_documents': ', '.join(llm_data.get('referenced_documents', [])),
        'properties': ', '.join(llm_data.get('properties', [])),
        'financial_amounts': ', '.join(llm_data.get('financial_amounts', [])),
        'key_information': ', '.join(llm_data.get('key_information', [])),
        'content_length': len(metadata.content) if hasattr(metadata, 'content') and metadata.content else 0,
        'analysis_model': llm_data.get('llm_model', ''),
        'analysis_timestamp': str(llm_data.get('analysis_timestamp', ''))
    }
    
    # Write to CSV with | delimiter
    mode = 'w' if write_header else 'a'
    with open(csv_file, mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = csv_row.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
        
        if write_header:
            writer.writeheader()
        writer.writerow(csv_row)


def analyze_pdf_with_openai():
    """Analyze a PDF document using OpenAI GPT-4o."""
    
    print("🤖 OpenAI Document Analysis Example")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        print("❌ Error: OPENAI_KEY environment variable not set")
        print("   Please set it with: export OPENAI_KEY='your-api-key-here'")
        return
    
    print(f"✅ OpenAI API key found (ending in ...{api_key[-4:]})")
    
    # Initialize the LLM and analyzer
    try:
        llm = OpenAILLM(model="gpt-4o", api_key=api_key)
        analyzer = DocumentAnalyzer(llm_interface=llm)
        pdf_reader = PDFDocumentReader()
        
        print(f"✅ Initialized OpenAI LLM with model: {llm.model}")
        
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI LLM: {e}")
        return
    
    # Find all PDFs to analyze
    sample_dir = Path("data/sample_pdfs")
    
    if not sample_dir.exists():
        print(f"❌ Sample directory not found: {sample_dir}")
        print("   Please create the directory and add PDF files")
        return
    
    pdf_files = list(sample_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in: {sample_dir}")
        print("   Please add PDF files to the data/sample_pdfs/ directory")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF file(s):")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file.name}")
    
    # Process each PDF file
    all_results = []
    
    # Create master CSV file for all results
    master_csv_file = create_master_csv_file()
    csv_header_written = False
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 Analyzing PDF {i}/{len(pdf_files)}: {pdf_file.name}")
        print("-" * 50)
    
        try:
            # Perform the analysis
            print("🔍 Reading PDF content...")
            result = analyzer.analyze_single_document(
                str(pdf_file), 
                pdf_reader, 
                use_llm=True
            )
            
            # Store result for summary
            all_results.append({
                'file': pdf_file,
                'result': result
            })
            
            # Display basic metadata
            metadata = result['basic_metadata']
            print(f"\n📊 BASIC METADATA")
            print(f"   File: {metadata.name}")
            print(f"   Size: {metadata.file_size:,} bytes" if metadata.file_size else "   Size: Unknown")
            print(f"   Type: {metadata.file_type}")
            print(f"   Modified: {metadata.modified_date}")
            
            # Display LLM analysis results
            if 'llm_analysis' in result:
                llm_data = result['llm_analysis']
                
                print(f"\n🤖 AI ANALYSIS RESULTS")
                print(f"   Model: {llm_data.get('llm_model', 'Unknown')}")
                print(f"   Document Type: {llm_data.get('document_type', 'Unknown')}")
                
                # Summary
                summary = llm_data.get('summary', 'No summary available')
                print(f"\n📝 SUMMARY")
                print(f"   {summary}")
                
                # Entities (condensed view for multiple files)
                people = llm_data.get('people', [])
                orgs = llm_data.get('organizations', [])
                dates = llm_data.get('dates', [])
                locations = llm_data.get('locations', [])
                financial_amounts = llm_data.get('financial_amounts', [])
                
                print(f"\n🔍 EXTRACTED ENTITIES")
                print(f"   👥 People ({len(people)}): {', '.join(people[:3])}" + ("..." if len(people) > 3 else ""))
                print(f"   🏢 Organizations ({len(orgs)}): {', '.join(orgs[:2])}" + ("..." if len(orgs) > 2 else ""))
                print(f"   📅 Dates ({len(dates)}): {', '.join(dates)}")
                print(f"   💰 Financial ({len(financial_amounts)}): {', '.join(financial_amounts[:2])}" + ("..." if len(financial_amounts) > 2 else ""))
                
                # Save detailed results to JSON and CSV
                output_dir = Path("data/output")
                output_dir.mkdir(exist_ok=True)
                
                output_file = output_dir / f"{pdf_file.stem}_llm_analysis.json"
                
                # Create a clean output structure
                output_data = {
                    "file_info": {
                        "filename": metadata.name,
                        "file_path": metadata.file_path,
                        "file_size": metadata.file_size,
                        "file_type": metadata.file_type,
                        "analysis_date": str(metadata.analysis_timestamp)
                    },
                    "llm_analysis": llm_data,
                    "content_preview": result.get('content_preview', '')[:500] + "..." if len(result.get('content_preview', '')) > 500 else result.get('content_preview', '')
                }
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, default=str)
                
                # Append to master CSV file
                append_to_csv(llm_data, metadata, master_csv_file, write_header=not csv_header_written)
                csv_header_written = True
                
                print(f"\n💾 SAVED RESULTS")
                print(f"   JSON: {output_file.name}")
                print(f"   CSV: Added to {master_csv_file.name}")
                
            else:
                print("❌ No LLM analysis results found")
                
        except Exception as e:
            print(f"❌ Analysis failed for {pdf_file.name}: {e}")
            continue
    
    # Display overall summary
    if all_results:
        print(f"\n🎯 OVERALL SUMMARY")
        print("=" * 50)
        print(f"📊 Total files processed: {len(all_results)}")
        
        # Aggregate statistics
        all_people = set()
        all_orgs = set()
        all_doc_types = []
        total_financial = 0
        
        for item in all_results:
            result = item['result']
            if 'llm_analysis' in result:
                llm_data = result['llm_analysis']
                all_people.update(llm_data.get('people', []))
                all_orgs.update(llm_data.get('organizations', []))
                all_doc_types.append(llm_data.get('document_type', 'unknown'))
                total_financial += len(llm_data.get('financial_amounts', []))
        
        print(f"👥 Unique people mentioned: {len(all_people)}")
        print(f"🏢 Unique organizations: {len(all_orgs)}")
        print(f"💰 Total financial amounts found: {total_financial}")
        
        # Document types
        from collections import Counter
        doc_type_counts = Counter(all_doc_types)
        print(f"\n📄 Document types:")
        for doc_type, count in doc_type_counts.most_common():
            print(f"   • {doc_type}: {count}")
        
        # Most common organizations
        if all_orgs:
            print(f"\n🏢 Organizations found:")
            for org in sorted(all_orgs)[:5]:  # Show first 5
                print(f"   • {org}")
            if len(all_orgs) > 5:
                print(f"   ... and {len(all_orgs) - 5} more")
        
        # Master CSV file info
        if csv_header_written:
            print(f"\n📊 MASTER CSV FILE")
            print(f"   File: {master_csv_file}")
            print(f"   Size: {master_csv_file.stat().st_size:,} bytes")
            print(f"   Records: {len(all_results)}")
            print(f"   Delimiter: | (pipe)")
        
        # Clear PDF cache to free memory
        pdf_reader.clear_cache()
        print(f"   Cache cleared to free memory")
    
    else:
        print(f"\n❌ No files were successfully processed")


def demonstrate_csv_export():
    """Demonstrate CSV export functionality for multiple PDFs."""
    
    print(f"\n📊 BULK CSV EXPORT EXAMPLE")
    print("=" * 50)
    
    api_key = os.getenv('OPENAI_KEY')
    if not api_key:
        print("❌ API key not available for CSV export demo")
        return
    
    try:
        llm = OpenAILLM(api_key=api_key)
        pdf_reader = PDFDocumentReader()
        
        # Find all PDFs in the sample directory
        sample_dir = Path("data/sample_pdfs")
        pdf_files = list(sample_dir.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ No PDF files found for CSV export demo")
            return
        
        print(f"📁 Found {len(pdf_files)} PDF file(s) for bulk analysis")
        
        # Analyze all documents
        documents = []
        for pdf_file in pdf_files:
            try:
                content = pdf_reader.read_content(str(pdf_file))
                metadata = pdf_reader.extract_metadata(str(pdf_file))
                metadata.content = content  # Add content for LLM analysis
                documents.append(metadata)
                print(f"   ✅ Prepared: {pdf_file.name}")
            except Exception as e:
                print(f"   ❌ Failed to prepare {pdf_file.name}: {e}")
        
        if documents:
            print(f"\n🤖 Analyzing {len(documents)} document(s) with OpenAI for CSV export...")
            csv_data = llm.analyze_documents_for_csv(documents)
            
            # Save to CSV with | delimiter and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = Path(f"data/output/bulk_llm_analysis_{timestamp}.csv")
            
            if csv_data:
                with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = csv_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|')
                    
                    writer.writeheader()
                    for row in csv_data:
                        writer.writerow(row)
                
                print(f"✅ Bulk CSV export completed: {output_file}")
                print(f"   Analyzed {len(csv_data)} document(s)")
                print(f"   File size: {output_file.stat().st_size:,} bytes")
                print(f"   Delimiter: | (pipe) - allows commas within fields")
                
                # Show a sample of the data
                print(f"\n📋 CSV SAMPLE (first row):")
                successful_rows = [row for row in csv_data if row.get('analysis_status') == 'Success']
                if successful_rows:
                    sample = successful_rows[0]
                    print(f"   File: {sample['filename']}")
                    print(f"   Type: {sample['document_type']}")
                    print(f"   Organizations: {sample['organizations']}")
                    print(f"   People: {sample['people']}")
            else:
                print("❌ No data generated for CSV export")
        
    except Exception as e:
        print(f"❌ CSV export failed: {e}")


if __name__ == "__main__":
    # Run the main analysis
    analyze_pdf_with_openai()
    
    # Demonstrate CSV export (optional - uncomment to try bulk analysis)
    # Note: This will use additional API calls
    # demonstrate_csv_export()
    
    print(f"\n✨ EXAMPLE COMPLETE")
    print("=" * 50)
    print("💡 Tips:")
    print("   • Check the data/output/ directory for saved JSON and CSV results")
    print("   • CSV files use | (pipe) delimiter - allows commas within fields")
    print("   • Uncomment demonstrate_csv_export() to try bulk analysis")
    print("   • The analyze_document() method combines entity extraction,")
    print("     summarization, and classification in a single efficient API call")
    print("   • All extracted data is structured and ready for further processing")
    print("   • Import CSV with pipe delimiter: pandas.read_csv('file.csv', sep='|')")
