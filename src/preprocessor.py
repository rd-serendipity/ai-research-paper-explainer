import io
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PaperPreprocessor:
    @staticmethod
    def extract_text_from_pdf(uploaded_file):
        if uploaded_file.type != "application/pdf":
            raise ValueError("Uploaded file is not a PDF")
        
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def split_text(text, chunk_size = 2000, chunk_overlap = 200, length_function = len):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len)
        splitted_text = text_splitter.split_text(text)
        return splitted_text
    



    

