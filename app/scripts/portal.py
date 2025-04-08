import requests
from bs4 import BeautifulSoup
import time
import re

from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)


# Function to fetch the hidden fields from the page (viewstate, viewstategen, and eventvalidation)
def get_hidden_fields(soup):
    try:
        viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategen = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']
    except (TypeError, KeyError) as e:
        raise ("Missing required hidden fields")
    return viewstate, viewstategen, eventvalidation

# Function to fetch and parse the portal pages
def fetch_page(session, url, headers, data, cookies):
    response = session.post(url, headers=headers, data=data, cookies=cookies)
    response.raise_for_status()
    return response.text

# Function to scrape all pages for courses data
def fetch_all_pages(session, url, headers, viewstate, viewstategen, eventvalidation, cookies, soup):

    tasks = [soup]
    print([int(re.match(r"^(\d+)" , a['href'].split('Page$')[1]).group(1)) for a in tasks[-1].find_all('a', href=True) if 'Page$' in a['href']])
    for page_num in range(2, max(
    list(map(int, [
    re.match(r"^(\d+)", x).group(1) 
    for x in [a['href'].split('Page$')[1] for a in tasks[-1].find_all('a', href=True) if 'Page$' in a['href']]
    if re.match(r"^(\d+)", x)
]))
)): # Page numbers are starting from 2
        
        data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategen,
            '__EVENTVALIDATION': eventvalidation,
            'radioStatus': '1',
            '__EVENTTARGET': 'GridView1',
            '__EVENTARGUMENT': f'Page${page_num}',
            'lstColgsAjax': 'كلية تكنولوجيا المعلومات',
            'lstDeptAjax': "علم الحاسوب"
        }
        page_content = fetch_page(session, url, headers, data, cookies)
        tasks.append(BeautifulSoup(page_content, 'html.parser'))

        # Delay between tasks to avoid ban and firewall
        time.sleep(0.5)

    return tasks

# Function to scrape course data from the portal
def scrapCourses(session_id):
    url = os.getenv('URLA')
    cookies = {'ASP.NET_SessionId': session_id}
    print('test')
    # Fetch initial page and extract hidden fields (viewstate, viewstategen, eventvalidation)
    try:
        with requests.Session() as session:
            response = session.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)
    except requests.RequestException as e:
        raise (f"Failed to fetch initial page: {str(e)}")
    print('test2')
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategen,
        '__EVENTVALIDATION': eventvalidation,
        'radioStatus': '1',
        'lstColgsAjax': 'كلية تكنولوجيا المعلومات',
        'lstDeptAjax': "علم الحاسوب"
    }
    print('test3')
    # Fetch the first page with the POST request and get subsequent pages
    try:
        page_content = fetch_page(session, url, headers, data, cookies)
        
        soup = BeautifulSoup(page_content, 'html.parser')
        viewstate, viewstategen, eventvalidation = get_hidden_fields(soup)
        
        portal_pages = fetch_all_pages(session, url, headers, viewstate, viewstategen, eventvalidation, cookies, soup)
        print('hi1')
    except requests.RequestException as e:
        raise (f"Error during POST request: {str(e)}")
    print('test3')

    # Process the pages to extract course data
    td_values = []
    for page_soup in portal_pages:
        rows = page_soup.findAll('tr', {'bgcolor': '#C8FFC8'})
        td_values.extend([td.text.strip() for row in rows for td in row.find_all('td')])

    return td_values

# Function to scrape user courses
def scrapUserCourses(session_id):
    url = os.getenv('URLB')
    cookies = {'ASP.NET_SessionId': session_id}

    try:
        with requests.Session() as session:
            response = session.get(url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            courses = [[cell.get_text(strip=True) for cell in row.find_all('td')] for row in soup.find_all('tr', {'bgcolor': '#F7F7DE'})]
            print(f"Number of courses found: {len(courses)}")
            print(courses)
    except requests.RequestException as e:
        raise (f"Failed to fetch user courses: {str(e)}")



