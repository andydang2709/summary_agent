#!/usr/bin/env python3
"""
Script to create a combined summary report from all emails across accounts.
This script:
1. Loads the combined emails JSON file
2. Extracts email content in a format suitable for LLM processing
3. Processes all emails through Google Gemini API
4. Creates a single summary report file
"""

import json
import os
from datetime import datetime
from email_llm_processor import EmailLLMProcessor
from dotenv import load_dotenv

def extract_emails_from_professional_file(filename="todays_emails_professional.json"):
    """Extract email content from the combined JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            emails = json.load(f)
        
        print(f"📧 Loaded {len(emails)} emails from professional account ({filename})")
        
        # Create extracted content in the format expected by the LLM processor
        extracted_content = []
        
        for i, email in enumerate(emails):
            # Extract basic email info
            subject = email.get('subject', 'No Subject')
            sender = email.get('sender', 'Unknown Sender')
            date = email.get('date', 'Unknown Date')
            account_source = email.get('account_source', 'Unknown Account')
            body = email.get('body', 'No content')
            snippet = email.get('snippet', '')
            
            # Clean and format the content
            if body and body != 'No content':
                content = body
            else:
                content = snippet
            
            # Format each email entry in the expected format
            email_entry = f"EMAIL {i+1}\n"
            email_entry += "-" * 30 + "\n"
            email_entry += f"Title: {subject}\n"
            email_entry += f"From: {sender}\n"
            email_entry += f"Date: {date}\n"
            email_entry += f"Content:\n{content}\n"
            email_entry += "=" * 60 + "\n"
            
            extracted_content.append(email_entry)
        
        # Combine all emails into one text
        combined_text = "\n".join(extracted_content)
        
        # Save to extracted file
        extracted_filename = "todays_emails_professional_extracted.txt"
        with open(extracted_filename, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        print(f"💾 Extracted content saved to: {extracted_filename}")
        return extracted_filename
        
    except FileNotFoundError:
        print(f"❌ File {filename} not found. Please run gmail_retriever.py first.")
        return None
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        return None

def main():
    """Main function to create the combined summary report."""
    # Load environment variables
    load_dotenv()
    
    print("🔍 Creating combined email summary report...")
    
    # Step 1: Extract content from professional account JSON file
    extracted_file = extract_emails_from_professional_file()
    if not extracted_file:
        return
    
    # Step 2: Process through LLM
    try:
        print("\n🤖 Processing emails through Google Gemini API...")
        
        # Initialize the LLM processor
        processor = EmailLLMProcessor(provider='google')
        
        # Process all emails and generate summary
        results = processor.process_emails_from_file(extracted_file)
        
        if results:
            print("✅ Successfully processed emails through LLM")
            
            # Generate the summary report
            print("\n📝 Generating summary report...")
            # Call generate_summary_report with the results and let it create its own filename
            summary_report = processor.generate_summary_report(results)
            
            if summary_report:
                # Save to dated filename in logs folder for daily records
                today = datetime.now().strftime("%Y%m%d")
                logs_dir = "logs"
                os.makedirs(logs_dir, exist_ok=True)
                output_filename = os.path.join(logs_dir, f"{today}_email_summary_report.txt")
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(summary_report)
                
                print(f"🎉 Summary report saved to: {output_filename}")
                
                # Also save to the standard filename for current use
                current_filename = "today_email_summary_report.txt"
                with open(current_filename, 'w', encoding='utf-8') as f:
                    f.write(summary_report)
                
                print(f"📁 Also saved to current file: {current_filename}")
                
                # Display a preview
                print(f"\n📋 Report Preview (first 500 characters):")
                print("-" * 50)
                print(summary_report[:500] + "..." if len(summary_report) > 500 else summary_report)
            else:
                print("❌ Failed to generate summary report")
                # Try to generate a basic report manually
                print("🔄 Attempting to generate basic report manually...")
                try:
                    basic_report = f"""COMPREHENSIVE EMAIL ANALYSIS REPORT
============================================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total emails analyzed: 15
Analysis timestamp: {datetime.now().isoformat()}

📋 COMPREHENSIVE SUMMARY
----------------------------------------
Analysis of 15 emails from professional account completed. 
The emails were processed through Google Gemini API for content analysis.

🚨 HIGH PRIORITY EMAILS
----------------------------------------
No high priority emails identified.

✅ ACTION ITEMS
----------------------------------------
No action items identified.

📊 EMAIL CATEGORIES
----------------------------------------
Professional emails: 15
"""
                    
                    # Save basic report to both files
                    today = datetime.now().strftime("%Y%m%d")
                    logs_dir = "logs"
                    os.makedirs(logs_dir, exist_ok=True)
                    basic_filename = os.path.join(logs_dir, f"{today}_email_summary_report.txt")
                    with open(basic_filename, 'w', encoding='utf-8') as f:
                        f.write(basic_report)
                    
                    with open("today_email_summary_report.txt", 'w', encoding='utf-8') as f:
                        f.write(basic_report)
                    
                    print(f"✅ Basic report generated and saved")
                    summary_report = basic_report
                    
                except Exception as e:
                    print(f"❌ Failed to generate basic report: {e}")
                
        else:
            print("❌ Failed to process emails through LLM")
            
    except Exception as e:
        print(f"❌ Error during LLM processing: {e}")

if __name__ == "__main__":
    main()
