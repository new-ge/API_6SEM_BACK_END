import os
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.ml.ml_train_faq_fixed import train_faq_classifier

MODEL_DIR = os.path.join(os.path.dirname(__file__), "artifacts/faq_sentence_transformer")

if not os.path.exists(MODEL_DIR):
    embedder = train_faq_classifier()
else:
    print("Carregando modelo existente de:", MODEL_DIR)
    embedder = SentenceTransformer(MODEL_DIR)

def preprocess_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

faq_data = list(db_data["faq"].find({}, {"Question": 1, "Answer": 1, "_id": 0}))
df_faq = pd.DataFrame(faq_data)
df_faq["Question_clean"] = df_faq["Question"].apply(preprocess_text)

emb_path = os.path.join(os.path.dirname(__file__), "artifacts/faq_question_embeddings.npy")

if os.path.exists(emb_path):
    faq_embeddings = np.load(emb_path)
    print("Embeddings das perguntas carregados do cache.")
else:
    print("Gerando embeddings para todas as perguntas da base...")
    faq_embeddings = embedder.encode(df_faq["Question_clean"].tolist(), convert_to_numpy=True, show_progress_bar=True)
    np.save(emb_path, faq_embeddings)
    print("Embeddings gerados e salvos.")

def search_similar_questions(user_question: str, top_k=5):
    q_proc = preprocess_text(user_question)
    q_emb = embedder.encode([q_proc], convert_to_numpy=True)
    sims = cosine_similarity(q_emb, faq_embeddings)[0]

    top_indices = np.argsort(sims)[::-1][:top_k]
    results = []
    for idx in top_indices:
        results.append({
            "similarity": float(sims[idx]),
            "question": df_faq.iloc[idx]["Question"],
            "answer": df_faq.iloc[idx]["Answer"]
        })
    return results