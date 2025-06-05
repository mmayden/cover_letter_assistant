## Features
- Generate 200-250 word cover letters using xAI’s Grok API with tailored prompts.
- Store cover letters in an SQLite database with job title, company, skills, and background.
- Display previous cover letters with formatted output (newlines preserved).
- Download cover letters as PDFs using a styled "Download PDF" button, powered by `reportlab`.

## Recent Improvements
- Added a "Download PDF" button to the "Previous Cover Letters" section, enabling users to export cover letters as PDF files.
- Updated database schema and queries to support PDF downloads using cover letter IDs.
- Enhanced HTML template with styled buttons for a professional user experience.