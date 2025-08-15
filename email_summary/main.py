#!/usr/bin/env python3
"""
Main script to run the complete email summary workflow.
This script:
1. Retrieves today's emails from both spam and professional accounts
2. Creates a combined summary report
3. Displays the final report
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle any errors."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout)
        if e.stderr:
            print("STDERR:")
            print(e.stderr)
        return False

def check_file_exists(filename, description):
    """Check if a required file exists."""
    if os.path.exists(filename):
        print(f"✅ {description}: {filename}")
        return True
    else:
        print(f"❌ {description} not found: {filename}")
        return False

def display_report(filename):
    """Display the final summary report."""
    print(f"\n{'='*60}")
    print(f"📋 FINAL EMAIL SUMMARY REPORT")
    print(f"{'='*60}")
    
    if not os.path.exists(filename):
        print(f"❌ Report file not found: {filename}")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(content)
        
        # Show file info
        file_size = os.path.getsize(filename)
        file_time = datetime.fromtimestamp(os.path.getmtime(filename))
        print(f"\n📁 File: {filename}")
        print(f"📏 Size: {file_size:,} bytes")
        print(f"🕒 Generated: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error reading report: {e}")

def main():
    """Main function to run the complete workflow."""
    print("🚀 EMAIL SUMMARY AGENT - COMPLETE WORKFLOW")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check required files
    print("\n🔍 Checking required files...")
    required_files = [
        ('gmail_retriever.py', 'Gmail retriever script'),
        ('create_combined_summary.py', 'Combined summary script'),
        ('email_llm_processor.py', 'LLM processor'),
        ('.env', 'Environment variables file'),
        ('professional_credentials.json', 'Professional account credentials')
    ]
    
    missing_files = []
    for filename, description in required_files:
        if not check_file_exists(filename, description):
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all required files are present before running.")
        return
    
    print("\n✅ All required files found!")
    
    # Step 1: Retrieve emails from professional account
    print("\n" + "="*60)
    print("📥 STEP 1: RETRIEVING EMAILS FROM PROFESSIONAL ACCOUNT")
    print("="*60)
    
    if not run_command("python gmail_retriever.py", "Retrieving emails from professional account"):
        print("❌ Failed to retrieve emails. Stopping workflow.")
        return
    
    # Check if professional emails file was created
    if not check_file_exists("todays_emails_professional.json", "Professional emails file"):
        print("❌ Professional emails file not created. Stopping workflow.")
        return
    
    # Step 2: Create combined summary report
    print("\n" + "="*60)
    print("🤖 STEP 2: CREATING COMBINED SUMMARY REPORT")
    print("="*60)
    
    if not run_command("python create_combined_summary.py", "Creating combined summary report"):
        print("❌ Failed to create summary report. Stopping workflow.")
        return
    
    # Check if final report was created
    final_report = "today_email_summary_report.txt"
    if not check_file_exists(final_report, "Final summary report"):
        print("❌ Final summary report not created. Stopping workflow.")
        return
    
    # Step 3: Display the final report
    print("\n" + "="*60)
    print("🎯 STEP 3: DISPLAYING FINAL REPORT")
    print("="*60)
    
    display_report(final_report)
    
    # Step 4: Generate storytelling summary for text-to-speech
    print("\n" + "="*60)
    print("🎙️ STEP 4: GENERATING STORYTELLING SUMMARY")
    print("="*60)
    
    if not run_command("python generate_executive_summary.py", "Generating storytelling summary for text-to-speech"):
        print("⚠️ Failed to generate storytelling summary, but workflow continues...")
    
    # Check if storytelling summary was created
    executive_summary_file = "executive_summary.txt"
    if check_file_exists(executive_summary_file, "Storytelling summary"):
        print(f"\n📖 STORYTELLING SUMMARY PREVIEW:")
        print("-" * 50)
        try:
            with open(executive_summary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Show just the summary content, not the header
                lines = content.split('\n')
                summary_start = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('=') and not line.startswith('Generated:') and not line.startswith('📧') and not line.startswith('💡'):
                        summary_start = i
                        break
                summary_content = '\n'.join(lines[summary_start:])
                print(summary_content[:500] + "..." if len(summary_content) > 500 else summary_content)
        except Exception as e:
            print(f"❌ Error reading storytelling summary: {e}")
    
    # Step 5: Cleanup temporary files
    print("\n" + "="*60)
    print("🧹 STEP 5: CLEANING UP TEMPORARY FILES")
    print("="*60)
    
    if not run_command("python cleanup_temp_files.py", "Cleaning up temporary files"):
        print("⚠️ Failed to cleanup temporary files, but workflow continues...")
    
    # Workflow completion
    print(f"\n{'='*60}")
    print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Final report: {final_report}")
    print(f"Storytelling summary: {executive_summary_file}")
    print("\n💡 You can now:")
    print("  • View the detailed report in the file above")
    print("  • Listen to the storytelling summary via text-to-speech")
    print("  • Check the dated files for daily records")
    print("  • Run this script again to get fresh emails")
    print("  • Modify the scripts to customize the analysis")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Workflow interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
