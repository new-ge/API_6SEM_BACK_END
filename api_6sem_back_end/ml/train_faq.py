# Pacotes de terceiros
import os
import sys
import joblib 
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression 
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from api_6sem_back_end.db.de import db_data
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

# ---------------------- [2] Carregamento e Análise dos Dados ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}2) CARREGAMENTO E ANÁLISE INICIAL DOS DADOS")
print(f"{Fore.YELLOW}{'='*60}")

# 1. Carrega todos os documentos da coleção 'faq'
try:
    data = list(collection.find({}))
    df = pd.DataFrame(data)

    print(f"{Fore.CYAN}Total de documentos carregados: {Fore.WHITE}{len(df)}")
    print(f"{Fore.CYAN}Colunas disponíveis: {Fore.WHITE}{df.columns.tolist()}")

except Exception as e:
    print(f"{Fore.RED}ERRO ao carregar dados do MongoDB: {e}")
    sys.exit(1)

# 2. Análise de Repetição (Identificação das Classes)

TARGET_COLUMN = 'Question'
FEATURE_COLUMN = 'Answer'

print(f"\n{Fore.YELLOW}ANÁLISE DE CLASSES E REPETIÇÃO:")

# Calcula a frequência de cada pergunta única (nossas classes)
class_counts = df[TARGET_COLUMN].value_counts()
num_classes = len(class_counts)

print(f"{Fore.CYAN}Coluna Target (Classes): {Fore.WHITE}{TARGET_COLUMN}")
print(f"{Fore.CYAN}Coluna Feature (Entrada): {Fore.WHITE}{FEATURE_COLUMN}")
print(f"{Fore.GREEN}Número de Perguntas Únicas (Classes): {Fore.WHITE}{num_classes}")
print(f"{Fore.GREEN}Total de Ocorrências: {Fore.WHITE}{len(df)}")

# ----------------------------------------------------------------------------------
# NOVO: ANÁLISE DE DISTRIBUIÇÃO DE REPETIÇÃO
# ----------------------------------------------------------------------------------
print(f"\n{Fore.YELLOW}TABELA DE DISTRIBUIÇÃO DE REPETIÇÃO:")

# Cria uma tabela: Contagem de quantos tópicos (perguntas) se repetem N vezes.
# Ex: Quantos tópicos têm exatamente 5 repetições, quantos têm 4, etc.
repetition_counts = class_counts.value_counts().sort_index(ascending=False)

print(f"{Fore.CYAN}{'| Perguntas (Tópicos)':<25} | {'Se Repetem (Frequência)':<25}|")
print(f"{Fore.CYAN}{'|'+'-'*25} | {'-'*25+'|'}")

for count, num_questions in repetition_counts.items():
    # count: o número de vezes que a pergunta se repete (o N da tabela)
    # num_questions: o número de perguntas que têm essa repetição (o "Perguntas" da tabela)
    print(f"| {num_questions:<23} | {count:<23} |")

# Exibe as 5 classes mais frequentes (apenas para manter o log original)
print(f"\n{Fore.YELLOW}Top 5 Perguntas (Classes) mais frequentes:")
top_classes = class_counts.head(27)
total = len(df)
for question, count in top_classes.items():
    percentage = (count / total) * 100
    print(f" - {Fore.MAGENTA}'{question}'{Style.RESET_ALL}: {count} ocorrências ({percentage:.2f}%)")

# O restante do código, incluindo o alerta e as Seções 3 a 8, permanece igual.
# ... (O restante do código do train_faq.py, das Seções 3 a 8) ...

# Contagem de quantas vezes cada resposta aparece
answer_counts = df['Answer'].value_counts()

# Número total de respostas únicas
num_unique_answers = answer_counts.shape[0]

# Número total de registros
total_answers = df.shape[0]

print(f"\nTotal de respostas: {total_answers}")
print(f"Respostas únicas: {num_unique_answers}")
print(f"Respostas repetidas: {total_answers - num_unique_answers}")

print("\nDistribuição de Repetição das Respostas:")
distribution = answer_counts.value_counts().sort_index(ascending=False)

print(f"{'Repetições':<15} {'Qtd de Respostas':<20}")
print("-" * 35)
for freq, count in distribution.items():
    print(f"{freq:<15} {count:<20}")


print("\nTop 10 Respostas mais repetidas:")
print(answer_counts.head(10))


# ---------------------- Análise da Resposta (Feature) ---------------------- #
print(f"\n{Fore.YELLOW}ANÁLISE DA COLUNA FEATURE (Resposta):")

num_unique_answers = df['Answer'].nunique()

print(f"{Fore.CYAN}Número de Respostas Únicas: {Fore.WHITE}{num_unique_answers}")

if num_unique_answers == len(df):
    print(f"{Fore.RED}ALERTA: Cada amostra tem uma resposta única. Isso reforça a necessidade de agrupamento.")
elif num_unique_answers > 855:
    print(f"{Fore.RED}ALERTA: O número de respostas únicas ({num_unique_answers}) é maior que o de perguntas únicas (855), o que é incomum e deve ser investigado (duas perguntas diferentes têm a mesma resposta, mas a resposta varia mais do que as perguntas).")
else:
    print(f"{Fore.GREEN}Confirmação: Existem {len(df) - num_unique_answers} respostas repetidas.")

# ---------------------- [3] Pré-Processamento e Agrupamento de Classes ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}3) PRÉ-PROCESSAMENTO: LIMPEZA, AGRUPAMENTO E NORMALIZAÇÃO")
print(f"{Fore.YELLOW}{'='*60}")

# 3.1 Limpeza Inicial e Remoção de Coluna Vazia
if '' in df.columns:
    df = df.drop(columns=['', '_id'], errors='ignore')
    print(f"{Fore.CYAN}Colunas Removidas: {Fore.WHITE} ['', '_id']")

# 3.2 Agrupamento em 7 categorias temáticas
def map_to_theme(question):
    q = question.lower()
    
    if any(kw in q for kw in ["ringtone", "wallpaper", "customize", "customization", "watch face", "visual elements", "personalize"]):
        return "Personalização e Usabilidade"
    elif any(kw in q for kw in ["health", "workout", "activity", "maps", "music", "reminders", "calls", "messages", "apps"]):
        return "Funcionalidades e Apps"
    elif any(kw in q for kw in ["display settings", "reset", "factory", "screenshot", "clear cache", "update"]):
        return "Configurações e Manutenção"
    elif any(kw in q for kw in ["privacy", "security", "erase"]):
        return "Privacidade e Segurança"
    elif any(kw in q for kw in ["battery", "prolong usage", "performance"]):
        return "Otimização e Performance"
    elif any(kw in q for kw in ["backup", "restore"]):
        return "Backup e Restauração"
    elif any(kw in q for kw in ["siri", "shortcuts", "translate", "safari", "get help", "assistant"]):
        return "Assistência, Automação e Acesso Web"
    else:
        return "OUTROS"

topic_names = {
    0: "Personalização e Usabilidade",
    1: "Funcionalidades e Apps",
    2: "Configurações e Manutenção",
    3: "Privacidade e Segurança",
    4: "Otimização e Performance",
    5: "Backup e Restauração",
    6: "Assistência, Automação e Acesso Web",
    7: "OUTROS"
}



# Aplica o mapeamento
df["Category"] = df["Question"].apply(map_to_theme)

# Atualiza a variável de coluna final
TARGET_COLUMN_FINAL = "Category"

# 3.3 Pré-processamento do Texto (Feature: Answer)
def preprocess_text(text):
    text = str(text).lower() 
    text = text.replace(r'[^\w\s]', '')
    return text

df[FEATURE_COLUMN] = df[FEATURE_COLUMN].apply(preprocess_text)
print(f"{Fore.GREEN}✔ Pré-processamento do texto (minúsculas) aplicado à coluna '{FEATURE_COLUMN}'.")

print(f"{Fore.YELLOW}{'='*60}\n")

# ---------------------- [4] Codificação (Label Encoding) e Divisão de Dados ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}4) CODIFICAÇÃO E DIVISÃO DE DADOS")
print(f"{Fore.YELLOW}{'='*60}")

# 4.1 Codificação do Target (Labels)
le = LabelEncoder()
df['Label'] = le.fit_transform(df[TARGET_COLUMN_FINAL])
num_encoded_classes = len(le.classes_)

print(f"{Fore.CYAN}Classes Codificadas (0 a {num_encoded_classes - 1}): {Fore.WHITE}{num_encoded_classes}")
print(f"{Fore.CYAN}Target Final: {Fore.WHITE}Label")

# Print das classes finais
print(f"\n{Fore.YELLOW}CLASSIFICAÇÕES FINAIS DAS PERGUNTAS (Rótulos do Modelo):")
for idx, class_name in enumerate(le.classes_):
    print(f" - {Fore.GREEN}{idx}: {class_name}")
print(f"{Fore.YELLOW}{'-'*60}")


# ---------------------- [4] Codificação (Label Encoding) e Divisão de Dados ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}4) CODIFICAÇÃO E DIVISÃO DE DADOS")
print(f"{Fore.YELLOW}{'='*60}")

# 4.1 Codificação do Target (Labels)
le = LabelEncoder()
df['Label'] = le.fit_transform(df[TARGET_COLUMN_FINAL])
num_encoded_classes = len(le.classes_)

print(f"{Fore.CYAN}Classes Codificadas (0 a {num_encoded_classes - 1}): {Fore.WHITE}{num_encoded_classes}")
print(f"{Fore.CYAN}Target Final: {Fore.WHITE}Label")

# Print das classes finais
print(f"\n{Fore.YELLOW}CLASSIFICAÇÕES FINAIS DAS PERGUNTAS (Rótulos do Modelo):")
for idx, class_name in enumerate(le.classes_):
    print(f" - {Fore.GREEN}{idx}: {class_name}")
print(f"{Fore.YELLOW}{'-'*60}")


# 4.2 Divisão em Treino e Teste
X = df[FEATURE_COLUMN] 
y = df['Label'] 

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"{Fore.CYAN}Tamanho do Conjunto de Treinamento: {Fore.WHITE}{len(X_train)} amostras")
print(f"{Fore.CYAN}Tamanho do Conjunto de Teste: {Fore.WHITE}{len(X_test)} amostras")
print(f"{Fore.GREEN}✔ Dados divididos (80/20).\n")


# ---------------------- [5] Vetorização (TF-IDF) ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}5) VETORIZAÇÃO DE TEXTO (TF-IDF)")
print(f"{Fore.YELLOW}{'='*60}")

vectorizer = TfidfVectorizer(
    max_features=5000,
    stop_words='english',
    ngram_range=(1, 2)
)


X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

print(f"{Fore.CYAN}Vocabulário TF-IDF aprendido: {Fore.WHITE}{len(vectorizer.vocabulary_)} termos")
print(f"{Fore.CYAN}Formato do Treinamento (Matriz Esparsa): {Fore.WHITE}{X_train_vectorized.shape}")
print(f"{Fore.CYAN}Formato do Teste (Matriz Esparsa): {Fore.WHITE}{X_test_vectorized.shape}")
print(f"{Fore.GREEN}✔ Vetorização TF-IDF concluída.\n")


# ---------------------- [6] Treinamento do Modelo (Logistic Regression) ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}6) TREINAMENTO DO CLASSIFICADOR")
print(f"{Fore.YELLOW}{'='*60}")

model = LogisticRegression(max_iter=1000, random_state=42) 

print(f"{Fore.CYAN}Modelo Selecionado: {Fore.WHITE}{type(model).__name__}")
model.fit(X_train_vectorized, y_train)

print(f"{Fore.GREEN}✔ Treinamento concluído com sucesso!")
print(f"{Fore.YELLOW}{'='*60}\n")


# ---------------------- [7] Avaliação do Modelo ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}7) AVALIAÇÃO DO MODELO")
print(f"{Fore.YELLOW}{'='*60}")

y_pred = model.predict(X_test_vectorized)

y_test_labels = le.inverse_transform(y_test)
y_pred_labels = le.inverse_transform(y_pred)

print(f"{Fore.CYAN}Relatório de Classificação (Conjunto de Teste):\n")
print(classification_report(y_test_labels, y_pred_labels, zero_division=0))

print(f"{Fore.GREEN}✔ Avaliação do modelo concluída.")
print(f"{Fore.YELLOW}{'='*60}\n")


# ---------------------- [8] Salvar o Modelo e Artefatos ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}8) SALVANDO O MODELO E OS ARTEFATOS")
print(f"{Fore.YELLOW}{'='*60}")

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "artifacts"))
os.makedirs(MODEL_DIR, exist_ok=True)

model_path = os.path.join(MODEL_DIR, 'faq_classifier_model.pkl')
joblib.dump(model, model_path)

vectorizer_path = os.path.join(MODEL_DIR, 'faq_tfidf_vectorizer.pkl')
joblib.dump(vectorizer, vectorizer_path)

label_encoder_path = os.path.join(MODEL_DIR, 'faq_label_encoder.pkl')
joblib.dump(le, label_encoder_path)

print(f"{Fore.GREEN}✔ Artefatos salvos em: {MODEL_DIR}")
print(f"{Fore.YELLOW}{'='*60}\n")

# Teste de categorização
sample_question = "How do I personalize my iPhone with custom ringtones, wallpapers, and other visual elements"
print(f"{Fore.YELLOW}Teste de categorização para pergunta:\n→ {sample_question}")
print(f"{Fore.CYAN}Categoria atribuída: {Fore.WHITE}{map_to_theme(sample_question)}\n")


print(map_to_theme("How do I use the Camera app on an iPhone"))