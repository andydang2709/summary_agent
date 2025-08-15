#!/usr/bin/env python3
"""
Email LLM Processor
Processes extracted email content through LLM APIs to parse and summarize emails.
"""

import json
import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
from datetime import datetime

class EmailLLMProcessor:
    """Process emails through LLM APIs for summarization and analysis"""
    
    def __init__(self, api_key: str = None, provider: str = "openai"):
        """
        Initialize the LLM processor.
        
        Args:
            api_key: API key for the LLM service
            provider: LLM provider ('openai', 'anthropic', 'google', 'local')
        """
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.provider = provider.lower()
        self.base_urls = {
            'openai': 'https://api.openai.com/v1/chat/completions',
            'anthropic': 'https://api.anthropic.com/v1/messages',
            'google': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent'
        }
        
        # Rate limiting for Gemini 2.0 Flash Lite
        self.rate_limits = {
            'google': {
                'requests_per_minute': 15,
                'tokens_per_minute': 250000,
                'requests_per_day': 1000,
                'min_delay_between_requests': 4.0  # 60 seconds / 15 requests = 4 seconds
            }
        }
        
        # Track usage
        self.usage_tracker = {
            'requests_this_minute': 0,
            'tokens_this_minute': 0,
            'requests_today': 0,
            'last_request_time': 0,
            'minute_start_time': time.time()
        }
        
        if not self.api_key:
            print(f"⚠️ No API key found. Set {provider.upper()}_API_KEY environment variable or pass api_key parameter.")
    
    def process_emails_from_file(self, extracted_file: str, output_file: str = None) -> List[Dict[str, Any]]:
        """
        Process all emails from a file at once through the LLM for comprehensive analysis.
        
        Args:
            extracted_file: Path to the extracted email text file
            output_file: Output file for processed results
            
        Returns:
            Comprehensive analysis of all emails
        """
        if not self.api_key:
            print("❌ API key required to process emails")
            return []
        
        # Parse the extracted file
        emails = self._parse_extracted_file(extracted_file)
        if not emails:
            print(f"❌ No emails found in {extracted_file}")
            return []
        
        print(f"📧 Processing {len(emails)} emails through {self.provider.upper()} in batch...")
        
        try:
            # Process all emails at once
            comprehensive_analysis = self._process_all_emails_batch(emails)
            
            # Save results
            if output_file:
                self._save_results(comprehensive_analysis, output_file)
            
            return comprehensive_analysis
                
        except Exception as e:
            print(f"⚠️ Error processing emails in batch: {e}")
            return []
    
    def _process_all_emails_batch(self, emails: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process all emails at once for comprehensive analysis."""
        
        # Create a comprehensive prompt for all emails
        batch_prompt = self._create_batch_analysis_prompt(emails)
        
        print(f"🔄 Sending batch request to {self.provider.upper()}...")
        
        # Send to LLM
        response = self._call_llm_api(batch_prompt)
        
        # Parse response
        parsed_response = self._parse_batch_response(response)
        
        return {
            'total_emails': len(emails),
            'analysis_timestamp': datetime.now().isoformat(),
            'comprehensive_summary': parsed_response.get('comprehensive_summary', 'No summary generated'),
            'high_priority_emails': parsed_response.get('high_priority_emails', []),
            'action_items': parsed_response.get('action_items', []),
            'email_categories': parsed_response.get('email_categories', {}),
            'processing_notes': parsed_response.get('processing_notes', ''),
            'raw_emails': emails  # Keep original email data for reference
        }
    
    def _create_batch_analysis_prompt(self, emails: List[Dict[str, str]]) -> str:
        """Create a comprehensive prompt for analyzing all emails at once."""
        
        # Prepare email summaries for the prompt
        email_summaries = []
        for i, email in enumerate(emails, 1):
            email_summary = f"""
Email {i}:
- Subject: {email['title']}
- From: {email['sender']}
- Date: {email['date']}
- Content: {email['text'][:500]}..."""  # Limit content length
            email_summaries.append(email_summary)
        
        all_emails_text = "\n".join(email_summaries)
        
        prompt = f"""
Please analyze the following {len(emails)} emails and provide a comprehensive summary. Focus on identifying high-priority emails and actionable items.

{all_emails_text}

IMPORTANT: Respond with ONLY valid JSON. Do not include any markdown formatting, code blocks, or additional text.

{{
    "comprehensive_summary": "A 3-4 paragraph summary of all emails received, highlighting main themes and patterns",
    "high_priority_emails": [
        {{
            "email_number": 1,
            "subject": "Email subject",
            "sender": "Sender email",
            "priority_level": "high/medium",
            "reason_for_priority": "Why this email is important",
            "key_points": ["Point 1", "Point 2", "Point 3"]
        }}
    ],
    "action_items": [
        {{
            "action": "What needs to be done",
            "priority": "high/medium/low",
            "deadline": "When it needs to be done (if mentioned)",
            "source_email": "Which email this action item came from"
        }}
    ],
    "email_categories": {{
        "work": 0,
        "personal": 0, 
        "marketing": 0,
        "notifications": 0,
        "other": 0
    }},
    "processing_notes": "Any additional insights or observations about the email batch"
}}

Focus on:
1. Identifying truly important emails that require immediate attention
2. Extracting all actionable items and tasks
3. Categorizing emails by type
4. Providing a comprehensive overview of the email batch
5. Highlighting urgent matters and deadlines

Remember: Return ONLY the JSON object, no additional formatting or text.
"""
        
        return prompt
    
    def _parse_batch_response(self, response: str) -> Dict[str, Any]:
        """Parse the batch LLM response to extract structured data."""
        try:
            # Remove markdown code blocks if present
            if '```json' in response:
                response = response.replace('```json', '').replace('```', '')
            
            # Try to extract JSON from the response
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                
                # Clean up the JSON string
                json_str = json_str.strip()
                
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback parsing
                return {
                    'comprehensive_summary': response[:500] + '...' if len(response) > 500 else response,
                    'high_priority_emails': [],
                    'action_items': [],
                    'email_categories': {},
                    'processing_notes': 'Response parsing failed'
                }
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing batch LLM response: {e}")
            print(f"Response preview: {response[:200]}...")
            
            # Try to extract just the summary from the response
            summary = response
            if 'comprehensive_summary' in response:
                try:
                    # Look for the summary content
                    summary_start = response.find('"comprehensive_summary"')
                    if summary_start != -1:
                        # Find the colon after the key
                        colon_pos = response.find(':', summary_start)
                        if colon_pos != -1:
                            # Find the first quote after the colon
                            quote_start = response.find('"', colon_pos)
                            if quote_start != -1:
                                # Find the next quote to get the full value
                                quote_end = response.find('"', quote_start + 1)
                                if quote_end != -1:
                                    summary = response[quote_start + 1:quote_end]
                                    if summary.strip():
                                        return {
                                            'comprehensive_summary': summary,
                                            'high_priority_emails': [],
                                            'action_items': [],
                                            'email_categories': {},
                                            'processing_notes': f'JSON parsing error: {e}. Using extracted summary instead.'
                                        }
                except Exception as extract_error:
                    print(f"Summary extraction failed: {extract_error}")
            
            # If we couldn't extract the summary, use the first part of the response
            if len(response) > 200:
                summary = response[:200] + "..."
            else:
                summary = response
            
            return {
                'comprehensive_summary': summary[:1000] + '...' if len(summary) > 1000 else summary,
                'high_priority_emails': [],
                'action_items': [],
                'email_categories': {},
                'processing_notes': f'JSON parsing error: {e}. Using extracted summary instead.'
            }
    
    def _parse_extracted_file(self, file_path: str) -> List[Dict[str, str]]:
        """Parse the extracted email text file."""
        emails = []
        current_email = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by email sections
            email_sections = content.split('EMAIL ')[1:]  # Skip the header
            
            for section in email_sections:
                if not section.strip():
                    continue
                    
                current_email = {}
                
                # Extract title
                title_match = section.split('Title: ')[1].split('\n')[0] if 'Title: ' in section else 'No Subject'
                current_email['title'] = title_match.strip()
                
                # Extract sender
                sender_match = section.split('From: ')[1].split('\n')[0] if 'From: ' in section else 'Unknown Sender'
                current_email['sender'] = sender_match.strip()
                
                # Extract date
                date_match = section.split('Date: ')[1].split('\n')[0] if 'Date: ' in section else 'Unknown Date'
                current_email['date'] = date_match.strip()
                
                # Extract content
                if 'Content:' in section:
                    content_start = section.find('Content:') + 8
                    content_end = section.find('==================================================')
                    if content_end == -1:
                        content_end = len(section)
                    
                    content_text = section[content_start:content_end].strip()
                    current_email['text'] = content_text
                else:
                    current_email['text'] = 'No content available'
                
                if current_email['title'] and current_email['text']:
                    emails.append(current_email)
            
        except Exception as e:
            print(f"❌ Error parsing file {file_path}: {e}")
            import traceback
            traceback.print_exc()
        
        return emails
    
    # Removed individual email processing methods - now using batch processing
    
    def _call_llm_api(self, prompt: str) -> str:
        """Call the appropriate LLM API based on provider."""
        
        if self.provider == 'openai':
            return self._call_openai_api(prompt)
        elif self.provider == 'anthropic':
            return self._call_anthropic_api(prompt)
        elif self.provider == 'google':
            return self._call_google_api(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API."""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'system', 'content': 'You are an email analysis assistant. Always respond with valid JSON.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 500
        }
        
        response = requests.post(self.base_urls['openai'], headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']
    
    def _call_anthropic_api(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 500,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        response = requests.post(self.base_urls['anthropic'], headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()['content'][0]['text']
    
    def _call_google_api(self, prompt: str) -> str:
        """Call Google Gemini API with rate limiting."""
        # Check rate limits before making request
        self._check_rate_limits()
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(prompt) // 4
        
        params = {'key': self.api_key}
        
        data = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'temperature': 0.3,
                'maxOutputTokens': 500
            }
        }
        
        response = requests.post(self.base_urls['google'], params=params, json=data)
        response.raise_for_status()
        
        # Update usage tracker
        self._update_usage_tracker(estimated_tokens)
        
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    
    def _check_rate_limits(self):
        """Check and enforce rate limits."""
        current_time = time.time()
        limits = self.rate_limits['google']
        
        # Reset minute counter if a minute has passed
        if current_time - self.usage_tracker['minute_start_time'] >= 60:
            self.usage_tracker['requests_this_minute'] = 0
            self.usage_tracker['tokens_this_minute'] = 0
            self.usage_tracker['minute_start_time'] = current_time
        
        # Check daily limit
        if self.usage_tracker['requests_today'] >= limits['requests_per_day']:
            raise Exception("Daily request limit (1000) exceeded. Please try again tomorrow.")
        
        # Check minute limits
        if self.usage_tracker['requests_this_minute'] >= limits['requests_per_minute']:
            wait_time = 60 - (current_time - self.usage_tracker['minute_start_time'])
            if wait_time > 0:
                print(f"⏳ Rate limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.usage_tracker['requests_this_minute'] = 0
                self.usage_tracker['tokens_this_minute'] = 0
                self.usage_tracker['minute_start_time'] = time.time()
        
        if self.usage_tracker['tokens_this_minute'] >= limits['tokens_per_minute']:
            wait_time = 60 - (current_time - self.usage_tracker['minute_start_time'])
            if wait_time > 0:
                print(f"⏳ Token limit reached. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                self.usage_tracker['tokens_this_minute'] = 0
                self.usage_tracker['minute_start_time'] = time.time()
        
        # Enforce minimum delay between requests
        time_since_last = current_time - self.usage_tracker['last_request_time']
        if time_since_last < limits['min_delay_between_requests']:
            wait_time = limits['min_delay_between_requests'] - time_since_last
            print(f"⏳ Waiting {wait_time:.1f} seconds between requests...")
            time.sleep(wait_time)
    
    def _update_usage_tracker(self, tokens_used: int):
        """Update usage tracking after API call."""
        current_time = time.time()
        
        self.usage_tracker['requests_this_minute'] += 1
        self.usage_tracker['tokens_this_minute'] += tokens_used
        self.usage_tracker['requests_today'] += 1
        self.usage_tracker['last_request_time'] = current_time
        
        # Print current usage status
        limits = self.rate_limits['google']
        print(f"📊 API Usage: {self.usage_tracker['requests_this_minute']}/{limits['requests_per_minute']} requests/min, "
              f"{self.usage_tracker['tokens_this_minute']}/{limits['tokens_per_minute']} tokens/min, "
              f"{self.usage_tracker['requests_today']}/{limits['requests_per_day']} requests/day")
    
    def get_usage_status(self) -> Dict[str, Any]:
        """Get current API usage status."""
        current_time = time.time()
        limits = self.rate_limits['google']
        
        # Calculate time until reset
        time_until_minute_reset = max(0, 60 - (current_time - self.usage_tracker['minute_start_time']))
        
        return {
            'requests_this_minute': self.usage_tracker['requests_this_minute'],
            'requests_per_minute_limit': limits['requests_per_minute'],
            'tokens_this_minute': self.usage_tracker['tokens_this_minute'],
            'tokens_per_minute_limit': limits['tokens_per_minute'],
            'requests_today': self.usage_tracker['requests_today'],
            'requests_per_day_limit': limits['requests_per_day'],
            'time_until_minute_reset': time_until_minute_reset,
            'can_make_request': (
                self.usage_tracker['requests_this_minute'] < limits['requests_per_minute'] and
                self.usage_tracker['tokens_this_minute'] < limits['tokens_per_minute'] and
                self.usage_tracker['requests_today'] < limits['requests_per_day']
            )
        }
    
    # Removed old individual response parsing method - now using batch parsing
    
    def _save_results(self, processed_emails: Dict[str, Any], output_file: str):
        """Save processed results to a file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(processed_emails, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Processed results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
    
    def generate_summary_report(self, processed_emails: Dict[str, Any], report_file: str = None):
        """Generate a human-readable summary report for batch analysis."""
        
        if not report_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"email_summary_report_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("COMPREHENSIVE EMAIL ANALYSIS REPORT\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                # Get total emails from the processed data or use a default
                total_emails = processed_emails.get('total_emails', 0)
                if not total_emails:
                    # Try to get from other fields or use a reasonable default
                    if 'comprehensive_summary' in processed_emails:
                        # Estimate from the summary content
                        summary = processed_emails.get('comprehensive_summary', '')
                        if 'batch of' in summary.lower():
                            # Look for "batch of X emails" pattern
                            import re
                            match = re.search(r'batch of (\d+) emails?', summary.lower())
                            if match:
                                total_emails = int(match.group(1))
                
                f.write(f"Total emails analyzed: {total_emails}\n")
                f.write(f"Analysis timestamp: {datetime.now().isoformat()}\n\n")
                
                # Comprehensive Summary
                f.write("📋 COMPREHENSIVE SUMMARY\n")
                f.write("-" * 40 + "\n")
                f.write(f"{processed_emails.get('comprehensive_summary', 'No summary available')}\n\n")
                
                # High Priority Emails
                high_priority = processed_emails.get('high_priority_emails', [])
                if high_priority:
                    f.write("🚨 HIGH PRIORITY EMAILS\n")
                    f.write("-" * 40 + "\n")
                    for email in high_priority:
                        f.write(f"📧 Email {email.get('email_number', 'N/A')}: {email.get('subject', 'No Subject')}\n")
                        f.write(f"   From: {email.get('sender', 'Unknown')}\n")
                        f.write(f"   Priority: {email.get('priority_level', 'Unknown')}\n")
                        f.write(f"   Reason: {email.get('reason_for_priority', 'No reason given')}\n")
                        f.write(f"   Key Points: {', '.join(email.get('key_points', []))}\n")
                        f.write("-" * 30 + "\n\n")
                else:
                    f.write("🚨 HIGH PRIORITY EMAILS\n")
                    f.write("-" * 40 + "\n")
                    f.write("No high priority emails identified.\n\n")
                
                # Action Items
                action_items = processed_emails.get('action_items', [])
                if action_items:
                    f.write("✅ ACTION ITEMS\n")
                    f.write("-" * 40 + "\n")
                    for i, item in enumerate(action_items, 1):
                        f.write(f"{i}. {item.get('action', 'No action specified')}\n")
                        f.write(f"   Priority: {item.get('priority', 'Unknown')}\n")
                        f.write(f"   Deadline: {item.get('deadline', 'No deadline')}\n")
                        f.write(f"   Source: {item.get('source_email', 'Unknown email')}\n")
                        f.write("-" * 20 + "\n\n")
                else:
                    f.write("✅ ACTION ITEMS\n")
                    f.write("-" * 40 + "\n")
                    f.write("No action items identified.\n\n")
                
                # Email Categories
                categories = processed_emails.get('email_categories', {})
                if categories:
                    f.write("📊 EMAIL CATEGORIES\n")
                    f.write("-" * 40 + "\n")
                    for category, count in categories.items():
                        f.write(f"{category.title()}: {count}\n")
                    f.write("\n")
                
                # Processing Notes section removed as requested
            
            print(f"📊 Comprehensive summary report saved to: {report_file}")
            
            # Read the content back to return it
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                return report_content  # Return the actual report content
            except Exception as e:
                print(f"⚠️ Warning: Could not read report content: {e}")
                return report_file  # Fallback to filename
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return None  # Return None for failure


def main():
    """Main function to demonstrate email LLM processing."""
    print("🤖 Email LLM Processor")
    print("=" * 40)
    
    # Check for extracted email files
    extracted_files = [f for f in os.listdir('.') if f.endswith('_extracted.txt')]
    
    if not extracted_files:
        print("❌ No extracted email files found!")
        print("💡 First run the email extractor to create _extracted.txt files.")
        return
    
    print(f"📁 Found extracted email files:")
    for i, file in enumerate(extracted_files, 1):
        print(f"  {i}. {file}")
    
    # Get API configuration
    print(f"\n🔑 LLM API Configuration:")
    print("Available providers: openai, anthropic, google")
    
    provider = input("Enter provider (default: openai): ").strip() or "openai"
    api_key = input(f"Enter {provider.upper()}_API_KEY (or press Enter to use environment variable): ").strip()
    
    if not api_key:
        api_key = None  # Will use environment variable
    
    # Initialize processor
    try:
        processor = EmailLLMProcessor(api_key=api_key, provider=provider)
        
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
                print(f"✅ Successfully processed {len(processed_emails)} emails")
            else:
                print(f"⚠️ No emails processed from {extracted_file}")
        
        print(f"\n🎉 All processing complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("1. Valid API key for the selected provider")
        print("2. Proper environment variables set")
        print("3. Internet connection for API calls")


if __name__ == '__main__':
    main()
