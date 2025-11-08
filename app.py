from flask import Flask, render_template, request
from quiz import QuizGenerator

app = Flask(__name__)
quiz_gen = QuizGenerator()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf')
        topic = request.form.get('topic')
        num_questions = int(request.form.get('num_questions', 5))

        if pdf_file and topic:
            questions = quiz_gen.generate_quiz(pdf_file, topic, num_questions)
            return render_template('quiz.html', quiz_results=questions)

    return render_template('quiz.html', quiz_results=None)

@app.route('/about')
def about():
    return "<h1>About EduGenAi</h1><p>This platform generates quizzes from PDFs for educational purposes.</p>"

if __name__ == '__main__':
    app.run(debug=True)
