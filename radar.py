import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior"]
Path("snapshots").mkdir(exist_ok=True)


def get_page_text(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()
    return text


def find_keywords(text, keywords):
    found = []
    for word in keywords:
        if word in text:
            found.append(word)
            print("Found word:", word)
            position = text.find(word)
            snippet = text[max(0, position - 60): position + 60]
            print("Context:", snippet)
    return found

def get_added_words(old, new):
    old_words = set(old.split())
    return [w for w in new.split() if w not in old_words]

def check_company(company):
    name = company["name"]
    url = company["url"]
    phrase = company["phrase"]
    snapshot = Path("snapshots") / f"{company['id']}.txt"
    print("Checking:", name)

    text = get_page_text(url)

    if snapshot.exists():
        old = snapshot.read_text(encoding="utf-8")
    else:
        old = None
    snapshot.write_text(text, encoding="utf-8")

    if old is None:
        print("First run, snapshot saved")
    elif old == text:
        print("Page unchanged")
    else:
        print("Page changed, check it")
        added = get_added_words(old, text)
        print("New words:",  " ".join(added[:30]))
        phrase_present = bool(phrase) and phrase in text
        found = find_keywords(text, KEYWORDS)
        if found and phrase_present:
            print("No vacancies found, but here what we found that could be useful")
        elif found and not phrase_present:
            position = text.find(found[0])
            snippet = text[max(0, position - 60): position + 60]
            print("Vacancy found:", snippet)
        elif not found and phrase_present:
            print("Nothing changed")
        else:
            print("Something might be new, go check it out!")


with open("companies.json", encoding="utf-8") as f:
    companies = json.load(f)

for company in companies:
    try:
        check_company(company)
    except requests.RequestException as error:
        print("Could not check", company["name"], "-", error)
    print()
    time.sleep(2)