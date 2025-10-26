# Pacotes de terceiros
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from api_6sem_back_end.db.de import db_data
from colorama import Fore, Style, init
init(autoreset=True)  # Inicializa o colorama para reset automático

# Ajuste de caminho para importar módulo local
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api_6sem_back_end.db.db_configuration import db

# ---------------------- [1] Conexão com o MongoDB ---------------------- #
print(f"\n{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}1) ESTABELECENDO CONEXÃO COM O MONGODB")
print(f"{Fore.YELLOW}{'='*60}")

client = MongoClient(os.getenv("DB_URL_MONGO"))
db = client["bd6sem-luminia"]
collection = db["tickets"]

print(f"{Fore.CYAN}URL MongoDB: {Fore.WHITE}{os.getenv('DB_URL_MONGO')}")
print(f"{Fore.CYAN}Banco de Dados: {Fore.WHITE}{db.name}")
print(f"{Fore.CYAN}Coleção: {Fore.WHITE}{collection.name}")
print(f"{Fore.CYAN}Collections Disponíveis: {Fore.WHITE}{db.list_collection_names()}")
print(f"{Fore.GREEN}✔ Conexão estabelecida com sucesso!\n")

# ---------------------- [2] Carregando Dados ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}2) CONSULTANDO DADOS NA COLEÇÃO 'tickets'")
print(f"{Fore.YELLOW}{'='*60}")

docs = db.tickets.find({}, {
    "_id": 0, "ticket_id": 1, "access_level": 1, 
    "category": 1, "description": 1, "title": 1, "sla": 1
})

data = pd.DataFrame(list(docs))

print(f"{Fore.CYAN}Total de Documentos Encontrados: {Fore.WHITE}{len(data)}")
print(f"{Fore.CYAN}Colunas: {Fore.WHITE}{data.columns.tolist()}")
print(f"{Fore.CYAN}Visualização Inicial:\n{Fore.WHITE}{data.head()}")
print(f"{Fore.CYAN}Valores Nulos:\n{Fore.WHITE}{data.isnull().sum()}")

# Verificando estrutura de dados aninhados
if isinstance(data['access_level'].iloc[0], dict):
    print(f"{Fore.CYAN}Subcampos de 'access_level': {Fore.WHITE}{list(data['access_level'].iloc[0].keys())}")
elif isinstance(data['access_level'].iloc[0], list):
    print(f"{Fore.CYAN}Lista de 'access_level': {Fore.WHITE}{data['access_level'].iloc[0]}")

if isinstance(data['sla'].iloc[0], str):
    try:
        json_data = json.loads(data['sla'].iloc[0])
        print(f"{Fore.CYAN}Subcampos de 'sla': {Fore.WHITE}{list(json_data.keys())}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}⚠ A coluna 'sla' não contém dados JSON válidos.")

print(f"{Fore.GREEN}✔ Dados consultados e carregados com sucesso!\n")

# ---------------------- [3] Codificando Categoria ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}3) CODIFICANDO A COLUNA 'category'")
print(f"{Fore.YELLOW}{'='*60}")

label_encoder = LabelEncoder()
data['category_encoded'] = label_encoder.fit_transform(data['category'])

print(f"{Fore.CYAN}Mapeamento de Categorias:")

for i, cat in enumerate(label_encoder.classes_):
    print(f"{Fore.WHITE}  {cat} => {label_encoder.transform([cat])[0]}")

print(f"{Fore.GREEN}✔ Codificação concluída!\n")

# ---------------------- [4] Vetorizando Texto ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}4) TRANSFORMANDO COLUNAS DE TEXTO (TF-IDF)")
print(f"{Fore.YELLOW}{'='*60}")

data['full_text'] = data['title'] + " " + data['description']
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
X_text = vectorizer.fit_transform(data['full_text']).toarray()

X_combined = np.hstack((X_text, data[['category_encoded']].values))
y = data['category_encoded']

print(f"{Fore.GREEN}✔ Texto vetorizado e colunas combinadas!\n")

# ---------------------- [5] Treinamento e Avaliação ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}5) TREINANDO MODELO DE ÁRVORE DE DECISÃO")
print(f"{Fore.YELLOW}{'='*60}")

X_train, X_test, y_train, y_test = train_test_split(X_combined, y, test_size=0.3, random_state=42)

print(f"{Fore.CYAN}Tamanho do treino: {Fore.WHITE} {X_train.shape},\n{Fore.CYAN} Tamanho do teste: {Fore.WHITE}{X_test.shape}")

clf = DecisionTreeClassifier(max_depth=5, min_samples_split=2, min_samples_leaf=1)
clf.fit(X_train, y_train)

print(f"{Fore.GREEN}✔ Modelo treinado com sucesso!\n")

# ---------------------- [6] Avaliação do Modelo ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}6) AVALIAÇÃO DO MODELO")
print(f"{Fore.YELLOW}{'='*60}")

y_pred = clf.predict(X_test)
print(f"{Fore.CYAN}Relatório de Classificação:\n{Fore.WHITE}{classification_report(y_test, y_pred)}")
print(f"{Fore.CYAN}Matriz de Confusão:\n{Fore.WHITE}{confusion_matrix(y_test, y_pred)}")

accuracy = clf.score(X_test, y_test)
print(f"\n{Fore.CYAN}Acurácia do Modelo: {Fore.GREEN}{accuracy * 100:.2f}%\n")

# ---------------------- [7] Salvando o Modelo ---------------------- #
print(f"{Fore.YELLOW}{'='*60}")
print(f"{Fore.YELLOW}7) SALVANDO MODELO E OBJETOS")
print(f"{Fore.YELLOW}{'='*60}")

joblib.dump(clf, 'modelo_chamados.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')

print(f"{Fore.GREEN}✔ Modelo e objetos salvos com sucesso!")

# ---------------------- [8] Carregando Modelo (Verificação) ---------------------- #
clf = joblib.load('modelo_chamados.pkl')
vectorizer = joblib.load('vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

print(f"{Fore.GREEN}✔ Modelo recarregado com sucesso!\n")



