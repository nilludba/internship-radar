import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior", "studierende", "werkstudierende", "praktikant", "trainee"]
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

def cut_text(text, start, end):
    ###Keep only text from start and end
    if start and start in text:
        text = text.split(start, 1)[1] #[1] takes only the second part
    if end and end in text:
        text = text.split(end, 1)[0] #[0] takes only the first part
    return text

def check_company(company):
    name = company["name"]
    url = company["url"]
    phrase = company["phrase"]
    snapshot = Path("snapshots") / f"{company['id']}.txt"
    print("Checking:", name)

    text = get_page_text(url)
    text = cut_text(text, company.get("start",""), company.get("end", ""))

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
        added_text = " ".join(added)
        print("New words:",  " ".join(added[:30]))
        phrase_present = bool(phrase) and phrase in text
        found = find_keywords(added_text, KEYWORDS)
        if found and phrase_present:
            print("No vacancies found, but here what we found that could be useful")
        elif found and not phrase_present:
            position = added_text.find(found[0])
            snippet = added_text[max(0, position - 60): position + 60]
            print("Vacancy found:", snippet)
        elif not found and phrase_present:
            print("Nothing changed")
        else:
            print("Something might be new, go check it out!")


with open("companies.json", encoding="utf-8") as f:
    companies = json.load(f)

for company in companies:
    if not company.get("enabled", True):
        print("Skipped:", company["name"])
        print()
        continue
    try:
        check_company(company)
    except requests.RequestException as error:
        print("Could not check", company["name"], "-", error)
    print()
    time.sleep(2)