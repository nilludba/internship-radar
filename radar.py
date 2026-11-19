import requests
from pathlib import Path
from bs4 import BeautifulSoup
SNAPSHOP = Path("snapshots/trinitec.txt")
SNAPSHOP.parent.mkdir(exist_ok=True)
URL = "https://trinitec.at/jobcorner"
KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior"]
response = requests.get(URL, timeout=15)
print("Answer code:", response.status_code)
print("Page length:", len(response.text))
soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text(" ", strip=True).lower()
phrase_present = "keine stellen ausgeschrieben" in text
if SNAPSHOP.exists():
    old = SNAPSHOP.read_text(encoding="utf-8")
else: old = None
SNAPSHOP.write_text(text, encoding="utf-8")
if old is None:
    print("First run, snapshot saved")
elif old == text:
    print("Page unchanged")
else: print("Page changed, check it")
found = []
for word in KEYWORDS:
    if word in text:
        found.append(word)
        print("Found word:", word)
        position = text.find(word)
        snippet = text[max(0, position - 60): position + 60]
        print("Context:", snippet)


# if "keine stellen ausgeschrieben" in text:
#     print("No vacancies")
# else: print("Page changed, check it out!")
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