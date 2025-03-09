# import time
import threading
import pandas as pd
import faiss
# import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch

class FinancialChatbot:
    def __init__(self, data_path, model_name="all-MiniLM-L6-v2", qwen_model_name="Qwen/Qwen2.5-1.5b"):
        self.data_path = data_path
        self.sbert_model = SentenceTransformer(model_name)
        self.index_map = {}
        self.faiss_index = None
        self.qwen_model = AutoModelForCausalLM.from_pretrained(qwen_model_name, torch_dtype="auto", device_map="auto", trust_remote_code=True)
        self.qwen_tokenizer = AutoTokenizer.from_pretrained(qwen_model_name, trust_remote_code=True)
        self.load_or_create_index()
    
    def load_or_create_index(self):
        try:
            self.faiss_index = faiss.read_index("financial_faiss.index")
            with open("index_map.pkl", "rb") as f:
                self.index_map = pickle.load(f)
            print("Index loaded successfully!")
        except:
            print("Creating new FAISS index...")
            df = pd.read_excel(self.data_path)
            sentences = []
            for index, row in df.iterrows():
                for col in df.columns[1:]:
                    text = f"{row[df.columns[0]]} - year {col} is: {row[col]}"
                    sentences.append(text)
                    self.index_map[len(sentences) - 1] = text
            embeddings = self.sbert_model.encode(sentences, convert_to_numpy=True)
            dim = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dim)
            self.faiss_index.add(embeddings)
            faiss.write_index(self.faiss_index, "financial_faiss.index")
            with open("index_map.pkl", "wb") as f:
                pickle.dump(self.index_map, f)
            print("Indexing completed!")
    
    def query_faiss(self, query, top_k=5):
        query_embedding = self.sbert_model.encode([query], convert_to_numpy=True)
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        return [self.index_map[idx] for idx in indices[0] if idx in self.index_map]
    
    def moderate_query(self, query):
        BLOCKED_WORDS = ["hack", "bypass", "illegal", "exploit", "scam", "kill", "laundering", "murder", "suicide", "self-harm"]
        return not any(word in query.lower() for word in BLOCKED_WORDS)
    
    def generate_answer(self, context, question):
        input_text = f"Context: {context}\nQuestion: {question}\nAnswer:"
        inputs = self.qwen_tokenizer.encode(input_text, return_tensors="pt")
        outputs = self.qwen_model.generate(inputs, max_length=100)
        return self.qwen_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    def get_answer(self, query, timeout=150):
        result = ["", 0.0]  # Placeholder for answer and confidence

        def task():
            if self.moderate_query(query):
                retrieved_docs = self.query_faiss(query)
                context = " ".join(retrieved_docs)
                answer = self.generate_answer(context, query)
                last_index = answer.rfind("Answer")
                if answer[last_index+9:11] == "--":
                    result[:] = ["No relevant information found", 0.0]
                else:
                    result[:] = [answer[last_index:], 0.9]
            else:
                result[:] = ["I'm unable to process your request due to inappropriate language.", 0.0]
        
        thread = threading.Thread(target=task)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            return "Execution exceeded time limit. Stopping function.", 0.0
        return tuple(result)

# if __name__ == "__main__":
#     chatbot = FinancialChatbot("C:\\Users\\Dell\\Downloads\\CAI_RAG\\DATA\\Nestle_Financtial_report_till2023.xlsx")
#     query = "What is the Employees Cost in Dec'20?"
#     print(chatbot.get_answer(query))
