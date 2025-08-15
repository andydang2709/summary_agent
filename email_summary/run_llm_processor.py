#!/usr/bin/env python3
"""
Simple runner for Email LLM Processor
Automatically uses Google Gemini API with environment variable.
"""

import os
from email_llm_processor import EmailLLMProcessor

def main():
    """Run the LLM processor automatically with Google Gemini."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables!")
        print("💡 Make sure your .env file contains: GOOGLE_API_KEY=your-key-here")
        return
    
    print(f"🔑 Using Google Gemini API key: {api_key[:10]}...")
    print("📊 Rate Limits: 15 requests/min, 250K tokens/min, 1000 requests/day")
    
    # Initialize processor
    processor = EmailLLMProcessor(api_key=api_key, provider='google')
    
    # Find extracted email files
    extracted_files = [f for f in os.listdir('.') if f.endswith('_extracted.txt')]
    
    if not extracted_files:
        print("❌ No extracted email files found!")
        print("💡 First run the email extractor to create _extracted.txt files.")
        return
    
    print(f"📁 Found {len(extracted_files)} extracted email files:")
    for file in extracted_files:
        print(f"  - {file}")
    
    # Process each file
    for extracted_file in extracted_files:
        print(f"\n🔄 Processing: {extracted_file}")
        
        # Generate output filenames
        base_name = extracted_file.replace('_extracted.txt', '')
        output_file = f"{base_name}_llm_processed.json"
        report_file = f"{base_name}_summary_report.txt"
        
        # Process emails
        processed_emails = processor.process_emails_from_file(extracted_file, output_file)
        
        if processed_emails:
            # Generate summary report
            processor.generate_summary_report(processed_emails, report_file)
            print(f"✅ Successfully processed {processed_emails.get('total_emails', 0)} emails in batch")
            print(f"   - Results: {output_file}")
            print(f"   - Report: {report_file}")
            
            # Show analysis highlights
            high_priority_count = len(processed_emails.get('high_priority_emails', []))
            action_items_count = len(processed_emails.get('action_items', []))
            print(f"   - High priority emails: {high_priority_count}")
            print(f"   - Action items: {action_items_count}")
            
            # Show current usage status
            usage_status = processor.get_usage_status()
            print(f"\n📊 Current API Usage Status:")
            print(f"   - Requests this minute: {usage_status['requests_this_minute']}/{usage_status['requests_per_minute_limit']}")
            print(f"   - Tokens this minute: {usage_status['tokens_this_minute']}/{usage_status['tokens_per_minute_limit']}")
            print(f"   - Requests today: {usage_status['requests_today']}/{usage_status['requests_per_day_limit']}")
            print(f"   - Time until minute reset: {usage_status['time_until_minute_reset']:.1f} seconds")
        else:
            print(f"⚠️ No emails processed from {extracted_file}")
    
    print(f"\n🎉 All processing complete!")

if __name__ == '__main__':
    main()
