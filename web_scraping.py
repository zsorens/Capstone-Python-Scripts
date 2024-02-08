import requests
from bs4 import BeautifulSoup
from itertools import islice
keywords = ['product', 'shop', 'about us']
def search_key_terms(url,terms):
    try:
        all_links = get_links_from_page(url)
    except Exception as e:
        print(f"Error getting links from {url}: {e}")
        return False
    all_links.append(url)
    for link in all_links:
        try:
            response = requests.get(link)
            response.raise_for_status()
        except Exception as e:
            print(f"Error occurred for {link}: {e}")
            continue
        content = BeautifulSoup(response.content,'html.parser')
        content_text = content.get_text().lower()
        # Check for the presence of key terms
        for term in terms:
            if term.lower() in content_text:
                return True
def get_links_from_page(url,max_links=2):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    if url.endswith('/'):
        url = url[:-1]
    #Extract 2 internal pages from the base url
    
    all_links = (a['href'] for a in soup.find_all('a', href=True, text=lambda t: t and any(keyword.lower() in t.lower() for keyword in keywords)))
    #Return list of 2 interal pages
    for a in all_links:
        if a.startswith('/'):
            a = url + a
        print(a)
    return list(all_links)

