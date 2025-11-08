import openai
import json
import random
import PyPDF2

class QuizGenerator:
    def __init__(self):
        openai.api_key = "AIzaSyBP337DxNJEM_80tEqdcPZD8Zck7AKbIY0"

    def extract_text(self, pdf_file):
        text = ""
        if pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text[:10000]  # limit text length to avoid token overflow

    def generate_quiz(self, pdf_file, topic, num_questions=5):
        text = self.extract_text(pdf_file)
        if not text:
            return [{"question": "Error: Could not extract text from PDF."}]

        prompt = f"""
        Generate {num_questions} multiple-choice questions (MCQs) on the topic '{topic}' 
        based on this material:
        {text}

        Each question should be formatted as JSON:
        [
          {{
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "answer": "B"
          }}
        ]
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            content = response["choices"][0]["message"]["content"]

            # Extract JSON safely
            data = json.loads(content)
            random.shuffle(data)
            return data

        except Exception as e:
            print("Error generating quiz:", e)
            return [{"question": f"Error generating quiz: {str(e)}"}]

    def export_pdf(self, quiz_data, include_answers=True):
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from io import BytesIO

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        c.setFont("Helvetica", 12)

        for i, q in enumerate(quiz_data):
            c.drawString(50, y, f"{i+1}. {q['question']}")
            y -= 20
            for opt in q['options']:
                c.drawString(70, y, opt)
                y -= 20
            if include_answers:
                c.setFillColorRGB(0, 1, 0)
                c.drawString(70, y, f"Answer: {q['answer']}")
                c.setFillColorRGB(0, 0, 0)
                y -= 30
            if y < 100:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - 50

        c.save()
        buffer.seek(0)
        return buffer
