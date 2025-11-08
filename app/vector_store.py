import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        self.processor = processor
        self.embed_model = embed_model
        self.db = None

    def create_chroma_collection(self):
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Split documents into chunks
        text_splitter = CharacterTextSplitter(separator=".", chunk_size=1000, chunk_overlap=100)
        plain_docs = [page.page_content for page in self.processor.pages]
        split_docs = []
        for doc in plain_docs:
            split_docs.extend(text_splitter.split_text(doc))

        documents = [Document(page_content=text) for text in split_docs]
        self.db = Chroma.from_documents(documents, embedding=self.embed_model)

        if self.db:
            st.success(f"✅ Successfully created Chroma Collection with {len(documents)} chunks!")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")

    def as_retriever(self):
        return self.db.as_retriever() if self.db else None

    def query_chroma_collection(self, query):
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")
