from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import joblib
import os

# ✅ Load SentenceTransformer model once
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

def read_csv_file(path):
    return pd.read_csv(path)
# ✅ Load your labeled questions dataset
labeled_questions = read_csv_file("app/ml_models/labeled_questions.csv")
# ✅ Extract the questions and labels
questions, labels = labeled_questions["Question"].to_list(), labeled_questions["Category"].to_list()
# ✅ Generate embeddings for the questions using SentenceTransformer
embeddings = sbert_model.encode(questions)

# ✅ Create a label-to-index mapping for classification
label_mapping = {label: idx for idx, label in enumerate(set(labels))}
y = [label_mapping[label] for label in labels]

# ✅ Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(embeddings, y, test_size=0.2, random_state=42)

# ✅ Train a Logistic Regression classifier
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train, y_train)

# ✅ Make predictions and evaluate the model
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred))

# ✅ Save the trained classifier and label mapping
os.makedirs("app/ml_models", exist_ok=True)
joblib.dump(classifier, "app/ml_models/classifier.pkl")
joblib.dump(label_mapping, "app/ml_models/label_mapping.pkl")
