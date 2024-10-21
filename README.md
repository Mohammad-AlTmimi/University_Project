# Project: University Questions and Table Management

This repository contains a few scripts that work together to label university-related questions into categories, fetch data from a university portal, and classify new questions using machine learning.

## Folder Structure

- **csv_converter.py**  
  This script converts labeled questions into a CSV file. The questions are divided into two main categories:
  1. *Build Table*: Questions related to creating and managing tables for projects.
  2. *General University Question*: General questions related to university life, such as academic policies and student services.  
  The script exports these questions and their corresponding categories to a CSV file named `labeled_questions.csv`.

- **portal.py**  
  This script fetches data from a university portal using cookies and makes HTTP requests. The data is extracted using `BeautifulSoup`, and asynchronous calls with `aiohttp` are made to retrieve pages efficiently. It collects hidden form fields from the webpage and submits them with the required payload to retrieve relevant information from the portal.

- **SBERT_Model.py**  
  This script utilizes the **Sentence-BERT** model to classify questions. It loads the labeled data from `labeled_questions.csv`, generates sentence embeddings, and trains a **Logistic Regression** model to classify questions into predefined categories.  
  Key functionalities include:
  - Encoding questions using the `SentenceTransformer`.
  - Splitting data into training and testing sets.
  - Training a logistic regression model on question embeddings.
  - Classifying new questions by predicting their category based on embeddings.

## How to Use

1. **Generate CSV File**  
   Run `csv_converter.py` to generate the `labeled_questions.csv` file. This file will contain all predefined questions with their respective categories.

   ```bash
   python csv_converter.py
   ```

2. **Fetch Portal Data**  
   Make sure to provide your session ID and URL in a `.env` file. The `portal.py` script fetches data from the university portal asynchronously. Ensure that the appropriate cookies and hidden fields are available in your environment.

   ```bash
   python portal.py
   ```

3. **Train and Classify Questions**  
   Use the `SBERT_Model.py` to train a classifier on the provided questions. You can then classify new questions using the trained model.

   ```bash
   python SBERT_Model.py
   ```

4. **Classify a New Question**  
   To classify a new question, modify the `new_question` variable in `SBERT_Model.py`, and run the script to see the classification result.

   ```python
   new_question = "How do I build a table?"
   ```

## Dependencies

- `BeautifulSoup`
- `requests`
- `aiohttp`
- `asyncio`
- `dotenv`
- `sentence-transformers`
- `scikit-learn`
- `pandas`

Make sure to install the required libraries by running:

```bash
pip install -r requirements.txt
```

## Notes
- Ensure your `.env` file contains valid environment variables for `URL` and `ASP_NET_SESSIONID`.
- The `SBERT_Model.py` uses a pre-trained model from Hugging Face's `sentence-transformers`. You can fine-tune or replace the model based on your needs.

---

This project provides a solid foundation for automating question classification and portal data retrieval, helping users streamline information access and categorization.
