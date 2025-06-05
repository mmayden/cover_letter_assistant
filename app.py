from flask import Flask, request, render_template, send_file
import requests
from dotenv import load_dotenv
import os
from database import init_db, save_cover_letter, get_all_cover_letters
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging
import sqlite3
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("X_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Register Calibri font
try:
    pdfmetrics.registerFont(TTFont("Calibri", "C:/Windows/Fonts/calibri.ttf"))
    pdfmetrics.registerFont(TTFont("Calibri-Bold", "C:/Windows/Fonts/calibrib.ttf"))
    FONT_REGULAR = "Calibri"
    FONT_BOLD = "Calibri-Bold"
except:
    logging.warning("Calibri font not found, using Arial as fallback")
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

def generate_cover_letter(job_title, company, skills, background, years_experience, career_narrative, name):
    messages = [
        {
            "role": "system",
            "content": """You are an expert cover letter writer specializing in compelling, authentic narratives for career transitions. Format outputs with double newlines (\n\n) between paragraphs. Use a formal, enthusiastic tone, avoiding clichés like 'passionate,' 'dynamic,' or 'fast learner.' Include specific, quantifiable examples (e.g., improved efficiency by 20%) and tailor content to the company's mission or achievements, ensuring a personal touch based on the user's background and career narrative."""
        },
        {
            "role": "user",
            "content": f"""Write a 200-250 word cover letter for a {job_title} position at {company}, structured as:
- 'Dear Hiring Manager,' greeting.
- 3-sentence introduction expressing enthusiasm for the {job_title} role, referencing a specific {company} achievement or value (e.g., innovation, AI solutions), and summarizing your background: {background} with {years_experience} years of experience.
- 4-sentence body paragraph detailing the skills ({skills}), including a specific, quantifiable example of one skill applied in a project (e.g., developed a Python tool that improved efficiency by 25%), and a personal anecdote tied to your career narrative: {career_narrative}.
- 3-sentence body paragraph explaining how your experience aligns with {company}'s goals and the role’s responsibilities, emphasizing your career transition and technical contributions.
- 2-sentence closing inviting an interview and reinforcing commitment to {company}'s mission, followed by 'Sincerely,' and the name '{name}' on a new line.
Use double newlines (\n\n) between paragraphs. Tailor the letter to {company}, ensuring specificity, authenticity, and a formal tone."""
        }
    ]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-2-latest",
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.9
    }
    try:
        response = requests.post(GROK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.RequestException as e:
        return f"Error generating cover letter: {str(e)}, Response: {response.text}"

@app.route('/', methods=['GET', 'POST'])
def index():
    cover_letter = None
    error = None
    try:
        letters = get_all_cover_letters()
    except sqlite3.Error as e:
        logging.error(f"Database error: {str(e)}")
        letters = []
        error = "Unable to load previous cover letters due to a database issue."
    
    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        company = request.form.get('company', '').strip()
        skills = request.form.get('skills', '').strip()
        background = request.form.get('background', 'IT professional transitioning to AI').strip()
        years_experience = request.form.get('years_experience', '5').strip()
        career_narrative = request.form.get('career_narrative', 'Pursuing a transition to AI development through self-taught programming and AI projects').strip()
        name = request.form.get('name', '').strip()
        if not all([job_title, company, skills]):
            error = "Please fill in all required fields."
        else:
            try:
                cover_letter = generate_cover_letter(job_title, company, skills, background, years_experience, career_narrative, name)
                save_cover_letter(job_title, company, skills, cover_letter, background, years_experience, career_narrative, name)
            except sqlite3.Error as e:
                logging.error(f"Database error during save: {str(e)}")
                error = "Failed to save cover letter due to a database issue."
    
    return render_template('index.html', cover_letter=cover_letter, letters=letters, error=error)

@app.route('/download/<int:letter_id>')
def download_letter(letter_id):
    logging.debug(f"Attempting to download letter with ID: {letter_id}")
    try:
        letters = get_all_cover_letters()
        letter_row = next((l for l in letters if l[0] == letter_id), None)
        if not letter_row:
            logging.error(f"Letter with ID {letter_id} not found")
            return "Letter not found", 404
        logging.debug(f"Found letter: {letter_row}")
        filename = f"cover_letter_{letter_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Set margins (1 inch = 72 points)
        left_margin = 72
        right_margin = 72
        top_margin = 72
        bottom_margin = 72
        width, height = letter
        usable_width = width - left_margin - right_margin
        
        # Date and recipient
        c.setFont(FONT_REGULAR, 12)
        c.drawString(left_margin, height - top_margin, datetime.now().strftime("%B %d, %Y"))
        c.drawString(left_margin, height - top_margin - 15, "Hiring Manager")
        c.drawString(left_margin, height - top_margin - 30, letter_row[2])
        
        # Header
        c.setFont(FONT_BOLD, 14)
        c.drawString(left_margin, height - top_margin - 50, f"Cover Letter for {letter_row[1]} at {letter_row[2]}")
        
        # Body text
        c.setFont(FONT_REGULAR, 12)
        y = height - top_margin - 80
        text_object = c.beginText(left_margin, y)
        text_object.setFont(FONT_REGULAR, 12)
        text_object.setLeading(14.4)
        text_lines = letter_row[5].split('\n')
        for i, line in enumerate(text_lines):
            line = line.strip()
            if line:
                words = line.split()
                current_line = ''
                for word in words:
                    test_line = f"{current_line} {word}".strip()
                    if c.stringWidth(test_line, FONT_REGULAR, 12) <= usable_width:
                        current_line = test_line
                    else:
                        text_object.textLine(current_line)
                        y -= 14.4
                        current_line = word
                        if y < bottom_margin:
                            c.drawText(text_object)
                            c.showPage()
                            c.setFont(FONT_REGULAR, 12)
                            text_object = c.beginText(left_margin, height - top_margin)
                            text_object.setLeading(14.4)
                            y = height - top_margin
                if current_line:
                    text_object.textLine(current_line)
                    y -= 14.4
            else:
                text_object.textLine('')
                y -= 14.4
            if y < bottom_margin and (i + 1 < len(text_lines) or current_line):
                c.drawText(text_object)
                c.showPage()
                c.setFont(FONT_REGULAR, 12)
                text_object = c.beginText(left_margin, height - top_margin)
                text_object.setLeading(14.4)
                y = height - top_margin
        c.drawText(text_object)
        
        # Footer
        c.setFont(FONT_REGULAR, 10)
        c.drawString(left_margin, bottom_margin - 20, f"Page 1")
        
        c.save()
        logging.info(f"PDF generated: {filename}")
        return send_file(filename, as_attachment=True)
    except sqlite3.Error as e:
        logging.error(f"Database error during download: {str(e)}")
        return "Unable to generate PDF due to a database issue.", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)