import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# LOAD DATASET
data = pd.read_csv("dataset.csv")

# INPUTS
X = data.drop("disease", axis=1)

# OUTPUT
y = data["disease"]

# SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# MODEL
model = RandomForestClassifier()

# TRAIN
model.fit(X_train, y_train)

# SAVE MODEL
with open("disease_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Model trained successfully!")