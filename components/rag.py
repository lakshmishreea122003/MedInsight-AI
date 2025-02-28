from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
import google.generativeai as genai
import os
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


class RAG:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.documents = None
        self.nodes = None
        self.query_engine = None
        GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def load_documents(self):
        loader = PDFReader()
        self.documents = loader.load_data(file=self.pdf_path)
        logging.debug(f"Loaded {len(self.documents)} documents from {self.pdf_path}")
        print(self.documents)
        print("############# load documents")

    def parse_documents(self):
        parser = SimpleNodeParser.from_defaults(chunk_size=200, chunk_overlap=10)
        self.nodes = parser.get_nodes_from_documents(self.documents)
        logging.debug(f"Extracted {len(self.nodes)} nodes from documents")
        print("############### nodes")
    

    def setup_llm_and_index(self):
        llm = Gemini(model="models/gemini-pro")
        embed_model = GeminiEmbedding(model_name="models/embedding-001")
        
        Settings.llm = llm
        Settings.embed_model = embed_model
        Settings.chunk_size = 512

        vector_index = VectorStoreIndex(self.nodes)
        self.query_engine = vector_index.as_query_engine()

    def query(self, query_text):
        response_vector = self.query_engine.query(query_text)
        return response_vector.response
    
    def response(self,query_text):
        res = self.query(query_text)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"This data {res} is from the rag chatbot for the question {query_text}. Use the given data to answer the question {query_text} in a precise manner. Give answers to the point. Then for the explanation write EXPLANATION then explain. ")
        res = model.generate_content(prompt).text
        return res
    
    def response_food(self,query_text):
        query_text = f"Based on the health status of the patient, remove the unnecessary ingredients in {query_text} tell why. Also suggest a healthy recipe for the patient using these ingredients."
        res = self.query(query_text)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (f"This data {res} is from the rag chatbot for the question {query_text}. Use the given data to answer the question {query_text} in a precise manner. Give answers to the point. Then for the explanation write EXPLANATION then explain. ")
        res = model.generate_content(prompt).text
        return res
