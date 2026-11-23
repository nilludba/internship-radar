import json
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

def get_links(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    links = []
    for a in soup.find_all("a", href = True):
        text = a.get_text(" ", strip=True)
        link = urljoin(url, a["href"])
        links.append((text, link))
    return links

with open("companies.json", encoding="utf-8") as f:
    companies = json.load(f)

for company in companies:
    print("=====", company["id"], "=====")
    for text, link in get_links(company["url"]):
        print(text, "|", link)