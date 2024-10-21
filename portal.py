import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time
from dotenv import load_dotenv
import os

load_dotenv()
a = time.time()

url = os.getenv('URL')
session_id = os.getenv('ASP_NET_SESSIONID')
#User Token
cookies = {
    'ASP.NET_SessionId': session_id
}

response = requests.get(url, cookies=cookies)
#print(response.text)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract hidden form fields
def get_hidden_fields(soup):
    viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
    viewstategen = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
    eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
    #print(type(viewstate))
    #print(type(viewstategen))
    #print(type(eventvalidation))
    return viewstate, viewstategen, eventvalidation

viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)
headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    '__VIEWSTATE': viewstate,
    '__VIEWSTATEGENERATOR': viewstategen,
    '__EVENTVALIDATION': eventvalidation,
    'radioStatus': '1',
    'lstColgsAjax': 'كلية تكنولوجيا المعلومات'
}

response = requests.post(url, headers=headers, data=data, cookies=cookies)

soup = BeautifulSoup(response.text, 'html.parser')

viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)
#print(viewstate)
#print(viewstategen)
#print(eventvalidation)

async def fetch_page(session, url, headers, data, cookies):
    async with session.post(url, headers=headers, data=data, cookies=cookies) as response:
        return await response.text()

async def fetch_all_pages(url, headers, viewstate, viewstategen, eventvalidation, cookies):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_num in range(2, 10):
            data = {
                '__VIEWSTATE': viewstate,
                '__VIEWSTATEGENERATOR': viewstategen,
                '__EVENTVALIDATION': eventvalidation,
                'radioStatus': '1',
                '__EVENTTARGET': 'GridView1',
                '__EVENTARGUMENT': f'Page${page_num}',
                'lstColgsAjax': 'كلية تكنولوجيا المعلومات'
            }
            tasks.append(fetch_page(session, url, headers, data, cookies))

        portalPages = await asyncio.gather(*tasks)
        return portalPages


async def main():
  return await fetch_all_pages(url, headers, viewstate, viewstategen, eventvalidation, cookies)

portalPages = asyncio.run(main())
print(time.time() - a)
#print(portalPages[0])
#portalPages.push(response)
#print(portalPages[len(portalPages) - 1])
soup = BeautifulSoup(portalPages[0], 'html.parser')
row = soup.find('tr', {'bgcolor': '#C8FFC8'})
td_values = [td.text.strip() for td in row.find_all('td')]
print(td_values)
print(time.time() - a)