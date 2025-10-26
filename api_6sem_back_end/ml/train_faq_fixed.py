# train_faq_fixed.py
# Versão corrigida e comentada do seu train_faq.py
# Agora com embeddings semânticos (SentenceTransformer)

import os
import sys
import re
import joblib
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.preprocessing import LabelEncoder
from colorama import Fore, Style, init
from sentence_transformers import SentenceTransformer

# Ajuste de caminho para importar módulo local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api_6sem_back_end.db.db_configuration import db

# ---------------------- [1] Conexão com o MongoDB ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}1) ESTABELECENDO CONEXÃO COM O MONGODB")
print(f"{Fore.YELLOW}{'='*60}")

client = MongoClient(os.getenv("DB_URL_MONGO"))
db = client["bd6sem-luminia"]
collection = db["faq"]

print(f"{Fore.CYAN}URL MongoDB: {Fore.WHITE}{os.getenv('DB_URL_MONGO')}")
print(f"{Fore.CYAN}Banco de Dados: {Fore.WHITE}{db.name}")
print(f"{Fore.CYAN}Coleção: {Fore.WHITE}{collection.name}")
print(f"{Fore.CYAN}Collections Disponíveis: {Fore.WHITE}{db.list_collection_names()}")
print(f"{Fore.GREEN}✔ Conexão estabelecida com sucesso!\n")


init(autoreset=True)  # Inicializa o colorama para reset automático

# ---------------------- [1] Conexão com o MongoDB ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}1) ESTABELECENDO CONEXÃO COM O MONGODB")
print(f"{Fore.YELLOW}{'='*60}")

MONGO_URL = os.getenv("DB_URL_MONGO")
if not MONGO_URL:
    print(f"{Fore.RED}Variável de ambiente DB_URL_MONGO não definida. Verifique antes de rodar.")
    sys.exit(1)

try:
    client = MongoClient(MONGO_URL)
    db = client["bd6sem-luminia"]
    collection = db["faq"]
    print(f"{Fore.CYAN}URL MongoDB: {Fore.WHITE}{MONGO_URL}")
    print(f"{Fore.CYAN}Banco de Dados: {Fore.WHITE}{db.name}")
    print(f"{Fore.CYAN}Coleção: {Fore.WHITE}{collection.name}")
    print(f"{Fore.CYAN}Collections Disponíveis: {Fore.WHITE}{db.list_collection_names()}")
    print(f"{Fore.GREEN}✔ Conexão estabelecida com sucesso!\n")
except Exception as e:
    print(f"{Fore.RED}Erro ao conectar ao MongoDB: {e}")
    sys.exit(1)

# ---------------------- [2] Carregamento e análise inicial ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}2) CARREGAMENTO E ANÁLISE INICIAL DOS DADOS")
print(f"{Fore.YELLOW}{'='*60}")

try:
    data = list(collection.find({}))
    df = pd.DataFrame(data)
    print(f"{Fore.CYAN}Total de documentos carregados: {Fore.WHITE}{len(df)}")
    print(f"{Fore.CYAN}Colunas disponíveis: {Fore.WHITE}{df.columns.tolist()}")
except Exception as e:
    print(f"{Fore.RED}ERRO ao carregar dados do MongoDB: {e}")
    sys.exit(1)

EXPECTED_Q = 'Question'
EXPECTED_A = 'Answer'
if EXPECTED_Q not in df.columns or EXPECTED_A not in df.columns:
    print(f"{Fore.RED}Colunas esperadas não encontradas. Colunas atuais: {df.columns.tolist()}")
    sys.exit(1)

df[EXPECTED_Q] = df[EXPECTED_Q].fillna("").astype(str)
df[EXPECTED_A] = df[EXPECTED_A].fillna("").astype(str)

print(f"{Fore.GREEN}✔ Dados carregados e tratados com sucesso!")

# ---------------------- [3] Pré-processamento e categorização ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}3) PRÉ-PROCESSAMENTO: LIMPEZA, AGRUPAMENTO E NORMALIZAÇÃO")
print(f"{Fore.YELLOW}{'='*60}")

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
print(f"{Fore.GREEN}✔ Pré-processamento aplicado. Exemplo:")
print(f"  - Original: {df[EXPECTED_A].iloc[0]}")
print(f"  - Processado: {df['Answer_processed'].iloc[0]}")

# ---------------------- [4] Codificação e divisão ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}4) CODIFICAÇÃO E DIVISÃO DE DADOS")
print(f"{Fore.YELLOW}{'='*60}")

le = LabelEncoder()
df["Label"] = le.fit_transform(df["Category"])

print(f"{Fore.CYAN}Classes encontradas:")
for i, c in enumerate(le.classes_):
    print(f" - {i}: {c}")

X = df["Answer_processed"]
y = df["Label"]

class_counts = df["Label"].value_counts()
min_count = class_counts.min()
use_stratify = min_count >= 2

split_args = dict(test_size=0.2, random_state=42)
if use_stratify:
    split_args["stratify"] = y

X_train, X_test, y_train, y_test = train_test_split(X, y, **split_args)
print(f"{Fore.CYAN}Tamanho Treino: {len(X_train)}, Teste: {len(X_test)}")

# ---------------------- [5] Embeddings Semânticos ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}5) EMBEDDINGS SEMÂNTICOS (Sentence Transformers)")
print(f"{Fore.YELLOW}{'='*60}")

embedder = SentenceTransformer("all-MiniLM-L6-v2")

print(f"{Fore.CYAN}Gerando embeddings para o conjunto de treinamento...")
X_train_vec = embedder.encode(X_train.tolist(), convert_to_numpy=True, show_progress_bar=True)
print(f"{Fore.CYAN}Gerando embeddings para o conjunto de teste...")
X_test_vec = embedder.encode(X_test.tolist(), convert_to_numpy=True, show_progress_bar=True)

print(f"{Fore.CYAN}Shape Treino: {X_train_vec.shape}, Teste: {X_test_vec.shape}")

# ---------------------- [6] Treinamento ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}6) TREINAMENTO DO CLASSIFICADOR (com Embeddings)")
print(f"{Fore.YELLOW}{'='*60}")

model = LogisticRegression(max_iter=2000, random_state=42, class_weight="balanced", solver="lbfgs", multi_class="auto")
model.fit(X_train_vec, y_train)
print(f"{Fore.GREEN}✔ Treinamento concluído com embeddings semânticos.")

# ---------------------- [7] Avaliação ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}7) AVALIAÇÃO DO MODELO")
print(f"{Fore.YELLOW}{'='*60}")

y_pred = model.predict(X_test_vec)
y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

print(f"{Fore.CYAN}Relatório de Classificação:\n")
print(classification_report(y_test_labels, y_pred_labels, zero_division=0))
macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
print(f"{Fore.CYAN}Macro F1: {Fore.WHITE}{macro_f1:.4f}")

cm = confusion_matrix(y_test, y_pred)
print(f"\n{Fore.CYAN}Matriz de Confusão (shape {cm.shape}):")
print(cm)

# ---------------------- [8] Salvar artefatos ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}8) SALVANDO ARTEFATOS")
print(f"{Fore.YELLOW}{'='*60}")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

model_path = os.path.join(ARTIFACTS_DIR, "faq_classifier_model.pkl")
le_path = os.path.join(ARTIFACTS_DIR, "faq_label_encoder.pkl")
embed_path = os.path.join(ARTIFACTS_DIR, "faq_sentence_transformer")

joblib.dump(model, model_path)
joblib.dump(le, le_path)
embedder.save(embed_path)

print(f"{Fore.GREEN}✔ Artefatos salvos em: {ARTIFACTS_DIR}")

# ---------------------- [9] Teste rápido ---------------------- #
def classify_text(text: str):
    txt_proc = preprocess_text(text)
    emb = embedder.encode([txt_proc], convert_to_numpy=True)
    pred = model.predict(emb)
    label = le.inverse_transform(pred)[0]
    return label

sample_question = "How do I personalize my iPhone with custom ringtones, wallpapers, and other visual elements"
print(f"\n{Fore.YELLOW}Teste de categorização para pergunta:\n→ {sample_question}")
print(f"{Fore.CYAN}map_to_theme: {Fore.WHITE}{map_to_theme(sample_question)}")
print(f"{Fore.CYAN}Modelo predito: {Fore.WHITE}{classify_text(sample_question)}\n")

print(f"{Fore.GREEN}Script finalizado com sucesso usando SentenceTransformer.")


print("O que eu fiz até o momento: Um modelo SentenceTransformer salvo em artifacts/faq_sentence_transformer")
print("Uma collection faq no MongoDB com campos Question e")
print("Answer e Função preprocess_text() para limpeza dos textos")