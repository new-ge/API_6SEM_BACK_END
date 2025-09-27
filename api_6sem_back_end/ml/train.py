import os
import pandas as pd
import joblib
import nltk
import unicodedata
import re

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from nltk.corpus import stopwords

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

data = [
    {"description": "Erro no cálculo da remuneração variável de agosto.", "sentiment": "negativo"},
    {"description": "Pesquisa de clima organizacional não foi enviada para todos.", "sentiment": "negativo"},
    {"description": "Sistema de atendimento está muito lento.", "sentiment": "negativo"},
    {"description": "Necessidade de atualização no perfil do cargo de analista de dados.", "sentiment": "neutro"},
    {"description": "Chamados não estão sendo direcionados corretamente aos agentes.", "sentiment": "negativo"},
    {"description": "Solicito simulação de metas com base na nova regra de bônus.", "sentiment": "neutro"},
    {"description": "Dificuldade em vincular ações de melhoria aos objetivos do PDI.", "sentiment": "negativo"},
    {"description": "Erro 500 ao acessar o módulo de pesquisas.", "sentiment": "negativo"},
    {"description": "Sugestão: permitir exportação em PDF dos perfis de cargo.", "sentiment": "positivo"},
    {"description": "Erro ao tentar salvar novo cargo na plataforma.", "sentiment": "negativo"},
    {"description": "Solicito relatório consolidado das respostas da última pesquisa.", "sentiment": "positivo"},
    {"description": "Plano de desenvolvimento não aparece para o colaborador.", "sentiment": "negativo"},
    {"description": "Sugestão de melhoria: permitir avaliação dos artigos.", "sentiment": "positivo"}
]

df = pd.DataFrame(data)
df.drop_duplicates(subset="description", inplace=True)

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
accuracy = accuracy_score(y_test, y_pred)

print(f"\n✅ Acurácia do modelo: {accuracy:.2%}")
print("\n📊 Relatório de Classificação:\n")
print(classification_report(y_test, y_pred, zero_division=0))

model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")
joblib.dump(pipeline, model_path)
print(f"✅ Modelo salvo em: {model_path}")
