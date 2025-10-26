import os
import re
import joblib
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# ---------------------- [1] Conexão MongoDB ---------------------- #
MONGO_URL = os.getenv("DB_URL_MONGO")
client = MongoClient(MONGO_URL)
db = client["bd6sem-luminia"]
collection = db["faq"]

# ---------------------- [2] Carrega modelo de embeddings ---------------------- #
embedder = SentenceTransformer(os.path.join(os.path.dirname(__file__), "artifacts/faq_sentence_transformer"))

def preprocess_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ---------------------- [3] Carrega base FAQ ---------------------- #
faq_data = list(collection.find({}, {"Question": 1, "Answer": 1, "_id": 0}))
df_faq = pd.DataFrame(faq_data)
df_faq["Question_clean"] = df_faq["Question"].apply(preprocess_text)

# ---------------------- [4] Cria ou carrega embeddings do banco ---------------------- #
emb_path = os.path.join(os.path.dirname(__file__), "artifacts/faq_question_embeddings.npy")

if os.path.exists(emb_path):
    faq_embeddings = np.load(emb_path)
    print("✅ Embeddings das perguntas carregados do cache.")
else:
    print("⚙️ Gerando embeddings para todas as perguntas da base...")
    faq_embeddings = embedder.encode(df_faq["Question_clean"].tolist(), convert_to_numpy=True, show_progress_bar=True)
    np.save(emb_path, faq_embeddings)
    print("✅ Embeddings gerados e salvos.")

# ---------------------- [5] Função para buscar perguntas semelhantes ---------------------- #
def search_similar_questions(user_question: str, top_k=5):
    q_proc = preprocess_text(user_question)
    q_emb = embedder.encode([q_proc], convert_to_numpy=True)
    sims = cosine_similarity(q_emb, faq_embeddings)[0]
    
    # Pega índices das perguntas mais semelhantes
    top_indices = np.argsort(sims)[::-1][:top_k]
    results = []
    for idx in top_indices:
        results.append({
            "similarity": float(sims[idx]),
            "question": df_faq.iloc[idx]["Question"],
            "answer": df_faq.iloc[idx]["Answer"]
        })
    return results

# ---------------------- [6] Teste manual ---------------------- #
if __name__ == "__main__":
    query = input("Digite sua pergunta: ")
    results = search_similar_questions(query)
    print("\n🔍 Resultados mais semelhantes:\n")
    for r in results:
        print(f"({r['similarity']:.3f}) {r['question']}")
        print(f"→ {r['answer']}\n")
