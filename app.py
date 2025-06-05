from flask import Flask, request, render_template
import requests
from dotenv import load_dotenv
import os
from database import init_db, save_cover_letter, get_all_cover_letters

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("X_API_KEY")
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

def generate_cover_letter(job_title, company, skills):
    messages = [
        {
            "role": "system",
            "content": "You are an expert in writing professional cover letters, specializing in clear, tailored, and enthusiastic responses."
        },
        {
            "role": "user",
            "content": f"""Create a 150-200 word cover letter for a {job_title} position at {company}. Structure it as follows:
- Begin with 'Dear Hiring Manager,'.
- Write a 2-sentence introduction expressing enthusiasm for the {job_title} role and a specific aspect of {company}'s mission or achievements.
- Write a 3-sentence body highlighting the skills ({skills}), including one concrete example of applying a skill in a project or job.
- End with a 2-sentence closing expressing eagerness to contribute and inviting an interview.
Ensure a formal, enthusiastic tone, avoid generic phrases like 'passionate' or 'dynamic,' and tailor the content to {company}. Exclude placeholders like '[Your Name]'."""
        }
    ]
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-2-latest",  # Changed to a confirmed model
        "messages": messages,
        "max_tokens": 400,
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
        cover_letter = generate_cover_letter(job_title, company, skills)
        save_cover_letter(job_title, company, skills, cover_letter)
    letters = get_all_cover_letters()
    return render_template('index.html', cover_letter=cover_letter, letters=letters)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)