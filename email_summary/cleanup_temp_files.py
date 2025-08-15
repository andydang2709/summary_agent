#!/usr/bin/env python3
"""
Cleanup script to remove temporary files after report generation.
This script removes intermediate files while preserving the final reports.
"""

import os
import glob
from datetime import datetime

def cleanup_temp_files():
    """Remove temporary files while preserving final reports."""
    print("🧹 CLEANING UP TEMPORARY FILES")
    print("=" * 50)
    
    # Files to preserve (final reports and essential files)
    preserve_patterns = [
        # Final reports
        "today_email_summary_report.txt",
        "executive_summary.txt",
        
        # Essential system files
        "*.py",
        "*.json",
        "*.pickle",
        ".env",
        ".gitignore",
        "README.md",
        "requirements.txt",
        "config.py"
    ]
    
    # Get all files that should be preserved
    preserved_files = set()
    for pattern in preserve_patterns:
        preserved_files.update(glob.glob(pattern))
    
    # Files to remove (temporary/intermediate files)
    temp_patterns = [
        "todays_emails_professional_extracted.txt",
        "email_summary_report_*.txt",
        "__pycache__"
    ]
    
    # Always preserve the logs folder
    print("📁 Preserving logs folder for historical reports...")
    
    removed_count = 0
    removed_files = []
    
    for pattern in temp_patterns:
        files = glob.glob(pattern)
        for file_path in files:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    removed_files.append(file_path)
                    removed_count += 1
                    print(f"🗑️  Removed: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not remove {file_path}: {e}")
            elif os.path.isdir(file_path):
                try:
                    import shutil
                    shutil.rmtree(file_path)
                    removed_files.append(file_path)
                    removed_count += 1
                    print(f"🗑️  Removed directory: {file_path}")
                except Exception as e:
                    print(f"⚠️  Could not remove directory {file_path}: {e}")
    
    if removed_count == 0:
        print("✨ No temporary files found to remove")
    else:
        print(f"\n✅ Cleanup completed: {removed_count} files/directories removed")
    
    # Show what files remain
    print(f"\n📁 Remaining files:")
    remaining_files = [f for f in os.listdir('.') if not f.startswith('.')]
    remaining_files.sort()
    
    for file in remaining_files:
        if os.path.isfile(file):
            size = os.path.getsize(file)
            print(f"  📄 {file} ({size:,} bytes)")
        else:
            print(f"  📁 {file}/")
    
    return removed_files

def main():
    """Main cleanup function."""
    try:
        removed = cleanup_temp_files()
        
        if removed:
            print(f"\n🎉 Cleanup successful! Removed {len(removed)} temporary files.")
        else:
            print(f"\n✨ No cleanup needed - all files are already organized.")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    main()
