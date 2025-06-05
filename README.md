## Features
- Generate 200-250 word cover letters using xAI’s Grok API with tailored prompts.
- Store cover letters in SQLite with job title, company, skills, background, and timestamp.
- Display previous cover letters with formatted output and a "Download PDF" button.
- Export cover letters as professional PDFs with Calibri font, 12pt text, 1-inch margins, and headers.

## Recent Improvements
- Fixed `sqlite3.OperationalError: no such table: cover_letters` by initializing the database before queries.
- Added error handling to display user-friendly messages for database issues (e.g., missing database).
- Corrected API key variable to `X_API_KEY` and prevented unwanted cover letter generation on page load.