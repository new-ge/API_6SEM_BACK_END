import os
import sys
import re
import joblib
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from colorama import Fore, init
from sentence_transformers import SentenceTransformer
from api_6sem_back_end.db.db_configuration import db_data

def train_faq_classifier():
    collection = db_data["faq"]

    init(autoreset=True)  

    MONGO_URL = os.getenv("DB_URL_MONGO")
    if not MONGO_URL:
        sys.exit(1)

    try:
        data = list(collection.find({}))
        df = pd.DataFrame(data)
    except Exception as e:
        sys.exit(1)

    EXPECTED_Q = 'Question'
    EXPECTED_A = 'Answer'
    if EXPECTED_Q not in df.columns or EXPECTED_A not in df.columns:
        sys.exit(1)

    df[EXPECTED_Q] = df[EXPECTED_Q].fillna("").astype(str)
    df[EXPECTED_A] = df[EXPECTED_A].fillna("").astype(str)

    def map_to_theme(question):
        if not isinstance(question, str) or question.strip() == "":
            return "OUTROS"
        q = question.lower()
        if any(kw in q for kw in ["ringtone", "wallpaper", "customize", "customization", "watch face", "visual elements", "personalize"]):
            return "Personalização e Usabilidade"
        elif any(kw in q for kw in ["health", "workout", "activity", "maps", "music", "reminders", "calls", "messages", "apps", "app"]):
            return "Funcionalidades e Apps"
        elif any(kw in q for kw in ["display settings", "reset", "factory", "screenshot", "clear cache", "update", "software", "settings"]):
            return "Configurações e Manutenção"
        elif any(kw in q for kw in ["privacy", "security", "erase", "passcode", "two-factor", "two factor", "face id", "touch id"]):
            return "Privacidade e Segurança"
        elif any(kw in q for kw in ["battery", "prolong usage", "performance", "slow", "lag"]):
            return "Otimização e Performance"
        elif any(kw in q for kw in ["backup", "restore", "backup and restore", "backup restore"]):
            return "Backup e Restauração"
        elif any(kw in q for kw in ["siri", "shortcuts", "translate", "safari", "get help", "assistant", "automation", "web access"]):
            return "Assistência, Automação e Acesso Web"
        else:
            return "OUTROS"

    df["Category"] = df[EXPECTED_Q].apply(map_to_theme)

    def preprocess_text(text: str) -> str:
        text = str(text).lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    df["Answer_processed"] = df[EXPECTED_A].apply(preprocess_text)

    le = LabelEncoder()
    df["Label"] = le.fit_transform(df["Category"])

    X = df["Answer_processed"]
    y = df["Label"]

    class_counts = df["Label"].value_counts()
    min_count = class_counts.min()
    use_stratify = min_count >= 2

    split_args = dict(test_size=0.2, random_state=42)
    if use_stratify:
        split_args["stratify"] = y

    X_train, X_test, y_train, y_test = train_test_split(X, y, **split_args)

    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    print(f"Gerando embeddings para o conjunto de treinamento...")
    X_train_vec = embedder.encode(X_train.tolist(), convert_to_numpy=True, show_progress_bar=True)
    print(f"Gerando embeddings para o conjunto de teste...")
    X_test_vec = embedder.encode(X_test.tolist(), convert_to_numpy=True, show_progress_bar=True)

    model = LogisticRegression(max_iter=2000, random_state=42, class_weight="balanced", solver="lbfgs", multi_class="auto")
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    y_test_labels = le.inverse_transform(y_test)
    y_pred_labels = le.inverse_transform(y_pred)

    ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    model_path = os.path.join(ARTIFACTS_DIR, "faq_classifier_model.pkl")
    le_path = os.path.join(ARTIFACTS_DIR, "faq_label_encoder.pkl")
    embed_path = os.path.join(ARTIFACTS_DIR, "faq_sentence_transformer")

    joblib.dump(model, model_path)
    joblib.dump(le, le_path)
    embedder.save(embed_path)

    print(f"Artefatos salvos em: {ARTIFACTS_DIR}")

    return embedder