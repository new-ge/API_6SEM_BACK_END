import joblib
import numpy as np


clf = joblib.load('modelo_chamados.pkl')
vectorizer = joblib.load('vectorizer.pkl')
label_encoder = joblib.load('label_encoder.pkl')

def predict_category(title, description, category_encoded):
    full_text = title + " " + description
    X_text = vectorizer.transform([full_text]).toarray()
    
    # Concatenar a feature category_encoded como uma matriz 2D
    X_combined = np.hstack((X_text, np.array([[category_encoded]])))
    
    pred_encoded = clf.predict(X_combined)[0]
    pred_category = label_encoder.inverse_transform([pred_encoded])[0]
    return pred_category