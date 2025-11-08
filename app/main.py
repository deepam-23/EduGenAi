import streamlit as st
from embedding_client import EmbeddingClient
from pdf_processing import DocumentProcessor
from vector_store import ChromaCollectionCreator
from quiz import QuizGenerator, QuizManager

st.set_page_config(page_title="Quiz Builder", layout="wide")
st.title("📘 Quiz Builder")

# Upload PDF
uploaded_file = st.file_uploader("Choose PDF file", type="pdf")
processor = DocumentProcessor()

if uploaded_file:
    processor.ingest_documents(uploaded_file)
    st.success(f"✅ Processed {len(processor.pages)} pages from PDF!")

# Embed client & Chroma
embed_client = EmbeddingClient()
chroma_creator = ChromaCollectionCreator(processor, embed_client)

topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter topic")
num_questions = st.slider("Number of Questions", 1, 10, 1)

if st.button("Generate Quiz"):
    chroma_creator.create_chroma_collection()
    generator = QuizGenerator(topic_input, num_questions, chroma_creator)
    question_bank = generator.generate_quiz()

    if question_bank:
        st.success("Quiz generated successfully!")
        quiz_manager = QuizManager(question_bank)
        st.session_state["question_index"] = 0
        question = quiz_manager.get_question_at_index(0)
        st.markdown(f"**Q:** {question['question']}")
        choices = [f"{c['key']}) {c['value']}" for c in question["choices"]]
        selected = st.radio("Select answer:", choices)
        if st.button("Submit Answer"):
            if selected.startswith(question["answer"]):
                st.success("Correct!")
            else:
                st.error("Incorrect!")
