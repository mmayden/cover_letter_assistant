## Features
- Generate 200-250 word cover letters using xAI’s Grok API with tailored prompts.
- Store cover letters in SQLite with job title, company, skills, background, and timestamp.
- Display previous cover letters with formatted output and a "Download PDF" button.
- Export cover letters as professional PDFs with Calibri font, 12pt text, 1-inch margins, and headers.

## Recent Improvements
- Fixed automatic cover letter generation on page load by restricting generation to POST requests with valid form inputs.
- Corrected API key variable to `X_API_KEY` for proper environment variable access.
- Enhanced PDF downloads with Calibri font, 14pt bold headers, 12pt body text, and 1-inch margins for a professional layout.