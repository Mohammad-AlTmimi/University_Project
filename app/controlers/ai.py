import aiohttp
from app.schemas.ai import MessageResponse
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from fastapi.responses import StreamingResponse
import json


env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")

templates = {
    'General University Question': """
    You are a virtual assistant Name MiLo (Mind Logic) for Hebron University.
    Answer the student's question accurately and logically.
    You can Use Markdown Formating to answer

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
    You are a chatbot assistant Name MiLo (Mind Logic) for Hebron University students.
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

    # Prepare the message format
    messages = [
        {
            'role': 'user',
            'content': templates.get(message.get('type'), '').format(question=message.get('content', ''))
        } if message.get('role') == 'user' else message
        for message in payload.messages
    ]
    print(messages)

    # Prepare the request payload
    request_payload = {
        "messages": messages,
        "max_tokens": 150,  
        "temperature": temperatures.get(payload.messages[-1].get('type'), 0.7),
        "stream": True  # Enable streaming of the response
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=request_payload) as response:
            if response.status // 100 != 2:
                raise Exception(f"Error: {await response.text()}")

            buffer = ""
            async for chunk in response.content.iter_any():
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    buffer += chunk_str

                    # Process complete SSE events (delimited by \n\n)
                    while "\n\n" in buffer:
                        event, buffer = buffer.split("\n\n", 1)
                        for line in event.split("\n"):
                            if line.startswith("data:"):
                                data_str = line[5:].strip()  # Remove "data:" prefix
                                if data_str == "[DONE]":
                                    return  # Stop streaming
                                if not data_str:
                                    continue
                                try:
                                    data = json.loads(data_str)
                                    # Check if choices exists and is non-empty
                                    if not data.get("choices") or len(data["choices"]) == 0:
                                        continue  # Skip chunks with no choices
                                    # Check if delta exists
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                                except json.JSONDecodeError as e:
                                    print(f"Error parsing JSON: {data_str} ({e})")
                                    continue