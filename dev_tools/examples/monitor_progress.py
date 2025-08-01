#!/usr/bin/env python3
"""
Monitor the LLM batch processing progress
"""
import os
from pathlib import Path
import time

def monitor_progress():
    # Find the most recent CSV file
    output_dir = Path("data/output")
    csv_files = list(output_dir.glob("llm_analysis_batch_*.csv"))
    
    if not csv_files:
        print("No batch CSV files found")
        return
    
    latest_csv = max(csv_files, key=os.path.getctime)
    
    print(f"📊 Monitoring: {latest_csv.name}")
    print("=" * 50)
    
    while True:
        try:
            # Count lines (subtract 1 for header)
            with open(latest_csv, 'r') as f:
                lines = len(f.readlines()) - 1
            
            file_size = latest_csv.stat().st_size
            
            print(f"\r✅ Records: {lines:2d} | Size: {file_size:,} bytes", end="", flush=True)
            
            time.sleep(5)  # Update every 5 seconds
            
        except KeyboardInterrupt:
            print(f"\n\nFinal status:")
            print(f"   Records processed: {lines}")
            print(f"   File: {latest_csv}")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break

if __name__ == "__main__":
    monitor_progress()
