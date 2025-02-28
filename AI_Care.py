from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from components.rag import RAG
from components.nutrition import NutritionAnalyzer
import logging
import sys

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize your RAG and other components here
pdf_path = "C:/Users/Lakshmi/Downloads/clinical_data_report (9).pdf"
rag = RAG(pdf_path)
rag.load_documents()
rag.parse_documents()
rag.setup_llm_and_index()

# Define Pydantic models for request bodies
class RAGQueryRequest(BaseModel):
    query: str

class FoodNutritionRequest(BaseModel):
    food_item: str

class RecipeRequest(BaseModel):
    preference: str

@app.get("/")
async def index():
    return {"message": "Server started"}

@app.post("/rag_query")
async def rag_query(request: RAGQueryRequest):
    res = rag.response(request.query)
    return {"response": res}

@app.post("/food_nutrition")
async def food_nutrition(request: FoodNutritionRequest):
    ingredients = [name.strip() for name in request.food_item.split(",")]
    nutri = NutritionAnalyzer(ingredients)
    nutri.update_dict_data()
    nutri_res = nutri.format_string()
    return {"nutrition_data": nutri_res}

@app.post("/recipe")
async def recipe(request: RecipeRequest):
    symptoms = rag.response("What are symptoms mentioned in the data?")
    treatments = rag.response("What are treatments mentioned in the data?")
    dietary_restrictions = rag.response("What are dietary restrictions mentioned in the data?")
    health_goals = rag.response("What are health goals mentioned in the data?")

    res1 = rag.response_food(request.preference)
    ingredients = rag.query(f"Based on the health status of the patient, remove the unnecessary ingredients in {request.preference} tell why. Also suggest a healthy recipe for the patient using these ingredients.")

    i_arr = ingredients.split(',')
    nutri = NutritionAnalyzer(i_arr)
    nutri.update_dict_data()
    nutri_res = nutri.format_string()

    return {"recipe": res1, "ingredients": ingredients, "nutrition_data": nutri_res}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)


