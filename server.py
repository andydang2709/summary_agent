#!/usr/bin/env python3
"""
Custom HTTP server for the Email Summary Dashboard.
This server scans the email_summary/logs directory and serves real files.
"""

import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes
from datetime import datetime

class EmailSummaryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Handle the scan-logs endpoint
        if path == '/scan-logs':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            try:
                files = self.scan_logs_directory()
                self.wfile.write(json.dumps(files, indent=2).encode())
            except Exception as e:
                error_response = {'error': str(e), 'files': []}
                self.wfile.write(json.dumps(error_response, indent=2).encode())
            return
        
        # Handle regular file requests
        super().do_GET()
    
    def scan_logs_directory(self):
        """Scan the email_summary/logs directory for .txt files."""
        files = []
        
        # Check if the logs directory exists
        logs_dir = 'email_summary/logs'
        if not os.path.exists(logs_dir):
            # Try alternative paths
            alt_paths = ['logs', '../logs', '../../logs']
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    logs_dir = alt_path
                    break
            else:
                raise Exception(f"Logs directory not found. Tried: {['email_summary/logs'] + alt_paths}")
        
        # Scan for .txt files in the logs directory
        try:
            for filename in os.listdir(logs_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(logs_dir, filename)
                    file_info = self.get_file_info(file_path, filename)
                    files.append(file_info)
        except Exception as e:
            print(f"Error scanning logs directory: {e}")
        
        # Also check for current files in the root directory
        current_files = ['today_email_summary_report.txt', 'executive_summary.txt']
        for filename in current_files:
            if os.path.exists(filename):
                file_info = self.get_file_info(filename, filename)
                files.append(file_info)
        
        # Sort files by date (newest first)
        files.sort(key=lambda x: x['date'], reverse=True)
        
        return files
    
    def get_file_info(self, file_path, filename):
        """Get information about a file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine file type based on filename
            file_type = 'summary'
            if 'storytelling' in filename or 'executive' in filename:
                file_type = 'storytelling'
            
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
            size_str = self.format_file_size(file_size)
            
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
            return {
                'name': filename,
                'type': 'unknown',
                'size': '0 B',
                'date': 'Unknown',
                'path': filename,
                'content': f"Error reading file: {str(e)}"
            }
    
    def format_file_size(self, bytes):
        """Format file size in human-readable format."""
        if bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while bytes >= 1024 and i < len(size_names) - 1:
            bytes /= 1024.0
            i += 1
        
        return f"{bytes:.1f} {size_names[i]}"
    
    def end_headers(self):
        """Add CORS headers."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, EmailSummaryHandler)
    
    print(f"🚀 Email Summary Dashboard Server")
    print(f"📍 Serving on http://localhost:{port}")
    print(f"📁 Scanning directory: email_summary/logs")
    print(f"🔄 Press Ctrl+C to stop the server")
    print(f"{'='*50}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Server stopped by user")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
