from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd

# Load the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to read CSV file and return the dataframe
def read_csv_file(path):
    data = pd.read_csv(path)
    return data

# Read the labeled questions from the CSV
labeled_questions = read_csv_file('app/scripts/labeled_questions.csv')


# Extract the questions and their labels
questions, labels = labeled_questions['Question'].to_list(), labeled_questions['Category'].to_list()

# Encode the questions using SentenceTransformer
embeddings = model.encode(questions)

# Create label mapping
label_mapping = {label: idx for idx, label in enumerate(set(labels))}
y = [label_mapping[label] for label in labels]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(embeddings, y, test_size=0.2, random_state=42)

# Train a Logistic Regression classifier
classifier = LogisticRegression()
classifier.fit(X_train, y_train)

# Test the classifier and print classification report
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred, target_names=label_mapping.keys()))

# Define a function to classify a new question/message
def classify_question(question):
    # Encode the incoming question
    embedding = model.encode([question])
    
    # Predict the category of the question
    predicted_index = classifier.predict(embedding)
    
    # Return the label corresponding to the predicted index
    return list(label_mapping.keys())[predicted_index[0]]


