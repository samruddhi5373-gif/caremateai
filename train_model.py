import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# SMALL DATASET

data = {

    'fever': [3,2,1,0,3],
    'cough': [3,2,1,0,2],
    'headache': [2,1,0,0,3],
    'fatigue': [3,2,1,0,2],
    'vomiting': [0,1,3,0,0],
    'body_pain': [3,2,1,0,2],
    'diarrhea': [0,0,3,0,0],
    'breathing': [2,1,0,0,3],
    'chest_pain': [0,0,0,3,2],
    'loss_smell': [0,3,0,0,2],
    'sore_throat': [3,2,1,0,2],

    'disease': [
        'Flu',
        'Covid',
        'Food Poisoning',
        'Heart Disease',
        'General Viral Infection'
    ]
}

df = pd.DataFrame(data)

X = df.drop('disease', axis=1)

y = df['disease']

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)

model = RandomForestClassifier()

model.fit(X, y_encoded)

joblib.dump(model, 'disease_model.pkl')

joblib.dump(label_encoder, 'label_encoder.pkl')

print("Model Trained Successfully!")