from flask import Flask, request, render_template
from transformers import pipeline
from database import init_db, save_cover_letter, get_all_cover_letters

app = Flask(__name__)
generator = pipeline('text2text-generation', model='google/flan-t5-base')

def generate_cover_letter(job_title, company, skills):
    prompt = f"""Write a professional 200-word cover letter for a {job_title} role at {company}, highlighting the following skills: {skills}. Ensure the tone is formal, enthusiastic, and tailored to the job and company."""
    result = generator(prompt, max_length=300, num_return_sequences=1)
    return result[0]['generated_text']

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