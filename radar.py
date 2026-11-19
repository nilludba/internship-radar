import requests
from pathlib import Path
from bs4 import BeautifulSoup
SNAPSHOT = Path("snapshots/trinitec.txt")
SNAPSHOT.parent.mkdir(exist_ok=True)
URL = "https://trinitec.at/jobcorner"
KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior"]
# print("Answer code:", response.status_code)
# print("Page length:", len(response.text))


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

text = get_page_text(URL)


if SNAPSHOT.exists():
    old = SNAPSHOT.read_text(encoding="utf-8")
else: old = None
SNAPSHOT.write_text(text, encoding="utf-8")
if old is None:
    print("First run, snapshot saved")
elif old == text:
    print("Page unchanged")
else: 
    phrase_present = "keine stellen ausgeschrieben" in text
    found = find_keywords(text, KEYWORDS)
    print("Page changed, check it")
    if found and phrase_present:
        print("No vacancies found, but here what we found that could be useful")
    elif found and not phrase_present:
        position = text.find(found[0])
        snippet = text[max(0, position - 60) : position + 60]
        print("Vacancy found:", snippet)
    elif not found and phrase_present:
        print("Nothing changed")
    else:   
        print("Something might be new, go check it out!")
