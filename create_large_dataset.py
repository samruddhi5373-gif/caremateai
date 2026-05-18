import pandas as pd
import random

symptoms = [
    'fever',
    'cough',
    'headache',
    'fatigue',
    'vomiting',
    'body_pain',
    'cold',
    'breathing_problem',
    'chest_pain',
    'sore_throat',
    'loss_of_smell'
]

disease_patterns = {

    'Flu': [1,1,1,1,0,1,1,0,0,1,0],

    'Covid': [1,1,1,1,0,1,0,1,0,1,1],

    'Cold': [0,1,0,0,0,0,1,0,0,1,0],

    'Food Poisoning': [0,0,1,1,1,0,0,0,0,0,0],

    'Heart Disease': [0,0,0,1,0,0,0,1,1,0,0],

    'Asthma': [0,1,0,1,0,0,0,1,0,0,0],

    'Typhoid': [1,0,1,1,1,1,0,0,0,0,0],

    'Pneumonia': [1,1,0,1,0,1,0,1,0,1,0],

    'Migraine': [0,0,1,1,0,0,0,0,0,0,0],

    'Malaria': [1,0,1,1,1,1,0,0,0,0,0]
}

rows = []

for disease, pattern in disease_patterns.items():

    for _ in range(5000):

        sample = []

        for value in pattern:

            # Add small random variation
            if random.random() < 0.1:
                sample.append(1 - value)
            else:
                sample.append(value)

        sample.append(disease)

        rows.append(sample)

columns = symptoms + ['disease']

df = pd.DataFrame(rows, columns=columns)

df = df.sample(frac=1).reset_index(drop=True)

df.to_csv('dataset.csv', index=False)

print("Large dataset created successfully!")
print("Total rows:", len(df))