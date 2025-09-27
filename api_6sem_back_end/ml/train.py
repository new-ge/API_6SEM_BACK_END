import os
import pandas as pd
import joblib
import nltk
import unicodedata
import re
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from api_6sem_back_end.db.db_configuration import db
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient
from dotenv import load_dotenv

collection = db["tickets"]

def preprocess_stopwords(stopwords_list):
    processed = set()
    for word in stopwords_list:
        nfkd = unicodedata.normalize('NFKD', word)
        no_accents = "".join([c for c in nfkd if not unicodedata.combining(c)])
        if re.fullmatch(r"\b\w\w+\b", no_accents.lower()):
            processed.add(no_accents.lower())
    return list(processed)

portuguese_stopwords = stopwords.words("portuguese")
portuguese_stopwords_processed = preprocess_stopwords(portuguese_stopwords)

sia = SentimentIntensityAnalyzer()

data = []
docs = collection.find({}, {"description": 1, "_id": 0})

for doc in docs:
    desc = doc.get("description", "").strip()
    if desc:
        score = sia.polarity_scores(desc)
        compound = score["compound"]

        if compound >= 0.05:
            sentiment = "positivo"
        elif compound <= -0.05:
            sentiment = "negativo"

        data.append({"description": desc, "sentiment": sentiment})

df = pd.DataFrame(data)
df.drop_duplicates(subset="description", inplace=True)

if df.empty:
    print("⚠️ Nenhuma descrição válida encontrada no banco.")
    exit()

X = df["description"]
y = df["sentiment"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.65, random_state=100, stratify=y
)

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        stop_words=portuguese_stopwords_processed,
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w\w+\b",
        max_df=0.95,
        min_df=1
    )),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
])

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)
print(y_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Acurácia do modelo: {accuracy:.2%}")
print("\n📊 Relatório de Classificação:\n")
print(classification_report(y_test, y_pred, zero_division=0))

print("\n📈 Distribuição dos sentimentos previstos pela IA:\n")
pred_df = pd.Series(y_pred)
contagem = pred_df.value_counts()
total = len(pred_df)

for sentimento, quantidade in contagem.items():
    porcentagem = (quantidade / total) * 100
    print(f"➡️ {sentimento}: {quantidade} ({porcentagem:.2f}%)")

model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")
joblib.dump(pipeline, model_path)
print(f"✅ Modelo salvo em: {model_path}")
