
import streamlit as st
import os
import google.generativeai as genai

from PyPDF2 import PdfReader
from io import BytesIO
from fpdf import FPDF
from docx import Document


os.environ['GOOGLE_API_KEY'] = "AIzaSyD4VSjKUKTqbrxIaRonGLE6HV1lmTfx_sY"
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')


def extract_text_from_pdf(uploaded_file):
    text = ""
    reader = PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    for page_number in range(num_pages):
        text += reader.pages[page_number].extract_text()
    return text


def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 8, content)
    return pdf


def create_word(content):
    doc = Document()
    doc.add_paragraph(content)
    return doc

st.title('CoverLetter Generator')

companyName = st.text_input('Enter the Company name : ');
role = st.text_input('Enter the Role : ');
discription = st.text_input('Enter the job discription (if present) :');
resume = st.file_uploader('Please upload your resume : ');

# prompts
if discription is not None:
    prompt1 = f"I am applying for the position of {role} at {companyName}, and below is the requirement or job discription \n {discription}.\n\n"
else:
    prompt1 = f"I am applying for the position of {role} at {companyName}.\n\n"


prompt2 = f"Write a compelling cover letter tailored to a job mentioned.Express your eagerness to contribute to the team and explain why you believe you're a perfect fit for the role. Be sure to convey your professionalism and enthusiasm for the opportunity in your letter. \n\n"

prompt3 = f"Below I am providing the resume, read the resume carefully, use the content of the resume in order to write the convincing coverletter. My resume: \n"

prompt4 = "Follow the given instruction while writing the Cover letter\n 1. Start directly from the Greetings, dont include address and all\n 2. Don't include any heading and all \n 3. Write in such a way so that i dont need to edit your written letter, I should only do copy and paste.\n 4. In the letter please dont write anything which i need to fill for example some times you are writing [] where i need to add something.\n for your reference, start the letter from Dear hiring manager"


if resume is not None:
    extracted_text = extract_text_from_pdf(resume)

    response = model.generate_content(prompt1 + prompt2 + prompt3 + extracted_text + "\n\n" + prompt4)
    generated_text = response.text

    pdf = create_pdf(generated_text)
    word = create_word(generated_text);
    
    word_bytes = BytesIO()
    word.save(word_bytes)
    word_bytes.seek(0)
    
    col1,col2 = st.columns([10,10])
    with col1:
        st.download_button(label="Download Word", data=word_bytes.getvalue(), file_name="CoverLetter.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    
    with col2:
        st.download_button(label="Download PDF",data=pdf.output(dest='S').encode('latin1'),file_name="CoverLetter.pdf",mime="application/pdf")
        

    