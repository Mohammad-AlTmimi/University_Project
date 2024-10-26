from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')


#model.save('fine-tuned-multilingual-sbert')

def read_csv_file(path) :
    data = pd.read_csv(path);
    return data
# r here mean literal it does'not effect the code at all i can delete it and nothing will change 
# but consider this code will be deploy in server it may make small issues 
labeled_questions = read_csv_file(r'./labeled_questions.csv')
#print(labeled_questions)

questions, labels = labeled_questions['Question'].to_list(), labeled_questions['Category'].to_list()
embeddings = model.encode(questions)


label_mapping = {label: idx for idx, label in enumerate(set(labels))}
y = [label_mapping[label] for label in labels]

X_train, X_test, y_train, y_test = train_test_split(embeddings, y, test_size=0.2, random_state=42)

# Train a Logistic Regression classifier
classifier = LogisticRegression()
classifier.fit(X_train, y_train)

target_names = ["Class 1", "Class 2"] 
y_pred = classifier.predict(X_test)
print(classification_report(y_test, y_pred, target_names=label_mapping.keys(), labels=[0, 1]))  # Change labels to your actual classes

def classify_question(question):
    embedding = model.encode([question])
    predicted_index = classifier.predict(embedding)
    return list(label_mapping.keys())[predicted_index[0]]

new_question = "Build table"
question_type = classify_question(new_question)
print(f"The question type is: {question_type}")