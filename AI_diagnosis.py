from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import google.generativeai as genai

from components.text_data import MedicalDataProcessor
from components.image_data import IAnalysis
from components.pdf_data import R_Analysis
from components.final_report import F_Diagnose
from components.pdf_generator import PDFGenerator

app = Flask(__name__)
CORS(app)

aws_access_key_id = 'your_aws_access_key_id'
aws_secret_access_key = 'your_aws_secret_access_key'

@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    text_data = data.get('text_data')
    
    if text_data:
        processor = MedicalDataProcessor(aws_access_key_id, aws_secret_access_key)
        text_deidentified = processor.deidentify(text_data)
        f_text = processor.process_medical_data(text_deidentified)
        return jsonify({"processed_text": f_text})
    return jsonify({"error": "No text data provided"}), 400

@app.route('/process_image', methods=['POST'])
def process_image():
    file = request.files['image']
    if file:
        file_path = os.path.join("uploaded_images", file.filename)
        file.save(file_path)
        
        i_analysis = IAnalysis(file_path)
        i_data = i_analysis.g_vision()
        return jsonify({"image_analysis": i_data})
    return jsonify({"error": "No image file provided"}), 400

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files['pdf']
    if file:
        file_path = os.path.join("uploaded_pdfs", file.filename)
        file.save(file_path)
        
        r_analysis = R_Analysis(file_path)
        r_data = r_analysis.get_data()
        return jsonify({"pdf_data": r_data})
    return jsonify({"error": "No pdf file provided"}), 400

@app.route('/generate_report', methods=['POST'])
def generate_report():
    data = request.json
    text_data = data.get('text_data')
    image_data = data.get('image_data')
    pdf_data = data.get('pdf_data')
    
    if text_data and image_data and pdf_data:
        final_data = f"{text_data}\n{image_data}\n{pdf_data}"
        
        f_diagnose = F_Diagnose(final_data)
        diagnosis_report = f_diagnose.diagnosis_report()
        diagnosis_report += f_diagnose.suggestions(diagnosis_report)
        
        pdf_data_input = format(diagnosis_report)
        pdf_gen = PDFGenerator(pdf_data_input, "clinical_data_report.pdf")
        pdf_buffer = pdf_gen.create_pdf()
        
        return send_file(pdf_buffer, as_attachment=True, download_name="clinical_data_report.pdf", mimetype='application/pdf')
    return jsonify({"error": "Incomplete data provided"}), 400

def format(data):
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (f"For the given data {data} format the data in a precise manner. This formatted data will be the diagnosis report to be written to a pdf and given to the user. This pdf will then be used for RAG. So format this data such that RAG can eisily extract the required medical concepts based on the query. Like Instead of Giving Symptoms: symptom1, symptom2 format the data to Symptoms: the symptoms are symptom1, symptom2. For Treatment: The treatments are treatment1, treatment 2. For Dietary Restrictions: the Dietary Restrictions are dietary_restrictions1,dietary_restrictions2. For  Health Goals: health_goal1, health_goal2.  For any other data category of data other than the ones mentioned just include them as it is in the given {data}. This way the RAG will easily be able to extract specific data when question like What? are asked.")
    res = model.generate_content(prompt).text
    return res

if __name__ == '__main__':
    app.run(debug=True)
