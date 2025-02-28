import google.generativeai as genai
import os
import google.generativeai as genai
import google.generativeai as genai


# Image class
class IAnalysis:

    def __init__(self, file_path):
        self.file_path = file_path
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
     
    def g_vision(self):
        sample_file = genai.upload_file(path=self.file_path, display_name="image")
        print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
        file = genai.get_file(name=sample_file.name)
        print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content([sample_file, "What can be seen in the image? Describe what ever can be seen in the image. This is health related image. Mention if there are any abnormalities seen in the image. Describe the image in medical manner."])
        return response.text
    
    def gemini(self):
        v_data = self.g_vision()
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"The following information is about the image uploaded by a patient(user). The google vision pro says: {v_data}.  Your duty is to consider the above given information and give a precise output about what the image is about. It is related to health. While analysing the data, give more importance to the google vision data.")
        res = model.generate_content(prompt).text
        return res


    def i_analysis(self):
        gemini_data = self.gemini()
        data = "The analysis of the uploaded image reveals the following data: "+ gemini_data
