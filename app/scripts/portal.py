import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import time
from dotenv import load_dotenv
import os

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

def scrapCourses(session_id):
    url = os.getenv('URL')

    # User Token
    cookies = {
        'ASP.NET_SessionId': session_id
    }

    # Get initial response
    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.RequestException as e:
        print(f"Error fetching the initial page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hidden form fields
    def get_hidden_fields(soup):
        viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategen = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
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

    try:
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error during the POST request: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)

    # Asynchronously fetch all pages
    async def main():
        return await fetch_all_pages(url, headers, viewstate, viewstategen, eventvalidation, cookies)

    start_time = time.time()
    portalPages = asyncio.run(main())
    print(f"Time taken: {time.time() - start_time} seconds")

    # Process the first page
    if portalPages:
        arrSoup = [BeautifulSoup(page, 'html.parser') for page in portalPages]
        rows = [soup.findAll('tr', {'bgcolor': '#C8FFC8'}) for soup in arrSoup]
        td_values = [td.text.strip() for r in rows for row in r for td in row.find_all('td')]
        return td_values
    return []

# Example usage:
# td_values = scrapCourses("your_session_id_here")
# print(td_values)
