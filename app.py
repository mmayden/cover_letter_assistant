from flask import Flask, request, render_template, send_file
import requests
from dotenv import load_dotenv
import os
from database import init_db, save_cover_letter, get_all_cover_letters
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("X_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

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
    if request.method == 'POST':
        job_title = request.form['job_title']
        company = request.form['company']
        skills = request.form['skills']
        background = request.form.get('background', 'IT professional transitioning to AI')
        cover_letter = generate_cover_letter(job_title, company, skills, background)
        save_cover_letter(job_title, company, skills, cover_letter)
    letters = get_all_cover_letters()
    return render_template('index.html', cover_letter=cover_letter, letters=letters)

@app.route('/download/<int:letter_id>')
def download_letter(letter_id):
    letters = get_all_cover_letters()
    letter = next((l for l in letters if l[0] == letter_id), None)
    if not letter:
        return "Letter not found", 404
    filename = f"cover_letter_{letter_id}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    y = 750
    for line in letter[4].split('\n'):
        c.drawString(100, y, line)
        y -= 15
    c.save()
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)