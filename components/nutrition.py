import requests
import google.generativeai as genai
import os
import logging
import sys
import os
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class NutritionAnalyzer:
    def __init__(self, ingredients):
        self.ingredients = ingredients
        self.dict_data = {}

    def nutrition(self, ingredient):
        app_key = '9c5410fa23997a92fba28164abaa7efb'  # Replace with your Edamam API app ID
        app_id = '1ce16faa'  # Replace with your Edamam API app key
        result = requests.get(
            'https://api.edamam.com/api/nutrition-data?ingr={}&app_id={}&app_key={}'.format(ingredient, app_id, app_key)
        )
        data = result.json()
        return data

    def update_dict_data(self):
        for ingredient in self.ingredients:
            data = self.nutrition(ingredient)
            if 'calories' in self.dict_data:
                self.dict_data['calories'] += data['calories']
            else:
                self.dict_data['calories'] = data['calories']

            for key, value in data['totalNutrients'].items():
                label = value['label']
                quantity = value['quantity']
                if label in self.dict_data:
                    self.dict_data[label] += quantity 
                else:
                    self.dict_data[label] = quantity

    
        # Create final string representation of dict_data
        final_string = str(self.dict_data)
        return final_string
    
    def get_final_string(self):
        # Convert quantities to string with units
        dummy = self.nutrition(self.ingredients[0])
        units = {value['label']: value['unit'] for label, value in dummy['totalNutrients'].items()}
        final_data = {}
        for label, quantity in self.dict_data.items():
            if label in units:
                unit = units[label]
                final_data[label] = f"{quantity} {unit}, \n"
            else:
                final_data[label] = str(quantity) +", \n"
        if 'calories' in self.dict_data:
            final_data['calories'] = str(self.dict_data['calories'])+", \n"

        # Create final string representation of dict_data
        final_string = " ".join([f"{label}: {value}" for label, value in final_data.items()])
        return final_string
    
    def format_string(self):
        data = self.get_final_string()
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"For the given nutritional data {str(data)} format it in a user friendly manner.")
        res = model.generate_content(prompt).text
        return res
