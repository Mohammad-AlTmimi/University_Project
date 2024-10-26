import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time
from dotenv import load_dotenv
import os
from app.exceptions import CustomError

load_dotenv()

# in this updated code now we automated the process of scrap data from portal page by pass user
# token to function 
# for performance and scailability i will treat this code as a package which i will only import it in needed place
# (for team meamber please read the code carefully make sure you understand every thing and if you have any question pls ask)
# this code might have a few problem so it still under testing which my take alitle time as the portal page is closed 
# this package still need to have the number of pages that need to scrap as we know give to page 
# but it should be automated 


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

def get_hidden_fields(soup):
    try:
        viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategen = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
    except (TypeError, KeyError) as e:
        raise CustomError("Missing required hidden fields", 1001)
    return viewstate, viewstategen, eventvalidation

def scrapCourses(session_id):
    url = os.getenv('URL')

    cookies = {
        'ASP.NET_SessionId': session_id
    }

    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
    except requests.RequestException as e:
        raise CustomError(f"Failed to fetch initial page: {str(e)}", 1002)

    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)
    except CustomError as e:
        print(e)
        return []  # Returning an empty list if hidden fields are missing

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

    try:
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        response.raise_for_status()
    except requests.RequestException as e:
        raise CustomError(f"Error during POST request: {str(e)}", 1003)

    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)

    async def main():
        return await fetch_all_pages(url, headers, viewstate, viewstategen, eventvalidation, cookies)

    start_time = time.time()
    portalPages = asyncio.run(main())
    print(f"Time taken: {time.time() - start_time} seconds")

    if portalPages:
        arrSoup = [BeautifulSoup(page, 'html.parser') for page in portalPages]
        rows = [soup.findAll('tr', {'bgcolor': '#C8FFC8'}) for soup in arrSoup]
        td_values = [td.text.strip() for r in rows for row in r for td in row.find_all('td')]
        return td_values

    return []

try:
    print(scrapCourses('1irpnm0mv1ibafsk5ot5zlgz'))
except CustomError as e:
    print(f"CustomError occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
