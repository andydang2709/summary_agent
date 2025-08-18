# Email Summary Data Repository

This repository contains the generated email summaries and reports from the Email Summary Agent.

## Structure

- `logs/` - Daily email summary reports (YYYYMMDD_email_summary_report.txt)
- `storytelling/` - Storytelling summaries for text-to-speech (YYYYMMDD_storytelling_summary.txt)
- `file_index.json` - Index of all available files with metadata
- `latest/` - Most recent summaries (today_email_summary_report.txt, executive_summary.txt)

## Files

### Daily Reports
- `20250817_email_summary_report.txt` - August 17, 2025 email summary
- `20250816_email_summary_report.txt` - August 16, 2025 email summary
- etc.

### Storytelling Summaries
- `20250817_storytelling_summary.txt` - August 17, 2025 storytelling summary
- `20250816_storytelling_summary.txt` - August 16, 2025 storytelling summary
- etc.

### Current Files
- `today_email_summary_report.txt` - Today's email summary
- `executive_summary.txt` - Today's storytelling summary

## Updates

This repository is automatically updated daily by GitHub Actions from the main Email Summary Agent repository.

## Usage

The main application fetches data from this repository via GitHub Pages URLs:
- `https://[username].github.io/email-summary-data/file_index.json`
- `https://[username].github.io/email-summary-data/logs/[filename]`
- `https://[username].github.io/email-summary-data/latest/[filename]`

## GitHub Pages

This repository is configured to serve files via GitHub Pages, making the data accessible to the main application.
