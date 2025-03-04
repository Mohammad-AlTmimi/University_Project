import os
import aiohttp
from app.schemas.ai import MessageResponse
from fastapi import HTTPException
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")

templates = {
    'General University Question': """
    You are a virtual assistant for Hebron University.
    Answer the student's question accurately and logically.

    ### Thought Process:
    1. Identify the **main topic** of the question.
    2. Determine if the answer requires **official information** (e.g., university policies , university staff , University college ... ) or **general knowledge about Hebron University**.
    3. If official information is needed, check if it exists on the university website: https://www.hebron.edu/.
    4. If no official source is available, provide the best answer based on your knowledge.
    5. Present the answer **clearly and step by step**.

    ### Question:
    {question}

    ### Response:
""",
    'Build Table': """
    You are a chatbot assistant for Hebron University students.
    Your task is to generate a table based on the student's semester courses.
    
    ### Thought Process:
    1. Extract the **required semester** from the question.
    2. Identify the **courses** that match the given semester.
    3. Format the courses into a **structured table** with:
       - Course Name  
       - Course Code  
       - Instructor  
       - Time & Location  
    4. If missing details, politely ask the student for clarification.
    5. Present the response in **table format**.
    
    ### Question:
    {question}
    
    ### Response:
"""
}

temperatures = {
    'General University Question': 0,
    'Build Table': 0
}


async def AIResponse(payload: MessageResponse):
    url = f"{ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
    
    headers = {
        "api-key": API_KEY, 
        "Content-Type": "application/json"
    }
    
    # Apply template based on the request type
    template = templates.get(payload.type, "{question}")
    formatted_prompt = template.format(question=payload.messages[-1])

    # Construct the messages array
    request_payload = {
        "messages": [{"role": "system", "content": formatted_prompt}] + payload.messages,
        "max_tokens": 150,  # You may adjust this based on your needs
        "temperature": temperatures.get(payload.type, 0.7)
    }
    
    # Handling additional capabilities like max fine-tune count, max user file count, etc.
    capabilities = {
        "MaxFineTuneCount": 100,
        "MaxRunningFineTuneCount": 3,
        "MaxUserFileCount": 50,
        "MaxTrainingFileSize": 512000000,
        "MaxUserFileImportDurationInHours": 1,
        "MaxFineTuneJobDurationInHours": 720,
        "MaxEvaluationRunDurationInHours": 5,
        "MaxRunningEvaluationCount": 5
    }

    # Check capabilities if necessary
    # Example: Ensure the request does not exceed the max fine-tune count or file size
    # (Add your conditions here based on your system's use case)
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=request_payload) as response:
            if response.status // 100 == 2:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise HTTPException(status_code=response.status , detail=await response.text())

# Example to test the function
# response = await AIResponse(payload)
# print(response)
