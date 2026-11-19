import requests
from bs4 import BeautifulSoup
URL = "https://trinitec.at/jobcorner"
KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior"]
response = requests.get(URL, timeout=15)
print("Answer code:", response.status_code)
print("Page length:", len(response.text))
soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text(" ", strip=True).lower()
for word in KEYWORDS:
    if word in text:
        print("Found word:", word)
if "keine stellen ausgeschrieben" in text:
    print("No vacancies")
else: print("Page changed, check it out!")