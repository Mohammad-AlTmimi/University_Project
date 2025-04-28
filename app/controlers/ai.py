import aiohttp
from app.schemas.ai import MessageResponse
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from fastapi.responses import StreamingResponse
import json
from app.services.templates import buildTableTemplate, generalQuestionTemplate
from app.schemas.ai import PortalPayload
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
import openai


env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)


API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")
openai.api_key = os.getenv("API_KEY")

templateBuilder = {
    'Build Table':  buildTableTemplate
}

temperatures = {
    'General University Question': 0,
    'Build Table': 0
}


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
    
    
    if payload.messageType == 'Build Table':
        template = await templateFunction(PortalPayload(
            portal_id= payload.portal_id,
            user_id= payload.user_id
        ))
        
    elif payload.messageType == 'General Question':
        template = templateFunction()
    messages = payload.messages
    messages[-1]['content'] = template + '\n\n' + messages[-1]['content']


    request_payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "max_tokens": 1000,  
        "temperature": temperatures.get(payload.messages[-1].get('type'), 0.7),
        "stream": True  
    }
    yield {'template': template}
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
                                

def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text


def chunk_text(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks    

def generate_embeddings(chunks):
    embedding_documents = []
    for chunk in chunks:
        response =  openai.embeddings.create(
            model="text-embedding-ada-002",
            input=chunk
        )
        embedding = response.data[0].embedding
        embedding_documents.append({
            "text": chunk,
            "embedding_table": embedding
        })
    return embedding_documents                            