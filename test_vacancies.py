import json

from radar import get_vacancies

with open("companies.json", encoding="utf-8") as f:
    companies = json.load(f)

for company in companies:
    if "job_link_contains" in company:
        print("=====", company["id"], "=====")
        for title, link in get_vacancies(company):
            print(title, "|", link)