#!/usr/bin/env python3
"""
Script to generate a static file index for GitHub Pages deployment.
This creates a JSON file that lists all available files in the logs directory.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def generate_file_index():
    """Generate a JSON index of all files in the logs directory."""
    
    # Paths to check
    logs_dir = 'logs'
    root_files = ['today_email_summary_report.txt', 'executive_summary.txt']
    
    files = []
    
    # Scan logs directory
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            if filename.endswith('.txt'):
                file_path = os.path.join(logs_dir, filename)
                file_info = get_file_info(file_path, filename)
                if file_info:
                    files.append(file_info)
    
    # Check for root files
    for filename in root_files:
        if os.path.exists(filename):
            file_info = get_file_info(filename, filename)
            if file_info:
                files.append(file_info)
    
    # Sort files by date (newest first)
    files.sort(key=lambda x: x['date'], reverse=True)
    
    # Create the index
    index = {
        'generated_at': datetime.now().isoformat(),
        'total_files': len(files),
        'files': files
    }
    
    # Save to public directory (accessible by GitHub Pages)
    output_file = '../file_index.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated file index: {output_file}")
    print(f"📁 Found {len(files)} files")
    
    # Also save to logs directory for backup
    backup_file = os.path.join(logs_dir, 'file_index.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Backup saved to: {backup_file}")
    
    return index

def get_file_info(file_path, filename):
    """Get information about a file."""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file type based on filename
        file_type = 'summary'
        if 'storytelling' in filename:
            file_type = 'storytelling'
        elif 'executive' in filename:
            file_type = 'executive'
        
        # Extract date from filename (format: YYYYMMDD_*)
        date = 'Unknown'
        import re
        date_match = re.search(r'(\d{8})', filename)
        if date_match:
            date_str = date_match.group(1)
            date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        elif filename in ['today_email_summary_report.txt', 'executive_summary.txt']:
            # Use today's date for current files
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Calculate file size
        file_size = os.path.getsize(file_path)
        size_str = format_file_size(file_size)
        
        # Determine path for display
        display_path = filename
        if date != 'Unknown' and filename not in ['today_email_summary_report.txt', 'executive_summary.txt']:
            display_path = f"logs/{filename}"
        
        return {
            'name': filename,
            'type': file_type,
            'size': size_str,
            'date': date,
            'path': display_path,
            'content': content
        }
        
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def format_file_size(bytes):
    """Format file size in human-readable format."""
    if bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while bytes >= 1024 and i < len(size_names) - 1:
        bytes /= 1024.0
        i += 1
    
    return f"{bytes:.1f} {size_names[i]}"

if __name__ == '__main__':
    generate_file_index()
