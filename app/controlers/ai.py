import aiohttp
from app.schemas.ai import MessageResponse
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from fastapi.responses import StreamingResponse
import json
from app.services.templates import buildTableTemplate, generalQuestionTemplate
from app.schemas.ai import PortalPayload, GeneralQuestionTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
import openai
import re

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)


API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")
openai.api_key = os.getenv("API_KEY")
client = openai.AsyncOpenAI(api_key=os.getenv("API_KEY")) 
templateBuilder = {
    'Build Table': buildTableTemplate,
    'General University Question': generalQuestionTemplate
}

temperatures = {
    'General University Question': 0,
    'Build Table': 0
}

async def get_title(question):
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful MiLo assistant. Your job is to create a concise and descriptive title from the user's question."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            temperature=0.5
        )
        print(response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(e)
        raise e


async def AIResponse(payload: MessageResponse):
    url = "https://api.openai.com/v1/chat/completions"
    

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    
    templateFunction = templateBuilder.get(payload.messageType)
    template = ''
    if not templateFunction:
        raise HTTPException(status_code=400, detail=f"Unsupported message type: {payload.messageType}")
    
    
    if payload.messageType == 'Build Table' and len(payload.user_id)> 20:
        template = await templateFunction(PortalPayload(
            portal_id= payload.portal_id,
            user_id= payload.user_id
        ))
        
    else :
        template = await generalQuestionTemplate(GeneralQuestionTemplate(
            portal_id=payload.portal_id,
            user_id= payload.user_id,
            question= payload.messages[-1]['content']
        ))
    messages = payload.messages
    messages[-1]['content'] = template + '\n\n' + messages[-1]['content']


    request_payload = {
        "model": "gpt-4",
        "messages": messages,
        "max_tokens": 700 if payload.messageType == 'Build Table' else 500,  
        "temperature": temperatures.get(payload.messages[-1].get('type'), 0.7),
        "stream": True  
    }
    yield {'template': template}
    print(messages)
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
                                

def remove_diacritics(text):
    arabic_diacritics = re.compile(r'[\u0610-\u061A\u064B-\u065F\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]')
    return re.sub(arabic_diacritics, '', text)

def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    text = remove_diacritics(text=text)
    return text


def chunk_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", "", '،']
    )
    chunks = splitter.split_text(text)
    return chunks    

                            