import google.generativeai as genai
import os
import google.generativeai as genai
import PyPDF2
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# pdf report
class R_Analysis:
    def __init__(self, file_path):
        self.file_path = file_path
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def extract_pdf(self):
        data = ""
        with open(self.file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]
                data += page.extract_text()
        return data        
    
    def deidentify(self,data):
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        prompt=f"PFrom the given data {data}, remove personal details of the patient like name, address and any other non medical personal information about the patient."
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt).text
        return res
    
    def get_data(self):
        data = self.extract_pdf()
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"the given data {data} is a medical lab report data. Organize this data is data is the right format with just the parameter/fields and the value. So that this data can be written in final diagnosis report of the patient. Remove unnecessary data.")
        res = model.generate_content(prompt).text
        result = self.deidentify(res)
        return result