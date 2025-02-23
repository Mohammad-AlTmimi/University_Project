from sentence_transformers import SentenceTransformer
import joblib
import os
import asyncio

# ✅ Load SentenceTransformer model once
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Load trained classifier
model_path = "app/ml_models/classifier.pkl"
classifier = joblib.load(model_path) if os.path.exists(model_path) else None

# ✅ Load label mapping
label_mapping_path = "app/ml_models/label_mapping.pkl"
label_mapping = joblib.load(label_mapping_path) if os.path.exists(label_mapping_path) else {}

async def classify_question(question: str) -> str:
    """Classifies a given question using the trained model asynchronously."""
    if not classifier:
        return "Unknown"

    # Run embedding + classification in an executor to prevent blocking
    loop = asyncio.get_running_loop()
    embedding = await loop.run_in_executor(None, sbert_model.encode, [question])
    
    # Reshaping the embedding to match the expected input for classifier.predict
    predicted_index = await loop.run_in_executor(None, classifier.predict, embedding.reshape(1, -1))

    return list(label_mapping.keys())[predicted_index[0]]
