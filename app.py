from flask import Flask, render_template, redirect, url_for, request, flash
from quiz import QuizGenerator

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages
quiz_gen = QuizGenerator()

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Demo login: redirect to quiz page
        return redirect(url_for('quiz'))
    return render_template('login.html')

# Quiz generation page
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    quiz_results = None
    if request.method == 'POST':
        if 'pdf' not in request.files or request.files['pdf'].filename == '':
            flash("Please upload a PDF file.")
            return redirect(request.url)

        pdf_file = request.files['pdf']
        topic = request.form.get('topic', 'General')
        try:
            num_questions = int(request.form.get('num_questions', 5))
        except ValueError:
            num_questions = 5

        # Generate quiz
        quiz_results = quiz_gen.generate_quiz(pdf_file, topic, num_questions)

    return render_template('quiz.html', quiz_results=quiz_results)

if __name__ == "__main__":
    app.run(debug=True)
