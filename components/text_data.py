import boto3
import google.generativeai as genai
import os




# text
class MedicalDataProcessor:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name='us-east-1'):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.comprehend_client = self.initialize_comprehend_client()
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.initialize_google_genai()

    def initialize_comprehend_client(self):
        return boto3.client(
            service_name='comprehendmedical',
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def detect_entities(self, text):
        result = self.comprehend_client.detect_entities(Text=text)
        entities = result['Entities']
        filtered_entities = [{'Text': item['Text'], 'Traits': item['Traits'], 'Score': item['Score']} for item in entities if item['Traits']]
        return filtered_entities

    def initialize_google_genai(self):
        genai.configure(api_key=self.google_api_key)

    def generate_content(self, prompt):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt).text
        return response

    def process_medical_data(self, data):
        entities = self.detect_entities(data)
        print("Detected entities from Comprehend Medical:", entities)

        prompt1 = f"from the given clinical data {data} extract the symptoms, treatment, medication dosage and frequency, health history, disorder(disease) and any other medical concepts only if mentioned in the given data. Your response should be like The symptoms are symptom1, symptom2, the treatments taken are treatment1,... and the same pattern for all. Also just give the data in a formatted manner for the final report"
        res1 = self.generate_content(prompt1)
        print("Response from Gemini:", res1)

        prompt2 = f"Based on the above responses from gemini {res1} and Comprehend Medical {str(entities)}, provide a final description of the patient's symptoms, treatment, medication and dosage of medication(if mentioned), health history, disorder(disease) and any other medical concepts. Your response should be like The symptoms are symptom1, symptom2, the treatments taken are treatment1,... and the same pattern for all. Also just give the data in a formatted manner for the final report. If some data is not mentioned or specified then no need to mention that in the final report. "
        res2 = self.generate_content(prompt2)
        return "Final description:\n"+ str(res2)

    def deidentify(self,data):
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        prompt=f"PFrom the given data {data}, remove personal details of the patient like name, address and any other non medical personal information about the patient."
        model = genai.GenerativeModel('gemini-1.5-flash')
        res = model.generate_content(prompt).text
        return res