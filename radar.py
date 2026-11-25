import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin

from db import init_db, add_vacancy, remove_closed

KEYWORDS = ["praktikum", "internship", "werkstudent", "student", "junior", "studierende", "werkstudierende", "praktikant", "trainee"]
Path("snapshots").mkdir(exist_ok=True)

def save_new_vacancies(company, vacancies):
    """Check if a vacancy is new"""
    new = []
    for title, link in vacancies:
        result = add_vacancy(company["name"], title, link)
        if result:
            new.append((title, link))
    return new

def get_page_text(url):
    """Takes the url of the page
    request.get downloads html
    BeautifulSoup divide it on tags
    get_text gets rid of tags and leaves visible text and makes it lower cases
    """
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True).lower()
    return text

def get_vacancies(company):
    """Recieves companies from companies.json
    sorters by job_link_contains and seen_links
    """
    response = requests.get(company["url"], timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    pattern = company["job_link_contains"]
    vacancies = []
    seen_links = set()
    for a in soup.find_all("a", href=True):
        link = urljoin(company["url"], a["href"])
        if pattern not in link or link in seen_links:
            continue
        seen_links.add(link)
        if company.get("title_from_link"):
            slug = link.rstrip("/").split("/")[-1]
            title = slug.replace("-", " ").title()
        else:
            title = a.get_text(" ", strip=True)
        vacancies.append((title, link))
    return vacancies

def find_keywords(text, keywords):
    """Recieves text and keywords and checks if it exists in the text"""
    found = []
    for word in keywords:
        if word in text:
            found.append(word)
    return found

def get_added_words(old, new):
    """Makes from old text a set and return new words"""
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
    """Checks the text for new words"""
    lines = []
    name = company["name"]
    url = company["url"]
    phrase = company["phrase"]
    snapshot = Path("snapshots") / f"{company['id']}.txt"
    lines.append(f"{name}:")
    
    text = get_page_text(url)
    text = cut_text(text, company.get("start",""), company.get("end", ""))

    if "job_link_contains" in company:
        #Check for new vacancies and delete closed, return them if exists
        vacancies = get_vacancies(company)
        current_links = [link for title, link in vacancies]
        closed = remove_closed(company["name"], current_links)
        for link in closed:
            lines.append(f"  Closed: {link}")
        new = save_new_vacancies(company, vacancies)
        if not new:
            lines.append("  No new vacancies")
        else:
            for title, link in new:
                lines.append(f"  New: {title} - {link}")
        return lines
    
    if snapshot.exists():
        old = snapshot.read_text(encoding="utf-8")
    else:
        old = None
    snapshot.write_text(text, encoding="utf-8")

    if old is None:
        lines.append("  First run, snapshot saved")
    elif old == text:
        lines.append("  Page unchanged")
    else:
        lines.append("  Page changed, check it")
        added = get_added_words(old, text)
        added_text = " ".join(added)
        lines.append("  New words: " + " ".join(added[:30]))
        phrase_present = bool(phrase) and phrase in text
        found = find_keywords(added_text, KEYWORDS)
        if found and phrase_present:
            lines.append("  No vacancies found, but here what we found that could be useful")
        elif found and not phrase_present:
            position = added_text.find(found[0])
            snippet = added_text[max(0, position - 60): position + 60]
            lines.append("  Vacancy found: " + snippet)
        elif not found and phrase_present:
            lines.append("  Nothing changed")
        else:
            lines.append("  Something might be new, go check it out!")
    return lines

def run_all():
    ###Check all enabled comapnies and return a text report
    init_db()
    
    with open("companies.json", encoding="utf-8") as f:
        companies = json.load(f)

    report = []
    for company in companies:
        if not company.get("enabled", True):
            continue
        try:
            report.extend(check_company(company))
        except requests.RequestException as error:
            report.append(f"Could not check {company["name"]} - {error}")
        report.append("")
        time.sleep(2)
    return "\n".join(report)

if __name__ == "__main__":
    print(run_all())