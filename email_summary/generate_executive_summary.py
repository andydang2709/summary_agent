#!/usr/bin/env python3
"""
Script to generate a storytelling email summary for text-to-speech reading.
This script:
1. Reads the existing today_email_summary_report.txt
2. Processes it through Google Gemini API to create a conversational, storytelling summary
3. Saves the summary in a format perfect for text-to-speech apps
4. Creates a natural narrative about your daily emails
"""

import os
import json
from datetime import datetime
from email_llm_processor import EmailLLMProcessor
from dotenv import load_dotenv

def create_executive_summary_prompt(report_content):
    """Create a prompt for generating a storytelling executive summary for text-to-speech."""
    prompt = f"""
You are a personal assistant creating a morning/evening email summary that will be read aloud by a text-to-speech app.

Please read the following email summary report and create a conversational, storytelling summary that:
1. Sounds natural when spoken aloud (like a friend telling you about your emails)
2. Uses conversational language and natural speech patterns
3. Tells a story about what happened in your inbox today
4. Highlights the most important and interesting emails
5. Is engaging and easy to listen to
6. Gives you a complete picture without being overwhelming
7. Uses phrases like "You received", "There was", "You have", etc.
8. Is 2-3 paragraphs maximum for easy listening
9. Highlights the key action items that you need to do today (if any)

The tone should be friendly and conversational, as if someone is personally updating you about your emails over coffee.

Do NOT include any other text in your response.

Here is the email summary report:

{report_content}
"""
    return prompt

def generate_executive_summary(report_file="today_email_summary_report.txt"):
    """Generate an executive summary from the existing report."""
    # Load environment variables
    load_dotenv()
    
    print("🔍 Generating executive summary...")
    
    # Check if report file exists
    if not os.path.exists(report_file):
        print(f"❌ Report file not found: {report_file}")
        return None
    
    # Read the existing report
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        print(f"📖 Read report: {len(report_content)} characters")
        
    except Exception as e:
        print(f"❌ Error reading report: {e}")
        return None
    
    # Create the executive summary prompt
    prompt = create_executive_summary_prompt(report_content)
    
    # Initialize the LLM processor
    try:
        print("🤖 Initializing Google Gemini API...")
        processor = EmailLLMProcessor(provider='google')
        
        # Call the API directly with our custom prompt
        print("🔄 Sending request to Google Gemini...")
        
        # Use the existing API call method but with our custom prompt
        response = processor._call_google_api(prompt)
        
        if response:
            # Extract the summary text from the response
            try:
                # Try to parse as JSON first
                response_data = json.loads(response)
                if 'candidates' in response_data and response_data['candidates']:
                    summary_text = response_data['candidates'][0]['content']['parts'][0]['text']
                else:
                    summary_text = response
            except json.JSONDecodeError:
                # If not JSON, use the response as-is
                summary_text = response
            
            # Clean up the summary text
            summary_text = summary_text.strip()
            
            # Remove any markdown formatting if present
            if summary_text.startswith('```'):
                lines = summary_text.split('\n')
                summary_text = '\n'.join(lines[1:-1])  # Remove first and last lines
            
            return summary_text
        else:
            print("❌ No response from API")
            return None
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return None

def save_executive_summary(summary_text, output_file="executive_summary.txt"):
    """Save the storytelling summary to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Save only the pure storytelling content, no headers or footers
            f.write(summary_text)
        
        print(f"💾 Storytelling summary saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving storytelling summary: {e}")
        return False

def main():
    """Main function to generate storytelling email summary for text-to-speech."""
    print("🎙️ EMAIL STORYTELLING SUMMARY GENERATOR")
    print("=" * 50)
    print("Creating a conversational summary perfect for text-to-speech reading...")
    
    # Generate the storytelling summary
    summary = generate_executive_summary()
    
    if summary:
        print("\n✅ Storytelling summary generated successfully!")
        print("\n📖 STORYTELLING SUMMARY PREVIEW:")
        print("-" * 50)
        print(summary)
        print("-" * 50)
        print("\n💡 This summary is designed to sound natural when read aloud!")
        
        # Save to dated filename in logs folder for daily records
        today = datetime.now().strftime("%Y%m%d")
        logs_dir = "logs"
        os.makedirs(logs_dir, exist_ok=True)
        dated_filename = os.path.join(logs_dir, f"{today}_storytelling_summary.txt")
        
        # Save to dated file
        if save_executive_summary(summary, dated_filename):
            print(f"\n🎉 Storytelling summary saved to: {dated_filename}")
            print(f"📏 Summary length: {len(summary)} characters")
        else:
            print("\n❌ Failed to save storytelling summary")
        
        # Also save to standard filename for current use
        if save_executive_summary(summary, "executive_summary.txt"):
            print(f"📁 Also saved to current file: executive_summary.txt")
        else:
            print("\n❌ Failed to save current storytelling summary")
    else:
        print("\n❌ Failed to generate storytelling summary")

if __name__ == "__main__":
    main()
