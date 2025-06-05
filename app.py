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

logging.basicConfig(level=logging.DEBUG)
load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("X_API_KEY")  # Corrected API key variable
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# Register Calibri font (if available)
try:
    pdfmetrics.registerFont(TTFont("Calibri", "C:/Windows/Fonts/calibri.ttf"))
    pdfmetrics.registerFont(TTFont("Calibri-Bold", "C:/Windows/Fonts/calibrib.ttf"))
    FONT_REGULAR = "Calibri"
    FONT_BOLD = "Calibri-Bold"
except:
    logging.warning("Calibri font not found, using Arial as fallback")
    FONT_REGULAR = "Helvetica"
    FONT_BOLD = "Helvetica-Bold"

def generate_cover_letter(job_title, company, skills, background):
    messages = [
        {
            "role": "system",
            "content": """You are an expert cover letter writer with a knack for crafting compelling, tailored narratives. Format outputs with double newlines (\n\n) between paragraphs. Ensure a formal, enthusiastic tone, avoiding generic phrases like 'passionate,' 'dynamic,' or 'fast learner.' Include specific, quantifiable examples when describing skills, and tailor content to the company's mission or achievements."""
        },
        {
            "role": "user",
            "content": f"""Write a 200-250 word cover letter for a {job_title} position at {company}, structured as follows:
- Start with 'Dear Hiring Manager,'.
- Write a 3-sentence introduction expressing enthusiasm for the {job_title} role, referencing a specific {company} achievement or value (e.g., a recent product launch or innovation focus), and summarizing your background: {background}.
- Write a 4-sentence body paragraph detailing the skills ({skills}), including a specific, quantifiable example of one skill applied in a project or job (e.g., developed a tool that improved efficiency by 20%).
- Write a 3-sentence body paragraph explaining how your technical or collaborative experience aligns with {company}'s goals and the role’s responsibilities (e.g., integrating AI systems or working with developers).
- End with a 2-sentence closing inviting an interview and reinforcing commitment to {company}'s mission.
Use double newlines (\n\n) between paragraphs. Tailor the letter to {company}, ensuring specificity and authenticity. Exclude placeholders like '[Your Name]'."""
        }
    ]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-2-latest",
        "messages": messages,
        "max_tokens": 600,
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
    letters = get_all_cover_letters()
    if request.method == 'POST':
        job_title = request.form.get('job_title', '').strip()
        company = request.form.get('company', '').strip()
        skills = request.form.get('skills', '').strip()
        background = request.form.get('background', 'IT professional transitioning to AI').strip()
        if not all([job_title, company, skills]):
            error = "Please fill in all required fields."
        else:
            cover_letter = generate_cover_letter(job_title, company, skills, background)
            save_cover_letter(job_title, company, skills, cover_letter, background)
    return render_template('index.html', cover_letter=cover_letter, letters=letters, error=error)

@app.route('/download/<int:letter_id>')
def download_letter(letter_id):
    logging.debug(f"Attempting to download letter with ID: {letter_id}")
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
    width, height = letter  # Page size from reportlab.lib.pagesizes.letter
    usable_height = height - top_margin - bottom_margin
    
    # Header
    c.setFont(FONT_BOLD, 14)
    c.drawString(left_margin, height - top_margin, f"Cover Letter for {letter_row[1]} at {letter_row[2]}")
    
    # Body text
    c.setFont(FONT_REGULAR, 12)
    y = height - top_margin - 40  # Start below header
    text_object = c.beginText(left_margin, y)
    text_object.setFont(FONT_REGULAR, 12)
    text_object.setLeading(14.4)  # 1.2x font size for line spacing
    for line in letter_row[5].split('\n'):
        text_object.textLine(line.strip())
        y -= 14.4
        if y < bottom_margin:
            c.drawText(text_object)
            c.showPage()
            c.setFont(FONT_REGULAR, 12)
            text_object = c.beginText(left_margin, height - top_margin)
            text_object.setLeading(14.4)
            y = height - top_margin
    c.drawText(text_object)
    c.save()
    logging.info(f"PDF generated: {filename}")
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)