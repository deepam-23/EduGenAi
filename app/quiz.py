import PyPDF2

class QuizGenerator:
    def generate_quiz(self, pdf_file, topic, num_questions):
        # Initialize PDF reader
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
        except Exception as e:
            print("Error reading PDF:", e)
            return [f"Error reading PDF: {e}"]

        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + " "

        if not full_text.strip():
            return [f"No readable text found in the PDF for topic '{topic}'"]

        # Split text into sentences
        sentences = [s.strip() for s in full_text.split('.') if len(s.strip()) > 20]

        questions = []
        for i in range(min(num_questions, len(sentences))):
            questions.append(f"Q{i+1}: {sentences[i]} (Topic: {topic})")

        while len(questions) < num_questions:
            questions.append(f"Q{len(questions)+1}: [Sample question about {topic}]")

        return questions
