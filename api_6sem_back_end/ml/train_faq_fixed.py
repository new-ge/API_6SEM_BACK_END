# train_faq_fixed.py
# Versão corrigida e comentada do seu train_faq.py

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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from colorama import Fore, Style, init

from colorama import Fore, Style, init
init(autoreset=True) # Inicializa o colorama para reset automático

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

# --- 2) Carregamento e Análise Inicial dos Dados ---
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

# --- Garantir colunas essenciais ---
EXPECTED_Q = 'Question'
EXPECTED_A = 'Answer'
if EXPECTED_Q not in df.columns or EXPECTED_A not in df.columns:
    print(f"{Fore.RED}Colunas esperadas não encontradas. Colunas atuais: {df.columns.tolist()}")
    sys.exit(1)

# Tratar valores nulos
df[EXPECTED_Q] = df[EXPECTED_Q].fillna("").astype(str)
df[EXPECTED_A] = df[EXPECTED_A].fillna("").astype(str)

# ---- Estatísticas simples
class_counts = df[EXPECTED_Q].value_counts()
print(f"{Fore.GREEN}Número de Perguntas Únicas (Classes): {Fore.WHITE}{len(class_counts)}")
print(f"{Fore.GREEN}Total de Ocorrências: {Fore.WHITE}{len(df)}")

answer_counts = df[EXPECTED_A].value_counts()
print(f"\nTotal de respostas: {len(df)}")
print(f"Respostas únicas: {answer_counts.shape[0]}")
print(f"Respostas repetidas: {len(df) - answer_counts.shape[0]}")

# --- 3) Pré-processamento e mapeamento para categorias (Topic mapping) ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}3) PRÉ-PROCESSAMENTO: LIMPEZA, AGRUPAMENTO E NORMALIZAÇÃO")
print(f"{Fore.YELLOW}{'='*60}")

def map_to_theme(question):
    if not isinstance(question, str) or question.strip() == "":
        return "OUTROS"
    q = question.lower()
    # palavras-chave (simples) para mapear em categorias
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

df['Category'] = df[EXPECTED_Q].apply(map_to_theme)

# Pré-processamento do texto (Answer)
def preprocess_text(text: str) -> str:
    # normalização básica: lower, remover pontuação, múltiplos espaços
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)        # remove pontuação (usa regex corretamente)
    text = re.sub(r'\s+', ' ', text).strip()    # colapsa espaços
    return text

df['Answer_processed'] = df[EXPECTED_A].apply(preprocess_text)
print(f"{Fore.GREEN}✔ Pré-processamento aplicado. Exemplo:\n  - Original: {df[EXPECTED_A].iloc[0]}\n  - Processado: {df['Answer_processed'].iloc[0]}")

# --- 4) Codificação das classes e divisão Treino/Teste ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}4) CODIFICAÇÃO E DIVISÃO DE DADOS")
print(f"{Fore.YELLOW}{'='*60}")

le = LabelEncoder()
df['Label'] = le.fit_transform(df['Category'])
num_encoded_classes = len(le.classes_)
print(f"{Fore.CYAN}Classes codificadas (0 a {num_encoded_classes - 1}): {Fore.WHITE}{num_encoded_classes}")
print(f"{Fore.YELLOW}Classes mapeadas:")
for idx, cls in enumerate(le.classes_):
    print(f" - {idx}: {cls}")

X = df['Answer_processed']
y = df['Label']

# Verifica se podemos usar stratify (cada classe precisa ter >=2 amostras)
class_sample_counts = df['Label'].value_counts()
min_count = class_sample_counts.min()
use_stratify = (min_count >= 2)
if not use_stratify:
    print(f"{Fore.RED}AVISO: Algumas classes têm menos que 2 amostras (min={min_count}). Não será usado 'stratify' no split.")
else:
    print(f"{Fore.GREEN}Todas as classes têm >=2 amostras (min={min_count}). Será usado 'stratify' para preservar proporções.")

split_args = dict(test_size=0.2, random_state=42)
if use_stratify:
    split_args['stratify'] = y

X_train, X_test, y_train, y_test = train_test_split(X, y, **split_args)
print(f"{Fore.CYAN}Tamanho Treino: {len(X_train)}, Teste: {len(X_test)}")

# --- 5) Vetorização TF-IDF ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}5) VETORIZAÇÃO TF-IDF")
print(f"{Fore.YELLOW}{'='*60}")

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2)
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"{Fore.CYAN}Vocabulário TF-IDF: {len(vectorizer.vocabulary_)} termos")
print(f"{Fore.CYAN}Shape Treino: {X_train_vec.shape}, Teste: {X_test_vec.shape}")

# --- 6) Treinamento (Logistic Regression com class_weight) ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}6) TREINAMENTO DO CLASSIFICADOR")
print(f"{Fore.YELLOW}{'='*60}")

model = LogisticRegression(max_iter=2000, random_state=42, class_weight='balanced', solver='lbfgs', multi_class='auto')
model.fit(X_train_vec, y_train)
print(f"{Fore.GREEN}✔ Treinamento concluído.")

# --- 7) Avaliação ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}7) AVALIAÇÃO DO MODELO")
print(f"{Fore.YELLOW}{'='*60}")

y_pred = model.predict(X_test_vec)

y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

print(f"\n{Fore.CYAN}Relatório de Classificação (Test set):\n")
print(classification_report(y_test_labels, y_pred_labels, zero_division=0))

macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
print(f"{Fore.CYAN}Macro F1: {Fore.WHITE}{macro_f1:.4f}")

# Matriz de confusão reduzida (opcional: imprimir apenas se classes pequenas)
cm = confusion_matrix(y_test, y_pred)
print(f"\n{Fore.CYAN}Matriz de Confusão (shape {cm.shape}):")
print(cm)

# --- 8) Salvar modelo e artefatos ---
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}8) SALVANDO ARTEFATOS")
print(f"{Fore.YELLOW}{'='*60}")

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

model_path = os.path.join(ARTIFACTS_DIR, "faq_classifier_model.pkl")
vec_path = os.path.join(ARTIFACTS_DIR, "faq_tfidf_vectorizer.pkl")
le_path = os.path.join(ARTIFACTS_DIR, "faq_label_encoder.pkl")

joblib.dump(model, model_path)
joblib.dump(vectorizer, vec_path)
joblib.dump(le, le_path)

print(f"{Fore.GREEN}✔ Artefatos salvos em: {ARTIFACTS_DIR}")

# --- Teste rápido de categorização com map_to_theme e modelo salvo ---
def classify_text(text: str):
    txt_proc = preprocess_text(text)
    v = vectorizer.transform([txt_proc])
    pred = model.predict(v)
    label = le.inverse_transform(pred)[0]
    return label

sample_question = "How do I personalize my iPhone with custom ringtones, wallpapers, and other visual elements"
print(f"\n{Fore.YELLOW}Teste de categorização para pergunta:\n→ {sample_question}")
print(f"{Fore.CYAN}map_to_theme: {Fore.WHITE}{map_to_theme(sample_question)}")
print(f"{Fore.CYAN}Modelo predito: {Fore.WHITE}{classify_text(sample_question)}\n")

print(f"{Fore.GREEN}Script finalizado.")


print(map_to_theme("How do I use the Safari web browser on an iPhone"))