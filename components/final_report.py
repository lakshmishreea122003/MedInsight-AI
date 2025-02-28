import google.generativeai as genai
import os


class F_Diagnose:

    def __init__(self, data):
        self.data = data
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def diagnosis_report(self):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"You are a healthcare assistant to help the health professional understand the problem. Thus you have to help prepare a diagnosis report based in the given patient data. The given data {self.data} of the medical details of the patient. Consider this information about the patient. Provide a detailed explaination as to what the person is suffering from based in the data. Tell what may be the reasons why the person is suffering from the problems he/she has. Basically you should help provide a diagnosis report based on the given data. Make sure the result repovided is well formatted.")
        res = model.generate_content(prompt).text
        return res
    
    def suggestions(self,data):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"Based on the given data given {data} about a patient you have to be the health care advisor. Suggest Dietary Restrictions, Required physical activities, Life style changes for better health, Health Goals the patient must set for better health. For all of these categories, provide a well formatted report to help manage the person's health condition.")
        res = model.generate_content(prompt).text
        return res